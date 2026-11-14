# 39. Retirada al acabar el plazo de los avisos del repositorio

Fecha: 2026-11-14 · Estado: aceptado

## Contexto

Los avisos de la revisión del repositorio de VCE (ADR 0013) salieron el 29-10-2026 con plazo: el 29-11-2026 para
los enlaces que no se abren (B) y las licencias incompatibles (D), y el 11-12-2026 para los GPT de ChatGPT (C), el
día que OpenAI los retira. Los recursos sin licencia (A) no se retiran nunca: quedan como recomendación (Juanjo,
29-10-2026). El plan que aprobó Juanjo el 27-10-2026 dejaba para el final del plazo volver a comprobar lo
pendiente, retirar lo que siga sin cumplir y desfijar el aviso del grupo (https://t.me/vceduca/14274), que fijó
el propio bot. Juanjo pidió que nada se retire sin su confirmación.

## Decisión

- `scripts/plazos.py`. El bot lo mira en cada vuelta de su bucle, como el aviso del diario y el resumen de los
  viernes: el día de cada plazo, desde las 9:00 de Madrid, una sola vez (lo apunta en `datos/plazos.json`). Si
  el bot estaba parado, lo hace al volver. Si falla, lo reintenta a la hora.
- B y D se vuelven a comprobar con la misma función que «Ya lo he corregido» (`catalogo.comprobar_licencia`, que
  ahora usan los dos), con el enlace tal como está en la hoja: las rutas de GitHub Pages distinguen mayúsculas, y
  la clave del aviso va en minúsculas.
  - Los que ya cumplen quedan «corregido» y su licencia pasa a la hoja, como con el botón.
  - Un B que ya se abre pero sigue sin licencia no se retira: el aviso solo hablaba del enlace («si sigue sin
    abrirse, se eliminará») y lo publicado antes del bot sin licencia se queda. Pasa a tipo A (`"era": "B"`), con
    su recomendación en `/misrecursos`.
  - Las apps de Gemini, Claude y AI Studio no se pueden comprobar: si se abren, van en la lista sin marcar, para
    que Juanjo las mire antes. Lo mismo si la comprobación falla.
- Los C no se comprueban: no tienen arreglo.
- Lo que ya no está en la hoja con ese enlace (su autor lo quitó o lo mudó) queda «sin_ficha». Lo que está en
  revisión manual de Juanjo («por_revisar») no se toca.
- Después le llega a Juanjo, por privado y en texto plano, qué se ha resuelto solo y la lista de lo que sigue sin
  cumplir (título, autor, enlace y por qué), con una casilla por recurso (✅ se retira, ⬜ se queda), «Retirar los
  marcados» y «No retirar ninguno». Solo él puede tocarlos. Las casillas se añadieron a los dos botones del
  encargo por las apps de plataforma, que el bot no puede comprobar: sin ellas, una sola duda obligaba a no
  retirar nada.
- Al retirar, solo lo marcado que sigue pendiente en ese momento (si su autor lo ha corregido o quitado mientras
  tanto, se salta y se dice). Antes de borrar cada fila de la hoja, se guarda entera en `datos/retirados.json`,
  con su dueño (la cuenta que lo dio de alta o la que ligó su correo) y su aviso. El aviso queda «retirado».
  `avisos.py restaurar URL` lo devuelve a la hoja y a su dueño. La copia va en el respaldo diario a IONOS.
- Retirado lo del 29-11-2026, el bot desfija el aviso del grupo (`unpinChatMessage`; es administrador con permiso
  para fijar). Con «No retirar ninguno», el aviso sigue fijado.
- A los autores no se les escribe nada: el aviso del 29-10-2026 ya decía qué pasaría.

## Alternativas descartadas

- Retirar sin confirmación al acabar el plazo: Juanjo quiere confirmar cada retirada.
- Una tarea aparte (cron del NAS o el bucle del índice): los botones los atiende el bot, y su bucle ya hace lo
  programado del día (diario, resumen semanal).
- Retirar también los B que se abren sin licencia: contradice el texto del aviso y la decisión sobre los A.

## Consecuencias

- El 29-11-2026 hacia las 9:00 y el 11-12-2026 a la misma hora, Juanjo recibe un mensaje con botones.
- Una ficha retirada se puede devolver. Si su autor solo tenía el correo del antiguo formulario sin cuenta ligada,
  al devolverla hay que volver a ligar a mano el enlace con su correo en el Apps Script (lo dice el comando).
- Lo que queda sin retirar (desmarcado o «No retirar ninguno») sigue con su aviso pendiente, y el bot no vuelve a
  preguntar por ese plazo.

## Evidencia

- 14-11-2026, `getChatMember` y `getChat` del grupo Vibe Coding Educativo: el bot es administrador con
  `can_pin_messages` y el mensaje fijado es el 14274, enviado por el propio bot.
- 14-11-2026, comprobación sin escribir nada con `avisos.json` del NAS y la hoja real: de 20 B y D pendientes, 12
  ya no están en la hoja con ese enlace, 7 siguen sin abrirse (404 o 502) y 1 es un enlace compartido de Gemini que
  responde pero el bot no puede comprobar. Las rutas de onio72.github.io llevan mayúsculas (`FQ2_…`,
  `departamentoFQ`) que la clave del aviso pierde.

## Riesgos y limitaciones

- El estado de cada enlace es el de las 9:00 del día del plazo; si su autor lo arregla después, la retirada lo
  salta solo si ha pulsado «Ya lo he corregido».
- Si Telegram no deja mandar el mensaje, no se apunta el plazo y se repite a la hora.

## Validación

- `pruebas/test_plazos.py` (sin red, Telegram ni API): cuándo toca y que sea una vez, qué se marca y qué no, la
  retirada con copia y desfijado, el segundo toque, lo corregido entre la lista y la retirada, «No retirar
  ninguno», que solo Juanjo pueda tocar los botones, la restauración y «Ya lo he corregido» tras el cambio.
- Simulación del 29-11 y del 11-12 con copias de `avisos.json` y `catalogo.json` del NAS, la hoja real solo para
  leer, los enlaces reales y Telegram de mentira: 8 en la lista del 29 (7 marcados y Gemini sin marcar), 6 GPT el
  11, desfijado solo el 29, y ninguna escritura en la hoja ni mensajes reales.
