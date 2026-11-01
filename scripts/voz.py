#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""El servicio de voz: pasa a texto las notas de voz que reciben los bots (ADR 0022).

Usa faster-whisper con el modelo «small», el mismo que el boletín semanal, y corre
con la imagen y el entorno de Python del boletín, con el modelo ya descargado en
su caché: nada nuevo que instalar ni que pagar. El modelo se carga en cada
petición y se suelta después, así que en reposo no ocupa memoria.

    POST /transcribir   el audio tal cual (ogg/opus de Telegram, mp3, wav…)
                        → {"texto": …, "lengua": "es", "duracion": 12.3}
    GET  /salud

Un audio de más de MAX_S segundos se rechaza con 413: la CPU del NAS es de
todos. Sin red para el modelo: HF_HUB_OFFLINE=1 en el compose.
"""
import json
import os
import subprocess
import sys
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock

MODELO = os.environ.get("MODELO_VOZ", "small")
PUERTO = int(os.environ.get("VOZ_PUERTO", "8001"))
MAX_S = int(os.environ.get("VOZ_MAX_S", "180"))  # segundos de audio como mucho
MAX_BYTES = 20 * 1024 * 1024  # lo que Telegram deja bajar a un bot
HILOS = int(os.environ.get("VOZ_HILOS", "2"))
LENGUAS = ("es", "ca", "gl", "eu", "en")
# Palabras que el modelo escribe mal si no se le avisa; valen para los dos bots.
TERMINOS = ("ChatGPT, Gemini, Claude, NotebookLM, eXeLearning, iDevice, SCORM, Moodle, Procomún, vibe coding, "
            "inteligencia artificial, alumnado, docentes, Telegram.")


def duracion(ruta: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ruta)],
                       capture_output=True, text=True, timeout=30)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def a_wav(origen: Path, destino: Path) -> None:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(origen), "-vn", "-ac", "1", "-ar", "16000",
                    "-c:a", "pcm_s16le", str(destino)], check=True, capture_output=True, timeout=120)


def transcribir(wav: Path) -> dict:
    """El modelo se carga aquí y muere con la función: la memoria vuelve al sistema."""
    from faster_whisper import WhisperModel
    modelo = WhisperModel(MODELO, device="cpu", compute_type="int8", cpu_threads=HILOS)
    segmentos, info = modelo.transcribe(str(wav), vad_filter=True, initial_prompt=TERMINOS, beam_size=3)
    texto = " ".join(s.text.strip() for s in segmentos).strip()
    lengua = info.language if info.language in LENGUAS else ""
    return {"texto": texto, "lengua": lengua, "duracion": round(info.duration, 1)}


class Servicio(BaseHTTPRequestHandler):
    turno = Lock()  # de uno en uno: dos modelos a la vez doblarían la memoria

    def do_GET(self):
        if self.path != "/salud":
            return self.send_error(404)
        self._responder(200, b"ok\n", "text/plain")

    def do_POST(self):
        if self.path != "/transcribir":
            return self.send_error(404)
        n = int(self.headers.get("Content-Length") or 0)
        if not 0 < n <= MAX_BYTES:
            return self.send_error(413)
        datos = self.rfile.read(n)
        with tempfile.TemporaryDirectory() as tmp:
            origen, wav = Path(tmp) / "audio", Path(tmp) / "audio.wav"
            origen.write_bytes(datos)
            try:
                segundos = duracion(origen)
                if segundos > MAX_S:
                    return self._responder(413, json.dumps({"error": "demasiado largo", "duracion": segundos}).encode(),
                                           "application/json")
                a_wav(origen, wav)
                with self.turno:
                    salida = transcribir(wav)
            except Exception as error:  # noqa: BLE001 — un audio raro no tumba el servicio
                print(f"voz: {type(error).__name__}: {error}", file=sys.stderr, flush=True)
                return self._responder(500, json.dumps({"error": type(error).__name__}).encode(), "application/json")
        print(f"voz: {salida['duracion']} s de audio, {len(salida['texto'].split())} palabras ({salida['lengua'] or '?'})",
              flush=True)
        self._responder(200, json.dumps(salida, ensure_ascii=False).encode(), "application/json")

    def _responder(self, codigo: int, cuerpo: bytes, tipo: str) -> None:
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print(f"voz: faster-whisper «{MODELO}» en el puerto {PUERTO}", flush=True)
    ThreadingHTTPServer(("", PUERTO), Servicio).serve_forever()
