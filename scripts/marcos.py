# SPDX-License-Identifier: AGPL-3.0-or-later
"""El MIAE y la guía Vibe coding responsable, para que el Bot de IA Educativa los explique (ADR 0031).

Las dos obras se toman de sus repositorios públicos de GitHub, donde se generan, y no de una copia:
una vez al día se descarga de cada uno solo el texto (Markdown y los JSON de la guía rápida y la
ficha del MIAE). Se escribe un Markdown por página publicada, con su dirección en `enlaces.json`, y
se indexa por idiomas con el mismo programa que la documentación de Karla bot (documentacion.py):
un índice por idioma, para que la búsqueda no devuelva el mismo apartado cinco veces.

Si la descarga falla, el bot sigue con lo último que tiene; si lleva más de tres días sin poder
ponerlo al día, avisa a Juanjo una vez al día.

Uso: marcos.py actualizar [--forzar]     descargar (si toca) y reindexar
     marcos.py buscar "consulta" [idioma]
"""
import argparse
import io
import json
import os
import re
import shutil
import tarfile
import time
import urllib.request
from pathlib import Path

import documentacion
from grupos import DATOS

CARPETA = DATOS / "marcos"
IDIOMAS = ("es", "ca", "gl", "eu", "en")
CADA = 20 * 3600   # segundos entre descargas: una al día, en la primera pasada que toque
AVISO_DIAS = 3

GUIA = {"repo": "Vibe-Coding-Educativo/vibe-responsable", "rama": "main",
        "web": "https://vibe-coding-educativo.github.io/vibe-responsable/"}
MIAE = {"repo": "jjdeharo/miae", "rama": "main", "web": "https://jjdeharo.github.io/miae/"}
# Página publicada de cada Markdown de la guía (construir.py de vibe-responsable).
PAGINAS_GUIA = {"00-presentacion.md": "index.html", "01-guia.md": "guia.html", "02-herramientas.md": "herramientas.html",
                "03-creditos.md": "creditos.html", "04-para-la-ia.md": "para-la-ia.html",
                "05-referencias.md": "referencias.html", "06-evaluacion-vcer.md": "vcer.html",
                "instrucciones-ia.md": "instrucciones-vibe-responsable.md",
                "evaluacion-ia.md": "evaluacion-vibe-responsable.md"}
# Los dos archivos para la IA se publican sueltos, pero quien lee los encuentra en la página que los muestra.
ENSENA = {"instrucciones-ia.md": "para-la-ia.html", "evaluacion-ia.md": "vcer.html"}


# --- descarga ---------------------------------------------------------------
def descargar(cual: dict, destino: Path) -> None:
    """El repositorio entero en un tar.gz (codeload no gasta cuota de la API); se extraen solo los .md y .json."""
    url = f"https://codeload.github.com/{cual['repo']}/tar.gz/refs/heads/{cual['rama']}"
    pedido = urllib.request.Request(url, headers={"User-Agent": "bot-ia-educativa"})
    datos = urllib.request.urlopen(pedido, timeout=120).read()
    nuevo = destino.with_name(destino.name + ".nuevo")
    shutil.rmtree(nuevo, ignore_errors=True)
    with tarfile.open(fileobj=io.BytesIO(datos), mode="r:gz") as tar:
        for m in tar.getmembers():
            ruta = Path(*Path(m.name).parts[1:])  # sin la carpeta raíz «repo-rama»
            if not m.isfile() or ruta.suffix not in (".md", ".json") or ".." in ruta.parts:
                continue
            if not (ruta.parts[:1] == ("contenido",) or ruta.parts[:1] == ("content",) or ruta.parts[:1] == ("data",)):
                continue
            salida = nuevo / ruta
            salida.parent.mkdir(parents=True, exist_ok=True)
            salida.write_bytes(tar.extractfile(m).read())
    if not any(nuevo.rglob("*.md")):
        shutil.rmtree(nuevo, ignore_errors=True)
        raise RuntimeError(f"{cual['repo']}: el archivo no trae ningún Markdown")
    shutil.rmtree(destino, ignore_errors=True)
    nuevo.rename(destino)


# --- de las fuentes a un Markdown por página ---------------------------------
def limpio(t: str) -> str:
    """Los JSON del MIAE llevan algo de HTML: la negrita pasa a Markdown y el resto se quita."""
    t = re.sub(r"</?(b|strong)>", "**", t)
    return re.sub(r"<[^>]+>", "", t)


