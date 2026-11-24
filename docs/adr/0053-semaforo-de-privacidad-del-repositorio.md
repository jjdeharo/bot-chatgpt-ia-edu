# 53. Semáforo de privacidad del repositorio

Fecha: 2026-11-24 · Estado: aceptado

## Contexto

El 23-11-2026, la [Guía de privacidad de herramientas educativas](https://guia-privacidad-edu.github.io/)
evaluó las aplicaciones del repositorio de Vibe Coding Educativo con el modelo del anexo I
de las *Orientaciones* del INTEF sobre protección de datos (v3.0, junio de 2026). Para ello
abrió cada una en un navegador y anotó con qué servidores conecta, qué les manda, qué cookies
pone y si pide iniciar sesión o datos personales. El resultado es un semáforo:

- verde, si no trata datos personales;
- amarillo, si los trata (servicios de datos, inicio de sesión, contadores de visitas,
  envíos a servidores ajenos);
- rojo, si sigue a quien la visita con analítica comercial (Google Analytics, Amplitude…).

El 24-11-2026 Juanjo decidió, por pasos:

- que el color saliera en el propio repositorio, en una base común (la hoja);
- que se calculara al dar de alta con el bot y no solo por la noche, para tenerlo al momento;
- que lo rojo no se admitiera en las altas nuevas, con revisión manual a petición;
- que una pasada cada noche mirara todas las aplicaciones;
- que las rojas, también las dos que ya había, siguieran a la vista pero con el enlace
  desactivado, y que se avisara a sus autores;
- que la guía fuera solo del INTEF: «lo del intef solo del intef». El evaluador pasó aquí.

## Decisión

- **El evaluador vive en este repositorio**:
  - `scripts/semaforo_auditar.py`: lo que se ve de una aplicación en Chromium;
  - `scripts/semaforo_reglas.py`: las reglas del color;
  - `scripts/semaforo.py`: el servicio, la pasada y los avisos.

  Viene de la guía (su ADR 0006), con las mismas reglas.
- **Corre en su propio contenedor del NAS**, `bot-semaforo`. Usa la imagen del boletín
  semanal, que ya trae Chromium, como el servicio de voz. La imagen del bot no crece:
  meterle un navegador eran unos 500 MB, y las reglas habrían quedado en dos sitios.
- **El navegador no entra en la red de casa.** Antes de evaluar, el enlace tiene que llevar
  a una dirección pública. Durante la visita, cualquier petición de la página a una
  dirección privada se corta. Las aplicaciones las manda cualquiera, y el navegador corre
  en el NAS.
- **En el alta.** El bot pide el color (`POST /evaluar`) después de comprobar el pago y la
  licencia, y lo enseña en la ficha («Privacidad: Amarillo. Envía datos…»). Al publicar, lo
  escribe en la hoja con el resto de la ficha. Si sale rojo, no lo publica: explica el
  motivo y cómo arreglarlo, y ofrece «Pedir una revisión», el mismo recorrido que los
  rechazos por contenido. Si Juanjo dice que cumple, se publica con el motivo precedido de
  «Admitida tras revisión manual», y la web no le desactiva el enlace.
- **Al cambiar el enlace.** Se evalúa la dirección nueva; si es roja, no se cambia. Los
  demás cambios no tocan el color (`a_fila` solo lo incluye si la ficha lo trae).
- **Si el servicio no responde,** la ficha se publica sin color («Pendiente de evaluar» en
  la web) y la pasada de la noche lo pone. Un fallo del semáforo no impide dar de alta.
- **La pasada de cada noche** (desde las 3:30, tres intentos; si fallan, aviso a Juanjo):
  - abre las 385 aplicaciones, unos 10 o 15 minutos;
  - escribe en la hoja las filas que cambian (acción `semaforos` de `api.gs`);
  - avisa al autor de cada aplicación que pasa a rojo, y otra vez cuando deja de serlo.
    `datos/semaforo/avisados.json` apunta a quién se ha avisado de qué, para no repetir.
    A Juanjo le llega una línea por cada aviso.
- **Cómo llega el aviso:**
  - por Telegram, desde el bot, si el autor lo ha usado: el recurso es suyo en
    `catalogo.json`, o su correo del antiguo formulario está ligado a su cuenta;
  - si no, por correo, con la acción `avisar_correo` de `api.gs`, que escribe al correo
    con que se dio de alta el recurso. El bot no ve la dirección.

  Va en castellano, como las fichas: el bot no guarda en qué idioma habla cada persona
  (ADR 0005).
- **`AVISOS_SEMAFORO`** (en `nas/compose.yml`) dice qué se hace con los avisos:
  - `autores`: los manda;
  - `juanjo`: le manda a Juanjo cada aviso tal como saldría, para verlo;
  - vacío: solo los apunta en el registro.

  Empezó en `juanjo` y pasó a `autores` el 24-11-2026, cuando Juanjo aprobó los textos.

- **Lo que no es una aplicación web** sale «sin evaluar», con un motivo que dice lo que
  pasa (Juanjo, 24-11-2026, al ver que «no se puede abrir» confundía):
  - un repositorio de código: «Es el código en GitHub, no una aplicación web». Si publica
    una web (su página de inicio, que no sea npm, o GitHub Pages; lo dice la API de GitHub),
    se revisa esa web y el motivo empieza por «Revisada su versión web (…)»;
  - una descarga: «Descarga un programa para instalar»;
  - un 404: «La página no existe».

  Los enlaces rotos ya los lleva la revisión del repositorio (ADR 0039).

## Consecuencias

- La web del repositorio (ADR 0002 de app_edu) enseña el color en cada tarjeta y desactiva
  el enlace de las rojas no admitidas.
- La ayuda del repositorio y los textos del bot dicen la condición nueva: no se admiten
  aplicaciones con analítica comercial.
- Una aplicación roja que se arregla vuelve a estar activa a la mañana siguiente, sin que
  nadie haga nada.
