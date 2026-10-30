# 11. Ayuda para enseñar a partir de lo compartido en los grupos

Fecha: 2026-10-28 · Estado: aceptado

## Contexto

Hasta ahora, si alguien pedía ideas, una actividad o una rúbrica, el bot
contestaba que eso no lo hacía y daba los mensajes que encontraba (ADR 0007:
esas peticiones se guardan como «fuera de alcance» para medir cuántas hay). Entre
las preguntas sin resolver había casos así: un profesor de FPB que quería un
trabajo sobre los órganos del cuerpo, o quien escribía solo «Probabilidad».

Juanjo preguntó si el bot podía redactar ideas, consejo o una clase con los
mensajes del grupo, y si merecía la pena por lo que cuesta. Ideas genéricas las
da gratis cualquier chat de IA; lo que solo puede dar este bot es «esto lo
compartió un compañero, y aquí está su mensaje». Por eso la condición es que
cada idea se apoye en lo que dice un mensaje y que el nombre de quien lo dijo
sea el correcto.

## Decisión

1. **Qué atiende.** Toda petición de ayuda para enseñar: ideas, consejo,
   preparar una clase, una actividad o un proyecto, una rúbrica, cómo evaluar o
   qué herramienta usar. Sigue fuera lo que es solo producir o retocar un texto
   (corregir, traducir, resumir un texto dado, redactar un examen o una carta).
2. **Quién lo hace.** Antes de buscar, una llamada mínima a Haiku (`es_ayuda`,
   unos 0,00003 USD) decide si el mensaje pide ayuda para enseñar, mirando
   también el mensaje anterior para entender un «¿y para primaria?». Si es así,
   responde Claude Sonnet 5.5 con las instrucciones `AYUDA` y el idioma de la
   conversación; si no, Haiku busca como siempre, con las mismas instrucciones
   de antes.
3. **Las citas las escribe el programa.** Sonnet marca cada fuente como
   `[[enlace]]` y no escribe nombres, fechas ni grupos; el programa añade
   «— Autor, grupo, fecha» y el enlace desde el índice (`por_enlace` en
   `buscador.py`). En las pruebas, cuando lo escribía el modelo, enlazaba otro
   mensaje del mismo hilo y ponía el nombre de otra persona.
4. **Una revisión antes de enviar.** Otra llamada a Sonnet compara cada idea
   con el texto de sus fuentes y de su hilo: la deja, cambia el enlace por el
   del mensaje que de verdad lo dice, recorta lo que no se sostiene (contexto
   añadido, citas que no están copiadas, cautelas perdidas, conclusiones del
   bot) o la quita (mensajes sin contenido o que no tratan de lo pedido). Lo
   que quita no se recoloca. Si la revisión falla, la respuesta no se envía.
6. **Una comprobación sin IA al final** (`comprobar`). Si una frase nombra a
   alguien del grupo (nombre y apellido) que no firma ninguna de sus fuentes,
   se añade como fuente su mensaje del mismo hilo; si no lo hay, la frase se
   quita. También se quita la frase que pone entre comillas lo que no está en
   sus fuentes y la que habla de «otro usuario» cuando todas son de la misma
   persona. Sonnet recibe además de forma explícita el idioma de la
   conversación.
5. **Lo del bot, aparte.** Las sugerencias propias van al final, en un bloque
   con su rótulo («Sugerencias del bot (no salen de los grupos):»), sin
   enlaces. Los rótulos que pone el programa van en el idioma de la
   conversación (ADR 0005).
7. **Sin apartado en /ayuda.** La función sigue en marcha, pero la ayuda no
   la anuncia: Juanjo quitó ese apartado el 28-10-2026.

## Alternativas descartadas

