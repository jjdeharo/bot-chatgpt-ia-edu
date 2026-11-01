# SPDX-License-Identifier: AGPL-3.0-or-later
"""Pruebas de los controles corregidos tras la revisión del 31-10-2026 (ADR 0019).

Sin red, sin Telegram y sin gastar API: los objetos se crean sin su constructor y lo que
habla con fuera se sustituye por funciones que apuntan lo que se les pide.

    .venv/bin/python -m unittest pruebas/test_revision.py
"""
import io
import json
import os
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
import documentacion  # noqa: E402
import karla  # noqa: E402
import textos  # noqa: E402
import textos_karla  # noqa: E402


def bot_sin_arrancar(clase=bot.Bot):
    """Un bot con sus diccionarios vacíos y sin Telegram: tg apunta las llamadas y enviar, los textos."""
    b = clase.__new__(clase)
    for nombre in ("memoria", "pendientes", "miembros", "espera", "fichas_rec", "listas", "lenguas", "recientes",
                   "compartir", "rechazados", "ambitos", "valorables", "borradores", "al_grupo"):
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


class InformeDelUnoDeNoviembre(unittest.TestCase):
    """Las correcciones del informe del 01-11-2026 (ADR 0020)."""

    def test_respuesta_vacia_lleva_texto_fijo(self):
        b = bot_sin_arrancar()
        b.lenguas[7] = "ca"
        r = {"texto": "", "sin_resolver": None}
        with mock.patch.object(bot, "registrar"):
            b.texto_o_nada(7, r, "pregunta")
        self.assertEqual(r["texto"], textos.texto("ca", "respuesta_vacia"))
        self.assertEqual(r["sin_resolver"], "respuesta vacía")
        r = {"texto": "Hola", "sin_resolver": None}
        b.texto_o_nada(7, r, "pregunta")
        self.assertEqual(r["texto"], "Hola")

    def test_envio_rechazado_no_cuenta_como_entregado(self):
        b = bot_sin_arrancar()
        b.tg = lambda metodo, **k: (b.llamadas.append(metodo), None)[1]
        with mock.patch.object(bot, "registrar"):
            self.assertFalse(b.enviar_valorable(7, 7, "x", "p", False))
        b.tg = lambda metodo, **k: {"message_id": 5}
        self.assertTrue(b.enviar_valorable(7, 7, "x", "p", False))

    def test_quitar_solo_quien_publico(self):
        """«Quitarlo de la Biblioteca» y «Quitarlo del grupo» llevan una firma atada a la cuenta."""
        b = bot_sin_arrancar()
        b.token, b.hoja, b.listas = "token-de-prueba", None, {}
        firma = b.firma(7, "-100", "11-12")
        self.assertTrue(b.firmado(7, firma, "-100", "11-12"))
        self.assertFalse(b.firmado(8, firma, "-100", "11-12"))  # otra cuenta
        self.assertFalse(b.firmado(7, firma, "-100", "11-13"))  # otros mensajes
        borrados = []
        b.tg = lambda metodo, **k: (borrados.append(k) if metodo == "deleteMessage" else None, {"message_id": 1})[1]
        b.boton({"id": "q", "from": {"id": 8, "language_code": "es"}, "data": f"bq:-100:11-12:{firma}"})
        b.boton({"id": "q", "from": {"id": 8, "language_code": "es"}, "data": "bq:-100:11-12"})
        self.assertEqual(borrados, [])
        self.assertEqual(b.enviados, [textos.texto("es", "no_tuyo")] * 2)
        b.boton_recurso(8, f"rcq:11:{b.firma(7, 11)}")
        b.boton_recurso(8, "rcq:11")
        self.assertEqual(borrados, [])
        with mock.patch.object(bot, "registrar"):
            b.boton_recurso(7, f"rcq:11:{b.firma(7, 11)}")
        self.assertEqual(len(borrados), 1)

    def test_telegram_reintenta_tras_429(self):
        tg = bot.Telegram("x")
        respuestas = [urllib.error.HTTPError("u", 429, "x", {}, io.BytesIO(b'{"parameters":{"retry_after":1}}')),
                      mock.MagicMock(**{"__enter__.return_value": io.BytesIO(b'{"ok":true,"result":{"id":1}}')})]
        with mock.patch.object(urllib.request, "urlopen", side_effect=respuestas), \
                mock.patch.object(bot.time, "sleep") as dormir, mock.patch.object(bot, "registrar"):
            self.assertEqual(tg("getMe"), {"id": 1})
        dormir.assert_called_once_with(1)

    def test_repuesto_html_con_encabezados_tablas_y_citas(self):
        h = bot.respuesta_html("### Pasos\n\n| Opción | Qué hace |\n|---|---|\n| A | algo |\n\n> cita\n\n**ok**")
        self.assertIn("<b>Pasos</b>", h)
        self.assertIn("• <b>A</b> — Qué hace: algo", h)
        self.assertIn("<blockquote>cita</blockquote>", h)
        self.assertNotIn("###", h)
        self.assertNotIn("|", h)

    def test_pregunta_larga_avisa_del_recorte(self):
        b = bot_sin_arrancar()
        self.assertEqual(b.pregunta("x" * 100, []), "x" * 100)
        larga = b.pregunta("x" * (bot.LARGO_PREGUNTA + 1), [])
        self.assertTrue(larga.endswith(bot.NOTA_RECORTE))
        self.assertEqual(len(larga), bot.LARGO_PREGUNTA + len(bot.NOTA_RECORTE))

    def test_enlace_de_telegram_es_una_pregunta(self):
        self.assertTrue(bot.ENLACE_TELEGRAM.match("https://t.me/vceduca/7674/13698"))
        self.assertFalse(bot.ENLACE_TELEGRAM.match("https://ejemplo.github.io/app/"))

    def test_responder_al_bot_sin_pregunta_no_cuenta(self):
        b = bot_sin_arrancar()
        b.id, b.usuario = 1, "IAEducativa_bot"
        respuesta = {"reply_to_message": {"from": {"id": 1}}, "text": "gracias"}
        self.assertFalse(b.le_hablan(respuesta))
        self.assertTrue(b.le_hablan({**respuesta, "text": "¿y esto cómo se usa?"}))
        self.assertTrue(b.le_hablan({"text": "@IAEducativa_bot hola"}))
        k = bot_sin_arrancar(karla.Karla)
        k.id, k.usuario = 2, "eXeKarlaBot"
        self.assertEqual(k.comando_en_grupo({"text": "/misrecursos"}), "")  # no es suyo
        self.assertEqual(k.comando_en_grupo({"text": "/ayuda"}), "ayuda")

    def test_nombres_largos_de_creative_commons(self):
        f = "**T**\n\n**Licencia**\nReconocimiento-CompartirIgual 4.0 Internacional\n\n(x)"
        self.assertTrue(fichas.se_puede_compartir(f))
        self.assertTrue(fichas.se_puede_compartir(f.replace("Reconocimiento-CompartirIgual 4.0 Internacional", "Attribution 4.0 International")))

    def test_textos_nuevos_en_los_cinco_idiomas(self):
        for mod in (textos, textos_karla):
            for lengua in textos.LENGUAS:
                for clave in ("respuesta_vacia", "codigo", "valoracion_antigua"):
                    self.assertIn(clave, mod.TEXTOS[lengua], (mod.__name__, lengua, clave))
                self.assertIn("{version}", mod.TEXTOS[lengua]["codigo"])
                self.assertNotIn("anónim", mod.TEXTOS[lengua]["ayuda_final"].lower())


