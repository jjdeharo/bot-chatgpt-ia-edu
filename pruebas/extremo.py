# SPDX-License-Identifier: AGPL-3.0-or-later
"""Pasa las preguntas de prueba por el bot entero (búsqueda + Claude).

Una respuesta acierta si cita el enlace de alguno de los mensajes esperados.
Guarda las respuestas en pruebas/respuestas-<fecha>.md para leerlas.
Cuesta dinero (unos 0,002 USD por pregunta con Haiku 5.5).
"""
import json
import sys
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "scripts"))
import consultar  # noqa: E402


def main():
    preguntas = json.loads((AQUI.parent / "datos" / "preguntas-prueba.json").read_text())  # fuera del repositorio: citan mensajes reales
    c = consultar.Consultor()
    obras = {i: o for o in c.b.obras.values() for i in o["ids"]}
    aciertos, total_usd, salida = 0, 0.0, []
    for q in preguntas:
        r = c.responder(q["p"])
        enlaces = set()
        for i in q["ids"]:
            enlaces.add(c.b.ms[i]["enlace"])
            if i in obras:
                enlaces.add(obras[i]["enlace"])
        ok = any(e in r["texto"] for e in enlaces)
        aciertos += ok
        total_usd += r["uso"]["usd"]
        u = r["uso"]
        print(f"{'✓' if ok else '✗'} {u['usd']:.4f} USD · {len(u['llamadas'])} búsq. · {q['p'][:75]}", flush=True)
        salida.append(f"## {'✓' if ok else '✗'} {q['p']}\n\n{r['texto']}\n\n"
                      f"_{len(u['llamadas'])} búsquedas · {u['entrada']}+{u['salida']} tokens · "
                      f"{u['usd']:.4f} USD_\n")
    resumen = (f"{aciertos}/{len(preguntas)} aciertos · {total_usd:.3f} USD en total · "
               f"{total_usd / len(preguntas):.4f} USD por pregunta · modelo {consultar.MODELO_CLAUDE}")
    print(resumen)
    f = AQUI / f"respuestas-{datetime.now():%Y-%m-%d-%H%M}.md"
    f.write_text(f"# Respuestas de prueba\n\n{resumen}\n\n" + "\n".join(salida))
    print(f)


if __name__ == "__main__":
    main()
