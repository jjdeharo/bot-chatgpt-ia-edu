# Registro de cambios

Las versiones siguen a los bots en marcha, no a los datos. La etiqueta de git y `bot.VERSION` llevan el mismo número.

## 1.26.0 — 2026-11-21

- Los dos bots recuerdan qué hicieron en cada respuesta anterior: cuántas búsquedas hicieron y de qué. Antes, del historial solo veían el texto, y el Bot de IA Educativa llegó a corregirse en falso («no la había comprobado») y a decir que había buscado cuando no (ADR 0052).
- El Bot de IA Educativa sabe en la conversación lo que el programa ha mandado con botones: la ficha publicada, el anuncio para «¡Comparte tu App!», si se publicó, se quitó o se canceló (ADR 0052).
- Al quitar del grupo un anuncio de «¡Comparte tu App!», el bot ofrece «Rehacer el anuncio»: se pide el cambio con palabras (por ejemplo, en otro idioma), se enseña el mensaje nuevo y se publica con los botones de siempre. Vale durante 48 horas desde la publicación (ADR 0052).
- Las respuestas ya no muestran los nombres internos de las herramientas, no dicen que algo no está en un sitio donde no han buscado y no cuentan como no resueltas cuando dan lo que se pedía (ADR 0052).

## 1.25.1 — 2026-11-21

- Cuando la Biblioteca digital no acepta un documento, el bot deja claro que enviarlo a revisión lo decide quien lo manda: «Si crees que debería publicarse, puedes enviarlo para revisión», con el botón «Enviar para revisión» (ADR 0050).

## 1.25.0 — 2026-11-21

- Cuando la Biblioteca digital no acepta un documento por un motivo en que el bot puede equivocarse, quien lo manda puede pedir una revisión manual. Ocurre cuando cree que no trata de IA en educación, que está repetido o que su licencia no deja compartirlo, cuando no puede leer el texto y cuando el archivo pesa demasiado. A Juanjo le llegan quién lo manda, el documento, la ficha y el motivo, con botones para publicarlo con el archivo, solo la ficha o no publicarlo. La persona recibe la decisión, y lo que se publica tras un rechazo queda apuntado para corregir el filtro. Como mucho, tres peticiones por persona y día. Las respuestas ya no invitan a subir el documento directamente al tema, que está cerrado (ADR 0050).

## 1.24.0 — 2026-11-21

- La Biblioteca digital descarga los documentos que se le mandan con un enlace de Google Drive. Antes contestaba que no había ningún documento, porque la página de Drive solo muestra un visor (ADR 0049).

## 1.23.1 — 2026-11-21

- La Biblioteca digital adjunta el archivo de cualquier documento con una licencia Creative Commons nombrada con su abreviatura y su versión, también las NoComercial y SinDerivadas. Antes dejó sin archivo un documento CC BY-NC-ND 3.0 (ADR 0048).

## 1.23.0 — 2026-11-21

- La Biblioteca digital ya no da por repetido un documento nuevo si el título no lo confirma: el del candidato tiene que estar en su texto y coincidir con el del documento. Antes rechazó el «Manual urgente sobre IA en el aula» confundiéndolo con una guía de 2024 (ADR 0048).
- Si alguien manda a la Biblioteca un enlace de LinkedIn, X, Facebook, Instagram, Threads, TikTok o Bluesky, el bot le explica que es una publicación y le pide el PDF o el enlace oficial del documento (ADR 0048).

## 1.22.0 — 2026-11-21

- La Biblioteca digital reconoce la licencia general del Consejo de la UE, la Comisión Europea y el Parlamento Europeo. Un PDF descargado de sus webs oficiales se publica con el archivo, aunque el propio documento no indique licencia, y la ficha incluye la norma que lo permite. Si el documento reserva sus derechos de forma expresa, se publica solo la ficha (ADR 0046).

## 1.21.1 — 2026-11-18

- La Biblioteca digital registra cada publicación al enviarla y compara las direcciones y la huella del PDF antes de preparar su ficha y al confirmar su publicación. También comprueba las direcciones de las fichas del historial. Así puede devolver el enlace existente aunque Telegram aún no se haya indexado (ADR 0045).

## 1.21.0 — 2026-11-18

