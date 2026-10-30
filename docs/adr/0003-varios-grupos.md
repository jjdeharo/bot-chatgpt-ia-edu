# 3. Búsqueda en varios grupos: ChatGPT-IA-edu, Vibe Coding Educativo y EduMedia-IAG

Fecha: 2026-10-27 · Estado: aceptado

## Contexto

Juanjo quiere ampliar el bot al grupo Vibe Coding Educativo (@vceduca, 1.806
miembros el 27-10-2026), que también creó y administra. El ADR 0001 ya preveía
varios grupos: un índice por grupo y lo propio de cada uno fuera del código.

Primero se planteó que cada persona buscara solo en los grupos de los que es
miembro. Juanjo lo cambió el mismo día: «quiero que perteneciendo a uno de los
grupos se pueda consultar en los 2».

## Decisión

1. **Un grupo, una carpeta.** `scripts/grupos.py` define cada grupo (nombre,
   @usuario, id y, si lo tiene, el tema de la Biblioteca digital). Sus datos
   van en `datos/<clave>/`: `chatgpt`, `vce` y `edumedia`. `GRUPOS` en el entorno elige
   los que están en marcha.
2. **Un índice por grupo**, construido igual que el de ChatGPT-IA-edu
   (ADR 0001). Los ids de mensaje se repiten de un grupo a otro, así que lo
   que ve Claude lleva el grupo delante (`vce:1234`).
3. **Basta con ser miembro de un grupo para buscar en todos.** El bot lo
   comprueba con `getChatMember` grupo por grupo y guarda la respuesta una
   hora, como antes.
4. **Cada búsqueda mira en todos los grupos a la vez** y mezcla los resultados
   por sus puntos de fusión (RRF), que son comparables porque todos los índices
   usan el mismo método. Si la pregunta nombra un grupo, Claude limita la
   búsqueda a ese. Cada mensaje citado dice de qué grupo es.
5. **La Biblioteca digital sigue siendo de ChatGPT-IA-edu.** VCE no tiene un
   tema equivalente: su catálogo de aplicaciones es otra cosa (`app_edu`).
   EduMedia-IAG solo aporta la búsqueda.
6. **El bot, administrador de VCE** con el permiso de invitar usuarios, como
   en ChatGPT-IA-edu: sin ser administrador, `getChatMember` no reconoce a los
   miembros (ADR 0001). El 27-10-2026 Juanjo le dio también el de fijar
   mensajes, para que fijara él su aviso de la revisión del repositorio.

## Alternativas descartadas

- Buscar solo en los grupos de quien pregunta: era el primer plan; Juanjo
  prefirió el acceso común. No expone nada nuevo: los dos grupos son públicos
  (tienen @usuario) y se pueden leer en Telegram sin entrar.
- Un índice común para los dos grupos: obliga a renumerar los mensajes y a
  rehacerlo todo cuando se añade o se quita un grupo.
- Un bot por grupo: dos tokens, dos procesos y el modelo de significado cargado
  dos veces en un NAS con unos 4 GB libres.

## Consecuencias

- Los datos de ChatGPT-IA-edu pasan de `datos/` a `datos/chatgpt/`. El cambio
  se hizo a mano en el portátil y en el NAS, con el bot parado; el estado del
  bot (`estado-bot.json`), los modelos y las instrucciones de las fichas
  siguen en `datos/`.
- El cupo diario y el tope de gasto son comunes a todos los grupos.

## Evidencia

- Los dos grupos son supergrupos con temas y muestran el historial a los
  miembros nuevos (`hidden_prehistory = False` en `GetFullChannelRequest`,
  27-10-2026).
- VCE: 9.790 mensajes desde su creación y cuatro temas («General»,
  «¡Comparte tu App!», «Resumen semanal» y «¿Por dónde empiezo?»).

## Buscar en un solo grupo durante la conversación

