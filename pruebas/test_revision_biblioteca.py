# SPDX-License-Identifier: AGPL-3.0-or-later
"""Revisión manual de lo que la Biblioteca digital no acepta (ADR 0050), sin red ni API.

    .venv/bin/python -m unittest pruebas/test_revision_biblioteca.py
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import bot  # noqa: E402
import fichas  # noqa: E402
import textos  # noqa: E402
from test_documento_web import AUTOR, DE, DOC, PDF, nuevo_bot  # noqa: E402

JUANJO = 1


class RevisionBiblioteca(unittest.TestCase):
    def setUp(self):
        carpeta = tempfile.TemporaryDirectory()
        self.addCleanup(carpeta.cleanup)
        raiz = Path(carpeta.name)
        for nombre, valor in (("JUANJO", JUANJO), ("ESTADO", raiz / "estado.json"),
                              ("REVISIONES_BIB", raiz / "revisiones.json"),
                              ("CORRECCIONES_BIB", raiz / "correcciones.jsonl")):
            self.enterContext(mock.patch.object(bot, nombre, valor))
        self.raiz = raiz
        self.b = nuevo_bot()
        self.b.fichero.buscar_enlace.return_value = ("", 0.0)
        self.b.repetido_biblioteca = lambda *a: ""
        self.b.registrar_publicacion_biblioteca = lambda *a: None

    def mandar(self, revision=None, texto="texto " * 100):
        if revision:
            self.b.fichero.revisar.return_value = (revision, [{"enlace": "https://t.me/ChatGPTedu/21753/5"}], 0.0)
        with mock.patch.object(fichas, "leer_pdf", return_value=(texto, "Pages: 3")):
            self.b.preparar_ficha(AUTOR, AUTOR, DE, "guia.pdf", lambda: (texto, "Pages: 3", "h"), pdf=PDF, enlace=DOC)

    def botones(self, chat):
        return [b["callback_data"] for m, k in self.b.llamadas if m == "sendMessage" and k.get("chat_id") == chat
                for fila in (k.get("reply_markup") or {}).get("inline_keyboard", []) for b in fila]

    def pedir(self):
        clave = self.b.rechazos_bib[AUTOR]["clave"]
        self.b.pedir_revision_biblioteca(AUTOR, clave)

    def test_lo_que_no_trata_de_ia_ofrece_la_revision(self):
        self.mandar({"trata_ia_educacion": False, "tema": "jardinería", "repetido": 0})
        self.assertTrue(any(c.startswith("bpr:") for c in self.botones(AUTOR)))
        self.assertEqual(self.b.rechazos_bib[AUTOR]["motivo"], "ajeno")

    def test_la_revision_le_llega_a_juanjo_con_la_ficha_hecha_y_los_botones(self):
        self.mandar({"trata_ia_educacion": True, "tema": "IA", "repetido": 1})
        self.pedir()
        aviso = next(k["text"] for m, k in self.b.llamadas if m == "sendMessage" and k.get("chat_id") == JUANJO)
        self.assertIn("tg://user?id=7002", aviso)
        self.assertIn("@ana", aviso)
        self.assertIn("https://t.me/ChatGPTedu/21753/5", aviso)  # el que cree repetido
        self.assertTrue(any(m == "subir" and k.get("chat_id") == JUANJO for m, k in self.b.llamadas))  # el PDF
        self.assertEqual({c.split(":")[0] for c in self.botones(JUANJO)}, {"bjs", "bjf", "bjn"})
        d = json.loads(bot.REVISIONES_BIB.read_text())
        (r,) = d.values()
        self.assertEqual((r["estado"], r["file_id"], r["motivo"]), ("por_revisar", "subido-1", "repetido"))
        self.assertNotIn(AUTOR, self.b.rechazos_bib)

    def test_tres_peticiones_al_dia(self):
        for _ in range(3):
            self.mandar({"trata_ia_educacion": False, "tema": "x", "repetido": 0})
            self.pedir()
        self.mandar({"trata_ia_educacion": False, "tema": "x", "repetido": 0})
        self.pedir()
        self.assertIn("tres revisiones", [k["text"] for m, k in self.b.llamadas if m == "enviar"][-1])
        self.assertEqual(len(json.loads(bot.REVISIONES_BIB.read_text())), 3)

    def decidir(self, orden):
        self.mandar({"trata_ia_educacion": False, "tema": "x", "repetido": 0})
        self.pedir()
        ref = next(iter(json.loads(bot.REVISIONES_BIB.read_text())))
        self.b.publicar = mock.Mock(return_value=("https://t.me/ChatGPTedu/21753/9", -1001, [8, 9]))
        self.b.firma = lambda *a: "f"
        self.b.decidir_revision_biblioteca(f"{orden}:{ref}")
        return ref

    def test_publicar_con_el_archivo_avisa_y_apunta_la_correccion(self):
        ref = self.decidir("bjs")
        p = self.b.publicar.call_args.args[0]
        self.assertTrue(p["compartir"])
        self.assertEqual(p["file_id"], "subido-1")
        self.assertIn("Ana (@ana)", p["autor"])
        al_autor = [k["text"] for m, k in self.b.llamadas if m == "sendMessage" and k.get("chat_id") == AUTOR]
        self.assertIn("Revisado a mano", al_autor[-1])
        apunte = json.loads(bot.CORRECCIONES_BIB.read_text().splitlines()[-1])
        self.assertEqual(apunte["motivo"], "ajeno")
        self.assertEqual(json.loads(bot.REVISIONES_BIB.read_text())[ref]["estado"], "publicado")
        self.b.decidir_revision_biblioteca(f"bjs:{ref}")  # un segundo toque no publica otra vez
        self.assertEqual(self.b.publicar.call_count, 1)

    def test_solo_la_ficha_y_no_publicar(self):
        self.decidir("bjf")
        self.assertFalse(self.b.publicar.call_args.args[0]["compartir"])
        b2 = self
        b2.setUp()
        self.decidir("bjn")
        self.b.publicar.assert_not_called()
        self.assertIn("no entra", [k["text"] for m, k in self.b.llamadas if m == "enviar" and k["chat_id"] == AUTOR][-1])
        self.assertFalse(bot.CORRECCIONES_BIB.exists())

    def test_sin_texto_no_hay_ficha_y_juanjo_puede_gestionarlo_a_mano(self):
        self.mandar(texto="poco")
        self.pedir()
        self.assertEqual({c.split(":")[0] for c in self.botones(JUANJO)}, {"bjm", "bjn"})
        self.b.fichero.ficha.assert_not_called()

    def test_la_vista_sin_archivo_permite_pedir_revisar_la_licencia(self):
        self.b.fichero.compartible.return_value = (False, 0.0)
        self.mandar()
        self.assertTrue(any(c.startswith("bpr:") for c in self.botones(AUTOR)))
        clave = self.b.pendientes[AUTOR]["clave"]
        self.b.pedir_revision_biblioteca(AUTOR, clave)
        r = next(iter(json.loads(bot.REVISIONES_BIB.read_text()).values()))
        self.assertEqual((r["motivo"], r["file_id"]), ("licencia", "subido-1"))  # el PDF descargado, subido para él
        self.assertNotIn(AUTOR, self.b.pendientes)

    def test_un_archivo_de_mas_de_20_mb_le_llega_a_juanjo_para_gestionarlo(self):
        msg = {"from": DE, "document": {"file_id": "grande-1", "file_name": "g.pdf", "mime_type": "application/pdf",
                                        "file_size": 30 * 1024 * 1024}}
        self.b.documento(AUTOR, AUTOR, msg)
        self.pedir()
        self.assertIn(("sendDocument", {"chat_id": JUANJO, "document": "grande-1"}), self.b.llamadas)
        self.assertEqual({c.split(":")[0] for c in self.botones(JUANJO)}, {"bjm", "bjn"})

    def test_textos_en_los_cinco_idiomas(self):
        for lengua in textos.LENGUAS:
            for clave in ("si_crees_biblioteca", "b_enviar_revision", "b_revisar_licencia", "revision_bib_pedida", "revision_bib_cupo",
                          "revision_bib_si", "revision_bib_no", "revision_bib_mano"):
                self.assertIn(clave, textos.TEXTOS[lengua], (lengua, clave))
            for clave in ("sin_texto", "web_grande", "grande"):
                self.assertNotIn("21753", textos.TEXTOS[lengua][clave], (lengua, clave))  # el tema está cerrado


if __name__ == "__main__":
    unittest.main()
