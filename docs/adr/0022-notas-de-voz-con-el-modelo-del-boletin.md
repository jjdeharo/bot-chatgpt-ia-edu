# 22. Notas de voz, pasadas a texto con el modelo de voz del boletín semanal

Fecha: 2026-11-01 · Estado: aceptado

## Contexto

Los dos bots rechazaban las notas de voz («solo entiendo mensajes escritos»), y mucho profesorado
las usa. El informe del 01-11-2026 dejó la voz fuera por suponer un modelo nuevo residente en el NAS
(1 GB) o una API de pago. Juanjo señaló que el boletín semanal ya pasa audio a texto: faster-whisper
con el modelo «small», en local, en el NAS, con el modelo descargado (464 MB) y la imagen con ffmpeg
y el entorno de Python ya hechos. No hay nada que instalar ni que pagar.

## Decisión

- **Un servicio de voz** (`scripts/voz.py`, contenedor `bot-voz`) como el de significado: recibe el
  audio por HTTP (`POST /transcribir`) y devuelve texto, idioma detectado y duración. Corre con la
  imagen del boletín (`boletin-semanal:local`), su entorno de Python (`repo/.venv`, montado en solo
  lectura) y su caché de modelos (`home/.cache/huggingface`, solo lectura, `HF_HUB_OFFLINE=1`). El
  modelo se carga en cada petición y se suelta: en reposo no ocupa memoria; mientras transcribe, unos
  500 MB. De uno en uno, con dos hilos y 1,5 núcleos como mucho; audios de hasta 3 minutos.
- **En los bots** (`Bot.voz_a_texto`, común a los dos): una nota de voz o un audio se descarga de
  Telegram, se manda al servicio y su texto sigue el camino de una pregunta escrita. Antes de responder,
  el bot enseña lo que ha entendido («He entendido: «…»»), porque el modelo se equivoca con los nombres;
  a Claude le llega con la nota «[Transcrito de una nota de voz: puede llevar erratas]», que no se
  guarda en el historial. El idioma que detecta el modelo vale para los textos fijos, sin llamar a
  Claude. Sin servicio, demasiado largo o sin palabras, un aviso y nada más.
- `solo_texto` y las ayudas dicen que se admiten notas de voz.

## Alternativas descartadas

- Una API de voz de pago: Juanjo no quiere gastos recurrentes.
- Instalar faster-whisper en la imagen de los bots: 1 GB más de imagen y un segundo modelo en disco;
  reutilizar lo del boletín no duplica nada.
- Mantener el modelo cargado: 500 MB permanentes en un NAS con 2,8 GB disponibles, para unas pocas
  notas al día; cargarlo cuesta 3-5 segundos y se acepta.
- Transcribir dentro del proceso del bot: lo bloquearía más tiempo y mezclaría dependencias.

## Consecuencias

- Una nota de voz tarda unos 10-20 segundos más que una pregunta escrita (carga del modelo y
  transcripción) y no cuesta nada de API; el bot avisa «Te escucho» y muestra «escribiendo».
- El servicio depende de dos carpetas del boletín: si el boletín cambia de entorno o de caché, hay
  que ajustar `nas/compose.yml`. Los lunes de madrugada compite por CPU con la transcripción del
  boletín, que usa tres núcleos; con 1,5 núcleos propios, ninguno se queda sin.
- El audio no se guarda en ningún sitio: va de Telegram al servicio en memoria y a un archivo
  temporal que se borra.

## Evidencia

- `boletin-semanal/scripts/transcribir.py` y su `requirements.txt` (`faster-whisper>=1.0`); en el NAS,
  `repo/.venv` con faster-whisper 1.2.1 y ctranslate2 4.8.2, y el modelo en
  `home/.cache/huggingface/hub/models--Systran--faster-whisper-small` (464 MB).
- Memoria del NAS al decidirlo: 7,7 GB en total, 2,8 GB disponibles.

## Riesgos y limitaciones

- El modelo «small» se equivoca con nombres propios y términos raros; por eso se enseña la
  transcripción y se avisa a Claude. `TERMINOS` en `voz.py` le da los habituales de los dos grupos.
- Un audio en un idioma distinto de los cinco se transcribe igual, pero los textos fijos siguen en
  el idioma que tuviera la persona.

## Validación

- `pruebas/test_revision.py`: 49 pruebas (46 anteriores y 3 nuevas: sin servicio, demasiado largo,
  transcripción que sigue como pregunta), en verde el 01-11-2026.
- En el NAS: el servicio responde en `/salud` y transcribe un audio de prueba sintetizado con la voz
  del boletín; una nota de voz real desde Telegram, pendiente de la primera que llegue.
