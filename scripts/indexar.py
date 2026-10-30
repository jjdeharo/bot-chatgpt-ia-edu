# SPDX-License-Identifier: AGPL-3.0-or-later
"""Construye o pone al día el índice de búsqueda de cada grupo en datos/<grupo>/indice/.

Solo calcula el significado de los textos nuevos o cambiados; lo que ya no
está en mensajes.jsonl (borrado en Telegram) desaparece del índice.
"""
import hashlib
import json
import shutil
import sqlite3
import time

import numpy as np

import buscador
import corpus
import grupos


def huella(t: str) -> str:
    return hashlib.sha1(t.encode()).hexdigest()[:16]


def vectores(modelo, indice, nuevo, c: str, textos: list[dict]) -> np.ndarray:
    previos = {}
    f_ids, f_v, f_h = indice / f"{c}-ids.json", indice / f"{c}.npy", indice / f"{c}-huellas.json"
    if f_ids.exists() and f_v.exists() and f_h.exists():
        ids, v, h = json.loads(f_ids.read_text()), np.load(f_v), json.loads(f_h.read_text())
        previos = {i: (h[n], v[n]) for n, i in enumerate(ids)}
    f_ids, f_v, f_h = nuevo / f"{c}-ids.json", nuevo / f"{c}.npy", nuevo / f"{c}-huellas.json"
    huellas = [huella(t["texto"]) for t in textos]
    nuevos = [n for n, t in enumerate(textos)
              if t["id"] not in previos or previos[t["id"]][0] != huellas[n]]
    dim = next(iter(previos.values()))[1].shape[0] if previos else 768  # la de EmbeddingGemma
    calc = {}
    if nuevos:
        t0 = time.time()
        nuevos.sort(key=lambda n: len(textos[n]["texto"]))  # lotes de longitud parecida: menos relleno
        vs = list(modelo.passage_embed([textos[n]["texto"] for n in nuevos], batch_size=16))
        for n, v in zip(nuevos, vs):
            calc[n] = v / np.linalg.norm(v)
        dim = len(vs[0])
        print(f"{c}: {len(nuevos)} textos nuevos o cambiados ({time.time() - t0:.0f} s)")
    V = np.zeros((len(textos), dim), dtype=np.float32)
    for n, t in enumerate(textos):
        V[n] = calc[n] if n in calc else previos[t["id"]][1]
    np.save(f_v, V)
    f_ids.write_text(json.dumps([t["id"] for t in textos]))
    f_h.write_text(json.dumps(huellas))
    retirados = len(set(previos) - {t["id"] for t in textos})
    if retirados:
        print(f"{c}: {retirados} retirados del índice")
    return V


def palabras(nuevo, cols: dict) -> None:
    tmp = nuevo / "palabras.db"
    tmp.unlink(missing_ok=True)
    db = sqlite3.connect(tmp)
    for c, textos in cols.items():
        db.execute(f"CREATE VIRTUAL TABLE {c} USING fts5(id UNINDEXED, texto, "
                   "tokenize='unicode61 remove_diacritics 2')")
        db.executemany(f"INSERT INTO {c} VALUES (?, ?)", [(t["id"], t["texto"]) for t in textos])
    db.commit()
    db.close()


def cambiar(indice, nuevo) -> None:
    """Sustituye el índice de una vez: el bot nunca lee uno a medio escribir."""
    viejo = indice.with_name(indice.name + ".viejo")
    shutil.rmtree(viejo, ignore_errors=True)
    if indice.exists():
        indice.rename(viejo)
    nuevo.rename(indice)
    shutil.rmtree(viejo, ignore_errors=True)


def indexar(g: grupos.Grupo, modelo=None):
    """Devuelve el modelo de significado, para no cargarlo otra vez en el grupo siguiente."""
    indice = buscador.indice(g)
    nuevo = indice.with_name(indice.name + ".nuevo")
    fuentes = [g.datos / "mensajes.jsonl", g.datos / "pdf-texto"]
    hecho = indice / "palabras.db"
    if hecho.exists() and all(f.stat().st_mtime < hecho.stat().st_mtime for f in fuentes if f.exists()):
        print(f"{g.clave} índice: nada nuevo")
        return modelo
    shutil.rmtree(nuevo, ignore_errors=True)
    nuevo.mkdir(parents=True)
    ms = corpus.cargar(g)
    cols = {"mensajes": corpus.textos_mensajes(ms, g), "biblioteca": corpus.obras_biblioteca(ms, g)}
    if modelo is None:
        modelo = buscador.modelo_significado()
    for c, textos in cols.items():
        vectores(modelo, indice, nuevo, c, textos)
    (nuevo / "biblioteca.json").write_text(json.dumps(cols["biblioteca"], ensure_ascii=False))
    palabras(nuevo, cols)
    cambiar(indice, nuevo)
    print(f"{g.clave} índice: {len(cols['mensajes'])} mensajes, {len(cols['biblioteca'])} obras de la biblioteca")
    return modelo


if __name__ == "__main__":
    import sys
    modelo = None
    for clave in sys.argv[1:] or grupos.ACTIVOS:
        modelo = indexar(grupos.TODOS[clave], modelo)
