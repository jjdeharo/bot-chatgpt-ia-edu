# SPDX-License-Identifier: AGPL-3.0-or-later
"""El documento de un enlace para la Biblioteca digital (ADR 0035), sin red ni API.

    .venv/bin/python -m unittest pruebas/test_documento_web.py
"""
import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import bot  # noqa: E402
import biblioteca_duplicados as duplicados  # noqa: E402
import documento_web as dw  # noqa: E402
import fichas  # noqa: E402

PDF = b"%PDF-1.7\n" + b"x" * 1000
ANUNCIO = "https://www.ejemplo.org/noticias/nueva-guia"
DOC = "https://www.ejemplo.org/publicaciones/guia.pdf"
FICHA_DOC = "https://repositorio.ejemplo.org/ark/123"
ARXIV = "https://arxiv.org/abs/2611.20061"
ARXIV_PDF = "https://arxiv.org/pdf/2611.20061v1"
CC_BY = "http://creativecommons.org/licenses/by/4.0/"


def pagina(*enlaces, texto="Presentamos la guía de IA en el aula.") -> bytes:
    a = "".join(f'<a href="{u}">{t}</a> ' for t, u in enlaces)
    return (f"<html><head><title>Nueva guía | Ejemplo</title><script>var x='no es texto';</script></head>"
            f"<body><nav><a href='/'>Inicio</a></nav><p>{texto}</p>{a}</body></html>").encode()


def web(respuestas: dict):
    """Lo que devuelve catalogo.descargar para cada dirección: (estado, final, tipo, datos)."""
    def descargar(url, limite):
        r = respuestas[url]
        return r if len(r) == 4 else (r[0], url, r[1], r[2])
    return mock.patch.object(dw.catalogo, "descargar", side_effect=descargar)


def eleccion(*numeros, titulo="Guía de IA en el aula"):
    return mock.patch.object(dw, "elegir", side_effect=[({"enlace": n, "titulo": titulo}, 0.001) for n in numeros])


def pagina_arxiv(licencia=CC_BY, version=ARXIV + "v1"):
    return (f'<html><td class="tablecell arxividv"><a href="{version}">versión</a></td>'
            f'<a class="has_license" title="Rights to this article" href="{licencia}">view license</a></html>').encode()


class Pagina(unittest.TestCase):
    def test_enlaces_absolutos_sin_anclas_ni_repetidos(self):
        titulo, texto, enlaces = dw.leer_pagina(
            pagina(("Descargar", "guia.pdf"), ("Otra vez", "guia.pdf#p2"), ("Ancla", "#arriba"),
                   ("Correo", "mailto:a@b.c")), "https://www.ejemplo.org/publicaciones/")
        self.assertEqual(titulo, "Nueva guía | Ejemplo")
        self.assertNotIn("no es texto", texto)
        self.assertIn(("Descargar", "https://www.ejemplo.org/publicaciones/guia.pdf"), enlaces)
        self.assertEqual([u for _, u in enlaces].count("https://www.ejemplo.org/publicaciones/guia.pdf"), 1)
        self.assertFalse(any(u.startswith("mailto:") or "#" in u for _, u in enlaces))

    def test_nombres(self):
        self.assertTrue(dw.parece_pdf("https://x.org/a/Guia.PDF?v=2"))
        self.assertFalse(dw.parece_pdf("https://x.org/app/"))
        self.assertEqual(dw.nombre_de("https://x.org/a/Gui%CC%81a.pdf"), "Guía.pdf")  # sin acentos descompuestos
        self.assertEqual(dw.nombre_de("https://x.org/a/ver?id=3"), "")
        self.assertEqual(dw.nombre_por_titulo("IA: guía / 2026"), "IA guía  2026.pdf")


