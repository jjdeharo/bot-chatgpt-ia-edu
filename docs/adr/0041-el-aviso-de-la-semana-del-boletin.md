# 41. El aviso de la semana del boletín, publicado por el bot

Fecha: 2026-11-16 · Estado: aceptado

## Contexto

El boletín semanal publicaba cada lunes a las 8:00 en los tres grupos el aviso de la semana (el mensaje y, en
ChatGPT-IA-edu y Vibe Coding Educativo, el vídeo y el pódcast de NotebookLM, en el tema «Resumen semanal»), con la
cuenta personal de Juanjo, programado en Telegram. Juanjo pidió el 16-11-2026 que lo publique el bot a partir de la
semana siguiente.

Un bot no puede programar mensajes, y la API de bots no deja subir archivos de más de 50 MB. El Bot de IA Educativa
es administrador de los tres grupos y ya publica a su hora los avisos del diario (ADR 0025); los dos temas «Resumen
semanal» están abiertos (comprobado el 16-11-2026 con la cuenta de Juanjo, solo leyendo).

## Decisión

- El boletín deja en `datos/boletin/<semana>/<grupo>.json` el aviso, ya redactado en HTML, con el tema, la hora de
  salida y, si toca, el vídeo, su miniatura y el pódcast en la misma carpeta (ADR 0012 del boletín).
- `scripts/boletin_grupos.py` y `boletin_si_toca()`, en el bucle del bot: a la hora de salida, dentro de una
  ventana de ocho horas, publica el mensaje (sin vista previa del enlace si lleva vídeo, como antes), el vídeo
  (con su miniatura, duración y medidas, para que se vea en el móvil) y el pódcast (con título e intérprete), todo
  en el tema del grupo. Va en un hilo, porque subir los vídeos tarda, y uno a la vez.
- Si algo falla a medias, borra lo enviado y reintenta en la vuelta siguiente; publicado, lo apunta en
  `<grupo>.publicado.json` y borra el vídeo y el pódcast de su carpeta. Si pasa la ventana sin salir,
  `<grupo>.fallido.json` y un aviso por privado a Juanjo.
- Un archivo de más de 50 MB no se sube: el mensaje sale igual, con el enlace a la semana del diario, que tiene el
  vídeo y el pódcast.
- `Telegram.subir` admite ahora el tipo del archivo y archivos adicionales (la miniatura), y un plazo más largo para
  los archivos grandes.

## Consecuencias

- Los avisos de la semana salen a nombre del bot, como los del diario.
- El bot ocupa la conexión de casa unos segundos cada lunes a las 8:00 (dos vídeos de unos 35 MB y dos pódcast).

## Validación

`pruebas/test_boletin_grupos.py` (hora de salida, ventana, orden de envío, tema, borrado si falla, sin repetir). El
16-11-2026, con los archivos reales de la semana 46: el bot publicó el aviso de ChatGPT-IA-edu en el chat privado de
Juanjo (mensaje, vídeo de 31 MB con miniatura y pódcast) en siete segundos.
