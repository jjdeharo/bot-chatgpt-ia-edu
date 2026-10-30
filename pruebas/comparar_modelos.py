# SPDX-License-Identifier: AGPL-3.0-or-later
"""Compara modelos de significado con las preguntas de prueba.

Para cada pregunta mira en qué puesto sale el mensaje que debería encontrar
(el mejor de los esperados). Uso: comparar_modelos.py MODELO [MODELO...]
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
from fastembed import TextEmbedding

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import corpus  # noqa: E402
import grupos  # noqa: E402

AQUI = Path(__file__).resolve().parent
CACHE = corpus.DATOS / "cache-modelos"


def vectores(modelo, nombre, textos, col):
    CACHE.mkdir(exist_ok=True)
    f = CACHE / f"{nombre.replace('/', '_')}-{col}.npy"
    if f.exists():
        return np.load(f)
    t = time.time()
    orden = sorted(range(len(textos)), key=lambda n: len(textos[n]["texto"]))  # menos relleno por lote
    calc = list(modelo.passage_embed([textos[n]["texto"] for n in orden], batch_size=16))
    v = np.zeros((len(textos), len(calc[0])), dtype=np.float32)
    for n, x in zip(orden, calc):
        v[n] = x
    v /= np.linalg.norm(v, axis=1, keepdims=True)
    np.save(f, v)
    print(f"  {col}: {len(textos)} textos en {time.time() - t:.0f} s", flush=True)
    return v


def main():
    g = grupos.TODOS["chatgpt"]  # las preguntas de prueba son de ChatGPT-IA-edu
    ms = corpus.cargar(g)
    cols = {"mensajes": corpus.textos_mensajes(ms, g), "biblioteca": corpus.obras_biblioteca(ms, g)}
    preguntas = json.loads((AQUI.parent / "datos" / "preguntas-prueba.json").read_text())  # fuera del repositorio: citan mensajes reales
    for nombre in sys.argv[1:]:
        print(f"== {nombre}", flush=True)
        modelo = TextEmbedding(nombre, threads=8)
        V = {c: vectores(modelo, nombre, t, c) for c, t in cols.items()}
        puestos = []
        for q in preguntas:
            textos = cols[q["col"]]
            qv = np.array(list(modelo.query_embed([q["p"]])), dtype=np.float32)[0]
            qv /= np.linalg.norm(qv)
            orden = np.argsort(-(V[q["col"]] @ qv))
            puesto = min(n + 1 for n, i in enumerate(orden)
                         if set(textos[i].get("ids", [textos[i]["id"]])) & set(q["ids"]))
            puestos.append(puesto)
            print(f"  {puesto:5d}  {q['p'][:70]}")
        p = np.array(puestos)
        print(f"  top5 {np.mean(p <= 5):.0%} · top20 {np.mean(p <= 20):.0%} · top50 {np.mean(p <= 50):.0%}"
              f" · mediana {np.median(p):.0f}\n", flush=True)


if __name__ == "__main__":
    main()
