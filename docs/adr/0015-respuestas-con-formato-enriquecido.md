# 15. Respuestas con formato enriquecido

Fecha: 2026-10-30 · Estado: aceptado

## Contexto

Las respuestas salían como mensaje normal de Telegram. El Bot de IA Educativa
tenía la instrucción de escribir «texto llano, enlaces en línea propia, sin
tablas ni encabezados»; Karla no tenía ninguna sobre el formato. Las dos ponían
a veces negritas, que el programa pasaba al HTML de Telegram
(`respuesta_html`). Desde el Bot API 10.1 (11-06-2026), Telegram tiene mensajes
enriquecidos (`sendRichMessage`) con encabezados, listas, tablas, citas y
bloques plegables. Juanjo pidió que los bots lo usen cuando haga falta porque
«visualmente mejora mucho».

## Decisión

- **Las respuestas a una pregunta se envían como mensaje enriquecido en
  Markdown** (`rich_message.markdown`), con 👍/👎 debajo (ADR 0014). Si
  Telegram lo rechaza, salen como antes, en HTML, y el registro lo dice
  («mensaje enriquecido rechazado»).
- **Una sola instrucción de formato para los dos bots** (`consultar.FORMATO`;
  Karla la añade a su persona): formato solo cuando ayude a leer; negrita para
  una o dos cosas; listas numeradas para pasos y con guiones para opciones;
  tabla para comparar varias cosas por las mismas características, con pocas
  columnas para el móvil; encabezados `###` solo si hay varias partes;
  `código` para nombres exactos de menús, botones, archivos u órdenes; `>` para
  citar un mensaje.
- **Los enlaces, como dirección completa**, nunca como `[texto](enlace)`: según
  la documentación, Telegram pide confirmación antes de abrir un enlace con
  texto. En el Bot de IA Educativa, cada enlace en su propia línea, como antes.
- **Sin el signo `$`**: en el Markdown de Telegram, `$…$` es una fórmula.
- La ayuda, los avisos, los menús, las fichas y el borrador de incidencia de
  Karla siguen como mensajes normales.

## Alternativas descartadas

- Seguir en texto llano: es lo que Juanjo quiere cambiar.
- Escribir las respuestas en el HTML enriquecido: el modelo escribe Markdown con
  más naturalidad, y la documentación lo da como compatible con GitHub Flavored
  Markdown en lo posible.

## Consecuencias

- Un mensaje enriquecido admite hasta 32.768 caracteres: la respuesta ya no se
  parte en trozos de 4.000 (sí en la vía de respaldo en HTML).
- Telethon (memoria-telegram, `tg.py`) aún no interpreta estos mensajes. No
  afecta al archivo de los grupos, porque los bots solo responden por privado.

## Evidencia

- Documentación del Bot API, apartados «Rich Message Formatting Options»,
  «Rich Message Limits» y `sendRichMessage` (consultada el 30-10-2026, versión
  10.3 del 24-08-2026): https://core.telegram.org/bots/api#rich-message-formatting-options
- `scripts/bot.py` (`Bot.enviar_valorable`) y `scripts/consultar.py` (`FORMATO`).

## Riesgos y limitaciones

- No se ha comprobado qué ve quien tiene una versión de Telegram anterior a los
  mensajes enriquecidos: la documentación no lo dice. Hipótesis pendiente.
- El Markdown de Telegram puede interpretar algo de forma inesperada (por
  ejemplo, el signo `$`); si lo rechaza, la respuesta sale igualmente en HTML.

## Validación

30-10-2026:
- `pruebas/simular_catalogo.py`: todo bien. Un paso del catálogo, que depende
  de la respuesta real de Claude, falló una vez y pasó al repetirlo; no tiene
  relación con este cambio.
- En Telegram, desde la cuenta de Juanjo: una comparación al Bot de IA Educativa
  y unos pasos a Karla salieron como mensaje enriquecido con 👍/👎, sin
  rechazos en el registro; al llegar la siguiente respuesta, la anterior perdió
  los botones. El aspecto lo mira Juanjo en la app.
