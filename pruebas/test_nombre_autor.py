# SPDX-License-Identifier: AGPL-3.0-or-later
"""El nombre con el que se firman los recursos del repositorio (ADR 0027).

Sin red, sin Telegram y sin gastar API.

    .venv/bin/python -m unittest pruebas/test_nombre_autor.py
"""
import sys
import tempfile
import time
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "scripts"))
sys.path.insert(0, str(AQUI))
import bot  # noqa: E402
import catalogo  # noqa: E402
import textos  # noqa: E402
from test_revision import bot_sin_arrancar  # noqa: E402

UID = 501
A, U = catalogo.COLUMNAS["autor"], catalogo.COLUMNAS["url"]


class HojaFalsa:
    def __init__(self, filas):
        self.lista = filas
        self.cambios = []

    def filas(self):
        return self.lista

    def buscar(self, url):
        return next((f for f in self.lista if catalogo.normalizar(f[U]) == catalogo.normalizar(url)), None)

    def alta(self, f):
        self.lista.append({**catalogo.a_fila(f), catalogo.COL_CORREO: ""})

    def modificar(self, url, f):
        self.buscar(url).update(catalogo.a_fila(f))

    def poner_autor(self, url, autor):
        self.cambios.append((url, autor))
        self.buscar(url)[A] = autor


def fila(url, autor):
    return {**catalogo.a_fila({"titulo": "T", "url": url, "autor": autor}), catalogo.COL_CORREO: ""}


def ficha(url="https://ejemplo.org/nuevo"):
    return {"titulo": "Nuevo", "url": url, "descripcion": "", "tipo": [], "niveles": [], "areas": [], "idiomas": [],
            "palabras_clave": [], "de_pago": False, "licencia_abierta": True, "licencia": "MIT",
            "licencia_contenidos": ""}


