# SPDX-License-Identifier: AGPL-3.0-or-later
"""Pruebas del aviso de la semana del boletín en los grupos (ADR 0041), sin red ni Telegram."""
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import boletin_grupos as b  # noqa: E402


class FalsoTelegram:
    def __init__(self, falla=None):
        self.llamadas, self.falla, self.n = [], falla, 100

    def _r(self, metodo):
        self.n += 1
        return None if metodo == self.falla else {"message_id": self.n}

    def __call__(self, metodo, **p):
        self.llamadas.append((metodo, p))
        return {} if metodo == "deleteMessage" else self._r(metodo)

    def subir(self, metodo, campo, nombre, datos, tipo="application/pdf", extra=None, **p):
        self.llamadas.append((metodo, dict(p, campo=campo, nombre=nombre, tipo=tipo, extra=sorted(extra or {}))))
        return self._r(metodo)


class Boletin(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        d = self.tmp / "2026-47"
        d.mkdir()
        (d / "chatgpt-video.mp4").write_bytes(b"v")
        (d / "chatgpt-miniatura.jpg").write_bytes(b"m")
        (d / "chatgpt-audio.mp3").write_bytes(b"a")
        (d / "chatgpt.json").write_text(json.dumps({
            "semana": "2026-47", "grupo": "chatgpt", "tema": 19215, "salida": "2026-11-23T08:00:00+01:00",
            "texto": "<b>Semana 47</b>\nHola\n\n👉 https://x",
            "video": {"archivo": "chatgpt-video.mp4", "miniatura": "chatgpt-miniatura.jpg", "duracion": 5,
                      "ancho": 1280, "alto": 720},
            "audio": {"archivo": "chatgpt-audio.mp3", "duracion": 9, "titulo": "Semana 47", "interprete": "@ChatGPTedu"}}))
        (d / "edumedia.json").write_text(json.dumps({
            "semana": "2026-47", "grupo": "edumedia", "tema": None, "salida": "2026-11-23T08:00:00+01:00",
            "texto": "<b>Semana 47</b>\nHola\n\n👉 https://y"}))
        self.f = d / "chatgpt.json"

    def test_antes_de_las_ocho_no_toca(self):
        toca, pasados = b.pendientes(datetime(2026, 11, 23, 6, 59, tzinfo=timezone.utc), self.tmp)
        self.assertEqual((toca, pasados), ([], []))

    def test_a_las_ocho_tocan_los_dos(self):
        toca, _ = b.pendientes(datetime(2026, 11, 23, 7, 0, tzinfo=timezone.utc), self.tmp)
        self.assertEqual({f.stem for f in toca}, {"chatgpt", "edumedia"})

    def test_pasada_la_ventana_es_fallido(self):
        toca, pasados = b.pendientes(datetime(2026, 11, 23, 15, 1, tzinfo=timezone.utc), self.tmp)
        self.assertEqual(toca, [])
        self.assertEqual(len(pasados), 2)

    def test_publica_mensaje_video_y_podcast_en_el_tema(self):
        tg = FalsoTelegram()
        self.assertTrue(b.publicar(tg, self.f, -100, registrar=lambda *_: None))
        metodos = [m for m, _ in tg.llamadas]
        self.assertEqual(metodos, ["sendMessage", "sendVideo", "sendAudio"])
        self.assertTrue(all(p.get("message_thread_id") == 19215 for _, p in tg.llamadas))
        self.assertEqual(tg.llamadas[0][1]["parse_mode"], "HTML")
        self.assertEqual(tg.llamadas[0][1]["link_preview_options"], {"is_disabled": True})
        self.assertEqual(tg.llamadas[1][1]["extra"], ["thumbnail"])
        self.assertEqual(tg.llamadas[1][1]["tipo"], "video/mp4")
        self.assertTrue(self.f.with_suffix(".publicado.json").exists())
        self.assertFalse((self.f.parent / "chatgpt-video.mp4").exists())   # ya está en Telegram
        toca, _ = b.pendientes(datetime(2026, 11, 23, 7, 5, tzinfo=timezone.utc), self.tmp)
        self.assertEqual({f.stem for f in toca}, {"edumedia"})   # no se repite

    def test_si_falla_el_video_borra_el_mensaje_y_no_apunta(self):
        tg = FalsoTelegram(falla="sendVideo")
        self.assertFalse(b.publicar(tg, self.f, -100, registrar=lambda *_: None))
        self.assertIn(("deleteMessage", {"chat_id": -100, "message_id": 101}), tg.llamadas)
        self.assertFalse(self.f.with_suffix(".publicado.json").exists())
        self.assertTrue((self.f.parent / "chatgpt-video.mp4").exists())

    def test_sin_tema_va_al_general_con_vista_previa(self):
        tg = FalsoTelegram()
        f = self.f.parent / "edumedia.json"
        self.assertTrue(b.publicar(tg, f, -200, registrar=lambda *_: None))
        self.assertEqual(len(tg.llamadas), 1)
        self.assertNotIn("message_thread_id", tg.llamadas[0][1])
        self.assertEqual(tg.llamadas[0][1]["link_preview_options"], {"is_disabled": False})


if __name__ == "__main__":
    unittest.main()
