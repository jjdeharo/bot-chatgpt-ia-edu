# SPDX-License-Identifier: AGPL-3.0-or-later
"""Pruebas de los controles corregidos tras la revisión del 31-10-2026 (ADR 0019).

Sin red, sin Telegram y sin gastar API: los objetos se crean sin su constructor y lo que
habla con fuera se sustituye por funciones que apuntan lo que se les pide.

    .venv/bin/python -m unittest pruebas/test_revision.py
"""
import io
import json
import sys
import tempfile
import time
import unittest
import urllib.request
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "scripts"))
import bot  # noqa: E402
import catalogo  # noqa: E402
import consultar  # noqa: E402
import fichas  # noqa: E402
import karla  # noqa: E402
import textos  # noqa: E402
import textos_karla  # noqa: E402


def bot_sin_arrancar(clase=bot.Bot):
    """Un bot con sus diccionarios vacíos y sin Telegram: tg apunta las llamadas y enviar, los textos."""
    b = clase.__new__(clase)
    for nombre in ("memoria", "pendientes", "miembros", "espera", "fichas_rec", "listas", "lenguas", "recientes",
                   "compartir", "rechazados", "ambitos", "valorables", "borradores"):
        setattr(b, nombre, {})
    b.llamadas, b.enviados = [], []
    b.tg = lambda metodo, **k: (b.llamadas.append((metodo, k)), {"message_id": 99})[1]
    b.enviar = lambda chat, texto, formato=None: b.enviados.append(texto)
    return b


class BusquedaPorAutor(unittest.TestCase):
    def test_buscar_autor_ya_no_falla(self):
        """T1: había dos métodos «autores» y el segundo tapaba al primero (TypeError en cada uso)."""
        c = consultar.Consultor.__new__(consultar.Consultor)
        c.buscadores = {}
        self.assertEqual(c.herramienta("buscar_autor", {"nombre": "Ana"}), [])
        self.assertEqual(c.nombres_del_grupo(), set())


