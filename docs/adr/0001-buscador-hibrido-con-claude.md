# 0001. Buscador híbrido con Claude para el grupo ChatGPT-IA-edu

- Estado: aceptada
- Fecha: 24-10-2026

## Contexto

Juanjo quiere que los miembros del grupo de Telegram ChatGPT-IA-edu (4.057 el
24-10-2026) puedan preguntar en lenguaje natural quién dijo algo, cuándo y en
qué mensaje, y qué documentos de la Biblioteca digital tratan un tema. El
buscador de Telegram ya resuelve la búsqueda por palabras exactas; lo que falta
es encontrar por el sentido («¿quién habló de evaluar sin que copien con IA?»
cuando el mensaje dice «diseñar tareas que hagan imposible no aprender»).
También existe el cuaderno de NotebookLM del grupo, que responde por el sentido
pero no da enlaces a los mensajes ni incluye lo del día.

Condiciones: sin gastos nuevos, con un tope mensual de gasto, y funcionando en
el NAS de casa (Intel N100, 4 núcleos, unos 4 GB
de memoria libres).

## Decisión

1. **Índice propio en el NAS**, con todo el historial del grupo (29.901
   mensajes desde abril de 2023 el 24-10-2026), descargado con la cuenta de
   Juanjo (Telethon): el bot no puede leer lo anterior a su llegada al grupo.
   El archivo diario de memoria-telegram no sirve de fuente: solo guarda los
   identificadores de mensaje desde marzo de 2026 y no guarda los documentos.
2. **Búsqueda híbrida**: por significado (vectores de un modelo de
   *embeddings* que corre en el propio NAS, sin servicio de pago) y por
   palabras (SQLite FTS5, para nombres propios y términos exactos),
   combinadas por fusión de rangos recíprocos (RRF, k = 60).
3. **Claude Haiku 5.5 con herramientas** interpreta la pregunta, decide las
   búsquedas (con filtros de autor y fechas), lee los resultados y responde con
   fecha, autor y enlace de cada mensaje. Nunca lee el grupo entero.
   Lee la pregunta por su intención, aunque traiga erratas (desde el
   27-10-2026: «orgasmos» por «órganos» le hacía buscar otra cosa).
4. **Biblioteca digital como colección aparte**: cada aportación (título,
   portada, PDF, ficha y comentarios, aunque vayan en mensajes separados) es
   una obra. De cada PDF se guarda el texto de sus 4 primeras páginas, porque
   muchos se compartieron solo con el nombre del archivo.
5. **Lo borrado se borra**: cada madrugada se rehace el historial entero y lo
   que ya no está en Telegram desaparece del índice.
6. **Gasto acotado en tres capas** (el cupo diario fijo se sustituyó el 27-10-2026 por frenos que no se ven: ADR 0006): tope del espacio de trabajo en la consola
   de Claude, tope propio del bot (`TOPE_MES_USD`) y cupo de 20 preguntas diarias por
   persona.

## Alternativas descartadas

- Pasar el grupo entero a Claude en cada pregunta: millones de tokens por
  consulta, inviable con el presupuesto.
- Solo palabras clave: es lo que ya hace Telegram.
- Un servicio de *embeddings* de pago (Voyage, OpenAI): gasto nuevo.
- Qwen3-Embedding-0.6B: 1,8 textos/s en el portátil, casi 4 horas para el
  índice inicial; demasiado pesado para el NAS.

## Validación

20 preguntas redactadas como las haría un miembro, sin las palabras exactas
del mensaje buscado (`datos/preguntas-prueba.json`, fuera del repositorio porque citan mensajes y personas reales de los grupos): 14 de mensajes y 6 de la
biblioteca. Se mide en qué puesto sale el mensaje esperado
(`pruebas/comparar_modelos.py`) y si la respuesta final cita su enlace
(`pruebas/extremo.py`).

| Modelo | Velocidad (portátil) | Puesto ≤ 5 | Puesto ≤ 20 |
|---|---|---|---|
| potion-multilingual-128M | instantáneo | 40 % | 45 % |
| paraphrase-multilingual-mpnet-base-v2 | 12,8 textos/s | 35 % | 45 % |
| **embeddinggemma-300m** (elegido) | 9,2 textos/s | 55 % | 65 % |

