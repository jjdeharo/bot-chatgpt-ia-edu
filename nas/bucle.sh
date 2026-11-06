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
  # Lo que se ve en las imágenes nuevas, con Claude Haiku (ADR 0028). Si falla, la pasada sigue y la
  # marca no se pierde: es un añadido, no la puesta al día.
  python imagenes.py || echo "imágenes: con fallos; se reintenta en la siguiente pasada"
  python indexar.py || ok=0
  # La documentación de eXeLearning para Karla bot, tal como la deja memoria-telegram (ADR 0008).
  if [ -n "${DOCS_FUENTES:-}" ]; then
    # shellcheck disable=SC2086 — son varias carpetas separadas por espacios
    python documentacion.py indexar $DOCS_FUENTES --salida /proyecto/datos/exelearning/documentacion || ok=0
    # Si memoria-telegram dejara de rehacerla, Karla seguiría con lo viejo sin que nadie lo notara (ADR 0021).
    # shellcheck disable=SC2086
    python documentacion.py vigilar $DOCS_FUENTES --dias 3 || true
  fi
  # El MIAE y la guía Vibe coding responsable, de sus repositorios de GitHub: se descargan una vez al día y se
  # reindexan solo si han cambiado (ADR 0031). Si falla, el bot sigue con la última copia.
  python marcos.py actualizar || echo "marcos: con fallos; sigo con la última copia"
  # Cuántas personas hay en cada grupo y en varios a la vez, para el diario (ADR 0032): una vez por semana;
  # si falla, a las seis horas. No toca la marca de la pasada: es un añadido.
  python comunidades.py || echo "comunidades: sin cifras nuevas en esta pasada"
  date '+%F %T' > /proyecto/datos/ultimo-intento   # cada pasada, haya ido bien o mal
  if [ "$ok" -eq 1 ]; then
    date '+%F %T' > /proyecto/datos/ultima-pasada   # la última puesta al día completa: la que enseñan los bots
  else
    echo "pasada con fallos: la marca ultima-pasada se queda como estaba"
  fi
  sleep $((900 - $(date +%s) % 900 + 120))   # cada cuarto de hora, sin deriva (27-10-2026: antes, cada hora)
done
