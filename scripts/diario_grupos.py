# SPDX-License-Identifier: AGPL-3.0-or-later
"""Aviso diario de «Tiza y Algoritmo» en los grupos (ADR 0025).

El diario deja cada noche en datos/diario/<fecha>.json los avisos del día, ya redactados y
repasados, uno por grupo. El bot los publica a las 7:00 de Madrid en el tema General de cada grupo,
con la vista previa del enlace (la portada del diario). Sin IA: el texto llega hecho.

Desde el 04-11-2026 (ADR 0029) cada aviso trae su saludo y dos o tres puntos, y el archivo, la
cabecera del número: {"fecha", "titulo", "fecha_texto", "url", "avisos": {"chatgpt": {"saludo":
"…", "puntos": ["…"], "url": "…"}, …}}. Desde el 07-11-2026 cada aviso puede traer su propio
enlace (la página de entrada de su grupo, con su imagen); si no, vale el de la cabecera. El bot monta el mensaje: el número en negrita, la fecha, el saludo,
los puntos con su marca y el enlace, con la imagen del número grande y encima del texto. Un aviso
que sea solo texto (el formato anterior) se publica tal cual.

Lo publicado se apunta grupo a grupo en datos/diario/<fecha>.publicado.json, para no repetir
un grupo si otro falló. Si el bot estaba parado, publica dentro de la VENTANA; después, ese día
se queda sin aviso (mejor nada que un «buenos días» a media tarde)."""
import html
import json
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

MADRID = ZoneInfo("Europe/Madrid")
HORA = time(7, 0)
VENTANA = timedelta(hours=5)
CARPETA = Path(__file__).resolve().parent.parent / "datos" / "diario"
PORTADA = "https://diarioiaeducativa.github.io/"   # si el archivo no trae la cabecera del número


def hoy_local(ahora: datetime | None = None) -> tuple[date, datetime]:
    local = (ahora or datetime.now(timezone.utc)).astimezone(MADRID)
    return local.date(), local


def mensaje(datos: dict, aviso) -> dict | None:
    """Los parámetros de sendMessage para un aviso, o None si no hay nada que publicar."""
    if isinstance(aviso, str):   # el formato anterior: texto hecho, con su enlace al final
        return {"text": aviso} if aviso.strip() else None
    if not isinstance(aviso, dict):
        return None
    puntos = [p.strip() for p in aviso.get("puntos") or [] if isinstance(p, str) and p.strip()]
    saludo = (aviso.get("saludo") or "").strip()
    url = (aviso.get("url") or datos.get("url") or "").strip() or PORTADA   # el de su grupo, si lo trae
    if not puntos:
        return None
    e = lambda t: html.escape(t, quote=False)  # noqa: E731
    lineas = []
    if datos.get("titulo"):
        lineas.append(f"<b>{e(datos['titulo'])}</b>")
    if datos.get("fecha_texto"):
        lineas.append(e(datos["fecha_texto"]))
    if saludo:
        lineas += ["", e(saludo)]
    lineas += [""] + [f"• {e(p)}" for p in puntos] + ["", f"👉 {e(url)}"]
    return {"text": "\n".join(lineas).strip(), "parse_mode": "HTML",
            "link_preview_options": {"url": url, "prefer_large_media": True, "show_above_text": True}}


def avisos(dia: date, carpeta: Path = CARPETA) -> dict[str, dict]:
    """Los avisos del día, ya montados: grupo → parámetros de sendMessage."""
    try:
        datos = json.loads((carpeta / f"{dia.isoformat()}.json").read_text())
    except (OSError, ValueError):
        return {}
    if datos.get("fecha") != dia.isoformat():
        return {}
    montados = {g: mensaje(datos, a) for g, a in (datos.get("avisos") or {}).items()}
    return {g: m for g, m in montados.items() if m}


def publicados(dia: date, carpeta: Path = CARPETA) -> set[str]:
    try:
        return set(json.loads((carpeta / f"{dia.isoformat()}.publicado.json").read_text()).get("grupos", []))
    except (OSError, ValueError):
        return set()


def pendientes(ahora: datetime | None = None, activos=None, carpeta: Path = CARPETA) -> tuple[date, dict[str, dict]]:
    """El día y los avisos que toca publicar ahora (vacío si no toca)."""
    dia, local = hoy_local(ahora)
    salida = datetime.combine(dia, HORA, tzinfo=MADRID)
    if not (salida <= local < salida + VENTANA):
        return dia, {}
    hechos = publicados(dia, carpeta)
    lista = {g: t for g, t in avisos(dia, carpeta).items() if g not in hechos and (activos is None or g in activos)}
    return dia, lista


def apuntar(dia: date, grupo: str, carpeta: Path = CARPETA) -> None:
    hechos = publicados(dia, carpeta) | {grupo}
    carpeta.mkdir(parents=True, exist_ok=True)
    (carpeta / f"{dia.isoformat()}.publicado.json").write_text(json.dumps(
        {"grupos": sorted(hechos), "momento": datetime.now(timezone.utc).isoformat()}))