- Al recibir un enlace suelto, el bot distingue un documento de una aplicación cuando la página ofrece indicios claros. Si hay duda, pregunta a qué destino se quiere aportar o si solo se quiere consultar el enlace (ADR 0044).

## 1.20.2 — 2026-11-18

- La Biblioteca digital lee la licencia de la versión del artículo en arXiv. Si permite compartir ese PDF, el bot lo adjunta e incluye la licencia y su fuente en la ficha. También acepta enlaces directos a fichas y PDF de arXiv (ADR 0043).

## 1.20.1 — 2026-11-16

- La ayuda de Karla dice, en los cinco idiomas, que también se le puede mandar el `.zip` de un estilo con la duda (ADR 0042).

## 1.20.0 — 2026-11-16

- Karla lee el código de los estilos de eXeLearning: si le mandan un estilo en ZIP, o un `.elpx` con un estilo propio, ve su `config.xml`, `style.css` y `style.js` (sin comentarios, hasta 80.000 caracteres) y busca en ellos la causa del fallo. De un estilo oficial solo dice cuál es (ADR 0042).

## 1.19.0 — 2026-11-16

- El aviso de la semana del boletín semanal lo publica el Bot de IA Educativa, no la cuenta de Juanjo: el lunes a las 8:00, el mensaje y, en ChatGPT-IA-edu y Vibe Coding Educativo, el vídeo y el pódcast en el tema «Resumen semanal». Si algo falla, lo reintenta durante ocho horas y, si no sale, avisa a Juanjo (ADR 0041).

## 1.18.0 — 2026-11-15

- El Bot de IA Educativa manda a Juanjo por privado el informe del día del Diario de IA Educativa en cuanto el diario lo deja: qué se ha publicado, si se usó la reserva, a quién se escribió y qué ha fallado (ADR 0040).

## 1.17.0 — 2026-11-14

- Al acabar el plazo de los avisos de la revisión del repositorio (el 29-11-2026 los enlaces que no se abren y las licencias incompatibles; el 11-12-2026 los GPT), a las 9:00, el bot vuelve a comprobar lo pendiente con la misma comprobación que «Ya lo he corregido», da por corregido lo que ya cumple y manda a Juanjo la lista de lo que sigue sin cumplir, con una casilla por recurso, «Retirar los marcados» y «No retirar ninguno». Solo se retira lo que él confirma, guardando antes la ficha entera para poder devolverla (`avisos.py restaurar`); al retirar lo del 29-11, se desfija el aviso del grupo. Un enlace que vuelve a abrirse sin licencia no se retira: queda como recomendación (ADR 0039).

## 1.16.2 — 2026-11-14

- Cuando el Bot de IA Educativa recomienda una herramienta o un servicio (un Gem, un GPT, NotebookLM, una app), busca antes en los grupos y en el diario si se ha dicho que cambia de nombre o desaparece, y lo avisa junto a la recomendación. Y no ofrece hacer nada que no pueda, como preguntar a otra persona (ADR 0038).
- Las preguntas sin resolver por un error guardan el tipo de error, en los dos bots, para saber al revisarlas por qué fallaron (ADR 0007).

## 1.16.1 — 2026-11-14

- Las preguntas sin resolver de los dos bots guardan también lo que respondió el bot (los primeros 1.500 caracteres) y si se quedó sin terminar la búsqueda, para saber al revisarlas si contestó a medias o nada. Siguen sin nada de quien pregunta (ADR 0007).

## 1.16.0 — 2026-11-14

- El aviso diario del Diario de IA Educativa lleva como imagen grande la portada del número, de la cabecera a la viñeta, la misma en los tres grupos. Si aún no está en la web a las 7:00, el bot espera hasta 20 minutos y después sale con la imagen de antes (ADR 0037).

## 1.15.1 — 2026-11-13

- El mensaje privado del diario empieza saludando por el nombre: «Buenos días, Nombre. Hoy el Diario de IA Educativa cuenta lo que has compartido:» (ADR 0036).

## 1.15.0 — 2026-11-13

- Quien ha aportado algo que sale en el Diario de IA Educativa (un documento de la Biblioteca digital, un recurso del repositorio o el recurso que cuenta una pieza) recibe un mensaje privado del bot con el titular y el enlace de cada pieza, y un botón para no recibirlos más (ADR 0036).

