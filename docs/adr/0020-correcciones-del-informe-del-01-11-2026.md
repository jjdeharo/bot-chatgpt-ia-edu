# 20. Correcciones del informe del 01-11-2026: respuesta vacía, botones firmados, 429, repuesto HTML, versión y pruebas en GitHub

Fecha: 2026-11-01 · Estado: aceptado

## Contexto

El 01-11-2026, un examen completo del código, de los registros del NAS y de ocho preguntas reales
(informe privado `Informes/bot-chatgpt-ia-edu/2026-11-01-errores-carencias-y-mejoras.md`) encontró,
además de lo ya resuelto en el ADR 0019:

1. Si Claude no deja texto (solo la marca final, o una revisión de la ayuda para enseñar que quita
   todos los párrafos), Telegram rechaza el mensaje vacío en sus tres formas y la persona no recibe
   nada, pero el bot lo registra como «pregunta respondida». Pasó el 31-10 a las 08:02.
2. «Quitarlo de la Biblioteca» (`bq:`) y «Quitarlo del grupo» (`rcq:`) borraban los mensajes cuyos
   números iban en el botón sin comprobar quién pulsaba; los demás botones sí comprueban el dueño o
   la clave del borrador. Un cliente modificado puede mandar cualquier dato en un `callback_query`.
3. Sin flujo de GitHub Actions: el 30-10 una f-string mal escrita en `karla.py` tumbó a Karla cinco
   veces seguidas en medio minuto. La guía de Juanjo pide pruebas que se pasen solas en cada cambio.
4. La copia diaria a IONOS no llevaba `estado-karla.json` ni las preguntas sin resolver.
5. En los arranques, Telegram contesta 429 a parte de las quince llamadas de perfil y menú (cinco
   idiomas por tres) y `Telegram.__call__` no reintentaba: textos sin poner en algún idioma, y un
   `sendMessage` en una ráfaga se perdía en silencio.
6. Cuando Telegram rechaza el mensaje enriquecido en Markdown, el repuesto HTML dejaba en crudo
   los encabezados `###`, las tablas y las citas `>` que las instrucciones piden a Claude.
7. La pregunta se recortaba a 1.000 (IA Educativa) o 1.500 (Karla) caracteres sin avisar: un reenvío
   de varios mensajes, que es para lo que existe la unión de mensajes seguidos, se quedaba a medias.
8. Un enlace `t.me` suelto iba al alta del repositorio y acababa en un rechazo por no ser educativo.
9. Cualquier respuesta a un mensaje del bot en el grupo recibía «escríbeme por privado», también un
   «gracias» al resumen de los viernes.
10. Ningún bot enlazaba su código, que la sección 13 de la AGPL exige ofrecer a quien usa el programa
    por red; sin etiqueta de versión ni registro de cambios.
11. Textos desfasados: «de forma anónima» (el texto de la pregunta se guarda tal cual), «solo
    entiendo mensajes escritos» (también capturas), la ayuda de Karla sin las capturas ni los avisos
    de error, el prompt de Karla sugiriendo ir a GitHub en vez de preparar ella el aviso, la lista de
    comandos del Bot de IA Educativa usada también por Karla, los nombres largos de las licencias
    Creative Commons sin reconocer en `LICENCIA_ABIERTA`, el «¡Gracias!» de un 👍 ante un 👎 de antes
    de reiniciar, y la cuenta de Telegram de Juanjo escrita en el código público.

## Decisión

- **Respuesta vacía → texto fijo** (`Bot.texto_o_nada`): si el texto queda vacío tras quitar las
  marcas, va `respuesta_vacia` en el idioma de la persona y la pregunta se guarda como sin resolver
  con motivo «respuesta vacía». `enviar_valorable` devuelve si Telegram ha aceptado alguna forma, y
  el registro dice «respondida» o «sin entregar».
- **Firma en los botones que borran** (`Bot.firma`, `Bot.firmado`): HMAC-SHA256 con el token del bot
  sobre la cuenta y los mensajes, 10 caracteres hexadecimales, en el propio dato del botón
  (`bq:<chat>:<ids>:<firma>`, `rcq:<id>:<firma>`), de modo que sobrevive a un reinicio sin guardar
  nada. Sin firma o con otra cuenta, «no_tuyo».
- **Un reintento ante 429**: `Telegram.__call__` espera `parameters.retry_after` (60 s como mucho) y
  repite una vez.
- **Repuesto HTML completo**: `respuesta_html` convierte `### Título` en negrita, `> cita` en
  `<blockquote>` y una tabla Markdown en líneas «• **primera celda** — cabecera: celda; …».
- **Preguntas hasta 6.000 caracteres** (`LARGO_PREGUNTA`), con la nota «[El mensaje era más largo:
  solo he recibido el principio.]» si se recorta, para que Claude lo diga. El historial sigue
  guardando 1.000.
