# 25. Aviso diario de «Tiza y Algoritmo» en los tres grupos

Fecha: 2026-11-01 · Estado: aceptado

## Contexto

«Tiza y Algoritmo» es un diario web que cuenta a quien no está en los grupos lo que se habla en
ChatGPT-IA-edu, Vibe Coding Educativo y EduMedia-IAG (idea de Raül Torres). Sale cada mañana, con
el día anterior ya cerrado. Juanjo quiere que el bot lo anuncie cada día en los tres grupos: así el
diario se recuerda y el bot también, que era uno de sus miedos (01-11-2026: «así cada día se recuerda
y el bot no se olvida»). Propuse un aviso semanal por miedo al ruido; él prefirió el diario.

## Decisión

- El diario deja cada noche en `datos/diario/<fecha>.json` un aviso por grupo, ya redactado y
  repasado: corto, con el titular que más interesa a ese grupo y una línea de la viñeta. **El texto es
  siempre distinto** (Juanjo, 01-11-2026): lo escribe la IA del diario cada día, sin plantilla, y se
  compara con los avisos de los días anteriores para no repetir saludo, arranque ni fórmula. El bot no
  redacta nada: solo publica (`scripts/diario_grupos.py`), sin IA ni gasto.
- A las 7:00 de Madrid, en el tema General de cada grupo, con la vista previa del enlace.
- Solo los días con número: si el diario no deja archivo, no hay aviso.
- Cada grupo se apunta al publicarse (`<fecha>.publicado.json`): si uno falla, se reintenta en la
  vuelta siguiente sin repetir los demás.
- Si el bot estaba parado, publica en las 5 horas siguientes; después, ese día se queda sin aviso.

## Alternativas descartadas

- **Aviso semanal**, que era mi propuesta: menos ruido, pero el diario y el bot se olvidan.
- **Que el bot redacte el aviso**: el diario ya tiene las piezas y su repaso; aquí solo se publica
  lo revisado, sin otra llamada a Claude.

## Consecuencias

- Siete mensajes por semana en cada grupo. Para que no sean ruido, el texto cambia cada día y dice
  algo útil, nunca un anuncio fijo. En Vibe Coding Educativo, el viernes coincide con la lista de
  aplicaciones de la semana (ADR 0018); se revisará si conviene unirlos.
- Validación: `pruebas/test_diario_grupos.py` (hora de salida en horario de invierno, ventana,
  grupos vacíos, sin repetir, solo grupos activos y archivo de otro día).
