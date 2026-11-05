# SPDX-License-Identifier: AGPL-3.0-or-later
"""Pruebas del MIAE y la guía Vibe coding responsable en el bot (ADR 0031), sin red ni modelo de significado."""
import io
import json
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import buscador  # noqa: E402
import marcos as m  # noqa: E402


class Palabras:
    """Un significado de juguete: un vector por palabras clave."""
    CLAVES = ("ortografía", "licencia", "accesibilidad", "cocreación")

    def _v(self, t):
        t = t.lower()
        return np.array([1.0 if c in t else 0.0 for c in self.CLAVES] + [0.01], dtype=np.float32)

    def passage_embed(self, textos, batch_size=16):
        return [self._v(t) for t in textos]

    def query_embed(self, textos):
        return [self._v(t) for t in textos]


def escribir(raiz: Path, ruta: str, texto: str) -> None:
    f = raiz / ruta
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(texto)


def fuentes(raiz: Path) -> None:
    """Un MIAE y una guía en miniatura, con la misma forma que sus repositorios."""
    g = raiz / "fuentes" / "vibe-responsable"
    miae = raiz / "fuentes" / "miae"
    for idioma in m.IDIOMAS:
        escribir(g, f"contenido/{idioma}/01-guia.md", "# La guía\n\n## Accesibilidad\n\nProbar la accesibilidad con el teclado.")
        escribir(g, f"contenido/{idioma}/capitulos/09-licencia-libre.md", "# Licencia libre\n\n## Cuál elegir\n\nLa licencia AGPL.")
        escribir(g, f"contenido/{idioma}/instrucciones-ia.md", "# Instrucciones\n\nLicencia y accesibilidad.")
        escribir(miae, f"content/v2.1/{idioma}.md", "# MIAE\n\n## Nivel 4\n\nLa cocreación entre persona e IA.")
        escribir(miae, f"data/quickref/{idioma}.json", json.dumps({
            "kicker": "Guía rápida", "lead": "La escala describe <b>cómo se reparte</b> el trabajo.",
            "levels": [{"name": "Sin IA", "split": "La persona crea.", "desc": "Nada de IA.", "examples": ["Examen"], "warn": ""},
                       {"name": "Reformulación", "split": "La IA reformula.", "desc": "Corregir la ortografía.",
                        "examples": ["Resumir"], "warn": "Corregir el estilo sigue siendo nivel 1."}],
            "back_title": "Cómo clasificar", "rules": [{"label": "Qué", "text": "La <i>tarea</i>."}]}))
        escribir(miae, f"data/guide/{idioma}.json", json.dumps({
            "guide_title": "Para empezar", "guide_intro": "Intro.", "principle": "No es calidad.",
            "steps": [["Delimita", "La tarea."]], "template_title": "Declara", "template_intro": "Completa.",
            "fields": ["Tarea", "Nivel"], "filled_title": "Ejemplo", "filled": ["Informe", "Nivel 2"],
            "teacher_title": "Para docentes", "teacher_intro": "Adapta.", "teacher_fields": ["Usos permitidos"]}))
    escribir(miae, "data/versions.json", json.dumps({"latest": "2.1"}))


