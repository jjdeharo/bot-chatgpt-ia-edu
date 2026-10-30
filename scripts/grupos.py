# SPDX-License-Identifier: AGPL-3.0-or-later
"""Los grupos en que busca el bot y lo propio de cada uno.

Cada grupo tiene su carpeta en datos/<clave>/ con sus mensajes, sus temas,
el texto de sus PDF y su índice. Quien pregunta solo busca en los grupos de
los que es miembro (ADR 0003).

GRUPOS=chatgpt,vce en el entorno elige cuáles están en marcha; sin la
variable, ChatGPT-IA-edu, Vibe Coding Educativo y EduMedia-IAG, los del Bot de
IA Educativa.
"""
import os
from dataclasses import dataclass
from pathlib import Path

DATOS = Path(__file__).resolve().parent.parent / "datos"


@dataclass(frozen=True)
class Grupo:
    clave: str
    nombre: str
    usuario: str          # @usuario público del grupo, el de sus enlaces t.me
    id: int               # id del chat para la API de bots
    biblioteca: int | None = None  # tema que hace de Biblioteca digital, si lo tiene

    @property
    def datos(self) -> Path:
        return DATOS / self.clave

    @property
    def enlace(self) -> str:
        return f"https://t.me/{self.usuario}"


TODOS = {g.clave: g for g in (
    Grupo("chatgpt", "ChatGPT-IA-edu", "ChatGPTedu", -1001939161653, biblioteca=21753),
    Grupo("vce", "Vibe Coding Educativo", "vceduca", -1002503665937),
    Grupo("exelearning", "eXeLearning", "exelearning", -1001390659548),
    Grupo("edumedia", "EduMedia-IAG", "EduMediaIAG", -1002761310940),
)}
# Sin GRUPOS, los del Bot de IA Educativa: el grupo eXeLearning es de Karla bot (ADR 0008).
ACTIVOS = {c: TODOS[c] for c in os.environ.get("GRUPOS", "chatgpt,vce,edumedia").split(",") if c}


def por_id(chat_id: int) -> Grupo | None:
    return next((g for g in ACTIVOS.values() if g.id == chat_id), None)


def conocido(chat_id: int) -> bool:
    """Si es uno de los grupos de TODOS, aunque no esté en marcha en este bot."""
    return any(g.id == chat_id for g in TODOS.values())


def con_biblioteca() -> Grupo | None:
    return next((g for g in ACTIVOS.values() if g.biblioteca), None)
