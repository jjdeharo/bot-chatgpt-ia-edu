# SPDX-License-Identifier: AGPL-3.0-or-later
"""Las descripciones de las imágenes de los grupos (ADR 0028).

Sin red, sin Telegram y sin gastar API.

    .venv/bin/python -m unittest pruebas/test_imagenes.py
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "scripts"))
import corpus  # noqa: E402
import imagenes  # noqa: E402


class GrupoFalso:
    def __init__(self, datos: Path):
        self.datos = datos
        self.biblioteca = None


class Imagenes(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.g = GrupoFalso(Path(self.tmp.name))
        ms = [{"id": 1, "fecha": "2026-11-03T18:39+01:00", "autor": "Ana", "tema": 1, "responde_a": None,
               "texto": "Claude y yo trabajando juntos", "media": "Photo"},
              {"id": 2, "fecha": "2026-11-03T18:40+01:00", "autor": "Luis", "tema": 1, "responde_a": None,
               "texto": "Un vídeo", "media": "Document", "mime": "video/mp4"}]
        (self.g.datos / "mensajes.jsonl").write_text("\n".join(json.dumps(m) for m in ms) + "\n")
        (self.g.datos / "imagenes").mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def test_que_se_describe(self):
        self.assertTrue(imagenes.es_imagen({"media": "Photo"}))
        self.assertTrue(imagenes.es_imagen({"media": "Document", "mime": "image/png"}))
        self.assertFalse(imagenes.es_imagen({"media": "Document", "mime": "video/mp4"}))
        self.assertFalse(imagenes.es_imagen({"media": "WebPage"}))

    def test_tipo_por_los_primeros_bytes(self):
        self.assertEqual(imagenes.tipo_de(b"\xff\xd8\xff\xe0resto"), "image/jpeg")
        self.assertEqual(imagenes.tipo_de(b"\x89PNG\r\n\x1a\nresto"), "image/png")
        self.assertEqual(imagenes.tipo_de(b"RIFF1234WEBPresto"), "image/webp")
        self.assertEqual(imagenes.tipo_de(b"%PDF-1.7"), "")

    def test_la_descripcion_llega_al_texto_que_se_busca(self):
        (self.g.datos / "imagenes" / "1.txt").write_text("Meme de un robot y una persona programando.\n")
        ms = corpus.cargar(self.g)
        self.assertEqual(ms[1]["imagen"], "Meme de un robot y una persona programando.")
        self.assertIn("[imagen: Meme de un robot", corpus.contenido(ms[1]))
        self.assertNotIn("imagen", ms[2])

    def test_lo_borrado_en_telegram_se_borra(self):
        (self.g.datos / "imagenes" / "1.txt").write_text("sigue\n")
        (self.g.datos / "imagenes" / "99.txt").write_text("borrado\n")
        imagenes.limpiar(self.g, corpus.cargar(self.g))
        self.assertTrue((self.g.datos / "imagenes" / "1.txt").exists())
        self.assertFalse((self.g.datos / "imagenes" / "99.txt").exists())

    def test_gasto_por_mes(self):
        imagenes.GASTO = self.g.datos / "gasto.json"
        g = {}
        imagenes.apuntar(g, "2026-11", 0.0003)
        imagenes.apuntar(g, "2026-11", 0.0002)
        self.assertEqual(g["2026-11"], {"imagenes": 2, "usd": 0.0005})


if __name__ == "__main__":
    unittest.main()