- **Una herramienta para que Haiku pasara la petición a Sonnet.** Se probó
  así primero; las 20 preguntas de búsqueda parecieron perder 1 o 2 aciertos y
  se cambió a la llamada previa. Medidas después las dos versiones a la vez, la
  diferencia era azar (producción 17 y 14; nueva 15 y 16), pero la llamada
  previa deja la búsqueda tal como estaba y decide igual de bien: de las
  peticiones de prueba, 14 de 15 van a la ayuda (la otra, «¿qué ideas se han
  compartido?», es una búsqueda y se responde como tal), ninguna de las 20
  búsquedas, ni «¿qué puedes hacer?», «tradúceme…» o «corrígeme…».

- **Seguir sin hacerlo.** Se deja sin respuesta una petición que llega y que
  el grupo puede contestar mejor que un chat genérico.
- **Haiku para redactar.** En la primera prueba atribuyó a Juanjo una
  experiencia de otro docente y mezcló sus propuestas con las citas (12 frases
  sin marcar, frente a 3 de Sonnet).
- **Haiku como revisor.** Cuesta 0,002 USD frente a unos 0,04, pero dejaba
  pasar atribuciones falsas («su escala», cuando era la AIAS de Leon Furze) y
  mensajes unidos sin relación.
- **Publicar tras la cuarta pasada** con el aviso de «comprueba el enlace»: 2
  ideas falsas de 104, con nombres de personas reales del grupo.

## Consecuencias

- Cada petición de este tipo cuesta unos 0,13 USD y tarda unos 30 segundos;
  con 100 al mes, unos 13 USD, dentro del tope del bot.
- Pueden quedar detalles inexactos dentro de ideas correctas; cada idea lleva
  su enlace debajo y el bot ya avisa de que conviene comprobarlo.
- Las búsquedas normales siguen escribiendo autor y fecha con el modelo: si se
  quiere, se les puede aplicar lo mismo que aquí.

## Evidencia

Seis pasadas con las mismas peticiones (10 en las dos primeras, 16 desde la
segunda: consejo, una clase de 50 minutos, una rúbrica, qué herramienta usar,
una en gallego y «Corrígeme este texto», que debe quedar fuera), juzgadas por
un agente aparte contra el texto de cada fuente. Informe personal de Juanjo:
`Informes/bot-chatgpt-ia-edu/2026-10-28-ideas-a-partir-de-los-mensajes.md`.

| Pasada | Ideas bien apoyadas | Ideas falsas | Autor, grupo o fecha mal | Coste por petición |
|---|---|---|---|---|
| 1.ª (Haiku / Sonnet, sin correcciones) | 77 % / 78 % | 1 / 2 | 3 / 2 | 0,007 / 0,11 USD |
| 2.ª (Sonnet, enlaces comprobados) | 88 % | 4 | 6 | 0,09 USD |
| 3.ª (citas del programa, revisión con Haiku) | 90 % | 0 | 0 | 0,09 USD |
| 4.ª (código del bot) | 89 % | 2 | 0 | 0,09 USD |
| 5.ª (revisión con Sonnet) | 91 % | 0 (3 detalles falsos) | 0 | 0,13 USD |
| 6.ª (comillas, cautelas y autor en la revisión) | 83 % | 1 (5 afirmaciones falsas) | 0 | 0,13 USD |

La sexta salió peor que la quinta con casi el mismo código: el mismo bot da
respuestas distintas cada vez, y añadir reglas a las instrucciones ya no
mejoraba. Por eso se añadió la comprobación sin IA del punto 6, y Juanjo
decidió publicarlo aunque no sea perfecto («quiero esta funcionalidad, aunque
no vaya perfecta»). Aplicada a las respuestas de la sexta pasada, quita las dos
frases de «otro usuario comenta…» sin fuente y, en la de Qwen, añade el mensaje
de Juanjo que la respaldaba (EduMediaIAG/8195), sin falsos positivos. En una
prueba real con cuatro peticiones quitó dos frases con comillas que no estaban en
las fuentes, y la respuesta en gallego salió en gallego.
