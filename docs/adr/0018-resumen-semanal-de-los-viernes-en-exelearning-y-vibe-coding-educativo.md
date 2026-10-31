# 18. Resumen semanal de los viernes en eXeLearning y Vibe Coding Educativo

Fecha: 2026-10-31 · Estado: aceptado

## Contexto

Los bots solo atienden por privado. Quien entra nuevo en un grupo no sabe que existen, y con el
tiempo los demás se olvidan. Juanjo quiere que se recuerden de vez en cuando, pero con algo útil
para el grupo: nada de anuncios fijos ni de un texto idéntico cada vez.

## Decisión

Cada viernes a las 18:00 (hora de Madrid), un mensaje en el tema General del grupo (`scripts/resumen_semanal.py`):

- **eXeLearning, Karla bot**: un resumen corto de la semana, con como mucho 3 novedades
  (versiones, manuales, complementos) y, hasta 6 elementos, las dudas resueltas más útiles,
  cada una con el enlace al mensaje. Lo elige Claude Sonnet 5.5 leyendo los mensajes de la
  semana, con respuesta en un esquema JSON. El mensaje entero no pasa de 150 palabras, lo que
  cabe en una pantalla de móvil; si se pasa, el programa quita lo último de la lista más larga.
- **Vibe Coding Educativo, Bot de IA Educativa**: las aplicaciones que han entrado esa semana en
  el repositorio, con su ficha y su autor, sacadas de la hoja. Sin IA.

La entradilla y el cierre rotan cada semana (4 y 6 variantes) y el cierre dice en pocas
palabras todo lo que hace el bot. Si la semana no tiene nada, no se publica. Lo publica cada bot
desde su bucle (`Bot.resumen_si_toca`), sin cron aparte, y lo deja apuntado en
`datos/<grupo>/resumen-semanal.json` para no repetirlo. Si el bot estaba parado, publica en las
6 horas siguientes; después, esa semana se queda sin resumen.

## Alternativas descartadas

- **Bienvenida a quien entra**: AntiUserbotsBot ya les escribe al comprobar que no son bots, y dos
  bots serían demasiado ruido.
- **Recordatorio fijo cada pocas semanas** diciendo lo que hace el bot: es publicidad y no aporta.
- **Solo las dudas resueltas en eXeLearning**: una versión nueva o un manual merecen aparecer.
- **El tema «Resumen semanal» de Vibe Coding Educativo**, donde sale el boletín de los lunes: lo ve
  menos gente.
- **Texto redactado por la IA cada semana**: variantes escritas de antemano son más baratas y
  quedan revisadas.
- **ChatGPT-IA-edu y EduMedia-IAG**: de momento no; EduMedia-IAG es de Raül Torres.

## Consecuencias

Karla gasta unos 0,02 USD por semana, apuntados en su contabilidad. El de Vibe Coding Educativo
no cuesta nada.

## Evidencia

- La «Marca temporal» de la hoja es la fecha de alta y no cambia al modificar un recurso:
  `vce-app_edu/api.gs`, acción `modificar` («conserva la fecha de alta»). Se guarda en UTC.
- Sonnet 5.5 rechaza forzar una herramienta (`tool_choice` de tipo `tool`: «not supported for
  this model», 31-10-2026); por eso la respuesta va con `output_config.format` y un esquema JSON.

## Riesgos y limitaciones

- La selección depende de Claude: en la primera prueba se dejó una pregunta de información
  contestada con enlaces y se amplió la instrucción. El programa quita lo que no puede situar
  (un id que no es de la semana, una respuesta anterior a la pregunta o de la misma persona).
- Los mensajes de la semana salen de `datos/exelearning/mensajes.jsonl`, que el índice pone al día
  cada 15 minutos: lo de los últimos minutos antes de las 18:00 puede no entrar.

## Validación

Probado el 31-10-2026 con las semanas del 16 al 23 y del 23 al 30 de octubre, comparando a mano
con los mensajes de cada semana, y con horas simuladas para la ventana del viernes (17:00 UTC en
noviembre). Los dos primeros resúmenes se publicaron a mano ese día con `--publicar`, a petición de
Juanjo.