- **Un enlace `t.me` suelto es una pregunta** (`ENLACE_TELEGRAM`), no un recurso. El resto de enlaces
  sueltos siguen yendo al repositorio: sin botón de elegir, porque el valor por defecto resuelve
  casi todos los casos.
- **Responder al bot en el grupo solo cuenta si lleva una pregunta** (`?` o `¿`). La mención y el
  comando siguen contando siempre.
- **Pie con licencia, versión y código** en la ayuda de los dos bots (`Bot.pie`, texto `codigo` en
  cinco idiomas), y `Versión x.y.z` al final de `/estado`. `bot.VERSION` y la etiqueta de git llevan
  el mismo número; `CHANGELOG.md` resume cada versión.
- **Pruebas en GitHub Actions** (`.github/workflows/pruebas.yml`): en cada push, `compileall`,
  `ruff check --select E9,F` y `pruebas/test_revision.py`. No se despliega con el flujo en rojo.
- **Copia diaria completa**: `estado-karla.json` y los dos `sin-resolver*.jsonl` van en la copia y en
  `respaldo/recuperar.sh`.
- **La cuenta de Juanjo, en el entorno** (`JUANJO` en `nas/compose.yml`); `AUTORIZADOS` parte de ella.
- **Textos**: «sin tu nombre ni tu cuenta» en lugar de «de forma anónima»; «mensajes escritos y
  capturas de pantalla»; la ayuda de Karla cuenta las capturas y los avisos de error; el prompt de
  Karla ofrece preparar el aviso; cada bot tiene su lista de comandos (`Bot.COMANDOS`);
  `LICENCIA_ABIERTA` reconoce «reconocimiento», «reconeixement», «recoñecemento», «aitortu»,
  «attribution» y «atribución»; un 👍/👎 de antes de reiniciar recibe «Gracias.» a secas.

## Alternativas descartadas

- Guardar `{mensaje: cuenta}` en memoria para los botones que borran: se pierde al reiniciar y los
  botones duran 48 horas; la firma no necesita estado.
- Un mensaje con dos botones («Añadirlo al repositorio», «Preguntar sobre él») para todo enlace
  suelto: un control de más para un caso raro; basta con excluir los enlaces de Telegram.
- Leer la versión con `git describe` al arrancar: la imagen del NAS no lleva git; una constante
  sincronizada con la etiqueta es suficiente y se comprueba a ojo en el CHANGELOG.
- Cambiar la clasificación de la ayuda para enseñar (una búsqueda de recursos por tema entra hoy
  por el camino caro de Sonnet con revisión): es una decisión de Juanjo sobre el ADR 0011; queda
  propuesta en el informe.

## Consecuencias

- La ayuda de los dos bots gana una línea en cursiva con la licencia, la versión y el enlace al
  código, y el aviso de traducción automática va en esa misma línea.
- Una pregunta larga cuesta algo más (hasta unos 1.500 tokens de entrada más): décimas de céntimo.
- Los botones «Quitarlo…» de antes de este cambio no llevan firma: al pulsarlos, «no_tuyo». Duran
  48 horas como mucho.
- Lo que dicen los bots sobre lo que guardan es ahora exacto: el texto de la pregunta se conserva,
  sin el nombre ni la cuenta.

## Evidencia

- Informe del 01-11-2026 (privado), con el registro del 31-10 a las 08:02 (`RICH_MESSAGE_MARKDOWN_INVALID`,
  dos `message text is empty` y «pregunta respondida»), el del 30-10 a las 09:17 (`SyntaxError`
  cinco veces) y el del 31-10 a las 17:22 (ocho 429 con `retry_after` en los dos bots).
- AGPL-3.0, sección 13 («Remote Network Interaction»): https://www.gnu.org/licenses/agpl-3.0.html
- Telegram Bot API: `ResponseParameters.retry_after` y `forward_origin`: https://core.telegram.org/bots/api

## Riesgos y limitaciones

- La firma protege de un dato forjado, no de que quien publicó pulse por error: para eso ya está el
  texto del botón y el límite de 48 horas.
- El repuesto HTML de las tablas pierde la cuadrícula: es el repuesto, no el camino normal.
- `ruff --select E9,F` solo detecta errores de sintaxis y de nombres; el estilo no se comprueba.

## Validación

- `pruebas/test_revision.py`, 40 pruebas (30 anteriores y 10 nuevas), todas en verde el 01-11-2026;
  `ruff check --select E9,F scripts pruebas` sin avisos.
- Despliegue en el NAS comprobado por la hora de arranque de los procesos y por la ayuda de los dos
  bots en Telegram, con el pie nuevo.
