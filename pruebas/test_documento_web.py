# SPDX-License-Identifier: AGPL-3.0-or-later
"""El documento de un enlace para la Biblioteca digital (ADR 0035), sin red ni API.

    .venv/bin/python -m unittest pruebas/test_documento_web.py
"""
import sys
import threading
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import bot  # noqa: E402
import documento_web as dw  # noqa: E402
import fichas  # noqa: E402

PDF = b"%PDF-1.7\n" + b"x" * 1000
ANUNCIO = "https://www.ejemplo.org/noticias/nueva-guia"
DOC = "https://www.ejemplo.org/publicaciones/guia.pdf"
FICHA_DOC = "https://repositorio.ejemplo.org/ark/123"


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

    def test_no_descargable_da_el_enlace_directo(self):
        b = nuevo_bot()
        textos = self.llamar(b, {"estado": "no_descargable", "enlace": FICHA_DOC, "titulo": "Guía"})
        self.assertIn(FICHA_DOC, textos[-1])
        self.assertIn("«Guía»", textos[-1])
        self.assertNotIn(AUTOR, b.pendientes)

    def test_cada_estado_tiene_su_mensaje(self):
        for estado, trozo in (("bloqueado", "no deja"), ("sin_documento", "ningún documento"),
                              ("no_abre", "No he podido abrir"), ("error", "Algo ha fallado")):
            with self.subTest(estado=estado):
                self.assertIn(trozo, self.llamar(nuevo_bot(), {"estado": estado})[-1])
        self.assertIn("60 MB", self.llamar(nuevo_bot(), {"estado": "grande", "mb": 60.2})[-1])


if __name__ == "__main__":
    unittest.main()
