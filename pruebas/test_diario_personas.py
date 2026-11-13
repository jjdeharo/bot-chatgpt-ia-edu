# SPDX-License-Identifier: AGPL-3.0-or-later
"""Pruebas del aviso privado a quien sale en el número (ADR 0036), sin red ni Telegram."""
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import diario_grupos as d  # noqa: E402
import textos  # noqa: E402

A_LAS_SIETE = datetime(2026, 11, 13, 6, 0, tzinfo=timezone.utc)
PIEZA = {c: {"titular": f"Titular {c}", "url": f"https://diarioiaeducativa.github.io/{'' if c == 'es' else c + '/'}2026-11-12/x.html"}
         for c in ("es", "ca", "gl", "eu", "en")}


class Personas(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        d.SIN_AVISOS = self.tmp / "sin.json"
        (self.tmp / "2026-11-13.json").write_text(json.dumps({"fecha": "2026-11-13", "avisos": {}, "personas": [
            {"id": 1, "piezas": [PIEZA]}, {"id": 2, "piezas": [PIEZA, PIEZA]}, {"id": 3, "piezas": []}]}))
        self.enviados = []

    def tg(self, metodo, **params):
        if metodo == "getChat":   # la 1 se llama Aina; de la 2, Telegram no da el nombre
            return {"first_name": "Aina "} if params["chat_id"] == 1 else None
        self.enviados.append(params)
        return None if params["chat_id"] == 2 else {"message_id": 1}   # a la 2 Telegram no deja escribirle

    def test_fuera_de_la_ventana_nada(self):
        _, lista = d.personas_pendientes(datetime(2026, 11, 13, 5, 59, tzinfo=timezone.utc), carpeta=self.tmp)
        self.assertEqual(lista, [])

    def test_una_vez_por_persona_y_sin_insistir(self):
        dia, lista = d.personas_pendientes(A_LAS_SIETE, carpeta=self.tmp)
        self.assertEqual([p["id"] for p in lista], [1, 2])   # la que no tiene piezas, no
        bien, mal = d.avisar_personas(self.tg, dia, lista, lambda uid: "ca", textos.texto, carpeta=self.tmp)
        self.assertEqual((bien, mal), (1, 1))
        _, otra_vez = d.personas_pendientes(A_LAS_SIETE, carpeta=self.tmp)
        self.assertEqual(otra_vez, [])

    def test_en_su_idioma_con_todas_sus_piezas_y_el_boton(self):
        dia, lista = d.personas_pendientes(A_LAS_SIETE, carpeta=self.tmp)
        d.avisar_personas(self.tg, dia, lista, lambda uid: "ca", textos.texto, carpeta=self.tmp)
        self.assertTrue(self.enviados[0]["text"].startswith("Bon dia, Aina. Avui el Diari d'IA Educativa"))
        m = self.enviados[1]
        self.assertTrue(m["text"].startswith("Bon dia. Avui el Diari d'IA Educativa"))
        self.assertEqual(m["text"].count("«Titular ca»"), 2)
        self.assertIn("/ca/2026-11-12/x.html", m["text"])
        self.assertEqual(m["reply_markup"]["inline_keyboard"][0][0]["callback_data"], d.BOTON_NO)

    def test_quien_no_quiere_no_recibe(self):
        d.no_avisar_mas(1)
        _, lista = d.personas_pendientes(A_LAS_SIETE, carpeta=self.tmp)
        self.assertEqual([p["id"] for p in lista], [2])


if __name__ == "__main__":
    unittest.main()
