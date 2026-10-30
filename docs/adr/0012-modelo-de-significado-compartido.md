# 12. Una sola copia del modelo de significado para los dos bots y el índice

Fecha: 2026-10-29 · Estado: aceptado

## Contexto

El Bot de IA Educativa y Karla bot cargaban cada uno su copia de EmbeddingGemma,
el modelo que convierte los textos en vectores para buscar por significado
(ADR 0001), y el contenedor del índice cargaba una tercera cada vez que había
algo nuevo que calcular. El ADR 0008 daba por hecho que «caben los dos», con
3,5 GB libres el 27-10-2026. Un día después el NAS (7,7 GB) usaba 3,7 GB de
swap, el proceso de Karla ocupaba 748 MB en memoria y 275 MB en swap, y el buffer
pool de MariaDB se había quedado en 128 MB.

La versión comprimida del modelo (q4) ahorraba unos 400 MB por bot, pero
encontraba peor los mensajes: el correcto quedaba entre los 5 primeros en 10
de las 20 preguntas de prueba, frente a 11 con la actual (informe del
28-10-2026, `Informes/bot-chatgpt-ia-edu/2026-10-28-modelo-ligero.md`).

## Decisión

1. **Un servicio con el modelo, en su propio contenedor** (`bot-significado`,
   `scripts/significado.py`). Los dos bots y el índice le piden los vectores
   por HTTP dentro de la red de Docker (`SIGNIFICADO_URL`). No se publica
   ningún puerto fuera.
2. **El resto del código no cambia.** El cliente ofrece lo mismo que se usaba
   de fastembed (`query_embed` y `passage_embed`). Sin `SIGNIFICADO_URL`, como
   en el portátil, cada programa carga el modelo como antes.
3. **Si el servicio no responde, los bots siguen buscando solo por palabras**
   y lo dejan escrito en su registro. El indexador falla esa pasada y lo
   intenta en la siguiente. El contenedor va en la lista del vigía del NAS.
4. **Para que el servicio no se quede con la memoria de cada lote que
   calcula**, cuatro ajustes, cada uno medido (ver Evidencia):
   - la reserva de memoria de onnxruntime, desactivada
     (`enable_cpu_mem_arena=False`, opción documentada de fastembed);
   - los textos para indexar, de cuatro en cuatro en vez de dieciséis;
   - tras cada lote, lo liberado se devuelve al sistema (`malloc_trim`);
   - `MALLOC_ARENA_MAX=2` en el contenedor.
5. **Las consultas de los bots no hacen cola detrás de la indexación**: solo
   los lotes para indexar van de uno en uno. onnxruntime admite cálculos
   simultáneos en la misma sesión.

## Alternativas descartadas

- **Los dos bots en un solo proceso.** Era menos trabajo, pero un fallo o un
  reinicio de uno tumbaría al otro, y el índice seguiría cargando su copia.
- **La versión comprimida (q4)**: busca peor (informe del 28-10-2026).
- **Solo desactivar la reserva de onnxruntime en cada bot**: unos 100 MB por
  bot, frente a casi 900 MB del servicio compartido.

## Consecuencias

- Una pieza más que puede fallar, pero, si falla, los bots siguen buscando
  por palabras en vez de pararse.
- Cada consulta añade el viaje de un contenedor a otro: unos milisegundos.
- Para llevar el bot a otra máquina, `nas/compose.yml` sigue sirviendo tal
  cual; sin Docker, basta con no definir `SIGNIFICADO_URL`.

## Evidencia

Medidas en el portátil (fastembed 0.9.0, EmbeddingGemma 300m fp32, 4 hilos),
con 64 textos largos (unos 2.200 caracteres) mientras un bot consultaba cada
0,3 s:

| Servicio | Espera máxima de una consulta | Pico | Al acabar |
|---|---|---|---|
| Primera versión: un solo turno, lotes de 16, sin ajustes de memoria | 14,3 s | 3.764 MB | 1.272 MB |
| Final (lotes de 4, `malloc_trim`, `MALLOC_ARENA_MAX=2`) | 0,13 s | 918 MB | 683 MB |
| Final con lotes de 16 | 0,16 s | 1.584 MB | 655 MB |
| Final sin `MALLOC_ARENA_MAX` | 0,14 s | 1.214 MB | 689 MB |
| Final sin `malloc_trim` | 0,13 s | 1.135 MB | 1.027 MB |

Con lotes de 4 se tarda lo mismo que con 16 (65 s frente a 72), y los
vectores difieren como mucho en 1,3·10⁻⁷. Solo la reserva de onnxruntime
(sin parchear `enable_mem_pattern`, que fastembed no expone) deja el proceso
en 863 MB tras indexar, igual que desactivando las dos opciones; con ella
activada, en 1.253 MB.

Vectores del servicio frente al modelo cargado en el propio proceso: idénticos
en consultas y pasajes, y las mismas búsquedas en ChatGPT-IA-edu y en la
documentación de eXeLearning. Con el servicio parado, las dos búsquedas
devuelven resultados por palabras, sin error.

## Riesgos y limitaciones

- Las medidas de memoria son del portátil; en el NAS se comprobaron el total
  y el resultado, no cada ajuste por separado.
- Un lote de textos muy largos sigue subiendo el pico del servicio mientras
  se calcula; lo que se ha resuelto es que no se quede con esa memoria.

## Validación

En el NAS, el 29-10-2026, recién desplegado:

- Memoria de los procesos: el Bot de IA Educativa pasa de 1.128 MB (131 en
  memoria y 997 en swap) a 325 MB, Karla de 986 MB a 244 MB, y el servicio
  ocupa 679 MB. En total, de 2.114 a 1.248 MB. La memoria disponible del NAS,
  de 2.500 a 3.185 MB.
- 40 mensajes de ChatGPT-IA-edu, repartidos por todo el historial,
  recalculados por el servicio: similitud mínima de 1,000000 con los vectores
  guardados en el índice. No hace falta reindexar.
- Una consulta al servicio tarda entre 37 y 77 ms; una búsqueda completa,
  0,15 s (la primera, 1,3 s, mientras carga el índice).
