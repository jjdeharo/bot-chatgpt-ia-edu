# SPDX-License-Identifier: AGPL-3.0-or-later
"""Cambios de una ficha escritos sin pulsar «Cambiar» (preguntas sin resolver del 07-11-2026, ADR 0004).

Sin red, sin Telegram y sin gastar API.

    .venv/bin/python -m unittest pruebas/test_cambio_pedido.py
"""
import sys
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "scripts"))
sys.path.insert(0, str(AQUI))
import bot  # noqa: E402
import catalogo  # noqa: E402
import consultar  # noqa: E402
import textos  # noqa: E402
from test_nombre_autor import HojaFalsa  # noqa: E402
from test_revision import bot_sin_arrancar  # noqa: E402

UID = 502
T, U = catalogo.COLUMNAS["titulo"], catalogo.COLUMNAS["url"]
PETICION = "Tres cambios: 1) Añade al principio de la descripción la idea central. 2) Idiomas: Español y English."


def fila(titulo, url, alta):
    return {**catalogo.a_fila({"titulo": titulo, "url": url, "autor": "Ana Pérez"}), catalogo.COL_CORREO: "",
            "Marca temporal": alta}


class CambioPedido(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        catalogo.DUENOS = Path(self.tmp.name) / "catalogo.json"
        b = self.b = bot_sin_arrancar()
        b.cambios_pedidos = {}
        b.lenguas[UID] = "es"
        b.cambiados = []
        b.cambiar_recurso = lambda chat, uid, peticion: b.cambiados.append((b.fichas_rec[uid]["ficha"]["url"], peticion))

    def tearDown(self):
        self.tmp.cleanup()

    def suyos(self, *filas):
        d = catalogo.leer_duenos()
        for f in filas:
            d["recursos"][catalogo.normalizar(f[U])] = UID
        catalogo.guardar_duenos(d)
        self.b.hoja = HojaFalsa(list(filas) + [fila("Ajeno", "https://ejemplo.org/ajeno", "2026-11-07T10:00:00Z")])

    def test_ficha_a_la_vista(self):
        """Con una ficha sin publicar, los cambios van a ella."""
        self.b.fichas_rec[UID] = {"ficha": {"titulo": "La cuerda", "url": "https://ejemplo.org/cuerda"},
                                  "modo": "alta", "momento": time.time()}
        self.b.cambio_pedido(UID, UID, PETICION)
        self.assertEqual(self.b.cambiados, [("https://ejemplo.org/cuerda", PETICION)])

    def test_un_solo_recurso_publicado(self):
        self.suyos(fila("La cuerda", "https://ejemplo.org/cuerda", "2026-11-07T18:18:00Z"))
        self.b.cambio_pedido(UID, UID, PETICION)
        self.assertEqual(self.b.cambiados, [("https://ejemplo.org/cuerda", PETICION)])
        self.assertEqual(self.b.fichas_rec[UID]["modo"], "modificar")

    def test_varios_elige_y_se_aplica(self):
        """Con varios, botones con el último publicado primero; al elegir, los cambios ya escritos."""
        self.suyos(fila("Atlas", "https://ejemplo.org/atlas", "2026-10-01T10:00:00Z"),
                   fila("La cuerda", "https://ejemplo.org/cuerda", "2026-11-07T18:18:00Z"),
                   fila("Fracciones", "https://ejemplo.org/fracciones", "2026-10-20T10:00:00Z"))
        self.b.cambio_pedido(UID, UID, PETICION)
        self.assertEqual(self.b.cambiados, [])
        metodo, k = self.b.llamadas[-1]
        self.assertEqual(k["text"], textos.ES["cual_cambiar"])
        botones = [fila[0] for fila in k["reply_markup"]["inline_keyboard"]]
        self.assertEqual([x["text"] for x in botones], ["La cuerda", "Fracciones", "Atlas"])
        self.b.boton_recurso(UID, botones[0]["callback_data"])
        self.assertEqual(self.b.cambiados, [("https://ejemplo.org/cuerda", PETICION)])
        self.assertNotIn(UID, self.b.cambios_pedidos)

    def test_nombra_el_recurso(self):
        self.suyos(fila("Atlas", "https://ejemplo.org/atlas", "2026-10-01T10:00:00Z"),
                   fila("La cuerda", "https://ejemplo.org/cuerda", "2026-11-07T18:18:00Z"))
        self.b.cambio_pedido(UID, UID, PETICION, "atlas")
        self.assertEqual(self.b.cambiados, [("https://ejemplo.org/atlas", PETICION)])

    def test_otro_recurso_que_el_de_la_vista(self):
        """Si nombra otro recurso que el de la ficha a la vista, va a ese otro."""
        self.suyos(fila("Atlas", "https://ejemplo.org/atlas", "2026-10-01T10:00:00Z"))
        self.b.fichas_rec[UID] = {"ficha": {"titulo": "La cuerda", "url": "https://ejemplo.org/cuerda"},
                                  "modo": "alta", "momento": time.time()}
        self.b.cambio_pedido(UID, UID, PETICION, "Atlas")
        self.assertEqual(self.b.cambiados, [("https://ejemplo.org/atlas", PETICION)])

    def test_sin_recursos(self):
        self.suyos()
        self.b.cambio_pedido(UID, UID, PETICION)
        self.assertEqual(self.b.cambiados, [])
        self.assertEqual(self.b.llamadas[-1][1]["text"], textos.ES["sin_recursos"])

    def test_boton_caducado(self):
        self.suyos(fila("Atlas", "https://ejemplo.org/atlas", "2026-10-01T10:00:00Z"),
                   fila("La cuerda", "https://ejemplo.org/cuerda", "2026-11-07T18:18:00Z"))
        self.b.cambio_pedido(UID, UID, PETICION)
        self.b.cambios_pedidos[UID]["momento"] -= bot.CADUCA_FICHA_H * 3600 + 1
        self.b.boton_recurso(UID, "rmc:0")
        self.assertEqual(self.b.cambiados, [])
        self.assertEqual(self.b.enviados[-1], textos.ES["caducado_recurso"])

    def test_nota_de_la_ficha_a_la_vista(self):
        self.assertEqual(self.b.nota_ficha(UID), "")
        self.b.fichas_rec[UID] = {"ficha": {"titulo": "La cuerda", "url": "u"}, "modo": "alta", "momento": time.time()}
        self.assertIn("«La cuerda»", self.b.nota_ficha(UID))
        self.b.fichas_rec[UID]["momento"] -= bot.CADUCA_FICHA_H * 3600 + 1
        self.assertEqual(self.b.nota_ficha(UID), "")

    def test_textos_en_los_cinco_idiomas(self):
        for lengua in textos.LENGUAS:
            for clave in ("cual_cambiar", "cual_cambiar_mas"):
                self.assertTrue(textos.TEXTOS[lengua].get(clave), (lengua, clave))


class HerramientaCambiarFicha(unittest.TestCase):
    def test_devuelve_la_accion(self):
        bloque = SimpleNamespace(type="tool_use", name="cambiar_ficha", input={"recurso": "La cuerda"}, id="t1")
        uso = SimpleNamespace(input_tokens=1, output_tokens=1, cache_read_input_tokens=0, cache_creation_input_tokens=0)
        c = consultar.Consultor.__new__(consultar.Consultor)
        c.buscadores = {"x": SimpleNamespace(al_dia=lambda: None, ultimo_momento=lambda: "2026-11-11 10:00")}
        c.cliente = SimpleNamespace(messages=SimpleNamespace(
            create=lambda **k: SimpleNamespace(content=[bloque], stop_reason="tool_use", usage=uso)))
        with mock.patch.object(consultar.Consultor, "es_ayuda", return_value=False):
            r = c.responder(PETICION, lengua="ca")
        self.assertEqual(r["accion"], {"tipo": "cambiar", "recurso": "La cuerda"})

    def test_idioma_de_la_conversacion_en_las_instrucciones(self):
        s = consultar.SISTEMA.format(hoy="h", ultimo="u", formato="f", idioma="catalán")
        self.assertIn("en catalán, el de la conversación", s)
        self.assertIn("cambiar_ficha", s)
        self.assertNotIn("sugiere cómo afinar", s)


if __name__ == "__main__":
    unittest.main()
