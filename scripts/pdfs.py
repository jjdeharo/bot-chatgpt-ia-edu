# SPDX-License-Identifier: AGPL-3.0-or-later
"""Saca el texto de las primeras páginas de los PDF de la Biblioteca digital.

Muchos documentos se compartieron solo con el nombre del archivo; sin su
texto no se pueden encontrar por el tema que tratan. Se guarda solo el
texto (datos/<grupo>/pdf-texto/<id>.txt) y el PDF se borra después: el
documento sigue en el grupo y el bot enlaza allí. Solo en los grupos con
biblioteca.
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


def limpiar(t: str) -> str:
    lineas = [" ".join(l.split()) for l in t.splitlines()]
    return "\n".join(l for l in lineas if len(l) > 2)[:4000]


async def principal():
    for g in grupos.ACTIVOS.values():
        if g.biblioteca:
            await textos(g)


async def textos(g: grupos.Grupo):
    salida = g.datos / "pdf-texto"
    salida.mkdir(parents=True, exist_ok=True)
    ms = corpus.cargar(g)
    pendientes = [m for m in ms.values()
                  if m["tema"] == g.biblioteca and m.get("mime") == "application/pdf"
                  and not (salida / f"{m['id']}.txt").exists() and (m.get("tamano") or 0) <= MAXIMO]
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
                ruta.unlink(missing_ok=True)
                print(f"  {m['id']} {m.get('archivo')}: {len(r.stdout)} caracteres", flush=True)
    finally:
        await cliente.disconnect()


if __name__ == "__main__":
    asyncio.run(principal())
