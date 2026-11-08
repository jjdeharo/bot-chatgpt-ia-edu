# SPDX-License-Identifier: AGPL-3.0-or-later
"""Saca el texto de las primeras páginas de los PDF de la Biblioteca digital.

Muchos documentos se compartieron solo con el nombre del archivo; sin su
texto no se pueden encontrar por el tema que tratan. Se guarda solo el
texto (datos/<grupo>/pdf-texto/<id>.txt) y el PDF se borra después: el
documento sigue en el grupo y el bot enlaza allí. Solo en los grupos con
biblioteca.

De los documentos desde COMPLETO_DESDE se guarda además el texto entero
(datos/<grupo>/pdf-completo/<id>.txt): con él escribe el Diario de IA Educativa
el artículo de cada documento de la Biblioteca cuando su web oficial no se
encuentra o no deja leer (ADR 0006 del diario, ADR 0026 de este bot).
"""
import asyncio
import subprocess
import tempfile
from pathlib import Path

import corpus
import exportar
import grupos

PAGINAS = 4
MAXIMO = 60 * 1024 * 1024  # bytes: lo que pase de aquí no se descarga
COMPLETO_DESDE = "2026-10-01"   # texto entero solo de lo nuevo: no se descarga otra vez toda la biblioteca
COMPLETO_MAX = 400_000          # caracteres del texto entero (un libro de unas 250 páginas)
# Lo anterior a COMPLETO_DESDE se recupera poco a poco, los más recientes primero: el diario escribe
# con ellos sus piezas de reserva «Del fondo de la biblioteca» (su ADR 0021). Dos por pasada de 15
# minutos, para no descargar toda la biblioteca de golpe (ADR 0026).
ATRASADOS_POR_PASADA = 2


def limpiar(t: str) -> str:
    lineas = [" ".join(l.split()) for l in t.splitlines()]
    return "\n".join(l for l in lineas if len(l) > 2)[:4000]


async def principal():
    for g in grupos.ACTIVOS.values():
        if g.biblioteca:
            await textos(g)


async def textos(g: grupos.Grupo):
    salida = g.datos / "pdf-texto"
    completo = g.datos / "pdf-completo"
    salida.mkdir(parents=True, exist_ok=True)
    completo.mkdir(parents=True, exist_ok=True)
    ms = corpus.cargar(g)

    def falta(m):
        if not (salida / f"{m['id']}.txt").exists():
            return True
        return m.get("fecha", "") >= COMPLETO_DESDE and not (completo / f"{m['id']}.txt").exists()

    pdfs = [m for m in ms.values()
            if m["tema"] == g.biblioteca and m.get("mime") == "application/pdf" and (m.get("tamano") or 0) <= MAXIMO]
    pendientes = [m for m in pdfs if falta(m)]
    atrasados = sorted((m for m in pdfs if m not in pendientes and not (completo / f"{m['id']}.txt").exists()),
                       key=lambda m: m.get("fecha", ""), reverse=True)
    pendientes += atrasados[:ATRASADOS_POR_PASADA]
    if not pendientes:
        print(f"{g.clave} pdf: nada nuevo")
        return
    cliente = exportar.cliente_telegram()
    await cliente.start()
    try:
        chat = await cliente.get_entity(g.usuario)
        with tempfile.TemporaryDirectory() as tmp:
            for m in pendientes:
                msg = await cliente.get_messages(chat, ids=m["id"])
                if not msg or not msg.file:
                    continue
                ruta = Path(tmp) / f"{m['id']}.pdf"
                await msg.download_media(file=str(ruta))
                r = subprocess.run(["pdftotext", "-l", str(PAGINAS), "-enc", "UTF-8", str(ruta), "-"],
                                   capture_output=True, text=True)
                (salida / f"{m['id']}.txt").write_text(limpiar(r.stdout))
                if True:   # el texto entero, también de lo anterior a COMPLETO_DESDE (poco a poco)
                    entero = subprocess.run(["pdftotext", "-enc", "UTF-8", str(ruta), "-"], capture_output=True, text=True)
                    (completo / f"{m['id']}.txt").write_text(entero.stdout[:COMPLETO_MAX])
                ruta.unlink(missing_ok=True)
                print(f"  {m['id']} {m.get('archivo')}: {len(r.stdout)} caracteres", flush=True)
    finally:
        await cliente.disconnect()


if __name__ == "__main__":
    asyncio.run(principal())
