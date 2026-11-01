# Registro de cambios

Las versiones siguen a los bots en marcha, no a los datos. La etiqueta de git y `bot.VERSION` llevan el mismo número.

## 1.3.2 — 2026-11-01

Si Anthropic deja de atender a un bot porque se han acabado los créditos o se ha llegado a un límite de gasto de la Console, el bot avisa a Juanjo una vez, con la causa, hasta que vuelva a funcionar (ADR 0024). A quien pregunta no se le dice nada de dinero.

## 1.3.1 — 2026-11-01

El mensaje que lleva una pregunta al grupo dice ahora que se contesta allí, respondiendo a ese mensaje, y a quién se le hará llegar por privado: la frase anterior se podía leer como si hubiera que escribir al bot.

## 1.3.0 — 2026-11-01

Dos ideas del análisis competitivo del 01-11 (ADR 0023). **Preguntar en el grupo**: cuando un bot no encuentra la respuesta, o la persona pulsa 👎, ofrece llevar la pregunta al grupo con su nombre; antes enseña el mensaje tal como quedará, y quien responda allí a ese mensaje le llega por privado durante una semana; se puede quitar en 48 horas, con un tope de tres al día por persona (no en EduMedia-IAG). **`/sinresolver`**, para Juanjo: las preguntas sin resolver agrupadas por temas con Sonnet, con qué las resolvería y un ejemplo literal de cada tema (unos 0,01 USD; sin gasto con menos de 5).

## 1.2.0 — 2026-11-01

Notas de voz en los dos bots (ADR 0022): un servicio de voz con faster-whisper «small», reutilizando la imagen, el entorno y el modelo ya descargado del boletín semanal; el bot enseña lo que ha entendido y responde como a una pregunta escrita. Sin gasto de API.

## 1.1.0 — 2026-11-01

Las mejoras del informe del 01-11 (ADR 0021): los mensajes reenviados llevan quién los escribió y cuándo, para que el bot dé con el hilo exacto; Karla ofrece avisar de cada respuesta del equipo a quien envía un aviso de error, y del cierre; Karla lee archivos `.elpx`, `.elp` y `.zip` (resumen del proyecto: versión, páginas, iDevices) y diagnostica con ellos; el bucle del índice avisa si la documentación de eXeLearning lleva tres días sin cambiar; y pedir aplicaciones o recursos de un tema va por la búsqueda normal, no por la ayuda para enseñar (de 0,08 a 0,003 USD).

## 1.0.0 — 2026-11-01

Primera versión etiquetada: los dos bots tal como corren en el NAS desde el 27-10-2026, con las correcciones de la revisión de seguridad del 31-10 (ADR 0019) y las del informe del 01-11 (ADR 0020): respuesta fija cuando Claude no deja texto, firma en los botones que borran lo publicado, reintento ante un 429 de Telegram, repuesto HTML con encabezados, tablas y citas, preguntas largas hasta 6.000 caracteres con aviso de recorte, enlaces de Telegram tratados como pregunta, sin aviso a quien responde al resumen semanal sin preguntar, enlace al código y versión en la ayuda, copia diaria con lo de Karla, pruebas en GitHub Actions y la cuenta de Juanjo fuera del código.
