#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Semáforo de privacidad del Repositorio de Vibe Coding Educativo (ADR 0053).

Corre en su propio contenedor del NAS («semaforo»), con la imagen del boletín semanal, que
trae Chromium. Hace tres cosas:

  servir    escucha en el puerto 8002 de la red de los bots:
              POST /evaluar {"url"} → {"semaforo", "motivo", "fecha"}: el bot lo pide al preparar
                la ficha de un recurso, para enseñar el color y no admitir el rojo;
              GET /salud;
            y cada noche, desde las 3:30, hace la pasada.
  pasada    abre todas las aplicaciones del repositorio, escribe en la hoja las que cambian de
            color y avisa a sus autores de las que pasan a rojo o dejan de serlo.
  probar    evalúa un enlace y lo enseña, sin escribir nada.

Los avisos a los autores salen según AVISOS_SEMAFORO: «autores» los manda; «juanjo» se los
manda solo a Juanjo, para verlos; vacío, solo los apunta en el registro.

    python3 scripts/semaforo.py servir
    python3 scripts/semaforo.py pasada [--sin-hoja]
    python3 scripts/semaforo.py probar URL
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import threading
import time
import urllib.parse
import urllib.request
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import textos  # noqa: E402
from semaforo_auditar import auditar, cargar_csv, normalizar_url, url_publica  # noqa: E402
from semaforo_reglas import resumen  # noqa: E402

BASE = Path(__file__).resolve().parent.parent
DATOS = BASE / "datos"
SEM = DATOS / "semaforo"
AUDITORIA = SEM / "auditoria.json"     # lo último que se vio de cada aplicación
AVISADOS = SEM / "avisados.json"       # {enlace normalizado: "ROJO" | "BIEN"}: el último aviso a su autor
PASADAS = SEM / "pasadas"              # AAAA-MM-DD.hecho / .intentos / .log
DUENOS = DATOS / "catalogo.json"       # del bot: qué cuenta de Telegram dio de alta cada recurso (ADR 0004)
REVISIONES = DATOS / "revisiones.json" # del bot: los rechazos revisados a mano (ADR 0004)
CATALOGO_CRED = Path(os.environ.get("CATALOGO_CRED", Path.home() / ".config/credenciales/catalogo-vce.json"))
BOT_CRED = Path(os.environ.get("BOT_CRED", Path.home() / ".config/credenciales/bot-chatgpt-ia-edu.json"))
JUANJO = int(os.environ.get("JUANJO", "0") or 0)
AVISOS = os.environ.get("AVISOS_SEMAFORO", "").strip()
COLS = ("Semáforo de privacidad", "Motivo del semáforo", "Fecha del semáforo")
ADMITIDA = "Admitida tras revisión manual. "
HORA_PASADA = 3 * 60 + 30
REPOSITORIO = "https://vibe-coding-educativo.github.io/app_edu/"
CERROJO = threading.Lock()  # un navegador a la vez: la pasada y una evaluación del bot no se pisan


def registrar(texto: str) -> None:
    print(f"{datetime.now():%Y-%m-%d %H:%M:%S} {texto}", flush=True)


def leer(ruta: Path, por_defecto):
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return por_defecto


def escribir(ruta: Path, datos) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    tmp = ruta.with_suffix(".tmp")
    tmp.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(ruta)


def api(accion: str, **datos) -> dict:
    c = json.loads(CATALOGO_CRED.read_text())
    pet = urllib.request.Request(c["url"], json.dumps({"clave": c["clave"], "accion": accion, **datos}).encode(),
                                 {"Content-Type": "application/json"})
    with urllib.request.urlopen(pet, timeout=120) as r:
        res = json.load(r)
    if res.get("error"):
        raise RuntimeError(f"API del repositorio: {res['error']}")
    return res


def telegram(chat: int, texto: str) -> bool:
    token = json.loads(BOT_CRED.read_text())["token"]
    datos = urllib.parse.urlencode({"chat_id": chat, "text": texto, "link_preview_options": '{"is_disabled": true}'})
    try:
        with urllib.request.urlopen(f"https://api.telegram.org/bot{token}/sendMessage", datos.encode(), timeout=30) as r:
            return json.load(r).get("ok", False)
    except Exception as error:  # noqa: BLE001 — un aviso que no sale no para la pasada
        registrar(f"Telegram no ha aceptado el mensaje: {type(error).__name__}: {error}")
        return False


def admitida(url: str) -> bool:
    """Juanjo la revisó a mano y dijo que cumple (el «Pedir una revisión» del bot)."""
    return leer(REVISIONES, {}).get(normalizar_url(url), {}).get("estado") == "aprobado"


def evaluar(apps: list[dict], concurrencia: int = 3) -> list[dict]:
    with CERROJO:
        return asyncio.run(auditar(apps, concurrencia, avisar=lambda _: None))


def color(r: dict) -> dict:
    x = resumen(r)
    if x["semaforo"] == "ROJO" and admitida(r["url"]):
        x["motivo"] = (ADMITIDA + x["motivo"])[:300]
    return x