## 1.14.2 — 2026-11-12

- Los documentos con licencias abiertas de gobiernos (Open Government Licence del Reino Unido, Licence Ouverte de Francia) o de documentación y datos (GFDL, The Unlicense, Open Data Commons) se publican en la Biblioteca digital con su archivo. Antes salía solo la ficha, como si la licencia no dejara compartirlo (ADR 0019).

## 1.14.1 — 2026-11-12

- El enlace que se manda después de `/biblioteca` va a la Biblioteca digital aunque no acabe en `.pdf`. Antes, el de una página que presenta el documento se tomaba como un recurso para el repositorio de Vibe Coding Educativo y se pedía su licencia de código (ADR 0035).

## 1.14.0 — 2026-11-12

- Para añadir un documento a la Biblioteca digital basta con mandar su enlace: el del PDF o el de la página que lo presenta. El bot busca el documento en la página, lo descarga y sigue como con un PDF enviado; si su web no deja descargarlo a un programa, como el repositorio de la UNESCO, da el enlace directo del documento para descargarlo y mandárselo. Una página sin documento no se añade (ADR 0035).

## 1.13.0 — 2026-11-11

- Quien escribe los cambios de la ficha de su recurso como un mensaje más, sin pulsar «Cambiar», ya no recibe una búsqueda sin resultado: el bot los aplica a la ficha que tiene a la vista o al recurso publicado que nombra; si tiene varios, pregunta cuál con un botón por recurso, el último primero, y enseña la ficha cambiada antes de guardar nada (ADR 0004).
- Una pregunta que es solo un nombre o un título («Selfie for teachers») se responde en el idioma de la conversación y no cambia el idioma del bot (ADR 0005).
- Si no encuentra nada, el bot ya no propone buscar con otras palabras lo que ya ha buscado él; como mucho, ofrece buscar en un solo grupo o en unas fechas.

## 1.12.0 — 2026-11-10

- Si el bot no consigue leer un recurso (no ve qué hace o el enlace no se abre), ofrece «Pedir una revisión»: le llega a Juanjo con lo que ha pasado y un botón «Volver a leer», que lo lee otra vez y sigue el alta con su autor (ADR 0004).

## 1.11.3 — 2026-11-10

- El bot lee las aplicaciones publicadas en Google Sites: saca el código de cada bloque «Insertar código» de la página, con su licencia, y lee la web de cada bloque «Insertar URL». Antes solo le llegaba el código de carga de Google, que ocupa los primeros 95 000 caracteres de la página, y pedía el código aparte (ADR 0004).

## 1.11.2 — 2026-11-07

- El bot cuenta cada día, y no cada semana, cuántas personas hay en cada grupo para el Diario de IA Educativa; si pasan dos días sin cifras, avisa (ADR 0032).

## 1.11.1 — 2026-11-07

- El aviso de cada comentario del diario lleva el comentario entero, y el bot lo sabe (ADR 0034).

## 1.11.0 — 2026-11-07

- En privado, el bot lee el mensaje al que se responde citándolo, con sus enlaces, y responde sobre él: también sobre los avisos que otros programas mandan en su nombre (ADR 0034).
- El bot sabe de los comentarios del Diario de IA Educativa: cómo se comenta, se responde o se borra un comentario, y que avisa de cada comentario nuevo a Juanjo de Haro y a Raül Torres (ADR 0034).

## 1.10.0 — 2026-11-07

- Antispam en los grupos, sin IA: el Bot de IA Educativa y Karla bot borran y expulsan a quien, sin haber escrito nunca en el grupo, escribe en chino, japonés, coreano o cirílico, menciona varios bots o manda una ráfaga de mensajes, y a quien entra con el nombre en esas escrituras. Cada expulsión llega a Juanjo por privado con un botón «Deshacer» (ADR 0033).

## 1.9.1 — 2026-11-07

- Cada grupo recibe el aviso del Diario de IA Educativa con su propia imagen de vista previa: si el aviso trae el enlace de la página de entrada de su grupo, el bot lo usa en lugar del general (ADR 0029).

