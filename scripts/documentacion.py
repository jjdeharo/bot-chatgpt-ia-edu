# SPDX-License-Identifier: AGPL-3.0-or-later
"""Documentación de un programa (manual, documentación técnica, complementos) para buscar en ella.

Prototipo para el bot de eXeLearning (27-10-2026). Los documentos son los Markdown
que ya prepara cada día memoria-telegram para el cuaderno de NotebookLM: aquí no
se descarga nada, se leen de donde se generan.

Cada documento se trocea por apartados (encabezados de Markdown). Un apartado
largo se parte por párrafos, y una tabla por filas, repitiendo su cabecera en
cada trozo: el catálogo de iDevices es una tabla enorme y, entera, no la lee el
modelo de significado. Cada trozo lleva delante el título del documento y la
ruta de encabezados, para que se entienda solo.

Uso: documentacion.py indexar CARPETA... --salida DIR
     documentacion.py buscar DIR "consulta"
"""
import argparse
import json
import re
import shutil
import sqlite3
from pathlib import Path

import numpy as np

import buscador

LARGO = 1500      # caracteres por trozo: el modelo de significado no lee mucho más
SECCION = 12000   # caracteres como mucho al leer un apartado entero


def apartados(texto: str) -> list[tuple[list[str], str]]:
    """[(ruta de encabezados, cuerpo)] en el orden del documento; ignora los # de los bloques de código."""
    salida, ruta, cuerpo, en_codigo = [], [], [], False
    for linea in texto.splitlines():
        if linea.lstrip().startswith("```"):
            en_codigo = not en_codigo
        m = None if en_codigo else re.match(r"^(#{1,6})\s+(.*)", linea)
        if m:
            if "".join(cuerpo).strip():
                salida.append((list(ruta), "\n".join(cuerpo).strip()))
            nivel = len(m.group(1))
            ruta = ruta[:nivel - 1] + [""] * max(0, nivel - 1 - len(ruta)) + [m.group(2).strip()]
            cuerpo = []
        else:
            cuerpo.append(linea)
    if "".join(cuerpo).strip():
        salida.append((list(ruta), "\n".join(cuerpo).strip()))
    return salida


def bloques(cuerpo: str) -> list[str]:
    """Párrafos, con cada tabla partida en filas sueltas precedidas de su cabecera."""
    salida = []
    for parrafo in re.split(r"\n\s*\n", cuerpo):
        lineas = parrafo.splitlines()
        if len(lineas) >= 3 and all(l.strip().startswith("|") for l in lineas[:2]) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lineas[1]):
            cabecera = "\n".join(lineas[:2])
            salida += [f"{cabecera}\n{fila}" for fila in lineas[2:] if fila.strip()]
        else:
            salida.append(parrafo.strip())
    return [b for b in salida if b]


def trozos(nombre: str, texto: str) -> list[dict]:
    titulo = nombre.removesuffix(".md")
    salida = []
    for n, (ruta, cuerpo) in enumerate(apartados(texto)):
        seccion = " › ".join(r for r in ruta if r) or "(inicio)"
        cabeza = f"[{titulo} › {seccion}]\n"
        actual = ""
        for b in bloques(cuerpo):
            if actual and len(cabeza) + len(actual) + len(b) > LARGO:
                salida.append({"doc": nombre, "seccion": seccion, "n": n, "texto": cabeza + actual})
                actual = ""
            actual = f"{actual}\n\n{b}" if actual else b
            while len(cabeza) + len(actual) > LARGO:  # un párrafo solo ya es demasiado largo
                corte = LARGO - len(cabeza)
                salida.append({"doc": nombre, "seccion": seccion, "n": n, "texto": cabeza + actual[:corte]})
                actual = actual[corte:]
        if actual.strip():
            salida.append({"doc": nombre, "seccion": seccion, "n": n, "texto": cabeza + actual})
    return salida