def no_respondio(r: dict) -> bool:
    """No se ha podido revisar entera (no contesta, error del servidor, o su contenido no se ha podido leer a
    tiempo). Entonces no se le pone color: se queda el que tenía, o gris si no tenía (Juanjo, 24-11-2026: «el
    color no debe inventarse»). Un 404 o un enlace a código sí es definitivo: «sin evaluar»."""
    return (bool(r.get("error")) or r.get("dom_sin_leer", False)
            or r.get("http_status", 0) == 0 or r.get("http_status", 0) >= 500)


def es_roja(x: dict) -> bool:
    return x["semaforo"] == "ROJO" and not x["motivo"].startswith(ADMITIDA)


# --- Lo que pide el bot ----------------------------------------------------------------------------

def evaluar_uno(url: str) -> dict:
    if not url_publica(url):
        return {"semaforo": "SIN EVALUAR", "motivo": "El enlace no lleva a una dirección pública.",
                "fecha": datetime.now().date().isoformat()}
    r = evaluar([{"url": url, "titulo": url}], 1)[0]
    if no_respondio(r) and not (r.get("http_status", 0) >= 400 and r.get("http_status", 0) < 500):
        registrar(f"evaluada para el bot: no se ha podido revisar entera · {url}")
        return {"semaforo": "PENDIENTE", "motivo": "No se ha podido revisar entera: se volverá a intentar esta noche.",
                "fecha": datetime.now().date().isoformat()}
    x = color(r)
    cache = leer(AUDITORIA, {})
    cache[normalizar_url(url)] = r
    escribir(AUDITORIA, cache)
    registrar(f"evaluada para el bot: {x['semaforo']} · {url}")
    return x


class Peticiones(BaseHTTPRequestHandler):
    def _responder(self, codigo: int, datos: dict) -> None:
        cuerpo = json.dumps(datos, ensure_ascii=False).encode()
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_GET(self):  # noqa: N802
        self._responder(200 if self.path == "/salud" else 404, {"ok": self.path == "/salud"})

    def do_POST(self):  # noqa: N802
        if self.path != "/evaluar":
            return self._responder(404, {"error": "no existe"})
        try:
            datos = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0)) or 0) or b"{}")
            self._responder(200, evaluar_uno(str(datos.get("url", "")).strip()))
        except Exception as error:  # noqa: BLE001
            registrar(f"error al evaluar: {type(error).__name__}: {error}")
            self._responder(500, {"error": str(error)})

    def log_message(self, *args):  # el registro lo lleva registrar()
        pass


# --- La pasada de cada noche -----------------------------------------------------------------------

def dueno_y_correo(url: str, filas_api: list[dict] | None) -> tuple[int | None, bool]:
    """La cuenta de Telegram del autor (si el recurso es del bot o ligó su correo) y si hay correo del formulario."""
    d = leer(DUENOS, {})
    n = normalizar_url(url)
    uid = d.get("recursos", {}).get(n)
    fila = next((f for f in filas_api or [] if normalizar_url(f.get("Enlace (URL) a la aplicación", "")) == n), {})
    correo = str(fila.get("Dirección de correo electrónico", "")).strip().lower()
    if uid is None and correo:  # correos: {cuenta de Telegram: [correos que ha ligado con su código]}
        uid = next((u for u, lista in d.get("correos", {}).items()
                    if correo in [str(x).strip().lower() for x in lista]), None)
    return (int(uid) if uid else None), bool(correo)


def avisar(app: dict, x: dict, tipo: str, filas_api: list[dict] | None) -> bool:
    """tipo «rojo» (pasa a rojo: enlace desactivado) o «bien» (deja de serlo: enlace activo otra vez)."""
    datos = {"titulo": app["titulo"], "motivo": x["motivo"].rstrip("."), "url": app["url"], "repositorio": REPOSITORIO}
    texto = textos.texto("es", f"semaforo_aviso_{tipo}", **datos)
    asunto = textos.texto("es", f"semaforo_asunto_{tipo}", **datos)
    uid, hay_correo = dueno_y_correo(app["url"], filas_api)
    via = "Telegram" if uid else ("correo" if hay_correo else "ninguna")
    if AVISOS != "autores":
        registrar(f"aviso «{tipo}» sin mandar ({AVISOS or 'solo registro'}), iría por {via}: {app['titulo']}")
        if AVISOS == "juanjo" and JUANJO:
            telegram(JUANJO, f"[Prueba: iría por {via} a su autor]\n\n{texto}")
        return False
    if uid:
        hecho = telegram(uid, texto)
    elif hay_correo:
        hecho = api("avisar_correo", url=app["url"], asunto=asunto, texto=texto).get("enviados", 0) > 0
    else:
        hecho = False
    if JUANJO:
        telegram(JUANJO, textos.texto("es", f"semaforo_a_juanjo_{tipo}", via=via if hecho else "nadie: no hay forma",
                                      **datos))
    registrar(f"aviso «{tipo}» {'mandado' if hecho else 'NO mandado'} por {via}: {app['titulo']}")
    return hecho


