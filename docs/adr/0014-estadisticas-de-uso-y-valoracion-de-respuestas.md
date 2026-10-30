# 14. Estadísticas de uso y valoración de las respuestas

Fecha: 2026-10-30 · Estado: aceptado

## Contexto

Hasta el 30-10-2026, `/estado` daba las preguntas, las personas de cada día y el
número de preguntas sin resolver. Con eso no se sabía lo que más importa: si el
bot sirve a quien lo usa. Juanjo eligió tres de las propuestas: personas que
vuelven, proporción de preguntas sin resolver y 👍/👎 bajo la última respuesta.

## Decisión

1. **Personas del mes y cuántas vuelven otro día.** `contar_pregunta` guarda,
   solo durante el mes, en qué días ha preguntado cada cuenta (`dias_mes` en el
   estado); al cambiar de mes se borra. `/estado` dice cuántas personas han
   preguntado y cuántas lo han hecho en más de un día. Empezó a contarse el
   30-10-2026: en octubre la línea dice «desde el 30/10» para no mezclarla con
   las preguntas, que son de todo el mes.
2. **Sin resolver como proporción.** Las guardadas (60 días) frente a las
   preguntas de esos mismos días, que salen del historial diario. Las que fallan
   por un error no se cuentan como respondidas, así que se suman a las
   preguntas.
3. **👍/👎 solo bajo la última respuesta.** Juanjo preguntó si saldrían en cada
   mensaje; decidir cuáles «dan una solución» no es fiable (el bot no sabe si ha
   resuelto la duda), así que van en toda respuesta a una pregunta, pero al
   llegar la siguiente se quitan de la anterior: nunca hay más de una fila a la
   vista. No las llevan la ayuda, los avisos, los menús, las fichas ni el
   borrador de una incidencia de Karla. Al pulsar, los botones desaparecen y un
   aviso breve da las gracias. Se cuentan sin decir quién; con 👎, la pregunta
   pasa a las sin resolver (anónima, motivo «valoración negativa»), salvo que ya
   estuviera. La ayuda de los dos bots lo dice en los cinco idiomas.

4. **En tablas.** Juanjo las prefiere si Telegram las admite, y las admite
   desde el Bot API 10.1 (11-06-2026), con los mensajes enriquecidos
   (`sendRichMessage`, `<table>` en su HTML). `/estado` manda una tabla «Uso» con
   lo de hoy y lo del mes en columnas («—» donde una cifra no existe: los
   documentos recibidos solo se cuentan por día y los publicados por mes) y otra
   con los últimos 7 días. Si Telegram rechaza el mensaje enriquecido, se manda
   lo mismo en texto con las columnas alineadas, que es también lo que da
   `python bot.py estado` en la terminal.

Lo de Juanjo no cuenta en nada de esto, pero ve los mismos botones y avisos que
los demás.

## Alternativas descartadas

- Botones en todas las respuestas: llenan la conversación de filas iguales.
- Botones solo en las respuestas que resuelven: no hay forma fiable de saberlo.
- Temas más preguntados: habría que guardar las preguntas, y los bots prometen
  guardar solo las que no resuelven.

## Consecuencias

- Además de las cuentas del día (para los cupos, ADR 0006), el estado guarda
  durante el mes los días en que pregunta cada cuenta. No guarda qué pregunta.
- La respuesta valorable se recuerda solo en memoria: tras reiniciar un bot, los
  botones de la respuesta anterior no se quitan solos y, si se tocan, no
  cuentan. Así un segundo toque tampoco cuenta dos veces.

## Evidencia

- `scripts/bot.py`: `contar_pregunta`, `personas_mes`, `sin_resolver_de`,
  `valoraciones`, `Bot.enviar_valorable` y `Bot.valorar`; Karla los hereda.

## Riesgos y limitaciones

- Poca gente pulsa estos botones: las valoraciones serán pocas y se leen como
  señal, no como medida del acierto.

## Validación

30-10-2026:
- `pruebas/simular_catalogo.py`: los botones salen en la respuesta y se quitan
  de la anterior; 👎 cuenta una vez y guarda la pregunta sin la cuenta; `/estado`
  da las tres cifras; quien pregunta en dos días cuenta como que vuelve y Juanjo
  no cuenta. Todo bien.
- En Telegram, desde la cuenta de Juanjo, dos preguntas a cada bot (IA Educativa
  y Karla): solo la última respuesta lleva 👍/👎; al pulsar 👎 sale «Gracias.
  Guardo la pregunta, sin nada tuyo, para mejorar.» y los botones desaparecen.
- `/estado` a los dos bots: Telegram acepta el mensaje enriquecido (sin error en
  el registro ni paso al texto). Telethon no lo interpreta, así que el aspecto se
  mira en la app.