class MejorasDelUnoDeNoviembre(unittest.TestCase):
    """Las mejoras 3 a 7 del informe del 01-11-2026 (ADR 0021)."""

    def test_reenvio_con_su_origen(self):
        fecha = int(datetime(2026, 10, 30, 10, 0, tzinfo=timezone.utc).timestamp())
        msg = {"chat": {"id": 7, "type": "private"}, "from": {"id": 7}, "text": "¿esto se arregló?",
               "forward_origin": {"type": "user", "date": fecha, "sender_user": {"first_name": "Ana", "last_name": "Pérez"}}}
        self.assertEqual(bot.origen(msg), "[Mensaje reenviado, escrito por Ana Pérez el 2026-10-30 11:00]")
        self.assertEqual(bot.origen({**msg, "forward_origin": {"type": "hidden_user", "sender_user_name": "Luis", "date": fecha}}),
                         "[Mensaje reenviado, escrito por Luis el 2026-10-30 11:00]")
        self.assertEqual(bot.origen({"text": "hola"}), "")
        salida = bot.juntar([{"update_id": 1, "message": msg}])
        self.assertTrue(salida[0]["message"]["text"].startswith("[Mensaje reenviado, escrito por Ana Pérez"))
        self.assertTrue(salida[0]["message"]["text"].endswith("¿esto se arregló?"))

    def test_leer_elpx(self):
        """Un .elpx se resume sin extraer nada a disco; uno que no es ZIP o sin content.xml se dice."""
        xml = ("<ode><odeProperties><odeProperty><key>pp_title</key><value>Prueba</value></odeProperty>"
               "<odeProperty><key>pp_exelearning_version</key><value>v4.0.6</value></odeProperty></odeProperties>"
               "<odeNavStructures><odeNavStructure><pageName>Inicio</pageName><odeIdeviceTypeName>text</odeIdeviceTypeName>"
               "<htmlView><![CDATA[<p>mucho html</p>]]></htmlView></odeNavStructure></odeNavStructures></ode>")
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("content.xml", xml)
            z.writestr("index.html", "<html></html>")
        r = karla.leer_elpx("proyecto.elpx", buf.getvalue())
        self.assertIn("[Archivo adjunto: proyecto.elpx] 2 entradas", r)
        self.assertIn("pp_exelearning_version=v4.0.6", r)
        self.assertIn("Páginas (1): Inicio", r)
        self.assertIn("text ×1", r)
        self.assertNotIn("mucho html", r)
        self.assertIn("No es un archivo ZIP válido", karla.leer_elpx("x.elpx", b"no soy un zip"))
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("index.html", "")
        self.assertIn("No lleva content.xml", karla.leer_elpx("x.zip", buf.getvalue()))

    def test_seguimiento_de_incidencias(self):
        k = bot_sin_arrancar(karla.Karla)
        k.lenguas[7] = "ca"
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "seguimiento.json"
            leida = {"titulo": "Bug", "estado": "open", "motivo": None, "enlace": "https://github.com/x/y/issues/5",
                     "comentarios": [], "n_comentarios": 0}
            with mock.patch.object(karla, "SEGUIMIENTO", f), mock.patch.object(karla, "incidencia", return_value=leida), \
                    mock.patch.object(bot, "registrar"):
                k.decidir_seguimiento(7, "sig:si:exelearning/exelearning#5", {})
                self.assertEqual(karla.leer_seguimiento()["exelearning/exelearning#5"]["uid"], 7)
                self.assertEqual(k.enviados[-1], textos_karla.texto("ca", "seguir_si"))
                k.decidir_seguimiento(7, "sig:si:otro/repo#5", {})  # fuera de la organización: no se sigue
                self.assertEqual(k.enviados[-1], textos_karla.texto("ca", "seguir_no"))
                # Un comentario nuevo se cuenta en el idioma de la persona; el cierre, y se deja de seguir
                leida["comentarios"], leida["n_comentarios"] = [{"autor": "dev", "fecha": "2026-11-02", "texto": "Fixed"}], 1
                k.revisar_seguimientos()
                self.assertIn("dev", k.enviados[-1])
                self.assertTrue(k.enviados[-1].startswith("Novetat"))
                k.revisar_seguimientos()
                self.assertTrue(k.enviados[-1].startswith("Novetat"))  # el mismo comentario no se repite
                self.assertEqual(len([e for e in k.enviados if e.startswith("Novetat")]), 1)
                leida.update(estado="closed", motivo="completed")
                k.revisar_seguimientos()
                self.assertIn("corregida o resuelta", k.enviados[-1])
                self.assertEqual(karla.leer_seguimiento(), {})

    def test_archivo_elpx_entra_como_pregunta(self):
        k = bot_sin_arrancar(karla.Karla)
        k.token = "t"
        self.assertIsNone(k.archivo_exe(7, 7, {"document": {"file_name": "foto.pdf"}}))
        self.assertEqual(k.archivo_exe(7, 7, {"document": {"file_name": "p.elpx", "file_size": 30 * 1024 * 1024}}), "")
        self.assertEqual(k.enviados[-1], textos_karla.texto("es", "archivo_grande"))

    def test_vigilar_documentacion(self):
        with tempfile.TemporaryDirectory() as tmp:
            c = Path(tmp) / "docs"
            c.mkdir()
            (c / "manual.md").write_text("x")
            self.assertTrue(documentacion.vigilar([c], 3))
            viejo = time.time() - 10 * 86400
            os.utime(c / "manual.md", (viejo, viejo))
            with mock.patch.dict(os.environ, {"DATOS_BOT": tmp, "JUANJO": ""}), \
                    mock.patch("sys.stdout", new_callable=io.StringIO) as salida:
                self.assertFalse(documentacion.vigilar([c], 3))
            self.assertIn("10 días sin cambiar", salida.getvalue())

    def test_textos_del_seguimiento_en_los_cinco_idiomas(self):
        for lengua in textos.LENGUAS:
            for clave in ("seguir_pregunta", "b_si_avisar", "b_no_avisar", "seguir_si", "seguir_no",
                          "incidencia_novedad", "incidencia_cerrada", "archivo_grande"):
                self.assertIn(clave, textos_karla.TEXTOS[lengua], (lengua, clave))


