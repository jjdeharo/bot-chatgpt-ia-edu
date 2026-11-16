# SPDX-License-Identifier: AGPL-3.0-or-later
"""El aviso de la semana en los grupos, con el vídeo y el pódcast del boletín semanal (ADR 0041).

El boletín semanal (su ADR 0012) deja, cuando tiene listo el aviso de un grupo, una carpeta
datos/boletin/<semana>/ con <grupo>.json y sus archivos:

    {"semana": "2026-47", "grupo": "chatgpt", "tema": 19215, "salida": "2026-11-23T08:00:00+01:00",
     "texto": "<b>Semana 47: del 16 al 22 de noviembre</b>\\n…\\n\\n👉 https://…",
     "video": {"archivo": "chatgpt-video.mp4", "miniatura": "chatgpt-miniatura.jpg", "duracion": 412,
               "ancho": 1280, "alto": 720},
     "audio": {"archivo": "chatgpt-audio.mp3", "duracion": 905, "titulo": "Semana 47 (2026) · ChatGPT-IA-edu",
               "interprete": "@ChatGPTedu"}}

El bot lo publica a la hora de «salida» (las 8:00 del lunes) en el tema del grupo («tema»; sin él, en el
general): el mensaje y, si los trae, el vídeo y el pódcast. Antes lo mandaba el boletín con la cuenta de
Juanjo, que dejaba los mensajes programados en Telegram; un bot no puede programar, así que espera a la hora.
Sin IA: el texto llega hecho.

Si algo falla a medias, se borra lo enviado y se reintenta en la vuelta siguiente, dentro de la VENTANA.
Lo publicado se apunta en <grupo>.publicado.json, y entonces se borran el vídeo y el pódcast, que ya están
en Telegram. Si pasada la ventana no ha salido, <grupo>.fallido.json y un aviso a Juanjo, una vez."""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

VENTANA = timedelta(hours=8)
MAXIMO = 49 * 1024 * 1024   # la API de bots no admite subir archivos de más de 50 MB
CARPETA = Path(__file__).resolve().parent.parent / "datos" / "boletin"


def avisos(carpeta: Path = CARPETA) -> list[Path]:
    """Los avisos entregados por el boletín, sin los ya publicados ni los dados por fallidos."""
    out = []
    for f in sorted(carpeta.glob("*/*.json")):
        if f.name.endswith((".publicado.json", ".fallido.json")):
            continue
        if f.with_suffix(".publicado.json").exists() or f.with_suffix(".fallido.json").exists():
            continue
        out.append(f)
    return out


def salida(f: Path) -> datetime | None:
    try:
        return datetime.fromisoformat(json.loads(f.read_text())["salida"])
    except (OSError, ValueError, KeyError, TypeError):
        return None


def pendientes(ahora: datetime | None = None, carpeta: Path = CARPETA) -> tuple[list[Path], list[Path]]:
    """Los avisos que toca publicar ahora y los que ya han pasado su ventana sin salir."""
    ahora = ahora or datetime.now(timezone.utc)
    toca, pasados = [], []
    for f in avisos(carpeta):
        s = salida(f)
        if s is None:
            continue
        if s <= ahora < s + VENTANA:
            toca.append(f)
        elif ahora >= s + VENTANA:
            pasados.append(f)
    return toca, pasados


def publicar(tg, f: Path, chat_id: int, registrar=print) -> bool:
    """Publica un aviso: el mensaje y, detrás, el vídeo y el pódcast. A medias no deja nada."""
    d = json.loads(f.read_text())
    hilo = {"message_thread_id": d["tema"]} if d.get("tema") else {}
    medios = bool(d.get("video") or d.get("audio"))
    enviados = []

    def borrar():
        for mid in enviados:
            tg("deleteMessage", chat_id=chat_id, message_id=mid)

    def archivo(nombre):
        ruta = f.parent / nombre
        if not ruta.is_file():
            raise FileNotFoundError(ruta)
        if ruta.stat().st_size > MAXIMO:
            registrar(f"boletín {f.parent.name} {f.stem}: {nombre} pasa de 50 MB y no se puede subir; va solo el enlace")
            return None
        return ruta

    try:
        r = tg("sendMessage", chat_id=chat_id, text=d["texto"], parse_mode="HTML",
               link_preview_options={"is_disabled": medios}, **hilo)
        if r is None:
            return False
        enviados.append(r["message_id"])
        v = d.get("video")
        if v and (ruta := archivo(v["archivo"])):
            extra = {}
            mini = f.parent / v.get("miniatura", "")
            if v.get("miniatura") and mini.is_file():
                extra["thumbnail"] = (mini.name, mini.read_bytes(), "image/jpeg")
            r = tg.subir("sendVideo", "video", ruta.name, ruta.read_bytes(), tipo="video/mp4", extra=extra,
                         chat_id=chat_id, duration=v.get("duracion"), width=v.get("ancho"), height=v.get("alto"),
                         supports_streaming="true", **hilo)
            if r is None:
                borrar()
                return False
            enviados.append(r["message_id"])
        a = d.get("audio")
        if a and (ruta := archivo(a["archivo"])):
            r = tg.subir("sendAudio", "audio", ruta.name, ruta.read_bytes(), tipo="audio/mpeg",
                         chat_id=chat_id, duration=a.get("duracion"), title=a.get("titulo"),
                         performer=a.get("interprete"), **hilo)
            if r is None:
                borrar()
                return False
            enviados.append(r["message_id"])
    except Exception:
        borrar()
        raise
    f.with_suffix(".publicado.json").write_text(json.dumps(
        {"mensajes": enviados, "momento": datetime.now(timezone.utc).isoformat()}) + "\n")
    for clave in ("video", "audio"):   # ya están en Telegram: no ocupan sitio en el NAS
        x = d.get(clave) or {}
        for nombre in (x.get("archivo"), x.get("miniatura")):
            if nombre:
                (f.parent / nombre).unlink(missing_ok=True)
    return True


def dar_por_fallido(f: Path) -> None:
    f.with_suffix(".fallido.json").write_text(json.dumps({"momento": datetime.now(timezone.utc).isoformat()}) + "\n")
