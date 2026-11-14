# 38. Recomendaciones al día y sin promesas

Fecha: 2026-11-14 · Estado: aceptado

## Contexto

En la revisión de las preguntas sin resolver del 14-11-2026 (ADR 0007), a «Busco
una manera de conectar NotebookLM con ChatGPT» el bot respondió bien que en los
grupos no hay una conexión directa, pero con dos fallos:

- Recomendó, como alternativa, poner cuadernos de NotebookLM como fuente de un
  Gem de Gemini, con mensajes de principios de 2026, sin decir que Google
  sustituye los Gems por Skills. Los grupos ya lo habían contado (ChatGPT-IA-edu,
  09-08-2026) y el Diario de IA Educativa también (n.º 10, 11-11-2026), pero el bot
  no lo buscó.
- Ofreció «preguntar a Ignasi por su método», algo que no puede hacer. Las
  instrucciones ya decían que, como mucho, ofreciera buscar en un grupo o en unas
  fechas.

## Decisión

Dos reglas nuevas en las instrucciones del Bot de IA Educativa
(`scripts/consultar.py`), junto a «Responde solo con lo que encuentres»:

1. **Recomendaciones al día.** Antes de responder, por cada herramienta o
   servicio que recomiende o explique cómo usar (un Gem, un GPT, NotebookLM, una
   app), hace una búsqueda más en los grupos y otra en el diario, con su nombre y
   palabras como «retira», «desaparece», «sustituye» o «cambia de nombre». Si se
   ha dicho que cambia o desaparece, lo dice junto a la recomendación, con su
   fecha y su enlace.
2. **Sin promesas.** No ofrece nada más que buscar en un grupo o en unas fechas,
   o preguntar qué más sabe quien pregunta: ni escribir o preguntar a otras
   personas ni nada que no esté en «Sobre ti».

Karla no cambia: ya tiene en cuenta si un mensaje es anterior a la última
versión de eXeLearning, que es lo que allí deja anticuado un consejo.

## Alternativas descartadas

- **Una regla genérica** («si recomiendas algo de mensajes de hace meses, mira si
  ha cambiado»): probada con dos preguntas, el bot no hizo la búsqueda y siguió
  recomendando los Gems sin aviso. Hizo falta decirle con qué herramientas y qué
  palabras buscar.
- **Una lista mantenida a mano de productos retirados** en las instrucciones:
  habría que tenerla al día, y el bot debe responder solo con lo que se ha dicho
  en los grupos y en el diario.

## Consecuencias

- Las respuestas que recomiendan una herramienta hacen una o dos búsquedas más:
  la de NotebookLM y ChatGPT pasó de 0,0026 a 0,0068 USD. Las de recursos del
  repositorio no cambian de forma apreciable (5 → 6 búsquedas en la prueba).
- El bot cuenta lo que dicen los grupos y el diario, aunque no coincida con la
  fuente oficial: sobre la fecha del fin de los Gems, los mensajes dan fechas
  distintas.

## Evidencia

Las mismas preguntas, con la versión anterior y con la nueva, en el contenedor
del NAS el 14-11-2026 (`python consultar.py "…"`):

- «Busco una manera de conectar notebooklm con ChatGPT»: antes recomendaba el Gem
  sin aviso y ofrecía preguntar a Ignasi; ahora dice que NotebookLM se llama
  Gemini Notebook y que Google sustituye los Gems por Skills, con los enlaces del
  diario, y no ofrece nada que no pueda hacer.
- «¿Cómo hago un asistente con mis apuntes en Gemini?»: con la regla genérica,
  explicaba los Gems sin aviso; con la nueva, empieza avisando del paso a
  Skills, con los mensajes de EduMedia-IAG.

## Riesgos y limitaciones

Es una instrucción al modelo, no una comprobación del programa: puede saltársela
alguna vez. Se vigila en las revisiones de las preguntas sin resolver.

## Validación

- Las 176 pruebas del bot y `ruff check --select E9,F`, en verde.
- Las tres preguntas de arriba, repetidas en el contenedor del NAS con la versión
  nueva (14-11-2026).
