# SPDX-License-Identifier: AGPL-3.0-or-later
# El bot del grupo ChatGPT-IA-edu en el NAS.
#
# La imagen solo trae Python, sus paquetes y pdftotext. El código, los datos,
# el índice, el modelo de significado y las credenciales se montan desde
# /volume1/docker/bot-chatgpt-ia-edu: reconstruir la imagen no toca nada.
FROM python:3.11-slim-bookworm

ENV TZ=Europe/Madrid \
    PYTHONUNBUFFERED=1 \
    FASTEMBED_CACHE_PATH=/proyecto/datos/modelos

RUN apt-get update && apt-get install -y --no-install-recommends tini poppler-utils tzdata \
 && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# El mismo uid que Juanjo en el NAS, para que lo escrito en los volúmenes sea suyo.
RUN useradd -u 1000 -m -s /bin/bash jjdeharo
USER 1000
WORKDIR /proyecto/scripts
ENTRYPOINT ["/usr/bin/tini", "--"]
