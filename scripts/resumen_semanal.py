# SPDX-License-Identifier: AGPL-3.0-or-later
"""El resumen de cada viernes que los bots publican en su grupo (Juanjo, 31-10-2026).

Para que el grupo recuerde que el bot existe con algo que le sirva, no con un anuncio:
- eXeLearning (Karla bot): las dudas resueltas en el grupo esa semana, con el enlace a la
  respuesta. Las elige Claude leyendo los mensajes de la semana.
- Vibe Coding Educativo (Bot de IA Educativa): las aplicaciones añadidas esa semana al
  repositorio, por la «Marca temporal» de la hoja, que es la fecha de alta y no cambia al
  modificar un recurso (api.gs).
Si en la semana no hay nada, no se publica nada.

Las horas se calculan en UTC y se pasan a la de Madrid solo para decidir el viernes y
para escribir las fechas.

    python resumen_semanal.py vce|exelearning [--ejemplo]

Con --ejemplo lo manda a Juanjo por privado en lugar de al grupo, con la semana que acabó
el último viernes.
"""
import html
import json
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

MADRID = ZoneInfo("Europe/Madrid")
DIA, HORA = 4, 18  # viernes a las 18:00, hora de Madrid
MAX_DUDAS = 10
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
         "octubre", "noviembre", "diciembre"]


def ultimo_cierre(ahora: datetime | None = None) -> datetime:
    """El último viernes a las 18:00 de Madrid que ya ha pasado, en UTC."""
    local = (ahora or datetime.now(timezone.utc)).astimezone(MADRID)
    dia = local.date() - timedelta(days=(local.weekday() - DIA) % 7)
    cierre = datetime(dia.year, dia.month, dia.day, HORA, tzinfo=MADRID)
    if cierre > local:
        cierre -= timedelta(days=7)
    return cierre.astimezone(timezone.utc)


def periodo(desde: datetime, hasta: datetime) -> str:
    """«del 23 al 30 de octubre», o «del 30 de octubre al 6 de noviembre»."""
    a, b = desde.astimezone(MADRID), hasta.astimezone(MADRID)
    if a.month == b.month:
        return f"del {a.day} al {b.day} de {MESES[b.month - 1]}"
    return f"del {a.day} de {MESES[a.month - 1]} al {b.day} de {MESES[b.month - 1]}"


def enlace(url: str, texto: str) -> str:
    return f'<a href="{html.escape(url)}">{html.escape(texto, quote=False)}</a>'


# --- Vibe Coding Educativo -------------------------------------------------
def apps_de_la_semana(filas: list[dict], desde: datetime, hasta: datetime) -> list[dict]:
    import catalogo
    nuevas = []
    for f in filas:
        try:
            alta = datetime.fromisoformat(f.get("Marca temporal", "").replace("Z", "+00:00"))
        except ValueError:
            continue
        url = f.get(catalogo.COLUMNAS["url"], "").strip()
        if desde <= alta < hasta and url:
            nuevas.append({"alta": alta, "url": url, "titulo": f.get(catalogo.COLUMNAS["titulo"], "").strip(),
                           "autor": f.get(catalogo.COLUMNAS["autor"], "").strip()})
    return sorted(nuevas, key=lambda x: x["alta"])


def texto_vce(apps: list[dict], desde: datetime, hasta: datetime, usuario: str) -> str | None:
    import catalogo
    if not apps:
        return None
    lineas = [f"Aplicaciones añadidas esta semana al {enlace(catalogo.WEB, 'repositorio de Vibe Coding Educativo')} "
              f"({periodo(desde, hasta)}):", ""]
    for a in apps:
        autor = f", de {html.escape(a['autor'], quote=False)}" if a["autor"] else ""
        lineas.append(f"• {enlace(catalogo.enlace_catalogo(a['url']), a['titulo'] or a['url'])}{autor}")
    lineas += ["", "Soy el Bot de IA Educativa. Si habéis hecho una aplicación educativa, os ayudo a añadirla "
               f"al repositorio por privado: https://t.me/{usuario}?start=repositorio"]
    return "\n".join(lineas)


# --- eXeLearning ------------------------------------------------------------
DUDAS = {
    "name": "dudas_resueltas",
    "description": "Las dudas sobre eXeLearning que se resolvieron en el grupo esa semana.",
    "input_schema": {
        "type": "object",
        "properties": {"dudas": {"type": "array", "items": {
            "type": "object",
            "properties": {
                "tema": {"type": "string", "description": "La duda como un título breve en castellano, sin "
                         "nombres de personas, que diga de qué trata: «Exportar a SCORM para Moodle»."},
                "pregunta": {"type": "integer", "description": "id del mensaje que plantea la duda"},
                "respuesta": {"type": "integer", "description": "id del mensaje que la resuelve"},
            },
            "required": ["tema", "pregunta", "respuesta"]}}},
        "required": ["dudas"]},
}

