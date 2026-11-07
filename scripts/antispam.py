# SPDX-License-Identifier: AGPL-3.0-or-later
"""Contra el spam de los grupos, sin IA (ADR 0033).

El antispam propio de Telegram, activado el 31-10-2026 en los cuatro grupos, no borró nada en una
semana, y los administradores siguieron quitando a mano anuncios en chino y ráfagas de mensajes. El
bot que administra cada grupo (el Bot de IA Educativa en ChatGPT-IA-edu, Vibe Coding Educativo y
EduMedia-IAG; Karla bot en eXeLearning) borra el mensaje y expulsa a quien lo escribe cuando:

- es alguien nuevo: nunca había escrito en el grupo (no está en datos/<grupo>/mensajes.jsonl) y el
  bot le ha visto como mucho NUEVO_MAX mensajes desde que arrancó, y
- el mensaje (o su nombre) va en chino, japonés, coreano o cirílico, o menciona varios bots;
  o manda más de RAFAGA_N mensajes en RAFAGA_S segundos.

Además, quien entra en el grupo con el nombre en esas escrituras sale en el momento, aunque no haya
escrito nada, salvo que ya hubiera escrito antes en el grupo (Juanjo, 07-11-2026: «los que tienen
nombres en chino o cirílico los borro directamente y los marco como spam, aunque no hayan escrito
nada»). Marcarlos como spam solo puede hacerlo una cuenta de persona, no un bot.

Nunca a un administrador, a un bot ni a un mensaje enviado en nombre de un canal o del propio grupo.
A Juanjo le llega cada expulsión por privado, con el mensaje y un botón «Deshacer» que vuelve a
admitir a la persona (los mensajes borrados no vuelven). La expulsión borra también lo demás que
hubiera escrito en el grupo, que en una cuenta nueva es lo del mismo envío.
"""
from __future__ import annotations

import hashlib
import hmac
import html
import json
import re
import time

NUEVO_MAX = 3          # mensajes que el bot puede haberle visto antes y seguir contando como nuevo
RAFAGA_N, RAFAGA_S = 5, 60
RECARGA_S = 3600       # cada cuánto se vuelve a leer quién ha escrito alguna vez en cada grupo
# Chino, japonés y coreano (también los signos de puntuación de esas lenguas) y cirílico
ESCRITURA = re.compile(r"[Ѐ-ӿ　-ヿ㐀-䶿一-鿿가-힯＀-￯]")
OTRO_BOT = re.compile(r"(?:@|t(?:elegram)?\.me/)[A-Za-z0-9_]{3,}bot\b", re.I)


def motivo(msg: dict) -> str | None:
    """Por qué el mensaje de alguien nuevo es spam, o None."""
    texto = (msg.get("text") or msg.get("caption") or "")
    de = msg.get("from") or {}
    nombre = " ".join(x for x in (de.get("first_name"), de.get("last_name")) if x)
    if len(ESCRITURA.findall(texto)) >= 2:
        return "escribe en chino, japonés, coreano o cirílico"
    if len(ESCRITURA.findall(nombre)) >= 2:
        return "su nombre está en chino, japonés, coreano o cirílico"
    # Varios bots a la vez: uno solo es casi siempre una orden («/donate@AntiUserbotsBot») o una
    # recomendación («@askplexbot»), como en cinco primeros mensajes legítimos de la historia de los grupos
    if len({b.lower() for b in OTRO_BOT.findall(texto)}) >= 2:
        return "menciona varios bots"
    return None


