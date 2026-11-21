# SPDX-License-Identifier: AGPL-3.0-or-later
"""Lo que el bot recuerda de lo que hizo, y rehacer el anuncio de «¡Comparte tu App!» (revisión de las
preguntas sin resolver del 21-11-2026, ADR 0052).

Sin red, sin Telegram y sin gastar API.

    .venv/bin/python -m unittest pruebas/test_memoria_programa.py
"""
import sys
import time
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "scripts"))
sys.path.insert(0, str(AQUI))
import bot  # noqa: E402
import consultar  # noqa: E402
import karla  # noqa: E402
import textos  # noqa: E402
from test_revision import bot_sin_arrancar  # noqa: E402

UID = 503
FICHA = {"titulo": "Simulador de máquinas simples", "url": "https://ejemplo.org/maquinas/", "autor": "Ana Pérez"}


class NotaDeBusquedas(unittest.TestCase):
    def test_sin_buscar(self):
        self.assertIn("sin hacer ninguna búsqueda", consultar.nota_busquedas([]))
        self.assertIn("sin hacer ninguna búsqueda", consultar.nota_busquedas(["ayuda_para_ensenar"]))

    def test_con_busquedas(self):
        nota = consultar.nota_busquedas(['buscar_mensajes({"consulta": "musicogramas", "n": 12})',
                                         'buscar_repositorio({"consulta": "música primaria"})', "preparar_incidencia"])
        self.assertIn("3 búsquedas", nota)
        self.assertIn("buscar_mensajes «musicogramas»", nota)
        self.assertIn("preparar_incidencia", nota)

    def test_larga_se_acorta(self):
        nota = consultar.nota_busquedas([f'buscar_mensajes({{"consulta": "tema {i} {"x" * 50}"}})' for i in range(20)])
        self.assertIn("20 búsquedas", nota)
        self.assertLess(len(nota), 520)

    def test_si_la_imita_se_quita(self):
        texto, marca, _ = consultar.quitar_marcas(
            "Esto es lo que hay.\n\n[Nota del programa: para esta respuesta se hicieron 2 búsquedas: x.]\n[[sin resultado]]")
        self.assertEqual(texto, "Esto es lo que hay.")
        self.assertEqual(marca, "sin resultado")


class NombresInternos(unittest.TestCase):
    NOMBRES = [h["name"] for h in consultar.HERRAMIENTAS]

    def test_con_herramienta_se_quita(self):
        t = consultar.sin_nombres_internos("Si vols canviar la llicència abans, digues-m'ho i ho farem amb `cambiar_ficha`.",
                                           self.NOMBRES, "ca")
        self.assertEqual(t, "Si vols canviar la llicència abans, digues-m'ho i ho farem.")

    def test_suelto_se_dice_con_palabras(self):
        t = consultar.sin_nombres_internos("Lo puedes pedir con tus palabras: cambiar_ficha lo hace.", self.NOMBRES, "es")
        self.assertEqual(t, "Lo puedes pedir con tus palabras: cambiar la ficha lo hace.")
        t = consultar.sin_nombres_internos("Según buscar_mensajes, no hay nada.", self.NOMBRES, "gl")
        self.assertEqual(t, "Según a busca, no hay nada.")

    def test_sin_nombres_no_cambia(self):
        t = "Para cambiar la ficha, dímelo con tus palabras."
        self.assertEqual(consultar.sin_nombres_internos(t, self.NOMBRES, "es"), t)

    def test_karla(self):
        nombres = [h["name"] for h in karla.HERRAMIENTAS + [karla.PREPARAR]]
        self.assertNotIn("preparar_incidencia", consultar.sin_nombres_internos("Lo hago con preparar_incidencia.", nombres))