SISTEMA = f"""Lees los mensajes de una semana del grupo de Telegram de eXeLearning, un programa libre \
para crear materiales educativos, y eliges las dudas sobre el programa que quedaron resueltas en el \
grupo: alguien preguntó o contó un problema y otra persona dio una respuesta que lo resuelve o que \
dice con claridad qué hacer. Para cada una, el mensaje de la duda y el de la respuesta que la \
resuelve (si la solución se reparte en varios, el principal).

No incluyas: dudas sin respuesta o con respuestas que no la resuelven, avisos, novedades, \
opiniones, saludos, agradecimientos, spam ni mensajes de bots. Si dos hilos tratan de lo mismo, \
uno solo. Como mucho {MAX_DUDAS}, las más útiles para otras personas. Si no hay ninguna, la lista \
vacía. Responde solo con la herramienta dudas_resueltas."""


def mensajes_de_la_semana(ruta, desde: datetime, hasta: datetime) -> list[dict]:
    semana = []
    with open(ruta) as f:
        for linea in f:
            m = json.loads(linea)
            if desde <= datetime.fromisoformat(m["fecha"]) < hasta and (m.get("texto") or "").strip():
                semana.append(m)
    return semana


def dudas_de_la_semana(cliente, modelo: str, mensajes: list[dict]) -> tuple[list[dict], object]:
    """Las dudas resueltas, comprobadas contra los mensajes, y el uso de la llamada."""
    if not mensajes:
        return [], None
    texto = "\n\n".join(
        f"[{m['id']}] {m['fecha'][:16]} {m.get('autor') or 'anónimo'}"
        + (f" (responde a {m['responde_a']})" if m.get("responde_a") else "") + f":\n{m['texto'][:2500]}"
        for m in mensajes)
    r = cliente.messages.create(model=modelo, max_tokens=3000, system=SISTEMA, tools=[DUDAS],
                                tool_choice={"type": "tool", "name": "dudas_resueltas"},
                                messages=[{"role": "user", "content": texto}])
    datos = next((b.input for b in r.content if b.type == "tool_use"), {}) or {}
    por_id = {m["id"]: m for m in mensajes}
    dudas, vistas = [], set()
    for d in datos.get("dudas", []):
        p, s = por_id.get(d.get("pregunta")), por_id.get(d.get("respuesta"))
        # Lo que no se puede situar se quita: la respuesta tiene que existir y ser posterior.
        if not (p and s and s["id"] > p["id"] and s["autor_id"] != p["autor_id"]) or s["id"] in vistas:
            continue
        vistas.add(s["id"])
        dudas.append({"tema": d["tema"].strip().rstrip("."), "enlace": s["enlace"]})
    return dudas[:MAX_DUDAS], r.usage


def texto_exelearning(dudas: list[dict], desde: datetime, hasta: datetime, usuario: str) -> str | None:
    if not dudas:
        return None
    lineas = [f"Dudas resueltas esta semana en el grupo ({periodo(desde, hasta)}):", ""]
    lineas += [f"• {enlace(d['enlace'], d['tema'])}" for d in dudas]
    lineas += ["", "Soy Karla bot. Si os queda alguna duda con eXeLearning, preguntadme por privado y os respondo "
               f"con el manual y lo hablado aquí: https://t.me/{usuario}"]
    return "\n".join(lineas)


if __name__ == "__main__":
    grupo, ejemplo = sys.argv[1], "--ejemplo" in sys.argv
    hasta = ultimo_cierre()
    desde = hasta - timedelta(days=7)
    if grupo == "exelearning":
        import anthropic
        import consultar
        import karla  # noqa: F401 — pone las credenciales de Karla en bot
    import bot
    tg = bot.Telegram(json.loads(bot.CRED.read_text())["token"])
    usuario = tg("getMe")["username"]
    if grupo == "vce":
        import catalogo
        texto = texto_vce(apps_de_la_semana(catalogo.Hoja().filas(), desde, hasta), desde, hasta, usuario)
    else:
        cliente = anthropic.Anthropic(api_key=karla.CLAVE.read_text().strip())
        dudas, u = dudas_de_la_semana(cliente, karla.MODELO,
                                      mensajes_de_la_semana(karla.GRUPO.datos / "mensajes.jsonl", desde, hasta))
        if u:
            uso = {"entrada": 0, "salida": 0, "usd": 0.0}
            consultar.Consultor.apuntar(uso, u, karla.MODELO)
            print(f"Claude: {uso['entrada']} + {uso['salida']} tokens, {uso['usd']:.4f} USD", file=sys.stderr)
        texto = texto_exelearning(dudas, desde, hasta, usuario)
    print(texto or "(nada esta semana)")
    if texto and ejemplo:
        tg("sendMessage", chat_id=bot.JUANJO, text=texto, parse_mode="HTML",
           link_preview_options={"is_disabled": True})
