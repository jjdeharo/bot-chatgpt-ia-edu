# 19. Controles de publicación y de entrada tras la revisión de seguridad

Fecha: 2026-10-31 · Estado: aceptado

## Contexto

El 31-10-2026, una revisión del código de los dos bots hecha por otro agente (Codex; informe
privado) encontró seis defectos reproducibles y cuatro mejoras. Todos se comprobaron
después en el código del commit `acd7517` y resultaron ciertos:

1. Un botón de una vista previa anterior confirmaba el borrador vigente, que podía ser otro: los
   botones solo decían `publicar`, `rp` o `inc:si`, y el bot recuperaba «el pendiente de esa
   persona». En Karla, además, la vista previa recortaba el cuerpo a 3.000 caracteres.
2. El permiso para adjuntar un PDF a la Biblioteca dependía de que la ficha contuviera la frase
   literal «No se podrá compartir»; cualquier otra redacción del modelo permitía compartirlo.
3. Un enlace aportado al catálogo llegaba a `urlopen` sin comprobar que fuera público: podía
   apuntar al propio NAS o a otro contenedor, y sus redirecciones no se comprobaban.
4. Un ZIP se descomprimía entero en memoria (`z.read(n)[:MAX_CODIGO]`) antes de recortarlo: un
   archivo de 4 KB hacía leer 4 MB, y uno preparado a propósito, mucho más. Y se descargaba
   antes de mirar el cupo.
5. `Consultor` tenía dos métodos `autores`; el segundo tapaba al primero y la herramienta
   `buscar_autor` fallaba siempre con `TypeError` (el modelo seguía con otras búsquedas, por eso
   no se notó).
6. La detección del idioma con Claude se lanzaba antes de comprobar si quien escribe es miembro
   y si queda presupuesto.

Mejoras: la espera de mensajes seguidos no tenía tope; un reintento de publicación en la
Biblioteca volvía a mandar el documento; la limpieza de las preguntas sin resolver solo se
hacía al guardar otra y la memoria de conversación nunca se borraba; y `nas/bucle.sh` escribía
la marca `ultima-pasada` aunque hubiera fallado la exportación o el índice.

## Decisión

Corregir los controles sin cambiar la arquitectura ni los modelos:

- **Cada borrador lleva una clave** (`Bot.clave_borrador`, 6 caracteres hexadecimales) que va en
  sus botones (`publicar:<clave>`, `rp:<clave>`, `inc:si:<clave>`…) y en el pendiente. Si la del
  botón no coincide con la vigente, el bot contesta «sustituido» y no toca nada; y al preparar
  una vista previa nueva se quitan los botones de la anterior. Antes de publicar se vuelve a
  comprobar la pertenencia al grupo. Karla enseña el cuerpo entero, en varios mensajes si hace
  falta.
- **El permiso de redistribución sale del apartado Licencia de la ficha** (`fichas.se_puede_compartir`):
  el archivo se adjunta solo si ese apartado nombra una licencia abierta (Creative Commons,
  dominio público, GPL, MIT… o un permiso expreso de distribución) y no dice nada en contra. Si
  falta el apartado o hay duda, se publica solo la ficha, que es lo que el bot ya sabía hacer.
- **Solo direcciones públicas** (`catalogo.direccion_publica`): http o https, nombre con punto,
  y todas las direcciones IP a las que resuelve tienen que ser globales (`ipaddress.is_global`).
  Se comprueba la dirección inicial, cada redirección (`_SoloPublicas`) y cada salto de `saltos`.
  Un enlace interno recibe el aviso «El enlace no lleva a una web pública».
- **El ZIP se lee por flujo** (`z.open(info).read(MAX_CODIGO + 1)`), con tope de 2.000 entradas,
  y el cupo se mira antes de descargar. `pdftotext` y `pdfinfo` tienen tiempo máximo.
- **Primero quién es, luego la IA**: `fijar_lengua` solo pone el idioma de Telegram;
  `lengua_de_la_frase` se llama después de comprobar permiso y pertenencia, no lanza nada si se
  ha llegado al tope del mes y admite dos detecciones a la vez (`DETECCIONES`).
