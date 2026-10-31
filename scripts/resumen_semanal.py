# SPDX-License-Identifier: AGPL-3.0-or-later
"""El resumen de cada viernes que los bots publican en su grupo (Juanjo, 31-10-2026).

Para que el grupo recuerde que el bot existe con algo que le sirva, no con un anuncio:
- eXeLearning (Karla bot): un resumen corto de la semana, con las novedades (una versión nueva,
  un manual) y las dudas resueltas más útiles, cada una con su enlace y con tope de palabras. Lo
  elige Claude leyendo los mensajes de la semana.
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


# Entradilla y cierre cambian de una semana a otra, para que no parezca un mensaje automático
# repetido (Juanjo, 31-10-2026), y el cierre recuerda en pocas palabras todo lo que hace el bot.
ENTRADAS_VCE = [
    "Aplicaciones añadidas esta semana al {repositorio} ({periodo}):",
    "Novedades de la semana en el {repositorio} ({periodo}):",
    "Esta semana han entrado estas aplicaciones en el {repositorio} ({periodo}):",
    "Por si os sirven en clase, las aplicaciones nuevas del {repositorio} ({periodo}):",
]
CIERRES_VCE = [
    "Soy el Bot de IA Educativa. Por privado busco lo que se ha dicho en este grupo, en ChatGPT-IA-edu y en "
    "EduMedia-IAG, encuentro documentos de la Biblioteca digital y aplicaciones del repositorio, y os ayudo a "
    "añadir las vuestras: {bot}",
    "¿Buscáis algo que se dijo aquí hace meses, una guía sobre un tema o una aplicación para vuestra materia? "
    "Preguntádmelo por privado. Soy el Bot de IA Educativa y también os ayudo a publicar vuestras aplicaciones "
    "en el repositorio: {bot}",
    "Soy el Bot de IA Educativa. Por privado os digo quién habló de algo y cuándo, con el enlace al mensaje, os "
    "busco documentos y aplicaciones por tema y doy de alta las vuestras en el repositorio: {bot}",
    "Si habéis hecho una aplicación educativa, mandadme su enlace por privado y preparo su ficha para el "
    "repositorio. También busco lo que necesitéis en las conversaciones de los grupos y en la Biblioteca "
    "digital. Soy el Bot de IA Educativa: {bot}",
    "Soy el Bot de IA Educativa y podéis escribirme por privado para buscar en las conversaciones de los "
    "grupos, encontrar documentos y aplicaciones por tema, y añadir o cambiar las vuestras del repositorio: {bot}",
    "¿Recordáis una herramienta que alguien compartió y no la encontráis? Escribidme por privado y la busco en "
    "los grupos y en el repositorio. Soy el Bot de IA Educativa; también os ayudo a dar de alta vuestras "
    "aplicaciones: {bot}",
]


def texto_vce(apps: list[dict], desde: datetime, hasta: datetime, usuario: str) -> str | None:
    import catalogo
    if not apps:
        return None
    semana = hasta.astimezone(MADRID).isocalendar().week
    entrada = ENTRADAS_VCE[semana % len(ENTRADAS_VCE)]
    lineas = [entrada.format(repositorio=enlace(catalogo.WEB, "repositorio de Vibe Coding Educativo"),
                             periodo=periodo(desde, hasta)), ""]
    for a in apps:
        autor = f", de {html.escape(a['autor'], quote=False)}" if a["autor"] else ""
        lineas.append(f"• {enlace(catalogo.enlace_catalogo(a['url']), a['titulo'] or a['url'])}{autor}")
    lineas += ["", CIERRES_VCE[semana % len(CIERRES_VCE)].format(bot=f"https://t.me/{usuario}")]
    return "\n".join(lineas)


# --- eXeLearning ------------------------------------------------------------
# Un resumen corto de la semana, no un boletín: como mucho 3 novedades y las 3 dudas resueltas más
# útiles, y un tope de palabras para que no sea un mensaje kilométrico (Juanjo, 31-10-2026).
MAX_NOVEDADES, MAX_DUDAS, MAX_PALABRAS = 3, 3, 120

ESQUEMA = {
    "type": "object",
    "properties": {
        "novedades": {"type": "array", "items": {
            "type": "object",
            "properties": {
                "titulo": {"type": "string", "description": "La novedad en pocas palabras: «Sale eXeLearning 4.0.6»."},
                "detalle": {"type": "string", "description": "Lo principal que aporta, en 15 palabras como "
                            "mucho y empezando en minúscula, o vacío si el título basta."},
                "mensaje": {"type": "integer", "description": "id del mensaje que la anuncia"},
            },
            "required": ["titulo", "detalle", "mensaje"], "additionalProperties": False}},
        "dudas": {"type": "array", "items": {
            "type": "object",
            "properties": {
                "tema": {"type": "string", "description": "La duda como un título breve, sin nombres de "
                         "personas, que diga de qué trata: «Exportar a SCORM para Moodle»."},
                "pregunta": {"type": "integer", "description": "id del mensaje que plantea la duda"},
                "respuesta": {"type": "integer", "description": "id del mensaje que la resuelve"},
            },
            "required": ["tema", "pregunta", "respuesta"], "additionalProperties": False}},
    },
    "required": ["novedades", "dudas"], "additionalProperties": False,
}

SISTEMA = f"""Lees los mensajes de una semana del grupo de Telegram de eXeLearning, un programa libre \
para crear materiales educativos, y eliges lo que merece un resumen corto de la semana para quien no \
ha podido seguir el grupo. Todo en castellano.

