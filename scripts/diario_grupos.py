# SPDX-License-Identifier: AGPL-3.0-or-later
"""Aviso diario de «Tiza y Algoritmo» en los grupos (ADR 0025).

El diario deja cada noche en datos/diario/<fecha>.json los avisos del día, ya redactados y
repasados, uno por grupo: {"fecha": "AAAA-MM-DD", "avisos": {"chatgpt": "…", "vce": "…",
"edumedia": "…"}}. El bot los publica a las 7:00 de Madrid en el tema General de cada grupo,
con la vista previa del enlace (la portada del diario). Sin IA: el texto llega hecho.

Lo publicado se apunta grupo a grupo en datos/diario/<fecha>.publicado.json, para no repetir
un grupo si otro falló. Si el bot estaba parado, publica dentro de la VENTANA; después, ese día
se queda sin aviso (mejor nada que un «buenos días» a media tarde)."""
import json
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

MADRID = ZoneInfo("Europe/Madrid")
HORA = time(7, 0)
VENTANA = timedelta(hours=5)
CARPETA = Path(__file__).resolve().parent.parent / "datos" / "diario"


def hoy_local(ahora: datetime | None = None) -> tuple[date, datetime]:
    local = (ahora or datetime.now(timezone.utc)).astimezone(MADRID)
    return local.date(), local


def avisos(dia: date, carpeta: Path = CARPETA) -> dict[str, str]:
    try:
        datos = json.loads((carpeta / f"{dia.isoformat()}.json").read_text())
    except (OSError, ValueError):
        return {}
    if datos.get("fecha") != dia.isoformat():
        return {}
    return {g: t for g, t in (datos.get("avisos") or {}).items() if isinstance(t, str) and t.strip()}


def publicados(dia: date, carpeta: Path = CARPETA) -> set[str]:
    try:
        return set(json.loads((carpeta / f"{dia.isoformat()}.publicado.json").read_text()).get("grupos", []))
    except (OSError, ValueError):
        return set()


def pendientes(ahora: datetime | None = None, activos=None, carpeta: Path = CARPETA) -> tuple[date, dict[str, str]]:
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


def publicar(tg, dia: date, lista: dict[str, str], carpeta: Path = CARPETA) -> list[str]:
    """Publica cada aviso en el tema General de su grupo y devuelve los grupos donde ha salido."""
    import grupos
    hechos = []
    for clave, texto in lista.items():
        g = grupos.TODOS.get(clave)
        if not g:
            continue
        if tg("sendMessage", chat_id=g.id, text=texto) is not None:
            apuntar(dia, clave, carpeta)
            hechos.append(clave)
    return hechos