Solo la búsqueda por significado y con la pregunta tal cual; en la biblioteca,
EmbeddingGemma pone la obra esperada en primer lugar en 5 de 6 preguntas.

Con el bot entero (búsqueda híbrida + Claude Haiku 5.5, esfuerzo medio), el
24-10-2026: 16 de 20 respuestas citan el enlace esperado, a 0,0017–0,0025 USD
por pregunta y 4–6 s en el portátil. Varía de una pasada a otra (una pregunta
fallida en una pasada acierta en otra). Las que fallan son las más rebuscadas;
en una, «las cuentas» se entendió como cuentas de usuario y no como cálculos.

Sonnet 5.5 en lugar de Haiku, 28-10-2026, con las mismas 20 preguntas: 16
aciertos, igual que Haiku (15 a 17 en seis pasadas), a 0,066 USD por pregunta,
unas 20 veces más. Falla otras cuatro, pero tres de ellas también las falla
Haiku a menudo: el límite está en lo que encuentra la búsqueda, no en el
modelo. Por eso se queda Haiku, a diferencia de Karla bot (ADR 0008), que
tiene que explicar la documentación y no solo encontrar mensajes.

En la primera pasada Claude construyó un enlace a partir del número interno de
una obra en vez de copiar el suyo. Desde entonces las herramientas de la
biblioteca no le dan ese número y el sistema le exige copiar los enlaces.

Erratas, 27-10-2026: «Dame ideas» para un trabajo «de los orgasmos del cuerpo…
de lo órganos» pasa a buscar «órganos del cuerpo humano» en lugar de contestar
que no hay nada de orgasmos; «quien hablo de notebok lm para prepara clases»
encuentra los mensajes de NotebookLM; «¿quién habló de criar caracoles en Marte
con IA?» sigue sin resultado, sin reinterpretar lo que estaba bien escrito.

## Riesgos

- La sesión de Telegram es una copia de la de Juanjo; Telegram anula una
  sesión usada a la vez desde dos IP, pero el NAS y el portátil salen por la
  misma. La pasada completa va a las 3 para no coincidir con memoria-telegram.
- Las preguntas y los mensajes encontrados se procesan en Anthropic (Estados
  Unidos, única ubicación disponible). El grupo es público y el bot lo dice en
  su presentación.
- Un mensaje del grupo puede contener instrucciones dirigidas a la IA: el
  sistema las trata como datos y el bot solo tiene herramientas de lectura.

## Varios grupos

Desde el 27-10-2026 el bot busca también en Vibe Coding Educativo, con un
índice por grupo: ver [ADR 0003](0003-varios-grupos.md).

## El bot en el grupo

El 24-10-2026 se añadió al grupo, a petición de Juanjo, para que conteste a
quien lo mencione allí que solo atiende por privado y para poder comprobar si
quien le escribe es miembro. Se pidió como administrador sin permisos, pero
Telegram no lo admite: sin ninguno lo deja como miembro normal, y así
`getChatMember` no reconocía a los miembros (`PARTICIPANT_ID_INVALID`).
Es administrador con un solo permiso, invitar usuarios, inocuo en un grupo
público; Telegram le añade la marca interna `other`.

Validación, el mismo día, como administrador: `getChatMember` devuelve
«creator» para Juanjo, «administrator» y «member» para dos miembros, y error
para una cuenta que no está en el grupo, que el bot trata como no miembro.
Como administrador recibe todos los mensajes del grupo; el bot solo contesta
a los que lo mencionan, le responden o llevan uno de sus comandos (desde el
29-10-2026, [ADR 0006](0006-limites-sin-cupos-fijos.md)) y descarta el resto sin gastar nada.

## Nombre del bot

El usuario de un bot de Telegram no se puede cambiar (comprobado en el menú de
BotFather el 24-10-2026: deja editar nombre, descripción, foto y comandos, no
el usuario), así que cada cambio de usuario es un bot nuevo con su token. Desde
el 24-10-2026 es **Bot de IA Educativa (@IAEducativa_bot)**; @IAEducativaBot
estaba cogido. Antes se llamó Buscador IA (@BuscaIABot), que nadie llegó a usar y se borró
el mismo día, y @ChatGPTeduBuscadorBot, que tampoco se usó.
