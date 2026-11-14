# 37. La portada como imagen del aviso del diario

Fecha: 2026-11-14 · Estado: aceptado

## Contexto

El aviso de cada mañana en los tres grupos (ADR 0025 y 0029) llevaba como imagen grande la vista previa de la
página de entrada de su grupo. El 13-11-2026, al ver la captura de la portada que el diario hace para su
hemeroteca (de la cabecera a la viñeta, su ADR 0053), Juanjo propuso usarla también en Telegram: «Es mucho más
llamativo que la imagen actual», y «mejora mucho con la portada completa, asi que no me importa que se repita
imagen». Pidió además que el texto no quedara «en forma de tubo», como pasa cuando la imagen va en un mensaje
con pie de foto, y propuso partirlo en dos mensajes. El cambio no llegó a hacerse, y el 14-11 los tres avisos
salieron sin la portada: «Ninguno de los tres mensajes de telegram ha salido con la imagen de la portada como
habíamos quedado. Arreglalo y si se puede edita los mensajes para que se vea».

## Decisión

- El diario añade al archivo de los avisos `imagen`, la dirección de la captura de la portada en castellano
  (`portadas/<fecha>-es.jpg` del sitio). El bot la pone como vista previa del mensaje: grande y encima del
  texto (`prefer_large_media`, `show_above_text`). Es la misma en los tres grupos; el enlace del final sigue
  siendo el de la página de cada grupo.
- **Un solo mensaje**, no dos. Con la imagen como vista previa, el texto ocupa todo el ancho del globo y no
  se estrecha, que era el motivo para partirlo; y un mensaje así se puede editar, cosa que no se puede hacer
  con uno de foto si después cambia la imagen.
- La portada se sube a la web pocos minutos antes de las 7:00. El bot comprueba que ya se descarga; si no,
  espera hasta 20 minutos (`ESPERA_IMAGEN`) y después publica con la imagen de la página del grupo, como antes.
- Los avisos del 14-11-2026, ya enviados, se editaron con la portada.

## Alternativas descartadas

- **Dos mensajes, la foto y después el texto**: avisan dos veces a cada miembro, y el primero no se puede
  convertir después en otro tipo de mensaje. La vista previa grande da el mismo resultado con uno.
- **La foto con el texto como pie**: Telegram estrecha el pie al ancho de la foto (el «tubo»).

## Consecuencias

- Si un día no hay captura (falla `portadas.py`), el aviso tarda hasta 20 minutos más y sale con la imagen
  de antes.
- La captura es alta (900 × 1607 píxeles); Telegram la reduce en la vista previa.

## Evidencia

- `pruebas/test_diario_grupos.py`, `test_portada_como_imagen_del_aviso`: con la portada disponible, la vista
  previa es la portada; si no, se espera, y pasada la espera sale con la página del grupo.

## Validación

- Las 174 pruebas del bot y `ruff check --select E9,F`, en verde.
- Los tres avisos del 14-11-2026 editados con `editMessageText` y la nueva vista previa, comprobados en
  Telegram.
