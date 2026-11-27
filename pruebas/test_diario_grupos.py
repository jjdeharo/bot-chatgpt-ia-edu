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
        portada, m = lista["chatgpt"]
        self.assertEqual(m["parse_mode"], "HTML")
        self.assertTrue(m["text"].startswith("<b>Diario de IA Educativa · Núm. 4</b>\nJueves, 5 de noviembre\n\nBuenos días."))
        self.assertIn("• Uno &lt;con&gt; &amp; signos\n• Dos\n\n👉 https://diarioiaeducativa.github.io/?n=4", m["text"])
        self.assertEqual(m["link_preview_options"], {"is_disabled": True})   # el texto, sin vista previa
        self.assertNotIn("disable_notification", m)                          # y es el que suena
        self.assertEqual(portada, {"text": "https://diarioiaeducativa.github.io/?n=4", "disable_notification": True,
                                   "link_preview_options": {"url": "https://diarioiaeducativa.github.io/?n=4",
                                                            "prefer_large_media": True, "show_above_text": True}})

    def test_enlace_propio_de_cada_grupo(self):
        (self.tmp / "2026-11-08.json").write_text(json.dumps({
            "fecha": "2026-11-08", "titulo": "Diario de IA Educativa · Núm. 7", "url": "https://diarioiaeducativa.github.io/?n=7",
            "avisos": {"chatgpt": {"saludo": "Hola.", "puntos": ["Uno"]},
                       "vce": {"saludo": "Hola.", "puntos": ["Dos"], "url": "https://diarioiaeducativa.github.io/n/7-vce.html"}}}))
        _, lista = d.pendientes(datetime(2026, 11, 8, 6, 0, tzinfo=timezone.utc), carpeta=self.tmp)
        self.assertEqual(lista["chatgpt"][0]["link_preview_options"]["url"], "https://diarioiaeducativa.github.io/?n=7")
        self.assertEqual(lista["vce"][0]["link_preview_options"]["url"], "https://diarioiaeducativa.github.io/n/7-vce.html")
        self.assertEqual(lista["vce"][0]["text"], "https://diarioiaeducativa.github.io/n/7-vce.html")
        self.assertTrue(lista["vce"][1]["text"].endswith("👉 https://diarioiaeducativa.github.io/n/7-vce.html"))

    def test_portada_como_imagen_del_aviso(self):
        (self.tmp / "2026-11-14.json").write_text(json.dumps({
            "fecha": "2026-11-14", "titulo": "Núm. 13", "url": "https://diarioiaeducativa.github.io/?n=13",
            "imagen": "https://diarioiaeducativa.github.io/portadas/2026-11-13-es.jpg",
            "avisos": {"vce": {"saludo": "Hola.", "puntos": ["Uno"], "url": "https://diarioiaeducativa.github.io/n/13-vce.html"}}}))
        a_las_7 = datetime(2026, 11, 14, 6, 1, tzinfo=timezone.utc)
        _, lista = d.pendientes(a_las_7, carpeta=self.tmp, disponible=lambda u: True)
        self.assertEqual(lista["vce"][0]["link_preview_options"]["url"], "https://diarioiaeducativa.github.io/portadas/2026-11-13-es.jpg")
        self.assertEqual(lista["vce"][0]["text"], "https://diarioiaeducativa.github.io/n/13-vce.html")
        self.assertTrue(lista["vce"][1]["text"].endswith("👉 https://diarioiaeducativa.github.io/n/13-vce.html"))
        # Si la portada aún no está en la web, se espera; pasada la espera, sale con la imagen de la página del grupo
        _, lista = d.pendientes(a_las_7, carpeta=self.tmp, disponible=lambda u: False)
        self.assertEqual(lista, {})
        _, lista = d.pendientes(datetime(2026, 11, 14, 6, 25, tzinfo=timezone.utc), carpeta=self.tmp, disponible=lambda u: False)
        self.assertEqual(lista["vce"][0]["link_preview_options"]["url"], "https://diarioiaeducativa.github.io/n/13-vce.html")

    def test_sin_cabecera_sale_igual(self):
        (self.tmp / "2026-11-05.json").write_text(json.dumps(
            {"fecha": "2026-11-05", "avisos": {"vce": {"saludo": "Buenos días.", "puntos": ["Uno", "Dos"]}}}))
        _, lista = d.pendientes(datetime(2026, 11, 5, 6, 0, tzinfo=timezone.utc), carpeta=self.tmp)
        self.assertEqual(lista["vce"][1]["text"], "Buenos días.\n\n• Uno\n• Dos\n\n👉 https://diarioiaeducativa.github.io/")

    def test_formato_anterior_tal_cual(self):
        _, lista = d.pendientes(datetime(2026, 11, 2, 6, 0, tzinfo=timezone.utc), carpeta=self.tmp)
        self.assertEqual(lista["chatgpt"], [{"text": "Hola A"}])

    def test_archivo_de_otro_dia_no_vale(self):
        (self.tmp / "2026-11-03.json").write_text(json.dumps({"fecha": "2026-11-02", "avisos": {"vce": "x"}}))
        _, lista = d.pendientes(datetime(2026, 11, 3, 6, 30, tzinfo=timezone.utc), carpeta=self.tmp)
        self.assertEqual(lista, {})

    def test_publica_en_dos_mensajes_y_sigue_por_el_que_falto(self):
        """La portada y el texto, en orden; si el texto falla, la vuelta siguiente manda solo el texto (ADR 0054)."""
        import types
        (self.tmp / "2026-11-28.json").write_text(json.dumps({
            "fecha": "2026-11-28", "titulo": "Núm. 27", "url": "https://diarioiaeducativa.github.io/?n=27",
            "avisos": {"vce": {"saludo": "Hola.", "puntos": ["Uno"]}}}))
        sys.modules["grupos"] = types.SimpleNamespace(TODOS={"vce": types.SimpleNamespace(id=-100)})
        self.addCleanup(sys.modules.pop, "grupos", None)
        a_las_7 = datetime(2026, 11, 28, 6, 0, tzinfo=timezone.utc)
        dia = a_las_7.date()
        llamadas = []

        def tg(metodo, **p):
            llamadas.append(p)
            return None if fallar and "parse_mode" in p else {"message_id": len(llamadas)}

        fallar = True
        _, lista = d.pendientes(a_las_7, carpeta=self.tmp)
        self.assertEqual(d.publicar(tg, dia, lista, self.tmp), [])
        self.assertEqual(d.enviados(dia, "vce", self.tmp), [1])
        fallar = False
        _, lista = d.pendientes(a_las_7, carpeta=self.tmp)
        self.assertEqual(d.publicar(tg, dia, lista, self.tmp), ["vce"])
        self.assertEqual([("parse_mode" in p) for p in llamadas], [False, True, True])   # la portada, una sola vez
        self.assertEqual(d.enviados(dia, "vce", self.tmp), [1, 3])
        _, lista = d.pendientes(a_las_7, carpeta=self.tmp)
        self.assertEqual(lista, {})


if __name__ == "__main__":
    unittest.main()


class InformeDelDia(unittest.TestCase):
    """El informe del día (ADR 0040): se manda una vez, y otra si el diario lo vuelve a dejar."""

    def test_pendiente_marcado_y_repetido(self):
        import os
        import time as tiempo
        with tempfile.TemporaryDirectory() as tmp:
            carpeta = Path(tmp)
            f = carpeta / "2026-11-15.informe.txt"
            f.write_text("Informe")
            (carpeta / "2026-11-15.json").write_text("{}")
            self.assertEqual(d.informes_pendientes(carpeta), [f])
            d.marcar_informe(f)
            self.assertEqual(d.informes_pendientes(carpeta), [])
            hecho = carpeta / "2026-11-15.informe-enviado"
            antes = tiempo.time() - 60
            os.utime(hecho, (antes, antes))
            f.write_text("Informe corregido")
            self.assertEqual(d.informes_pendientes(carpeta), [f])
