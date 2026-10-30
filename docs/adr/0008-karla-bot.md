# 8. Karla bot: el cuaderno de eXeLearning, como bot de Telegram

Fecha: 2026-10-27 · Estado: aceptado

## Contexto

El grupo de Telegram eXeLearning tenía un asistente en NotebookLM, el
cuaderno «Karla - Experta en eXeLearning», con 88 fuentes: las conversaciones
del grupo desde 2019 y la documentación que prepara cada día `memoria-telegram`
(manual de usuario, documentación técnica del programa y de su formato,
complementos de Moodle y WordPress, eXeViewer y utilidades). Juanjo quiso un
bot aparte para el grupo que lo sustituyera, si podía hacerse de forma barata.

El cuaderno exige cuenta de Google y otra web, recibe las conversaciones una
vez al día y no dice cuánto se usa ni qué no sabe responder.

## Decisión

1. **Un segundo bot con el mismo programa.** @eXeKarlaBot, nombre visible
   «Karla bot» (Juanjo: «así queda claro que no es una persona»), en
   femenino. `scripts/karla.py` reutiliza `bot.py` (Telegram, idioma, límites,
   preguntas sin resolver y cuentas) con sus propios archivos
   (`datos/estado-karla.json`, `datos/sin-resolver-karla.jsonl`) y sus textos
   en cinco idiomas (`scripts/textos_karla.py`). No hay biblioteca ni catálogo.
2. **Las mismas fuentes y las mismas instrucciones que el cuaderno.** Las
   instrucciones de Karla se copiaron del cuaderno (`scripts/karla_persona.md`)
   y se adaptaron a un bot multilingüe. La documentación se lee de donde la
   genera `memoria-telegram` en el NAS, montada en solo lectura; no se copia.
3. **La documentación, troceada por apartados** (`scripts/documentacion.py`):
   cada trozo lleva el documento y la ruta de encabezados; las tablas se parten
   por filas con su cabecera repetida, y la búsqueda puede limitarse a un
   documento (el registro de cambios, el manual…). Al ponerse al día solo se
   recalculan los trozos que cambian.
4. **Claude Sonnet 5.5, con Claude Haiku 5.5 de reserva.** Sonnet hasta un gasto
   del mes (`CAMBIO_USD`); desde ahí, Haiku hasta el día 1, para no dejar de
   responder, con un tope propio (`TOPE_MES_USD`) y otro en el espacio de
   trabajo «Karla bot» de la consola de Claude.
5. **Puesta al día cada 15 minutos**, en el mismo reloj que los otros dos
   grupos (`nas/bucle.sh`), con una sola sesión de Telegram.
6. **Abierta a los miembros del grupo eXeLearning** desde el 27-10-2026, tras
   probarla solo con Juanjo. Es administradora del grupo con el mínimo de
   permisos (invitar usuarios), como el otro bot en el suyo, y está enlazada
   en el mensaje fijado del grupo. Solo funciona en Telegram, por privado, y
   lo sabe: a «¿te puedo integrar en un foro de Moodle?» responde con «Sobre
   ti» que no, sin guardarlo como pregunta sin resolver (29-10-2026, ADR 0007).
7. **Sabe de su grupo.** Lo lee de Telegram al arrancar y lo incluye en sus
   instrucciones (`actualizar_entorno`):
   - los administradores (solo personas);
   - el nombre y la descripción del grupo;
   - el mensaje fijado, con sus enlaces escritos.

   Lo vuelve a leer cuando alguien gana o pierde el cargo, cuando se fija o
   se edita el mensaje fijado y, por si se perdiera el aviso, cada seis horas.
   Juanjo le preguntó quién administraba el grupo y contestó que no lo sabía.
   Ahora responde sin buscar y distingue a quien administra el grupo del
   equipo que desarrolla eXeLearning.
8. **Habla para profesorado, no para informáticos** (28-10-2026). Juanjo
   vio que a veces era demasiado técnica: debe dar información fiable y
   completa, pero que el profesorado entienda. Sus instrucciones
   (`karla_persona.md`, «Cómo hablas») le piden contar la consecuencia
   práctica y no cómo funciona por dentro. Usa los términos del programa,
   pero no los de informática, y explica en pocas palabras los que sean
   imprescindibles. Cuando la solución depende de otra persona, dice quién
   la pone y qué hay que pedirle. Nombra las fuentes en palabras corrientes,
   avisa antes de dar código y lo da listo para copiar. Con quien escribe
   en lenguaje técnico, responde en el mismo registro.
9. **Sabe cuál es la última versión** (30-10-2026). A «¿cuál es la última
   versión?» respondió que la 4.0.3, con la 4.0.6 ya publicada e indexada.
   La búsqueda devuelve apartados del registro de cambios por parecido, no
   por orden, y el de la 4.0.4, que no tiene notas porque el equipo se saltó
   esa versión a propósito, le hizo creer que no había nada después. Ahora
   el programa, sin IA, toma la primera versión con fecha del registro de
   cambios oficial (`version_vigente`) y se la da en sus instrucciones;
   `karla_persona.md` explica lo de la 4.0.4.