class NotasDeVoz(unittest.TestCase):
    """ADR 0022: una nota de voz sigue como pregunta escrita; sin servicio o demasiado larga, un aviso."""

    def test_sin_servicio(self):
        b = bot_sin_arrancar()
        with mock.patch.object(bot, "VOZ_URL", ""):
            self.assertEqual(b.voz_a_texto(7, 7, {"voice": {"file_id": "x", "duration": 5}}), "")
        self.assertEqual(b.enviados, [textos.texto("es", "sin_voz")])
        self.assertIsNone(b.voz_a_texto(7, 7, {"text": "hola"}))

    def test_demasiado_larga(self):
        b = bot_sin_arrancar()
        with mock.patch.object(bot, "VOZ_URL", "http://voz:8001"):
            self.assertEqual(b.voz_a_texto(7, 7, {"voice": {"file_id": "x", "duration": 600}}), "")
        self.assertEqual(b.enviados, [textos.texto("es", "audio_largo", minutos=3)])

    def test_transcripcion_sigue_como_pregunta(self):
        b = bot_sin_arrancar()
        b.escribiendo = lambda chat: mock.Mock()
        b.transcribir = lambda file_id: {"texto": "com exporto a SCORM", "lengua": "ca", "duracion": 4.2}
        with mock.patch.object(bot, "VOZ_URL", "http://voz:8001"), mock.patch.object(bot, "registrar"):
            self.assertEqual(b.voz_a_texto(7, 7, {"voice": {"file_id": "x", "duration": 4}}), "com exporto a SCORM")
        self.assertEqual(b.lenguas[7], "ca")  # el idioma detectado vale para los textos fijos
        self.assertEqual(b.enviados[-1], textos_karla.texto("ca", "entendido", texto="com exporto a SCORM"))
        b.transcribir = lambda file_id: {"texto": "", "lengua": ""}
        with mock.patch.object(bot, "VOZ_URL", "http://voz:8001"):
            self.assertEqual(b.voz_a_texto(7, 7, {"voice": {"file_id": "x", "duration": 4}}), "")
        self.assertEqual(b.enviados[-1], textos.texto("ca", "audio_vacio"))


