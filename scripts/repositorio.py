# SPDX-License-Identifier: AGPL-3.0-or-later
"""Búsqueda en el Repositorio de recursos educativos digitales de Vibe Coding Educativo (ADR 0016).

Las fichas se leen de la hoja del repositorio con la misma API que usa el bot para darlas de alta
(catalogo.Hoja) y se vuelven a leer cada 15 minutos. Se busca como en los grupos: por significado y
por palabras, con la fusión por rangos recíprocos de buscador.py.

El significado de cada ficha se calcula una sola vez y se guarda en datos/repositorio-vectores.npz:
en el NAS, las 349 fichas de octubre de 2026 tardaron más de cinco minutos. Se calcula en segundo
plano, así que nadie espera por ello: mientras falte el de una ficha, esa ficha solo se encuentra por
sus palabras.

De cada ficha sale lo que ya publica la web del repositorio, nunca el correo de quien la dio de alta.

Uso de prueba: repositorio.py "consulta" ["otra consulta"…]
"""
import hashlib
import sqlite3
import sys
import threading
import time

import buscador
import numpy as np
from grupos import DATOS

WEB = "https://vibe-coding-educativo.github.io/app_edu/"  # la web del repositorio; catalogo.WEB es esta
REFRESCO = 15 * 60
ESPERA_PRIMERA = 30  # segundos que espera la primera búsqueda a que lleguen las fichas
VECTORES = DATOS / "repositorio-vectores.npz"
CAMPOS = ("titulo", "autor", "descripcion", "tipo", "niveles", "areas", "idiomas", "palabras_clave", "licencia")


def texto(f: dict) -> str:
    """Lo que se indexa de una ficha: lo que dice qué es y para quién."""
    return ". ".join(x for x in (f["titulo"], f["descripcion"], ", ".join(f["palabras_clave"]),
                                 ", ".join(f["areas"]), ", ".join(f["niveles"]), ", ".join(f["tipo"])) if x)


def clave(t: str) -> str:
    return hashlib.sha1(t.encode()).hexdigest()


