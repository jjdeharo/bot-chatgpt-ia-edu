# SPDX-License-Identifier: AGPL-3.0-or-later
"""El antispam de los grupos (ADR 0033), con los casos reales de la semana del 31-10-2026.

Sin red y sin Telegram: las llamadas se apuntan en una lista.

    python -m unittest pruebas/test_antispam.py
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "scripts"))
import antispam  # noqa: E402
import grupos  # noqa: E402

JUANJO = 111
GRUPO = grupos.TODOS["vce"]
VETERANO = 222


class TelegramFalso:
    def __init__(self, estado="member"):
        self.llamadas, self.estado = [], estado

    def __call__(self, metodo, **params):
        self.llamadas.append((metodo, params))
        if metodo == "getChatMember":
            return {"status": self.estado}
        return True

    def metodos(self):
        return [m for m, _ in self.llamadas]


def mensaje(uid, texto, nombre="Persona", n=1):
    return {"message_id": n, "chat": {"id": GRUPO.id, "type": "supergroup"},
            "from": {"id": uid, "first_name": nombre, "is_bot": False}, "text": texto}


class Antispam(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        datos = Path(self.dir.name) / "vce"
        datos.mkdir()
        (datos / "mensajes.jsonl").write_text(json.dumps({"id": 1, "autor_id": VETERANO}) + "\n")
        self.antes = grupos.DATOS
        grupos.DATOS = Path(self.dir.name)
        self.tg = TelegramFalso()
        self.a = antispam.Antispam(self.tg, "token", JUANJO, lambda t: None, [GRUPO])

    def tearDown(self):
        grupos.DATOS = self.antes
        self.dir.cleanup()

    def test_saludo_en_chino_de_alguien_nuevo(self):
        """«大家好» de PLus005, antes del anuncio (vceduca, 04-11-2026): fuera, con aviso a Juanjo."""
        self.assertTrue(self.a.revisar(mensaje(333, "大家好", "PLus005•Pro007全模不降智90%缓存")))
        self.assertIn("deleteMessage", self.tg.metodos())
        self.assertIn("banChatMember", self.tg.metodos())
        aviso = [p for m, p in self.tg.llamadas if m == "sendMessage"][0]
        self.assertEqual(aviso["chat_id"], JUANJO)
        self.assertIn("Deshacer", json.dumps(aviso["reply_markup"]))

    def test_varios_bots(self):
        """muqin (eXeLearning, 30-10-2026): tres bots seguidos, sin chino."""
        self.assertTrue(self.a.revisar(mensaje(333, "@xcb1cv5fdbot  @dsfsfds56bot  @cxvxcrfdsfbot", "muqin")))

    def test_un_bot_solo_no(self):
        """«/donate@AntiUserbotsBot» o «@askplexbot» de alguien nuevo: legítimos en la historia de los grupos."""
        self.assertFalse(self.a.revisar(mensaje(333, "/donate@AntiUserbotsBot")))
        self.assertFalse(self.a.revisar(mensaje(334, "Probad @askplexbot")))

    def test_texto_corriente_de_alguien_nuevo(self):
        self.assertFalse(self.a.revisar(mensaje(333, "¡Hola, compañeros! Os comparto algo por si a alguien le sirve.")))
        self.assertNotIn("banChatMember", self.tg.metodos())

    def test_quien_ya_habia_escrito(self):
        self.assertFalse(self.a.revisar(mensaje(VETERANO, "大家好")))

    def test_administradores_no(self):
        self.tg.estado = "administrator"
        self.assertFalse(self.a.revisar(mensaje(333, "大家好")))
        self.assertNotIn("banChatMember", self.tg.metodos())

    def test_rafaga(self):
        """Las flechas de «J G» (ChatGPT-IA-edu, 02-11-2026): más de 5 mensajes en un minuto."""
        echado = [self.a.revisar(mensaje(333, "⬇️⬇️⬇️⬇️", "J G", n)) for n in range(1, 8)]
        self.assertEqual(echado[:5], [False] * 5)
        self.assertTrue(echado[5])
        borrados = {p["message_id"] for m, p in self.tg.llamadas if m == "deleteMessage"}
        self.assertTrue({1, 2, 3, 4, 5, 6} <= borrados)
        self.assertTrue(echado[6])  # lo que llega después, también fuera

    def test_entrada_con_nombre_cirilico(self):
        cambio = {"chat": {"id": GRUPO.id}, "old_chat_member": {"status": "left"},
                  "new_chat_member": {"status": "member", "user": {"id": 333, "first_name": "Антон", "is_bot": False}}}
        self.a.entrada(cambio)
        self.assertIn("banChatMember", self.tg.metodos())

    def test_entrada_de_quien_ya_habia_escrito(self):
        cambio = {"chat": {"id": GRUPO.id}, "old_chat_member": {"status": "left"},
                  "new_chat_member": {"status": "member", "user": {"id": VETERANO, "first_name": "科汉", "is_bot": False}}}
        self.a.entrada(cambio)
        self.assertNotIn("banChatMember", self.tg.metodos())

    def test_entrada_con_nombre_corriente(self):
        cambio = {"chat": {"id": GRUPO.id}, "old_chat_member": {"status": "left"},
                  "new_chat_member": {"status": "member", "user": {"id": 333, "first_name": "Ana", "is_bot": False}}}
        self.a.entrada(cambio)
        self.assertEqual(self.tg.llamadas, [])

    def test_deshacer(self):
        self.a.revisar(mensaje(333, "大家好"))
        datos = f"as:{GRUPO.id}:333:{self.a.firma(GRUPO.id, 333)}"
        ajeno = {"from": {"id": 999}, "data": datos, "message": {}}
        self.assertTrue(self.a.deshacer(ajeno))
        self.assertNotIn("unbanChatMember", self.tg.metodos())  # solo Juanjo
        falso = {"from": {"id": JUANJO}, "data": f"as:{GRUPO.id}:333:0000000000", "message": {}}
        self.a.deshacer(falso)
        self.assertNotIn("unbanChatMember", self.tg.metodos())  # con la firma mal, nada
        self.assertTrue(self.a.deshacer({"from": {"id": JUANJO}, "data": datos, "message": {}}))
        self.assertIn("unbanChatMember", self.tg.metodos())
        self.assertFalse(self.a.revisar(mensaje(333, "大家好", n=9)))  # readmitido: ya no cuenta como nuevo

    def test_otros_botones_no_son_suyos(self):
        self.assertFalse(self.a.deshacer({"from": {"id": JUANJO}, "data": "val:+"}))


if __name__ == "__main__":
    unittest.main()