Juanjo, 27-10-2026: el grupo elegido «debería quedar fijado en esa sesión a no
ser que se diga lo contrario». `/buscar` ofrece un botón por grupo y «Todos los
grupos»; también se fija diciéndolo («busca solo en VCE») o con una pregunta
que nombre un grupo: si todas las búsquedas de una respuesta se limitan al
mismo grupo, el código lo deja fijado, porque Claude no siempre usa la
herramienta `cambiar_ambito` (en la primera prueba limitó la búsqueda sin
fijarla). Dura lo que la conversación (30 minutos sin escribir) o hasta que se
pide otro o todos. Mientras está fijado, cada respuesta empieza con «Buscando
solo en …», y el código aplica el grupo a toda búsqueda que no diga otro.

Después (Juanjo, el mismo día): en lugar de un botón por grupo y «Todos los
grupos», casillas que se marcan y desmarcan en el mismo mensaje (✅ / ⬜), todas
marcadas al empezar y al menos una siempre; así se puede combinar cuando haya un
tercer grupo (EduMedia-IAG). Lo fijado es un conjunto de grupos y la línea
«Buscando en: …» solo aparece si no están todos y la respuesta ha buscado.

## Quién administra cada grupo

El bot pide a Telegram los administradores de cada grupo al arrancar, se queda
con las personas (no con los bots) y lo sabe para responder «¿quién
administra…?» o para remitir a ellas (Juanjo, 27-10-2026). Cuando alguien gana
o pierde el cargo, Telegram se lo avisa (`chat_member`, que solo llega a los
bots administradores y hay que pedir expresamente) y rehace la lista en el
momento; la consulta cada 6 horas queda de reserva por si se perdiera un aviso.
Antes solo había esa consulta, y un administrador retirado siguió saliendo
durante horas. El aviso no añade carga al NAS: llega por la misma espera de
mensajes que ya tenía el bot y solo cuando cambia un cargo.

## Resúmenes de un periodo

Cada búsqueda da los 12 mensajes más parecidos, que no bastan para «resúmeme lo
de hoy» o «lo de septiembre». `leer_periodo` entrega todos los mensajes de
unas fechas, hasta 1.500, en una línea cada uno con 220 caracteres de texto.
Medido el 27-10-2026: una semana normal de los dos grupos son unos 175
mensajes, y un mes, entre 500 y 1.100 (septiembre de 2026, 1.091). En JSON,
septiembre ocupaba 232.000 tokens; en el formato compacto, 120.000. El resumen
de septiembre salió por temas y con enlaces en 15 s y por 0,014 USD. Para más
de 1.500 mensajes, entrega los más recientes y avisa.

No se hizo un contador de palabras: el buscador de Telegram ya lo hace, y
contar por el sentido no sería fiable (Juanjo, 27-10-2026).

## Validación

27-10-2026, en el portátil:
- Índice de VCE: 8.483 mensajes con texto, 17 minutos con EmbeddingGemma
  (66 de CPU). El de ChatGPT-IA-edu, movido a `datos/chatgpt/`, no se
  recalcula («nada nuevo»).
- Las 20 preguntas de prueba de ChatGPT-IA-edu (`pruebas/extremo.py`), ya con
  los dos grupos mezclados: 17 de 20 citan el enlace esperado (16 de 20 con un
  solo grupo, el 24-10-2026), a 0,0033 USD por pregunta de media.
- Preguntas sobre VCE: «¿qué se ha dicho en Vibe Coding Educativo sobre
  publicar apps en GitHub Pages?» se limita a VCE y da cinco mensajes
  pertinentes; «¿quién ha hablado de Google AI Studio para crear
  aplicaciones?» mezcla los dos grupos y dice de cuál es cada mensaje. Se
  colaban los ids internos (`vce:2930`): el sistema pide no mostrarlos.

En el NAS, el mismo día: el índice de la hora encuentra los dos grupos al día;
con el bot como administrador de VCE, `getChatMember` devuelve «creator» para
Juanjo y «member» para tres autores recientes.

## Tercer grupo: EduMedia-IAG

Juanjo, 28-10-2026: «quiero añadir al bot de ia educativa el grupo edumedia
iag, aquí soy administrador pero no soy el propietario». El día anterior se lo
había ofrecido por privado a su propietario.

- **Qué es.** @EduMediaIAG, supergrupo público sin temas, sobre la IA
  generativa para crear audio, vídeo e imagen con fines educativos: 785
  miembros, unos 12.000 mensajes desde julio de 2025 y el historial visible
  para los miembros nuevos (`hidden_prehistory = False`), como los otros dos.
  Por eso el acceso común no expone nada nuevo.