class Buscar(unittest.TestCase):
    def test_pdf_directo(self):
        with web({DOC: (200, "application/pdf", PDF)}):
            r = dw.buscar(None, DOC)
        self.assertEqual((r["estado"], r["nombre"], r["enlace"]), ("pdf", "guia.pdf", DOC))

    def test_redirigido_a_un_pdf_conserva_la_pagina_que_se_mando(self):
        with web({ANUNCIO: (200, "https://cdn.ejemplo.net/f/guia.pdf", "application/pdf", PDF)}):
            r = dw.buscar(None, ANUNCIO)
        self.assertEqual((r["estado"], r["enlace"], r["nombre"]), ("pdf", ANUNCIO, "guia.pdf"))

    def test_anuncio_que_enlaza_al_pdf(self):
        with web({ANUNCIO: (200, "text/html", pagina(("PDF", DOC))), DOC: (200, "application/pdf", PDF)}), eleccion(2):
            r = dw.buscar(None, ANUNCIO)  # [1] es «Inicio»
        self.assertEqual((r["estado"], r["enlace"]), ("pdf", DOC))
        self.assertAlmostEqual(r["usd"], 0.001)

    def test_anuncio_ficha_del_repositorio_y_pdf(self):
        ficha = pagina(("Descargar PDF", "/files/123.pdf"))
        with web({ANUNCIO: (200, "text/html", pagina(("Ver documento", FICHA_DOC))),
                  FICHA_DOC: (200, "text/html", ficha),
                  "https://repositorio.ejemplo.org/files/123.pdf": (200, "application/pdf", PDF)}), eleccion(2, 2):
            r = dw.buscar(None, ANUNCIO)
        self.assertEqual((r["estado"], r["enlace"]), ("pdf", FICHA_DOC))  # la página propia del documento

    def test_repositorio_que_no_deja_descargar(self):
        with web({ANUNCIO: (200, "text/html", pagina(("Ver documento", FICHA_DOC))),
                  FICHA_DOC: (403, "", b"")}), eleccion(2):
            r = dw.buscar(None, ANUNCIO)
        self.assertEqual((r["estado"], r["enlace"], r["titulo"]), ("no_descargable", FICHA_DOC, "Guía de IA en el aula"))

    def test_repositorio_que_solo_funciona_con_javascript(self):
        vacia = b"<html><body><div id='app'></div><script src='/app.js'></script></body></html>"
        with web({ANUNCIO: (200, "text/html", pagina(("Ver documento", FICHA_DOC))),
                  FICHA_DOC: (200, "text/html", vacia)}), eleccion(2):
            r = dw.buscar(None, ANUNCIO)
        self.assertEqual(r["estado"], "no_descargable")

    def test_la_direccion_mandada_no_deja_entrar(self):
        with web({FICHA_DOC: (403, "", b"")}):
            self.assertEqual(dw.buscar(None, FICHA_DOC)["estado"], "bloqueado")

    def test_pagina_sin_documento_no_se_imprime(self):
        with web({ANUNCIO: (200, "text/html", pagina(("Contacto", "/contacto")))}), eleccion(0):
            self.assertEqual(dw.buscar(None, ANUNCIO)["estado"], "sin_documento")

    def test_un_numero_inventado_no_vale(self):
        with web({ANUNCIO: (200, "text/html", pagina(("PDF", DOC)))}), eleccion(99):
            self.assertEqual(dw.buscar(None, ANUNCIO)["estado"], "sin_documento")

    def test_demasiado_grande(self):
        with web({DOC: (200, "application/pdf", PDF)}), mock.patch.object(dw, "MAX_PDF", 100):
            self.assertEqual(dw.buscar(None, DOC)["estado"], "grande")

    def test_direccion_que_no_abre(self):
        with mock.patch.object(dw.catalogo, "descargar", side_effect=dw.catalogo.NoPublica("interna")):
            self.assertEqual(dw.buscar(None, "http://192.168.1.1/")["estado"], "no_abre")

    def test_arxiv_fija_la_version_y_devuelve_la_licencia_de_la_ficha(self):
        respuestas = {ARXIV: (200, "text/html", pagina_arxiv()),
                      ARXIV_PDF: (200, "application/pdf", PDF)}
        with web(respuestas):
            r = dw.buscar(None, ARXIV)
        self.assertEqual((r["estado"], r["enlace"], r["datos"], r["usd"]), ("pdf", ARXIV + "v1", PDF, 0))
        self.assertIn("CC BY 4.0", r["licencia"])
        self.assertIn("https://creativecommons.org/licenses/by/4.0/", r["licencia"])

    def test_arxiv_pdf_directo_consulta_la_ficha_de_su_version(self):
        with web({ARXIV + "v1": (200, "text/html", pagina_arxiv()), ARXIV_PDF: (200, "application/pdf", PDF)}):
            self.assertIn("CC BY 4.0", dw.buscar(None, ARXIV_PDF)["licencia"])

    def test_arxiv_no_hereda_la_licencia_de_otra_version(self):
        respuestas = {ARXIV + "v1": (200, "text/html", pagina_arxiv(version=ARXIV + "v2")),
                      ARXIV_PDF: (200, "application/pdf", PDF)}
        with web(respuestas):
            self.assertNotIn("licencia", dw.buscar(None, ARXIV_PDF))

    def test_arxiv_no_confunde_su_permiso_de_deposito_con_una_licencia_abierta(self):
        respuestas = {ARXIV + "v1": (200, "text/html", pagina_arxiv("https://arxiv.org/licenses/nonexclusive-distrib/1.0/")),
                      ARXIV_PDF: (200, "application/pdf", PDF)}
        with web(respuestas):
            r = dw.buscar(None, ARXIV_PDF)
        self.assertEqual(r["estado"], "pdf")
        self.assertNotIn("licencia", r)

    def test_arxiv_no_aplica_licencias_de_otro_dominio_ni_a_pdfs_redirigidos(self):
        falso = "https://arxiv.org.ejemplo.org/pdf/2611.20061v1"
        with web({falso: (200, "application/pdf", PDF)}):
            self.assertNotIn("licencia", dw.buscar(None, falso))
        with web({ARXIV: (200, "text/html", pagina_arxiv()), ARXIV_PDF: (200, falso, "application/pdf", PDF)}):
            self.assertIsNone(dw.documento_arxiv(ARXIV))