class NotasDelPrograma(unittest.TestCase):
    def setUp(self):
        self.b = bot_sin_arrancar()
        self.b.token = "x"

    def test_entran_una_vez_y_caducan(self):
        b = self.b
        b.nota_programa(UID, "el bot ha enseñado una ficha.")
        b.notas_prog[UID].insert(0, (time.time() - bot.MEMORIA_MIN * 60 - 5, "una vieja."))
        notas = b.notas_pendientes(UID)
        self.assertEqual(notas, "[Nota del programa: el bot ha enseñado una ficha.]\n")
        self.assertEqual(b.notas_pendientes(UID), "")

    def test_como_mucho_cuatro(self):
        for i in range(6):
            self.b.nota_programa(UID, f"nota {i}.")
        self.assertEqual(self.b.notas_pendientes(UID).count("[Nota del programa:"), 4)


class RehacerElAnuncio(unittest.TestCase):
    def setUp(self):
        b = self.b = bot_sin_arrancar()
        b.token = "x"
        b.apuntar = lambda *a, **k: None
        b.compartir[UID] = {"ficha": FICHA, "usuario": "ana", "texto": "Ana Pérez ha compartido su simulador.",
                            "momento": time.time()}

    def botones(self, metodo="sendMessage"):
        llamada = [k for m, k in self.b.llamadas if m == metodo and k.get("reply_markup")][-1]
        return [x["callback_data"] for fila in llamada["reply_markup"]["inline_keyboard"] for x in fila]

    def test_publicar_quitar_y_rehacer(self):
        b = self.b
        b.boton_compartir(UID, "rcp")
        self.assertIn((UID, 99), b.anunciados)
        self.assertIn("ha publicado en «¡Comparte tu App!»", b.notas_pendientes(UID))
        quitar = next(c for c in self.botones() if c.startswith("rcq:"))
        b.boton_recurso(UID, quitar)
        self.assertIn(("deleteMessage", {"chat_id": bot.CATALOGO.id, "message_id": 99}), b.llamadas)
        self.assertEqual(b.llamadas[-1][1]["text"], textos.texto("es", "quitado_grupo"))
        self.assertEqual(self.botones(), ["rcr:99"])
        self.assertIn("ha quitado del grupo", b.notas_pendientes(UID))
        b.compartir.clear()
        b.boton_recurso(UID, "rcr:99")
        self.assertEqual(b.enviados[-1], textos.texto("es", "que_cambio_mensaje"))
        self.assertEqual(b.espera[UID]["que"], "cambio_compartir")
        self.assertEqual(b.compartir[UID]["texto"], "Ana Pérez ha compartido su simulador.")
        self.assertEqual(b.compartir[UID]["ficha"], FICHA)
        # El botón sirve una vez: el anuncio vuelve al circuito normal (Publicar, Cambiar…).
        b.boton_recurso(UID, "rcr:99")
        self.assertEqual(b.enviados[-1], textos.texto("es", "caducado_recurso"))

    def test_rehacer_caducado(self):
        b = self.b
        b.anunciados[(UID, 98)] = {**b.compartir.pop(UID), "momento": time.time() - 49 * 3600}
        b.boton_recurso(UID, "rcr:98")
        self.assertEqual(b.enviados[-1], textos.texto("es", "caducado_recurso"))
        self.assertNotIn(UID, b.compartir)

    def test_de_otra_persona_no(self):
        b = self.b
        b.anunciados[(UID + 1, 97)] = {**b.compartir[UID], "momento": time.time()}
        b.boton_recurso(UID, "rcr:97")
        self.assertEqual(b.enviados[-1], textos.texto("es", "caducado_recurso"))

    def test_quitado_tras_reiniciar_sin_boton(self):
        b = self.b
        n = "55"
        b.boton_recurso(UID, f"rcq:{n}:{b.firma(UID, n)}")
        self.assertEqual(b.enviados[-1], textos.texto("es", "quitado_grupo_sin_rehacer"))

    def test_textos_en_cinco_idiomas(self):
        for lengua in textos.LENGUAS:
            for clave in ("quitado_grupo", "quitado_grupo_sin_rehacer", "b_rehacer"):
                self.assertIn(clave, textos.TEXTOS[lengua], f"{clave} en {lengua}")


if __name__ == "__main__":
    unittest.main()
