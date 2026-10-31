#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# El reloj del índice dentro del contenedor.
#
# Cada 15 minutos, lo nuevo de cada grupo: mensajes, textos de PDF y significado. A las
# 3 de la madrugada, el historial entero: lo que alguien haya borrado o
# editado en Telegram se refleja en el índice como mucho al día siguiente.
# A esa hora se manda también a IONOS la copia de lo que solo está en el NAS
# (respaldo.py). A las 3 y no a las 4, para no coincidir con la pasada del archivo diario
# (memoria-telegram), que usa la misma cuenta.
set -u
cd /proyecto/scripts || exit 1

while true; do
  hora=$((10#$(date +%H)))
  dia=$(date +%F)
  ok=1   # la marca de puesta al día solo se escribe si todos los pasos han ido bien (revisión del 31-10-2026)
  if [ "$hora" -eq 3 ] && [ "$(cat /proyecto/datos/ultimo-completo 2>/dev/null)" != "$dia" ]; then
    if python exportar.py --todo; then echo "$dia" > /proyecto/datos/ultimo-completo; else ok=0; fi
    python respaldo.py || echo "respaldo: no se ha podido mandar la copia a IONOS"
  else
    python exportar.py || ok=0
  fi
  python pdfs.py || ok=0
  python indexar.py || ok=0
  # La documentación de eXeLearning para Karla bot, tal como la deja memoria-telegram (ADR 0008).
  if [ -n "${DOCS_FUENTES:-}" ]; then
    # shellcheck disable=SC2086 — son varias carpetas separadas por espacios
    python documentacion.py indexar $DOCS_FUENTES --salida /proyecto/datos/exelearning/documentacion || ok=0
  fi
  date '+%F %T' > /proyecto/datos/ultimo-intento   # cada pasada, haya ido bien o mal
  if [ "$ok" -eq 1 ]; then
    date '+%F %T' > /proyecto/datos/ultima-pasada   # la última puesta al día completa: la que enseñan los bots
  else
    echo "pasada con fallos: la marca ultima-pasada se queda como estaba"
  fi
  sleep $((900 - $(date +%s) % 900 + 120))   # cada cuarto de hora, sin deriva (27-10-2026: antes, cada hora)
done