class PermisoDeCompartir(unittest.TestCase):
    def ficha(self, licencia):
        return f"**TÍTULO**\n\nReferencia.\n\n**Resumen**\nTexto.\n\n**Palabras clave**\n#ia\n\n**Licencia**\n{licencia}\n\n(Para crear…)"

    def test_frase_literal(self):
        self.assertFalse(fichas.se_puede_compartir(self.ficha("No se podrá compartir con el grupo ChatGPT-IA-edu: © 2025.")))

    def test_otra_redaccion(self):
        """T2: antes, una prohibición dicha de otra forma dejaba adjuntar el archivo."""
        self.assertFalse(fichas.se_puede_compartir(self.ficha("Todos los derechos reservados. No se puede compartir el archivo.")))
        self.assertFalse(fichas.se_puede_compartir(self.ficha("© 2024 Editorial Ejemplo")))
        self.assertFalse(fichas.se_puede_compartir(self.ficha("El documento no indica licencia.")))

    def test_sin_apartado(self):
        self.assertFalse(fichas.se_puede_compartir("**TÍTULO**\n\nSolo un resumen."))

    def test_abiertas(self):
        for lic in ("Creative Commons Atribución-NoComercial-CompartirIgual 4.0 Internacional (CC BY-NC-SA 4.0)",
                    "CC BY 4.0", "CC0 1.0 Universal", "Dominio público", "GNU General Public License v3 (GPL-3.0)",
                    "El titular permite expresamente su libre distribución."):
            self.assertTrue(fichas.se_puede_compartir(self.ficha(lic)), lic)

    def fichero(self, respuesta):
        """Un Fichero cuyo Claude contesta lo dado (o falla, si es una excepción)."""
        f = fichas.Fichero.__new__(fichas.Fichero)
        f.c = mock.Mock()
        r = mock.Mock(usage=mock.Mock(input_tokens=100, output_tokens=20, cache_read_input_tokens=0,
                                      cache_creation_input_tokens=0))
        if isinstance(respuesta, Exception):
            f.c.cliente.messages.create.side_effect = respuesta
        else:
            r.content = [mock.Mock(type="text", text=json.dumps(respuesta))]
            f.c.cliente.messages.create.return_value = r
        return f

    def test_una_mencion_no_es_un_permiso(self):
        """Segunda revisión: «no está bajo Creative Commons» y «trabaja en el MIT» pasaban el filtro de expresiones."""
        for lic in ("No está bajo una licencia Creative Commons.",
                    "Licencia propietaria; no autoriza la distribución. El autor trabaja en el MIT."):
            f = self.fichero({"licencia": "", "permite_compartir": False})
            self.assertEqual(f.compartible(self.ficha(lic)), (False, mock.ANY), lic)
            self.assertTrue(f.c.cliente.messages.create.called, "la decisión la toma Claude, no las expresiones")

    def test_las_dos_lecturas_tienen_que_coincidir(self):
        ficha = self.ficha("CC BY 4.0")
        self.assertTrue(self.fichero({"licencia": "CC BY 4.0", "permite_compartir": True}).compartible(ficha)[0])
        self.assertFalse(self.fichero({"licencia": "", "permite_compartir": True}).compartible(ficha)[0])
        self.assertFalse(self.fichero({"licencia": "propietaria", "permite_compartir": True}).compartible(ficha)[0])
        self.assertFalse(self.fichero({"licencia": "CC BY 4.0", "permite_compartir": False}).compartible(ficha)[0])

    def test_sin_claude_solo_la_ficha(self):
        f = self.fichero(RuntimeError("sin red"))
        with mock.patch("sys.stderr", new_callable=io.StringIO):
            self.assertEqual(f.compartible(self.ficha("CC BY 4.0")), (False, 0.0))

    def test_lo_cerrado_no_pregunta_a_claude(self):
        f = self.fichero({"licencia": "CC BY 4.0", "permite_compartir": True})
        self.assertEqual(f.compartible(self.ficha("© 2024 Editorial Ejemplo")), (False, 0.0))
        self.assertFalse(f.c.cliente.messages.create.called)


class DireccionesPublicas(unittest.TestCase):
    def test_internas(self):
        """T4: una dirección interna o local no llega a la red."""
        for url in ("http://127.0.0.1:9999/prueba", "http://localhost/", "http://192.168.1.10/", "http://10.0.0.1/x",
                    "http://[::1]/", "http://significado:8000/salud", "ftp://ejemplo.com/", "file:///etc/passwd",
                    "http://169.254.169.254/latest/meta-data", "http://nas.local/"):
            self.assertFalse(catalogo.direccion_publica(url), url)

    def test_publica(self):
        with mock.patch.object(catalogo.socket, "getaddrinfo", return_value=[(2, 1, 6, "", ("93.184.216.34", 443))]):
            self.assertTrue(catalogo.direccion_publica("https://ejemplo.com/app"))

    def test_leer_url_avisa_sin_pedirla(self):
        with mock.patch.object(catalogo._ABRIDOR, "open", side_effect=AssertionError("no debía pedirse")):
            texto, aviso = catalogo.leer_url("http://127.0.0.1:9999/prueba")
        self.assertEqual((texto, aviso), ("", catalogo.AVISO_NO_PUBLICA))

    def test_redireccion_interna(self):
        pet = urllib.request.Request("https://acortador.ejemplo/x")
        with self.assertRaises(catalogo.NoPublica):
            catalogo._SoloPublicas().redirect_request(pet, None, 302, "Found", {}, "http://10.0.0.5/admin")