class NombreDeAutor(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        catalogo.DUENOS = Path(self.tmp.name) / "catalogo.json"
        d = catalogo.leer_duenos()
        d["recursos"][catalogo.normalizar("https://ejemplo.org/viejo")] = UID   # otro recurso suyo, con el nombre de Telegram
        catalogo.guardar_duenos(d)
        b = self.b = bot_sin_arrancar()
        b.lenguas[UID] = "es"
        b.hoja = HojaFalsa([fila("https://ejemplo.org/viejo", "D"), fila("https://ejemplo.org/ajeno", "Otra")])
        b.sugerir_licencia_visible = lambda *a: False
        b.grupos_de = lambda uid, al_dia=False: {bot.CATALOGO.clave}
        b.apuntar = lambda *a, **k: None
        b.avisar_juanjo = lambda *a, **k: None

    def tearDown(self):
        self.tmp.cleanup()

    def alta(self, nombre):
        self.b.seguir_alta(UID, UID, {"first_name": nombre}, ficha(), "contenido", "")

    def pregunta(self):
        """La última pregunta «¿en todos o solo en este?»: su texto y sus dos botones."""
        m = [k for metodo, k in self.b.llamadas if metodo == "sendMessage" and "rnt:" in str(k.get("reply_markup"))]
        if not m:
            return "", []
        return m[-1]["text"], [x["callback_data"] for x in m[-1]["reply_markup"]["inline_keyboard"][0]]

    def dar_nombre(self):
        self.alta("D")
        self.b.poner_nombre(UID, UID, "Dolores Pérez")
        self.b.publicar_recurso(UID)
        texto, botones = self.pregunta()
        self.assertIn("(1)", texto)
        self.assertIsNone(self.b.hoja.buscar("https://ejemplo.org/nuevo"), "no publica hasta que elige")
        return botones

    def test_nombre_corto_lo_pide_y_lo_cambia_en_todos(self):
        self.alta("D")
        self.assertEqual(self.b.espera[UID]["que"], "nombre")
        self.assertIn("«D»", self.b.enviados[-1])
        self.assertFalse(any(m == "sendMessage" for m, _ in self.b.llamadas), "aún no enseña la ficha")
        self.b.poner_nombre(UID, UID, "jc")
        self.assertEqual(self.b.enviados[-1], textos.texto("es", "nombre_no_valido"))
        self.b.poner_nombre(UID, UID, "  Dolores   Pérez ")
        self.assertEqual(self.b.fichas_rec[UID]["ficha"]["autor"], "Dolores Pérez")
        self.b.publicar_recurso(UID)
        texto, botones = self.pregunta()
        self.assertIn("(1)", texto)
        self.b.boton_recurso(UID, botones[0])   # «En todos»
        self.assertEqual(catalogo.nombre_guardado(UID), "Dolores Pérez")
        self.assertEqual(self.b.hoja.buscar("https://ejemplo.org/viejo")[A], "Dolores Pérez")
        self.assertEqual(self.b.hoja.buscar("https://ejemplo.org/ajeno")[A], "Otra", "lo de otra persona no se toca")
        self.assertTrue(any("ahora todos salen a nombre de «Dolores Pérez»" in t for t in self.b.enviados))

    def test_solo_en_este(self):
        botones = self.dar_nombre()
        self.b.boton_recurso(UID, botones[1])   # «Solo en este»
        self.assertIsNotNone(self.b.hoja.buscar("https://ejemplo.org/nuevo"))
        self.assertEqual(self.b.hoja.buscar("https://ejemplo.org/viejo")[A], "D", "los demás no cambian")
        self.assertEqual(catalogo.nombre_guardado(UID), "Dolores Pérez", "sin nombre guardado, se guarda para no volver a pedirlo")

    def test_solo_en_este_no_cambia_el_nombre_guardado(self):
        d = catalogo.leer_duenos()
        d["nombres"][str(UID)] = "D. Pérez"
        catalogo.guardar_duenos(d)
        self.b.hoja.buscar("https://ejemplo.org/viejo")[A] = "D. Pérez"
        self.alta("D")
        self.b.fichas_rec[UID]["ficha"]["autor"] = "Dolores Pérez y Luis Gil"   # como tras «Cambiar algo»
        self.b.publicar_recurso(UID)
        self.b.boton_recurso(UID, self.pregunta()[1][1])
        self.assertEqual(catalogo.nombre_guardado(UID), "D. Pérez")
        self.assertEqual(self.b.hoja.buscar("https://ejemplo.org/viejo")[A], "D. Pérez")
        self.assertEqual(self.b.hoja.buscar("https://ejemplo.org/nuevo")[A], "Dolores Pérez y Luis Gil")

    def test_boton_de_una_vista_anterior(self):
        self.dar_nombre()
        self.b.boton_recurso(UID, "rnt:otra")
        self.assertIsNone(self.b.hoja.buscar("https://ejemplo.org/nuevo"))

    def test_el_nombre_guardado_no_se_vuelve_a_pedir(self):
        d = catalogo.leer_duenos()
        d["nombres"][str(UID)] = "Dolores Pérez"
        catalogo.guardar_duenos(d)
        self.alta("D")
        self.assertNotIn(UID, self.b.espera)
        self.assertEqual(self.b.fichas_rec[UID]["ficha"]["autor"], "Dolores Pérez")
        self.b.publicar_recurso(UID)
        self.assertEqual(self.b.hoja.cambios, [], "sin cambio de nombre no toca los demás")

    def test_nombre_largo_ni_se_pide_ni_se_guarda(self):
        self.alta("Dolores Pérez")
        self.assertNotIn(UID, self.b.espera)
        self.b.publicar_recurso(UID)
        self.assertEqual(catalogo.nombre_guardado(UID), "")

    def test_cambiar_el_autor_de_uno_publicado_lo_cambia_en_todos(self):
        self.b.hoja.lista.append(fila("https://ejemplo.org/otro", "D"))
        d = catalogo.leer_duenos()
        d["recursos"][catalogo.normalizar("https://ejemplo.org/otro")] = UID
        catalogo.guardar_duenos(d)
        f = catalogo.de_fila(self.b.hoja.buscar("https://ejemplo.org/otro"))
        self.b.fichas_rec[UID] = {"ficha": {**f, "autor": "Dolores Pérez"}, "modo": "modificar",
                                  "momento": time.time(), "autor_original": "D"}
        self.b.fichas_rec[UID]["clave"] = "k"
        self.b.publicar_recurso(UID)
        self.assertEqual(self.pregunta()[1], ["rnt:k", "rns:k"])
        self.b.boton_recurso(UID, "rnt:k")
        self.assertEqual(self.b.hoja.buscar("https://ejemplo.org/viejo")[A], "Dolores Pérez")
        self.assertEqual(catalogo.nombre_guardado(UID), "Dolores Pérez")

    def test_nombre_corto(self):
        for n, corto in (("D", True), ("jc", True), ("J.C.", True), ("", True), ("Ana", False), ("D. Pérez", False)):
            self.assertEqual(catalogo.nombre_corto(n), corto, n)


if __name__ == "__main__":
    unittest.main()
