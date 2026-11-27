# 54. El aviso del diario en dos mensajes

Fecha: 2026-11-27 · Estado: aceptado

## Contexto

Desde el ADR 0037, el aviso de cada mañana en los tres grupos es un solo mensaje: la portada del número como vista
previa grande, encima del texto. Ese ADR descartó partirlo porque daba por hecho que, con la imagen como vista
previa, el texto ocupaba todo el ancho del globo. No es así: el 27-11-2026, Juanjo vio que Telegram ajusta el globo
al ancho de la vista previa y, como la portada es alta (900 × 1607 píxeles), el texto queda estrecho. Propuso
partirlo en dos mensajes, uno con el enlace y otro con el texto, y dejó al agente decidir el orden.

## Decisión

- **Primero la portada y después el texto.**
  - El primer mensaje es el enlace de la página del grupo, con la portada como vista previa grande (si no está a
    tiempo, la imagen de la página, como antes). Sale **sin sonido** (`disable_notification`).
  - El segundo es el texto de siempre (número, fecha, saludo, puntos y 👉 enlace), **sin vista previa**, y es el
    que suena.
- Así, el aviso se ve igual que antes, con la portada arriba, pero el texto ocupa todo el ancho. Cada miembro
  recibe un aviso, no dos, que era la objeción del ADR 0037. La lista de chats muestra el último mensaje del grupo,
  que es el texto y no la dirección. Y el texto se puede abrir o reenviar sin el mensaje de la portada.
- `<fecha>.publicado.json` apunta, además de los grupos terminados, el número de cada mensaje enviado
  (`mensajes`: grupo → números, en orden).
  - Si el texto falla tras la portada, la vuelta siguiente manda solo lo que faltaba y no repite la portada.
  - Un aviso ya enviado se corrige con `editMessageText` sobre esos números. Los dos mensajes son de texto, así
    que se pueden editar los dos.
- Un aviso en el formato anterior (texto hecho) sigue saliendo en un solo mensaje.

## Alternativas descartadas

- **Primero el texto y después el enlace**: la portada, que es lo llamativo, quedaría debajo. Además, en la lista
  de chats se vería la dirección y no el saludo.
- **Recortar la portada a una imagen apaisada**: el globo sería ancho, pero la portada completa fue lo que gustó en
  el ADR 0037.

## Consecuencias

- Un aviso son dos mensajes seguidos en el tema General. Entre los dos no puede colarse otro porque salen uno tras
  otro, en la misma vuelta.
- Corregir un aviso ya enviado puede requerir editar los dos mensajes (el enlace de la portada o el texto).

## Evidencia

- `pruebas/test_diario_grupos.py`: el formato de los dos mensajes (`test_formato_nuevo_con_puntos`) y el envío con
  un fallo a mitad (`test_publica_en_dos_mensajes_y_sigue_por_el_que_falto`).

## Validación

- Las pruebas del bot y `ruff check --select E9,F`, en verde.
- Un aviso de prueba, el del día, mandado por privado a Juanjo con el bot antes de desplegar.
