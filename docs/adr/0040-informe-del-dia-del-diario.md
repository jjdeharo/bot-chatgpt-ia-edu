# 40. El informe del día del diario, a Juanjo por el bot

Fecha: 2026-11-15 · Estado: aceptado

## Contexto

El Diario de IA Educativa manda cada día a Juanjo un informe: si ha salido todo, si se usó la reserva, a quién se
escribió y qué ha fallado (su ADR 0069). El primero salió por el bot de los avisos de los agentes («Agentes IA»).
Juanjo: «tienes que enviarlo por el bot de IA educativa, que es el que hace este tipo de cosas de los grupos».

## Decisión

- El diario deja el informe en `datos/diario/<fecha>.informe.txt`, la carpeta que ya comparte con el bot para los
  avisos de los grupos. El bot lo manda a Juanjo por privado en su vuelta siguiente (`informe_si_toca`), sin vista
  previa de enlaces y en texto llano, y deja `<fecha>.informe-enviado` al lado para no repetirlo.
- Si el diario lo vuelve a dejar después (corregido), se manda otra vez.

## Alternativas descartadas

- **Dar al diario el token del bot**: dos sitios con la misma credencial; el bot ya recoge lo que el diario le deja.

## Validación

`pruebas/test_diario_grupos.py`, `InformeDelDia`: un informe nuevo está pendiente, deja de estarlo al marcarlo y
vuelve a estarlo si se deja de nuevo. Las 194 pruebas y `ruff check --select E9,F`, en verde.
