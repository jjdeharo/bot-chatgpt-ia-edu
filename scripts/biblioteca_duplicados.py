# SPDX-License-Identifier: AGPL-3.0-or-later
"""Identifica documentos de la Biblioteca sin depender de la búsqueda semántica."""
import json
import re
from functools import lru_cache
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlencode, urlsplit, urlunsplit

import documento_web

URL = re.compile(r'https?://[^\s<>"»\]]+')
RESUMEN = re.compile(r'^\s*(?:\*\*)?Resumen(?:\*\*)?\s*$', re.M | re.I)
VERSION_ARXIV = re.compile(r"v[1-9]\d*$")


def enlaces(texto: str) -> list[str]:
    return [m.rstrip(".,;)") for m in URL.findall(texto)]


def arxiv(url: str) -> str:
    identificador = documento_web.id_arxiv(url)
    if identificador:
        return identificador
    doi = re.fullmatch(r"https?://(?:dx\.)?doi\.org/10\.48550/arxiv\.(.+)", url, re.I)
    if doi:
        return documento_web.id_arxiv(f"https://arxiv.org/abs/{doi.group(1).lower()}")
    return ""


def enlace_normalizado(url: str) -> str:
    try:
        u = urlsplit(url)
        if u.scheme not in ("http", "https") or not u.hostname or u.username or u.password:
            return ""
        dominio = u.hostname.lower()
        if dominio in ("doi.org", "dx.doi.org"):
            return "doi:" + unquote(u.path.strip("/")).lower()
        if ":" in dominio:
            dominio = f"[{dominio}]"
        if u.port not in (None, 80, 443):
            dominio += f":{u.port}"
        consulta = urlencode([(k, v) for k, v in parse_qsl(u.query, keep_blank_values=True)
                              if not k.lower().startswith("utm_") and k.lower() not in {"fbclid", "gclid"}])
    except ValueError:
        return ""
    return urlunsplit(("https", dominio, u.path.rstrip("/"), consulta, ""))


def claves(urls=(), huella: str = "") -> set[str]:
    ids = set(filter(None, map(arxiv, urls)))
    fijados = {VERSION_ARXIV.sub("", i) for i in ids if VERSION_ARXIV.search(i)}
    resultado = {"arxiv:" + i for i in ids if i not in fijados}
    resultado.update(k for u in urls if not arxiv(u) and (k := enlace_normalizado(u)))
    if huella:
        resultado.add("sha256:" + huella)
    return resultado


def enlaces_ficha(ficha: str) -> list[str]:
    partes = re.split(r"\n\s*\n", ficha.strip(), maxsplit=2)
    urls = enlaces(partes[1]) if len(partes) > 1 else []
    # La referencia puede dar la URL sin versión. La sección Licencia enlaza la ficha de la versión exacta.
    preprints = {VERSION_ARXIV.sub("", i) for u in urls if (i := arxiv(u))}
    if preprints:
        urls += [u for u in enlaces(ficha) if (i := arxiv(u)) and VERSION_ARXIV.search(i)
                 and VERSION_ARXIV.sub("", i) in preprints]
    return urls


@lru_cache(maxsize=2)
def _indice(ruta: Path, tema: int, mtime: int, inodo: int) -> tuple[dict, set]:
    del mtime, inodo  # identifican la instantánea de la exportación en la caché
    indice, ids = {}, set()
    with ruta.open() as f:
        for linea in f:
            m = json.loads(linea)
            if m.get("tema") != tema:
                continue
            ids.add(m["id"])
            texto = m.get("texto", "")
            if RESUMEN.search(texto):
                urls = enlaces_ficha(texto)
            elif not m.get("responde_a"):
                url = (m.get("web") or {}).get("url")
                urls = [url] if url else enlaces(texto)[:1]
            else:
                continue  # un enlace en un comentario no identifica la obra publicada
            for clave in claves(urls):
                indice.setdefault(clave, []).append((m.get("responde_a") or m["id"], m["enlace"]))
    return indice, ids


def ya_publicado(grupo, buscadas: set[str], recientes: dict, omitir: int | None = None) -> str:
    """El historial exportado y lo que acaba de publicar el bot, aun si el índice va por detrás."""
    if not buscadas:
        return ""
    ruta = grupo.datos / "mensajes.jsonl"
    indice, ids, pasada_completa = {}, None, 0.0
    try:
        ficha = ruta.stat()
        indice, ids = _indice(ruta, grupo.biblioteca, ficha.st_mtime_ns, ficha.st_ino)
        pasada_completa = (ruta.parent.parent / "ultimo-completo").stat().st_mtime
    except (OSError, ValueError, KeyError):
        pass
    anteriores = [par for k in buscadas for par in indice.get(k, ()) if par[0] != omitir]
    if anteriores:
        return min(anteriores)[1]
    for id_, publicacion in recientes.items():
        mensaje = int(id_)
        if mensaje == omitir or (ids is not None and mensaje not in ids and pasada_completa > publicacion["momento"]):
            continue
        if buscadas.intersection(publicacion["claves"]):
            return publicacion["enlace"]
    return ""
