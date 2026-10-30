# SPDX-License-Identifier: AGPL-3.0-or-later
"""Los avisos de la revisión del repositorio de VCE (ADR 0013), en datos/avisos.json.

El bot los lee en /misrecursos: marca con ⚠️ los recursos con un aviso pendiente, dice qué les falta y
ofrece «Ya lo he corregido», que lo vuelve a comprobar. Este guion los prepara a partir de la clasificación
de la revisión (el informe de Juanjo) y los enseña; no avisa a nadie.

  avisos.py preparar CLASIFICACION.json --plazo AAAA-MM-DD   crea los pendientes (no toca los que ya hay)
  avisos.py prueba URL TIPO [MOTIVO]                          uno suelto, para probar el bot
  avisos.py ver                                               cuántos hay en cada estado
"""
import argparse
import collections
import json
from datetime import date, timedelta

import catalogo

TIPOS = {"A": "sin licencia", "B": "el enlace no se abre", "C": "un GPT de ChatGPT", "D": "derechos reservados"}
PLAZO_GPT = "2026-12-11"  # OpenAI retira los GPT ese día


def tipo_de(x: dict) -> str:
    m = x["motivo"]
    if m.startswith("derechos reservados"):
        return "D"
    if m.startswith("un GPT"):
        return "C"
    if m.startswith(("el servidor", "el enlace compartido")) or "no se abre" in m or "no existe" in m:
        return "B"
    return "A"


def motivo_corto(x: dict) -> str:
    m = x["motivo"]
    if m.startswith("el servidor responde"):
        return "error " + m.split()[-1]
    return m


def preparar(ruta: str, plazo: str) -> None:
    d = catalogo.leer_avisos()
    nuevos = 0
    for x in json.loads(open(ruta).read()):
        if x["categoria"] != "no_cumple":
            continue
        clave = catalogo.normalizar(x["url"])
        if clave in d:
            continue
        t = tipo_de(x)
        d[clave] = {"tipo": t, "motivo": motivo_corto(x), "titulo": x["titulo"], "aviso": date.today().isoformat(),
                    "plazo": PLAZO_GPT if t == "C" else plazo, "estado": "pendiente"}
        nuevos += 1
    catalogo.guardar_avisos(d)
    print(f"{nuevos} avisos nuevos; {len(d)} en total")


def ver() -> None:
    d = catalogo.leer_avisos()
    print(collections.Counter((a["tipo"], a["estado"]) for a in d.values()))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="orden", required=True)
    a = sub.add_parser("preparar")
    a.add_argument("clasificacion")
    a.add_argument("--plazo", required=True)
    b = sub.add_parser("prueba")
    b.add_argument("url")
    b.add_argument("tipo", choices=list(TIPOS))
    b.add_argument("motivo", nargs="?", default="")
    sub.add_parser("ver")
    args = p.parse_args()
    if args.orden == "preparar":
        preparar(args.clasificacion, args.plazo)
    elif args.orden == "prueba":
        d = catalogo.leer_avisos()
        d[catalogo.normalizar(args.url)] = {"tipo": args.tipo, "motivo": args.motivo, "titulo": "", "prueba": True,
                                            "aviso": date.today().isoformat(), "plazo": PLAZO_GPT if args.tipo == "C"
                                            else (date.today() + timedelta(days=30)).isoformat(),
                                            "estado": "pendiente"}
        catalogo.guardar_avisos(d)
        print("aviso de prueba puesto")
    else:
        ver()