class PreguntarEnElGrupo(unittest.TestCase):
    """ADR 0023: lo que el bot no ha sabido responder se puede llevar al grupo, viéndolo antes."""

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.parche = mock.patch.object(bot, "PREGUNTAS_GRUPO", Path(self.dir.name) / "preguntas-grupo.json")
        self.parche.start()
        self.reg = mock.patch.object(bot, "registrar")
        self.reg.start()

    def tearDown(self):
        self.parche.stop()
        self.reg.stop()
        self.dir.cleanup()

    def bot(self, clase=bot.Bot, suyos=("chatgpt", "vce")):
        b = bot_sin_arrancar(clase)
        b.token, b.id = "token", 555
        b.grupos_de = lambda uid, al_dia=False: set(suyos)
        if clase is not bot.Bot:
            del b.ambitos  # Karla no acota la búsqueda por grupos
        return b

    DE = {"id": 7, "first_name": "Ana", "last_name": "Pérez"}

    def preparar(self, b, ofrecer=True, fotos=()):
        b.enviar_valorable(7, 7, "No lo he encontrado.", "¿cómo se hace X?", True,
                           al_grupo={"texto": "¿Cómo se hace X?", "fotos": list(fotos)}, ofrecer=ofrecer)
        return b.al_grupo[7]["clave"]

    def botones(self, llamada):
        return [x["callback_data"] for fila in llamada[1]["reply_markup"]["inline_keyboard"] for x in fila]

    def test_se_ofrece_si_no_encuentra_nada(self):
        b = self.bot()
        clave = self.preparar(b)
        envio = next(c for c in b.llamadas if c[0] == "sendRichMessage")
        self.assertEqual(self.botones(envio), ["val:+", "val:-", f"pg:{clave}"])
        b2 = self.bot()
        self.preparar(b2, ofrecer=False)
        envio = next(c for c in b2.llamadas if c[0] == "sendRichMessage")
        self.assertEqual(self.botones(envio), ["val:+", "val:-"])

    def test_con_pulgar_abajo_queda_el_boton_del_grupo(self):
        b = self.bot()
        clave = self.preparar(b, ofrecer=False)
        with mock.patch.object(bot, "guardar_sin_resolver"), mock.patch.object(bot, "leer_estado", return_value={}), \
                mock.patch.object(bot, "contabilidad", return_value={"utiles_hoy": 0, "utiles_mes": 0,
                                                                     "no_utiles_hoy": 0, "no_utiles_mes": 0}), \
                mock.patch.object(bot, "guardar_estado"):
            b.valorar({"id": "q", "from": {"id": 7}, "data": "val:-", "message": {"chat": {"id": 7}, "message_id": 99}})
        edicion = [c for c in b.llamadas if c[0] == "editMessageReplyMarkup"][-1]
        self.assertEqual(self.botones(edicion), [f"pg:{clave}"])

    def test_vista_previa_antes_de_publicar(self):
        b = self.bot()
        clave = self.preparar(b)
        b.llamadas.clear()
        b.pregunta_grupo(7, f"pg:{clave}", {}, self.DE)
        self.assertEqual([c[0] for c in b.llamadas], ["sendMessage"])  # nada en el grupo todavía
        vista = b.llamadas[0][1]
        self.assertEqual(vista["chat_id"], 7)
        self.assertIn("Ana Pérez", vista["text"])
        self.assertIn("¿Cómo se hace X?", vista["text"])
        self.assertEqual(self.botones(b.llamadas[0]), [f"pgp:{clave}:chatgpt", f"pgp:{clave}:vce", f"pgx:{clave}"])

    def test_publicar_guarda_quien_y_ofrece_quitarla(self):
        b = self.bot(suyos=("vce",))
        clave = self.preparar(b)
        b.llamadas.clear()
        b.pregunta_grupo(7, f"pgp:{clave}:vce", {}, self.DE)
        grupo, privado = b.llamadas
        self.assertEqual(grupo[1]["chat_id"], bot.grupos.TODOS["vce"].id)
        self.assertIn('<a href="tg://user?id=7">Ana Pérez</a>', grupo[1]["text"])
        d = bot.leer_preguntas_grupo()
        self.assertEqual(list(d.values())[0]["uid"], 7)
        quitar = self.botones(privado)[0]
        self.assertTrue(quitar.startswith(f"pgq:{bot.grupos.TODOS['vce'].id}:99:"))
        self.assertNotIn(7, b.al_grupo)  # una pregunta se lleva una sola vez
        b.llamadas.clear()
        b.pregunta_grupo(7, f"pgp:{clave}:vce", {}, self.DE)
        self.assertEqual(b.llamadas, [])
        self.assertEqual(b.enviados[-1], textos.texto("es", "pregunta_caducada"))

    def test_boton_viejo_o_de_otro_grupo_no_publica(self):
        b = self.bot(suyos=("vce",))
        self.preparar(b)
        b.llamadas.clear()
        b.pregunta_grupo(7, "pgp:000000:vce", {}, self.DE)
        clave = b.al_grupo[7]["clave"]
        b.pregunta_grupo(7, f"pgp:{clave}:chatgpt", {}, self.DE)  # no es miembro de ese grupo
        self.assertFalse([c for c in b.llamadas if c[0] == "sendMessage"])

    def test_tope_diario(self):
        b = self.bot(suyos=("vce",))
        for _ in range(bot.PREGUNTAS_GRUPO_DIA):
            clave = self.preparar(b)
            b.pregunta_grupo(7, f"pgp:{clave}:vce", {}, self.DE)
        b.llamadas.clear()
        clave = self.preparar(b)
        b.llamadas.clear()
        b.pregunta_grupo(7, f"pgp:{clave}:vce", {}, self.DE)
        self.assertFalse([c for c in b.llamadas if c[0] == "sendMessage"])
        self.assertEqual(b.enviados[-1], textos.texto("es", "pregunta_tope", n=bot.PREGUNTAS_GRUPO_DIA))

    def test_con_una_imagen_va_como_foto(self):
        b = self.bot(suyos=("vce",))
        clave = self.preparar(b, fotos=["foto1"])
        b.llamadas.clear()
        b.pregunta_grupo(7, f"pgp:{clave}:vce", {}, self.DE)
        self.assertEqual(b.llamadas[0][0], "sendPhoto")
        self.assertLessEqual(len(b.llamadas[0][1]["caption"]), 1024)

    def test_respuesta_en_el_grupo_llega_por_privado(self):
        b = self.bot(suyos=("vce",))
        g = bot.grupos.TODOS["vce"]
        bot.guardar_preguntas_grupo({f"{g.id}:50": {"uid": 7, "ids": [50], "grupo": "vce", "momento": time.time(),
                                                    "lengua": "ca"}})
        ajeno = {"chat": {"id": g.id}, "message_id": 61, "from": {"id": 8, "first_name": "Luis"},
                 "text": "Prueba con el menú Herramientas", "reply_to_message": {"message_id": 50, "from": {"id": 555}}}
        with mock.patch.object(bot.grupos, "ACTIVOS", {"vce": g}):
            self.assertTrue(b.respuesta_a_pregunta(ajeno))
        self.assertEqual(b.enviados[-1], textos.texto("ca", "respuesta_en_grupo", quien="Luis",
                                                      extracto="Prueba con el menú Herramientas",
                                                      enlace=f"{g.enlace}/61"))
        propio = {**ajeno, "from": {"id": 7, "first_name": "Ana"}}
        n = len(b.enviados)
        self.assertTrue(b.respuesta_a_pregunta(propio))  # quien preguntó no se avisa a sí mismo
        self.assertEqual(len(b.enviados), n)
        otro = {**ajeno, "reply_to_message": {"message_id": 51, "from": {"id": 555}}}
        self.assertFalse(b.respuesta_a_pregunta(otro))  # otro mensaje del bot: sigue como siempre

    def test_caducan_a_la_semana(self):
        g = bot.grupos.TODOS["vce"]
        bot.guardar_preguntas_grupo({f"{g.id}:50": {"uid": 7, "ids": [50], "momento": time.time() - 8 * 86400}})
        self.assertEqual(bot.leer_preguntas_grupo(), {})

    def test_solo_quien_la_llevo_la_quita(self):
        b = self.bot(suyos=("vce",))
        g = bot.grupos.TODOS["vce"]
        bot.guardar_preguntas_grupo({f"{g.id}:50": {"uid": 7, "ids": [50], "momento": time.time()}})
        b.pregunta_grupo(8, f"pgq:{g.id}:50:{b.firma(7, g.id, 50)}", {}, {"id": 8})
        self.assertFalse([c for c in b.llamadas if c[0] == "deleteMessage"])
        b.pregunta_grupo(7, f"pgq:{g.id}:50:{b.firma(7, g.id, 50)}", {}, self.DE)
        self.assertEqual([c[1]["message_id"] for c in b.llamadas if c[0] == "deleteMessage"], [50])
        self.assertEqual(bot.leer_preguntas_grupo(), {})

    def test_edumedia_no_es_destino(self):
        b = self.bot(suyos=("edumedia", "vce"))
        self.assertEqual([g.clave for g in b.grupos_para_preguntar(7)], ["vce"])

    def test_karla_con_sus_textos(self):
        b = self.bot(karla.Karla, suyos=("exelearning",))
        clave = self.preparar(b)
        b.llamadas.clear()
        with mock.patch.object(bot.grupos, "ACTIVOS", {"exelearning": bot.grupos.TODOS["exelearning"]}):
            b.pregunta_grupo(7, f"pg:{clave}", {}, self.DE)
        self.assertIn("documentación de eXeLearning", b.llamadas[0][1]["text"])
        self.assertEqual(self.botones(b.llamadas[0]), [f"pgp:{clave}:exelearning", f"pgx:{clave}"])


