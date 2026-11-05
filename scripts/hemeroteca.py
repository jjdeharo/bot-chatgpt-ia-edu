# SPDX-License-Identifier: AGPL-3.0-or-later
"""Búsqueda en lo publicado por el Diario de IA Educativa (ADR 0030).

Cada mañana, cuando el sitio ya está en línea, el diario deja en datos/diario/hemeroteca.json todo lo
publicado: una entrada por pieza, breve, reportaje o editorial, con su número, el enlace en castellano
y en catalán y el mensaje original del grupo. Se toma de ahí, donde lo genera el diario, y no de la web.
El archivo se vuelve a leer cuando cambia.

Se busca como en los grupos y en el repositorio: por significado y por palabras, con la fusión por
rangos recíprocos de buscador.py. El significado de cada entrada se calcula una vez y se guarda en
datos/diario-vectores.npz; mientras falte, la entrada solo se encuentra por sus palabras.

Uso de prueba: hemeroteca.py "consulta" ["otra consulta"…]
"""
import hashlib
import json
import sqlite3
import sys
import threading

import buscador
import numpy as np
from grupos import DATOS

ARCHIVO = DATOS / "diario" / "hemeroteca.json"
VECTORES = DATOS / "diario-vectores.npz"
WEB = "https://diarioiaeducativa.github.io/"
LARGO = 900  # caracteres del texto de cada entrada que ve Claude


def texto(x: dict) -> str:
    """Lo que se indexa de una entrada: titular, entradilla y texto."""
    return ". ".join(t for t in (x.get("antetitulo"), x.get("titular"), x.get("entradilla"), x.get("texto")) if t)


def clave(t: str) -> str:
    return hashlib.sha1(t.encode()).hexdigest()


