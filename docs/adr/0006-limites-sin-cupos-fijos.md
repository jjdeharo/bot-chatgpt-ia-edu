# 6. Límites sin cupos fijos: freno por ritmo de gasto y contra el uso automático

Fecha: 2026-10-27 · Estado: aceptado

## Contexto

El bot tenía cupos fijos por persona y día (20 preguntas, 3 documentos, 5
recursos) y los anunciaba en la ayuda. Juanjo: «no me gusta que la gente vea
un limite, salvo momentos puntuales yo creo que siempre iremos sobrados».

Uso real del 24 al 27-10-2026: 33 preguntas (13 de Juanjo). Quien más preguntó
en un día hizo 9. A unos 0,003 USD por pregunta, el tope mensual del bot da
para miles de preguntas al mes.

El riesgo que sí hay que cubrir es el uso automático: un programa que
pregunte sin parar podría gastar el presupuesto del mes en un día.

## Decisión

1. **Sin cupos a la vista**: la ayuda ya no los menciona y en condiciones
   normales no se aplican.
2. **Freno por ritmo de gasto.** Cada día se puede gastar lo que queda del
   tope del mes dividido entre los días que faltan. Si un día se gasta más del doble, entran los cupos por persona
   de antes hasta el día siguiente, y Juanjo recibe un aviso. `/estado` dice
   cuánto se lleva gastado hoy y a partir de cuánto entrarían.
3. **Freno contra el uso automático**, siempre activo: más de 30 consultas de
   pago en una hora de la misma persona (preguntas, documentos, fichas,
   cambios y códigos) y el bot le pide que siga dentro de un rato, sin hablar
   de límites. Juanjo queda fuera.
4. Siguen el tope mensual propio (`TOPE_MES_USD`), el del espacio de trabajo en
   la consola de Claude y el aviso a Juanjo al 80 %.

## Consecuencias

- El umbral del freno crece hacia final de mes si sobra presupuesto. Es lo buscado: no
  frenar mientras haya margen; el tope mensual sigue por encima.
- Las cifras (el doble y 30 por hora) son prudentes; se ajustarán con lo que
  muestre `/estado`.

## Validación

`pruebas/simular_catalogo.py`, 27-10-2026: la ayuda no anuncia cupos; sin
freno, una persona pasa de las 20 preguntas; con el freno activo, entra el
cupo; la consulta número 31 en una hora recibe el mensaje de pausa.

## Avisos en los grupos (27-10-2026)

En los grupos, el bot responde que se le escriba por privado cuando alguien lo
menciona o le contesta. Sin límite, quien lo mencionara una y otra vez llenaría
el grupo de avisos iguales. Juanjo preguntó si un usuario malicioso podía
provocarlo, y se puso un freno en los dos bots (`Bot.solo_privado`):

- a cada persona, como mucho un aviso cada 30 minutos;
- en todo el grupo, como mucho 3 avisos cada 10 minutos.

Pasado el freno, el bot calla. El aviso es un texto fijo, sin IA ni gasto.
Probado con casos simulados: veinte menciones de una persona dan un aviso, y
diez personas seguidas dan tres.

### Comandos mandados al grupo (29-10-2026)

Cuatro miembros de VCE mandaron `/misrecursos` al grupo en dos días. Un
`/comando` escrito en un mensaje de grupo sale como enlace, y al pulsarlo
Telegram lo envía al grupo, no al bot; los anuncios del repositorio lo
llevaban escrito así. El bot, que como administrador recibe esos mensajes, no
los contestaba porque no lo mencionan.

Desde ese día el bot trata como dirigido a él un mensaje que empieza por uno
de sus comandos (`Bot.comando_en_grupo`), salvo si va a otro bot
(`/buscar@otro_bot`). Contesta con el mismo freno y con un enlace que abre el
privado ya en ese comando: `https://t.me/IAEducativa_bot?start=misrecursos`.
Telegram manda entonces `/start misrecursos`, y el bot lo atiende como
`/misrecursos`; con cualquier otra cosa detrás de `/start`, la ayuda de
siempre. Ese enlace es también el que conviene poner en los anuncios en lugar
del `/comando`. Texto fijo, sin IA ni gasto. Probado con casos simulados:
comando solo, con el nombre del bot, con el de otro bot, dentro de una frase
y `/start` con y sin comando detrás.