## 1.9.0 — 2026-11-05

- El Bot de IA Educativa explica el MIAE y la guía Vibe coding responsable con sus textos completos, al día y en los cinco idiomas: en qué nivel del MIAE está un uso de la IA (y qué le falta saber para decirlo), cómo declararlo, qué pide cada recomendación de la guía, qué licencia poner o cómo evaluar con la VCER, con el enlace de la página de cada apartado. En la ayuda para enseñar también los usa, revisados y citados como el resto de fuentes (ADR 0031).

## 1.8.1 — 2026-11-05

- Las piezas del diario que no salen de un mensaje de los grupos (las del repositorio) se citan con la pieza y sus fuentes, sin decir que les falta el mensaje (ADR 0030).

## 1.8.0 — 2026-11-05

- El bot busca en lo publicado por el Diario de IA Educativa, al día cada mañana en cuanto sale el número: dice qué trae un número o el de un día y si el diario ha contado algo, citando primero el mensaje original del grupo y debajo la pieza del diario (ADR 0030).
- Quien no encuentra los números anteriores del diario recibe el enlace de la hemeroteca, en castellano y en catalán.

## 1.7.1 — 2026-11-04

- La descripción de las imágenes de los grupos se limita a la imagen: ya no juzga el mensaje ni sus enlaces. Había dado por «una entrada antigua de otro sitio» un blog con fecha de 2013 en la dirección que se había vuelto a publicar ese día con una aplicación nueva, y el Diario de IA Educativa la descartó por eso (ADR 0028).

## 1.7.0 — 2026-11-04

- El aviso diario del Diario de IA Educativa llega con formato: el número en negrita, la fecha, un saludo y dos o tres puntos, y encima la imagen del número en grande (ADR 0029).

## 1.6.0 — 2026-11-03

- El bot describe con Claude Haiku las imágenes que se comparten en los grupos, con el texto que se lee en ellas, y las usa al buscar y al ayudar a preparar clases; el Diario de IA Educativa también las lee (ADR 0028).

## 1.5.2 — 2026-11-03

- Cuando el bot no admite un recurso por no tener licencia abierta, explica que la licencia tiene que ponerla su autor en el propio recurso y qué pedir a la IA con la que lo hizo: la línea SPDX al principio del código y la licencia visible en el pie (ADR 0004).

## 1.5.1 — 2026-11-03

- Si se cambia el autor de una ficha y la persona tiene más recursos con otro nombre, al publicar el bot pregunta si lo cambia en todos o solo en ese, para los recursos firmados a varias manos (ADR 0027).

## 1.5.0 — 2026-11-03

- Al dar de alta un recurso del repositorio de Vibe Coding Educativo, si el nombre de Telegram tiene menos de tres letras («D»), el bot pide una vez el nombre con el que se quiere firmar y lo recuerda para los siguientes.
- Si se cambia el autor de una ficha, el nombre nuevo se guarda y se cambia en todos los recursos de esa persona; la ficha lo avisa antes de publicar (ADR 0027).

## 1.4.5 — 2026-11-03

- Los PDF nuevos de la Biblioteca digital guardan también su texto entero, para los artículos del Diario de IA Educativa (ADR 0026).

## 1.4.4 — 2026-11-03

Las fichas de la Biblioteca digital llevan la dirección del documento. Si el documento no la trae, el Bot de IA Educativa la busca en internet (la página oficial de su autor o su editorial) y, si no la encuentra, la pide a quien lo envía, con un botón «Sin enlace» para quien no la tenga. La ficha ya no termina con «Para crear un resumen como este, utiliza…», sino con «(Para publicar un documento en la Biblioteca digital, envíaselo por privado a @IAEducativa_bot)» (ADR 0002).

## 1.4.3 — 2026-11-02

A quien pregunta cómo recibir el Diario de IA Educativa, el Bot de IA Educativa le dice que no hay boletín por correo, que el número del día se publica cada mañana en los tres grupos y que fuera de ellos se puede seguir por RSS, en castellano o en catalán. Ya no remite a nadie las dudas sobre el diario.

## 1.4.2 — 2026-11-02

