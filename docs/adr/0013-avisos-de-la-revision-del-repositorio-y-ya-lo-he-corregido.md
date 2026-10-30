# 13. Avisos de la revisión del repositorio y «Ya lo he corregido»

Fecha: 2026-10-29 · Estado: aceptado

## Contexto

El 29-10-2026 se revisaron las 353 fichas del Repositorio de recursos educativos
digitales de VCE (informe de Juanjo, fuera del repositorio). 79 no
cumplen sus condiciones (gratuito y con licencia abierta que conste en el recurso), de
26 personas, todas del antiguo formulario. Juanjo decidió avisarlas con un mes de plazo
y pidió un botón «Ya lo he corregido» que vuelva a comprobar el recurso (29-10-2026).
También señaló que el aviso tiene que explicar cómo se hace todo con el bot, porque desde
que se cerró el formulario es la única vía para cambiar o quitar un recurso.

## Decisión

- `datos/avisos.json` guarda, por enlace, el tipo de aviso, el motivo, la fecha y el
  plazo, y su estado: «pendiente», «corregido» (lo comprobó el bot) o «por_revisar» (lo
  mira Juanjo). Tipos: A, sin licencia; B, el enlace no se abre; C, un GPT de ChatGPT,
  que sale el 11-12-2026, cuando OpenAI los retira; D, derechos reservados. Lo prepara
  `scripts/avisos.py` a partir de la clasificación de la revisión; nadie recibe nada
  hasta que se manden los avisos.
- En `/misrecursos`, los recursos con un aviso pendiente llevan ⚠️ delante, y su ficha
  dice qué falta y hasta cuándo. Salvo los GPT, que no tienen arreglo, llevan el botón
  «Ya lo he corregido».
- «Ya lo he corregido» vuelve a abrir el recurso como un visitante. Si no se abre, lo
  dice. Si se abre, Claude Haiku 5.5 lee lo que se ha podido leer y dice si tiene una
  licencia abierta y si es gratuito, con los criterios del alta (ADR 0004). Si cumple, el
  aviso queda «corregido» y la licencia pasa a la columna «Licencia de uso» de la hoja,
  que la API cambia sin tocar lo demás. Si no, explica qué falta.
- Lo que el bot no puede comprobar solo pasa a revisión manual de Juanjo: las apps de
  Gemini, Claude y AI Studio, cuyo código ve quien las abre pero no un programa sin
  navegador, y los recursos de los que la persona dice que ya tienen licencia aunque el
  bot no la vea (botón «Sí la tiene: revisión manual»). El mensaje que recibe Juanjo dice de
  qué era el aviso, por qué no lo ha resuelto el bot y qué mirar, con dos botones (30-10-2026,
  tras un primer mensaje que no decía qué revisar): «Cumple» le pide la licencia, la pone en la
  hoja, da el aviso por corregido y se lo dice al autor; «No cumple» lo deja pendiente y le dice
  al autor que aún falta. El botón lleva un resumen del enlace (SHA-1, 12 caracteres), que cabe
  en los 64 bytes de Telegram y sobrevive a un reinicio del bot.
- Los textos que ve el autor no nombran a Juanjo: hablan de «revisión manual» (Juanjo,
  30-10-2026: nombrarle «me parece poco profesional»).
- Cada comprobación cuenta en el cupo diario de recursos y en el gasto común.
- `/misrecursos` sigue siendo solo para miembros del grupo de Vibe Coding Educativo, como
  el resto del repositorio: quien quiera rectificar tiene que estar en el grupo (Juanjo,
  29-10-2026). A quien no está, el bot le da el enlace para entrar.

## Alternativas descartadas

- Dejar entrar en `/misrecursos` a cualquiera que demuestre con el código que el correo
  de la ficha es suyo, aunque no esté en el grupo: lo propuso Claude y Juanjo lo rechazó.

- Comprobar con Claude Sonnet, como el alta: leer una licencia no necesita la ficha
  entera, y Haiku cuesta unas diez veces menos.
- Abrir las páginas con un navegador sin ventana en el NAS, para leer lo que pinta el
  JavaScript: añade cientos de MB a un NAS que ya va justo de memoria (ADR 0012). Lo
  poco que se escape lo resuelve Juanjo con el botón «Sí la tiene».

## Consecuencias

- Juanjo recibe un mensaje por cada app de plataforma, o licencia que el bot no ve, que alguien dé por corregida, y lo resuelve con un botón.
- Los avisos salieron el 29-10-2026: 79 recursos de 26 personas. A las 5 que ya habían ligado su
  correo con `/misrecursos`, un mensaje del bot; a las otras 21, un correo desde la cuenta de Juanjo
  con los pasos para hacerlo con el bot. `avisos.json` guarda por dónde salió cada uno (`via`).
- La retirada al acabar el plazo y el recordatorio a falta de una semana quedan para
  la fase siguiente.
- Rectificado el mismo 29-10-2026: lo publicado antes del bot no se retira por no tener
  licencia (Juanjo: «lo que estaba de antes en el tema de licencias lo íbamos a dejar, excepto las
  licencias incompatibles como copyright»). Los 53 avisos de tipo A quedan como recomendación:
  en `/misrecursos` llevan ℹ️ en lugar de ⚠️, su ficha dice que seguirán en el repositorio y
  no tienen plazo; «Ya lo he corregido» sigue sirviendo para que la licencia pase a la hoja.
  La retirada solo alcanza a los tipos B, C y D. A las 20 personas con avisos de tipo A se les
  manda una rectificación por la misma vía.

## Evidencia

- Prueba del 29-10-2026 con `catalogo.Fichas.comprobar`: `jjdeharo.github.io/ajedrez`,
  licencia encontrada (AGPL v3 y CC BY-SA 4.0, 0,002 USD); `pablogguizar.github.io/quiz`,
  ninguna (0,0003 USD); `pablogguizar.github.io/escritorio-interactivo-page`, no se abre
  (404); la página de Serendiphia con «Todos los derechos reservados», sin licencia
  abierta; un enlace `g.co/gemini/share/…`, pasado a Juanjo.

## Riesgos y limitaciones

- Una licencia que solo aparece al ejecutarse el JavaScript de la página no se ve
  (mismo límite que el alta); para eso está el botón que lo pasa a revisión manual.
- GitHub Pages tarda unos minutos en publicar: el texto lo advierte.

## Validación

- Recorrido en Telegram con un aviso de prueba sobre un recurso de Juanjo.
- Revisión manual (30-10-2026): recorrido simulado sin Telegram ni la hoja reales: «No cumple» deja el aviso pendiente y avisa al autor; un segundo toque dice que ya no está por revisar; «Cumple» pide la licencia, la pone en la hoja y avisa al autor en su idioma.
