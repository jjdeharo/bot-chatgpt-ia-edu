# 35. Documentos de la Biblioteca digital a partir de un enlace

Fecha: 2026-11-12 · Estado: aceptado

## Contexto

Un miembro le pidió al bot «Descarga y publica en la biblioteca» con el enlace de una noticia de la UNESCO que
presentaba un documento nuevo. El bot solo aceptaba el PDF (ADR 0002) y le pidió que guardara la página como PDF
desde el navegador. Juanjo preguntó qué costaría que el bot lo hiciera él. Se le propusieron tres pasos: descargar
el PDF si el enlace es uno; si es una página que presenta un documento, buscar y descargar ese documento; y, si no
hay documento detrás, guardar la página como PDF. Aprobó los dos primeros y rechazó el tercero (12-11-2026: «el
ultimo punto no. los dos primeros sí»): la biblioteca recoge documentos, no páginas web.

## Decisión

- El miembro puede mandar, en vez del PDF, el enlace del PDF o de la página que presenta el documento. Un enlace
  suelto que acaba en `.pdf` va a la biblioteca, y no al catálogo de recursos. Si lo pide con sus palabras
  («publica en la biblioteca este documento: …»), Claude llama a la herramienta `anadir_documento`.
- `scripts/documento_web.py` descarga el enlace. Si es un PDF, ya está. Si es una página, Claude Haiku 5.5 elige
  entre sus enlaces el del documento que presenta: su PDF o su página propia en el repositorio de quien lo
  publica. Lo hace por número, así que no puede inventarse una dirección. Se siguen como mucho dos saltos: la página
  que se manda, la página del documento y su PDF.
- Si el documento está detrás de una protección contra programas (una respuesta 401, 403, 429 o 503), o en una web
  que solo funciona con JavaScript y no tiene enlaces que seguir, el bot no la salta. Le da a la persona el título
  y el enlace directo del documento para que lo descargue ella y se lo mande. Si la página no presenta ningún
  documento, se lo dice: la página no se guarda como PDF.
- El PDF descargado sigue el mismo camino que uno enviado: comprobación del tema y de repetidos, ficha, licencia
  y visto bueno. Si se va a publicar con el archivo, el bot se lo manda antes a la persona. Así ve lo que se
  publicará, y Telegram le da el identificador con que se publica. Si la licencia no permite compartirlo, se
  publica solo la ficha y el archivo no se sube.
- El enlace de la ficha, si el documento no lo trae, es la dirección de donde se ha sacado el documento, y no se
  gasta la búsqueda web del ADR 0002. Si la persona mandó la página del documento y el PDF está en otro servidor,
  el enlace es esa página y no la del servidor donde se guardan los archivos. Si se llegó por la ficha del
  documento en su repositorio, el enlace es esa ficha.
- La descarga es la misma que la de los recursos del catálogo (`catalogo.descargar`): solo direcciones públicas,
  también en cada redirección (ADR 0019). El PDF puede pesar hasta 50 MB, lo más que un bot puede subir a
  Telegram. El límite de 20 MB es solo para lo que manda la persona, que Telegram no deja descargar a un bot.
- Cuenta para el cupo de documentos del día, como uno enviado.

## Alternativas descartadas

- **Guardar la página como PDF con un navegador sin pantalla** cuando no hay documento detrás: lo rechazó Juanjo.
  Se probó en el NAS con Chromium y funcionaba: 9 s y unos 350 MB de memoria. Pero en la página salían el aviso de
  cookies y la encuesta de la web, y lo que quedaba era la noticia, no el documento.
- **Saltar la protección de UNESDOC** (el repositorio de la UNESCO, tras una comprobación de Cloudflare) con un
  navegador o con su API interna: la protección está puesta a propósito contra la lectura automática.
- **Un navegador para leer las páginas**: con una descarga normal basta. Las páginas que solo funcionan con
  JavaScript son, en las pruebas, justo las de los repositorios que no dejan descargar a un programa.

## Consecuencias

- Coste: elegir el enlace cuesta menos de una décima de céntimo por página (0,0004–0,0008 USD medidos). La ficha
  cuesta lo mismo que la de un PDF enviado.
- En el NAS no hay piezas nuevas: una descarga y una llamada a la API, sin navegador.
- Con los documentos de UNESDOC, que son buena parte de lo que publica la UNESCO, la persona tendrá que
  descargarlos ella, pero recibe el enlace directo.

## Evidencia

Pruebas del 12-11-2026 con `scripts/documento_web.py`, desde el portátil:

- Noticia de la UNESCO «AI Answers. You Decide» → elige `https://unesdoc.unesco.org/ark:/48223/pf0000400013`, que
  no se deja descargar → «no_descargable» con ese enlace y el título del documento (0,0006 USD).
- Noticia de la UNESCO sobre la guía de IA generativa → el enlace de UNESDOC de la guía (0,0008 USD).
- Noticia del INTEF sobre su guía de IA → el PDF de code.intef.es, 3 MB, en 3 s (0,0004 USD).
- Página del MIT del informe de su comité → redirige al PDF de su servidor de archivos. Se descarga, y el enlace
  de la ficha es la página del MIT.
- Un enlace directo a UNESDOC → «bloqueado». La portada de noticias del INTEF → «sin_documento». Una dirección de
  la red de casa → «no_abre».
- Desde el NAS, UNESDOC responde 403 a una descarga normal y la página de comprobación de Cloudflare
  («Just a moment…») a Chromium.

Con una llamada real a la API, «Descarga y publica en la biblioteca <enlace>» y «quiero añadir este documento a la
biblioteca: <enlace>» llaman a `anadir_documento`, y «añade esta app al repositorio <enlace>» sigue llamando a
`anadir_recurso`.

## Validación

`pruebas/test_documento_web.py`, sin red ni API: lectura de enlaces, los caminos de `buscar` (PDF directo,
redirección, anuncio con PDF, anuncio con la ficha de un repositorio, protección, web sin enlaces, página sin
documento, número inventado, tamaño, dirección interna) y el recorrido del bot (subida del archivo solo si se
comparte, enlace de la ficha sin búsqueda, cupo y mensajes de cada caso).