def publicar(tg, dia: date, lista: dict[str, dict], carpeta: Path = CARPETA) -> list[str]:
    """Publica cada aviso en el tema General de su grupo y devuelve los grupos donde ha salido."""
    import grupos
    hechos = []
    for clave, partes in lista.items():
        g = grupos.TODOS.get(clave)
        if not g:
            continue
        if tg("sendMessage", chat_id=g.id, **partes) is not None:
            apuntar(dia, clave, carpeta)
            hechos.append(clave)
    return hechos


# --- Aviso privado a quien sale en el número (ADR 0036 del bot; ADR 0052 del diario) -------------------
# El diario añade al archivo del día una lista «personas»: el id de Telegram de quien ha aportado algo que sale
# en el número y las piezas que lo cuentan, con su titular y su enlace en cada idioma. El bot le escribe por
# privado, en su idioma si lo sabe, un solo mensaje con todas sus piezas y un botón para no recibirlos más.
# Telegram solo deja escribir a quien ya ha hablado con el bot: si no se puede, se apunta y no se insiste.
SIN_AVISOS = CARPETA.parent / "diario-sin-avisos.json"
BOTON_NO = "dno"


def sin_avisos() -> set[int]:
    try:
        return {int(x) for x in json.loads(SIN_AVISOS.read_text())}
    except (OSError, ValueError, TypeError):
        return set()


def no_avisar_mas(uid: int) -> None:
    ids = sorted(sin_avisos() | {uid})
    tmp = SIN_AVISOS.with_suffix(".tmp")
    tmp.write_text(json.dumps(ids))
    tmp.replace(SIN_AVISOS)


def personas_hechas(dia: date, carpeta: Path = CARPETA) -> set[int]:
    try:
        return {int(x) for x in json.loads((carpeta / f"{dia.isoformat()}.privados.json").read_text())}
    except (OSError, ValueError, TypeError):
        return set()


def apuntar_persona(dia: date, uid: int, carpeta: Path = CARPETA) -> None:
    hechas = sorted(personas_hechas(dia, carpeta) | {uid})
    (carpeta / f"{dia.isoformat()}.privados.json").write_text(json.dumps(hechas))


def personas_pendientes(ahora: datetime | None = None, carpeta: Path = CARPETA) -> tuple[date, list[dict]]:
    """Las personas a las que toca escribir ahora: dentro de la ventana, sin las ya hechas ni las que no quieren."""
    dia, local = hoy_local(ahora)
    salida = datetime.combine(dia, HORA, tzinfo=MADRID)
    if not (salida <= local < salida + VENTANA):
        return dia, []
    try:
        datos = json.loads((carpeta / f"{dia.isoformat()}.json").read_text())
    except (OSError, ValueError):
        return dia, []
    if datos.get("fecha") != dia.isoformat():
        return dia, []
    fuera = personas_hechas(dia, carpeta) | sin_avisos()
    lista = [p for p in datos.get("personas") or [] if isinstance(p, dict) and isinstance(p.get("id"), int)
             and p["id"] not in fuera and p.get("piezas")]
    return dia, lista


def mensaje_persona(persona: dict, lengua: str, cabecera: str, boton: str) -> dict | None:
    """Los parámetros de sendMessage: la frase, y cada pieza con su titular y su enlace en ese idioma."""
    e = lambda t: html.escape(t, quote=False)  # noqa: E731
    bloques = []
    for pieza in persona.get("piezas") or []:
        v = pieza.get(lengua) or pieza.get("es") or {}
        if v.get("url"):
            bloques.append(f"«{e(v.get('titular', '').strip())}»\n{e(v['url'])}")
    if not bloques:
        return None
    primera = (persona["piezas"][0].get(lengua) or persona["piezas"][0].get("es"))["url"]
    return {"text": e(cabecera) + "\n\n" + "\n\n".join(bloques), "parse_mode": "HTML",
            "link_preview_options": {"url": primera, "prefer_large_media": True},
            "reply_markup": {"inline_keyboard": [[{"text": boton, "callback_data": BOTON_NO}]]}}


def avisar_personas(tg, dia: date, lista: list[dict], lengua_de, texto, carpeta: Path = CARPETA) -> tuple[int, int]:
    """Escribe a cada persona y la apunta, haya salido o no (no se insiste). Devuelve (enviados, fallidos)."""
    bien = mal = 0
    for p in lista:
        lengua = lengua_de(p["id"])
        partes = mensaje_persona(p, lengua, texto(lengua, "diario_tuyo"), texto(lengua, "diario_no_mas"))
        apuntar_persona(dia, p["id"], carpeta)
        if partes and tg("sendMessage", chat_id=p["id"], **partes) is not None:
            bien += 1
        else:
            mal += 1
    return bien, mal
