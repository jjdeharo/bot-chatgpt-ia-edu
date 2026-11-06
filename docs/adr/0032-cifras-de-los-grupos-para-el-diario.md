# 32. Cifras de los grupos para el diario

Fecha: 2026-11-06 · Estado: aceptado

## Contexto

Juanjo quiere en el Diario de IA Educativa tres círculos, uno por grupo (ChatGPT-IA-edu, Vibe Coding
Educativo y EduMedia-IAG), con los miembros de cada uno, los que están en dos a la vez, los que están en
los tres y el total de personas distintas, «informativo pero también una especie de logotipo», y que
esté al día: «el bot ia educativa también es administrador en los 3 grupos, quizás que lo haga él» (06-11-2026).

La API de bots no da la lista de miembros de un grupo, solo cuántos son. El protocolo completo de
Telegram sí: `channels.getParticipants` lo pueden usar «both users and bots», siendo administrador
(https://core.telegram.org/method/channels.getParticipants). Telegram no lista más de unos 10.000 miembros
por grupo; el mayor tiene unos 4.000.

## Decisión

- `scripts/comunidades.py` entra con el token del bot por el protocolo completo (Telethon, que el
  repositorio ya usa para `exportar.py`), sin recibir mensajes (`receive_updates=False`), para no quitarle
  ninguno a `bot.py`. Su sesión, en `datos/comunidades/bot.session`. La cuenta de Juanjo no interviene.
- Baja las tres listas, quita bots y cuentas borradas, cruza los identificadores y guarda solo las cifras
  en `datos/comunidades/AAAA-MM-DD.json`: miembros por grupo, las siete zonas y el total. Ningún nombre ni
  identificador se escribe en disco.
- Una vez por semana, desde `nas/bucle.sh` (el reloj del índice). Si falla, lo reintenta a las seis horas;
  si pasan nueve días sin cifras nuevas, avisa a Juanjo por el bot, una vez al día. Si Telegram da menos
  miembros de los que dice tener (el tope de 10.000), no guarda nada: las cifras dejarían de ser exactas.
- El diario lee la carpeta desde su contenedor (`/bot-datos`, solo lectura), copia las cifras nuevas a su
  repositorio al publicar y las dibuja (su ADR 0029).

## Validación

Prueba del 06-11-2026 con el token del bot: 4.061 personas en ChatGPT-IA-edu (Telegram anunciaba 4.066
miembros y dio 4.064), 1.827 en VCE y 787 en EduMedia-IAG; 5.210 distintas. Las zonas suman el total de
cada grupo. La segunda vuelta, con cifras de menos de una semana, no hace nada.

## Riesgos

- Si un grupo pasa de 10.000 miembros, el recuento se para y avisa; habría que contar de otra forma.
- Las cifras son las de un día de la semana: cambian a diario, y el diario dice de qué fecha son.
