# 36. Aviso privado a quien sale en el Diario de IA Educativa

Fecha: 2026-11-13 · Estado: aceptado

## Contexto

Juanjo pidió el 13-11-2026 que se avise a quien ha aportado algo que sale en el diario, «para fomentar su
lectura y el interés», por privado y con un mensaje corto. El diario decide a quién (su ADR 0052): añade al
archivo de avisos del día una lista `personas`, con el id de Telegram y las piezas, con titular y enlace en
cada idioma.

## Decisión

- A partir de las 7:00 y dentro de la misma ventana que los avisos de los grupos, el bot escribe a cada
  persona un solo mensaje: «Hoy el Diario de IA Educativa cuenta lo que has compartido:» y, debajo, el
  titular y el enlace de cada pieza, en su idioma si el bot lo sabe (si no, en castellano), con la vista
  previa de la primera.
- Debajo, el botón «No avisarme más»: quien lo pulsa queda en `datos/diario-sin-avisos.json` y no vuelve a
  recibirlos (lo descartado no vuelve).
- Cada persona se apunta en `datos/diario/<fecha>.privados.json` al intentarlo, haya salido o no: Telegram
  no deja a un bot escribir primero a quien nunca le ha hablado, y no se insiste.
- Sin IA: el texto lo monta el programa.

## Alternativas descartadas

- Mencionar a las personas en el aviso de cada grupo: lo descartó Juanjo («no quiero mensajes tan largos»).
