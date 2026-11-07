# SPDX-License-Identifier: AGPL-3.0-or-later
"""El mensaje citado en privado va delante de la pregunta (ADR 0034), con el aviso de un comentario del
diario como caso real: texto con negritas y dos enlaces escondidos en el texto.

    python -m unittest pruebas/test_citado.py
"""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "scripts"))
import bot  # noqa: E402

BOT, PERSONA = 900, 222
AVISO = ("Diario de IA Educativa\n\nComentario nuevo de docente en «Docentes debaten si hace falta la "
         "autorización de las familias»:\n\nMuy útil.\n\nVer en el diario · Ver en GitHub")


def entidad(texto, trozo, url):
    """Una entidad text_link como las da Telegram: posiciones en UTF-16."""
    antes = texto[:texto.index(trozo)]
    return {"type": "text_link", "offset": len(antes.encode("utf-16-le")) // 2,
            "length": len(trozo.encode("utf-16-le")) // 2, "url": url}


class Citado(unittest.TestCase):
    def setUp(self):
        self.bot = SimpleNamespace(id=BOT)

    def citar(self, citado, pregunta="¿De qué va esto?"):
        msg = {"from": {"id": PERSONA}, "reply_to_message": citado}
        return bot.Bot.con_citado(self.bot, msg, pregunta)

    def test_sin_cita_queda_igual(self):
        self.assertEqual(bot.Bot.con_citado(self.bot, {"from": {"id": PERSONA}}, "Hola"), "Hola")

    def test_aviso_del_diario_con_sus_enlaces(self):
        r = self.citar({"from": {"id": BOT}, "text": AVISO, "entities": [
            {"type": "bold", "offset": 0, "length": 22},
            entidad(AVISO, "Ver en el diario", "https://diarioiaeducativa.github.io/2026-11-06/a.html#t-comentarios"),
            entidad(AVISO, "Ver en GitHub", "https://github.com/x/y/discussions/1#c")]})
        self.assertTrue(r.startswith("[Responde citando un mensaje tuyo: «Diario de IA Educativa"))
        self.assertIn("Ver en el diario: https://diarioiaeducativa.github.io/2026-11-06/a.html#t-comentarios", r)
        self.assertIn("Ver en GitHub: https://github.com/x/y/discussions/1#c", r)
        self.assertTrue(r.endswith("]\n\n¿De qué va esto?"))

    def test_posiciones_en_utf16_con_emoji(self):
        texto = "👉 Mira esto: enlace"
        r = self.citar({"from": {"id": BOT}, "text": texto, "entities": [entidad(texto, "enlace", "https://e.org")]})
        self.assertIn("enlace: https://e.org", r)

    def test_quien_escribio_el_citado(self):
        self.assertIn("un mensaje suyo", self.citar({"from": {"id": PERSONA}, "text": "Lo mío"}))
        self.assertIn("citando un mensaje:", self.citar({"from": {"id": 333}, "caption": "De otra persona"}))

    def test_citado_largo_se_recorta(self):
        r = self.citar({"from": {"id": BOT}, "text": "a" * (bot.LARGO_CITADO + 500)})
        self.assertIn("a" * bot.LARGO_CITADO + "…»", r)
        self.assertNotIn("a" * (bot.LARGO_CITADO + 1), r)


if __name__ == "__main__":
    unittest.main()
