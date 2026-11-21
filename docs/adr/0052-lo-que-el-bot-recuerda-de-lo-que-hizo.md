# 52. Lo que el bot recuerda de lo que hizo, y rehacer el anuncio de «¡Comparte tu App!»

Fecha: 2026-11-21 · Estado: aceptado

## Contexto

En la revisión de las preguntas sin resolver del 21-11-2026 (ADR 0007), las ocho del Bot de IA Educativa
desde el 14-11 dejaron ver dos fallos de fondo:

- **El bot no sabía qué había hecho antes.** De cada respuesta anterior, el historial guardaba solo el
  texto: ni las búsquedas ni los mensajes que el programa manda por su cuenta con botones (la ficha, el
  anuncio para «¡Comparte tu App!»). Según el registro del contenedor:
  - El 18-11, la respuesta a «Uso de la IA para Docentes» se dio con 3 búsquedas, y en la siguiente el bot
    se corrigió en falso: «no la había comprobado con búsquedas».
  - El 21-11, una respuesta se dio con 0 búsquedas y el bot dijo que había buscado la app. En la misma
    conversación negó haber escrito un mensaje para el grupo que el programa le acababa de enseñar.
- **Un anuncio quitado no se podía rehacer.** El 21-11, el bot publicó en «¡Comparte tu App!» el anuncio de
  un simulador, en catalán, y su autora lo quitó al momento. Después pidió el mismo mensaje en castellano
  y que lo publicara. El modelo se lo ofreció («només el publicaré si ho confirmes») y luego tuvo que decir
  que no podía, algo que ya prohibía la regla «Sin promesas» del ADR 0038. Al final lo publicó ella copiando
  el texto.

Y tres detalles: «Educación musical» quedó como no resuelta aunque la respuesta daba cinco recursos; otra
respuesta decía que algo «tampoco aparece en la Biblioteca digital, aunque no la he buscado»; y otra mostró
el nombre interno de una herramienta («ho farem amb `cambiar_ficha`»).

## Decisión

1. **Las búsquedas de cada respuesta, en el historial.** Al guardar la respuesta en la memoria de la
   conversación, el programa le añade «[Nota del programa: para esta respuesta se hicieron N búsquedas:
   buscar_mensajes «…»; …]» o «… se dio sin hacer ninguna búsqueda» (`consultar.nota_busquedas`). Quien
   pregunta no la ve: solo la lee el modelo en las preguntas siguientes. Vale también para Karla, que
   guardaba el historial igual.
2. **Lo que manda el programa, en la conversación.** Cada vez que el programa publica un recurso o guarda
   sus cambios, enseña el anuncio para «¡Comparte tu App!», lo publica, lo quita, lo cancela o da el texto
   para publicarlo uno mismo, apunta una nota (`Bot.nota_programa`). Las notas entran como «[Nota del
   programa: …]» delante del siguiente mensaje de la persona y se quedan en el historial. Caducan con la
   conversación (30 minutos) y se guardan como mucho cuatro.
3. **Las instrucciones lo explican**: las notas las escribe el programa, lo que cuentan ha pasado, el modelo
   no las escribe ni las menciona y, si una respuesta anterior se dio sin buscar, busca antes de confirmar
   lo que decía. Si aun así imita una nota, `quitar_marcas` la quita antes de enviar.
4. **Rehacer el anuncio.** Al quitar del grupo un anuncio publicado por el bot, sale el botón «Rehacer el
   anuncio». Con él se pide el cambio con palabras (otro idioma, otro texto) y vuelve al circuito de
   siempre: se enseña el mensaje con «Publicar», «Cambiar», «Lo publico yo» y «Cancelar». Vale durante
   48 horas desde la publicación, las mismas en que Telegram deja borrarlo, y una vez por anuncio. Un
   anuncio publicado antes de reiniciarse el bot se quita igual, sin el botón (el anuncio solo se guarda en
   memoria, como el resto del circuito). «Sobre ti» dice que el anuncio se maneja solo con sus botones.
5. **Los detalles.** Las instrucciones dicen que no es «sin resultado» si se dan mensajes, documentos o
   recursos que responden a lo pedido, y que no se dice que algo no está en un sitio donde no se ha
   buscado. Los nombres de las herramientas no se dejan a las instrucciones: `consultar.sin_nombres_internos`
   quita «con `x`» y sus variantes en los cinco idiomas y cambia el nombre suelto por palabras normales
   («cambiar la ficha», «la búsqueda»). En los dos bots.

## Alternativas descartadas

- **Guardar en el historial las llamadas a las herramientas con sus resultados**: el historial crecería con
  miles de caracteres por respuesta que se mandan en cada pregunta siguiente. El modelo solo necesita saber
  qué buscó para no contradecirse; si hace falta el contenido, busca otra vez.
- **Una herramienta del modelo para publicar en el grupo**: publicaría sin que la persona vea antes el
  mensaje con sus botones, que es la condición de Juanjo desde el 27-10-2026.
- **Actualizar el anuncio del grupo al cambiar una ficha ya anunciada** (lo pidió alguien el 20-11): hay que
  guardar qué mensaje del grupo corresponde a cada recurso, más allá de las 48 horas. Queda para más
  adelante, si Juanjo lo pide.

## Consecuencias

- Cada pregunta de seguimiento lleva unas decenas de palabras más por intercambio: sin coste apreciable.
- Si el modelo dice que buscó o que no buscó, ahora puede comprobarlo; lo que cuente sigue siendo una
  respuesta del modelo, no una comprobación del programa.

## Validación

- 15 pruebas nuevas sin red ni API (`pruebas/test_memoria_programa.py`) y las 266 de la carpeta, en verde;
  `ruff check --select E9,F`, en verde (también se quitó una importación sobrante de
  `test_revision_biblioteca.py`, que dejaba en rojo la comprobación de GitHub).
- `pruebas/simular_catalogo.py`, con Claude de verdad: publicar el anuncio, quitarlo, «Rehacer el anuncio»,
  pedirlo «en catalán» y recibir el mensaje rehecho en catalán con sus botones; la conversación siguiente
  lleva las notas y las búsquedas. La simulación estaba rota desde hace días (le faltaban el antispam y
  otros diccionarios, y los botones de la ficha llevan clave): se arregló. Quedan cinco comprobaciones
  que fallan igual con el código anterior, por partes de la simulación que no se pusieron al día con
  cambios posteriores (la pregunta de a dónde va un enlace y los botones con clave de la Biblioteca).
- Con Haiku, en el contenedor del NAS, dos casos de la revisión: a «¿Esto lo has comprobado o te lo has
  inventado?», con la nota de tres búsquedas, ya no se acusa en falso (lo comprueba buscando); a «el mismo
  mensaje en castellano, y publícalo», tras las notas de publicado y quitado, explica que se hace con el
  botón «Refer l'anunci» y no promete publicarlo.

## Riesgos y limitaciones

Las notas son información para el modelo, no una comprobación: puede no hacerles caso alguna vez. Se vigila
en las revisiones de las preguntas sin resolver.
