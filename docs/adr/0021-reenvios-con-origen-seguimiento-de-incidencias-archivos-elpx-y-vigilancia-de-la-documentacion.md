# 21. Reenvíos con su origen, seguimiento de incidencias, archivos .elpx, vigilancia de la documentación y búsqueda de recursos por el camino barato

Fecha: 2026-11-01 · Estado: aceptado

## Contexto

El informe del 01-11-2026 (`Informes/bot-chatgpt-ia-edu/2026-11-01-errores-carencias-y-mejoras.md`)
proponía, además de las correcciones del ADR 0020, seis mejoras. Juanjo pidió hacerlas («haz las
mejoras»). Se hacen cinco; la sexta (mensajes de voz) se deja fuera, ver abajo.

1. Al reenviar al bot un mensaje del grupo, el programa juntaba los textos pero perdía quién lo escribió
   y cuándo, y Claude respondía sobre un mensaje parecido, no sobre ese.
2. Quien enviaba un aviso de error con Karla recibía el enlace y nada más: si el equipo preguntaba algo
   en GitHub, no se enteraba.
3. Un archivo `.elpx` mandado a Karla recibía «solo entiendo mensajes escritos».
4. La documentación de Karla la genera memoria-telegram cada día; si dejara de hacerlo, el bucle diría
   «documentación: nada nuevo» y Karla seguiría con lo viejo sin que nadie lo notara.
5. «¿Hay alguna aplicación para practicar fracciones?» entraba como ayuda para enseñar (Sonnet, seis
   búsquedas, revisión: 0,084 USD, treinta veces una pregunta normal), cuando es una búsqueda en el
   repositorio.

## Decisión

- **Reenvíos con su origen** (`bot.origen`): cada trozo reenviado lleva delante «[Mensaje reenviado,
  escrito por NOMBRE el AAAA-MM-DD HH:MM]», a partir del campo `forward_origin` de la API de Telegram
  (usuario, usuario oculto, grupo o canal). Las instrucciones de los dos bots dicen que, con eso,
  busquen el mensaje acotando la fecha y lean su hilo.
- **Seguimiento de incidencias, con permiso** (Karla): tras abrir una, dos botones, «Sí, avísame» y «No
  hace falta», con el aviso de que se guarda su cuenta junto al número hasta que se cierre.
  `datos/seguimiento-incidencias.json` (fuera del repositorio y en la copia diaria) guarda cuenta,
  idioma, título, comentarios contados y estado. Cada 15 minutos, un programa sin IA lee cada incidencia
  seguida en GitHub (una llamada por incidencia, pocas) y manda a la persona, en su idioma, cada
  comentario nuevo y el cierre con su motivo; cerrada, se deja de seguir. `/estado` dice cuántas hay.
- **Archivos .elpx, .elp y .zip** (`karla.leer_elpx`): se leen en memoria, nunca a disco, y se resumen
  para Claude: entradas del ZIP, formato (content.xml, o contentv3/contentv2 de eXe 2.x), propiedades
  (`pp_title`, `pp_exelearning_version`…), páginas, iDevices por tipo y el principio del XML sin el
  HTML de los iDevices (6.000 caracteres). El pie del archivo es la pregunta. Las instrucciones piden
  diagnosticar con eso sin inventar lo que el resumen no dice.
- **Vigilancia de la documentación** (`documentacion.py vigilar`, desde `nas/bucle.sh` tras cada
  pasada): si ningún documento de memoria-telegram ha cambiado en tres días, aviso a Juanjo por el bot,
  una vez al día (marca `datos/aviso-docs`).
- **Búsqueda de recursos por el camino normal**: `SISTEMA_ES_AYUDA` excluye pedir aplicaciones, recursos
  o materiales de un tema, salvo que pida además consejo, una actividad o cómo usarlos. Matiza el ADR
  0011, que incluía «qué herramienta usar» como ayuda.
- **Mensajes de voz, no**: exigiría un modelo de voz en el NAS (Whisper pequeño por CPU: 1 GB más de
  memoria, 10-20 s por nota) o una API de pago, que Juanjo no quiere. Nadie lo ha pedido; se revisará
  si aparece en las preguntas sin resolver.

## Alternativas descartadas

- Seguir las incidencias con la búsqueda de GitHub (una llamada para todas): no da los comentarios;
  una llamada por incidencia seguida es más simple y son pocas.
- Guardar el seguimiento sin preguntar: liga una cuenta de Telegram a una incidencia pública; es un dato
  más de la persona y se pide permiso.
- Extraer el `.elpx` a disco y leerlo entero: el ZIP se lee por flujo en memoria y basta con el resumen;
  el HTML de los iDevices se quita para no gastar tokens.
- Dar a Claude el `.elpx` sin resumir: 50.000 caracteres de XML por archivo; el resumen cabe en 8.000.

## Consecuencias

- Una pregunta con un `.elpx` cuesta hasta 2.000 tokens más de entrada.
- El seguimiento hace una llamada a GitHub cada 15 minutos por incidencia seguida (con clave, 5.000 por
  hora de límite): irrelevante.
- Karla guarda un dato nuevo de personas, con su permiso y solo hasta el cierre; va en la copia diaria.
- Las búsquedas de recursos bajan de 0,08 a 0,003 USD y de 40 a 10 segundos; la ayuda para enseñar
  sigue igual para lo que pide consejo o una actividad.

## Evidencia

- `forward_origin` y `MessageOrigin` en https://core.telegram.org/bots/api (comprobado el 01-11-2026).
- Estructura de `content.xml`: documentación técnica de eXeLearning (`doc/elpx-format/content-xml.md`,
  indexada por Karla) y el archivo de ejemplo `Archivos_de_ejemplo/elpx/manual-edex.elpx`.
- La prueba de las fracciones: informe del 01-11-2026, 6 búsquedas y 0,0841 USD.

## Riesgos y limitaciones

- Un reenvío de un canal o de alguien que oculta su cuenta solo lleva el nombre: la fecha basta para
  acotar la búsqueda.
- El seguimiento solo ve los 8 últimos comentarios de cada lectura: más de 8 comentarios nuevos en
  15 minutos no se contarían todos (muy improbable).
- `leer_elpx` reconoce el formato 2.0 de eXeLearning 4; de un `.elp` antiguo solo dice que lo es.

## Validación

- `pruebas/test_revision.py`: 46 pruebas (40 anteriores y 6 nuevas), todas en verde el 01-11-2026.
- `leer_elpx` probado con `manual-edex.elpx` real: 103 entradas, título, versión, 4 páginas, 2 tipos de
  iDevice.
- Pendiente de observar en producción: el primer seguimiento real y el primer reenvío.
