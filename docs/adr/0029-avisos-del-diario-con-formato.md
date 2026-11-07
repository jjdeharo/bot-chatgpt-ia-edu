# 29. Avisos del diario con formato

Fecha: 2026-11-04 · Estado: aceptado

## Contexto

El aviso diario del Diario de IA Educativa (ADR 0025) llegaba del diario como texto hecho y el bot
lo publicaba tal cual: un bloque sin formato, con una vista previa pequeña y siempre igual. Juanjo
lo vio «muy simplón» (04-11-2026) y aceptó la propuesta de darle formato y una imagen por número
(ADR 0010 del diario).

## Decisión

- El diario deja en `datos/diario/<fecha>.json`, además de los avisos, la cabecera del número:
  `titulo` («Diario de IA Educativa · Núm. 3»), `fecha_texto` y `url` (la portada con `?n=3`).
  Cada aviso es `{"saludo": "…", "puntos": ["…", "…"]}`.
- `diario_grupos.mensaje()` monta el mensaje en HTML: el título en negrita, la fecha, el saludo,
  los puntos con «•» y `👉 url`, con el texto escapado. Pide la vista previa de `url`, grande y
  encima del texto (`link_preview_options`).
- Sin cabecera, el mensaje sale igual con la portada como enlace. Un aviso sin puntos no se publica.
  Un aviso en texto (el formato anterior) se publica tal cual.

## Alternativas descartadas

- Recibir el HTML hecho del diario: un error de etiquetas de la IA haría que Telegram rechazara el
  mensaje y el grupo se quedaría sin aviso.

## Consecuencias

- El bot no decide el contenido: solo lo coloca. El texto sigue llegando hecho y repasado.

## Evidencia

- Bot API, `LinkPreviewOptions`: `prefer_large_media` solo vale si se da `url` de forma explícita,
  por eso el bot la pasa siempre. https://core.telegram.org/bots/api#linkpreviewoptions

- **Un enlace por grupo** (07-11-2026, versión 1.9.1): cada aviso puede traer su `url`, la página de
  entrada de su grupo en el diario (`n/<número>-<grupo>.html`), que solo lleva la imagen de ese grupo
  y redirige a la portada del número; si no la trae, vale la de la cabecera. Así Telegram enseña en
  cada grupo la imagen de una pieza suya (Juanjo: «yo pensaba que cada una tenía la suya»; eligió que
  la página lleve a la portada). La decisión de qué imagen va en cada grupo es del diario (su ADR 0010).

## Riesgos y limitaciones

- El tamaño de la vista previa lo decide al final el cliente de Telegram.

## Validación

- `pruebas/test_diario_grupos.py`: formato nuevo, signos escapados, aviso sin cabecera, sin puntos
  y formato anterior.
- Aviso de prueba enviado solo a Juanjo el 04-11-2026.
