# 2. Fichas y publicación de documentos en la Biblioteca digital

Fecha: 2026-10-24 · Estado: aceptado

## Contexto

Hasta ahora, quien quería añadir un documento a la Biblioteca digital lo subía
al tema, preparaba la ficha con la página
https://chatgpt-ia-edu.github.io/resumen/ y un asistente de IA, y la pegaba en
respuesta. Juanjo quiere que el bot lo haga todo: que el miembro le mande el
archivo y el bot compruebe, haga la ficha y publique, sin aprobación previa de
Juanjo («yo estaré atento»), y que descarte lo que no trate de IA educativa.

## Decisión

- El miembro manda el PDF por privado. El bot comprueba con Claude Haiku 5.5
  (salida JSON estructurada) que trate de IA en educación en sentido amplio y
  que no sea uno de los seis documentos más parecidos de la biblioteca.
- La ficha la hace Claude Sonnet 5.5 con las instrucciones de la propia página
  de resúmenes, leídas de ella cada vez (copia local si no responde): mismo
  formato que las fichas hechas a mano y un solo sitio donde cambiarlo. Lee el
  texto de las 30 primeras páginas (pdftotext) y los metadatos del PDF.
- La persona ve la ficha y decide con los botones «Publicar» o «Cancelar».
- Se publica como lo hacía Juanjo: el documento con el título en mayúsculas y
  «Aportado por Nombre (@usuario)» como pie, y la ficha en respuesta. Si la
  ficha dice «No se podrá compartir…» (sin licencia libre, según las
  instrucciones de la página), se publica solo la ficha, sin el archivo.
- El índice atribuye la obra a la persona del «Aportado por», no al bot.
- Límite de 3 documentos al día por persona.

## Alternativas descartadas

- **Aprobación de Juanjo antes de publicar**: él prefirió vigilar después.
- **Preguntar a la persona si el documento es de libre distribución** cuando
  no indica licencia: las instrucciones de la página ya lo tratan como no
  compartible, y esa es la norma del grupo.
- **Servidor propio de la API de bots** para archivos de más de 20 MB: otra
  pieza que mantener; a esos se les explica el motivo y se les pide que los
  suba su dueño a mano.

## Consecuencias

- Coste: unos 0,0005 USD la comprobación y 0,03–0,08 USD cada ficha (medido
  con tres PDF el 24-10-2026). Sale del mismo tope mensual.
- El bot publica en el grupo: no puede hacerlo en nombre de la persona, así
  que firma con «Aportado por».

## Evidencia y validación

24-10-2026, con tres PDF: un certificado urbanístico (descartado), «Evaluar con
inteligencia», que ya está en la biblioteca (detectado, con su enlace), y la
metodología de sistemas adaptativos bayesianos de Juanjo (ficha y publicación
correctas). La primera versión del filtro descartó esta última por no ser IA
generativa; se amplió el criterio («ante la duda, encaja»). Publicación probada
en un chat privado (`BIBLIOTECA_PRUEBA`) antes de abrirla al grupo.

## Riesgos y limitaciones

- La comprobación de repetidos compara con seis candidatos: una edición
  distinta del mismo documento se publica como nueva.
- Un PDF escaneado como imagen no tiene texto que leer: se pide subirlo a mano.

## Quitarlo si se arrepiente

Desde el 27-10-2026 (Juanjo: «un botón del arrepentimiento como al publicar en
vce»), el aviso de «Publicado en la Biblioteca digital» lleva «Quitarlo de la
Biblioteca» y «Mantenerlo». Quitarlo borra los mensajes que publicó el bot (el
documento y su ficha, o solo la ficha); Telegram deja a un bot borrar sus
mensajes durante 48 horas, y después el bot remite a quien administra el grupo.
El índice lo retira en la pasada completa de la madrugada.

