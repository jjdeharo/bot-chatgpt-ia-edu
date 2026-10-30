# 17. Caché de prompts en las preguntas de los dos bots

Fecha: 2026-10-30 · Estado: aceptado

## Contexto

Cada pregunta a los bots es una serie de rondas: Claude pide una búsqueda, recibe los
resultados y vuelve a llamar. En cada ronda se reenvía todo lo anterior (instrucciones,
herramientas, pregunta y resultados), y hasta ahora se pagaba entero cada vez. Karla gastaba
unos 0,06 USD por pregunta con Sonnet 5.5; a ese ritmo rozaba el tope mensual de su espacio de
trabajo.

## Decisión

Las llamadas de las rondas de una pregunta (`Consultor.responder` y `Consultora.responder`)
usan la caché de prompts de la API con dos marcas, de 5 minutos:

- **Caché automática** (`cache_control` en la petición): la marca avanza sola hasta el último
  bloque, así que cada ronda lee de la caché lo que envió la anterior.
- **Una marca al final del sistema** (`consultar.en_cache`): una pregunta que llega a menos de
  5 minutos de otra, con el mismo sistema, lee de la caché las instrucciones y las herramientas
  (unos 7.200 tokens en Karla).

El gasto que apunta el bot (`Consultor.apuntar`) cobra aparte lo escrito en la caché (1,25 veces
la entrada) y lo leído (0,1 veces en Haiku 5.5 y 0,05 en Sonnet 5.5), para que el tope
mensual cuente lo que de verdad se paga.

Las llamadas de una sola vuelta (decidir si es ayuda para enseñar, revisar las citas, las
fichas) se quedan sin caché: no repiten nada que leer.

## Alternativas descartadas

- **Caché de 1 hora.** Escribir cuesta el doble de la entrada en vez de 1,25 veces, y el sistema
  cambia cuando llegan mensajes nuevos (lleva la hora del último), así que pocas preguntas
  aprovecharían esa hora de más.
- **Solo la caché automática.** Ahorra en las rondas, pero cada pregunta vuelve a escribir las
  instrucciones aunque la anterior sea de hace un minuto.

## Consecuencias

Las respuestas no cambian: la caché solo cambia lo que se cobra. Si el sistema cambia entre dos
preguntas (mensajes nuevos, otro día, otro ámbito), la segunda vuelve a escribirlo, al mismo
precio que antes con la caché automática.

## Evidencia

- [Documentación de la caché de prompts](https://platform.claude.com/docs/es/build-with-claude/prompt-caching),
  consultada el 30-10-2026: precios, mínimo de 512 tokens en Haiku 5.5 y Sonnet 5.5, caché
  automática y hasta 4 marcas por petición.
- SDK `anthropic` 2.3.0 en la imagen del NAS: `messages.create` acepta `cache_control`.
- Ritmo real, del registro de los contenedores (29 y 30-10-2026): 8 de cada 22 preguntas a Karla y 4
  de cada 11 al Bot de IA Educativa llegan a menos de 5 minutos de la anterior.

## Riesgos y limitaciones

- El precio de Haiku 5.5 sube por encima de 100.000 tokens de entrada; ni el cálculo anterior ni
  este lo tienen en cuenta, porque las preguntas no llegan a ese tamaño.
- El ahorro real depende de cuántas preguntas lleguen seguidas: es una estimación hasta que se
  compare el gasto medio por pregunta de unas semanas con el anterior (0,06 USD en Karla y 0,009 USD
  en el otro bot).

## Validación

Diez preguntas a cada bot en sus contenedores del NAS, el 30-10-2026, con una copia del código
aparte de la que está en marcha. Lo que habría costado sin caché se calcula con los mismos tokens.

| Bot | Sin caché | Con caché, preguntas separadas | Con caché, preguntas seguidas |
|---|---|---|---|
| Karla (Sonnet 5.5) | 0,637 USD | 0,473 USD (−26 %) | 0,300 USD (−53 %) |
| IA Educativa (Haiku 5.5) | 0,050 USD | 0,033 USD (−33 %) | 0,025 USD (−50 %) |

«Separadas» es el caso en que cada pregunta escribe de nuevo las instrucciones; «seguidas», el
de la prueba, con todas a menos de 5 minutos. Con el ritmo real, el ahorro esperado es de un
35 % en Karla y de un 40 % en el otro bot. La marca del sistema no encarece las preguntas
separadas: en una primera tanda solo con la caché automática, Karla ahorró un 24 %. El gasto que
apuntó el bot coincidió con el calculado.
