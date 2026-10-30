#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Monta en IONOS el receptor de la copia diaria y deja al NAS con su testigo.
# Se ejecuta EN EL PORTÁTIL. El testigo se genera aquí y va por tuberías a IONOS y
# al NAS: no se imprime ni se guarda en el repositorio.
#
#   respaldo/instalar.sh            instala o actualiza el receptor
#   respaldo/instalar.sh --testigo  además genera un testigo nuevo
set -euo pipefail

BASE="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
IONOS="${IONOS_HOST:-ionos-webspace}"
NAS="${NAS_BOT:-jjdeharo@192.168.1.113}"
CARPETA="respaldo-bot-ia-educativa"
URL="https://bilateria.org/$CARPETA/recibir.php"
CRED_NAS="/volume1/docker/bot-chatgpt-ia-edu/credenciales/respaldo-ionos.json"

ssh "$IONOS" "mkdir -p '$CARPETA'"
ssh "$IONOS" "cat > '$CARPETA/recibir.php'" < "$BASE/recibir.php"
ssh "$IONOS" "cat > '$CARPETA/.htaccess'" < "$BASE/htaccess"

if [ "${1:-}" = "--testigo" ] || ! ssh "$IONOS" "test -s '$CARPETA/token.txt'"; then
  testigo=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
  printf '%s' "$testigo" | ssh "$IONOS" "cat > '$CARPETA/token.txt' && chmod 600 '$CARPETA/token.txt'"
  printf '{"url": "%s", "token": "%s"}\n' "$URL" "$testigo" \
    | ssh "$NAS" "umask 077 && cat > '$CRED_NAS'"
  unset testigo
  echo "Testigo nuevo instalado en IONOS y en el NAS."
fi

echo -n "La copia no se sirve desde la web: "
curl -s -o /dev/null -w '%{http_code}\n' "https://bilateria.org/$CARPETA/token.txt"
echo -n "Sin testigo, el receptor rechaza: "
curl -s -o /dev/null -w '%{http_code}\n' -X POST "$URL"
