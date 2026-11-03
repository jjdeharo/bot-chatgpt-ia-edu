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

- La ficha lleva la dirección del documento (03-11-2026, Juanjo: «falta el
  enlace»; «si el bot no encuentra el enlace que lo pida al usuario»). Si la
  referencia no trae DOI ni dirección, Claude Haiku 5.5 la busca con la
  búsqueda web de la API (hasta tres búsquedas): la página oficial dedicada al
  documento o, si no la hay, su PDF en el sitio oficial, nunca una copia de
  terceros. La dirección solo vale si abre. Si no la encuentra, el bot la pide
  a la persona antes de enseñarle la ficha, con un botón «Sin enlace» para
  quien no la tenga.
- La última línea de la ficha no es la de la página de resúmenes («Para crear
  un resumen como este, utiliza…»), que sirve a quien la hace a mano, sino
  «(Para publicar un documento en la Biblioteca digital, envíaselo por privado
  a @IAEducativa_bot)» (03-11-2026: «la frase final entre paréntesis no debe
  aparecer»).

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
- Buscar la dirección cuesta algo más de un céntimo (0,011 USD medido el
  03-11-2026: una búsqueda a 0,01 USD más los tokens de Haiku), y solo se
  gasta cuando el documento no la trae.
- El bot publica en el grupo: no puede hacerlo en nombre de la persona, así
  que firma con «Aportado por».

## Evidencia y validación

24-10-2026, con tres PDF: un certificado urbanístico (descartado), «Evaluar con
inteligencia», que ya está en la biblioteca (detectado, con su enlace), y la
metodología de sistemas adaptativos bayesianos de Juanjo (ficha y publicación
correctas). La primera versión del filtro descartó esta última por no ser IA
generativa; se amplió el criterio («ante la duda, encaja»). Publicación probada
en un chat privado (`BIBLIOTECA_PRUEBA`) antes de abrirla al grupo.

Dirección del documento, 03-11-2026: con el informe del comité del MIT sobre
IA en la docencia, que no trae su dirección, la búsqueda dio
https://sites.mit.edu/ai-use/ai-committee-final-report-aug-13/ en tres
intentos seguidos (lleva al PDF en el sitio del MIT); con la primera redacción
de la instrucción dio la portada del sitio, y se pidió la página del propio
documento. Con un documento inventado devolvió la cadena vacía, y el bot pide
el enlace. Pruebas sin red de los tres caminos (da el enlace, escribe otra
cosa, pulsa «Sin enlace») en `pruebas/test_revision.py`.

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

