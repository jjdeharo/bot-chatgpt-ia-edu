# 45. Duplicados en la Biblioteca digital

Fecha: 2026-11-18 · Estado: aceptado

## Contexto

El mismo preprint de arXiv se publicó dos veces entre pasadas del índice de Telegram, a las 12:03 y las 12:13. La comprobación de repetidos del ADR 0002 solo consultaba los candidatos que ya estaban en el índice. El repositorio de Vibe Coding Educativo ya consulta la URL de la hoja y su API comprueba la misma URL bajo un cerrojo al dar de alta la fila.

## Decisión

- Antes de generar una ficha, se comparan las direcciones del documento y la huella SHA-256 del PDF con las publicaciones del propio bot. Para las publicaciones anteriores se consultan las direcciones de las referencias y aportaciones del historial ya descargado del tema Biblioteca digital. Los enlaces que aparecen solo en comentarios se ignoran. La búsqueda por similitud sigue siendo complementaria.
- En arXiv, las direcciones de la ficha, el PDF y el DOI se comparan por su identificador. Si se conoce la versión, se usa la versión concreta. Una revisión distinta conserva su identidad.
- Antes de publicar, se comprueba otra vez dentro del mismo cerrojo que protege el envío. Al aceptar Telegram el documento, o el mensaje de ficha si sale sin archivo, el bot guarda el enlace y sus identificadores, incluido el del PDF, en el mismo estado que ya se respalda. Así los puede comparar desde la siguiente solicitud y después de reiniciar. Si falla la ficha tras enviarse el PDF, el reintento del mismo borrador utiliza ese mensaje.
- La acción «Quitarlo de la Biblioteca» retira también el registro inmediato tras borrar los mensajes. Una retirada directa se refleja al completarse una exportación íntegra del grupo.

## Validación

Con el preprint 2611.20061v1, la URL directa y la ficha se refieren a una única versión y el historial devuelve el enlace de la primera aportación. Se probaron dos borradores confirmados para el mismo PDF con el índice ausente, un reintento tras un fallo parcial, la detección por huella con otra dirección y un comentario que enlaza a una versión distinta.