- Los dos métodos pasan a llamarse `autores` (búsqueda) y `nombres_del_grupo` (revisión de
  atribuciones).
- La espera de mensajes seguidos acaba a los 15 s o 100 mensajes. Un reintento de publicación
  reutiliza el documento ya enviado (`p["doc"]`). Cada hora, `Bot.limpiar` borra lo caducado
  (memoria, borradores, esperas, consultas recientes y preguntas sin resolver de más de 60 días).
  El bucle del Bot de IA Educativa protege cada actualización con `try`, como ya hacía Karla.
- `nas/bucle.sh` escribe `ultimo-intento` en cada pasada y `ultima-pasada` solo si todos los
  pasos han ido bien: lo que los bots dicen como «última puesta al día» es una puesta al día
  completa.

## Alternativas descartadas

- Pedir a Claude una decisión estructurada sobre la licencia en otra llamada: más gasto por
  documento y la misma dependencia del modelo; el apartado Licencia ya tiene formato fijo.
- Fijar la IP resuelta en la conexión (contra un cambio de resolución entre la comprobación y
  la petición): con `urllib` exige rehacer la conexión TLS a mano; queda como límite conocido.
- Guardar los borradores en disco para que sobrevivan a un reinicio: el reinicio es raro y el
  borrador se rehace mandando el documento otra vez; no compensa el estado persistente.
- Una cola con trabajadores para atender varias consultas a la vez: `Consultor` guarda el
  ámbito de búsqueda en el propio objeto y habría que aislarlo por petición; se deja para
  cuando la espera entre personas lo pida.

## Consecuencias

- Los botones de las vistas previas anteriores al despliegue no llevan clave: al pulsarlos el
  bot responde «caducado», porque el reinicio ya vaciaba los pendientes.
- Un documento con licencia abierta escrita de una forma que no reconozca `LICENCIA_ABIERTA`
  se publica sin el archivo (solo la ficha): es el lado seguro, y el texto «vista_sin_archivo»
  se lo dice a quien lo aporta antes de publicar.
- Si una pasada del índice falla, la fecha que enseñan los bots deja de avanzar y el vigía del
  NAS, si mira esa marca, avisa: es lo que se quiere.

## Evidencia

- Informe de la revisión del 31-10-2026 (privado), con sus seis pruebas aisladas sobre el commit
  `acd7517`; las mismas pruebas, sobre el código corregido, están en `pruebas/test_revision.py`.
- `pruebas/test_revision.py`: 23 pruebas sin red ni API que reproducen cada defecto sobre el
  código corregido (`.venv/bin/python -m unittest pruebas/test_revision.py`).
- `ipaddress.is_global` excluye las direcciones privadas, de bucle local, de enlace local,
  reservadas y multicast: https://docs.python.org/es/3/library/ipaddress.html#ipaddress.IPv4Address.is_global
- `ZipFile.open` devuelve un flujo que se lee a trozos; `ZipFile.read` devuelve la entrada
  entera: https://docs.python.org/es/3/library/zipfile.html#zipfile.ZipFile.open

## Riesgos y limitaciones

- Un servidor cuyo nombre resuelva a una IP pública al comprobar y a una privada al conectar
  (cambio de resolución) seguiría pasando; hipótesis no probada en el NAS. La red del contenedor
  es la de Docker por defecto, sin restricción de salida.
- `direccion_publica` hace una resolución DNS por enlace y por salto: unos milisegundos más
  por recurso.
- La lista `LICENCIA_ABIERTA` es cerrada: una licencia libre poco común se trata como dudosa.

## Validación

- `pruebas/test_revision.py`, 23 pruebas, todas en verde el 31-10-2026.
- Los módulos compilan e importan sin red; `bash -n nas/bucle.sh`.
- Pendiente de observar en producción: que una ficha de la Biblioteca con licencia abierta
  siga adjuntando el archivo, y que `ultima-pasada` avance cada 15 minutos.