class LicenciaInstitucional(unittest.TestCase):
    CONSEJO = "https://data.consilium.europa.eu/doc/document/ST-14902-2026-INIT/es/pdf"

    def test_pdf_del_consejo_lleva_su_decision_de_reutilizacion(self):
        with web({self.CONSEJO: (200, "application/pdf", PDF)}):
            r = dw.buscar(None, self.CONSEJO)
        self.assertIn("2017/1842", r["licencia_institucional"])

    def test_cada_institucion_y_sus_subdominios(self):
        for url, trozo in (("https://commission.europa.eu/document/download/x.pdf", "CC BY 4.0"),
                           ("https://joint-research-centre.ec.europa.eu/a.pdf", "CC BY 4.0"),
                           ("https://www.europarl.europa.eu/RegData/etudes/a.pdf", "Parlamento Europeo"),
                           ("https://www.consilium.europa.eu/media/1/a.pdf", "2017/1842")):
            with self.subTest(url=url):
                self.assertIn(trozo, dw.licencia_institucional(url))

    def test_no_vale_otro_dominio_ni_sin_https(self):
        for url in ("https://consilium.europa.eu.ejemplo.net/a.pdf", "https://falsoconsilium.europa.eu/a.pdf",
                    "http://data.consilium.europa.eu/a.pdf", "https://eur-lex.europa.eu/a.pdf",
                    "https://www.ejemplo.org/consilium.europa.eu/a.pdf"):
            with self.subTest(url=url):
                self.assertEqual(dw.licencia_institucional(url), "")

    def test_cuenta_el_dominio_que_sirve_el_pdf_tras_redirigir(self):
        with web({ANUNCIO: (200, self.CONSEJO, "application/pdf", PDF)}):
            self.assertIn("2017/1842", dw.buscar(None, ANUNCIO)["licencia_institucional"])
        with web({self.CONSEJO: (200, "https://cdn.ejemplo.net/a.pdf", "application/pdf", PDF)}):
            self.assertNotIn("licencia_institucional", dw.buscar(None, self.CONSEJO))


class RedesSociales(unittest.TestCase):
    def test_una_publicacion_de_una_red_no_es_el_documento(self):
        for url in ("https://www.linkedin.com/posts/alguien_guia-ugcPost-1-zrVt/?utm_source=social_share_send",
                    "https://es.linkedin.com/pulse/una-guia", "https://lnkd.in/abc", "https://x.com/a/status/1",
                    "https://m.facebook.com/a/posts/1", "https://bsky.app/profile/a/post/1"):
            with self.subTest(url=url), web({}):
                self.assertEqual(dw.buscar(None, url)["estado"], "red_social")

    def test_no_confunde_otros_dominios(self):
        for url in ("https://linkedin.com.ejemplo.org/a.pdf", "https://www.ejemplo.org/linkedin.com/a.pdf",
                    "https://www.intef.es/x.pdf"):
            with self.subTest(url=url):
                self.assertFalse(dw.es_red_social(url))


