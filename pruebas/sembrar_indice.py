# SPDX-License-Identifier: AGPL-3.0-or-later
"""Aprovecha los vectores de la comparación para el índice definitivo.

Calcular el significado de 25.000 mensajes lleva tres cuartos de hora; si la
comparación ya lo hizo con el modelo elegido, se copia a datos/indice/ y
indexar.py solo tiene que completar lo que falte.
Uso: sembrar_indice.py MODELO [GRUPO]
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import buscador  # noqa: E402
import corpus  # noqa: E402
import grupos  # noqa: E402
import indexar  # noqa: E402

modelo = sys.argv[1]
g = grupos.TODOS[sys.argv[2] if len(sys.argv) > 2 else "chatgpt"]
INDICE = buscador.indice(g)
ms = corpus.cargar(g)
cols = {"mensajes": corpus.textos_mensajes(ms, g), "biblioteca": corpus.obras_biblioteca(ms, g)}
INDICE.mkdir(parents=True, exist_ok=True)
for c, textos in cols.items():
    f = corpus.DATOS / "cache-modelos" / f"{modelo.replace('/', '_')}-{c}.npy"
    v = np.load(f)
    assert len(v) == len(textos), f"{c}: la caché no corresponde a los textos actuales"
    np.save(INDICE / f"{c}.npy", v)
    (INDICE / f"{c}-ids.json").write_text(json.dumps([t["id"] for t in textos]))
    (INDICE / f"{c}-huellas.json").write_text(json.dumps([indexar.huella(t["texto"]) for t in textos]))
    print(f"{c}: {len(v)} vectores sembrados")
