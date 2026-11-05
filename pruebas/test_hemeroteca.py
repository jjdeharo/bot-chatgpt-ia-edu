# SPDX-License-Identifier: AGPL-3.0-or-later
"""Pruebas de la búsqueda en el Diario de IA Educativa (ADR 0030), sin red ni modelo de significado."""
import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import hemeroteca as h  # noqa: E402


class SinServicio:
    """Como el servicio de significado caído: se busca solo por palabras."""
    def passage_embed(self, textos, batch_size=16):
        raise OSError("sin servicio")

    def query_embed(self, textos):
        raise OSError("sin servicio")


class Palabras:
    """Un significado de juguete: un vector por palabras clave."""
    CLAVES = ("blender", "jigsaw", "célula", "agentes")

    def _v(self, t):
        t = t.lower()
        return np.array([1.0 if c in t else 0.0 for c in self.CLAVES] + [0.01], dtype=np.float32)

    def passage_embed(self, textos, batch_size=16):
        return [self._v(t) for t in textos]

    def query_embed(self, textos):
        return [self._v(t) for t in textos]


def entrada(numero, sale, titular, texto, mensaje="vce:1"):
    grupo, i = mensaje.split(":")
    return {"tipo": "pieza", "numero": numero, "fecha": "", "sale": sale, "seccion": "Multimedia",
            "antetitulo": "", "titular": titular, "entradilla": "", "texto": texto, "grupo": "Vibe Coding Educativo",
            "mensaje": f"https://t.me/vceduca/{i}", "mensaje_id": mensaje, "fuentes": [],
            "url": f"https://diarioiaeducativa.github.io/x/{numero}.html",
            "url_ca": f"https://diarioiaeducativa.github.io/ca/x/{numero}.html"}


class Hemeroteca(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        h.VECTORES = self.tmp / "vectores.npz"
        self.archivo = self.tmp / "hemeroteca.json"
        self.escribir([entrada(3, "2026-11-04", "Una cámara virtual para Blender", "Con el móvil y Blender", "edumedia:12067"),
                       entrada(4, "2026-11-05", "Grupos de la técnica Jigsaw", "Forma grupos al azar", "vce:14500"),
                       entrada(4, "2026-11-05", "Un juego sobre la célula", "Orgánulos y tejidos", "vce:14501")])

    def escribir(self, entradas):
        self.archivo.write_text(json.dumps({"ultimo_numero": max(e["numero"] for e in entradas),
                                            "hemeroteca": "https://diarioiaeducativa.github.io/archivo.html",
                                            "entradas": entradas}))

    def esperar(self, d):
        with d.calculando:
            pass

    def test_sin_archivo_no_falla(self):
        d = h.Hemeroteca(self.tmp / "no-existe.json", modelo=SinServicio())
        r = d.buscar("blender")
        self.assertEqual(r["resultados"], [])
        self.assertIn("archivo.html", r["hemeroteca"])

    def test_busca_por_palabras_sin_servicio(self):
        d = h.Hemeroteca(self.archivo, modelo=SinServicio())
        r = d.buscar("cámara de blender")
        self.assertEqual(r["resultados"][0]["mensaje"], "https://t.me/vceduca/12067")
        self.assertEqual(r["resultados"][0]["id_mensaje"], "edumedia:12067")
        self.assertEqual(r["ultimo_numero"], 4)

    def test_por_significado(self):
        d = h.Hemeroteca(self.archivo, modelo=Palabras())
        d.al_dia()
        self.esperar(d)
        self.assertEqual(d.v.shape[0], 3)
        self.assertEqual(d.buscar("jigsaw")["resultados"][0]["titular"], "Grupos de la técnica Jigsaw")

    def test_todo_un_numero_sin_consulta(self):
        d = h.Hemeroteca(self.archivo, modelo=SinServicio())
        titulares = [x["titular"] for x in d.buscar(numero=4)["resultados"]]
        self.assertEqual(titulares, ["Grupos de la técnica Jigsaw", "Un juego sobre la célula"])
        self.assertEqual(len(d.buscar(salio="2026-11-04")["resultados"]), 1)

    def test_filtro_y_consulta(self):
        d = h.Hemeroteca(self.archivo, modelo=SinServicio())
        self.assertEqual(d.buscar("blender", numero=4)["resultados"], [])

    def test_vuelve_a_leer_cuando_cambia(self):
        d = h.Hemeroteca(self.archivo, modelo=Palabras())
        d.al_dia()
        self.esperar(d)
        self.escribir([entrada(5, "2026-11-06", "Agentes en el aula", "Agentes de IA y permisos")])
        t = time.time() + 5
        os.utime(self.archivo, (t, t))  # que cambie la fecha aunque el sistema de archivos sea poco preciso
        r = d.buscar("agentes")
        self.assertEqual([x["numero"] for x in r["resultados"]], [5])
        self.esperar(d)
        self.assertEqual(d.v.shape[0], 1)

    def test_archivo_roto_conserva_lo_anterior(self):
        d = h.Hemeroteca(self.archivo, modelo=SinServicio())
        d.al_dia()
        self.archivo.write_text("{roto")
        t = time.time() + 5
        os.utime(self.archivo, (t, t))
        self.assertEqual(len(d.buscar(numero=4)["resultados"]), 2)


if __name__ == "__main__":
    unittest.main()