class Repositorio:
    def __init__(self, hoja=None, modelo=None):
        import catalogo  # aquí y no arriba: catalogo importa consultar, que importa este módulo
        self.catalogo = catalogo
        self.hoja = hoja if hoja is not None else (catalogo.Hoja() if catalogo.CRED.exists() else None)
        self.modelo = modelo or buscador.modelo_significado()
        self.fichas, self.claves, self.db, self.por_enlace = [], [], None, {}
        self.v = np.zeros((0, 0), dtype=np.float32)
        self.vectores = self._leer_vectores()  # de cada texto indexado (por su clave), su vector
        self.momento = 0.0
        self.leyendo = threading.Lock()
        self.hay_fichas = threading.Event()

    # --- puesta al día ----------------------------------------------------
    def al_dia(self, esperar: bool = True) -> None:
        """Si toca, vuelve a leer la hoja en segundo plano. La primera búsqueda espera un poco a las fichas."""
        if self.hoja is not None and time.time() - self.momento >= REFRESCO and self.leyendo.acquire(blocking=False):
            self.momento = time.time()
            threading.Thread(target=self._refrescar, daemon=True).start()
        if esperar and not self.hay_fichas.is_set():
            self.hay_fichas.wait(ESPERA_PRIMERA)

    def _refrescar(self) -> None:
        try:
            self._cargar(self.hoja.filas())
            self.hay_fichas.set()
            self._calcular()
        except Exception as e:  # noqa: BLE001 — sin la hoja o sin el servicio, se busca con lo que haya
            print(f"repositorio: {type(e).__name__}: {e}; sigo con {len(self.fichas)} fichas", flush=True)
        finally:
            self.hay_fichas.set()
            self.leyendo.release()

    def _cargar(self, filas: list[dict]) -> None:
        """Una ficha por enlace, la última que aparece, como hace la web del repositorio."""
        vistas, fichas = set(), []
        for fila in reversed(filas):
            f = self.catalogo.de_fila(fila)
            url = f["url"].strip()
            if not f["titulo"].strip() or not url.startswith(("http://", "https://")):
                continue
            if self.catalogo.normalizar(url) in vistas:
                continue
            vistas.add(self.catalogo.normalizar(url))
            fichas.append({k: f[k] for k in CAMPOS} | {"url": url, "ficha": self.catalogo.enlace_catalogo(url)})
        textos = [texto(f) for f in fichas]
        db = sqlite3.connect(":memory:", check_same_thread=False)
        db.execute("CREATE VIRTUAL TABLE fichas USING fts5(texto)")
        db.executemany("INSERT INTO fichas(rowid, texto) VALUES (?, ?)",
                       [(n, buscador.sin_tildes(f"{t}. {f['autor']}")) for n, (t, f) in enumerate(zip(textos, fichas))])
        por_enlace = {f["ficha"]: {"tipo": "recurso", "autor": f["autor"] or "?", "titulo": f["titulo"], "texto": t}
                      for f, t in zip(fichas, textos)}
        self.fichas, self.claves, self.db, self.por_enlace = fichas, [clave(t) for t in textos], db, por_enlace
        self._matriz()

    def _matriz(self) -> None:
        """Los vectores en el orden de las fichas; el de una ficha sin calcular, a cero (no puntúa)."""
        dim = next((len(v) for v in self.vectores.values()), 0)
        if dim:
            ceros = np.zeros(dim, dtype=np.float32)
            self.v = np.array([self.vectores.get(c, ceros) for c in self.claves], dtype=np.float32)

    def _calcular(self, lote: int = 16) -> None:
        """El significado de las fichas que no lo tienen, de lote en lote, guardándolo en disco cada vez."""
        textos = {c: texto(f) for c, f in zip(self.claves, self.fichas)}
        faltan = [c for c in self.claves if c not in self.vectores]
        for i in range(0, len(faltan), lote):
            parte = faltan[i:i + lote]
            for c, v in zip(parte, self.modelo.passage_embed([textos[c] for c in parte], batch_size=lote)):
                v = np.asarray(v, dtype=np.float32)
                self.vectores[c] = v / np.linalg.norm(v)
            self._matriz()
            self._guardar_vectores(set(self.claves))
        if faltan:
            print(f"repositorio: calculado el significado de {len(faltan)} fichas", flush=True)

    @staticmethod
    def _leer_vectores() -> dict:
        try:
            with np.load(VECTORES) as z:
                return dict(zip(z["claves"].tolist(), z["v"]))
        except (OSError, KeyError, ValueError):
            return {}

    def _guardar_vectores(self, vigentes: set[str]) -> None:
        """Solo los de las fichas que siguen en el repositorio."""
        vs = {c: v for c, v in self.vectores.items() if c in vigentes}
        temporal = VECTORES.with_suffix(".tmp.npz")
        np.savez(temporal, claves=np.array(list(vs)), v=np.array(list(vs.values()), dtype=np.float32))
        temporal.replace(VECTORES)

    # --- búsqueda -----------------------------------------------------------
    def buscar(self, consulta: str, n: int = 8) -> list[dict]:
        self.al_dia()
        fichas, db, v = self.fichas, self.db, self.v  # lo de esta lectura, aunque otra la sustituya mientras
        if not fichas:
            return []
        puntos = {}
        if v.shape[0] == len(fichas):
            q = buscador.vector_consulta(self.modelo, consulta)
            if q is not None:
                s = v @ q
                for r, i in enumerate(i for i in np.argsort(-s)[:100].tolist() if s[i] > 0):
                    puntos[i] = puntos.get(i, 0) + 1 / (buscador.RRF + r + 1)
        fts = buscador.consulta_fts(consulta)
        if fts:
            filas = db.execute("SELECT rowid FROM fichas WHERE fichas MATCH ? ORDER BY bm25(fichas) LIMIT 100",
                               (fts,)).fetchall()
            for r, (i,) in enumerate(filas):
                puntos[i] = puntos.get(i, 0) + 1 / (buscador.RRF + r + 1)
        salida = []
        for i in sorted(puntos, key=puntos.get, reverse=True)[:n]:
            f = fichas[i]
            # «enlace» es la ficha en la web del repositorio, que es lo que se cita; «url», el recurso mismo.
            salida.append({"titulo": f["titulo"], "autor": f["autor"], "descripcion": f["descripcion"][:500],
                           "tipo": f["tipo"], "niveles": f["niveles"], "areas": f["areas"], "idiomas": f["idiomas"],
                           "licencia": f["licencia"], "url": f["url"], "enlace": f["ficha"]})
        return salida


if __name__ == "__main__":
    r = Repositorio()
    r.al_dia()
    if r.leyendo.locked():
        print("calculando el significado de las fichas nuevas…", flush=True)
        with r.leyendo:  # en la prueba, sí se espera a que acabe
            pass
    for consulta in sys.argv[1:]:
        print(f"== {consulta}")
        for f in r.buscar(consulta, 6):
            print(f"  {f['titulo']} · {f['autor']} · {', '.join(f['niveles'])}\n    {f['enlace']}")
