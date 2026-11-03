# 27. Nombre de autor de los recursos del repositorio

Fecha: 2026-11-03 · Estado: aceptado

## Contexto

Al dar de alta un recurso del repositorio de Vibe Coding Educativo, el bot pone como autor el nombre
de Telegram de la persona (nombre y apellido de su perfil). Hay perfiles con un nombre que no sirve
para firmar: una persona que firma en Telegram como «D» saldría como «D» en el repositorio. Podía
cambiarlo al revisar la ficha («el autor es…»), pero el bot no se lo pedía ni lo recordaba: en el
recurso siguiente volvía a salir «D». En la hoja del 29-10-2026 el nombre más corto es «jc», con tres
recursos, que entraron por el formulario antiguo.

## Decisión

- El bot guarda, junto a la cuenta de Telegram, el nombre con el que la persona firma sus recursos
  (`nombres` en `datos/catalogo.json`, junto a los dueños y los correos). Es el mismo nombre que ya se
  publica en el repositorio.
- En un alta, si hay nombre guardado, la ficha lo lleva. Si no lo hay y el nombre de Telegram tiene
  menos de tres letras, el bot lo pide antes de enseñar la ficha, una sola vez.
- Si el autor de una ficha cambia (al pedirlo la primera vez o con «Cambiar algo», en un alta o en un
  recurso ya publicado), ese nombre pasa a ser el guardado y **se cambia en todos sus recursos**,
  también los del formulario antiguo que ha recuperado con su correo, para que salgan todos igual
  (Juanjo, 03-11-2026: «si se cambia el nombre se cambia para todas sus fichas»). Antes de publicar,
  la ficha avisa de cuántos recursos más cambiarán; después, el bot dice cuántos ha cambiado.
- La hoja cambia solo la columna del autor (`Hoja.poner_autor`), como ya hacía con la licencia.

## Consecuencias

- Quien firma con un nombre de Telegram corto responde una pregunta más en su primer alta, y nada más.
- Un recurso firmado a varias manos («Ana Pérez y Luis Gil») haría que ese nombre pasara a todos sus
  recursos: el aviso previo lo deja ver antes de publicar, y se arregla volviendo a cambiar el autor.
- El nombre guardado viaja en la copia diaria de `catalogo.json` (README, «Copias»).
- Pruebas: `pruebas/test_nombre_autor.py`, en GitHub con cada cambio.