El Bot de IA Educativa sabe que publica el aviso del Diario de IA Educativa: a «¿publicas tú el diario?» o «¿qué es el diario?» responde que cada mañana a las 7:00 publica el aviso en los tres grupos, qué recoge el diario y su web, en castellano y en catalán; como no lo lee, para lo que trae un número remite a la web (ADR 0025).

## 1.4.1 — 2026-11-02

Responder en el grupo a un mensaje que el bot publica por su cuenta (el aviso del diario, el resumen de los viernes) ya no recibe «escríbeme por privado», aunque lleve una pregunta: el bot calla. La mención y los comandos siguen remitiendo al privado (ADR 0020).

## 1.4.0 — 2026-11-01

Cada mañana a las 7:00, el aviso de «Tiza y Algoritmo», el diario de los grupos, en el tema General de ChatGPT-IA-edu, Vibe Coding Educativo y EduMedia-IAG. El texto llega redactado y repasado del diario; el bot solo lo publica, una vez por grupo y día (ADR 0025).

## 1.3.3 — 2026-11-01

Cuando un bot llega a su tope del mes, dice solo que ahora no puede responder y que volverá a funcionar el día 1, sin hablar de presupuesto: los problemas de dinero se le avisan a Juanjo, no a quien pregunta (ADR 0024).

## 1.3.2 — 2026-11-01

Si Anthropic deja de atender a un bot porque se han acabado los créditos o se ha llegado a un límite de gasto de la Console, el bot avisa a Juanjo una vez, con la causa, hasta que vuelva a funcionar (ADR 0024). A quien pregunta no se le dice nada de dinero.

## 1.3.1 — 2026-11-01

El mensaje que lleva una pregunta al grupo dice ahora que se contesta allí, respondiendo a ese mensaje, y a quién se le hará llegar por privado: la frase anterior se podía leer como si hubiera que escribir al bot.

## 1.3.0 — 2026-11-01

Dos ideas del análisis competitivo del 01-11 (ADR 0023). **Preguntar en el grupo**: cuando un bot no encuentra la respuesta, o la persona pulsa 👎, ofrece llevar la pregunta al grupo con su nombre; antes enseña el mensaje tal como quedará, y quien responda allí a ese mensaje le llega por privado durante una semana; se puede quitar en 48 horas, con un tope de tres al día por persona (no en EduMedia-IAG). **`/sinresolver`**, para Juanjo: las preguntas sin resolver agrupadas por temas con Sonnet, con qué las resolvería y un ejemplo literal de cada tema (unos 0,01 USD; sin gasto con menos de 5).

## 1.2.0 — 2026-11-01

Notas de voz en los dos bots (ADR 0022): un servicio de voz con faster-whisper «small», reutilizando la imagen, el entorno y el modelo ya descargado del boletín semanal; el bot enseña lo que ha entendido y responde como a una pregunta escrita. Sin gasto de API.

## 1.1.0 — 2026-11-01

Las mejoras del informe del 01-11 (ADR 0021): los mensajes reenviados llevan quién los escribió y cuándo, para que el bot dé con el hilo exacto; Karla ofrece avisar de cada respuesta del equipo a quien envía un aviso de error, y del cierre; Karla lee archivos `.elpx`, `.elp` y `.zip` (resumen del proyecto: versión, páginas, iDevices) y diagnostica con ellos; el bucle del índice avisa si la documentación de eXeLearning lleva tres días sin cambiar; y pedir aplicaciones o recursos de un tema va por la búsqueda normal, no por la ayuda para enseñar (de 0,08 a 0,003 USD).

## 1.0.0 — 2026-11-01

Primera versión etiquetada: los dos bots tal como corren en el NAS desde el 27-10-2026, con las correcciones de la revisión de seguridad del 31-10 (ADR 0019) y las del informe del 01-11 (ADR 0020): respuesta fija cuando Claude no deja texto, firma en los botones que borran lo publicado, reintento ante un 429 de Telegram, repuesto HTML con encabezados, tablas y citas, preguntas largas hasta 6.000 caracteres con aviso de recorte, enlaces de Telegram tratados como pregunta, sin aviso a quien responde al resumen semanal sin preguntar, enlace al código y versión en la ayuda, copia diaria con lo de Karla, pruebas en GitHub Actions y la cuenta de Juanjo fuera del código.