class Zip(unittest.TestCase):
    def test_no_se_descomprime_entero(self):
        """T5: un ZIP de 4 KB con una entrada de 4 MB no se carga entera en memoria."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("index.html", b"0" * 4_000_000)
            z.writestr("carpeta/", b"")
        datos = buf.getvalue()
        self.assertLess(len(datos), 10_000)
        pedidos = []
        original = zipfile.ZipExtFile.read

        def medido(self, n=-1):
            pedidos.append(n)
            return original(self, n)

        with mock.patch.object(zipfile.ZipExtFile, "read", medido):
            texto = catalogo.leer_archivo("app.zip", datos)
        self.assertTrue(pedidos and max(pedidos) <= catalogo.MAX_CODIGO + 1, pedidos)
        self.assertLessEqual(len(texto), catalogo.MAX_CODIGO)


class Idioma(unittest.TestCase):
    def test_telegram_sin_ia(self):
        b = bot_sin_arrancar()
        b.en_hilo = lambda *a: self.fail("no debía detectarse nada")
        b.fijar_lengua(7, {"language_code": "ca"})
        self.assertEqual(b.lenguas[7], "ca")

    def test_deteccion_tras_permisos_y_presupuesto(self):
        """T3: la detección se pide solo cuando ya se sabe que es miembro y queda presupuesto."""
        b = bot_sin_arrancar()
        hilos = []
        b.en_hilo = lambda f, *a: hilos.append(a)
        with mock.patch.object(bot, "leer_estado", return_value={}), \
                mock.patch.object(bot, "contabilidad", return_value={"usd_mes": bot.TOPE_MES_USD}):
            b.lengua_de_la_frase(7, "hola, qué tal todo")
        self.assertEqual(hilos, [])
        with mock.patch.object(bot, "leer_estado", return_value={}), \
                mock.patch.object(bot, "contabilidad", return_value={"usd_mes": 0.0}):
            b.lengua_de_la_frase(7, "/ayuda por favor")
            b.lengua_de_la_frase(7, "https://ejemplo.com")
            self.assertEqual(hilos, [])
            b.lengua_de_la_frase(7, "hola, qué tal todo")
        self.assertEqual(len(hilos), 1)
        bot.DETECCIONES.release()  # el hilo simulado no ha corrido

    def test_con_la_frecuencia_agotada_no_detecta(self):
        """Segunda revisión: a quien se le va a pedir pausa no se le lanza la detección."""
        b = bot_sin_arrancar()
        b.en_hilo = lambda *a: self.fail("se programó una detección con las consultas agotadas")
        b.recientes[7] = [time.time()] * bot.SEGUIDAS_HORA
        with mock.patch.object(bot, "leer_estado", return_value={}), \
                mock.patch.object(bot, "contabilidad", return_value={"usd_mes": 0.0}):
            b.lengua_de_la_frase(7, "hola, qué tal todo")
        b.enviar = lambda chat, texto, formato=None: b.enviados.append(texto)
        with mock.patch.object(bot, "registrar"):
            self.assertTrue(b.seguidas(7, 7))
        self.assertEqual(b.enviados, [textos.texto("es", "seguidas")])

    def test_el_semaforo_se_devuelve_si_falla(self):
        b = bot_sin_arrancar()
        b.consultor = mock.Mock()
        b.consultor.cliente.messages.create.side_effect = RuntimeError("sin red")
        with mock.patch.object(bot, "registrar"):
            bot.DETECCIONES.acquire()
            b.detectar_lengua(7, "hola, qué tal")
        self.assertTrue(bot.DETECCIONES.acquire(blocking=False))
        bot.DETECCIONES.release()

    def test_no_miembro_no_detecta(self):
        b = bot_sin_arrancar()
        b.en_hilo = lambda *a: self.fail("se programó una detección para alguien rechazado")
        b.grupos_de = lambda uid, **k: set()
        with mock.patch.object(bot, "ABIERTO", True):
            b.atender({"chat": {"id": 7, "type": "private"}, "from": {"id": 7, "language_code": "es"},
                       "text": "hola, qué tal todo"})
        self.assertEqual(b.enviados, [textos.texto("es", "no_miembro")])


class BotonesConClave(unittest.TestCase):
    def cq(self, data, uid=7):
        return {"id": "1", "from": {"id": uid, "language_code": "es"}, "data": data,
                "message": {"chat": {"id": uid}, "message_id": 5}}

    def test_biblioteca_boton_antiguo(self):
        """T6: el botón de una ficha anterior no publica la vigente."""
        b = bot_sin_arrancar()
        b.pendientes[7] = {"clave": "bbb", "momento": time.time(), "ficha": "**X**", "compartir": False}
        b.boton(self.cq("publicar:aaa"))
        self.assertEqual(b.enviados, [textos.texto("es", "sustituido")])
        self.assertIn(7, b.pendientes)

    def test_botones_sin_clave(self):
        """Segunda revisión: un botón anterior al despliegue, sin clave, tampoco publica el borrador nuevo."""
        b = bot_sin_arrancar()
        b.pendientes[7] = {"clave": "bbb", "momento": time.time(), "ficha": "**X**", "compartir": False}
        b.fichas_rec[7] = {"clave": "bbb", "momento": time.time(), "ficha": {}, "modo": "alta"}
        b.publicar = b.publicar_recurso = lambda *a: self.fail("se publicó con un botón sin clave")
        b.boton(self.cq("publicar"))
        b.boton_recurso(7, "rp")
        b.boton_recurso(7, "rc")
        self.assertEqual(b.enviados, [textos.texto("es", "sustituido")] * 3)
        self.assertIn(7, b.pendientes)
        self.assertIn(7, b.fichas_rec)
        k = bot_sin_arrancar(karla.Karla)
        k.borradores[7] = {"clave": "bbb", "momento": time.time(), "titulo": "T", "cuerpo": "C", "repositorio": "exelearning/x"}
        k.grupos_de = lambda uid, **kw: self.fail("se llegó a la incidencia con un botón sin clave")
        k.boton_karla(self.cq("inc:si"))
        k.boton_karla(self.cq("inc:no"))
        self.assertEqual(k.enviados, [textos_karla.texto("es", "sustituido")] * 2)
        self.assertIn(7, k.borradores)

    def test_publicar_pregunta_a_telegram_aunque_haya_cache(self):
        """Segunda revisión: la pertenencia guardada (una hora) no vale para publicar en nombre de alguien."""
        b = bot_sin_arrancar()
        b.miembros[7] = (time.time(), {"chatgpt", "vce"})
        b.tg = lambda metodo, **k: (b.llamadas.append((metodo, k)), {"status": "left"})[1]
        self.assertEqual(b.grupos_de(7), {"chatgpt", "vce"})
        self.assertEqual(b.llamadas, [])
        self.assertEqual(b.grupos_de(7, al_dia=True), set())
        self.assertTrue(all(m == "getChatMember" for m, k in b.llamadas) and b.llamadas)

    def test_biblioteca_boton_vigente_recomprueba_el_grupo(self):
        b = bot_sin_arrancar()
        b.pendientes[7] = {"clave": "bbb", "momento": time.time(), "ficha": "**X**", "compartir": False}
        b.grupos_de = lambda uid, **k: set()
        b.boton(self.cq("publicar:bbb"))
        self.assertEqual(b.enviados, [textos.texto("es", "solo_chatgpt")])
        self.assertNotIn(7, b.pendientes)

    def test_catalogo_boton_antiguo(self):
        b = bot_sin_arrancar()
        b.fichas_rec[7] = {"clave": "bbb", "momento": time.time(), "ficha": {}, "modo": "alta"}
        b.boton_recurso(7, "rp:aaa")
        b.boton_recurso(7, "rx:aaa")
        self.assertEqual(b.enviados, [textos.texto("es", "sustituido")] * 2)
        self.assertIn(7, b.fichas_rec)

    def test_karla_boton_antiguo(self):
        k = bot_sin_arrancar(karla.Karla)
        k.borradores[7] = {"clave": "bbb", "momento": time.time(), "titulo": "T", "cuerpo": "C", "repositorio": "exelearning/x"}
        k.boton_karla(self.cq("inc:si:aaa"))
        self.assertEqual(k.enviados, [textos_karla.texto("es", "sustituido")])
        self.assertIn(7, k.borradores)

    def test_vista_previa_nueva_quita_botones_de_la_anterior(self):
        k = bot_sin_arrancar(karla.Karla)
        k.borradores[7] = {"clave": "aaa", "momento": time.time(), "mensaje": (7, 41)}
        k.ensenar_borrador(7, 7, "", {"titulo": "T", "cuerpo": "x" * 6000, "repositorio": "exelearning/x"})
        quitados = [k for m, k in k.llamadas if m == "editMessageReplyMarkup"]
        self.assertEqual(quitados[0]["message_id"], 41)
        enviados = [k for m, k in k.llamadas if m == "sendMessage"]
        self.assertEqual(len(enviados), 3)  # 6000 caracteres: dos trozos y el último con los botones
        self.assertIn(k.borradores[7]["clave"], enviados[-1]["reply_markup"]["inline_keyboard"][0][0]["callback_data"])
        self.assertNotIn("reply_markup", enviados[0])

    def test_un_reintento_no_repite_el_documento(self):
        b = bot_sin_arrancar()
        p = {"ficha": "**X**\n\nRef.", "file_id": "f", "autor": "A", "compartir": True, "doc": {"message_id": 7}}
        b.publicar(p)
        self.assertNotIn("sendDocument", [m for m, _ in b.llamadas])


class MensajesSeguidos(unittest.TestCase):
    def test_tope_de_espera(self):
        """A: un chorro de mensajes juntables no retiene el bucle sin fin."""
        b = bot_sin_arrancar()
        n = [0]

        def tg(metodo, **k):
            n[0] += 1
            return [{"update_id": n[0], "message": {"chat": {"id": 7, "type": "private"}, "from": {"id": 7}, "text": "más"}}]
        b.tg = tg
        updates = tg("getUpdates")
        with mock.patch.object(bot, "JUNTAR_MAX_S", 0.05):
            salida = b.esperar_seguidos(updates)
        self.assertLessEqual(n[0], 101)  # la primera llamada es la de la prueba
        self.assertEqual(len(salida), 1)  # todo junto en una consulta


class Limpieza(unittest.TestCase):
    def test_sin_resolver_caduca_sin_preguntas_nuevas(self):
        """C: la limpieza ya no depende de que entre otra pregunta."""
        vieja = (datetime.now(timezone.utc) - timedelta(days=61)).isoformat(timespec="seconds")
        nueva = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "sin-resolver.jsonl"
            f.write_text(json.dumps({"fecha": vieja, "motivo": "x", "pregunta": "a"}) + "\n"
                         + json.dumps({"fecha": nueva, "motivo": "x", "pregunta": "b"}) + "\n")
            with mock.patch.object(bot, "SIN_RESOLVER", f):
                bot.purgar_sin_resolver()
            self.assertEqual([json.loads(l)["pregunta"] for l in f.read_text().splitlines()], ["b"])

    def test_memoria_y_borradores_caducados_se_borran(self):
        b = bot_sin_arrancar()
        hace = time.time() - 48 * 3600
        b.memoria[1], b.memoria[2] = (hace, []), (time.time(), [])
        b.pendientes[1] = {"momento": hace}
        b.recientes[1] = [hace]
        with mock.patch.object(bot, "purgar_sin_resolver"):
            b.limpiar()
        self.assertEqual(set(b.memoria), {2})
        self.assertEqual((b.pendientes, b.recientes), ({}, {}))
        k = bot_sin_arrancar(karla.Karla)
        k.borradores[1] = {"momento": hace}
        with mock.patch.object(bot, "purgar_sin_resolver"):
            k.limpiar()
        self.assertEqual(k.borradores, {})


if __name__ == "__main__":
    unittest.main()