class MismoTitulo(unittest.TestCase):
    def test_titulos_distintos_no_son_repetidos(self):
        self.assertFalse(fichas.mismo_titulo(
            "Manual urgente sobre IA en el aula: miradas y análisis de la esfera digital desde Abya Yala",
            "Inteligencia Artificial en la Educación. Una guía práctica para profesores en la era digital",
            "INTELIGENCIA ARTIFICIAL EN LA EDUCACIÓN: UNA GUÍA PRÁCTICA PARA PROFESORES EN LA ERA DIGITAL 2024"))

    def test_mismo_titulo_aunque_cambien_mayusculas_y_tildes(self):
        self.assertTrue(fichas.mismo_titulo(
            "Inteligencia artificial en la educación: una guía práctica para profesores",
            "INTELIGENCIA ARTIFICIAL EN LA EDUCACION: UNA GUIA PRACTICA PARA PROFESORES",
            "Libro.pdf\nINTELIGENCIA ARTIFICIAL EN LA EDUCACION: UNA GUIA PRACTICA PARA PROFESORES EN LA ERA DIGITAL"))

    def test_el_titulo_del_candidato_tiene_que_estar_en_su_texto(self):
        self.assertFalse(fichas.mismo_titulo("Manual urgente sobre IA en el aula", "Manual urgente sobre IA en el aula",
                                             "Una guía práctica para profesores"))

    def test_revisar_anula_el_repetido_que_no_respalda_el_titulo(self):
        f = fichas.Fichero.__new__(fichas.Fichero)
        cand = [{"enlace": "https://t.me/ChatGPTedu/21753/21758", "archivo": "Libro completo de IA de AV.pdf",
                 "texto": "INTELIGENCIA ARTIFICIAL EN LA EDUCACIÓN: UNA GUÍA PRÁCTICA PARA PROFESORES"}]
        respuesta = {"trata_ia_educacion": True, "tema": "IA", "repetido": 1, "titulo": "Manual urgente sobre IA en el aula",
                     "titulo_repetido": "Inteligencia artificial en la educación: una guía práctica para profesores"}
        r = SimpleNamespace(content=[SimpleNamespace(type="text", text=json.dumps(respuesta))],
                            usage=SimpleNamespace(input_tokens=1, output_tokens=1, cache_read_input_tokens=0,
                                                  cache_creation_input_tokens=0))
        f.c = SimpleNamespace(b=SimpleNamespace(al_dia=lambda: None, biblioteca=lambda *a, **k: cand),
                              cliente=SimpleNamespace(messages=SimpleNamespace(create=lambda **k: r)))
        datos, _, _ = f.revisar("Manual urgente sobre IA en el aula " * 20, "manual.pdf")
        self.assertEqual(datos["repetido"], 0)
        respuesta.update(titulo="Inteligencia artificial en la educación. Una guía práctica para profesores")
        r.content[0].text = json.dumps(respuesta)
        self.assertEqual(f.revisar("x " * 300, "guia.pdf")[0]["repetido"], 1)


class TipoDeEnlace(unittest.TestCase):
    def test_pdf_sin_extension(self):
        with web({FICHA_DOC: (200, "application/octet-stream", PDF)}):
            self.assertEqual(dw.tipo_de_enlace(FICHA_DOC), "documento")

    def test_ficha_academica_y_su_pdf_en_metadatos(self):
        datos = b'<meta name="citation_pdf_url" content="/publicaciones/guia.pdf">'
        with web({ANUNCIO: (200, "text/html", datos)}):
            self.assertEqual(dw.tipo_de_enlace(ANUNCIO), "documento")
        self.assertEqual(dw.leer_pagina(datos, ANUNCIO)[2], [("PDF del documento", DOC)])

    def test_aplicacion_declarada_en_la_pagina(self):
        datos = b'<meta name="application-name" content="Simulador"><link rel="manifest" href="manifest.webmanifest">'
        with web({ANUNCIO: (200, "text/html", datos)}):
            self.assertEqual(dw.tipo_de_enlace(ANUNCIO), "recurso")

    def test_un_pdf_en_una_pagina_no_basta_para_asignarla(self):
        with web({ANUNCIO: (200, "text/html", pagina(("Descargar PDF", DOC)))}):
            self.assertEqual(dw.tipo_de_enlace(ANUNCIO), "")

    def test_pagina_con_indicios_de_documento_y_de_aplicacion(self):
        datos = b'<meta property="og:type" content="softwareapplication"><meta name="citation_pdf_url" content="/guia">'
        with web({ANUNCIO: (200, "text/html", datos)}):
            self.assertEqual(dw.tipo_de_enlace(ANUNCIO), "")

    def test_pagina_no_disponible(self):
        with web({ANUNCIO: (403, "", b"")}):
            self.assertEqual(dw.tipo_de_enlace(ANUNCIO), "")


AUTOR = 7002
DE = {"id": AUTOR, "first_name": "Ana", "username": "ana"}
FICHA = ("**Guía de IA en el aula**\n\nEjemplo. (2026). Guía de IA en el aula.\n\n**Resumen**\nTexto.\n\n"
         "**Licencia**\nCC BY 4.0")


class Telegram:
    def __init__(self, b):
        self.b = b

    def __call__(self, metodo, **k):
        self.b.llamadas.append((metodo, k))
        return {"message_id": 99}

    def subir(self, metodo, campo, nombre, datos, **k):
        self.b.llamadas.append(("subir", {"nombre": nombre, **k}))
        return {"message_id": 98, "document": {"file_id": "subido-1"}}


