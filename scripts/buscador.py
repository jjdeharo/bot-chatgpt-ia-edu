# SPDX-License-Identifier: AGPL-3.0-or-later
"""Búsqueda en un grupo: por significado y por palabras, combinadas.

El índice lo construye indexar.py en datos/<grupo>/indice/. Este módulo solo lee.
"""
import json
import os
import re
import sqlite3
import unicodedata
from datetime import date
from pathlib import Path

import numpy as np

import corpus
import significado
from grupos import Grupo

MODELO = significado.MODELO
RRF = 60  # constante de la fusión por rangos recíprocos (Cormack et al., 2009)


def sin_tildes(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")


def indice(g: Grupo) -> Path:
    return g.datos / os.environ.get("INDICE", "indice")


def modelo_significado():
    """En el NAS, el servicio compartido por los dos bots y el indexador (ADR 0012)."""
    return significado.modelo()


def vector_consulta(modelo, consulta: str):
    """El de la consulta, normalizado; None si el servicio no responde y solo queda buscar por palabras."""
    try:
        q = np.array(list(modelo.query_embed([consulta])), dtype=np.float32)[0]
    except OSError as e:
        print(f"significado: sin respuesta del servicio ({e}); busco solo por palabras", flush=True)
        return None
    return q / np.linalg.norm(q)


def consulta_fts(texto: str) -> str | None:
    palabras = {p for p in re.findall(r"\w+", sin_tildes(texto)) if len(p) > 2}
    return " OR ".join(f'"{p}"' for p in sorted(palabras)) or None


class Buscador:
    def __init__(self, g: Grupo, modelo=None):
        self.g = g
        self.indice = indice(g)
        self.modelo = modelo or modelo_significado()
        self.firma = None
        self.al_dia()

    def _firma(self):
        return ((self.indice / "palabras.db").stat().st_ino, (self.g.datos / "mensajes.jsonl").stat().st_mtime)

    def al_dia(self) -> None:
        """Vuelve a cargar el índice si el proceso de la hora lo ha cambiado."""
        firma = self._firma()
        if firma != self.firma:
            self._cargar()
            self.firma = firma

    def _cargar(self) -> None:
        self.ms = corpus.cargar(self.g)
        self.temas = corpus.temas(self.g)
        self.db = sqlite3.connect(f"file:{self.indice / 'palabras.db'}?mode=ro", uri=True, check_same_thread=False)
        self.col = {}
        for c in ("mensajes", "biblioteca"):
            ids = json.loads((self.indice / f"{c}-ids.json").read_text())
            self.col[c] = {"ids": np.array(ids, dtype=np.int64), "pos": {i: n for n, i in enumerate(ids)},
                           "v": np.load(self.indice / f"{c}.npy")}
        self.obras = {o["id"]: o for o in json.loads((self.indice / "biblioteca.json").read_text())}
        # De cada enlace, lo que dice: las citas de la ayuda para enseñar las escribe el programa (ADR 0011).
        self.por_enlace = {m["enlace"]: {"tipo": "mensaje", "b": self, "i": i, "autor": m["autor"] or "?",
                                         "grupo": self.g.nombre, "fecha": m["fecha"]}
                           for i, m in self.ms.items()}
        self.por_enlace.update({o["enlace"]: {"tipo": "documento", "autor": o["autor"] or "?", "fecha": o["fecha"],
                                              "archivo": o["archivo"], "texto": o["texto"][:2000]}
                                for o in self.obras.values()})

    # --- búsqueda base -------------------------------------------------
    def _semantica(self, c: str, consulta: str, mascara) -> list[int]:
        if not len(self.col[c]["ids"]):
            return []
        q = vector_consulta(self.modelo, consulta)
        if q is None:
            return []
        s = self.col[c]["v"] @ q
        if mascara is not None:
            s = np.where(mascara, s, -np.inf)
        orden = np.argsort(-s)[:200]
        return [int(self.col[c]["ids"][i]) for i in orden if np.isfinite(s[i])]

    def _palabras(self, c: str, consulta: str, permitidos) -> list[int]:
        q = consulta_fts(consulta)
        if not q:
            return []
        filas = self.db.execute(
            f"SELECT id FROM {c} WHERE {c} MATCH ? ORDER BY bm25({c}) LIMIT 400", (q,)).fetchall()
        return [i for (i,) in filas if permitidos is None or i in permitidos][:200]

    def _mascara(self, c, autor_ids, desde, hasta):
        if not (autor_ids or desde or hasta):
            return None, None
        ok = set()
        for i in self.col[c]["ids"].tolist():
            m = self.ms[i]
            if autor_ids and m["autor_id"] not in autor_ids:
                continue
            f = m["fecha"][:10]
            if desde and f < desde or hasta and f > hasta:
                continue
            ok.add(i)
        mascara = np.array([i in ok for i in self.col[c]["ids"].tolist()])
        return mascara, ok

    def puntuar(self, c, consulta, autor_ids=None, desde=None, hasta=None) -> dict[int, float]:
        """Puntos de fusión de cada resultado; sirven para mezclar los de varios grupos."""
        mascara, permitidos = self._mascara(c, autor_ids, desde, hasta)
        puntos = {}
        for lista in (self._semantica(c, consulta, mascara), self._palabras(c, consulta, permitidos)):
            for r, i in enumerate(lista):
                puntos[i] = puntos.get(i, 0) + 1 / (RRF + r + 1)
        return puntos

    def buscar(self, c, consulta, autor_ids=None, desde=None, hasta=None, n=12) -> list[int]:
        puntos = self.puntuar(c, consulta, autor_ids, desde, hasta)
        return sorted(puntos, key=puntos.get, reverse=True)[:n]

    # --- lo que ve Claude ------------------------------------------------
    def autores(self, nombre: str) -> list[dict]:
        n = sin_tildes(nombre.lstrip("@"))
        vistos = {}
        for m in self.ms.values():
            a = sin_tildes(m["autor"] or "")
            u = sin_tildes(m["usuario"] or "")
            if n in a or n == u:
                d = vistos.setdefault(m["autor_id"], {"autor_id": m["autor_id"], "nombre": m["autor"],
                                                      "usuario": m["usuario"], "mensajes": 0})
                d["mensajes"] += 1
        return sorted(vistos.values(), key=lambda d: -d["mensajes"])[:8]

    def ficha(self, i: int, largo=600) -> dict:
        m = self.ms[i]
        d = {"id": f"{self.g.clave}:{i}", "grupo": self.g.nombre,
             "fecha": m["fecha"].replace("T", " "), "autor": m["autor"],
             "tema": self.temas.get(m["tema"], m["tema"]), "enlace": m["enlace"],
             "texto": corpus.contenido(m)[:largo]}
        if m["responde_a"] and m["responde_a"] in self.ms:
            p = self.ms[m["responde_a"]]
            d["responde_a"] = {"id": f"{self.g.clave}:{p['id']}", "autor": p["autor"],
                               "texto": corpus.contenido(p)[:200]}
        return d

    def mensajes(self, consulta, autor_ids=None, desde=None, hasta=None, n=12) -> list[dict]:
        return [self.ficha(i) for i in self.buscar("mensajes", consulta, autor_ids, desde, hasta, n)]

    def hilo(self, i: int) -> list[dict]:
        """El mensaje, aquello a lo que responde y lo que le respondieron."""
        if i not in self.ms:
            return []
        cadena, r = [], self.ms[i]
        while r["responde_a"] in self.ms and len(cadena) < 4:
            r = self.ms[r["responde_a"]]
            cadena.insert(0, r["id"])
        respuestas = [m["id"] for m in self.ms.values() if m["responde_a"] == i][:15]
        return [self.ficha(x, 900) for x in cadena + [i] + respuestas]

    def biblioteca(self, consulta, desde=None, hasta=None, n=8) -> list[dict]:
        salida = []
        for i in self.buscar("biblioteca", consulta, None, desde, hasta, n):
            o = self.obras[i]
            # Sin el id de la obra: Claude llegó a construir un enlace con él en vez de copiar «enlace».
            salida.append({"grupo": self.g.nombre, "fecha": o["fecha"][:10], "aportado_por": o["autor"],
                           "archivo": o["archivo"], "enlace": o["enlace"], "texto": o["texto"][:900]})
        return salida

    def ultimo_dia(self) -> str:
        return max(m["fecha"] for m in self.ms.values())[:10]

    def ultimo_momento(self) -> str:
        """La última puesta al día (la marca nas/bucle.sh), o la fecha del último mensaje si no consta."""
        f = corpus.DATOS / "ultima-pasada"
        try:
            return f.read_text().strip()[:16]
        except OSError:
            return max(m["fecha"] for m in self.ms.values())[:16].replace("T", " ")


def hoy() -> str:
    return date.today().isoformat()
