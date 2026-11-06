# SPDX-License-Identifier: AGPL-3.0-or-later
"""Cuántas personas hay en cada grupo del Bot de IA Educativa y en varios a la vez (ADR 0032).

Para el Diario de IA Educativa, que lo dibuja como tres círculos en «La redacción» y en el pie de
cada página. El bot es administrador de ChatGPT-IA-edu, Vibe Coding Educativo y EduMedia-IAG, y como
administrador puede pedir la lista de miembros de cada uno (channels.getParticipants: «Both users
and bots can use this method»). La API de bots no lo permite, así que entra con su token por el
protocolo completo de Telegram (Telethon), sin recibir sus mensajes, que siguen llegando a bot.py.

Cruza los identificadores y guarda solo las cifras, sin bots ni cuentas borradas: ningún nombre ni
identificador sale de la memoria del programa.

    python comunidades.py            si las últimas cifras tienen una semana, las rehace (lo normal)
    python comunidades.py --ya       las rehace ahora

Deja datos/comunidades/AAAA-MM-DD.json, que el diario copia a su repositorio al publicar. Si falla,
lo reintenta seis horas después; si pasan nueve días sin cifras nuevas, avisa a Juanjo una vez al día.
"""
import asyncio
import datetime
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from telethon import TelegramClient

import grupos

CARPETA = grupos.DATOS / "comunidades"
CLAVES = ("chatgpt", "vce", "edumedia")   # los del bot; eXeLearning es de Karla bot y no sale en el diario
CADA = 7          # días entre recuentos
REINTENTO = 6     # horas entre intentos fallidos
AVISO = 9         # días sin cifras nuevas antes de avisar
CRED = Path(os.environ.get("TG_CRED", Path.home() / ".config/credenciales/telegram-cuenta.json"))
BOT_CRED = Path(os.environ.get("BOT_CRED", Path.home() / ".config/credenciales/bot-chatgpt-ia-edu.json"))


def ultimo() -> datetime.date | None:
    fechas = sorted(f.stem for f in CARPETA.glob("????-??-??.json"))
    return datetime.date.fromisoformat(fechas[-1]) if fechas else None


async def miembros() -> dict[str, set[int]]:
    c = json.loads(CRED.read_text())   # api_id y api_hash de la aplicación; la sesión es la del bot
    cliente = TelegramClient(str(CARPETA / "bot.session"), int(c["api_id"]), c["api_hash"],
                             receive_updates=False, device_model="Bot de IA Educativa (comunidades)", system_version="Linux")
    await cliente.start(bot_token=json.loads(BOT_CRED.read_text())["token"])
    try:
        listas = {}
        for clave in CLAVES:
            gente = await cliente.get_participants(grupos.TODOS[clave].id)
            # Telegram no lista más de unos 10.000 por grupo: si se acerca, las cifras dejarían de ser exactas
            if gente.total and len(gente) < gente.total - 20:
                raise RuntimeError(f"{clave}: Telegram dice {gente.total} y solo ha dado {len(gente)}")
            listas[clave] = {u.id for u in gente if not u.bot and not u.deleted}
        return listas
    finally:
        await cliente.disconnect()


def cifras(s: dict[str, set[int]]) -> dict:
    a, b, c = s["chatgpt"], s["vce"], s["edumedia"]
    return {
        "fecha": datetime.date.today().isoformat(),
        "fuente": "Bot de IA Educativa, administrador de los tres grupos; sin bots ni cuentas borradas",
        "grupos": {k: len(v) for k, v in s.items()},
        "zonas": {"chatgpt": len(a - b - c), "vce": len(b - a - c), "edumedia": len(c - a - b),
                  "chatgpt+vce": len((a & b) - c), "chatgpt+edumedia": len((a & c) - b),
                  "vce+edumedia": len((b & c) - a), "tres": len(a & b & c)},
        "total": len(a | b | c),
    }


def avisar(texto: str) -> None:
    """Una vez al día, por el bot, a Juanjo."""
    marca, hoy = CARPETA / "aviso", time.strftime("%Y-%m-%d")
    if marca.exists() and marca.read_text().strip() == hoy:
        return
    print(texto)
    juanjo = int(os.environ.get("JUANJO") or 0)
    if juanjo and BOT_CRED.exists():
        token = json.loads(BOT_CRED.read_text())["token"]
        datos = urllib.parse.urlencode({"chat_id": juanjo, "text": texto}).encode()
        urllib.request.urlopen(f"https://api.telegram.org/bot{token}/sendMessage", datos, timeout=30)
        marca.write_text(hoy)


def main() -> int:
    CARPETA.mkdir(parents=True, exist_ok=True)
    hoy, u = datetime.date.today(), ultimo()
    if "--ya" not in sys.argv:
        if u and (hoy - u).days < CADA:
            return 0
        intento = CARPETA / "intento"
        if intento.exists() and time.time() - intento.stat().st_mtime < REINTENTO * 3600:
            return 0
        intento.touch()
    try:
        datos = cifras(asyncio.run(miembros()))
    except Exception as error:  # noqa: BLE001 — se reintenta más tarde; el diario sigue con las últimas
        print(f"comunidades: no he podido contar ({type(error).__name__}: {error})")
        if not u or (hoy - u).days >= AVISO:
            avisar("Aviso del Bot de IA Educativa: hace más de nueve días que no consigo contar los miembros de los "
                   f"grupos para el diario ({type(error).__name__}). El diario sigue con las cifras del {u or 'principio'}.")
        return 1
    tmp = CARPETA / f"{datos['fecha']}.tmp"
    tmp.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n")
    tmp.replace(CARPETA / f"{datos['fecha']}.json")
    print(f"comunidades: {datos['total']} personas distintas en los tres grupos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
