# 24. Aviso a Juanjo cuando Anthropic corta por saldo o por un límite de gasto

Fecha: 2026-11-01 · Estado: aceptado

## Contexto

Cada bot lleva su propio tope mensual (`TOPE_MES_USD`) y avisa a Juanjo al llegar al 80 %. Pero
Anthropic puede cortar antes, por dos motivos que el bot no ve: que se acaben los créditos de la
organización (los del plan, que comparten todas sus claves, también las de otros proyectos) o que se
llegue al límite de gasto del espacio de trabajo en la Console. Hasta ahora ese error solo quedaba en
el registro del NAS («error al atender») y nadie se enteraba.

Juanjo pidió el aviso para él, pero no para quien pregunta (01-11-2026): «Los problemas económicos no
deben transmitirse al usuario».

## Decisión

1. **Un solo punto.** `scripts/saldo.py` crea el cliente de Claude de los dos bots (`saldo.cliente`) y
   envuelve `messages.create` y `beta.messages.create`. Así lo cubren todas las llamadas: respuestas,
   revisión de citas, fichas, documentos, resumen semanal y `/sinresolver`.
2. **Qué cuenta como corte.** Según la [documentación de errores](https://platform.claude.com/docs/en/api/errors)
   (consultada el 01-11-2026), un 400 al quedarse sin créditos o llegar a un límite de gasto, un 429 al
   llegar al tope mensual del nivel de uso y un 402 si falla la facturación. El 400 y el 429 se
   distinguen de los demás por el mensaje («credit balance», «usage limit», «spend limit», «spend cap»).
3. **Un aviso por corte.** Lo manda el propio bot a Juanjo, con la causa y el mensaje literal de
   Anthropic, y deja una marca en `datos/aviso-saldo-<credencial>`. No vuelve a avisar hasta que una
   llamada vaya bien, que borra la marca. El índice usa la credencial del Bot de IA Educativa y comparte
   su marca.
4. **A quien pregunta no se le dice nada nuevo.** El error sigue su camino de antes; el bot no menciona
   saldo ni créditos.

## Consecuencias

- Si el aviso no sale (Telegram caído), no queda marca y se intenta en la siguiente llamada fallida.
- El texto exacto de los mensajes de Anthropic no está documentado: si cambia, un corte podría pasar sin
  aviso. El 402 se reconoce por el código. Validado con pruebas sin red (`AvisoDeSaldo`) y con una
  llamada real a un modelo inexistente (404, sin gasto y sin aviso); el corte real no se ha provocado.