10. **Sabe quién es del equipo de eXeLearning** (30-10-2026). Antes era una
    lista de nombres escrita a mano en sus instrucciones, incompleta (faltaban
    Manuel Narváez y Pablo Amaya) y ambigua (hay dos «Ernesto» en el grupo).
    No hay una lista pública: la web no la da, la organización de GitHub no
    tiene miembros públicos y quien aporta código no es todo el equipo (la
    coordinación no programa). Ahora la lista va por cuenta de Telegram en
    `datos/equipo-exelearning.json`, fuera del repositorio porque son datos de
    personas, y entra en la copia diaria de IONOS. Los mensajes del equipo le
    llegan a Karla marcados con «equipo»: true, y sus nombres van en sus
    instrucciones. Una vez por semana, un programa sin IA cuenta los cambios
    aceptados por persona en los repositorios de eXeLearning en seis meses; a
    quien pasa de 5 y no está decidido se le pregunta a Juanjo, con la persona
    del grupo que más se le parece (mismo usuario o mismas palabras del
    nombre) y dos botones, «Es del equipo» y «No lo es». Lo decidido no se
    vuelve a preguntar.

## Alternativas descartadas

- **Seguir con el cuaderno.** Es gratis, pero tarda unos 30 segundos por
  respuesta, no enlaza el mensaje exacto del grupo, recibe las conversaciones
  una vez al día y no da estadísticas de uso.
- **El bot con Haiku.** Cuesta unos 0,003 USD por pregunta, pero en la prueba
  respondió peor que el cuaderno en 7 de 30 preguntas (citas mal etiquetadas,
  un «lo he probado» falso, un enlace roto).
- **Un bot nuevo desde cero.** Duplicaría lo que ya resuelve `bot.py`.
- **Sacar el equipo solo de GitHub.** Dejaría fuera a quien coordina sin
  programar y metería a cualquiera con un par de cambios; y los nombres de
  GitHub no coinciden con los de Telegram («cvaldera», «Pablo A»), así que
  emparejarlos sin que nadie lo confirme sería frágil.
- **Un repositorio para cada bot.** Karla reutiliza casi todo `bot.py`
  (Telegram, idioma, límites, cuentas) y el buscador. En repositorios
  separados habría que copiar ese código o sacarlo a una biblioteca común,
  y cada cambio tendría que llegar a los dos. En uno solo, una corrección
  vale para los dos bots a la vez, y en el NAS comparten imagen, modelo de
  significado (ADR 0012) y sesión de Telegram (decisión 5).

## Evidencia

Comparación del 27-10-2026 con 30 preguntas reales del grupo, juzgadas contra
las respuestas del equipo, el manual y el registro de cambios (informe
personal de Juanjo: `Informes/bot-chatgpt-ia-edu/2026-10-27-karla-bot-frente-al-cuaderno.md`):

| | Cuaderno | Haiku 5.5 | Sonnet 5.5 |
|---|---|---|---|
| Tiempo medio | 30 s | 8 s | 8 s |
| Coste por pregunta | gratis | 0,003 USD | 0,05 USD |
| Frente al cuaderno: mejor / empate / peor | — | 2 / 21 / 7 | 6 / 23 / 1 |

Lecciones de la prueba, aplicadas:

- La documentación técnica y el registro de cambios están en inglés: el bot
  busca también en inglés y puede limitar la búsqueda a un documento.
- La copia de la documentación del portátil llevaba sin actualizarse desde el
  08-09-2026: la buena es la del NAS. Por eso se monta de allí.
- El bot se atribuía respuestas que había dado el cuaderno («la ruta que te di
  antes») y suponía que quien pregunta era quien escribió un mensaje parecido:
  los mensajes que hablan de «Karla» llevan una nota, y las instrucciones piden
  contar lo del grupo en tercera persona.
- El manual de usuario se había quedado en la 4.0.1 con la 4.0.5 publicada:
  desde el mismo día, `memoria-telegram` busca solo la última versión.

Prueba del lenguaje (28-10-2026). Se hicieron 6 preguntas reales del grupo
con Sonnet, con las instrucciones de antes y con las de ahora. Antes salían
Docker, el fichero `.env`, «el README de mod_exescorm» y «el código fuente»;
ahora no, y se mantienen los mismos datos, enlaces y versiones. En la
primera redacción, por explicar sencillo, se inventó la causa de un fallo
que no estaba en las fuentes. Se añadió que «explicar sencillo no es
suponer», se repitió la pregunta dos veces y no volvió a pasar. Lo que solo
se resuelve con código lo sigue dando, pero ahora lo anuncia y explica cómo
deshacerlo.

## Riesgos

- **Cuántas preguntas recibirá no se sabe**: NotebookLM no da estadísticas. El
  gasto depende de cuántas haya; los topes impiden pasar del límite fijado.
- **Las respuestas de un modelo cambian algo de una vez a otra**: en la
  prueba, Haiku acertó en una ronda preguntas que falló en otra.
- **La memoria del NAS**: al principio cada bot cargaba su copia del modelo de
  significado (unos 900 MB). Con 3,5 GB libres el 27-10-2026 parecía que cabían
  los dos, pero un día después el NAS ya tiraba de swap; desde el 29-10-2026,
  los dos bots y el índice usan una sola copia (ADR 0012).