def nuevo_bot(compartir=True):
    b = bot.Bot.__new__(bot.Bot)
    for nombre in ("pendientes", "espera", "lenguas"):
        setattr(b, nombre, {})
    b.lenguas[AUTOR] = "es"
    b.llamadas = []
    b.tg = Telegram(b)
    b.enviar = lambda chat, texto, formato=None: b.llamadas.append(("enviar", {"chat_id": chat, "text": texto}))
    b.escribiendo = lambda chat: threading.Event()
    b.apuntar = lambda *a, **k: b.llamadas.append(("apuntar", k))
    b.puede_documento = lambda chat, uid: True
    b.consultor = mock.Mock()
    b.fichero = mock.Mock()
    b.fichero.revisar.return_value = ({"trata_ia_educacion": True, "tema": "IA", "repetido": 0}, [], 0.0)
    b.fichero.ficha.return_value = (FICHA, 0.0)
    b.fichero.compartible.return_value = (compartir, 0.0)
    return b


class Bot(unittest.TestCase):
    def llamar(self, b, r):
        with mock.patch.object(dw, "buscar", return_value={"usd": 0.0, **r}), \
             mock.patch.object(fichas, "leer_pdf", return_value=("texto " * 100, "Pages: 3")):
            b.documento_web(AUTOR, AUTOR, DE, ANUNCIO)
        return [k.get("text", "") for m, k in b.llamadas if m in ("enviar", "sendMessage")]

    def test_descargado_se_le_manda_y_se_publica_con_ese_archivo(self):
        b = nuevo_bot()
        self.llamar(b, {"estado": "pdf", "datos": PDF, "nombre": "", "enlace": DOC})
        subida = next(k for m, k in b.llamadas if m == "subir")
        self.assertEqual(subida["nombre"], "Guía de IA en el aula.pdf")  # sin nombre en la dirección, el del título
        p = b.pendientes[AUTOR]
        self.assertEqual(p["file_id"], "subido-1")
        self.assertIn(DOC, p["ficha"])  # la ficha lleva el enlace del documento descargado, sin buscarlo
        b.fichero.buscar_enlace.assert_not_called()
        self.assertIn(("apuntar", {"documento": AUTOR}), b.llamadas)  # cuenta para el cupo del día

    def test_sin_licencia_abierta_no_se_sube(self):
        b = nuevo_bot(compartir=False)
        self.llamar(b, {"estado": "pdf", "datos": PDF, "nombre": "guia.pdf", "enlace": DOC})
        self.assertFalse(any(m == "subir" for m, _ in b.llamadas))
        self.assertIsNone(b.pendientes[AUTOR]["file_id"])

    def test_licencia_verificada_corrige_la_ficha_y_adjunta_el_original(self):
        b = nuevo_bot(compartir=False)
        ficha = FICHA.replace("CC BY 4.0", "No se podrá compartir el documento.")
        b.fichero.ficha.return_value = (ficha, 0)
        licencia = f"CC BY 4.0 según arXiv. {ARXIV}"
        self.llamar(b, {"estado": "pdf", "datos": PDF, "nombre": "", "enlace": ARXIV, "licencia": licencia})
        p = b.pendientes[AUTOR]
        self.assertEqual(bot.fichas.licencia_de(p["ficha"]), licencia)
        self.assertTrue(p["compartir"])
        self.assertEqual(p["file_id"], "subido-1")
        b.fichero.compartible.assert_not_called()

    def test_licencia_institucional_adjunta_el_pdf_sin_licencia_propia(self):
        b = nuevo_bot(compartir=False)
        ficha = FICHA.replace("CC BY 4.0", "No se podrá compartir con el grupo ChatGPT-IA-edu: el documento no "
                              "indica ninguna licencia.")
        b.fichero.ficha.return_value = (ficha, 0)
        licencia = dw.licencia_institucional("https://data.consilium.europa.eu/doc/a.pdf")
        self.llamar(b, {"estado": "pdf", "datos": PDF, "nombre": "a.pdf", "enlace": DOC,
                        "licencia_institucional": licencia})
        p = b.pendientes[AUTOR]
        self.assertEqual(bot.fichas.licencia_de(p["ficha"]), licencia)
        self.assertTrue(p["compartir"])
        self.assertEqual(p["file_id"], "subido-1")
        b.fichero.compartible.assert_not_called()

    def test_lo_que_el_pdf_reserva_manda_sobre_la_licencia_institucional(self):
        b = nuevo_bot(compartir=False)
        ficha = FICHA.replace("CC BY 4.0", "No se podrá compartir con el grupo ChatGPT-IA-edu: el documento indica "
                              "© 2026 Editorial Ejemplo, todos los derechos reservados.")
        b.fichero.ficha.return_value = (ficha, 0)
        self.llamar(b, {"estado": "pdf", "datos": PDF, "nombre": "a.pdf", "enlace": DOC,
                        "licencia_institucional": dw.licencia_institucional("https://ec.europa.eu/a.pdf")})
        self.assertFalse(any(m == "subir" for m, _ in b.llamadas))
        self.assertIn("derechos reservados", bot.fichas.licencia_de(b.pendientes[AUTOR]["ficha"]))

    def test_no_descargable_da_el_enlace_directo(self):
        b = nuevo_bot()
        textos = self.llamar(b, {"estado": "no_descargable", "enlace": FICHA_DOC, "titulo": "Guía"})
        self.assertIn(FICHA_DOC, textos[-1])
        self.assertIn("«Guía»", textos[-1])
        self.assertNotIn(AUTOR, b.pendientes)

    def test_cada_estado_tiene_su_mensaje(self):
        for estado, trozo in (("bloqueado", "no deja"), ("sin_documento", "ningún documento"),
                              ("red_social", "red social"),
                              ("no_abre", "No he podido abrir"), ("error", "Algo ha fallado")):
            with self.subTest(estado=estado):
                self.assertIn(trozo, self.llamar(nuevo_bot(), {"estado": estado})[-1])
        self.assertIn("60 MB", self.llamar(nuevo_bot(), {"estado": "grande", "mb": 60.2})[-1])