def guia(fuente: Path, idioma: str) -> dict[str, tuple[str, str]]:
    """{nombre: (texto, enlace)} de la guía en un idioma."""
    base = fuente / "contenido" / idioma
    salida = {}
    for f in sorted(base.glob("*.md")):
        if f.name in PAGINAS_GUIA:
            pagina = PAGINAS_GUIA[f.name]
            salida[f"vibe-responsable · {Path(pagina).stem}.md"] = (
                f.read_text(), f"{GUIA['web']}{idioma}/{ENSENA.get(f.name, pagina)}")
    for f in sorted((base / "capitulos").glob("*.md")):
        n = int(f.name.split("-")[0])
        salida[f"vibe-responsable · capitulo-{n}.md"] = (f.read_text(), f"{GUIA['web']}{idioma}/capitulo-{n}.html")
    return salida


def miae(fuente: Path, idioma: str) -> dict[str, tuple[str, str]]:
    """El marco completo, la guía rápida y la ficha para declarar el uso de IA, en un idioma."""
    version = json.loads((fuente / "data" / "versions.json").read_text())["latest"]
    salida = {}
    marco = fuente / "content" / f"v{version}" / f"{idioma}.md"
    if marco.exists():
        salida["miae · marco.md"] = (marco.read_text(), f"{MIAE['web']}v{version}/{idioma}/")
    q = fuente / "data" / "quickref" / f"{idioma}.json"
    if q.exists():
        q = json.loads(q.read_text())
        partes = [f"# {limpio(q['kicker'])}", limpio(q["lead"])]
        for n, nivel in enumerate(q["levels"]):
            partes.append(f"## {n}. {limpio(nivel['name'])}\n\n**{limpio(nivel['split'])}** {limpio(nivel['desc'])}")
            partes.append("\n".join(f"- {limpio(e)}" for e in nivel.get("examples", [])))
            if nivel.get("warn"):
                partes.append(f"⚠ {limpio(nivel['warn'])}")
        partes.append(f"## {limpio(q['back_title'])}")
        partes += [f"**{limpio(r['label'])}.** {limpio(r['text'])}" for r in q.get("rules", [])]
        salida["miae · guia-rapida.md"] = ("\n\n".join(p for p in partes if p), f"{MIAE['web']}{idioma}/guia/")
    g = fuente / "data" / "guide" / f"{idioma}.json"
    if g.exists():
        g = json.loads(g.read_text())
        partes = [f"# {limpio(g['guide_title'])}", limpio(g["guide_intro"]), limpio(g["principle"])]
        partes.append("\n".join(f"{n}. **{limpio(t)}.** {limpio(x)}" for n, (t, x) in enumerate(g["steps"], 1)))
        partes += [f"## {limpio(g['template_title'])}", limpio(g["template_intro"]),
                   "\n".join(f"- {limpio(c)}" for c in g["fields"]),
                   f"### {limpio(g['filled_title'])}",
                   "\n".join(f"- **{limpio(c)}:** {limpio(v)}" for c, v in zip(g["fields"], g["filled"])),
                   f"## {limpio(g['teacher_title'])}", limpio(g["teacher_intro"]),
                   "\n".join(f"- {limpio(c)}" for c in g["teacher_fields"])]
        salida["miae · ficha.md"] = ("\n\n".join(p for p in partes if p), f"{MIAE['web']}{idioma}/ficha/")
    return salida


def preparar(carpeta: Path = CARPETA) -> None:
    for idioma in IDIOMAS:
        docs = {**miae(carpeta / "fuentes" / "miae", idioma), **guia(carpeta / "fuentes" / "vibe-responsable", idioma)}
        md = carpeta / "md" / idioma
        shutil.rmtree(md, ignore_errors=True)
        md.mkdir(parents=True)
        for nombre, (texto, _) in docs.items():
            (md / nombre).write_text(texto)
        (md.parent / f"enlaces-{idioma}.json").write_text(
            json.dumps({n: e for n, (_, e) in docs.items()}, ensure_ascii=False, indent=1))
        documentacion.indexar([md], carpeta / "indice" / idioma)


