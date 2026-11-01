# SPDX-License-Identifier: AGPL-3.0-or-later
"""Pruebas del aviso diario de «Tiza y Algoritmo» (ADR 0025), sin red ni Telegram."""
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import diario_grupos as d  # noqa: E402


class Diario(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "2026-11-02.json").write_text(json.dumps(
            {"fecha": "2026-11-02", "avisos": {"chatgpt": "Hola A", "vce": "Hola B", "edumedia": " "}}))

    def test_antes_de_las_siete_no_toca(self):
        # 05:59 UTC = 06:59 en Madrid (horario de invierno)
        _, lista = d.pendientes(datetime(2026, 11, 2, 5, 59, tzinfo=timezone.utc), carpeta=self.tmp)
        self.assertEqual(lista, {})

    def test_a_las_siete_toca_y_salta_los_vacios(self):
        _, lista = d.pendientes(datetime(2026, 11, 2, 6, 0, tzinfo=timezone.utc), carpeta=self.tmp)
        self.assertEqual(set(lista), {"chatgpt", "vce"})

    def test_pasada_la_ventana_ya_no(self):
        _, lista = d.pendientes(datetime(2026, 11, 2, 11, 1, tzinfo=timezone.utc), carpeta=self.tmp)
        self.assertEqual(lista, {})

    def test_no_repite_un_grupo_ya_publicado(self):
        dia = datetime(2026, 11, 2).date()
        d.apuntar(dia, "chatgpt", self.tmp)
        _, lista = d.pendientes(datetime(2026, 11, 2, 6, 30, tzinfo=timezone.utc), carpeta=self.tmp)
        self.assertEqual(set(lista), {"vce"})

    def test_solo_grupos_activos(self):
        _, lista = d.pendientes(datetime(2026, 11, 2, 6, 30, tzinfo=timezone.utc), activos={"vce": 1}, carpeta=self.tmp)
        self.assertEqual(set(lista), {"vce"})

    def test_archivo_de_otro_dia_no_vale(self):
        (self.tmp / "2026-11-03.json").write_text(json.dumps({"fecha": "2026-11-02", "avisos": {"vce": "x"}}))
        _, lista = d.pendientes(datetime(2026, 11, 3, 6, 30, tzinfo=timezone.utc), carpeta=self.tmp)
        self.assertEqual(lista, {})


if __name__ == "__main__":
    unittest.main()
