# SPDX-License-Identifier: AGPL-3.0-or-later
"""El final del plazo de los avisos de la revisión del repositorio (ADR 0039).

Sin red, sin Telegram y sin gastar API: la hoja, la comprobación y Telegram son de mentira y la fecha, simulada.

    .venv/bin/python -m unittest pruebas/test_plazos.py
"""
import json
import sys
import tempfile
import threading
import unittest
from datetime import datetime, timezone
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "scripts"))
sys.path.insert(0, str(AQUI))
import bot  # noqa: E402
import catalogo  # noqa: E402
import plazos  # noqa: E402
from test_revision import bot_sin_arrancar  # noqa: E402

U, T, AU = catalogo.COLUMNAS["url"], catalogo.COLUMNAS["titulo"], catalogo.COLUMNAS["autor"]
CERROJO = threading.Lock()
JUANJO = 1000


class Hoja:
    """La hoja: buscar como la de verdad (sin distinguir mayúsculas), y apunta lo que se borra o se cambia."""

    def __init__(self, filas):
        self.lista, self.borrados, self.licencias, self.altas = filas, [], [], []

    def buscar(self, url):
        return next((f for f in self.lista if catalogo.normalizar(f[U]) == catalogo.normalizar(url)), None)

    def borrar(self, url):
        self.borrados.append(url)
        self.lista = [f for f in self.lista if catalogo.normalizar(f[U]) != catalogo.normalizar(url)]

    def poner_licencia(self, url, licencia):
        self.licencias.append((url, licencia))

    def alta_fila(self, fila):
        self.altas.append(fila)
        self.lista.append(fila)


def fila(url, titulo, correo=""):
    return {"Marca temporal": "2025-06-01T10:00:00.000Z", U: url, T: titulo, AU: "Ana Pérez",
            catalogo.COL_CORREO: correo, "Licencia de uso": ""}


def aviso(tipo, plazo="2026-11-29", estado="pendiente"):
    return {"tipo": tipo, "motivo": "m", "titulo": f"aviso {tipo}", "aviso": "2026-10-29", "plazo": plazo,
            "estado": estado}


# Lo que diría «Ya lo he corregido» de cada enlace
RESULTADOS = {
    "https://a.github.io/Roto": {"resultado": "no_abre", "detalle": "El servidor responde con el código 404."},
    "https://a.github.io/arreglado": {"resultado": "cumple", "licencia": "AGPL v3", "usd": 0.002},
    "https://a.github.io/abre-sin-licencia": {"resultado": "sin_licencia", "usd": 0.001},
    "https://b.es/copyright": {"resultado": "sin_licencia", "usd": 0.001},
    "https://g.co/gemini/share/x": {"resultado": "plataforma"},
}


