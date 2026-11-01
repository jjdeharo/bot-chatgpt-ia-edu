# Bot de IA Educativa y Karla bot

[Bot de IA Educativa](https://t.me/IAEducativa_bot) (@IAEducativa_bot): bot de Telegram que busca en los grupos
[ChatGPT-IA-edu](https://t.me/ChatGPTedu), [Vibe Coding Educativo](https://t.me/vceduca)
y [EduMedia-IAG](https://t.me/EduMediaIAG) con preguntas en lenguaje natural: quién dijo algo, cuándo y en qué mensaje
(con su enlace), qué documentos de la Biblioteca digital de ChatGPT-IA-edu
tratan un tema y qué recursos hay en el repositorio de Vibe Coding Educativo
(`scripts/repositorio.py`, ADR 0016). Basta con ser miembro de uno de los grupos para buscar en
todos.
También añade documentos a la biblioteca: el miembro le manda el PDF y el bot
comprueba que encaje, hace su ficha y lo publica (`scripts/fichas.py`). Y
añade recursos educativos al [catálogo de Vibe Coding Educativo](https://vibe-coding-educativo.github.io/app_edu/):
el miembro le manda el enlace, el bot lee el recurso, comprueba que sea
educativo, que ya se pueda usar en clase, gratuito y con licencia abierta, hace
su ficha y la escribe en la hoja del catálogo; con `/misrecursos` los cambia o
los quita (`scripts/catalogo.py`). Si lo rechaza por su contenido, quien lo
aporta puede pedir una revisión manual (ADR 0004). Cada aportación es solo para los miembros de su grupo.
Si le piden ayuda para enseñar (ideas, consejo, una clase, una rúbrica), la
prepara con lo que se ha compartido en los grupos: cada idea con quién la
compartió, cuándo y el enlace, y aparte lo que añade el bot (ADR 0011).

Entiende capturas de pantalla y notas de voz (ADR 0022). Habla en castellano, catalán, gallego, euskera o inglés: al principio, en el
idioma del Telegram de cada persona y, en cuanto escribe una frase, en el de
la frase (`scripts/textos.py`, ADR 0005). Las traducciones son automáticas,
hechas con IA, sin revisión profesional.

## Karla bot

[Karla bot](https://t.me/eXeKarlaBot) (@eXeKarlaBot) resuelve dudas sobre
eXeLearning a los miembros del [grupo eXeLearning](https://t.me/exelearning),
por privado y en los mismos cinco idiomas. Responde con lo que se ha dicho en
el grupo y con la documentación del programa (manual, documentación técnica y
complementos), siempre con sus fuentes, y en un lenguaje pensado para el
profesorado. Si la duda es un fallo o una mejora de eXeLearning, busca si ya
hay una incidencia en GitHub y, si la persona lo confirma, la abre; si lo pide, le avisa de cada
respuesta del equipo y del cierre (ADR 0021). Entiende capturas de pantalla y archivos `.elpx` del
proyecto, que resume antes de responder. Sustituye
al cuaderno de NotebookLM «Karla - Experta en eXeLearning». Usa el mismo
programa que el Bot de IA Educativa (`scripts/karla.py`, con sus textos en
`scripts/textos_karla.py` y sus instrucciones en `scripts/karla_persona.md`).
Las razones, en los ADR 0008 a 0010 y 0021.

El porqué de cada decisión está en [docs/adr](docs/adr/).

## Cómo funciona

0. `scripts/grupos.py` dice qué grupos hay y lo propio de cada uno; cada
   grupo guarda sus datos en `datos/<grupo>/` (`chatgpt`, `vce`, `edumedia`, `exelearning`).
1. `scripts/exportar.py` descarga los mensajes de cada grupo con la cuenta de
   Juanjo (`--todo` rehace el historial y retira lo borrado).
2. `scripts/pdfs.py` saca el texto de las primeras páginas de los PDF de la
   biblioteca.
3. `scripts/indexar.py` calcula el significado de lo nuevo y rehace el índice
   de palabras en `datos/<grupo>/indice/`.
4. `scripts/bot.py` atiende en Telegram; cada pregunta la resuelve
   `scripts/consultar.py`: Claude Haiku 5.5 busca con las herramientas de
   `scripts/buscador.py` y responde con los enlaces.
5. `scripts/karla.py` atiende a Karla bot; `scripts/documentacion.py` trocea por
   apartados la documentación de eXeLearning para que pueda buscar en ella.

Cada vez que alguien publica algo con un bot, ese bot se lo cuenta a Juanjo
por privado con el enlace, para que pueda verlo: un documento nuevo en la
Biblioteca digital, un recurso nuevo en el repositorio de Vibe Coding
Educativo (no los cambios) o una incidencia abierta en GitHub desde Karla.
Lo que publica él mismo no se avisa.

Los viernes a las 18:00, cada bot publica en su grupo un resumen de la semana
(`scripts/resumen_semanal.py`, ADR 0018): Karla, las novedades y dudas resueltas
en eXeLearning; el Bot de IA Educativa, las aplicaciones nuevas del repositorio
en Vibe Coding Educativo.

## Probar

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cd scripts
../.venv/bin/python exportar.py --todo && ../.venv/bin/python pdfs.py && ../.venv/bin/python indexar.py
../.venv/bin/python consultar.py "¿quién habló de evaluar con IA?"
../.venv/bin/python ../pruebas/extremo.py      # las 20 preguntas de prueba (unos 0,04 USD)
cd .. && .venv/bin/python -m unittest pruebas/test_revision.py   # los controles de seguridad (ADR 0019), sin red ni API
```

## En el NAS

`nas/compose.yml`, con el repositorio en `/volume1/docker/bot-chatgpt-ia-edu/repo`
y las credenciales en `/volume1/docker/bot-chatgpt-ia-edu/credenciales`
(`telegram-cuenta.json` y `.session`, `bot-chatgpt-ia-edu.json` con el token
del bot, `anthropic-bot.txt` con la clave de API del espacio de trabajo
«Bot ChatGPT-IA-edu» y `catalogo-vce.json` con la dirección y la clave de la
API del catálogo).

En el NAS, `repo/` es un clon de git. Se despliega desde el portátil con
`desplegar-nas`, después del push: lleva allí el commit, copia
`nas/compose.yml` y reinicia o reconstruye lo que pide `nas/despliegue.conf`.
`desplegar-nas --comprobar` dice qué commit corre en el NAS y si allí se ha
tocado algo.

Las notas de voz las pasa a texto el contenedor `bot-voz` (`scripts/voz.py`, ADR 0022), que corre con
la imagen, el entorno de Python y el modelo faster-whisper «small» del boletín semanal, montados en solo
lectura desde `../boletin-semanal`. Si se para, los bots piden la pregunta por escrito.

Los dos bots y el índice comparten una sola copia del modelo de significado,
en el contenedor `bot-significado` (ADR 0012). Si se para, los bots siguen
contestando, pero buscan solo por palabras.

## Si el NAS falla

El bot se puede llevar a cualquier ordenador con Linux y Python 3.11, o con
Docker, en menos de una hora. Lo que no depende del NAS sigue funcionando
mientras tanto: la web del repositorio (GitHub Pages), la hoja de sus fichas
(Google Drive) y la Biblioteca digital (Telegram). Lo que se para es el bot.

Qué hay que rehacer y de dónde sale:

| Pieza | De dónde se recupera |
|---|---|
| Código | este repositorio |
| Mensajes e índice (`datos/<grupo>/`) | Telegram: `exportar.py --todo`, `pdfs.py` e `indexar.py` (en el portátil, unos 20 minutos VCE, 25 EduMedia-IAG y 45 ChatGPT-IA-edu) |
| Modelo de significado | se descarga solo la primera vez (1,2 GB) |
| Dueños de los recursos, gasto de los dos bots y preguntas sin resolver (`catalogo.json`, `estado-bot.json`, `estado-karla.json`, `sin-resolver*.jsonl`, avisos, equipo y revisiones) | la copia diaria en IONOS: `respaldo/recuperar.sh` |
| Credenciales | ver abajo |

Credenciales, en `~/.config/credenciales/` del portátil, con los mismos nombres que en el NAS:
`bot-chatgpt-ia-edu.json` (token del bot), `telegram-cuenta.json` y
`telegram-cuenta.session` (cuenta de Juanjo, para descargar los mensajes),
`catalogo-vce.json` (API de la hoja) y `anthropic-bot.txt` (clave de API de Claude).
La cuenta de Telegram de Juanjo (avisos y `/estado`) va en la variable `JUANJO` del entorno, como en `nas/compose.yml`.
La de la copia (`respaldo-ionos.json`) solo está en el NAS: en la máquina nueva
se genera otra con `NAS_BOT=usuario@máquina respaldo/instalar.sh --testigo`
(cambiando la ruta `CRED_NAS` del guion).

Pasos:

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
respaldo/recuperar.sh                       # dueños de los recursos y gasto
cd scripts
../.venv/bin/python exportar.py --todo && ../.venv/bin/python pdfs.py && ../.venv/bin/python indexar.py
ABIERTO=1 ../.venv/bin/python bot.py        # el bot; solo puede haber uno en marcha con el mismo token
```

Con Docker, `nas/compose.yml` sirve tal cual cambiando las rutas de los
volúmenes. Si el NAS vuelve, antes de arrancarlo allí hay que pararlo en la
otra máquina y llevar de vuelta `datos/catalogo.json`, que habrá cambiado.

La copia la manda `scripts/respaldo.py` cada madrugada (tras la pasada
completa de las 3) a `bilateria.org/respaldo-bot-ia-educativa/`, que guarda 30
días y no deja descargar nada desde la web (`respaldo/`). Si falla, el bot
avisa a Juanjo por Telegram.

## Gasto

Cada pregunta cuesta del orden de 0,001–0,003 USD; una ficha de recurso para el repositorio, entre 0,03 y 0,10 USD según el tamaño del recurso (la lee Sonnet entera), y un documento de la Biblioteca, unos 0,06 USD. Tiene un tope mensual en la
consola de Claude y otro en el propio bot. No hay cupos a la vista: los cupos por
persona solo entran el día que se gasta más del doble de lo que toca, y quien
hace más de 30 consultas en una hora tiene que esperar (ADR 0006).
Juanjo ve las consultas y el gasto escribiendo `/estado` al bot (solo a él le responde), o con
`docker exec bot-chatgpt-ia-edu python bot.py estado` en el NAS. Del uso solo se
guardan cifras por día, sin separar grupos (ADR 0003), y durante el mes en qué días ha preguntado
cada cuenta, para saber cuántas personas vuelven (ADR 0014). La última respuesta lleva 👍/👎. Las
preguntas que el bot no consigue responder, y las marcadas con 👎, se guardan de forma anónima, sin
nada de quién pregunta, en `datos/sin-resolver.jsonl`, y se borran a los 60 días (ADR 0007).

Karla bot usa Claude Sonnet 5.5 hasta un gasto del mes y, a partir de ahí, Claude Haiku 5.5
hasta el día 1, con su propio tope.

## Versiones y pruebas

Cada versión lleva su etiqueta en git (`v1.0.0`, …) y su entrada en [CHANGELOG.md](CHANGELOG.md); la versión que corre se ve en la ayuda de los bots y en `/estado`. En cada push, GitHub Actions compila el código, pasa `ruff` y las pruebas de `pruebas/test_revision.py` (`.github/workflows/pruebas.yml`); no se despliega una versión con el flujo en rojo.

## Licencia

Código: AGPL-3.0-or-later. Imágenes de los bots (`imagen/avatar.jpg` y, de Karla bot, `docs/imagenes/karla-avatar.jpg`): CC BY-SA 4.0. Hecho por Juan José de Haro con IA
([nivel 4 del MIAE](https://jjdeharo.github.io/miae/?nivel=4)).