class Preparar(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self.tmp.name)
        fuentes(self.raiz)
        with mock.patch.object(buscador, "modelo_significado", return_value=Palabras()):
            m.preparar(self.raiz)

    def tearDown(self):
        self.tmp.cleanup()

    def test_enlaces_de_cada_pagina(self):
        e = json.loads((self.raiz / "md" / "enlaces-ca.json").read_text())
        self.assertEqual(e["vibe-responsable · capitulo-9.md"], m.GUIA["web"] + "ca/capitulo-9.html")
        self.assertEqual(e["vibe-responsable · guia.md"], m.GUIA["web"] + "ca/guia.html")
        # el archivo para la IA, en la página que lo enseña, no el .md suelto
        self.assertEqual(e["vibe-responsable · instrucciones-vibe-responsable.md"], m.GUIA["web"] + "ca/para-la-ia.html")
        self.assertEqual(e["miae · marco.md"], m.MIAE["web"] + "v2.1/ca/")
        self.assertEqual(e["miae · guia-rapida.md"], m.MIAE["web"] + "ca/guia/")
        self.assertEqual(e["miae · ficha.md"], m.MIAE["web"] + "ca/ficha/")

    def test_json_del_miae_a_markdown(self):
        q = (self.raiz / "md" / "es" / "miae · guia-rapida.md").read_text()
        self.assertIn("**cómo se reparte**", q)
        self.assertIn("## 1. Reformulación", q)
        self.assertIn("Corregir el estilo sigue siendo nivel 1.", q)
        self.assertNotIn("<i>", q)
        f = (self.raiz / "md" / "es" / "miae · ficha.md").read_text()
        self.assertIn("- **Nivel:** Nivel 2", f)
        self.assertIn("## Para docentes", f)

    def test_buscar_con_enlace_y_obra(self):
        with mock.patch.object(buscador, "modelo_significado", return_value=Palabras()):
            b = m.Marcos(Palabras(), self.raiz)
            r = b.buscar("ortografía", "es")
            self.assertEqual(r["idioma"], "es")
            self.assertEqual(r["resultados"][0]["documento"], "miae · guia-rapida.md")
            self.assertTrue(r["resultados"][0]["enlace"].endswith("/es/guia/"))
            solo = b.buscar("licencia", "es", "miae")["resultados"]
            self.assertTrue(solo and all(x["documento"].startswith("miae ·") for x in solo))
            self.assertEqual(b.buscar("licencia", "xx")["idioma"], "es")  # un idioma raro: castellano
            leido = b.leer("vibe-responsable · capitulo-9.md", "Cuál elegir", "gl")
            self.assertIn("AGPL", leido["texto"])
            self.assertTrue(leido["enlace"].endswith("/gl/capitulo-9.html"))

    def test_sin_indice_lo_dice(self):
        with self.assertRaises(RuntimeError):
            m.Marcos(Palabras(), self.raiz / "nada").buscar("licencia", "es")


class Descargar(unittest.TestCase):
    def test_solo_texto_y_sin_salir_de_la_carpeta(self):
        datos = io.BytesIO()
        with tarfile.open(fileobj=datos, mode="w:gz") as tar:
            for nombre, texto in (("miae-main/content/v2.1/es.md", "# MIAE"), ("miae-main/data/versions.json", "{}"),
                                  ("miae-main/assets/logo.svg", "<svg/>"), ("miae-main/README.md", "# fuera"),
                                  ("miae-main/content/../../fuera.md", "# no")):
                b = texto.encode()
                info = tarfile.TarInfo(nombre)
                info.size = len(b)
                tar.addfile(info, io.BytesIO(b))
        respuesta = mock.Mock()
        respuesta.read.return_value = datos.getvalue()
        with tempfile.TemporaryDirectory() as tmp, mock.patch("urllib.request.urlopen", return_value=respuesta):
            destino = Path(tmp) / "fuentes" / "miae"
            destino.parent.mkdir()
            m.descargar(m.MIAE, destino)
            hay = sorted(str(p.relative_to(destino)) for p in destino.rglob("*") if p.is_file())
            self.assertEqual(hay, ["content/v2.1/es.md", "data/versions.json"])
            self.assertFalse((Path(tmp) / "fuera.md").exists())


class Citas(unittest.TestCase):
    def test_enlaces_del_miae_y_la_guia_son_fuentes(self):
        import consultar
        texto = ("Idea. [[https://jjdeharo.github.io/miae/es/ficha/]]\n\n"
                 "Otra. [[https://vibe-coding-educativo.github.io/vibe-responsable/es/capitulo-9.html]]\n\n"
                 "Ajena. [[https://example.com/x]]")
        self.assertEqual(len(consultar.FUENTE.findall(texto)), 2)
        x = {"tipo": "marco", "obra": "vibe-responsable", "documento": "vibe-responsable · capitulo-9.md", "texto": "t"}
        self.assertEqual(consultar.Consultor.cita("https://e/", x, "ca"), "— Guia Vibe coding responsable\nhttps://e/")
        x["obra"] = "miae"
        self.assertEqual(consultar.Consultor.cita("https://e/", x, "en"), "— MIAE\nhttps://e/")


if __name__ == "__main__":
    unittest.main()
