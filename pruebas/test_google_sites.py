# SPDX-License-Identifier: AGPL-3.0-or-later
"""Lectura de las páginas de Google Sites (ADR 0004, punto 1), sin red."""
import html
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import catalogo  # noqa: E402

CODIGO = "<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->\n<html><body><h1>Pentagrama</h1>" \
         "<footer>Licencia CC BY-SA 4.0</footer></body></html>"
RELLENO = "<script>" + "var x=1;" * 15_000 + "</script>"  # el código de carga de Google, más largo que MAX_CODIGO


def pagina(cuerpo: str) -> str:
    return (f"<html><head><title>Inicio</title>{RELLENO}</head><body><p>Juego para leer notas</p>{cuerpo}"
            '<img src="https://lh3.googleusercontent.com/foto.png"></body></html>')


class GoogleSites(unittest.TestCase):
    def test_codigo_insertado_aunque_vaya_tras_el_codigo_de_carga(self):
        t = pagina(f'<div data-url="https://1-atari-embeds.googleusercontent.com/embeds/x/inner-frame-minified.html" '
                   f'data-code="{html.escape(CODIGO)}"></div>')
        self.assertGreater(t.find("data-code"), catalogo.MAX_CODIGO)
        leido = catalogo.de_google_sites("https://sites.google.com/x/y/inicio", t)
        self.assertIn(CODIGO, leido)
        self.assertIn("Juego para leer notas", leido)
        self.assertNotIn("var x=1", leido)

    def test_dominio_propio(self):
        self.assertTrue(catalogo.es_google_sites("https://www.colegio.es/app",
                                                 '<div data-url="https://1-atari-embeds.googleusercontent.com/e">'))
        self.assertFalse(catalogo.es_google_sites("https://ejemplo.org/", "<html></html>"))

    def test_web_insertada_se_lee_una_vez(self):
        t = pagina('<iframe src="https://www.google.com/url?q=https%3A%2F%2Fapp.ejemplo.org%2F&amp;sa=D"></iframe>'
                   '<iframe src="https://www.youtube.com/embed/abc"></iframe>')
        with mock.patch.object(catalogo, "leer_url", return_value=(CODIGO, None)) as leer:
            leido = catalogo.de_google_sites("https://sites.google.com/x/y/inicio", t)
        leer.assert_called_once_with("https://app.ejemplo.org/", 1)
        self.assertIn(CODIGO, leido)
        with mock.patch.object(catalogo, "leer_url") as leer:  # dentro de otra web insertada, ya no se sigue
            leido = catalogo.de_google_sites("https://sites.google.com/x/y/inicio", t, 1)
        leer.assert_not_called()
        self.assertIn("sin leer): https://app.ejemplo.org/", leido)

    def test_codigo_muy_largo_conserva_principio_y_final(self):
        largo = "<!-- SPDX-License-Identifier: MIT -->" + "a" * 100_000 + "<footer>Licencia MIT</footer>"
        leido = catalogo.de_google_sites("https://sites.google.com/x", pagina(f'<div data-code="{html.escape(largo)}">'))
        self.assertIn("SPDX-License-Identifier: MIT", leido)
        self.assertIn("<footer>Licencia MIT</footer>", leido)
        self.assertLessEqual(len(leido), catalogo.MAX_CODIGO)

    def test_sin_nada_insertado(self):
        leido = catalogo.de_google_sites("https://sites.google.com/x", pagina(""))
        self.assertIn("no tiene ningún bloque", leido)


if __name__ == "__main__":
    unittest.main()