def pasada(sin_hoja: bool = False) -> dict:
    apps = cargar_csv()
    if len(apps) < 100:  # una hoja vacía o a medias no puede borrar colores ni mandar avisos
        raise RuntimeError(f"la hoja solo trae {len(apps)} aplicaciones")
    registrar(f"pasada: {len(apps)} aplicaciones")
    # A trozos: entre uno y otro se suelta el navegador, y una evaluación que pide el bot no espera a la pasada entera.
    vistas = []
    for i in range(0, len(apps), 12):
        vistas += evaluar(apps[i:i + 12], 3)
        if (i // 12) % 4 == 3:
            registrar(f"  pasada: {len(vistas)}/{len(apps)}")
    # Las que no han respondido (no un error 404: eso es que no existe), otra vez al final, de una en una.
    otra_vez = [k for k, r in enumerate(vistas) if no_respondio(r)]
    if otra_vez:
        for k, r in zip(otra_vez, evaluar([apps[k] for k in otra_vez], 1)):
            vistas[k] = r
        registrar(f"  segundo intento: {len(otra_vez)}; siguen sin responder {sum(no_respondio(vistas[k]) for k in otra_vez)}")
    cache = {normalizar_url(r["url"]): r for r in vistas}
    escribir(AUDITORIA, cache)

    filas, cambios, avisos_rojo, avisos_bien = [], [], [], []
    avisados = leer(AVISADOS, {})
    for app, r in zip(apps, vistas):
        x = color(r)
        actual = tuple((app["hoja"].get(c) or "").strip() for c in COLS)
        if no_respondio(r):
            continue  # sin revisarla entera no se le pone color: se queda el que tenía, o gris; mañana, otra vez
        if actual != (x["semaforo"], x["motivo"], x["fecha"]):
            filas.append({"url": app["url"], **x})
        if actual[0] and actual[0] != x["semaforo"]:
            cambios.append(f"{actual[0]} → {x['semaforo']}: {app['titulo']}")
        n = normalizar_url(app["url"])
        if es_roja(x) and avisados.get(n) != "ROJO":
            avisos_rojo.append((app, x))
        elif not es_roja(x) and avisados.get(n) == "ROJO" and x["semaforo"] != "SIN EVALUAR":
            avisos_bien.append((app, x))

    if filas and not sin_hoja:
        res = api("semaforos", filas=filas)
        registrar(f"hoja: {res.get('cambiadas', 0)} filas cambiadas")
    filas_api = api("listar")["filas"] if (avisos_rojo or avisos_bien) else None
    for tipo, lista in (("rojo", avisos_rojo), ("bien", avisos_bien)):
        for app, x in lista:
            if avisar(app, x, tipo, filas_api):
                avisados[normalizar_url(app["url"])] = "ROJO" if tipo == "rojo" else "BIEN"
    escribir(AVISADOS, avisados)
    for c in cambios:
        registrar(f"cambio de color: {c}")
    return {"apps": len(apps), "filas": len(filas), "cambios": cambios,
            "rojo": len(avisos_rojo), "bien": len(avisos_bien)}


def reloj() -> None:
    """Desde las 3:30, una pasada al día. Tres intentos; si fallan los tres, aviso a Juanjo."""
    PASADAS.mkdir(parents=True, exist_ok=True)
    while True:
        ahora = datetime.now()
        hoy = ahora.date().isoformat()
        hecho, intentos = PASADAS / f"{hoy}.hecho", PASADAS / f"{hoy}.intentos"
        n = int(intentos.read_text() or 0) if intentos.exists() else 0
        if ahora.hour * 60 + ahora.minute >= HORA_PASADA and not hecho.exists() and n < 3:
            intentos.write_text(str(n + 1))
            try:
                r = pasada()
                hecho.write_text(json.dumps(r, ensure_ascii=False))
            except Exception as error:  # noqa: BLE001
                registrar(f"la pasada ha fallado: {type(error).__name__}: {error}")
                if n + 1 >= 3 and JUANJO:
                    telegram(JUANJO, f"Semáforo de privacidad: la pasada de hoy ha fallado tres veces ({error}).")
        for viejo in PASADAS.glob("*"):
            if viejo.stat().st_mtime < time.time() - 30 * 86400:
                viejo.unlink(missing_ok=True)
        time.sleep(300)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="orden", required=True)
    sub.add_parser("servir")
    p = sub.add_parser("pasada")
    p.add_argument("--sin-hoja", action="store_true")
    p = sub.add_parser("probar")
    p.add_argument("url")
    args = ap.parse_args()
    if args.orden == "probar":
        print(json.dumps(evaluar_uno(args.url), ensure_ascii=False, indent=1))
    elif args.orden == "pasada":
        print(json.dumps(pasada(args.sin_hoja), ensure_ascii=False, indent=1))
    else:
        threading.Thread(target=reloj, daemon=True).start()
        registrar("semáforo de privacidad: escuchando en el puerto 8002")
        ThreadingHTTPServer(("0.0.0.0", 8002), Peticiones).serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
