# 51. El gorro de Papá Noel en las vacaciones de Navidad

Fecha: 2026-11-21 · Estado: aceptado

## Contexto

Otros años Juanjo ponía a mano una foto con gorro de Papá Noel en ChatGPT-IA-edu y Vibe Coding Educativo: el
22-12-2025 la puso y el 7-1-2026 volvió a la de siempre (las dos siguen en el historial de fotos de cada grupo).
El 21-11-2026 pidió lo mismo, también para los bots y para Tiza y Algoritmo en el diario, desde que empiezan las
vacaciones de Navidad hasta Reyes. Aprobó las imágenes ese día y pidió mejorar la de Karla.

## Decisión

- **Fechas**: del 22 de diciembre al 6 de enero, ambos incluidos (las vacaciones escolares de Cataluña del curso
  2026-27 son del 22-12 al 7-1, Orden EDF/66/2026); el 7 de enero vuelven las de siempre. Se repite cada año.
- **Qué cambia**: las fotos del Bot de IA Educativa y de Karla bot, y las de ChatGPT-IA-edu y Vibe Coding
  Educativo (las del año pasado). EduMedia-IAG, solo si lo aprueba Raül Torres, su creador; el grupo de
  eXeLearning lleva el logo oficial del proyecto y no se toca.
- **Quién lo hace**: `scripts/navidad.py`, en cada pasada de `nas/bucle.sh`. Guarda en
  `datos/navidad-estado.json` cómo quedó cada foto y solo actúa al cambiar; si una falla, la reintenta en la
  pasada siguiente sin volver a subir las demás, para no repetir el aviso de «foto cambiada» en los grupos.
  Juanjo recibe del bot, por privado, lo que ha cambiado y, una vez al día como mucho, lo que no.
- **Cómo**: los bots, con `setMyProfilePhoto` de la API de bots. Los grupos, con la cuenta de Juanjo (la sesión
  de `exportar.py`), como lo hacía él: el bot no tiene en esos dos grupos el permiso de cambiar la información.
- **Los dibujos**: un gorro en SVG (`imagen/navidad/gorro.py`) sobre el original del bot; el de Karla, con
  volumen y sombra (`gorro3d.py`), porque el plano se veía pegado sobre su dibujo en 3D (Juanjo: «el de karla
  intenta arreglarlo un poco»).

## Evidencia y validación

- `navidad.py --fecha F --simular` con el 21-11, 21-12, 22-12, 6-1 y 7-1: pone el gorro solo del 22-12 al 6-1.
- Las dos llamadas de los bots se probaron con las fotos de siempre. `setMyProfilePhoto` **sustituye** la foto
  (el bot sigue con una) y `removeMyProfilePhoto` la quita sin volver a la anterior: el 21-11, al deshacer la
  prueba con esta última, los dos bots se quedaron sin foto aproximadamente un minuto hasta que se les volvió a poner. Para
  volver a la de siempre, se pone la de siempre; nunca `removeMyProfilePhoto`.
- La cuenta de Juanjo es creadora de los dos grupos (`change_info`), comprobado con la sesión del contenedor.
  El cambio de foto de los grupos no se probó de verdad, para no dejar un aviso en grupos de cientos de
  personas: se verá el 22-12, y si falla avisa el bot.
