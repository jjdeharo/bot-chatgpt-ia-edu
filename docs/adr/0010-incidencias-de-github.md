# 10. Incidencias de GitHub desde Karla bot

Fecha: 2026-10-27 · Estado: aceptado

## Contexto

Al anunciar Karla bot en el grupo, Ernesto Serrano, del equipo de
eXeLearning, propuso que el bot abriera una incidencia en GitHub cuando una
consulta fuera un error. Que el bot lo hiciera por su cuenta tenía estos
problemas:

- **Incidencias falsas.** La mayoría de las dudas del grupo son de uso o de
  la plataforma donde se publica, no fallos del programa.
- **Incidencias sin datos.** Quien pregunta casi nunca da la versión ni los
  pasos para reproducir el fallo.
- **Privacidad.** Se publicarían en GitHub el texto y los datos de alguien sin
  que lo hubiera decidido.

La primera alternativa fue preparar la incidencia para que la abriera la
propia persona. Juanjo señaló que la mayoría no tiene cuenta de GitHub, y
también que casi nadie sabe qué es una incidencia (*issue*) ni para qué
sirve.

## Decisión

1. **Buscar siempre.** Karla tiene `buscar_incidencias` (búsqueda de GitHub
   en todos los repositorios de la organización `exelearning`) y
   `leer_incidencia` (el texto y los últimos comentarios). Si lo que le
   cuentan parece un fallo, mira el registro de cambios y las incidencias. Si
   ya existe una, da el enlace y su estado.
2. **Abrir solo con el visto bueno de la persona.** Si no existe:
   - Karla explica en una frase qué es una incidencia y pide los datos que
     falten: versión, sistema, navegador y pasos.
   - Prepara el borrador en inglés con `preparar_incidencia`, sin datos de la
     persona y sin inventar ninguno.
   - El bot enseña el borrador con un texto fijo que explica qué es una
     incidencia, que es pública, que va en inglés y que no lleva datos de la
     persona, y con dos botones: «Enviar al equipo» y «No enviar».
   - Sin la pulsación no se publica nada. El borrador caduca a las 24 horas.
3. **Cuenta de máquina propia, eXeKarlaBot**, creada por Juanjo. Su clave
   clásica tiene solo el permiso `public_repo`: abrir incidencias y comentar
   en repositorios públicos. Cada incidencia lleva al pie que la redactó el
   bot a partir de una consulta y que la persona la revisó.
4. **Sin etiquetas.** Según la documentación de la API de GitHub, las
   etiquetas de quien no tiene permiso de escritura se descartan sin aviso. El
   equipo encuentra las del bot buscando `author:eXeKarlaBot`.
5. **Límites.** Entre todas las personas, `INCIDENCIAS_DIA` (3) incidencias al
   día, salvo Juanjo, para que un error del bot no llene el repositorio. Las
   capturas no se pueden adjuntar por la API, así que el texto describe lo
   que mostraban.
6. **Interruptor `INCIDENCIAS`** en el servicio `karla`:
   - vacío: solo se buscan incidencias;
   - `dueño/repositorio`: todas se abren ahí y solo se le ofrece a Juanjo
     (pruebas);
   - `1`: se abren en el repositorio de eXeLearning que corresponda.

## Consecuencias

- Las pruebas usan `eXeKarlaBot/pruebas`, un repositorio público de la
  cuenta del bot.
- Probado en el NAS con un fallo de ejemplo, la eñe de la sopa de letras en
  SCORM:
  - En el primer mensaje, Karla buscó en la documentación, el grupo y las
    incidencias, no encontró nada, pidió versión, plataforma y dónde se ve el
    fallo, y explicó qué es una incidencia.
  - En el segundo, con los datos, preparó un borrador completo en inglés.
  - Se le había colado un dato no dado («standard SCORM activity»), y se le
    añadió la instrucción de no inventar ninguno.
- Juanjo lo probó en Telegram: la incidencia de prueba se abrió en
  `eXeKarlaBot/pruebas` (#1, cerrada después). Con eso decidió abrirlo a todo el grupo el mismo
  día (`INCIDENCIAS: "1"`). La propuesta era de Ernesto Serrano, del equipo de
  eXeLearning, que ya había apuntado que las que no procedan se pueden cerrar
  como «not planned».

## Las que ha abierto Karla (28-10-2026)

Karla no sabía cuáles había abierto: buscar_incidencias busca por tema y no por
autor. Juanjo lo vio al preguntárselo, y además /estado decía 2 cuando en GitHub
había 1, porque el contador del bot sumaba la de prueba de `eXeKarlaBot/pruebas`.

- La herramienta `mis_incidencias` las pide a GitHub (`author:eXeKarlaBot
  org:exelearning`), con su estado de hoy, y Karla termina con el enlace a la
  lista completa en la web de GitHub, que se abre sin cuenta. La idea del
  enlace filtrado es de Juanjo; se dan las dos cosas.
- /estado cuenta también desde GitHub: abiertas, cerradas, las últimas con su
  enlace y la lista completa. El contador propio sigue para el tope diario y
  solo se muestra si GitHub no responde, dicho como tal.
- Comprobado el 28-10-2026: «¿cuántas incidencias has creado?» → la #2646,
  abierta, con su enlace y el de la lista.
