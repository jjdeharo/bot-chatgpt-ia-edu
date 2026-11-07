# 34. El mensaje citado en privado y los avisos de comentarios del diario

Fecha: 2026-11-07 · Estado: aceptado

## Contexto

Desde el 07-11-2026, el Diario de IA Educativa tiene comentarios al pie de cada pieza (ADR 0030 del
repositorio del diario), y una acción de GitHub avisa de cada comentario nuevo a Juanjo de Haro y a Raül
Torres con el token de este bot. El bot no sabía que esos avisos existían ni los veía: los manda otro
programa. Y en privado no leía el mensaje que se cita al responder (solo en los grupos, para las
preguntas que lleva, ADR 0023): si alguien citaba el aviso y preguntaba por él, el bot solo veía la
pregunta y podía negar haberlo enviado o inventarse una explicación.

## Decisión

- **El mensaje citado, delante de la pregunta**: en privado, si se responde citando un mensaje, va a
  Claude delante de la pregunta, como «[Responde citando un mensaje tuyo / suyo / un mensaje: «…»]»,
  con los enlaces que el texto lleva escondidos (entidades `text_link`, con sus posiciones en UTF-16) y
  como mucho 2.000 caracteres (`LARGO_CITADO`). Sirve para cualquier mensaje citado, no solo para los
  avisos. No pasa al historial de la conversación: allí queda solo la pregunta.
- **Los comentarios del diario, en las instrucciones**: cómo se comenta (cuenta de GitHub), cómo se
  responde, edita, borra u oculta un comentario, y que el bot avisa por privado a Juanjo y a Raül de cada
  comentario nuevo mediante un programa que usa su nombre, sin leerlos ni moderarlos él.

## Alternativas descartadas

- **Herramienta para leer los comentarios de cada pieza** (Discussions de GitHub): aplazada hasta que
  haya comentarios de verdad.

## Validación

`pruebas/test_citado.py`: el aviso real de un comentario con sus dos enlaces, posiciones con un emoji
delante, quién escribió el citado y el recorte de un citado largo.
