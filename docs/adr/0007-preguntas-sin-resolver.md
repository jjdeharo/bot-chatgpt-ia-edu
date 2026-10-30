# 7. Preguntas sin resolver, guardadas de forma anónima

Fecha: 2026-10-27 · Estado: aceptado

## Contexto

Juanjo quiere que el bot tome nota de las peticiones que no resuelve, para
analizarlas más adelante, siempre que no cueste mucho. El bot prometía en la
ayuda «No guardo tus preguntas».

## Decisión

1. **Tres señales, sin preguntar a nadie:** Claude no encuentra lo que se pide;
   le piden algo que no sabe hacer («solo sirvo para…»), que es lo que revela
   funciones que faltan; o hay un error. Las dos primeras las marca Claude al
   final de su respuesta (`[[sin resultado]]`, `[[fuera de alcance]]`), y el
   programa quita la marca antes de enviarla: no cuesta ninguna llamada de más.
   Desde el 28-10-2026 (ADR 0011), las ideas, el consejo, una clase o una
   rúbrica las prepara con lo compartido en los grupos y ya no se marcan; solo
   se marca «fuera de alcance» lo que es producir o retocar un texto. Antes:
   cuando le piden que haga algo él (ideas, una actividad, una rúbrica), dice
   primero en una línea que eso no lo hace y que busca lo compartido en los
   grupos y la biblioteca, sigue con lo encontrado que le sirva a esa persona y
   lo marca siempre «fuera de alcance», para que se vea cuánta gente se lo pide.
   Antes buscaba el tema sin explicarlo: a «dame ideas para un trabajo de los
   órganos» devolvía mensajes de anatomía y quien preguntaba no sabía por qué.
   Sin botones de «me ha servido» bajo cada respuesta, que serían ruido.
   Desde el 29-10-2026, las preguntas sobre el propio bot no se marcan nunca:
   se responden con «Sobre ti», y aunque la respuesta sea que no, están
   resueltas. Por eso «Sobre ti» dice, en los dos bots, que solo funcionan en
   Telegram, por privado, y que no se pueden integrar en Moodle, en una web ni
   en otra plataforma (Juanjo, ante un «¿te puedo integrar en un foro de
   Moodle?» que Karla marcó «fuera de alcance»: «debería corresponder al
   autoconocimiento del bot»).
2. **Anónimo:** `datos/sin-resolver.jsonl` guarda la fecha, el motivo y el
   texto de la pregunta, sin la cuenta ni el nombre de quien la hace. Se borra a
   los 60 días. Las preguntas de Juanjo no se guardan.
3. **La ayuda lo dice**, en los cinco idiomas: «Solo guardo, de forma anónima,
   las preguntas que no consigo responder, para mejorar el bot, y las borro a los
   60 días» (texto de Juanjo; «de forma anónima» y no «totalmente», porque si
   alguien escribe un dato suyo dentro de la pregunta, ese texto queda).
4. **El análisis**, a mano con Juanjo un mes después (27-11-2026), sin gasto de
   API. `/estado` dice cuántas hay guardadas.

## Validación

27-10-2026, con Claude: «¿quién habló de criar caracoles en Marte con IA?» se
marca «sin resultado»; «escríbeme un poema sobre el otoño», «fuera de alcance»;
una pregunta normal no se marca, y la marca nunca llega a la respuesta.
El mismo día, con el índice real: «Dame ideas» para un trabajo de los órganos y
«¿cómo hago una rúbrica?» empiezan diciendo qué hace el bot, siguen con lo
encontrado y se marcan «fuera de alcance»; «¿quién habló de NotebookLM para
preparar clases?» y «¿qué documentos de la biblioteca tratan de evaluación con
IA?» responden como antes, sin marca. En
`pruebas/simular_catalogo.py`, lo guardado no lleva el id ni el nombre de quien
pregunta.
