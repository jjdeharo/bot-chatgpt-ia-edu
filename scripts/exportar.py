# SPDX-License-Identifier: AGPL-3.0-or-later
"""Descarga los mensajes de cada grupo a datos/<grupo>/mensajes.jsonl.

Sin argumentos, trae solo lo nuevo desde el último mensaje guardado.
Con --todo, rehace el historial completo y retira lo que se haya borrado
en Telegram: lo que un miembro quita del grupo no puede seguir en el índice.

Usa la cuenta de Juanjo (Telethon). El bot no puede leer el historial
anterior a su llegada al grupo; la cuenta sí.

Uso: exportar.py [--todo] [grupo ...]   sin grupos, todos los activos
"""
import argparse
import asyncio
import json
import os
from pathlib import Path
from zoneinfo import ZoneInfo

from telethon import TelegramClient, functions, types, utils

import grupos
from grupos import Grupo

CRED = Path(os.environ.get("TG_CRED", Path.home() / ".config/credenciales/telegram-cuenta.json"))
SESION = Path(os.environ.get("TG_SESION", Path.home() / ".config/credenciales/telegram-cuenta.session"))
ZONA = ZoneInfo("Europe/Madrid")


def tema_de(m) -> int:
    """Id del tema del mensaje; 1 es el tema General."""
    r = m.reply_to
    if r is None:
        return 1
    if getattr(r, "forum_topic", False):
        return r.reply_to_top_id or r.reply_to_msg_id
    return 1


def responde_a(m, tema: int):
    r = m.reply_to
    if r and r.reply_to_msg_id and r.reply_to_msg_id != tema:
        return r.reply_to_msg_id
    return None


def enlace(usuario: str, tema: int, id_: int) -> str:
    return f"https://t.me/{usuario}/{tema}/{id_}" if tema != 1 else f"https://t.me/{usuario}/{id_}"


def registro(m, usuario: str) -> dict:
    tema = tema_de(m)
    remitente = m.sender
    d = {
        "id": m.id,
        "fecha": m.date.astimezone(ZONA).isoformat(timespec="minutes"),
        "autor_id": m.sender_id,
        "autor": utils.get_display_name(remitente) if remitente else None,
        "usuario": getattr(remitente, "username", None),
        "tema": tema,
        "responde_a": responde_a(m, tema),
        "texto": m.message or "",
        "enlace": enlace(usuario, tema, m.id),
    }
    if m.fwd_from:
        d["reenviado"] = True
    if m.media:
        d["media"] = type(m.media).__name__.replace("MessageMedia", "")
        if m.file:
            if m.file.name:
                d["archivo"] = m.file.name
            if m.file.mime_type:
                d["mime"] = m.file.mime_type
            if m.file.size:
                d["tamano"] = m.file.size
        if isinstance(m.media, types.MessageMediaWebPage) and isinstance(m.media.webpage, types.WebPage):
            w = m.media.webpage
            d["web"] = {k: v for k, v in {"url": w.url, "titulo": w.title,
                                          "descripcion": w.description}.items() if v}
    return d


async def temas_del_grupo(c, chat) -> dict:
    if not getattr(chat, "forum", False):  # grupo sin temas, como el de eXeLearning
        return {1: "General"}
    temas, offset_date, offset_id, offset_topic = {}, None, 0, 0
    while True:
        r = await c(functions.messages.GetForumTopicsRequest(
            peer=chat, offset_date=offset_date, offset_id=offset_id,
            offset_topic=offset_topic, limit=100))
        if not r.topics:
            break
        for t in r.topics:
            if hasattr(t, "title"):
                temas[t.id] = t.title
        ultimo = r.topics[-1]
        if len(r.topics) < 100:
            break
        offset_topic, offset_id = ultimo.id, ultimo.top_message
        offset_date = getattr(ultimo, "date", None)
    temas.setdefault(1, "General")
    return temas


def leer_guardados(g: Grupo) -> dict:
    f = g.datos / "mensajes.jsonl"
    if not f.exists():
        return {}
    with f.open() as f:
        return {d["id"]: d for d in map(json.loads, f)}


def guardar(g: Grupo, mensajes: dict) -> None:
    tmp = g.datos / "mensajes.tmp"
    with tmp.open("w") as f:
        for id_ in sorted(mensajes):
            f.write(json.dumps(mensajes[id_], ensure_ascii=False) + "\n")
    tmp.replace(g.datos / "mensajes.jsonl")


def cliente_telegram() -> TelegramClient:
    c = json.loads(CRED.read_text())
    return TelegramClient(str(SESION), int(c["api_id"]), c["api_hash"],
                          device_model="Bot ChatGPT-IA-edu (índice)", system_version="Linux")


async def principal(todo: bool, claves: list[str]) -> None:
    cliente = cliente_telegram()
    await cliente.start()
    try:
        for clave in claves or grupos.ACTIVOS:
            await exportar(cliente, grupos.TODOS[clave], todo)
    finally:
        await cliente.disconnect()


async def exportar(cliente, g: Grupo, todo: bool) -> None:
    g.datos.mkdir(parents=True, exist_ok=True)
    chat = await cliente.get_entity(g.usuario)
    temas = await temas_del_grupo(cliente, chat)
    (g.datos / "temas.json").write_text(json.dumps(temas, ensure_ascii=False, indent=1))

    guardados = {} if todo else leer_guardados(g)
    desde = max(guardados, default=0)
    nuevos = {}
    async for m in cliente.iter_messages(chat, min_id=desde, reverse=True, wait_time=1):
        if isinstance(m, types.MessageService):
            continue
        nuevos[m.id] = registro(m, chat.username)
        if len(nuevos) % 2000 == 0:
            print(f"  {len(nuevos)} mensajes…", flush=True)

    if todo:
        antes = leer_guardados(g)
        borrados = set(antes) - set(nuevos)
        if borrados:
            print(f"retirados {len(borrados)} mensajes borrados en Telegram")
        mensajes = nuevos
    else:
        mensajes = {**guardados, **nuevos}
    if mensajes != (leer_guardados(g) if todo else guardados):
        guardar(g, mensajes)  # sin cambios no se reescribe: el índice no se rehace en balde
    print(f"{g.clave}: {len(nuevos)} descargados; {len(mensajes)} en total; {len(temas)} temas")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--todo", action="store_true", help="rehacer el historial completo")
    p.add_argument("grupos", nargs="*", choices=[[]] + list(grupos.TODOS), help="sin grupos, todos los activos")
    a = p.parse_args()
    asyncio.run(principal(a.todo, a.grupos))
