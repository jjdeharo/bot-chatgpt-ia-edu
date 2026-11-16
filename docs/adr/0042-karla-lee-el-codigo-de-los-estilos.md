# 42. Karla lee el código de los estilos

Fecha: 2026-11-16 · Estado: aceptado

## Contexto

Karla resume los archivos que le mandan (ADR 0021): de un `.elpx`, las propiedades, las páginas, los iDevices y
el principio de `content.xml`; de un ZIP sin `content.xml`, solo la lista de la raíz. El 14-11-2026 alguien le
preguntó por un estilo propio cuyo menú lateral funcionaba en la vista de móvil pero no en la de ordenador, en la
previsualización y en la exportación. Mandó el proyecto y después el estilo en ZIP. Karla respondió que no podía ver
lo que había dentro de `style.css` ni de `style.js`, dio pistas generales y las ocho preguntas de esa conversación
quedaron como «sin resultado». Juanjo lo vio el 16-11-2026 y pidió que leyera el código del estilo.

Medido ese día con los once estilos oficiales de eXeLearning (`public/files/perm/themes/base`): entre `config.xml`,
`style.css` y `style.js` ocupan de 22.000 caracteres (base) a 77.000 (eTwinning, CEDEC, INTEF y Kids). Un estilo
propio suele partir de uno de ellos. Un `.elpx` guarda siempre su estilo en `theme/` (`ElpxExporter.ts`), también
el oficial.

## Decisión

- **Un ZIP que es un estilo** (un `config.xml` con un `style.css` al lado, en la raíz o dentro de una carpeta) se
  presenta como estilo, no como «proyecto no reconocible», y lleva su `config.xml`, `style.css` y `style.js`.
- **Un `.elpx` con un estilo propio** lleva los mismos archivos de `theme/`. Si el estilo es uno de los once
  oficiales (`ESTILOS_OFICIALES`), solo se dice cuál es: los conoce la documentación y costarían sin aportar.
- **CSS y JS sin comentarios de bloque, sin líneas que solo son un comentario `//` y sin sangría ni líneas en
  blanco** (`compactar`): no cambia lo que hace el código y el oficial más grande baja a unos 58.000 caracteres.
- **Tope de 80.000 caracteres entre los tres** (`MAX_ESTILO`), que cabe entero en todos los oficiales. Si un estilo
  pasa, va entero primero `config.xml`, después `style.css`, y lo que se corta lleva «[… recortado: faltan N
  caracteres de …]». Las instrucciones de Karla le dicen que busque la causa concreta en el código, diga qué reglas
  cambiar y no dé por revisado lo que llega recortado.
- **Las imágenes, fuentes e iconos del estilo no se pasan**: solo cuántos hay.
- Como el resto del adjunto, al historial de la conversación pasan solo los primeros 1.000 caracteres de la
  pregunta (`bot.py`): una pregunta de seguimiento no vuelve a pagar el estilo, pero tampoco lo ve. Si hace falta,
  la persona lo vuelve a mandar.

## Alternativas descartadas

- **20.000 caracteres**, la primera propuesta: no cabía entero ni el estilo oficial más pequeño.
- **Pasar siempre el estilo de un `.elpx`**, también el oficial: unos 20.000 tokens más en cada proyecto que manden,
  para nada.

## Consecuencias

- Una pregunta con un estilo cuesta unos 20.000 tokens más de entrada: en la prueba, 0,064 USD con Sonnet 5.5, sin
  búsquedas. Las búsquedas siguientes de la misma respuesta leen el estilo de la caché. Llegan pocas: la del
  14-11-2026 fue la primera.

## Validación (16-11-2026)

- Los once estilos oficiales, comprimidos sueltos y uno (eTwinning) dentro de su carpeta: se reconocen como estilo
  y caben enteros (de 17.000 a 58.000 caracteres el resumen completo).
- Tres `.elpx` reales (guía de software libre con «neo», manual de EdEX y un proyecto de prueba con «base»): dicen
  el estilo oficial y no añaden su código.
- Con Claude, de extremo a extremo: el estilo «zen» rebautizado y con una franja decorativa `body::before` fija,
  de 320 px y `z-index: 50`, solo desde 768 px (el caso del 14-11). A «los enlaces del menú no funcionan en vista
  PC, pero sí en móvil» Karla señaló ese bloque como causa, explicó por qué solo en ordenador y propuso
  `pointer-events: none`.
- `pruebas/test_revision.py` (`test_leer_estilo`): estilo en la raíz y en carpeta, comentarios quitados sin tocar
  `'http://x'`, `.elpx` propio y oficial, y recorte con el aviso de lo que falta. Las 201 pruebas pasan en un
  entorno limpio; dentro del contenedor en marcha fallan siete, ajenas a este cambio, porque toman sus variables de
  producción (`JUANJO`, `GRUPOS`…).
