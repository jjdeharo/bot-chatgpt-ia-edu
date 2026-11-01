# SPDX-License-Identifier: AGPL-3.0-or-later
"""Manda a IONOS la copia de lo que el bot solo tiene en el NAS.

Todo lo demás se puede rehacer: el código está en GitHub, las fichas del
repositorio en la hoja de Google y los mensajes en Telegram. Lo único que no
es quién es dueño de cada recurso (datos/catalogo.json), las preguntas sin
resolver de los dos bots (datos/sin-resolver*.jsonl) y los avisos de la
revisión del repositorio (datos/avisos.json, ADR 0013), los rechazos que su autor
pide revisar a mano (datos/revisiones.json, sin lo leído del recurso, que se
vuelve a leer; ADR 0004) y quién es del equipo de
eXeLearning (datos/equipo-exelearning.json, ADR 0008); va también la cuenta
del gasto de los dos bots (datos/estado-bot.json y datos/estado-karla.json). Lo llama nas/bucle.sh cada madrugada.
El receptor está en respaldo/ y la recuperación, en el README.
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from grupos import DATOS

CRED = Path(os.environ.get("RESPALDO_CRED", Path.home() / ".config/credenciales/respaldo-ionos.json"))
BOT_CRED = Path(os.environ.get("BOT_CRED", Path.home() / ".config/credenciales/bot-chatgpt-ia-edu.json"))
JUANJO = int(os.environ.get("JUANJO") or 0)  # en el entorno, no en el código (ADR 0020)


def leer(nombre: str) -> dict:
    try:
        return json.loads((DATOS / nombre).read_text())
    except (OSError, ValueError):
        return {}


def leer_texto(nombre: str) -> str:
    try:
        return (DATOS / nombre).read_text()
    except OSError:
        return ""


def avisar(texto: str) -> None:
    """Si la copia falla, Juanjo se entera por el propio bot; si va bien, no se le escribe nada."""
    token = json.loads(BOT_CRED.read_text())["token"]
    datos = urllib.parse.urlencode({"chat_id": JUANJO, "text": texto}).encode()
    urllib.request.urlopen(f"https://api.telegram.org/bot{token}/sendMessage", datos, timeout=30)


def main() -> int:
    try:
        enviar()
    except Exception as error:  # noqa: BLE001 — se avisa y el bucle sigue
        print(f"respaldo: {type(error).__name__}: {error}")
        avisar("Aviso del Bot de IA Educativa: no he podido mandar a IONOS la copia diaria de los "
               f"dueños de los recursos ({type(error).__name__}). El bot sigue funcionando; mañana "
               "vuelvo a intentarlo.")
        return 1
    (DATOS / "ultimo-respaldo").write_text(datetime.now(timezone.utc).isoformat(timespec="seconds"))
    return 0


def enviar() -> None:
    c = json.loads(CRED.read_text())
    copia = {"marca": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "catalogo": leer("catalogo.json"), "estado": leer("estado-bot.json"), "avisos": leer("avisos.json"),
             "equipo": leer("equipo-exelearning.json"),
             # Lo de Karla y las preguntas sin resolver faltaban hasta el 01-11-2026 (ADR 0020).
             "estado_karla": leer("estado-karla.json"),
             "sin_resolver": leer_texto("sin-resolver.jsonl"), "sin_resolver_karla": leer_texto("sin-resolver-karla.jsonl"),
             "revisiones": {k: {c: v for c, v in r.items() if c != "contenido"}
                            for k, r in leer("revisiones.json").items()}}
    pet = urllib.request.Request(c["url"], json.dumps(copia, ensure_ascii=False).encode(),
                                 {"Content-Type": "application/json", "X-Token": c["token"]})
    with urllib.request.urlopen(pet, timeout=60) as r:
        print("respaldo:", json.load(r))


if __name__ == "__main__":
    sys.exit(main())