def indexar(carpetas: list[Path], destino: Path) -> None:
    todos, textos = [], {}
    for carpeta in carpetas:
        for f in sorted(carpeta.glob("*.md")):
            if f.name in textos:
                continue  # el mismo documento en dos carpetas: vale el primero
            textos[f.name] = f.read_text()
            todos += trozos(f.name, textos[f.name])
    for i, t in enumerate(todos):
        t["id"] = i
    # Solo se calcula lo nuevo o cambiado: el resto se toma del índice anterior.
    previos = {}
    if (destino / "trozos.json").exists():
        viejos = json.loads((destino / "trozos.json").read_text())
        if [t["texto"] for t in viejos] == [t["texto"] for t in todos]:
            print("documentación: nada nuevo")  # no se reescribe: el bot no recarga en balde
            return
    nuevo = destino.with_name(destino.name + ".nuevo")
    shutil.rmtree(nuevo, ignore_errors=True)
    nuevo.mkdir(parents=True)
    if (destino / "trozos.json").exists():
        Vv = np.load(destino / "docs.npy")
        previos = {t["texto"]: Vv[n] for n, t in enumerate(viejos)}
    faltan = sorted({t["texto"] for t in todos if t["texto"] not in previos}, key=len)  # lotes parejos
    if faltan:
        modelo = buscador.modelo_significado()
        for texto, v in zip(faltan, modelo.passage_embed(faltan, batch_size=16)):
            previos[texto] = v / np.linalg.norm(v)
    print(f"{len(faltan)} trozos nuevos o cambiados de {len(todos)}")
    V = np.array([previos[t["texto"]] for t in todos], dtype=np.float32)
    np.save(nuevo / "docs.npy", V)
    (nuevo / "trozos.json").write_text(json.dumps(todos, ensure_ascii=False))
    (nuevo / "documentos.json").write_text(json.dumps(textos, ensure_ascii=False))
    db = sqlite3.connect(nuevo / "palabras.db")
    db.execute("CREATE VIRTUAL TABLE docs USING fts5(id UNINDEXED, texto, tokenize='unicode61 remove_diacritics 2')")
    db.executemany("INSERT INTO docs VALUES (?, ?)", [(t["id"], t["texto"]) for t in todos])
    db.commit()
    db.close()
    shutil.rmtree(destino, ignore_errors=True)
    nuevo.rename(destino)
    print(f"{len(textos)} documentos, {len(todos)} trozos")


class Documentacion:
    def __init__(self, carpeta: Path, modelo=None):
        self.modelo = modelo or buscador.modelo_significado()
        self.trozos = json.loads((carpeta / "trozos.json").read_text())
        self.textos = json.loads((carpeta / "documentos.json").read_text())
        self.V = np.load(carpeta / "docs.npy")
        self.db = sqlite3.connect(f"file:{carpeta / 'palabras.db'}?mode=ro", uri=True, check_same_thread=False)

    def buscar(self, consulta: str, n: int = 8, documento: str | None = None) -> list[dict]:
        """«documento»: limitar a los documentos cuyo nombre contenga ese texto (p. ej. CHANGELOG)."""
        dentro = None
        if documento:
            dentro = {i for i, t in enumerate(self.trozos) if documento.lower() in t["doc"].lower()}
        q = buscador.vector_consulta(self.modelo, consulta)
        semantica = []
        if q is not None:
            s = self.V @ q
            if dentro is not None:
                s = np.where([i in dentro for i in range(len(s))], s, -np.inf)
            semantica = [i for i in np.argsort(-s)[:200].tolist() if np.isfinite(s[i])]
        fts = buscador.consulta_fts(consulta)
        palabras = [i for (i,) in self.db.execute(
            "SELECT id FROM docs WHERE docs MATCH ? ORDER BY bm25(docs) LIMIT 400", (fts,))
                    if dentro is None or i in dentro][:200] if fts else []
        puntos = {}
        for lista in (semantica, palabras):
            for r, i in enumerate(lista):
                puntos[i] = puntos.get(i, 0) + 1 / (buscador.RRF + r + 1)
        mejores = sorted(puntos, key=puntos.get, reverse=True)[:n]
        return [{"documento": self.trozos[i]["doc"], "apartado": self.trozos[i]["seccion"],
                 "texto": self.trozos[i]["texto"]} for i in mejores]

    def leer(self, documento: str, apartado: str | None = None) -> dict:
        """Un apartado entero (con sus subapartados) o, sin apartado, el índice del documento."""
        if documento not in self.textos:
            parecidos = [d for d in self.textos if documento.lower().removesuffix(".md") in d.lower()]
            if len(parecidos) != 1:
                return {"error": "No existe ese documento", "documentos": sorted(self.textos)}
            documento = parecidos[0]
        partes = apartados(self.textos[documento])
        if not apartado:
            return {"documento": documento,
                    "apartados": [" › ".join(r for r in ruta if r) for ruta, _ in partes][:300]}
        elegidas = [(ruta, c) for ruta, c in partes if apartado.lower() in " › ".join(ruta).lower()]
        if not elegidas:
            return {"error": "No existe ese apartado", "apartados": [" › ".join(r for r in ruta if r) for ruta, _ in partes][:300]}
        texto = "\n\n".join(f"## {' › '.join(r for r in ruta if r)}\n{c}" for ruta, c in elegidas)
        salida = {"documento": documento, "texto": texto[:SECCION]}
        if len(texto) > SECCION:
            salida["aviso"] = f"Apartado recortado: {len(texto)} caracteres; pide uno más concreto."
        return salida


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="orden", required=True)
    i = sub.add_parser("indexar")
    i.add_argument("carpetas", nargs="+", type=Path)
    i.add_argument("--salida", type=Path, required=True)
    b = sub.add_parser("buscar")
    b.add_argument("carpeta", type=Path)
    b.add_argument("consulta")
    a = p.parse_args()
    if a.orden == "indexar":
        indexar(a.carpetas, a.salida)
    else:
        for r in Documentacion(a.carpeta).buscar(a.consulta):
            print(f"· {r['documento']} › {r['apartado']}\n  {r['texto'][:200]!r}")
