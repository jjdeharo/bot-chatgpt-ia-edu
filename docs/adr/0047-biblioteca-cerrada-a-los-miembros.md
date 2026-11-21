# 47. Biblioteca digital cerrada a los miembros

Fecha: 2026-11-21 · Estado: aceptado

## Contexto

Algunos miembros publicaban directamente en el tema «Biblioteca digital» de ChatGPT-IA-edu, sin pasar por el bot. Así entraban publicaciones de LinkedIn en lugar de documentos: un anuncio de un libro, un análisis personal y el anuncio de una revista de pago. Esas publicaciones no tenían ficha y no se comprobaba su licencia ni si ya estaban en la biblioteca.

## Decisión

- El tema está cerrado: los miembros pueden leerlo y buscar en él, pero no escribir. Solo publican los administradores, entre ellos el bot.
- El bot tiene el permiso de gestionar temas, porque Telegram no deja escribir en un tema cerrado a un administrador sin ese permiso. Conserva además los permisos que ya tenía: borrar mensajes, expulsar e invitar.
- El mensaje fijado del tema dice que solo publica el bot, cómo mandarle un documento (el archivo o su enlace oficial) y que los libros y documentos se recomiendan o se comentan en «General».

## Evidencia y validación

- La [documentación de los foros de Telegram](https://core.telegram.org/api/forum) explica que un tema cerrado no admite mensajes nuevos.
- El 21-11-2026, con el tema cerrado, el bot recibió `TOPIC_CLOSED` al intentar escribir. Con el permiso de gestionar temas, el mensaje de prueba se publicó sin notificación y se borró al momento.