class SinResolverPorTemas(unittest.TestCase):
    def guardar(self, f, preguntas):
        f.write_text("".join(json.dumps({"fecha": "2026-11-01T10:00:00+00:00", "motivo": m, "pregunta": q}) + "\n"
                             for m, q in preguntas))

    def test_pocas_no_gastan(self):
        cliente = mock.Mock()
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "s.jsonl"
            self.guardar(f, [("sin resultado", "a"), ("error", "b")])
            with mock.patch.object(bot, "SIN_RESOLVER", f):
                temas, errores, uso = bot.temas_sin_resolver(cliente, "ctx", ["x"])
        cliente.messages.create.assert_not_called()
        self.assertEqual(len(errores), 1)
        texto = bot.a_texto(bot.bloques_temas(temas, errores, uso))
        self.assertIn("Son pocas", texto)
        self.assertIn("1 falló por un error", texto)

    def test_temas_con_las_preguntas_literales(self):
        bloque = mock.Mock(type="text", text=json.dumps({"temas": [
            {"tema": "Exportar a SCORM", "preguntas": [1, 2, 99], "falta": "f", "solucion": "x", "propuesta": "p"},
            {"tema": "Repetida", "preguntas": [2], "falta": "", "solucion": "x", "propuesta": ""}]}))
        cliente = mock.Mock()
        cliente.messages.create.return_value = mock.Mock(content=[bloque], usage=mock.Mock(
            input_tokens=1000, output_tokens=200, cache_read_input_tokens=0, cache_creation_input_tokens=0))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "s.jsonl"
            self.guardar(f, [("sin resultado", f"pregunta {i}") for i in range(1, 7)] + [("error", "fallo")])
            with mock.patch.object(bot, "SIN_RESOLVER", f):
                temas, errores, uso = bot.temas_sin_resolver(cliente, "ctx", ["x"])
        enviado = cliente.messages.create.call_args.kwargs["messages"][0]["content"]
        self.assertNotIn("fallo", enviado)  # los errores del programa no se mandan
        self.assertEqual([t["tema"] for t in temas], ["Sin tema", "Exportar a SCORM"])  # 4 sueltas, 2 en el tema
        self.assertEqual([g["pregunta"] for g in temas[1]["preguntas"]], ["pregunta 1", "pregunta 2"])
        self.assertGreater(uso["usd"], 0)
        html_ = bot.a_html(bot.bloques_temas(temas, errores, uso))
        self.assertIn("<b>2. Exportar a SCORM: 2 preguntas</b>", html_)


if __name__ == "__main__":
    unittest.main()
