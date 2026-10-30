# 16. Búsqueda en el Repositorio de recursos

Fecha: 2026-10-30 · Estado: aceptado

## Contexto

El Bot de IA Educativa buscaba en los mensajes de los grupos y en la Biblioteca
digital, pero no en el Repositorio de recursos educativos digitales de Vibe
Coding Educativo (https://vibe-coding-educativo.github.io/app_edu/), al que
él mismo añade recursos (ADR 0004). En la primera revisión de las preguntas sin
resolver (ADR 0007, 30-10-2026), cinco de las once eran búsquedas de recursos
por tema («Probabilidad», «Ecuaciones, inecuaciones y sistemas», «Geometría
analítica», «¿Y de probabilidad?», «¿Y de geometría analítica?», 28-10-2026).
El repositorio sí los tenía: 9 fichas mencionan la probabilidad, 7 las
ecuaciones y 6 la geometría. Juanjo pidió hacer el buscador («haz el buscador
del repositorio»).

## Decisión

- **Herramienta `buscar_repositorio`** (`scripts/repositorio.py`). Busca por
  significado y por palabras, combinados con la misma fusión por rangos
  recíprocos que los grupos (`buscador.RRF`). Se indexan el título, la
  descripción, las palabras clave, las áreas, los niveles y el tipo; por
  palabras, también el autor.
- **Las fichas se leen de la hoja del repositorio** con la API que ya usa el bot
  para darlas de alta (`catalogo.Hoja.filas`), cada 15 minutos y en segundo
  plano. Hay una ficha por enlace, la última, igual que en la web
  (`vce-app_edu/script.js`). Si la hoja no responde, el bot sigue buscando con
  lo último que leyó.
- **El significado de cada ficha se calcula una sola vez** y se guarda en
  `datos/repositorio-vectores.npz`, con la huella del texto indexado como
  clave. Solo se recalcula una ficha cuando cambia. Mientras falta el de una
  ficha, esa ficha solo se encuentra por sus palabras.
- **Cada resultado trae lo que ya publica la web**: título, autor, descripción,
  tipo, niveles, áreas, idiomas, licencia y dirección del recurso. El correo de
  quien lo dio de alta no sale nunca. Lo que se cita es el enlace a la ficha
  dentro del repositorio (`catalogo.enlace_catalogo`, `?ids=`), que abre solo
  esa ficha.
- **También en la ayuda para enseñar** (ADR 0011). Una ficha del repositorio
  puede ser fuente de una idea como un mensaje o un documento. La revisión la
  comprueba con el texto de la ficha, y el programa escribe la cita: «título,
  de autor, en el repositorio de Vibe Coding Educativo», en los cinco idiomas.
- **Las instrucciones y la ayuda lo dicen**. Cuando piden recursos,
  aplicaciones o materiales de un tema, aunque sea con una palabra suelta, se
  busca en el repositorio además de en los grupos. La ayuda de /buscar, en los
  cinco idiomas, lo explica con un ejemplo («¿hay alguna aplicación para
  practicar probabilidad?»).
- **La dirección del repositorio se define en un solo sitio**:
  `repositorio.WEB`, que `catalogo.WEB` reutiliza.

## Alternativas descartadas

- **Leer el CSV publicado de la hoja**, como hace la web. No necesita
  credenciales, pero Google lo publica con retraso, y el bot ya tiene la API,
  que da lo que acaba de entrar.
- **Indexarlo en el contenedor del índice**, junto a los grupos. Habría que
  darle las credenciales de la hoja a otro contenedor. Son pocos cientos de
  fichas y caben en la memoria del bot.
- **Calcular el significado al leer la hoja**, sin guardarlo. En el NAS, las
  349 fichas tardaron más de cinco minutos (30-10-2026): cada arranque del bot
  lo repetiría y la primera búsqueda esperaría todo ese tiempo.

## Consecuencias

- El bot lee la hoja cada 15 minutos mientras está en marcha: una llamada a la
  API de Apps Script, sin coste.
- Una búsqueda en el repositorio añade a la respuesta los tokens de hasta 8
  fichas. No hay ningún gasto fijo.
- Al primer arranque, y cuando entren muchas fichas a la vez, el servicio de
  significado trabaja unos minutos en segundo plano (ADR 0012). Las demás
  consultas siguen funcionando, algo más lentas.

## Evidencia

- Preguntas sin resolver: `datos/sin-resolver.jsonl` del NAS, revisado con
  Juanjo el 30-10-2026.
- Recursos por tema: búsqueda en las 349 filas de la revisión del 29-10-2026
  (`Informes/vce-app_edu/2026-10-29-revision-datos/filas-despues.json`).
- Cómo elige la web una ficha por enlace y cómo enlaza a una sola ficha:
  `vce-app_edu/script.js` (repositorio vibe-coding-educativo.github.io,
  `app.key = url`, parámetro `ids`).

## Riesgos y limitaciones

- Las fichas están en castellano (ADR 0005): una consulta en otro idioma se
  encuentra por significado más que por palabras.
- Si la API de la hoja cambia los nombres de las columnas, `catalogo.de_fila`
  deja las fichas vacías y el buscador no encuentra nada. Fallaría a la vez el
  alta de recursos, que ya lo pondría de manifiesto.

## Validación

30-10-2026, en el NAS:

- `repositorio.py` con las consultas de las preguntas sin resolver. Calcular
  el significado de las 349 fichas llevó 8 minutos (de 11:27 a 11:35), y el
  archivo de vectores ocupa 1,1 MB. «Probabilidad» da los simuladores de
  probabilidad total y de distribución binomial, BayesLab y la máquina de
  Galton. «Ecuaciones, inecuaciones y sistemas» da las dos aplicaciones de
  sistemas y el Laboratori d'equacions. «Geometría analítica» da poco, porque
  hay pocos recursos de ese tema.
- Las siete preguntas guardadas, otra vez, con el bot entero (0,27 USD en
  total):
  - Las tres de matemáticas responden con fichas del repositorio y mensajes
    de los grupos. La de geometría analítica sigue marcada «sin resultado»,
    porque lo encontrado es poco específico.
  - La de traducir al euskera explica qué permite cada licencia.
  - La del canal responde con «Sobre ti» que no se le puede añadir.
  - La de LaTeX encuentra un GPT especializado y un asistente de Poe.
  - La del seguimiento por competencias, por la ayuda para enseñar, cita dos
    fichas del repositorio con la cita que escribe el programa.
- Al reiniciar, el bot lee los vectores del disco y no recalcula nada.