class DuplicadosBiblioteca(unittest.TestCase):
    def setUp(self):
        carpeta = tempfile.TemporaryDirectory()
        self.addCleanup(carpeta.cleanup)
        self.raiz = Path(carpeta.name)
        self.datos = self.raiz / "chatgpt"
        self.datos.mkdir()
        self.grupo = SimpleNamespace(datos=self.datos, biblioteca=21753, id=-1001, enlace="https://t.me/ChatGPTedu")
        self.enterContext(mock.patch.object(bot, "BIBLIOTECA", self.grupo))
        self.enterContext(mock.patch.object(bot, "BIBLIOTECA_PRUEBA", None))
        self.enterContext(mock.patch.object(bot, "ESTADO", self.raiz / "estado.json"))

    def borrador(self):
        return {"ficha": FICHA, "file_id": "f", "autor": "A", "compartir": True, "clave": "abc",
                "momento": bot.time.time(), "claves": sorted(duplicados.claves([ARXIV_PDF]))}

    def test_una_version_y_sus_enlaces_no_confunden_versiones_nuevas(self):
        doi = "https://doi.org/10.48550/arXiv.2611.20061v1"
        self.assertEqual(duplicados.claves([ARXIV, ARXIV_PDF, doi]), {"arxiv:2611.20061v1"})
        self.assertEqual(duplicados.claves([ARXIV + "v2"]), {"arxiv:2611.20061v2"})
        self.assertEqual(duplicados.claves(["http://ejemplo.org/Doc/?utm_source=telegram&id=2#otro"]),
                         {"https://ejemplo.org/Doc?id=2"})

    def test_encuentra_en_el_historial_la_ficha_y_no_un_comentario(self):
        encontrado = f"{self.grupo.enlace}/{self.grupo.biblioteca}/22"
        ficha = f"Título\n\nReferencia. {ARXIV}\n\nResumen\nEjemplo.\n\nLicencia\nCC BY 4.0. {ARXIV}v1"
        filas = [
            {"id": 21, "tema": self.grupo.biblioteca, "responde_a": None, "texto": "Un documento", "enlace": "original"},
            {"id": 22, "tema": self.grupo.biblioteca, "responde_a": 21, "texto": ficha, "enlace": encontrado},
            {"id": 23, "tema": self.grupo.biblioteca, "responde_a": 21, "texto": f"Otro trabajo: {ARXIV}v2", "enlace": "ajeno"},
        ]
        (self.datos / "mensajes.jsonl").write_text("\n".join(map(json.dumps, filas)))
        b = nuevo_bot()
        self.assertEqual(b.repetido_biblioteca(duplicados.claves([ARXIV_PDF])), encontrado)
        self.assertFalse(b.repetido_biblioteca(duplicados.claves([ARXIV + "v2"])))

    def test_rechaza_el_mismo_documento_antes_de_hacer_ficha_y_aunque_el_indice_no_exista(self):
        b = nuevo_bot()
        enlace, _, _ = b.publicar(self.borrador())
        otro = nuevo_bot()
        r = {"estado": "pdf", "datos": PDF, "nombre": "", "enlace": ARXIV_PDF, "usd": 0.0}
        with mock.patch.object(dw, "buscar", return_value=r), mock.patch.object(fichas, "leer_pdf") as leer:
            otro.documento_web(AUTOR, AUTOR, DE, ARXIV)
        leer.assert_not_called()
        otro.fichero.revisar.assert_not_called()
        self.assertIn(enlace, [k["text"] for m, k in otro.llamadas if m == "enviar"][-1])

    def test_dos_vistas_previas_comprueban_de_nuevo_al_publicar(self):
        primero, segundo = nuevo_bot(), nuevo_bot()
        primero.pendientes[AUTOR] = self.borrador()
        segundo.pendientes[AUTOR] = self.borrador()
        for b in (primero, segundo):
            b.token = "token-de-prueba"
            b.fijar_lengua = lambda *a: None
            b.grupos_de = lambda *a, **k: {bot.grupos.con_biblioteca().clave}
            b.antispam = mock.Mock()
            b.antispam.deshacer.return_value = False
            b.avisar_juanjo = mock.Mock()
        self.grupo.clave = bot.grupos.con_biblioteca().clave
        cq = {"id": "boton", "from": DE, "data": "publicar:abc"}
        primero.boton(cq)
        segundo.boton(cq)
        self.assertIn("sendDocument", [m for m, _ in primero.llamadas])
        self.assertNotIn("sendDocument", [m for m, _ in segundo.llamadas])
        self.assertIn("ya está en la Biblioteca", segundo.llamadas[-1][1]["text"])

    def test_si_falla_la_ficha_registra_el_documento_y_el_reintento_lo_reutiliza(self):
        b = nuevo_bot()
        p = self.borrador()
        b.tg = mock.Mock(side_effect=[{"message_id": 12}, None, {"message_id": 13}])
        with self.assertRaises(RuntimeError):
            b.publicar(p)
        self.assertTrue(nuevo_bot().repetido_biblioteca(set(p["claves"])))
        self.assertFalse(b.repetido_biblioteca(set(p["claves"]), omitir=12))
        b.publicar(p)
        self.assertEqual([ll.args[0] for ll in b.tg.call_args_list], ["sendDocument", "sendMessage", "sendMessage"])

    def test_reconoce_la_huella_aunque_cambie_el_enlace(self):
        b = nuevo_bot()
        b.registrar_publicacion_biblioteca({"claves": ["sha256:abc", "https://ejemplo.org/informe"]}, 23)
        self.assertTrue(b.repetido_biblioteca(duplicados.claves(["https://ejemplo.net/documento"], "abc")))


