# SPDX-License-Identifier: AGPL-3.0-or-later
"""El modelo de significado, una sola copia para todos (ADR 0012).

En el NAS lo tiene cargado el contenedor «significado», y los dos bots y el
indexador le piden los vectores por HTTP (SIGNIFICADO_URL): una copia de casi
1 GB en vez de tres. Sin SIGNIFICADO_URL, en el portátil, cada programa carga
la suya, como antes. Los dos dan los mismos vectores.

    python significado.py      el servicio, en el puerto 8000 de la red de Docker

Para que el servicio no se quede con la memoria de cada lote que calcula: la
reserva de onnxruntime va desactivada, los textos se calculan de cuatro en
cuatro y, tras cada lote, lo liberado vuelve al sistema (ADR 0012).
"""
import ctypes
import json
import os
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import numpy as np

MODELO = os.environ.get("MODELO_SIGNIFICADO", "google/embeddinggemma-300m")
URL = os.environ.get("SIGNIFICADO_URL", "").rstrip("/")
PUERTO = int(os.environ.get("SIGNIFICADO_PUERTO", "8000"))
LOTE = 16  # textos por petición al indexar
LOTE_MODELO = int(os.environ.get("SIGNIFICADO_LOTE", "4"))  # y de cuántos en cuántos los calcula el servicio


def local():
    from fastembed import TextEmbedding
    return TextEmbedding(MODELO, threads=4, enable_cpu_mem_arena=False)


def modelo():
    """El servicio si lo hay; si no, el modelo cargado en este proceso."""
    return Remoto(URL) if URL else local()


class Remoto:
    """Lo mismo que usamos de fastembed (query_embed y passage_embed), pidiéndoselo al servicio.

    Si el servicio no responde, lanza OSError: el buscador sigue solo por palabras.
    """

    def __init__(self, url: str):
        self.url = url

    def _pedir(self, ruta: str, textos: list[str], espera: float) -> np.ndarray:
        cuerpo = json.dumps({"textos": textos}).encode()
        pet = urllib.request.Request(self.url + ruta, cuerpo, {"Content-Type": "application/json"})
        with urllib.request.urlopen(pet, timeout=espera) as r:
            dim = int(r.headers["X-Dim"])
            return np.frombuffer(r.read(), dtype="<f4").reshape(-1, dim)

    def query_embed(self, textos):
        yield from self._pedir("/consulta", list(textos), 30)

    def passage_embed(self, textos, batch_size=LOTE):
        textos = list(textos)
        for i in range(0, len(textos), batch_size):
            yield from self._pedir("/pasajes", textos[i:i + batch_size], 600)


def devolver_memoria() -> None:
    """Lo que ocupó un lote de textos largos vuelve al sistema; si no, el proceso se queda con ello."""
    try:
        ctypes.CDLL("libc.so.6").malloc_trim(0)
    except (OSError, AttributeError):
        pass


class Servicio(BaseHTTPRequestHandler):
    modelo = None
    # Los textos para indexar, de uno en uno: dos lotes a la vez doblarían la memoria. Las
    # consultas de los bots no hacen cola detrás (onnxruntime admite cálculos simultáneos).
    turno = threading.Lock()

    def do_GET(self):
        if self.path != "/salud":
            return self.send_error(404)
        self._responder(200, b"ok\n", {"Content-Type": "text/plain"})

    def do_POST(self):
        if self.path not in ("/consulta", "/pasajes"):
            return self.send_error(404)
        try:
            textos = json.loads(self.rfile.read(int(self.headers["Content-Length"])))["textos"]
            assert isinstance(textos, list) and textos and all(isinstance(t, str) for t in textos)
        except (ValueError, KeyError, TypeError, AssertionError):
            return self.send_error(400)
        if self.path == "/consulta":
            vs = list(self.modelo.query_embed(textos))
        else:
            with self.turno:
                vs = list(self.modelo.passage_embed(textos, batch_size=LOTE_MODELO))
                devolver_memoria()
        V = np.array(vs, dtype="<f4").reshape(len(textos), -1)
        self._responder(200, V.tobytes(), {"Content-Type": "application/octet-stream", "X-Dim": str(V.shape[1])})

    def _responder(self, codigo, cuerpo, cabeceras):
        self.send_response(codigo)
        for k, v in cabeceras.items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def log_message(self, *a):
        pass  # una línea por consulta solo sería ruido en docker logs


if __name__ == "__main__":
    Servicio.modelo = local()
    list(Servicio.modelo.query_embed(["prueba"]))  # la primera consulta prepara el modelo; mejor ahora
    print(f"significado: {MODELO} listo en el puerto {PUERTO}", flush=True)
    ThreadingHTTPServer(("", PUERTO), Servicio).serve_forever()