class Plazos(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        catalogo.AVISOS, catalogo.DUENOS = d / "avisos.json", d / "catalogo.json"
        plazos.ESTADO, plazos.RETIRADOS = d / "plazos.json", d / "retirados.json"
        catalogo.guardar_avisos({
            "https://a.github.io/roto": aviso("B"),
            "https://a.github.io/arreglado": aviso("B"),
            "https://a.github.io/abre-sin-licencia": aviso("B"),
            "https://a.github.io/quitado": aviso("B"),
            "https://g.co/gemini/share/x": aviso("B"),
            "https://b.es/copyright": aviso("D"),
            "https://b.es/en-revision": aviso("D", estado="por_revisar"),
            "https://c.es/sin-licencia": aviso("A"),
            "https://chatgpt.com/g/g-abc": aviso("C", plazo="2026-12-11"),
            "https://chatgpt.com/g/g-def": aviso("C", plazo="2026-12-11"),
        })
        catalogo.guardar_duenos({"recursos": {"https://a.github.io/roto": 7}, "correos": {"8": ["eva@x.es"]},
                                 "nombres": {}})
        self.hoja = Hoja([fila("https://a.github.io/Roto", "Roto"), fila("https://a.github.io/arreglado", "Arreglado"),
                          fila("https://a.github.io/abre-sin-licencia", "Abre"), fila("https://g.co/gemini/share/x", "Gemini"),
                          fila("https://b.es/copyright", "Copyright", "eva@x.es"), fila("https://b.es/en-revision", "Rev"),
                          fila("https://c.es/sin-licencia", "Sin licencia"), fila("https://chatgpt.com/g/g-ABC", "GPT 1"),
                          fila("https://chatgpt.com/g/g-def", "GPT 2")])
        self.comprobados = []
        self.juanjo_antes = bot.JUANJO

    def tearDown(self):
        self.tmp.cleanup()
        bot.JUANJO = self.juanjo_antes

    def comprobar(self, url):
        self.comprobados.append(url)
        return RESULTADOS[url]

    def revisar(self, plazo="2026-11-29"):
        return plazos.revisar(plazo, self.hoja, self.comprobar, lambda url: None, CERROJO)

    def test_cuando_toca(self):
        antes = datetime(2026, 11, 29, 7, 59, tzinfo=timezone.utc)   # 8:59 en Madrid
        a_las_nueve = datetime(2026, 11, 29, 8, 0, tzinfo=timezone.utc)
        self.assertIsNone(plazos.vencido(ahora=datetime(2026, 11, 14, 12, tzinfo=timezone.utc)))
        self.assertIsNone(plazos.vencido(ahora=antes))
        self.assertEqual(plazos.vencido(ahora=a_las_nueve), "2026-11-29")
        self.revisar()
        self.assertIsNone(plazos.vencido(ahora=a_las_nueve))     # una sola vez
        self.assertIsNone(plazos.vencido(ahora=datetime(2026, 12, 11, 7, 59, tzinfo=timezone.utc)))
        self.assertEqual(plazos.vencido(ahora=datetime(2026, 12, 11, 8, 0, tzinfo=timezone.utc)), "2026-12-11")

    def test_si_el_bot_estaba_parado_lo_hace_al_volver(self):
        self.assertEqual(plazos.vencido(ahora=datetime(2026, 12, 2, 10, tzinfo=timezone.utc)), "2026-11-29")

    def test_revision_del_29(self):
        r = self.revisar()
        avisos = catalogo.leer_avisos()
        # Se comprueba con el enlace de la hoja (con sus mayúsculas), no con la clave normalizada
        self.assertIn("https://a.github.io/Roto", self.comprobados)
        self.assertEqual(avisos["https://a.github.io/arreglado"]["estado"], "corregido")
        self.assertEqual(self.hoja.licencias, [("https://a.github.io/arreglado", "AGPL v3")])
        self.assertEqual(avisos["https://a.github.io/quitado"]["estado"], "sin_ficha")
        # Un B que ya se abre sin licencia se queda, como los A
        self.assertEqual(avisos["https://a.github.io/abre-sin-licencia"]["tipo"], "A")
        self.assertEqual(avisos["https://a.github.io/abre-sin-licencia"]["estado"], "pendiente")
        # Lo que tiene Juanjo en revisión manual, ni se comprueba ni se lista; los A y los GPT, tampoco el 29
        self.assertNotIn("https://b.es/en-revision", self.comprobados)
        self.assertEqual(avisos["https://c.es/sin-licencia"], aviso("A"))
        lista = {i["clave"]: i for i in r["lista"]}
        self.assertEqual(set(lista), {"https://a.github.io/roto", "https://b.es/copyright", "https://g.co/gemini/share/x"})
        self.assertTrue(lista["https://a.github.io/roto"]["marcado"])
        self.assertTrue(lista["https://b.es/copyright"]["marcado"])
        self.assertFalse(lista["https://g.co/gemini/share/x"]["marcado"])   # no se puede comprobar: lo decide él
        self.assertEqual(len(r["por_revisar"]), 1)
        # Nada se ha retirado todavía
        self.assertEqual(self.hoja.borrados, [])
        self.assertEqual(avisos["https://a.github.io/roto"]["estado"], "pendiente")

    def test_mensaje_y_botones(self):
        r = self.revisar()
        t = plazos.texto("2026-11-29", r)
        self.assertIn("hoy, 29/11/2026", t)
        self.assertIn("1 ya cumplen", t)
        self.assertIn("Siguen sin cumplir (3)", t)
        self.assertIn("desfijo el aviso", t)
        b = plazos.botones("2026-11-29", r)["inline_keyboard"]
        self.assertEqual(len(b), 4)
        self.assertTrue(all(len(x["callback_data"].encode()) <= 64 for fila_ in b for x in fila_))
        self.assertEqual(b[-1][0]["text"], "Retirar los marcados (2)")

    def test_los_gpt_el_11(self):
        r = self.revisar("2026-12-11")
        self.assertEqual(self.comprobados, [])   # no tienen arreglo: no se comprueban
        self.assertEqual([i["url"] for i in r["lista"]], ["https://chatgpt.com/g/g-ABC", "https://chatgpt.com/g/g-def"])
        t = plazos.texto("2026-12-11", r)
        self.assertIn("los GPT de ChatGPT", t)
        self.assertNotIn("desfijo", t)

    def bot(self):
        b = bot_sin_arrancar()
        b.hoja = self.hoja
        bot.JUANJO = JUANJO
        return b

    def test_retirar_con_copia_y_desfijar(self):
        self.revisar()
        b = self.bot()
        m = {"chat": {"id": JUANJO}, "message_id": 5}
        b.boton_plazo("pz:2026-11-29:2", m)       # desmarca el tercero (el de copyright)
        self.assertIn("⬜ 3.", b.llamadas[-1][1]["reply_markup"]["inline_keyboard"][2][0]["text"])
        b.boton_plazo("pz:2026-11-29:2", m)       # y lo vuelve a marcar
        b.boton_plazo("pzr:2026-11-29", m)
        self.assertEqual(sorted(self.hoja.borrados), ["https://a.github.io/Roto", "https://b.es/copyright"])
        copia = plazos.leer_retirados()
        self.assertEqual(copia["https://a.github.io/roto"]["fila"][T], "Roto")
        self.assertEqual(copia["https://a.github.io/roto"]["dueno_uid"], 7)
        self.assertEqual(copia["https://b.es/copyright"]["dueno_uid"], 8)   # por el correo ligado
        avisos = catalogo.leer_avisos()
        self.assertEqual(avisos["https://a.github.io/roto"]["estado"], "retirado")
        self.assertEqual(avisos["https://g.co/gemini/share/x"]["estado"], "pendiente")   # no estaba marcado
        self.assertNotIn("https://a.github.io/roto", catalogo.leer_duenos()["recursos"])
        self.assertIn(("unpinChatMessage", {"chat_id": -1002503665937, "message_id": 14274}), b.llamadas)
        self.assertIn("Retirados del repositorio: 2", b.enviados[-1])
        # Un segundo toque no retira dos veces
        b.boton_plazo("pzr:2026-11-29", m)
        self.assertEqual(len(self.hoja.borrados), 2)
        self.assertEqual(b.enviados[-1], "Esa lista ya está decidida.")

    def test_lo_corregido_despues_de_la_lista_no_se_retira(self):
        self.revisar()
        d = catalogo.leer_avisos()
        d["https://a.github.io/roto"]["estado"] = "corregido"   # su autor pulsa «Ya lo he corregido» a las 10
        catalogo.guardar_avisos(d)
        b = self.bot()
        b.boton_plazo("pzr:2026-11-29", {})
        self.assertEqual(self.hoja.borrados, ["https://b.es/copyright"])
        self.assertIn("mientras tanto", b.enviados[-1])

    def test_no_retirar(self):
        self.revisar()
        b = self.bot()
        b.boton_plazo("pzn:2026-11-29", {"chat": {"id": JUANJO}, "message_id": 5})
        self.assertEqual(self.hoja.borrados, [])
        self.assertNotIn("unpinChatMessage", [x[0] for x in b.llamadas])
        self.assertEqual(plazos.leer_estado()["2026-11-29"]["estado"], "no_retirar")
        b.boton_plazo("pzr:2026-11-29", {})
        self.assertEqual(self.hoja.borrados, [])

    def test_ninguno_marcado(self):
        self.revisar()
        b = self.bot()
        for n in (0, 2):
            b.boton_plazo(f"pz:2026-11-29:{n}", {})
        b.boton_plazo("pzr:2026-11-29", {})
        self.assertEqual(self.hoja.borrados, [])
        self.assertIn("No hay ninguno marcado", b.enviados[-1])
        self.assertEqual(plazos.leer_estado()["2026-11-29"]["estado"], "esperando")

    def test_solo_juanjo_toca_los_botones(self):
        self.revisar()
        b = self.bot()
        b.en_hilo = lambda f, *a: f(*a)
        b.boton({"id": "1", "from": {"id": 55, "language_code": "es"}, "data": "pzr:2026-11-29",
                 "message": {"chat": {"id": 55}, "message_id": 3}})
        self.assertEqual(self.hoja.borrados, [])

    def test_restaurar(self):
        self.revisar()
        b = self.bot()
        b.boton_plazo("pzr:2026-11-29", {})
        self.assertEqual(plazos.restaurar("https://a.github.io/Roto/", self.hoja), "Restaurado.")
        alta = self.hoja.altas[-1]
        self.assertEqual(alta[U], "https://a.github.io/Roto")
        self.assertNotIn("Marca temporal", alta)
        self.assertNotIn(catalogo.COL_CORREO, alta)   # el correo no va a la hoja, que es pública
        self.assertEqual(catalogo.leer_duenos()["recursos"]["https://a.github.io/roto"], 7)
        self.assertEqual(catalogo.leer_avisos()["https://a.github.io/roto"]["estado"], "restaurado")
        self.assertEqual(plazos.restaurar("https://a.github.io/roto", self.hoja), "Ya está en el repositorio.")

    def test_un_fallo_al_comprobar_no_marca(self):
        def falla(url):
            raise TimeoutError
        r = plazos.revisar("2026-11-29", self.hoja, falla, lambda url: None, CERROJO)
        self.assertTrue(all(not i["marcado"] for i in r["lista"]))
        self.assertEqual(json.loads(catalogo.AVISOS.read_text())["https://a.github.io/arreglado"]["estado"], "pendiente")


class YaLoHeCorregido(unittest.TestCase):
    """«Ya lo he corregido» usa ahora catalogo.comprobar_licencia, la misma comprobación que el plazo: hace lo mismo."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        catalogo.AVISOS = Path(self.tmp.name) / "avisos.json"
        catalogo.guardar_avisos({"https://a.github.io/app": aviso("D")})
        self.b = b = bot_sin_arrancar()
        b.puede_preparar = lambda chat, uid: True
        b.gastos, b.pasados = [], []
        b.apuntar = lambda usd, **k: b.gastos.append(usd)
        b.pasar_a_juanjo = lambda uid, f, clave: b.pasados.append(clave)
        b.hoja = Hoja([])
        self.leer, self.plataforma, self.respuesta = catalogo.leer_url, catalogo.es_de_plataforma, None
        catalogo.es_de_plataforma = lambda u: "gemini" in u   # la de verdad sigue las redirecciones por la red
        b.recursos = type("R", (), {"comprobar": lambda _, url, texto: (self.respuesta, 0.002)})()

    def tearDown(self):
        catalogo.leer_url, catalogo.es_de_plataforma = self.leer, self.plataforma
        self.tmp.cleanup()

    def pulsar(self, url="https://a.github.io/app", leido=("<p>hola</p>", None), **respuesta):
        catalogo.leer_url = lambda u: leido
        self.respuesta = {"licencia_abierta": False, "de_pago": False, "pago_detalle": "", "licencia": "",
                          "licencia_contenidos": "", **respuesta}
        self.b.comprobar_aviso(5, {"url": url, "titulo": "App", "autor": "Ana"})

    def test_cumple(self):
        self.pulsar(licencia_abierta=True, licencia="MIT")
        self.assertEqual(catalogo.leer_avisos()["https://a.github.io/app"]["estado"], "corregido")
        self.assertEqual(self.b.hoja.licencias, [("https://a.github.io/app", "MIT")])
        self.assertEqual(self.b.gastos, [0.002])

    def test_no_abre_no_gasta(self):
        self.pulsar(leido=("", "No se abre."))
        self.assertIn("Sigue sin abrirse. No se abre.", self.b.enviados[-1])
        self.assertEqual(self.b.gastos, [])

    def test_de_pago(self):
        self.pulsar(de_pago=True, pago_detalle="suscripción")
        self.assertIn("suscripción", self.b.enviados[-1])
        self.assertEqual(catalogo.leer_avisos()["https://a.github.io/app"]["estado"], "pendiente")

    def test_sin_licencia(self):
        self.pulsar()
        self.assertEqual(self.b.llamadas[-1][0], "sendMessage")
        self.assertEqual(catalogo.leer_avisos()["https://a.github.io/app"]["estado"], "pendiente")

    def test_plataforma(self):
        catalogo.guardar_avisos({"https://g.co/gemini/share/x": aviso("B")})
        self.pulsar(url="https://g.co/gemini/share/x")
        self.assertEqual(self.b.pasados, ["aviso_plataforma"])


if __name__ == "__main__":
    unittest.main()