class Hemeroteca:
    def __init__(self, archivo=ARCHIVO, modelo=None):
        self.archivo = archivo
        self.modelo = modelo or buscador.modelo_significado()
        self.datos, self.entradas, self.claves, self.db = {}, [], [], None
        self.v = np.zeros((0, 0), dtype=np.float32)
        self.vectores = self._leer_vectores()
        self.firma = None
        self.calculando = threading.Lock()

    # --- puesta al día ----------------------------------------------------
    def al_dia(self) -> None:
        """Si el diario ha dejado un archivo nuevo, se lee; el significado se calcula en segundo plano."""
        try:
            firma = self.archivo.stat().st_mtime_ns
        except OSError:
            return  # sin archivo todavía: se busca con lo que haya (nada, la primera vez)
        if firma == self.firma:
            return
        try:
            datos = json.loads(self.archivo.read_text())
        except (OSError, ValueError) as e:
            print(f"hemeroteca: {type(e).__name__}: {e}; sigo con {len(self.entradas)} entradas", flush=True)
            return
        self.firma = firma
        entradas = datos.get("entradas", [])
        textos = [texto(x) for x in entradas]
        db = sqlite3.connect(":memory:", check_same_thread=False)
        db.execute("CREATE VIRTUAL TABLE entradas USING fts5(texto)")
        db.executemany("INSERT INTO entradas(rowid, texto) VALUES (?, ?)",
                       [(n, buscador.sin_tildes(t)) for n, t in enumerate(textos)])
        self.datos, self.entradas, self.claves, self.db = datos, entradas, [clave(t) for t in textos], db
        self._matriz()
        if self.calculando.acquire(blocking=False):
            threading.Thread(target=self._calcular, daemon=True).start()

    def _matriz(self) -> None:
        dim = next((len(v) for v in self.vectores.values()), 0)
        if dim:
            ceros = np.zeros(dim, dtype=np.float32)
            self.v = np.array([self.vectores.get(c, ceros) for c in self.claves], dtype=np.float32)

    def _calcular(self, lote: int = 16) -> None:
        """De lote en lote y siempre sobre las entradas vigentes: si llega un archivo nuevo mientras se
        calcula, lo suyo entra en la vuelta siguiente."""
        fallo = False
        try:
            hechos = 0
            while True:
                textos = {clave(texto(x)): texto(x) for x in self.entradas}
                parte = [c for c in textos if c not in self.vectores][:lote]
                if not parte:
                    break
                for c, v in zip(parte, self.modelo.passage_embed([textos[c] for c in parte], batch_size=lote)):
                    v = np.asarray(v, dtype=np.float32)
                    self.vectores[c] = v / np.linalg.norm(v)
                hechos += len(parte)
                self._matriz()
                self._guardar_vectores(set(textos))
            if hechos:
                print(f"hemeroteca: calculado el significado de {hechos} entradas", flush=True)
        except Exception as e:  # noqa: BLE001 — sin el servicio, se busca solo por palabras
            print(f"hemeroteca: {type(e).__name__}: {e}; busco por palabras", flush=True)
            fallo = True  # se reintenta con el siguiente archivo, no en bucle
        finally:
            self.calculando.release()
        # Un archivo llegado justo al terminar no ha podido lanzar su cálculo: se lanza aquí.
        if not fallo and any(clave(texto(x)) not in self.vectores for x in self.entradas) and self.calculando.acquire(blocking=False):
            threading.Thread(target=self._calcular, daemon=True).start()

    @staticmethod
    def _leer_vectores() -> dict:
        try:
            with np.load(VECTORES) as z:
                return dict(zip(z["claves"].tolist(), z["v"]))
        except (OSError, KeyError, ValueError):
            return {}

    def _guardar_vectores(self, vigentes: set[str]) -> None:
        vs = {c: v for c, v in self.vectores.items() if c in vigentes}
        temporal = VECTORES.with_suffix(".tmp.npz")
        np.savez(temporal, claves=np.array(list(vs)), v=np.array(list(vs.values()), dtype=np.float32))
        temporal.replace(VECTORES)

    # --- búsqueda -----------------------------------------------------------
    @staticmethod
    def ficha(x: dict) -> dict:
        """Lo que ve Claude: «mensaje» es el original del grupo, que se cita primero; «enlace», la pieza."""
        return {"tipo": x["tipo"], "numero": x["numero"], "salio": x["sale"], "seccion": x["seccion"],
                "titular": x["titular"], "entradilla": x["entradilla"], "texto": x["texto"][:LARGO],
                "grupo": x["grupo"], "mensaje": x["mensaje"], "id_mensaje": x["mensaje_id"],
                "fuentes": x["fuentes"], "enlace": x["url"], "enlace_ca": x["url_ca"]}

    def buscar(self, consulta: str | None = None, numero: int | None = None, salio: str | None = None,
               n: int = 8) -> dict:
        """Lo más parecido a la consulta; con «numero» o «salio» (AAAA-MM-DD), solo de ese número, y sin
        consulta, todo lo de ese número en su orden."""
        self.al_dia()
        entradas, db, v = self.entradas, self.db, self.v  # lo de esta lectura, aunque otra la sustituya
        cabecera = {"ultimo_numero": self.datos.get("ultimo_numero"),
                    "hemeroteca": self.datos.get("hemeroteca", WEB + "archivo.html")}
        if not entradas:
            return cabecera | {"resultados": [], "aviso": "Todavía no hay nada del diario para buscar."}
        vale = [i for i, x in enumerate(entradas)
                if (numero is None or x["numero"] == numero) and (salio is None or x["sale"] == salio)]
        if not consulta:
            return cabecera | {"resultados": [self.ficha(entradas[i]) for i in vale[:20]]}
        dentro, puntos = set(vale), {}
        if v.shape[0] == len(entradas):
            q = buscador.vector_consulta(self.modelo, consulta)
            if q is not None:
                s = v @ q
                orden = [i for i in np.argsort(-s).tolist() if i in dentro and s[i] > 0][:100]
                for r, i in enumerate(orden):
                    puntos[i] = puntos.get(i, 0) + 1 / (buscador.RRF + r + 1)
        fts = buscador.consulta_fts(consulta)
        if fts:
            filas = db.execute("SELECT rowid FROM entradas WHERE entradas MATCH ? ORDER BY bm25(entradas) LIMIT 100",
                               (fts,)).fetchall()
            for r, i in enumerate(i for (i,) in filas if i in dentro):
                puntos[i] = puntos.get(i, 0) + 1 / (buscador.RRF + r + 1)
        mejores = sorted(puntos, key=puntos.get, reverse=True)[:n]
        return cabecera | {"resultados": [self.ficha(entradas[i]) for i in mejores]}


if __name__ == "__main__":
    h = Hemeroteca()
    h.al_dia()
    with h.calculando:  # en la prueba, sí se espera al significado
        pass
    for consulta in sys.argv[1:]:
        print(f"== {consulta}")
        for x in h.buscar(consulta, n=5)["resultados"]:
            print(f"  núm. {x['numero']} ({x['salio']}) · {x['titular'][:90]}\n    {x['enlace']}\n    {x['mensaje']}")