class Antispam:
    def __init__(self, tg, token: str, juanjo: int, registrar, lista):
        """«lista»: los grupos que administra este bot (Karla, solo eXeLearning)."""
        self.tg, self.token, self.juanjo, self.registrar = tg, token, juanjo, registrar
        self.grupos = {g.id: g for g in lista}
        self.autores: dict[int, set[int]] = {}   # grupo -> quién ha escrito alguna vez (del índice)
        self.cargado = 0.0
        self.vistos: dict[tuple[int, int], list[tuple[float, int]]] = {}  # (grupo, persona) -> (momento, mensaje)
        self.expulsados: set[tuple[int, int]] = set()

    def cargar(self) -> None:
        """Quién ha escrito alguna vez en cada grupo, del índice que se pone al día cada 15 minutos."""
        for g in self.grupos.values():
            ids = set()
            try:
                with open(g.datos / "mensajes.jsonl", encoding="utf-8") as f:
                    for linea in f:
                        try:
                            a = json.loads(linea).get("autor_id")
                        except ValueError:
                            continue
                        if a:
                            ids.add(int(a))
            except OSError:
                pass
            if ids or g.id not in self.autores:
                self.autores[g.id] = ids
        self.cargado = time.time()

    def nuevo(self, chat: int, uid: int, tope: int = NUEVO_MAX) -> bool:
        """Nunca había escrito en el grupo y el bot le ha visto como mucho «tope» mensajes."""
        if time.time() - self.cargado > RECARGA_S:
            self.cargar()
        if not self.autores.get(chat):
            return False  # sin la lista de quién ha escrito, no se puede saber quién es nuevo: no se actúa
        return uid not in self.autores[chat] and len(self.vistos.get((chat, uid), [])) <= tope

    def firma(self, chat: int, uid: int) -> str:
        return hmac.new(self.token.encode(), f"as:{chat}:{uid}".encode(), hashlib.sha256).hexdigest()[:10]

    def revisar(self, msg: dict) -> bool:
        """True si el mensaje era spam y se ha quitado: quien llama no hace nada más con él."""
        chat, de = msg["chat"]["id"], msg.get("from") or {}
        uid = de.get("id")
        if not uid or de.get("is_bot") or msg.get("sender_chat") or not self.grupos.get(chat):
            return False
        if (chat, uid) in self.expulsados:  # lo que llega después de expulsarle, en el mismo envío
            self.tg("deleteMessage", chat_id=chat, message_id=msg["message_id"])
            return True
        ahora = time.time()
        vistos = [v for v in self.vistos.get((chat, uid), []) if ahora - v[0] < 24 * 3600]
        vistos.append((ahora, msg["message_id"]))
        self.vistos[(chat, uid)] = vistos[-(RAFAGA_N + NUEVO_MAX + 1):]
        rafaga = [m for t, m in vistos if ahora - t < RAFAGA_S]
        porque = motivo(msg) if self.nuevo(chat, uid) else None
        if not porque and len(rafaga) > RAFAGA_N and self.nuevo(chat, uid, RAFAGA_N + NUEVO_MAX + 1):
            porque = f"{len(rafaga)} mensajes en menos de un minuto"
        if not porque:
            return False
        estado = (self.tg("getChatMember", chat_id=chat, user_id=uid) or {}).get("status")
        if estado not in ("member", "restricted"):
            return False  # administradores, creador o quien ya no está: no se toca
        for m in set(rafaga) | {msg["message_id"]}:
            self.tg("deleteMessage", chat_id=chat, message_id=m)
        self.expulsar(chat, de, porque, msg)
        return True

    def expulsar(self, chat: int, de: dict, porque: str, msg: dict | None = None) -> None:
        echado = self.tg("banChatMember", chat_id=chat, user_id=de["id"], revoke_messages="true")
        self.expulsados.add((chat, de["id"]))
        g = self.grupos.get(chat)
        self.registrar(f"antispam: {g.clave}, expulsado {de['id']} ({porque})")
        self.avisar(g, de, msg, porque, bool(echado))

    def entrada(self, cambio: dict) -> None:
        """Quien entra en el grupo con el nombre en chino, japonés, coreano o cirílico sale en el momento."""
        chat = cambio["chat"]["id"]
        de = cambio["new_chat_member"].get("user") or {}
        antes, ahora = cambio["old_chat_member"]["status"], cambio["new_chat_member"]["status"]
        if (not self.grupos.get(chat) or de.get("is_bot") or antes not in ("left", "kicked")
                or ahora not in ("member", "restricted")):
            return
        nombre = " ".join(x for x in (de.get("first_name"), de.get("last_name")) if x)
        if len(ESCRITURA.findall(nombre)) < 2:
            return
        if time.time() - self.cargado > RECARGA_S:
            self.cargar()
        if not self.autores.get(chat) or de["id"] in self.autores[chat]:
            return  # ya había escrito en el grupo (o no se sabe): es de la casa
        self.expulsar(chat, de, "ha entrado con el nombre en chino, japonés, coreano o cirílico")

    def avisar(self, g, de: dict, msg: dict | None, porque: str, echado: bool) -> None:
        if not self.juanjo:
            return
        nombre = " ".join(x for x in (de.get("first_name"), de.get("last_name")) if x) or str(de["id"])
        usuario = f" (@{de['username']})" if de.get("username") else ""
        if msg:
            texto = (msg.get("text") or msg.get("caption") or "[sin texto]").strip()
            hecho = "Mensaje borrado y persona expulsada." if echado else "Mensaje borrado; no se ha podido expulsar."
            cita = f"\n\n<blockquote>{html.escape(texto[:600])}</blockquote>"
        else:
            hecho = "Expulsada al entrar, sin haber escrito." if echado else "No se ha podido expulsar."
            cita = ""
        cuerpo = (f"<b>Spam quitado en {html.escape(g.nombre)}</b>\n"
                  f"{html.escape(nombre + usuario)}, id {de['id']}: {html.escape(porque)}.\n{hecho}{cita}")
        boton = {"inline_keyboard": [[{"text": "Deshacer", "callback_data":
                                       f"as:{g.id}:{de['id']}:{self.firma(g.id, de['id'])}"}]]} if echado else None
        self.tg("sendMessage", chat_id=self.juanjo, text=cuerpo, parse_mode="HTML",
                link_preview_options={"is_disabled": True}, **({"reply_markup": boton} if boton else {}))

    def deshacer(self, cq: dict) -> bool:
        """El botón «Deshacer»: vuelve a admitir a la persona. True si el botón era suyo."""
        datos = cq.get("data") or ""
        if not datos.startswith("as:"):
            return False
        try:
            _, chat, uid, firma = datos.split(":")
            chat, uid = int(chat), int(uid)
        except ValueError:
            return True
        m = cq.get("message") or {}
        if cq["from"]["id"] != self.juanjo or not hmac.compare_digest(firma, self.firma(chat, uid)):
            return True
        hecho = self.tg("unbanChatMember", chat_id=chat, user_id=uid, only_if_banned="true")
        self.expulsados.discard((chat, uid))
        self.vistos.pop((chat, uid), None)
        if hecho:
            self.autores.setdefault(chat, set()).add(uid)  # no se le vuelve a tomar por nuevo
        self.registrar(f"antispam: deshecho {chat} {uid} ({'readmitido' if hecho else 'no se pudo'})")
        if m:
            self.tg("editMessageReplyMarkup", chat_id=m["chat"]["id"], message_id=m["message_id"],
                    reply_markup={"inline_keyboard": []})
            self.tg("sendMessage", chat_id=m["chat"]["id"], reply_parameters={"message_id": m["message_id"]},
                    text=("Hecho: puede volver a entrar en el grupo. Los mensajes borrados no vuelven."
                          if hecho else "No se ha podido readmitir: Telegram no lo ha aceptado."))
        return True
