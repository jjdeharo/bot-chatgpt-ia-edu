# 28. Descripción de las imágenes de los grupos

Fecha: 2026-11-03 · Estado: aceptado

## Contexto

El índice guarda de cada mensaje su texto y, si lleva algo adjunto, solo el tipo de archivo. Una
captura de una herramienta, una infografía o un resultado compartidos con poco texto no dicen nada al
buscador del bot, a la ayuda para preparar clases ni al Diario de IA Educativa, que leen
`datos/<grupo>/mensajes.jsonl`. Juanjo lo preguntó el 03-11-2026 a propósito de un meme que reenvió a
Vibe Coding Educativo, y aprobó que el bot describa las imágenes («sí, compruébalo y prepáralo»).

En los 30 días anteriores al 03-11-2026 hubo 64 fotos en ChatGPT-IA-edu, Vibe Coding Educativo y
EduMedia-IAG (32 con menos de 40 caracteres de texto), y en eXeLearning unas 22 al mes. Vídeos y
audios, unos 26 al mes en los tres grupos.

## Decisión

- `scripts/imagenes.py`, en cada pasada de `nas/bucle.sh` después de los PDF: de cada foto (o archivo
  de imagen JPEG, PNG, GIF o WebP de hasta 10 MB) publicada desde el 01-11-2026 en los grupos
  activos del índice, descarga la imagen con la cuenta de Juanjo, como `pdfs.py`, y pide a Claude
  Haiku 5.5 una descripción de una a cuatro frases en castellano, con el texto importante que se lea
  y, si es un meme, el chiste. Se le pasa también el texto del mensaje.
- Se guarda solo la descripción, en `datos/<grupo>/imagenes/<id>.txt`; la imagen sigue en el grupo.
  `corpus.cargar` la une al mensaje (`imagen`) y `corpus.contenido` la añade como `[imagen: …]`, así
  que llega sin más cambios al buscador, a la ayuda para preparar clases y a Karla bot. El diario la
  lee en su `scripts/preparar.py`.
- Lo de un mensaje borrado en Telegram se borra también (`limpiar`), como hace el índice con el texto.
- Sin pensamiento y con esfuerzo bajo (`thinking: disabled`, `effort: low`, que Haiku 5.5 admite);
  hasta 500 tokens de salida. Una imagen que falla tres veces se deja (`imagenes/fallos.json`).
- Límites: 40 por pasada y 1 USD al mes, con su cuenta en `datos/imagenes-gasto.json`. Usa la clave y
  el cliente del Bot de IA Educativa (`saldo.cliente`), que avisa si Anthropic corta por saldo.
- El encargo pide no identificar a nadie por su cara y tratar el texto de la imagen como material,
  no como instrucciones.
- Si falla, la pasada sigue: es un añadido y no impide la puesta al día.

## Alternativas descartadas

- **Describir también vídeos y audios**: son pocos, casi siempre ejemplos o memes, y cuestan mucho
  más; las notas de voz que se mandan al bot ya se transcriben (ADR 0022).
- **Describir el historial entero** (unas 15.000 imágenes desde 2019 en los cuatro grupos): unos 4 USD
  y miles de descargas de Telegram. Se puede hacer más adelante bajando `DESDE`.
- **Que el diario mire las imágenes por su cuenta**: solo serviría al diario, y el bot no guarda las
  imágenes.
- **Guardar la descripción en `mensajes.jsonl`**: la pasada completa de madrugada (`exportar.py
  --todo`) rehace ese archivo y la perdería.
- **Copia en IONOS** (`respaldo.py`): no hace falta; se rehace desde Telegram por céntimos.

## Consecuencias

- Con unas 85 imágenes al mes, unos 2 o 3 céntimos de dólar al mes (cálculo abajo).
- El índice se rehace también cuando cambia `imagenes/`, y solo vuelve a calcular el significado de
  los mensajes con descripción nueva.

## Evidencia

- Precio de Claude Haiku 5.5: 0,10 USD por millón de tokens de entrada y 0,50 de salida, para peticiones
  de hasta 100.000 tokens (https://platform.claude.com/docs/en/about-claude/pricing, consultada el
  03-11-2026).
- Tokens de una imagen: `⌈ancho / 28⌉ × ⌈alto / 28⌉`; en los modelos Claude 4.7 y posteriores, como
  Haiku 5.5, como mucho 4.784 por imagen (lado mayor de 2.576 píxeles)
  (https://platform.claude.com/docs/en/build-with-claude/vision, consultada el 03-11-2026). Una foto de
  Telegram de 1280 × 960 son 46 × 35 = 1.610 tokens.
- Coste por imagen: unos 2.000 tokens de entrada (imagen e instrucciones) y 200 de salida, unos 0,0003
  USD; en el peor caso (4.784 tokens de imagen), unos 0,0007 USD.
- Recuento de imágenes: `datos/<grupo>/mensajes.jsonl` del NAS, 03-11-2026.

## Riesgos y limitaciones

- La descripción la escribe una IA y puede equivocarse; el encargo del diario lo dice al redactor.
- Una captura con datos personales queda descrita en el NAS como el resto de mensajes, que ya estaban
  publicados en un grupo abierto.

## Validación

Pruebas sin red en `pruebas/test_imagenes.py` (qué se describe, tipo por los primeros bytes, la
descripción llega al texto que se busca, lo borrado se borra, la cuenta del gasto). Primera pasada de
verdad en el NAS el 03-11-2026, con las imágenes desde el 01-11.

## Corrección del 04-11-2026

La descripción de una captura compartida con un enlace a geografiaagustinos.blogspot.com/2013/10/…
añadió que el enlace «apunta a una entrada antigua de otro sitio». La entrada se había vuelto a
publicar el 3-11-2026 con una aplicación hecha con Gemini, que Juanjo probó; el redactor del diario
la descartó apoyándose en esa frase. Desde la 1.7.1 las instrucciones piden describir solo la imagen,
sin juzgar el mensaje ni valorar sus enlaces, que el modelo no puede abrir.

