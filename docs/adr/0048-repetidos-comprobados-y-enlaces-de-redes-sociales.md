# 48. Repetidos comprobados por el título y enlaces de redes sociales

Fecha: 2026-11-21 · Estado: aceptado

## Contexto

- El 21-11-2026, la Biblioteca digital rechazó como repetido el «Manual urgente sobre IA en el aula» (Ferrarelli y Corvalán, CESDi-UNSAM, 2026). Lo identificó con una guía de 2024 que no tenía nada en común con él. Al repetir la prueba eligió otro candidato distinto, también equivocado. Ninguno de los seis candidatos de la búsqueda por similitud era el manual. Aun así, Claude Haiku, con esfuerzo bajo, dio uno por el mismo documento.
- Algunos miembros publicaban en el tema enlaces de LinkedIn, en lugar del documento (ADR 0047). Una publicación de una red social anuncia o comenta un documento, pero no es el documento. Además, esas redes no dejan descargarlo sin cuenta.

## Decisión

- La revisión devuelve también el título del documento nuevo y el del candidato repetido, copiados de sus textos. Un repetido solo vale si el título del candidato está en su propio texto y si los dos títulos comparten al menos dos tercios de las palabras del más corto y la mitad de las del más largo. La comparación no distingue mayúsculas ni tildes. Si no se cumple, el documento sigue como nuevo y el registro anota el repetido descartado. La comprobación por dirección y por huella del PDF (ADR 0045) no cambia.
- Un enlace de LinkedIn, X, Facebook, Instagram, Threads, TikTok o Bluesky que se manda a la Biblioteca recibe una respuesta en el idioma de la persona. La respuesta le explica que es una publicación y le pide el PDF o el enlace oficial del documento.

## Evidencia y validación

- Caso original: con el PDF del manual, la revisión en el NAS devolvió `repetido: 6` (`https://t.me/ChatGPTedu/21753/21864`, «Inteligencia Artificial en la Educación. Una guía práctica para profesores»). En el primer intento había devuelto `21758`, el mismo libro publicado otra vez.
- `pruebas/test_documento_web.py` comprueba tres casos de títulos: distintos, iguales aunque cambien mayúsculas y tildes, y un título del candidato que no aparece en su texto. Comprueba también que `revisar` anula un repetido que el título no respalda y mantiene el que sí. Para las redes, comprueba las direcciones de cada red y que no se confundan con dominios parecidos.

## Riesgos

- Un documento repetido con un título muy distinto en cada copia, por ejemplo una traducción, ya no se detectaría por similitud. En ese caso se publicaría dos veces, que es un error más fácil de corregir que dejar fuera un documento nuevo.