- **Quién lo nombra administrador.** Juanjo administra el grupo, pero sin el
  permiso de nombrar administradores (`add_admins = False`); de las personas
  que lo administran, solo lo tiene su propietario. Juanjo puede invitar usuarios: añadió
  el bot como miembro normal para que su propietario solo tenga que hacerlo administrador
  con el permiso de invitar usuarios. Mientras no lo sea, `getChatMember` no
  reconoce a quien solo es de EduMedia-IAG (ADR 0001), y esas personas no
  pueden usar el bot. Los miembros de los otros grupos sí buscan en él.
- **No se sale de un grupo conocido.** Antes, el bot dejaba cualquier grupo
  que no estuviera en marcha en cuanto le llegaba un mensaje de él. Ahora
  solo deja los que no están en `grupos.TODOS`. En uno conocido que no busca
  (un grupo nuevo mientras se prepara su índice) se queda callado. Si alguien
  añadiera el Bot de IA Educativa al grupo eXeLearning, que es de Karla bot,
  también se quedaría callado allí: es un caso que no ocurre, y no hace daño.
- **Casillas de /buscar, una por fila.** Con tres botones en la misma fila,
  el móvil corta los nombres. El aviso «Buscando en: …» sigue el orden de
  `grupos.TODOS`, no el alfabético de las claves.
- **Resúmenes de un periodo.** Septiembre de 2026, el mes más movido, suma
  1.608 mensajes entre los tres grupos (828, 416 y 364). Sin los muy cortos,
  que `leer_periodo` deja fuera, son unos 1.400 (en los dos primeros grupos se
  quedaba el 88 %). Caben en el tope de 1.500, pero justo: un mes más movido
  entregará los más recientes y lo avisará.

Validación de EduMedia-IAG, 28-10-2026, en el portátil:
- Descarga de los 10.502 mensajes con la cuenta de Juanjo, en 2 minutos;
  índice, en 23 minutos con EmbeddingGemma.
- `pruebas/simular_catalogo.py`: 56 de 56. Incluye a quien solo es de
  EduMedia-IAG: la ayuda le ofrece buscar, y `/biblioteca` y `/repositorio` lo
  remiten a su grupo. También comprueba las casillas en filas y los tres
  enlaces en el mensaje para quien no es de ningún grupo.
- Las 20 preguntas de prueba, el mismo día y con el mismo código: con los tres
  grupos, 16 y 15 aciertos; solo con ChatGPT-IA-edu y VCE (`GRUPOS=chatgpt,vce`),
  16 y 16. Fallan casi siempre las mismas preguntas y ninguna respuesta fallida
  cita EduMedia-IAG: no hay diferencia medible.
- «¿Qué se ha dicho en EduMedia-IAG sobre crear música con IA para clase?» se
  limita al grupo y da cinco mensajes pertinentes (AIVA, Suno, Mubert…); «¿quién
  ha hablado de generar vídeos con IA?» mezcla ChatGPT-IA-edu y EduMedia-IAG.

En el NAS, el mismo día, con el bot como miembro de EduMedia-IAG y aún sin ser
administrador: `getChatMember` reconoce a 2 de los 25 autores que solo han
escrito en EduMedia-IAG y a 16 de los 60 primeros que también escriben en los
otros grupos; para el resto, `PARTICIPANT_ID_INVALID`. A Juanjo, que lo
administra, sí lo reconoce. Confirma que hace falta que su propietario lo nombre
administrador; cuando lo haga, funcionará sin tocar nada, porque el bot
pregunta en cada consulta y guarda la respuesta como mucho una hora.

Su propietario hizo administrador al bot el 28-10-2026. Desde entonces `getChatMember`
reconoce a 20 de los 25 autores que solo escriben en EduMedia-IAG y a 49 de
los 60 primeros que también están en otros grupos; el resto ya no están en el
grupo («member not found»). Le dio casi todos los permisos, no solo el de
invitar usuarios. El bot no usa los demás, pero Juanjo no puede quitárselos,
porque el cargo lo dio el propietario (`can_be_edited = False`).
