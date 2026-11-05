# 30. Búsqueda en el Diario de IA Educativa

Fecha: 2026-11-05 · Estado: aceptado

## Contexto

El bot publica cada mañana el aviso del Diario de IA Educativa (ADR 0025 y 0029), pero no sabía qué
traía cada número: lo mandaba a la web. En la revisión de las preguntas sin resolver del 05-11-2026
(ADR 0007 y 0023) quedaba una del 03-11, «Me meto en el diario pero solo puedo ver el número 2»; al
repetirla, el bot contestó que no sabía por qué y dio solo el enlace del último número, sin la
hemeroteca. Juanjo propuso entonces: «quizás el diario debería añadirse a la documentacion del bot de
cada noche», y lo aprobó ese mismo día.

## Decisión

- El diario deja cada mañana, con el sitio ya subido, todo lo publicado en
  `datos/diario/hemeroteca.json` (ADR 0017 del diario): una entrada por pieza, breve, reportaje o
  editorial, con su número, el día en que salió, el texto, el mensaje original y el enlace de la
  pieza en castellano y en catalán. Se toma de ahí, donde se genera, y no de la web.
- `scripts/hemeroteca.py` lo vuelve a leer cuando cambia y busca como en el repositorio (ADR 0016):
  por significado y por palabras, con la fusión por rangos recíprocos. El significado se calcula en
  segundo plano y se guarda en `datos/diario-vectores.npz`; mientras falta, se busca por palabras.
- Herramienta `buscar_diario` (consulta, número, día en que salió); sin consulta y con número o día,
  da todo lo de ese número. El bot cita primero el mensaje original del grupo y debajo la pieza del
  diario, con su número y su día: el diario resume lo que se dijo en los grupos y no sustituye a
  los mensajes, que siguen siendo la fuente.
- Solo para preguntas sobre el diario. En la ayuda para enseñar (ADR 0011) no está: sus ideas se
  citan con el mensaje, el documento o la ficha de donde salen, que es lo que comprueba el revisor.
- «Sobre ti» da el enlace de la hemeroteca en castellano y en catalán, y ya no dice que el bot no
  ha leído el diario.
- Karla no lo tiene: el diario no trata del grupo eXeLearning.

## Alternativas descartadas

- Meter las piezas del diario en el índice de los mensajes: el bot las citaría como si fueran de los
  grupos y se duplicaría cada asunto.
- Leer la web o el RSS: no traen el mensaje original de cada pieza y serían una copia de lo generado.

## Consecuencias

- Sin gasto fijo nuevo: la búsqueda es local (SQLite FTS5 y el servicio de significado del NAS,
  ADR 0012); solo cuentan los tokens de la respuesta, como en cualquier pregunta.
- Una corrección del diario hecha durante el día llega al bot con el número siguiente.

## Riesgos y limitaciones

- Si el diario no entrega el índice una mañana, el bot sigue con el del día anterior.
- Las notas internas de la redacción no llegan al bot: no puede explicar por qué se descartó algo.

## Validación

- `pruebas/test_hemeroteca.py`: sin archivo, sin servicio de significado, por significado, todo un
  número, filtro con consulta, archivo nuevo y archivo roto.
- 05-11-2026: la pregunta del número 2 y otras sobre el diario, repetidas en el NAS con el bot 1.8.0
  (resultados en la conversación de ese día).