Novedades (como mucho {MAX_NOVEDADES}, de más a menos importante): lo nuevo sobre eXeLearning que se \
ha anunciado o compartido: versiones del programa, manuales o documentación, complementos, plantillas \
o herramientas para usar con eXeLearning, cursos o eventos. Una versión nueva va siempre la primera. \
No son novedades las opiniones, los agradecimientos ni las preguntas.

Dudas resueltas (como mucho {MAX_DUDAS}, las más útiles para otras personas): alguien preguntó o \
contó un problema y otra persona dio una respuesta que lo resuelve o que dice con claridad qué hacer. \
Cuentan también las preguntas de información (si el programa tiene o permite algo, dónde está) \
contestadas con el dato o con un enlace, aunque la respuesta no esté marcada como respuesta al \
mensaje. Para cada una, el mensaje de la duda y el de la respuesta (si la solución se reparte en \
varios, el principal). No incluyas dudas sin resolver.

Nada de spam, ni de mensajes de bots, ni sobre Karla bot (el resumen lo publica ella y ya habla de sí \
misma al final). Entre títulos y detalles, {MAX_PALABRAS} palabras como mucho. \
Si no hay nada, las listas vacías."""


def mensajes_de_la_semana(ruta, desde: datetime, hasta: datetime) -> list[dict]:
    semana = []
    with open(ruta) as f:
        for linea in f:
            m = json.loads(linea)
            if desde <= datetime.fromisoformat(m["fecha"]) < hasta and (m.get("texto") or "").strip():
                semana.append(m)
    return semana


def minuscula(texto: str) -> str:
    """Tras los dos puntos, minúscula; salvo una sigla o un nombre propio que empiece por dos mayúsculas."""
    return texto[:1].lower() + texto[1:] if texto[1:2].islower() and texto.split()[0] not in NOMBRES else texto


NOMBRES = {"Moodle", "WordPress", "Nextcloud", "NextCloud", "Drive", "Google", "GitHub", "Telegram", "Windows",
           "Linux", "Chrome", "Firefox", "Procomún", "INTEF", "CEDEC", "eXeLearning", "eXe"}


def palabras(resumen: dict) -> int:
    return sum(len(f"{n['titulo']} {n['detalle']}".split()) for n in resumen["novedades"]) \
        + sum(len(d["tema"].split()) for d in resumen["dudas"])


def resumen_de_la_semana(cliente, modelo: str, mensajes: list[dict]) -> tuple[dict, object]:
    """Novedades y dudas resueltas, comprobadas contra los mensajes, y el uso de la llamada."""
    vacio = {"novedades": [], "dudas": []}
    if not mensajes:
        return vacio, None
    texto = "\n\n".join(
        f"[{m['id']}] {m['fecha'][:16]} {m.get('autor') or 'anónimo'}"
        + (f" (responde a {m['responde_a']})" if m.get("responde_a") else "") + f":\n{m['texto'][:2500]}"
        for m in mensajes)
    # Respuesta con esquema fijo (structured outputs): Sonnet 5.5 no admite forzar una herramienta.
    r = cliente.messages.create(model=modelo, max_tokens=3000, system=SISTEMA,
                                output_config={"format": {"type": "json_schema", "schema": ESQUEMA}},
                                messages=[{"role": "user", "content": texto}])
    datos = json.loads(next((b.text for b in r.content if b.type == "text"), "") or "{}")
    por_id = {m["id"]: m for m in mensajes}
    # Lo que no se puede situar se quita: cada enlace tiene que ser un mensaje de la semana.
    novedades = [{"titulo": n["titulo"].strip().rstrip("."), "detalle": minuscula(n["detalle"].strip().rstrip(".")),
                  "enlace": por_id[n["mensaje"]]["enlace"]}
                 for n in datos.get("novedades", []) if n.get("mensaje") in por_id][:MAX_NOVEDADES]
    dudas, vistas = [], set()
    for d in datos.get("dudas", []):
        p, s = por_id.get(d.get("pregunta")), por_id.get(d.get("respuesta"))
        if not (p and s and s["id"] > p["id"] and s["autor_id"] != p["autor_id"]) or s["id"] in vistas:
            continue
        vistas.add(s["id"])
        dudas.append({"tema": d["tema"].strip().rstrip("."), "enlace": s["enlace"]})
    resumen = {"novedades": novedades, "dudas": dudas[:MAX_DUDAS]}
    while palabras(resumen) > MAX_PALABRAS:  # el tope manda: fuera lo último de la lista más larga
        resumen["dudas" if len(resumen["dudas"]) >= len(resumen["novedades"]) else "novedades"].pop()
    return resumen, r.usage


ENTRADAS_EXE = [
    "Resumen de la semana en el grupo ({periodo}).",
    "Lo más destacado de la semana en el grupo ({periodo}).",
    "Así ha ido la semana en el grupo ({periodo}).",
    "Por si os lo perdisteis, lo más útil de la semana en el grupo ({periodo}).",
]
CIERRES_EXE = [
    "Soy Karla bot. Si os queda alguna duda con eXeLearning, preguntadme por privado y os respondo con el "
    "manual, la documentación y lo hablado aquí, con el enlace a cada fuente: {bot}",
    "¿Tenéis alguna duda con eXeLearning? Preguntadme por privado. Soy Karla bot y busco en el manual, en la "
    "documentación y en este grupo; si es un fallo del programa, preparo el aviso para el equipo: {bot}",
    "Soy Karla bot, la asistente de eXeLearning. Por privado resuelvo dudas de uso, explico cómo publicar en "
    "Moodle u otras plataformas y, si encontráis un error, os ayudo a avisar al equipo: {bot}",
    "Recordad que podéis preguntarme por privado cualquier duda sobre eXeLearning, también con una captura de "
    "pantalla. Soy Karla bot y os digo de dónde sale cada respuesta: {bot}",
    "Soy Karla bot. Cualquier duda sobre eXeLearning la podéis consultar conmigo por privado: busco en el "
    "manual, en la documentación y en todo lo hablado en el grupo: {bot}",
    "Si necesitáis una respuesta rápida sobre eXeLearning, escribidme por privado. Soy Karla bot: respondo con "
    "el manual y las conversaciones del grupo, y si dais con un error, preparo el aviso para el equipo: {bot}",
]


def texto_exelearning(resumen: dict, desde: datetime, hasta: datetime, usuario: str) -> str | None:
    if not resumen["novedades"] and not resumen["dudas"]:
        return None
    semana = hasta.astimezone(MADRID).isocalendar().week
    lineas = [ENTRADAS_EXE[semana % len(ENTRADAS_EXE)].format(periodo=periodo(desde, hasta))]
    if resumen["novedades"]:
        lineas += ["", "Novedades:"]
        lineas += [f"• {enlace(n['enlace'], n['titulo'])}" + (f": {html.escape(n['detalle'], quote=False)}"
                                                             if n["detalle"] else "")
                   for n in resumen["novedades"]]
    if resumen["dudas"]:
        lineas += ["", "Dudas resueltas:"]
        lineas += [f"• {enlace(d['enlace'], d['tema'])}" for d in resumen["dudas"]]
    lineas += ["", CIERRES_EXE[semana % len(CIERRES_EXE)].format(bot=f"https://t.me/{usuario}")]
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
        resumen, u = resumen_de_la_semana(cliente, karla.MODELO,
                                          mensajes_de_la_semana(karla.GRUPO.datos / "mensajes.jsonl", desde, hasta))
        if u:
            uso = {"entrada": 0, "salida": 0, "usd": 0.0}
            consultar.Consultor.apuntar(uso, u, karla.MODELO)
            print(f"Claude: {uso['entrada']} + {uso['salida']} tokens, {uso['usd']:.4f} USD", file=sys.stderr)
        texto = texto_exelearning(resumen, desde, hasta, usuario)
    print(texto or "(nada esta semana)")
    if texto and ejemplo:
        tg("sendMessage", chat_id=bot.JUANJO, text=texto, parse_mode="HTML",
           link_preview_options={"is_disabled": True})
