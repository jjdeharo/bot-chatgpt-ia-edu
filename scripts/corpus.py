# SPDX-License-Identifier: AGPL-3.0-or-later
"""Convierte los mensajes descargados en textos que se pueden buscar.

Dos colecciones:
- mensajes: cada mensaje con algo que decir, con el arranque del mensaje al
  que responde, porque un «sí, a mí también me pasa» solo se entiende así.
- biblioteca: cada aportación del tema Biblioteca digital (documento, enlace
  o texto) junto con sus fichas y comentarios, que suelen ir en respuesta.
  Solo en los grupos que tienen ese tema.
"""
import json
import re
from grupos import DATOS, Grupo  # noqa: F401 — DATOS lo usan otros módulos

MINIMO = 25          # caracteres: por debajo, «gracias», «👍» y similares no se indexan
CONTEXTO = 220       # caracteres del mensaje al que se responde
LARGO = 1500         # el modelo de significado no lee mucho más


def cargar(g: Grupo) -> dict:
    with (g.datos / "mensajes.jsonl").open() as f:
        return {d["id"]: d for d in map(json.loads, f)}


def temas(g: Grupo) -> dict:
    return {int(k): v for k, v in json.loads((g.datos / "temas.json").read_text()).items()}


def contenido(m: dict) -> str:
    partes = [m["texto"].strip()]
    w = m.get("web") or {}
    for k in ("titulo", "descripcion"):
        if w.get(k) and w[k] not in partes[0]:
            partes.append(w[k])
    if m.get("archivo"):
        partes.append(f"[archivo: {m['archivo']}]")
    return "\n".join(p for p in partes if p)


def textos_mensajes(ms: dict, g: Grupo) -> list[dict]:
    salida = []
    for m in ms.values():
        if g.biblioteca and m["tema"] == g.biblioteca:
            continue
        c = contenido(m)
        if len(c) < MINIMO:
            continue
        previo = ms.get(m["responde_a"]) if m["responde_a"] else None
        texto = f"{m['autor'] or '?'}: {c}"
        if previo:
            texto = f"(en respuesta a {previo['autor'] or '?'}: {contenido(previo)[:CONTEXTO]})\n{texto}"
        salida.append({"id": m["id"], "texto": texto[:LARGO]})
    return salida


def _segundos(m: dict) -> float:
    from datetime import datetime
    return datetime.fromisoformat(m["fecha"]).timestamp()


def obras_biblioteca(ms: dict, g: Grupo) -> list[dict]:
    """Agrupa cada aportación con todo lo que cuelga de ella.

    Muchas aportaciones son una ráfaga del mismo autor: el título en un
    mensaje, la portada en otro y el PDF en un tercero, sin responderse.
    Se juntan si van seguidas (menos de 3 minutos) y no empiezan otra obra.
    Las fichas y comentarios en respuesta van con la obra a la que responden.
    """
    if not g.biblioteca:
        return []
    bib = sorted((m for m in ms.values() if m["tema"] == g.biblioteca), key=lambda x: x["id"])
    grupos, de, actual = {}, {}, None
    for m in bib:  # «obra», no «g»: el 27-10-2026 pisaba el grupo y el índice de ChatGPT-IA-edu dejó de rehacerse
        if m["responde_a"] in de:
            obra = de[m["responde_a"]]
        else:
            tiene_doc = actual and any(x.get("media") == "Document" for x in grupos[actual])
            sigue = (actual and m["autor_id"] == ms[actual]["autor_id"]
                     and _segundos(m) - _segundos(grupos[actual][-1]) <= 180
                     and not (tiene_doc and (m["texto"].strip() or m.get("media") == "Document")))
            if not sigue:
                actual = m["id"]
                grupos[actual] = []
            obra = actual
        grupos[obra].append(m)
        de[m["id"]] = obra
    textos_pdf = g.datos / "pdf-texto"
    obras = []
    for id_, grupo in grupos.items():
        cabeza = ms[id_]
        texto = "\n\n".join(p for p in (contenido(m) for m in grupo) if p)
        doc = next((m for m in grupo if m.get("media") == "Document"), None)
        enlace_web = any(m.get("web") or "http" in m["texto"] for m in grupo)
        if not (doc or enlace_web or len(texto) >= 200):
            continue  # agradecimientos y avisos, no obras
        pdf = textos_pdf / f"{doc['id']}.txt" if doc else None
        extracto = pdf.read_text()[:1500] if pdf and pdf.exists() else ""
        # Lo que publica el bot lleva «Aportado por Nombre (@usuario)»: la obra es de esa persona.
        aportado = next((re.search(r"Aportado por (.+)", m["texto"]) for m in grupo
                         if "Aportado por" in m["texto"]), None)
        obras.append({
            "id": id_,
            "ids": [m["id"] for m in grupo],
            "texto": (texto[:2500] + ("\n\n[primeras páginas del documento]\n" + extracto if extracto else "")),
            "aporte": texto[:900],
            "archivo": doc.get("archivo") if doc else None,
            "id_archivo": doc["id"] if doc else None,
            "autor": aportado.group(1).strip() if aportado else cabeza["autor"],
            "fecha": cabeza["fecha"],
            "enlace": (doc or cabeza)["enlace"],
        })
    return obras
