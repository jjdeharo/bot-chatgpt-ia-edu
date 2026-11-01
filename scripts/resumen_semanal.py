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

    python resumen_semanal.py vce|exelearning [--ejemplo] [--publicar] [--atras N]

Con --ejemplo lo manda a Juanjo por privado en lugar de al grupo, con la semana que acabó
el último viernes; con --atras N, la de N semanas antes; con --publicar, lo publica en el grupo
a mano. Lo normal es que lo publique el propio bot desde su bucle (Bot.resumen_si_toca).
"""
import html
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

MADRID = ZoneInfo("Europe/Madrid")
DIA, HORA = 4, 18  # viernes a las 18:00, hora de Madrid
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
    "Aplicaciones añadidas esta semana al {repositorio}",
    "Novedades de la semana en el {repositorio}",
    "Aplicaciones que han entrado esta semana en el {repositorio}",
    "Lo nuevo del {repositorio}, por si os sirve en clase",
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
    titulo = entrada.format(repositorio=enlace(catalogo.WEB, "repositorio de Vibe Coding Educativo"))
    lineas = [f"📱 <b>{titulo}</b> ({periodo(desde, hasta)})", ""]
    for a in apps:
        autor = f", de {html.escape(a['autor'], quote=False)}" if a["autor"] else ""
        lineas.append(f"• {enlace(catalogo.enlace_catalogo(a['url']), a['titulo'] or a['url'])}{autor}")
    lineas += ["", f"<i>{CIERRES_VCE[semana % len(CIERRES_VCE)].format(bot=f'https://t.me/{usuario}')}</i>"]
    return "\n".join(lineas)


# --- eXeLearning ------------------------------------------------------------
# Un resumen corto de la semana, no un boletín: como mucho 3 novedades y, hasta completar 6
# elementos, las dudas resueltas más útiles; el mensaje entero, 150 palabras como mucho, lo que cabe
# en una pantalla de móvil (Juanjo, 31-10-2026).
MAX_NOVEDADES, MAX_ELEMENTOS, MAX_PALABRAS = 3, 6, 150

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

Dudas resueltas (como mucho {MAX_ELEMENTOS} menos el número de novedades, las más útiles para otras personas): alguien preguntó o \
contó un problema y otra persona dio una respuesta que lo resuelve o que dice con claridad qué hacer. \
Cuentan también las preguntas de información (si el programa tiene o permite algo, dónde está) \
contestadas con el dato o con un enlace, aunque la respuesta no esté marcada como respuesta al \
mensaje. Para cada una, el mensaje de la duda y el de la respuesta (si la solución se reparte en \
varios, el principal). No incluyas dudas sin resolver.

Nada de spam, ni de mensajes de bots, ni sobre Karla bot (el resumen lo publica ella y ya habla de sí \
misma al final). Entre títulos y detalles, 90 palabras como mucho. \
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


def palabras(texto: str) -> int:
    """Las palabras que se leen: sin etiquetas; una dirección cuenta como una."""
    return len(re.sub(r"<[^>]+>", "", texto).split())


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
    return {"novedades": novedades, "dudas": dudas[:MAX_ELEMENTOS - len(novedades)]}, r.usage


ENTRADAS_EXE = [
    "Resumen de la semana en el grupo",
    "Lo más destacado de la semana en el grupo",
    "Así ha ido la semana en el grupo",
    "Lo más útil de la semana en el grupo",
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
    """El mensaje, con el tope de palabras: si se pasa, fuera lo último de la lista más larga."""
    resumen = {k: list(v) for k, v in resumen.items()}
    while (texto := componer_exelearning(resumen, desde, hasta, usuario)) and palabras(texto) > MAX_PALABRAS:
        resumen["dudas" if len(resumen["dudas"]) >= len(resumen["novedades"]) else "novedades"].pop()
    return texto


def componer_exelearning(resumen: dict, desde: datetime, hasta: datetime, usuario: str) -> str | None:
    if not resumen["novedades"] and not resumen["dudas"]:
        return None
    semana = hasta.astimezone(MADRID).isocalendar().week
    lineas = [f"<b>{ENTRADAS_EXE[semana % len(ENTRADAS_EXE)]}</b> ({periodo(desde, hasta)})"]
    if resumen["novedades"]:
        lineas += ["", "🆕 <b>Novedades</b>"]
        lineas += [f"• {enlace(n['enlace'], n['titulo'])}" + (f": {html.escape(n['detalle'], quote=False)}"
                                                             if n["detalle"] else "")
                   for n in resumen["novedades"]]
    if resumen["dudas"]:
        lineas += ["", "✅ <b>Dudas resueltas</b>"]
        lineas += [f"• {enlace(d['enlace'], d['tema'])}" for d in resumen["dudas"]]
    lineas += ["", f"<i>{CIERRES_EXE[semana % len(CIERRES_EXE)].format(bot=f'https://t.me/{usuario}')}</i>"]
    return "\n".join(lineas)


# --- publicar -----------------------------------------------------------------
VENTANA = timedelta(hours=6)  # si el bot estaba parado el viernes, se publica esa noche; después, ya no


def marca(grupo: str):
    import grupos
    return grupos.TODOS[grupo].datos / "resumen-semanal.json"


def ya_publicado(grupo: str, cierre: datetime) -> bool:
    try:
        return json.loads(marca(grupo).read_text()).get("cierre") == cierre.isoformat()
    except (OSError, ValueError):
        return False


def toca(grupo: str, ahora: datetime | None = None) -> datetime | None:
    """El cierre de esta semana si toca publicarlo ahora: viernes desde las 18:00 y sin publicar."""
    ahora = ahora or datetime.now(timezone.utc)
    cierre = ultimo_cierre(ahora)
    if ahora - cierre > VENTANA or ya_publicado(grupo, cierre):
        return None
    return cierre


def generar(grupo: str, hasta: datetime, usuario: str, cliente=None, modelo: str = "") -> tuple[str | None, object]:
    """El mensaje de la semana que acaba en «hasta» y el uso de Claude (None si no lo ha usado)."""
    import grupos
    desde = hasta - timedelta(days=7)
    if grupo == "vce":
        import catalogo
        return texto_vce(apps_de_la_semana(catalogo.Hoja().filas(), desde, hasta), desde, hasta, usuario), None
    resumen, uso = resumen_de_la_semana(cliente, modelo, mensajes_de_la_semana(
        grupos.TODOS[grupo].datos / "mensajes.jsonl", desde, hasta))
    return texto_exelearning(resumen, desde, hasta, usuario), uso


def publicar(tg, grupo: str, cierre: datetime, texto: str | None) -> bool:
    """En el tema General del grupo (Juanjo, 31-10-2026: donde lo ve todo el mundo). Se apunta la semana
    aunque no haya nada que publicar, para no volver a intentarlo."""
    import grupos
    hecho = True
    if texto:
        hecho = tg("sendMessage", chat_id=grupos.TODOS[grupo].id, text=texto, parse_mode="HTML",
                   link_preview_options={"is_disabled": True}) is not None
    if hecho:
        marca(grupo).write_text(json.dumps({"cierre": cierre.isoformat(), "publicado": bool(texto),
                                            "momento": datetime.now(timezone.utc).isoformat()}))
    return hecho


if __name__ == "__main__":
    grupo, ejemplo, al_grupo = sys.argv[1], "--ejemplo" in sys.argv, "--publicar" in sys.argv
    atras = int(sys.argv[sys.argv.index("--atras") + 1]) if "--atras" in sys.argv else 0  # semanas antes
    hasta = ultimo_cierre() - timedelta(days=7 * atras)
    cliente = modelo = None
    if grupo == "exelearning":
        import saldo
        import consultar
        import karla  # noqa: F401 — pone las credenciales de Karla en bot
        cliente, modelo = saldo.cliente(karla.CLAVE), karla.MODELO
    import bot
    tg = bot.Telegram(json.loads(bot.CRED.read_text())["token"])
    texto, u = generar(grupo, hasta, tg("getMe")["username"], cliente, modelo)
    if u:
        uso = {"entrada": 0, "salida": 0, "usd": 0.0}
        consultar.Consultor.apuntar(uso, u, modelo)
        print(f"Claude: {uso['entrada']} + {uso['salida']} tokens, {uso['usd']:.4f} USD", file=sys.stderr)
    print(texto or "(nada esta semana)")
    if texto and ejemplo:
        tg("sendMessage", chat_id=bot.JUANJO, text=texto, parse_mode="HTML",
           link_preview_options={"is_disabled": True})
    if al_grupo:  # a mano, fuera del viernes (Juanjo, 31-10-2026); queda apuntado para no repetirlo
        print("publicado en el grupo" if publicar(tg, grupo, hasta, texto) else "Telegram no lo ha aceptado")
