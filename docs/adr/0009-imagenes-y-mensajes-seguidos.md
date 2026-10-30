# 9. Imágenes y mensajes seguidos en una sola consulta

Fecha: 2026-10-27 · Estado: aceptado

## Contexto

Juanjo reenvió a Karla bot una duda del grupo eXeLearning: dos mensajes, cada
uno con una captura del índice de Moodle y el texto como pie. Karla contestó
dos veces «Escríbeme la pregunta en texto». Los dos bots solo leían el campo
`text` de Telegram, así que una foto con pie llegaba vacía. Además, cada
mensaje se atendía por separado: un reenvío de dos mensajes daba dos
respuestas.

En las dudas de eXeLearning, la captura suele ser media pregunta. Claude
(Sonnet y Haiku) entiende imágenes. Según la tarifa de Anthropic, una imagen
cuesta unos 1.500 tokens de entrada, unos 0,003 US$ con Sonnet.

## Decisión

Igual en los dos bots, en el código común (`bot.py`):

1. **Se lee el pie de las fotos** como texto de la consulta.
2. **Las fotos van a Claude** junto con la pregunta, como máximo `MAX_FOTOS`
   (3), con las imágenes delante y el texto detrás, como recomienda Anthropic.
   Telegram entrega las fotos en JPEG; se usa la versión más grande.
3. **Los mensajes seguidos de una persona, en privado, son una sola
   consulta.** Cuando lo último que llega es texto o una foto, el bucle espera
   `JUNTAR_S` (3) segundos por si llega más. Telegram entrega un reenvío de
   varios mensajes en tandas con menos de un segundo entre ellas. Se junta el
   texto de todos, en su orden, y sus fotos (`juntar()`).
   - **Siguen su propio camino:** los comandos, un enlace suelto (un recurso
     para el catálogo) y los documentos (la Biblioteca digital).
   - **Corta la consulta:** un botón pulsado entre medias.
   - **Mientras espera,** el bot ya muestra «escribiendo…».
4. **Foto sin texto:** se responde igualmente. Las instrucciones de los dos
   bots les dicen que miren las imágenes como parte de la pregunta y, si sin
   texto no se entiende la duda, que pidan que se explique.
5. **El historial y las preguntas sin resolver guardan el texto** con la
   constancia de cuántas imágenes llevaba (`con_fotos()`). Las imágenes no
   pasan al historial, porque se volverían a mandar en cada pregunta de
   seguimiento.

## Consecuencias

- Cada consulta en privado tarda unos 3 segundos más. Es el precio de no
  responder a medias un reenvío.
- La consulta del SCORM, con sus dos capturas, le costó a Karla 0,09 US$ y
  tardó 15 s. Cinco búsquedas, frente a las dos o tres de una pregunta corta.
  La respuesta usó las capturas y todo lo que afirmó estaba en las fuentes:
  la incidencia #2334 y el registro de cambios de la 4.0.5.
- Con una captura sin texto, el bot de IA Educativa la describió y preguntó
  qué se buscaba, sin buscar (0,0008 US$).
- Se probaron con casos simulados el reenvío, el texto seguido de una foto, el
  comando, el enlace suelto, dos personas intercaladas, el documento, el grupo
  y el botón entre medias.
- Sin probar en vivo: un álbum de más de tres fotos y una foto reenviada
  desde un canal.
