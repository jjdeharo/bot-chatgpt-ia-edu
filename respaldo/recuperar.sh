#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Trae de IONOS la copia más reciente y la deja en datos/ (catalogo.json,
# estado-bot.json y avisos.json), donde la lee el bot. Se ejecuta en la máquina que vaya a
# llevar el bot. Lo que haya ya en datos/ se guarda al lado con «.antes».
#
#   respaldo/recuperar.sh [DESTINO]     por defecto, la carpeta datos/ del repositorio
set -euo pipefail

BASE="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/.." && pwd)"
IONOS="${IONOS_HOST:-ionos-webspace}"
DESTINO="${1:-$BASE/datos}"
CARPETA="respaldo-bot-ia-educativa"

ultima=$(ssh "$IONOS" "ls -1 $CARPETA/copia-*.json | tail -1")
echo "Copia: $ultima"
mkdir -p "$DESTINO"
ssh "$IONOS" "cat '$ultima'" | python3 -c '
import json, sys
from pathlib import Path
destino = Path(sys.argv[1])
copia = json.load(sys.stdin)
for clave, nombre in (("catalogo", "catalogo.json"), ("estado", "estado-bot.json"), ("avisos", "avisos.json")):
    if clave not in copia:  # las copias anteriores al 29-10-2026 no llevan avisos
        continue
    f = destino / nombre
    if f.exists():
        f.replace(f.with_name(nombre + ".antes"))
    f.write_text(json.dumps(copia[clave], ensure_ascii=False, indent=1))
cat = copia["catalogo"]
print("Del", copia["marca"] + ":", len(cat.get("recursos", {})), "recursos con dueño,",
      len(cat.get("correos", {})), "cuentas con correos comprobados.")
' "$DESTINO"
