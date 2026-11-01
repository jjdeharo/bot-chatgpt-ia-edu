# 23. Preguntar en el grupo lo que el bot no resuelve, y preguntas sin resolver por temas

Fecha: 2026-11-01 · Estado: aceptado

## Contexto

El análisis competitivo del 01-11-2026 (informe para Juanjo, fuera del repositorio) comparó los dos bots
con los servicios externos parecidos. Dos ideas de otros servicios encajaban sin cambiar lo que son los
bots, y Juanjo pidió las dos («haz las 2 mejoras»):

- Inkeep pone bajo cada respuesta de su bot de Discord «Ask for help», que pasa la duda a personas. En
  los bots, cuando no encontraban la respuesta, la persona se quedaba ahí: tenía que ir al grupo por su
  cuenta.
- kapa.ai agrupa por temas las respuestas inseguras («Coverage Gaps») y propone qué documentar. Los
  bots ya guardaban las preguntas sin resolver (ADR 0007), pero la revisión con Juanjo partía de la
  lista sin agrupar.

## Decisión

### Preguntar en el grupo

1. **Cuándo se ofrece.** El botón «Preguntar en el grupo» va bajo la respuesta cuando el bot no ha
   encontrado nada (motivos «sin resultado» y «respuesta vacía»). En cualquier otra respuesta valorable
   aparece al pulsar 👎, en lugar de los botones. Lo que queda fuera del alcance del bot (pedirle que
   redacte) no lleva botones y no se ofrece: no es una duda para el grupo.
2. **Nada se publica sin verlo.** El botón enseña el mensaje tal como quedará en el grupo y la persona
   elige «Publicar en …» o «Cancelar». Cada botón lleva la clave de esa pregunta (como los borradores,
   ADR 0019), así que uno antiguo no publica otra cosa; la pertenencia al grupo se vuelve a comprobar
   al publicar. Cada pregunta se lleva una sola vez.
3. **El mensaje del grupo**, en castellano, que es el idioma de los cuatro grupos: dice en la primera
   línea, en negrita, que es una pregunta de esa persona que el bot no ha sabido responder, con su
   nombre enlazado a su perfil (tercera persona, como pide Juanjo para lo que un programa publica en
   nombre de alguien), lo que el bot ha mirado, la pregunta en una cita y que quien responda a ese mensaje
   hará llegar su respuesta por privado, dicho de forma que se entienda que se contesta en el grupo (1.3.1, a petición de Juanjo). Las imágenes de la consulta van con ella (como foto o álbum); la
   pregunta se recorta a 1.500 caracteres, o a 700 con imágenes, porque el pie de foto admite 1.024.
4. **Las respuestas llegan a quien preguntó.** Como administradores, los bots reciben todos los mensajes
   del grupo. Si uno responde a una pregunta que llevó el bot, el bot manda a quien la hizo, por privado y
   en su idioma, quién ha respondido, el principio de la respuesta y su enlace. Para eso guarda, durante 7
   días, qué mensaje del grupo es de quién (`datos/preguntas-grupo.json` y `preguntas-grupo-karla.json`:
   cuenta, idioma, grupo y momento). La vista previa lo dice antes de publicar. Una respuesta a esas
   preguntas no recibe el «escríbeme por privado», aunque lleve interrogación.
5. **Se puede retirar.** Tras publicar, un botón «Quitarla del grupo», firmado con la cuenta de quien la
   llevó (ADR 0020), la borra durante 48 horas, lo que Telegram deja a un bot.
6. **Topes.** Tres preguntas por persona y día (en memoria; un reinicio lo pone a cero).
7. **Dónde.** En el grupo de Karla (eXeLearning) y, en el Bot de IA Educativa, en ChatGPT-IA-edu y Vibe
   Coding Educativo; si la persona está en los dos, elige. EduMedia-IAG queda fuera de entrada
   (`GRUPOS_PREGUNTAR`): es el grupo de Raül Torres y el bot no publica nada allí.
8. **Sin aviso a Juanjo.** Lo que se publica en un grupo que administra ya lo ve; avisarle de cada pregunta
   sería ruido.

### Preguntas sin resolver por temas

1. **`/sinresolver`**, solo para Juanjo, en los dos bots (y `bot.py sinresolver` o `karla.py sinresolver`
   desde la terminal del NAS, para la revisión con un agente). Agrupa las preguntas sin resolver de los
   últimos 60 días por temas: de cada tema, cuántas preguntas, qué buscaba la gente, qué lo resolvería y
   un ejemplo literal.
