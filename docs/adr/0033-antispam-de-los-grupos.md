# 33. Antispam de los grupos, sin IA

Fecha: 2026-11-07 · Estado: aceptado

## Contexto

El 31-10-2026 se activó el antispam propio de Telegram en los cuatro grupos, contra los anuncios en
chino de cuentas recién llegadas que superan la verificación de AntiUserbotsBot. Una semana después,
el registro de administradores (que copia cada día memoria-telegram, `datos/registro-admin/`) no
recoge ni un borrado suyo, y el antispam seguía activado en los cuatro grupos (comprobado con
`channels.getFullChannel`, campo `antispam`). En esos días los administradores quitaron a mano unas
diez tandas de spam: anuncios en chino de reventa de cuentas de IA en Vibe Coding Educativo (las
mismas cuentas tres días seguidos), venta de suscripciones de ChatGPT y Gemini y una ráfaga de
flechas en ChatGPT-IA-edu y EduMedia-IAG, y anuncios en chino en eXeLearning. Las cuentas en chino
escribían primero «大家好» («hola a todos») y horas después el anuncio.

## Decisión

Juanjo aprobó el 07-11-2026 que los bots borren y expulsen solos, con una regla sin IA
(`scripts/antispam.py`). Lo hace el bot que administra cada grupo: el Bot de IA Educativa en
ChatGPT-IA-edu, Vibe Coding Educativo y EduMedia-IAG, y Karla bot en eXeLearning. Ese día se les dio
permiso de borrar mensajes y expulsar en los tres grupos donde no lo tenían (en EduMedia-IAG ya lo
tenía), sin cambiar el resto de sus permisos.

- **Mensajes.** Se quitan los de alguien nuevo (nunca había escrito en el grupo, según
  `datos/<grupo>/mensajes.jsonl`, y el bot le ha visto como mucho 3 mensajes) si el texto o su
  nombre van en chino, japonés, coreano o cirílico, o si menciona dos bots o más. También una ráfaga
  de más de 5 mensajes en un minuto de alguien que nunca había escrito.
- **Entradas.** Quien entra con el nombre en esas escrituras sale en el momento, aunque no haya
  escrito, salvo que ya hubiera escrito antes en el grupo. Es lo que hacía Juanjo a mano: «los que
  tienen nombres en chino o cirílico los borro directamente y los marco como spam, aunque no hayan
  escrito nada». Marcarlos como spam no lo puede hacer un bot.
- **Nunca** a un administrador, a un bot ni a un mensaje enviado en nombre de un canal.
- **Expulsión** con `banChatMember` y `revoke_messages`, que borra también lo demás que hubiera
  escrito en el grupo.
- **Aviso** a Juanjo por privado, del bot que actúa: grupo, persona, motivo y el mensaje, con un
  botón «Deshacer» que solo él puede usar (firmado con el token, como los demás botones que borran,
  ADR 0020) y que la vuelve a admitir. Los mensajes borrados no vuelven.

## Alternativas descartadas

- **Esperar al antispam de Telegram**: una semana sin actuar en ningún caso.
- **Una mención a un bot como señal**: en la historia de los grupos, cinco primeros mensajes
  legítimos lo hacían («/donate@AntiUserbotsBot», «@askplexbot»). El spam con un solo bot llevaba
  además texto en chino.
- **Avisar en AdminsChatGPT**: es un grupo de 2023 con tres personas, sin mensajes desde diciembre
  de 2023.
- **Clasificar con IA**: coste por mensaje y nada que una regla fija no resuelva en estos casos.

## Consecuencias

- Uno o dos avisos al día a Juanjo, según lo visto en la semana del 31-10.
- El bot ve todos los mensajes de los grupos porque es administrador; no guarda nada en disco: los
  mensajes vistos y los expulsados, solo en memoria.

## Evidencia

- Registro de administradores del 29-10 al 06-11-2026 (585 acciones): ninguna de la cuenta de
  antispam de Telegram; las tandas de spam citadas, borradas por Juanjo, Raül Torres, Manel Soengas y
  Cristina.
- La regla, pasada por los cuatro primeros mensajes de cada autor de toda la historia de los grupos
  (unos 2.900 autores): el texto no da ningún falso positivo; el nombre, cinco casos de cuatro
  personas legítimas (dos nombres en chino o japonés, uno en caracteres japoneses decorativos y
  «Антон», que preguntaba en castellano por eXeLearning en 2024). Si entraran hoy, saldrían, como
  con el criterio de Juanjo; el botón «Deshacer» lo corrige.
- Del spam de la semana que tenía texto, la regla quita todo el que va en chino o con varios bots;
  no quita la venta de suscripciones de «Red de Ingenieros» (nombre con letras decorativas
  latinas, texto en castellano) ni, por el texto, las flechas, que caen por la ráfaga.
- `pruebas/test_antispam.py`, con esos casos.

## Riesgos y limitaciones

- Quien escribe en un idioma con esas escrituras sin haber escrito antes sale del grupo. No ha
  pasado en la historia de los grupos.
- Si falta `mensajes.jsonl`, el bot no actúa: sin saber quién ha escrito, no puede saber quién es
  nuevo.
- Lo que no sea chino, japonés, coreano, cirílico, varios bots o una ráfaga sigue llegando.

## Validación

Las pruebas automáticas y, en producción, los avisos a Juanjo y el registro de administradores de
las semanas siguientes.
