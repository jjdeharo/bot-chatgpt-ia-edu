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

    def test_formato_nuevo_con_puntos(self):
        (self.tmp / "2026-11-05.json").write_text(json.dumps({
            "fecha": "2026-11-05", "titulo": "Diario de IA Educativa · Núm. 4", "fecha_texto": "Jueves, 5 de noviembre",
            "url": "https://diarioiaeducativa.github.io/?n=4",
            "avisos": {"chatgpt": {"saludo": "Buenos días. Hoy, en el número:", "puntos": ["Uno <con> & signos", " ", "Dos"]},
                       "vce": {"saludo": "Buenos días.", "puntos": []}}}))
        _, lista = d.pendientes(datetime(2026, 11, 5, 6, 0, tzinfo=timezone.utc), carpeta=self.tmp)
        self.assertEqual(set(lista), {"chatgpt"})   # sin puntos no hay aviso
        m = lista["chatgpt"]
        self.assertEqual(m["parse_mode"], "HTML")
        self.assertTrue(m["text"].startswith("<b>Diario de IA Educativa · Núm. 4</b>\nJueves, 5 de noviembre\n\nBuenos días."))
        self.assertIn("• Uno &lt;con&gt; &amp; signos\n• Dos\n\n👉 https://diarioiaeducativa.github.io/?n=4", m["text"])
        self.assertEqual(m["link_preview_options"], {"url": "https://diarioiaeducativa.github.io/?n=4",
                                                     "prefer_large_media": True, "show_above_text": True})

    def test_enlace_propio_de_cada_grupo(self):
        (self.tmp / "2026-11-08.json").write_text(json.dumps({
            "fecha": "2026-11-08", "titulo": "Diario de IA Educativa · Núm. 7", "url": "https://diarioiaeducativa.github.io/?n=7",
            "avisos": {"chatgpt": {"saludo": "Hola.", "puntos": ["Uno"]},
                       "vce": {"saludo": "Hola.", "puntos": ["Dos"], "url": "https://diarioiaeducativa.github.io/n/7-vce.html"}}}))
        _, lista = d.pendientes(datetime(2026, 11, 8, 6, 0, tzinfo=timezone.utc), carpeta=self.tmp)
        self.assertEqual(lista["chatgpt"]["link_preview_options"]["url"], "https://diarioiaeducativa.github.io/?n=7")
        self.assertEqual(lista["vce"]["link_preview_options"]["url"], "https://diarioiaeducativa.github.io/n/7-vce.html")
        self.assertTrue(lista["vce"]["text"].endswith("👉 https://diarioiaeducativa.github.io/n/7-vce.html"))

    def test_portada_como_imagen_del_aviso(self):
        (self.tmp / "2026-11-14.json").write_text(json.dumps({
            "fecha": "2026-11-14", "titulo": "Núm. 13", "url": "https://diarioiaeducativa.github.io/?n=13",
            "imagen": "https://diarioiaeducativa.github.io/portadas/2026-11-13-es.jpg",
            "avisos": {"vce": {"saludo": "Hola.", "puntos": ["Uno"], "url": "https://diarioiaeducativa.github.io/n/13-vce.html"}}}))
        a_las_7 = datetime(2026, 11, 14, 6, 1, tzinfo=timezone.utc)
        _, lista = d.pendientes(a_las_7, carpeta=self.tmp, disponible=lambda u: True)
        self.assertEqual(lista["vce"]["link_preview_options"]["url"], "https://diarioiaeducativa.github.io/portadas/2026-11-13-es.jpg")
        self.assertTrue(lista["vce"]["text"].endswith("👉 https://diarioiaeducativa.github.io/n/13-vce.html"))
        # Si la portada aún no está en la web, se espera; pasada la espera, sale con la imagen de la página del grupo
        _, lista = d.pendientes(a_las_7, carpeta=self.tmp, disponible=lambda u: False)
        self.assertEqual(lista, {})
        _, lista = d.pendientes(datetime(2026, 11, 14, 6, 25, tzinfo=timezone.utc), carpeta=self.tmp, disponible=lambda u: False)
        self.assertEqual(lista["vce"]["link_preview_options"]["url"], "https://diarioiaeducativa.github.io/n/13-vce.html")

    def test_sin_cabecera_sale_igual(self):
        (self.tmp / "2026-11-05.json").write_text(json.dumps(
            {"fecha": "2026-11-05", "avisos": {"vce": {"saludo": "Buenos días.", "puntos": ["Uno", "Dos"]}}}))
        _, lista = d.pendientes(datetime(2026, 11, 5, 6, 0, tzinfo=timezone.utc), carpeta=self.tmp)
        self.assertEqual(lista["vce"]["text"], "Buenos días.\n\n• Uno\n• Dos\n\n👉 https://diarioiaeducativa.github.io/")

    def test_formato_anterior_tal_cual(self):
        _, lista = d.pendientes(datetime(2026, 11, 2, 6, 0, tzinfo=timezone.utc), carpeta=self.tmp)
        self.assertEqual(lista["chatgpt"], {"text": "Hola A"})

    def test_archivo_de_otro_dia_no_vale(self):
        (self.tmp / "2026-11-03.json").write_text(json.dumps({"fecha": "2026-11-02", "avisos": {"vce": "x"}}))
        _, lista = d.pendientes(datetime(2026, 11, 3, 6, 30, tzinfo=timezone.utc), carpeta=self.tmp)
        self.assertEqual(lista, {})


if __name__ == "__main__":
    unittest.main()