class TrasBiblioteca(unittest.TestCase):
    """/biblioteca y luego el enlace de una página: va a la biblioteca, no al catálogo (12-11-2026)."""
    def atender(self, b, texto):
        b.atender({"chat": {"id": AUTOR, "type": "private"}, "from": DE, "text": texto, "message_id": 1})

    def nuevo(self):
        b = nuevo_bot()
        b.fijar_lengua = b.lengua_de_la_frase = lambda *a: None
        b.voz_a_texto = lambda *a: None
        b.agotadas = lambda uid: False
        b.grupos_de = lambda uid: {bot.BIBLIOTECA.clave, bot.CATALOGO.clave}  # de los dos grupos
        b.en_hilo = lambda f, *a: b.llamadas.append(("hilo", {"f": f.__name__, "a": a}))
        return b

    def hilos(self, b):
        return [(k["f"], k["a"][-1]) for m, k in b.llamadas if m == "hilo"]

    def test_enlace_de_pagina_va_a_la_biblioteca(self):
        b = self.nuevo()
        with mock.patch.object(bot, "AUTORIZADOS", {AUTOR}):
            self.atender(b, "/biblioteca")
            self.atender(b, ANUNCIO)
        self.assertEqual(self.hilos(b), [("documento_web", ANUNCIO)])
        self.assertNotIn(AUTOR, b.espera)

    def test_enlace_suelto_se_clasifica_antes_de_elegir_destino(self):
        b = self.nuevo()
        with mock.patch.object(bot, "AUTORIZADOS", {AUTOR}):
            self.atender(b, ANUNCIO)
        [(funcion, pendiente)] = self.hilos(b)
        self.assertEqual((funcion, pendiente["url"]), ("clasificar_enlace", ANUNCIO))

    def test_repositorio_explicito_sigue_yendo_al_catalogo(self):
        b = self.nuevo()
        with mock.patch.object(bot, "AUTORIZADOS", {AUTOR}):
            self.atender(b, "/repositorio")
            self.atender(b, ANUNCIO)
        self.assertEqual(self.hilos(b), [("recurso", ANUNCIO)])

    def test_arxiv_va_a_la_biblioteca_sin_comando(self):
        b = self.nuevo()
        with mock.patch.object(bot, "AUTORIZADOS", {AUTOR}):
            self.atender(b, ARXIV)
        self.assertEqual(self.hilos(b), [("documento_web", ARXIV)])

    def test_otro_comando_deja_la_espera(self):
        b = self.nuevo()
        with mock.patch.object(bot, "AUTORIZADOS", {AUTOR}):
            self.atender(b, "/biblioteca")
            self.atender(b, "/repositorio")
            self.atender(b, ANUNCIO)
        self.assertEqual(self.hilos(b), [("recurso", ANUNCIO)])

    def pendiente(self, b):
        with mock.patch.object(bot, "AUTORIZADOS", {AUTOR}):
            self.atender(b, ANUNCIO)
        return b.espera[AUTOR]

    def test_enlace_claro_abre_su_propio_destino(self):
        for tipo in ("documento", "recurso"):
            with self.subTest(tipo=tipo):
                b = self.nuevo()
                p = self.pendiente(b)
                b.documento_web, b.recurso = mock.Mock(), mock.Mock()
                with mock.patch.object(dw, "tipo_de_enlace", return_value=tipo):
                    b.clasificar_enlace(AUTOR, AUTOR, p)
                elegido, otro = (b.documento_web, b.recurso) if tipo == "documento" else (b.recurso, b.documento_web)
                opciones = {"limpiar_espera": False} if tipo == "recurso" else {}
                elegido.assert_called_once_with(AUTOR, AUTOR, DE, ANUNCIO, **opciones)
                otro.assert_not_called()
                self.assertNotIn(AUTOR, b.espera)

    def test_pide_destino_y_la_eleccion_solo_cuenta_una_vez(self):
        b = self.nuevo()
        b.antispam = mock.Mock()
        b.antispam.deshacer.return_value = False
        p = self.pendiente(b)
        with mock.patch.object(dw, "tipo_de_enlace", return_value=""):
            b.clasificar_enlace(AUTOR, AUTOR, p)
        envio = [k for m, k in b.llamadas if m == "sendMessage"][-1]
        botones = [fila[0] for fila in envio["reply_markup"]["inline_keyboard"]]
        self.assertEqual([b["text"] for b in botones], ["Biblioteca digital", "Repositorio de VCE", "Consultarlo", "Cancelar"])
        self.assertEqual(envio["reply_parameters"], {"message_id": 1})
        clic = {"id": "abc", "data": botones[0]["callback_data"], "from": DE}
        b.boton(clic)
        b.boton(clic)
        self.assertEqual(self.hilos(b)[-1], ("abrir_destino_enlace", "documento"))
        self.assertEqual(len(self.hilos(b)), 2)

    def test_ofrece_solo_destinos_permitidos_y_sustituye_la_eleccion_anterior(self):
        b = self.nuevo()
        b.grupos_de = lambda uid: {bot.CATALOGO.clave}
        anterior = self.pendiente(b)
        nuevo = self.pendiente(b)
        with mock.patch.object(dw, "tipo_de_enlace", return_value="recurso"), mock.patch.object(b, "recurso") as recurso:
            b.clasificar_enlace(AUTOR, AUTOR, anterior)
            recurso.assert_not_called()
        b.boton_destino_enlace(AUTOR, f"de:recurso:{anterior['clave']}")
        b.boton_destino_enlace(AUTOR, f"de:documento:{nuevo['clave']}")
        with mock.patch.object(dw, "tipo_de_enlace", return_value=""):
            b.clasificar_enlace(AUTOR, AUTOR, nuevo)
        envio = [k for m, k in b.llamadas if m == "sendMessage"][-1]
        opciones = envio["reply_markup"]["inline_keyboard"]
        self.assertEqual([fila[0]["text"] for fila in opciones], ["Repositorio de VCE", "Consultarlo", "Cancelar"])
        self.assertEqual(len(self.hilos(b)), 2)
        self.assertIs(b.espera[AUTOR], nuevo)

    def test_consulta_usa_el_mensaje_original_sin_clasificarlo_otra_vez(self):
        b = self.nuevo()
        p = self.pendiente(b)
        b.atender = mock.Mock()
        b.abrir_destino_enlace(AUTOR, AUTOR, p, "consulta")
        b.atender.assert_called_once_with(p["msg"], decidir_destino=False)

    def test_enlace_arxiv_no_acaba_en_el_catalogo_si_se_esperaban_detalles_de_una_app(self):
        b = self.nuevo()
        b.espera[AUTOR] = {"que": "detalle", "url": ANUNCIO, "momento": bot.time.time()}
        with mock.patch.object(bot, "AUTORIZADOS", {AUTOR}):
            self.atender(b, ARXIV)
        self.assertEqual(self.hilos(b), [("documento_web", ARXIV)])


if __name__ == "__main__":
    unittest.main()