2. **Con Sonnet 5.5 y salida estructurada** (`output_config.format`, el mismo mecanismo que la revisión
   de la ayuda para enseñar): Sonnet 5.5 no admite obligar a usar una herramienta. El modelo devuelve los
   números de las preguntas de cada tema y el programa pone el texto literal, así que los ejemplos no se
   inventan; lo que el modelo no coloca va a «Sin tema», a la vista.
3. **«Qué lo resolvería»**, de una lista propia de cada bot. Karla: añadir una receta probada, está
   documentado pero no lo encuentra, falta en la documentación oficial, fallo o carencia del programa,
   completar lo que sabe de sí misma, fuera de su ámbito. Bot de IA Educativa: nadie lo ha tratado en los
   grupos, está en los grupos pero no lo encuentra, función que no tiene, completar lo que sabe de sí
   mismo, fuera de su ámbito.
4. **Sin gasto cuando no hace falta.** Las que fallaron por un error del programa no se mandan (no dicen
   qué falta, sino que algo se rompió): se cuentan aparte. Con menos de 5 preguntas no se llama a la IA y
   se enseñan tal cual. El gasto de la orden se apunta en el del bot; el de la terminal, no.
5. `/estado` lo recuerda al final de la línea de sin resolver: «Por temas: /sinresolver».

## Alternativas descartadas

- **Responder en el grupo a quien menciona al bot**, como Quickchat o Chat Data: los bots atienden solo
  por privado desde el 24-10-2026 (ADR 0001). Aquí el bot publica en el grupo solo cuando la persona lo
  pide y lo confirma.
- **Publicar sin vista previa**, con un solo botón: más rápido, pero la persona no vería que sale su nombre
  ni qué texto exacto se publica.
- **Agrupar por temas de forma automática cada mes y mandárselo a Juanjo**: la revisión ya tiene fecha con
  él y un aviso periódico sería una interrupción más. Se pide cuando hace falta.
- **Agrupar con Haiku**: más barato, pero el gasto con Sonnet es de un céntimo por análisis y la agrupación
  es lo que decide qué se mejora.

## Consecuencias

- Lo que el bot no resuelve llega a quien puede resolverlo, y la respuesta del grupo entra en el índice a
  los 15 minutos: la próxima vez el bot la encuentra.
- Los bots publican en el grupo algo más que el resumen de los viernes y «¡Comparte tu App!», siempre a
  petición de una persona y con su nombre.
- Se guarda la cuenta de quien lleva una pregunta durante 7 días, con su conocimiento. Ese archivo no va en
  la copia diaria: si se pierde, solo se pierden los avisos de las respuestas pendientes.
- La revisión de las preguntas sin resolver (ADR 0007) parte de la lista agrupada.

## Evidencia

- Telegram: un bot solo puede borrar sus mensajes durante 48 horas sin permiso de borrar
  (`deleteMessage`, Bot API); como administrador recibe todos los mensajes del grupo (ADR 0001).
- Anthropic: `tool_choice` de tipo «tool» devuelve con Sonnet 5.5 el error «tool_choice: type "tool" and
  "any" are not supported for this model» (prueba del 01-11-2026); la salida estructurada sí funciona.

## Riesgos y limitaciones

- Solo se avisan las respuestas directas al mensaje del bot; una respuesta a otra respuesta no llega.
- Con un álbum de varias fotos, la respuesta tiene que ir a la primera foto, la que lleva el texto, o a
  cualquiera de las otras: se guardan todas.
- El tope diario está en memoria.

## Validación

- 01-11-2026, `pruebas/test_revision.py` (63 pruebas, sin red): el botón sale con «sin resultado» y no en
  una respuesta normal; con 👎 queda «Preguntar en el grupo»; la vista previa no publica nada y ofrece los
  grupos de la persona; publicar guarda quién la llevó, ofrece quitarla y no deja publicarla dos veces; un
  botón antiguo o de otro grupo no publica; el tope de tres al día; con una imagen va como foto con un pie
  de menos de 1.024 caracteres; la respuesta de otro en el grupo llega en el idioma de quien preguntó, la
  suya no y la respuesta a otro mensaje del bot sigue como siempre; lo guardado caduca a los 7 días; solo
  quien la llevó la puede quitar; EduMedia-IAG no es destino; Karla usa sus textos. La agrupación por temas
  no gasta con menos de 5 preguntas, no manda las de error, usa las preguntas literales y deja a la vista
  las que el modelo no coloca.
- 01-11-2026, Sonnet 5.5 de verdad sobre 13 preguntas de prueba al estilo del grupo eXeLearning (12 y un
  error): seis temas razonables (temporizador en cuestionarios, fuentes en ePub, Google Classroom,
  imágenes perdidas al importar proyectos de la 2.9, pedir contenidos, privacidad), todas colocadas, en 7
  segundos y por 0,01 USD.
