#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""El gorro de Papá Noel en las vacaciones de Navidad (ADR 0051).

Del 22 de diciembre al 6 de enero, ambos incluidos (las vacaciones escolares de Cataluña), el Bot de IA
Educativa y Karla bot llevan su foto con gorro, y los grupos de `GRUPOS` la suya; el 7 de enero vuelven las de
siempre. Lo lanza cada pasada de `nas/bucle.sh`: compara lo que toca con lo que dejó la última vez
(`datos/navidad-estado.json`, foto por foto) y solo hace algo al cambiar, así que no repite ni vuelve a subir fotos. Si una foto falla,
no apunta su cambio y la reintenta en la pasada siguiente; a Juanjo le escribe el bot por privado lo que ha
cambiado y, una vez al día como mucho, lo que no ha ido.

Las fotos de los bots, con su API (`setMyProfilePhoto`); las de los grupos, con la cuenta de Juanjo, como las
cambiaba él a mano otros años (el bot no tiene en esos grupos el permiso de cambiar la información).
Sin el archivo de estado (la primera vez), apunta lo que toca sin cambiar nada fuera de Navidad.

    python navidad.py            # lo que toque hoy
    python navidad.py --fecha 2026-12-22 --simular   # qué haría ese día, sin tocar nada
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import urllib.parse
import urllib.request
import uuid
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
IMAGEN = RAIZ / "imagen"
NAVIDAD_IMG = IMAGEN / "navidad"
ESTADO = RAIZ / "datos" / "navidad-estado.json"
DESDE, HASTA = "12-22", "01-06"   # mes-día, ambos incluidos

JUANJO = int(os.environ.get("JUANJO") or 0)
BOT_CRED = Path(os.environ.get("BOT_CRED", Path.home() / ".config/credenciales/bot-chatgpt-ia-edu.json"))
KARLA_CRED = Path(os.environ.get("KARLA_CRED", BOT_CRED.with_name("karla-bot.json")))

# (nombre, credenciales, foto con gorro, foto de siempre)
BOTS = [
    ("Bot de IA Educativa", BOT_CRED, NAVIDAD_IMG / "avatar-navidad.jpg", IMAGEN / "avatar.jpg"),
    ("Karla bot", KARLA_CRED, NAVIDAD_IMG / "karla-navidad.jpg", RAIZ / "docs" / "imagenes" / "karla-avatar.jpg"),
]
# (nombre, alias, foto con gorro, foto de siempre). EduMedia-IAG, solo si Raül Torres lo aprueba.
GRUPOS = [
    ("ChatGPT-IA-edu", "ChatGPTedu", NAVIDAD_IMG / "grupo-chatgptedu-navidad.jpg", NAVIDAD_IMG / "grupo-chatgptedu.jpg"),
    ("Vibe Coding Educativo", "vceduca", NAVIDAD_IMG / "grupo-vceduca-navidad.jpg", NAVIDAD_IMG / "grupo-vceduca.jpg"),
]


def es_navidad(d: date) -> bool:
    md = d.strftime("%m-%d")
    return md >= DESDE or md <= HASTA


