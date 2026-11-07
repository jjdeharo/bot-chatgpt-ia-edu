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