def avisar(texto: str) -> None:
    """Una vez al día, por el bot, a Juanjo."""
    marca, hoy = CARPETA / "aviso", time.strftime("%Y-%m-%d")
    if marca.exists() and marca.read_text().strip() == hoy:
        return
    juanjo = int(os.environ.get("JUANJO") or 0)
    cred = Path(os.environ.get("BOT_CRED", Path.home() / ".config/credenciales/bot-chatgpt-ia-edu.json"))
    print(texto)
    if juanjo and cred.exists():
        import urllib.parse
        token = json.loads(cred.read_text())["token"]
        datos = urllib.parse.urlencode({"chat_id": juanjo, "text": texto}).encode()
        urllib.request.urlopen(f"https://api.telegram.org/bot{token}/sendMessage", datos, timeout=30)
        marca.write_text(hoy)


def actualizar(forzar: bool = False) -> None:
    CARPETA.mkdir(parents=True, exist_ok=True)
    hecho = CARPETA / "descargado"
    edad = time.time() - (hecho.stat().st_mtime if hecho.exists() else 0)
    falta = not all((CARPETA / "indice" / i / "trozos.json").exists() for i in IDIOMAS)
    nuevo = False
    if forzar or edad > CADA or falta:
        try:
            descargar(MIAE, CARPETA / "fuentes" / "miae")
            descargar(GUIA, CARPETA / "fuentes" / "vibe-responsable")
            hecho.touch()
            edad, nuevo = 0, True
        except Exception as error:  # noqa: BLE001 — se sigue con lo último descargado
            print(f"marcos: no he podido descargar ({type(error).__name__}: {error}); sigo con lo que hay")
    if edad > AVISO_DIAS * 86400:
        avisar("Aviso del Bot de IA Educativa: hace más de tres días que no consigo descargar de GitHub el MIAE y la "
               "guía Vibe coding responsable. Sigo respondiendo con la última copia que tengo.")
    # Solo con algo recién descargado (o si falta el índice): el resto de pasadas no tocan nada.
    if (nuevo or falta) and all((CARPETA / "fuentes" / r).exists() for r in ("miae", "vibe-responsable")):
        preparar()


# --- búsqueda -----------------------------------------------------------------
class Marcos:
    """Un índice por idioma; se recarga solo cuando el bucle del NAS lo rehace."""

    def __init__(self, modelo=None, carpeta: Path = CARPETA):
        self.carpeta, self.modelo = carpeta, modelo
        self.indices, self.enlaces, self.firmas = {}, {}, {}

    def idioma(self, idioma: str | None) -> str:
        idioma = idioma if idioma in IDIOMAS else "es"
        trozos = self.carpeta / "indice" / idioma / "trozos.json"
        firma = trozos.stat().st_mtime if trozos.exists() else None
        if firma is None:
            raise RuntimeError("El MIAE y la guía todavía no están disponibles; responde con lo de los grupos.")
        if self.firmas.get(idioma) != firma:
            self.indices[idioma] = documentacion.Documentacion(trozos.parent, self.modelo)
            self.modelo = self.indices[idioma].modelo
            self.enlaces[idioma] = json.loads((self.carpeta / "md" / f"enlaces-{idioma}.json").read_text())
            self.firmas[idioma] = firma
        return idioma

    def buscar(self, consulta: str, idioma: str | None = None, obra: str | None = None) -> dict:
        i = self.idioma(idioma)
        filtro = {"miae": "miae ·", "vibe-responsable": "vibe-responsable ·"}.get(obra or "")
        res = self.indices[i].buscar(consulta, n=8, documento=filtro)
        for r in res:
            r["enlace"] = self.enlaces[i].get(r["documento"], "")
        return {"idioma": i, "resultados": res}

    def leer(self, documento: str, apartado: str | None = None, idioma: str | None = None) -> dict:
        i = self.idioma(idioma)
        r = self.indices[i].leer(documento, apartado)
        if "documento" in r:
            r["enlace"] = self.enlaces[i].get(r["documento"], "")
        return r


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="orden", required=True)
    a = sub.add_parser("actualizar")
    a.add_argument("--forzar", action="store_true")
    b = sub.add_parser("buscar")
    b.add_argument("consulta")
    b.add_argument("idioma", nargs="?", default="es")
    args = p.parse_args()
    if args.orden == "actualizar":
        actualizar(args.forzar)
    else:
        for r in Marcos().buscar(args.consulta, args.idioma)["resultados"]:
            print(f"· {r['documento']} › {r['apartado']}\n  {r['enlace']}\n  {r['texto'][:160]!r}")