def api(token: str, metodo: str, campos: dict, archivos: dict[str, Path] | None = None) -> dict:
    """Una llamada a la API de bots; con archivos, en multipart/form-data."""
    url = f"https://api.telegram.org/bot{token}/{metodo}"
    if not archivos:
        datos = urllib.parse.urlencode(campos).encode()
        req = urllib.request.Request(url, datos)
    else:
        lim = uuid.uuid4().hex
        partes = []
        for k, v in campos.items():
            partes.append(f'--{lim}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
        for k, ruta in archivos.items():
            partes.append(f'--{lim}\r\nContent-Disposition: form-data; name="{k}"; filename="{ruta.name}"\r\n'
                          f'Content-Type: image/jpeg\r\n\r\n'.encode() + ruta.read_bytes() + b"\r\n")
        partes.append(f"--{lim}--\r\n".encode())
        req = urllib.request.Request(url, b"".join(partes), {"Content-Type": f"multipart/form-data; boundary={lim}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        res = json.load(r)
    if not res.get("ok"):
        raise RuntimeError(res.get("description") or metodo)
    return res


def foto_bot(cred: Path, foto: Path) -> None:
    token = json.loads(cred.read_text())["token"]
    api(token, "setMyProfilePhoto", {"photo": json.dumps({"type": "static", "photo": "attach://foto"})}, {"foto": foto})


async def fotos_grupos(cambios: list[tuple[str, Path]]) -> list[str]:
    """Con la cuenta de Juanjo (la misma sesión que `exportar.py`). Devuelve los fallos."""
    from telethon import functions, types
    from exportar import cliente_telegram
    fallos = []
    cliente = cliente_telegram()
    await cliente.start()
    try:
        for alias, foto in cambios:
            try:
                subida = await cliente.upload_file(str(foto))
                await cliente(functions.channels.EditPhotoRequest(alias, types.InputChatUploadedPhoto(file=subida)))
            except Exception as e:  # noqa: BLE001 — se apunta y se sigue con los demás
                fallos.append(f"{alias}: {type(e).__name__}: {e}")
    finally:
        await cliente.disconnect()
    return fallos


def avisar(texto: str) -> None:
    if not JUANJO:
        print(texto)
        return
    token = json.loads(BOT_CRED.read_text())["token"]
    api(token, "sendMessage", {"chat_id": JUANJO, "text": texto})


def leer_estado() -> dict:
    try:
        return json.loads(ESTADO.read_text())
    except (OSError, ValueError):
        return {}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fecha", help="AAAA-MM-DD (por defecto, hoy)")
    ap.add_argument("--simular", action="store_true", help="dice qué haría, sin tocar nada")
    a = ap.parse_args()
    hoy = date.fromisoformat(a.fecha) if a.fecha else date.today()
    toca = "puesto" if es_navidad(hoy) else "quitado"
    poner = toca == "puesto"
    estado = leer_estado()   # {nombre: "puesto"|"quitado", "aviso": fecha del último aviso de fallo}
    nombres = [b[0] for b in BOTS] + [g[0] for g in GRUPOS]
    if not any(n in estado for n in nombres) and not poner:   # la primera vez, fuera de Navidad: nada que deshacer
        if not a.simular:
            estado.update({n: toca for n in nombres})
            ESTADO.write_text(json.dumps(estado, ensure_ascii=False) + "\n")
        return 0
    # Cada foto por separado: si una falla, solo se reintenta esa (no se vuelven a subir las que ya cambiaron)
    pendientes = [n for n in nombres if estado.get(n) != toca]
    if not pendientes:
        return 0
    if a.simular:
        print(f"navidad: {hoy} → {'pondría' if poner else 'quitaría'} el gorro en " + ", ".join(pendientes))
        return 0
    fallos = []
    for nombre, cred, con, sin in BOTS:
        if nombre in pendientes:
            try:
                foto_bot(cred, con if poner else sin)
                estado[nombre] = toca
            except Exception as e:  # noqa: BLE001
                fallos.append(f"{nombre}: {type(e).__name__}: {e}")
    grupos = [(n, alias, con if poner else sin) for n, alias, con, sin in GRUPOS if n in pendientes]
    if grupos:
        mal = asyncio.run(fotos_grupos([(alias, f) for _, alias, f in grupos]))
        for n, alias, _ in grupos:
            if not any(m.startswith(alias + ":") for m in mal):
                estado[n] = toca
        fallos += mal
    hechos = [n for n in pendientes if estado.get(n) == toca]
    aviso = ""
    if hechos:
        aviso = "Gorro de Navidad " + ("puesto" if poner else "quitado") + ": " + ", ".join(hechos) + "."
    if fallos and estado.get("aviso") != hoy.isoformat():   # un aviso de fallo al día, como mucho
        estado["aviso"] = hoy.isoformat()
        aviso += ("\n\n" if aviso else "") + ("No he podido " + ("ponerlo" if poner else "quitarlo") +
                  " en todo; lo reintento cada cuarto de hora:\n" + "\n".join(fallos))
    ESTADO.write_text(json.dumps(estado, ensure_ascii=False) + "\n")
    if fallos:
        print("navidad: con fallos: " + "; ".join(fallos))
    if aviso:
        avisar(aviso)
    return 1 if fallos else 0


if __name__ == "__main__":
    raise SystemExit(main())
