# 5. El bot habla en el idioma de quien le escribe

Fecha: 2026-10-27 · Estado: aceptado

## Contexto

Las respuestas de la búsqueda ya salían en el idioma de la pregunta, porque
las redacta Claude, pero los textos fijos (ayuda, avisos, botones y menú)
estaban solo en castellano. Juanjo preguntó si el bot podía hablar en el
idioma que cada persona tiene por defecto «o en el que se dirige al bot».

El idioma de Telegram (`language_code`) es el de la interfaz de la app, no
necesariamente el de la persona. Además, al pulsar `/start` o un botón del
menú todavía no ha escrito nada.

## Decisión

1. **Cinco idiomas**: castellano, catalán, gallego, euskera e inglés
   (`scripts/textos.py`). Cualquier otro, castellano.
2. **Al principio, el idioma de su Telegram si es catalán, gallego o
   euskera; si no, castellano**; **en cuanto escribe una frase** (dos palabras
   al menos, sin contar comandos, enlaces ni códigos), el de la frase. Un «ok»
   o un código no lo cambian. El inglés no se toma de Telegram desde el
   27-10-2026: la app de Juanjo, configurada en castellano, mandaba «en», y
   Karla bot le respondió en inglés a `/start`.
3. **Lo detecta Claude Haiku 5.5**, con la respuesta «dudoso» cuando la frase
   podría ser de dos idiomas; entonces se mantiene el que había. La detección
   va en un hilo aparte y no retrasa la respuesta.
4. **Solo en memoria.** El bot no guarda en disco el idioma de nadie; si se
   reinicia, vuelve al de Telegram hasta la siguiente frase.
5. **El menú, en los cinco idiomas** (`setMyCommands` con `language_code`);
   Telegram muestra el de la app de cada persona.
6. **Las fichas no se traducen**: las del catálogo y las de la biblioteca son
   contenido común y van en castellano. Fuera del castellano, el bot avisa de
   que la ficha está en castellano.
7. **Traducción automática con IA, sin revisión profesional**: lo dice la
   ayuda en los otros cuatro idiomas.

## Alternativas descartadas

Medido el 27-10-2026 con 30 frases cortas, seis por idioma, escritas como las
que recibe el bot («quita Bachillerato», «hai algo sobre rúbricas?»):

| Detector | Aciertos | Gallego | Errores que cambiarían mal el idioma | Coste |
|---|---|---|---|---|
| lingua 2.1.1 | — | no tiene gallego | — | gratis |
| langid 1.1.6 (limitado a los 5) | 21 | 0 de 6 | 9 | gratis |
| fastText `lid.176.ftz` | 21 | 2 de 6 | 9 | gratis |
| **Claude Haiku 5.5** | **26** | **4 de 6** | **1** | 0,00004 USD por mensaje |

De los cuatro fallos de Haiku, tres son «dudoso» (no cambian nada) y el otro
es «busco guías sobre IA en infantil», que se escribe igual en castellano y en
gallego. Con los detectores gratuitos, quien escribe en gallego pasaría casi
siempre al castellano. El coste de Haiku son unos 4 céntimos por cada 1.000
mensajes, dentro del tope del bot.

También se descartó un comando `/idioma`: con la detección no hace falta, y el
menú tiene una opción menos. Si la detección fallara en la práctica, se añade.

## Evidencia

La primera prueba real del catálogo (27-10-2026), hecha con Telethon desde la
cuenta de Juanjo, sacó una ficha en inglés: la ficha seguía el
`language_code` que manda Telegram. Una hora después, con Telethon
configurado en inglés a propósito, el bot recibió castellano. El Telegram de
Juanjo está en castellano. De qué depende el `language_code` no está
comprobado: es un dato poco fiable, y por eso solo vale hasta la primera
frase, y la ficha no depende de él (punto 6).

## Validación

Con el bot real, el 27-10-2026: una pregunta en catalán recibe la respuesta en
catalán y la ayuda siguiente sale en catalán; una pregunta en castellano
devuelve al castellano. El menú está publicado en los cinco idiomas
(`getMyCommands` con `language_code`).

`pruebas/simular_catalogo.py`, el mismo día: Telegram en inglés sin frase,
ayuda en inglés con el aviso de traducción; tras una frase en catalán, en
catalán; un «ok» no lo cambia; Telegram en gallego y frase en castellano, en
castellano; la ficha, en castellano aunque Telegram esté en inglés.
