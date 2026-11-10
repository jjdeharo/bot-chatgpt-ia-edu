# SPDX-License-Identifier: AGPL-3.0-or-later
"""Lo que el bot no consigue leer se puede pasar a revisión manual (ADR 0004, punto 1), sin red ni API.

    .venv/bin/python -m unittest pruebas/test_no_lo_lee.py
"""
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import bot  # noqa: E402
import catalogo  # noqa: E402

AUTOR = 7001
URL = "https://sites.google.com/x/app/inicio"
DE = {"id": AUTOR, "first_name": "Ana", "last_name": "Pérez"}
FICHA = {"suficiente": True, "es_recurso_educativo": True, "nivel_minimo": True, "de_pago": False, "pago_detalle": "",
         "licencia": "CC-BY-SA-4.0", "licencia_contenidos": "", "licencia_abierta": True,
         "licencia_solo_repositorio": False, "motivo": "", "titulo": "Pentagrama", "descripcion": "Lee notas.",
         "tipo": ["Juego / Gamificación"], "niveles": ["Secundaria"], "areas": ["Artes y Humanidades"],
         "palabras_clave": "", "idiomas": ["Español"]}


class Hoja:
    def buscar(self, url):
        return None


def nuevo_bot():
    b = bot.Bot.__new__(bot.Bot)
    for nombre in ("memoria", "pendientes", "miembros", "espera", "fichas_rec", "listas", "lenguas", "recientes",
                   "compartir", "rechazados", "ambitos", "valorables", "borradores", "al_grupo"):
        setattr(b, nombre, {})
    b.lenguas[AUTOR] = "es"
    b.llamadas = []
    b.tg = lambda metodo, **k: (b.llamadas.append((metodo, k)), {"message_id": 99})[1]
    b.enviar = lambda chat, texto, formato=None: b.llamadas.append(("enviar", {"chat_id": chat, "text": texto}))
    b.hoja = Hoja()
    b.escribiendo = lambda chat: threading.Event()
    b.apuntar = lambda *a, **k: None
    b.puede_preparar = lambda chat, uid: True
    b.en_hilo = lambda f, *a: f(*a)
    b.recursos = mock.Mock()
    return b


def textos(b, a=None):
    return [(k.get("chat_id"), k.get("text", ""), k.get("reply_markup")) for m, k in b.llamadas if m in ("enviar", "sendMessage")
            and (a is None or k.get("chat_id") == a)]


class NoLoLee(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        parche = mock.patch.object(catalogo, "REVISIONES", Path(self.tmp.name) / "revisiones.json")
        parche.start()
        self.addCleanup(parche.stop)
        self.addCleanup(self.tmp.cleanup)
        self.b = nuevo_bot()

    def pedir(self, leido=("código de carga", None), analisis=None):
        self.b.recursos.analizar.return_value = (analisis or {**FICHA, "suficiente": False,
                                                              "motivo": "solo se ve el código de carga"}, 0.0)
        with mock.patch.object(catalogo, "leer_url", return_value=leido):
            self.b.recurso(AUTOR, AUTOR, DE, URL)
        ultimo = textos(self.b, AUTOR)[-1]
        return ultimo

    def test_ofrece_pedir_revision_cuando_no_ve_que_hace(self):
        _, texto, botones = self.pedir()
        self.assertIn("No consigo ver qué hace", texto)
        self.assertIn("Pedir una revisión", texto)
        self.assertEqual(botones["inline_keyboard"][0][0]["callback_data"], "rr")
        self.assertEqual(self.b.espera[AUTOR]["que"], "detalle")  # sigue pudiendo mandar el HTML o el ZIP

    def test_ofrece_pedir_revision_cuando_el_enlace_no_se_abre(self):
        _, texto, botones = self.pedir(("", "El enlace no se abre desde fuera: el servidor responde con el código 403."))
        self.assertIn("403", texto)
        self.assertEqual(botones["inline_keyboard"][0][0]["callback_data"], "rr")

    def test_direccion_no_publica_no_ofrece_nada(self):
        _, texto, botones = self.pedir(("", catalogo.AVISO_NO_PUBLICA))
        self.assertIsNone(botones)

    def test_llega_a_juanjo_y_volver_a_leer_sigue_el_alta(self):
        self.pedir()
        self.b.boton_recurso(AUTOR, "rr")
        self.assertIn("cómo lo has publicado", textos(self.b, AUTOR)[-1][1])
        self.b.pedir_revision(AUTOR, "Está en Google Sites, con el código insertado")
        _, texto, botones = textos(self.b, bot.JUANJO)[-1]
        self.assertIn("no ha podido leer", texto)
        self.assertIn("Google Sites, con el código insertado", texto)
        self.assertIn(URL, texto)
        datos = [x["callback_data"] for x in botones["inline_keyboard"][0]]
        self.assertTrue(datos[0].startswith("jrl:") and datos[1].startswith("jrn:"))
        # Arreglado el bot, «Volver a leer»: esta vez lo lee y le enseña la ficha a su autor.
        self.b.recursos.analizar.return_value = (dict(FICHA), 0.0)
        with mock.patch.object(catalogo, "leer_url", return_value=("<html>app</html>", None)), \
                mock.patch.object(self.b, "seguir_alta") as seguir:
            self.b.revisar_rechazo(datos[0])
        seguir.assert_called_once()
        self.assertIn("Lo vuelvo a leer", " ".join(t for _, t, _ in textos(self.b, AUTOR)))
        self.assertIn("sigue con el alta", textos(self.b, bot.JUANJO)[-1][1])
        self.assertEqual(catalogo.leer_revisiones()[catalogo.normalizar(URL)]["estado"], "releido")

    def test_volver_a_leer_sin_arreglo_se_lo_dice_a_juanjo(self):
        self.pedir()
        self.b.boton_recurso(AUTOR, "rr")
        self.b.pedir_revision(AUTOR, "Funciona")
        jrl = textos(self.b, bot.JUANJO)[-1][2]["inline_keyboard"][0][0]["callback_data"]
        with mock.patch.object(catalogo, "leer_url", return_value=("código de carga", None)):
            self.b.revisar_rechazo(jrl)
        self.assertIn("sigue sin poder leer", textos(self.b, bot.JUANJO)[-1][1])
        self.assertEqual(textos(self.b, AUTOR)[-1][2]["inline_keyboard"][0][0]["callback_data"], "rr")

    def test_no_cumple_se_lo_dice_a_su_autor(self):
        self.pedir()
        self.b.boton_recurso(AUTOR, "rr")
        self.b.pedir_revision(AUTOR, "Funciona")
        jrn = textos(self.b, bot.JUANJO)[-1][2]["inline_keyboard"][0][1]["callback_data"]
        self.b.revisar_rechazo(jrn)
        self.assertIn("no entra en el repositorio", textos(self.b, AUTOR)[-1][1])

    def test_el_rechazo_por_contenido_sigue_con_cumple(self):
        self.pedir(analisis={**FICHA, "nivel_minimo": False, "motivo": "está a medio hacer"})
        self.b.boton_recurso(AUTOR, "rr")
        self.assertIn("por qué crees", textos(self.b, AUTOR)[-1][1])
        self.b.pedir_revision(AUTOR, "Ya funciona")
        _, texto, botones = textos(self.b, bot.JUANJO)[-1]
        self.assertIn("ha rechazado", texto)
        self.assertTrue(botones["inline_keyboard"][0][0]["callback_data"].startswith("jrc:"))


if __name__ == "__main__":
    unittest.main()
