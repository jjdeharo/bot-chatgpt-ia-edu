# 4. Recursos educativos para el catálogo de Vibe Coding Educativo

Fecha: 2026-10-27 · Estado: aceptado

## Contexto

El catálogo de Vibe Coding Educativo (https://vibe-coding-educativo.github.io/app_edu/)
lee una hoja de cálculo publicada en CSV. Hasta ahora se llenaba con un
formulario de Google que obliga a iniciar sesión en Google; una app de Gemini
ayudaba a rellenarlo. Para cambiar un recurso había que reenviar el formulario
entero con la misma URL o el mismo título; para quitarlo, marcar una casilla y
escribir «cualquier cosa» en el resto. Un Apps Script borraba cada noche los
duplicados y lo marcado. El 27-10-2026 el catálogo tenía 347 recursos de 41
correos distintos.

Juanjo quiere que el bot lo haga todo: «el usuario proporciona el código
fuente en forma de archivo único o repositorio, el bot analiza lo que hace y
completa la hoja de cálculo», con una forma sencilla de modificar y borrar. Y
que en el menú aparezcan las dos aportaciones, cada una solo para los miembros
de su grupo.

## Decisión

1. **El enlace basta.** Quien aporta un recurso manda su enlace: con
   `/repositorio`, suelto o pidiéndolo con sus palabras («añade mi app al
   repositorio https://…»), en cualquier idioma. Para eso último, Claude
   tiene en la búsqueda la herramienta `anadir_recurso`: el primer día, una
   petición así fue a la búsqueda y el bot contestó que solo servía para
   buscar. El bot lo abre como cualquier visitante: si el enlace
   no funciona o pide iniciar sesión, lo dice. Si la página no deja ver qué
   hace el recurso (un GPT, un Gem, una página que solo carga otra), pide el
   archivo HTML, un ZIP, el repositorio de GitHub o una explicación. Con un
   repositorio de GitHub lee el README y los archivos principales.
2. **Claude Sonnet 5.5 prepara la ficha** con las listas cerradas del
   formulario (tipo, niveles, áreas e idiomas), en castellano, la lengua del
   catálogo, aunque el bot hable con cada persona en su idioma (ADR 0005).
   Al principio la ficha seguía el idioma de la app de Telegram, y en la
   primera prueba real salió en inglés, porque la prueba se hizo con un
   cliente en inglés.
   Descarta lo que no es educativo. El autor sale del nombre de Telegram.
   Antes de publicar, la persona ve la ficha y puede pedir cambios con sus
   palabras (Claude Haiku 5.5 los aplica). Lo mismo con `/misrecursos` en uno
   ya publicado.
2b. **Los cambios miran otra vez el recurso** (Juanjo, 28-10-2026). Al
   principio Haiku recibía solo la ficha y la petición: «añade la licencia»
   no hacía nada, «revisa el tipo» o «rehaz la descripción» se resolvían a
   ciegas con lo que ya decía la ficha, y la ficha cambiada sustituía a la
   anterior entera, así que un cambio cualquiera borraba la licencia. Ahora
   recibe también lo leído del recurso: en un alta, lo mismo que sirvió para
   la ficha (que puede venir de un archivo, un repositorio o la nota de quien
   lo aporta); en uno publicado, la página o el repositorio leídos de nuevo,
   por si se ha puesto la licencia entretanto. Cambia solo lo que se pide;
   lo que pide revisar o rehacer lo hace a partir del recurso, con los
   mismos criterios que la ficha. La licencia sale siempre del código y se
   comprueba en cada cambio, aunque no se pida: así se completa la de las
   fichas antiguas, que no la tenían; si no la encuentra, deja la que había;
   si no hay ninguna o es cerrada, no guarda el cambio y explica cómo ponerla,
   como en el alta. Lo que el cambio no toca se conserva. Cuesta unos
   0,0015 USD por cambio (AulaMap, 28-10-2026), frente a casi nada antes.
   El enlace también se cambia, para un recurso que se ha mudado (Juanjo,
   28-10-2026, al pedir el nuevo del Calendario ODS: el bot lo ignoraba y
   decía «Así queda»). El bot comprueba que el enlace nuevo se abre y que no
   es el de otro recurso, rehace la ficha leyendo el recurso en su sitio
   nuevo (por si cambia su licencia, unos 0,0015 USD más) y, al publicar, la
   API cambia la fila que tenía el enlace antiguo; el dueño pasa al enlace
   nuevo, también el correo del antiguo formulario. Lo que el enlace no
   conserva: los favoritos de la web del catálogo, que se guardan por enlace
   en cada navegador. Validación: `pruebas/simular_catalogo.py` (enlace de
   otro recurso rechazado; mudanza sin duplicar la fila y con el mismo dueño)
   y, en la hoja real, una fila de prueba dada de alta, mudada, con el
   duplicado rechazado y borrada.
2c. **/misrecursos también añade uno nuevo** (Juanjo, 28-10-2026): debajo de la
   lista, y en el aviso de quien aún no tiene ninguno, el botón «Añadir un
   recurso nuevo» pide el enlace como /repositorio.
3. **El bot escribe en la hoja** a través de una aplicación web de Apps
   Script del propio catálogo (`api.gs` en Vibe-Coding-Educativo/app_edu),
   protegida con una clave que comparte con el bot. La web del catálogo no
   cambia: sigue leyendo el mismo CSV. Los cambios modifican la fila en su
   sitio y conservan la fecha de alta; quitar un recurso borra su fila. Ya no
   hacen falta duplicados ni casillas de borrado.
4. **El dueño es la cuenta de Telegram.** El bot guarda en
   `datos/catalogo.json` qué cuenta dio de alta cada recurso. Los recursos del
   formulario están ligados a un correo: la primera vez que alguien quiere
   gestionarlos, el bot manda un código de seis cifras a ese correo (desde la
   cuenta de Juanjo, con Apps Script) y, si lo escribe bien, liga ese correo a
   su cuenta de Telegram.
5. **Solo recursos gratuitos y con el código bajo una licencia abierta**
   (Juanjo, 27-10-2026: «lo que no quiero son programas cerrados que no se
   puede examinar el codigo o con los que se hace negocio»). Se rechaza lo
   que no es educativo, lo de pago y lo freemium. La licencia tiene que
   constar en el código (comentario SPDX, pie, metadatos) o en su repositorio;
   decirla en la conversación no basta. Valen las de código abierto, el
   dominio público y cualquier Creative Commons, también las NC: Juanjo pidió
   primero «al menos opensource» y lo rectificó el mismo día («CC BY-NC-SA
   4.0 aunque no sea libre es abierta»). De una página `usuario.github.io/repo`
   se mira la licencia de `github.com/usuario/repo`. A quien no tiene licencia,
   el bot le ofrece recomendarle una según lo que quiera permitir, con el
   criterio de la guía Vibe coding responsable (AGPL v3 o MIT para el código,
   CC BY-SA o CC BY para los contenidos; NC admitida pero desaconsejada), le
   explica cómo ponerla (LICENSE en GitHub, línea SPDX y pie en el HTML, o
   pedírselo a la IA con que lo hizo) y enlaza el capítulo 9 de la guía en su
   idioma. Después le deja volver a enviar el recurso, que vuelve a leer.
   Primero enlazaba el generador de licencias de Juanjo, que no le convence
   (27-10-2026).
   Lo compartido en Gemini o en Claude también necesita la licencia en su
   código: la plataforma deja copiarlo dentro de ella, pero eso no es una
   licencia para usarlo fuera (las condiciones de Google mantienen los
   derechos del autor y el permiso a Google es para que el servicio funcione).
   Como el bot no puede leer esos enlaces, pide el archivo HTML.
5b. **Presentarlo en «¡Comparte tu App!»** (Juanjo, 27-10-2026). Al publicar un
   recurso nuevo, el bot pregunta si lo comparte en ese tema de VCE, avisando de
   que aún no se publicará nada. Si dice que sí, Claude Haiku escribe tres o
   cuatro frases, como las contaría una persona, sin apartados y sin añadir nada
   que no diga la ficha, en el idioma de la conversación. Va en tercera persona
   y empieza por el nombre y el @usuario del autor, porque lo publica el bot. La
   persona puede publicarlo, pedir cambios, cancelarlo o elegir «Lo publico yo»,
   y entonces recibe el texto en primera persona para mandarlo con su cuenta. Al
   publicarlo, el aviso lleva «Quitarlo del grupo» y «Mantenerlo»: Telegram deja
   a un bot borrar sus propios mensajes durante 48 horas; después, el bot remite
   a quien administra el grupo.
5c. **Un mínimo, y revisión manual de lo que el bot rechaza** (Juanjo,
   30-10-2026, al preguntar si el bot comprueba «que el recurso tenga un
   mínimo de nivel y no acepta cualquier cosa», y después: «proporciona un
   medio para impugnar esta decisión»). Además de ser educativo, el recurso
   tiene que poder usarse en clase tal como está: fuera lo roto o a medio
   hacer, las plantillas y páginas de prueba sin contenido propio y lo que
   enseña con errores de bulto. No es una nota: no se juzga si es mejor que
   otros ni si es sencillo, y en la duda entra. Lo decide Claude Sonnet en la
   misma llamada de la ficha (`nivel_minimo`, criterio en
   `catalogo.ADMISION`), sin coste añadido. Al rechazar un recurso por no ser
   educativo o por el mínimo, el bot ofrece «Pedir una revisión»: la persona
   cuenta en un mensaje por qué debería entrar, y a Juanjo le llega el recurso
   con el motivo del bot, las razones de su autor y dos botones. «Cumple» lo
   apunta como aprobado y sigue el alta donde la dejó el rechazo (pago,
   licencia y ficha para publicar); «No cumple» se lo dice al autor. Los casos
   se guardan en `datos/revisiones.json`, que sobrevive a un reinicio y va en
   la copia diaria (sin lo leído del recurso, que se vuelve a leer); un
   enlace aprobado no se vuelve a rechazar por su contenido. Cuando un recurso
   publicado cambia de enlace, el bot comprueba también que lo que hay en el
   nuevo sigue entrando (`Fichas.admitir`, Sonnet con el mismo criterio, unos
   0,01 USD por mudanza); si no, no guarda el cambio y lo explica.
6. **Se llama «repositorio»**, como lo titula su web («Repositorio de
   aplicaciones educativas») y como lo conoce la comunidad (Juanjo,
   27-10-2026). El comando era `/recurso` y los mensajes decían «catálogo»;
   `/recurso` sigue valiendo, fuera del menú. En el código y en estos ADR se
   mantiene «catálogo».
7. **Cada aportación, para los miembros de su grupo** (Juanjo, 27-10-2026):
   la Biblioteca digital, para los de ChatGPT-IA-edu; el catálogo, para los de
   Vibe Coding Educativo. Buscar sigue abierto a los de cualquiera de los dos.
   El menú del bot (`setMyCommands`) muestra las cinco acciones a todos (Juanjo
   prefirió que, si alguien intenta algo que no puede, el bot le diga cómo
   unirse al grupo), y la ayuda solo explica las que tocan a cada persona. El
   chat de Juanjo tenía un menú propio con `/ayuda` y `/estado`, puesto en las
   pruebas, que tapaba el general: el bot le pone ahora el completo más
   `/estado`.
8. **Cupos.** Cinco fichas de recurso al día por persona (`RECURSOS_DIA`),
   dentro del tope de gasto común. Cada código enviado cuenta en el cupo: nadie
   puede llenar de códigos el buzón de otra persona.

## Alternativas descartadas

- Seguir con el formulario y que el bot lo enviara: el formulario exige
  iniciar sesión en Google con la cuenta de quien aporta.
- Una cuenta de servicio de Google con la API de Sheets: obliga a crear un
  proyecto en Google Cloud; Apps Script ya estaba en el catálogo, con `clasp`.
- Identificar al dueño por el nombre que aparece en el recurso: cualquiera
  puede escribir cualquier nombre.

## Consecuencias

- Los recursos que da de alta el bot no llevan correo: la columna queda vacía
  y el script de limpieza nocturna los ignora.
- El formulario se cerró el 27-10-2026 con un mensaje que remite al bot. Si
  el bot cayera mucho tiempo, Google permite reabrirlo en un minuto: es la
  salida de emergencia (README, «Si el NAS falla»). El enlace de la app de
  Gemini que lo rellenaba (`ja.cat/form-analiza`) sigue apuntando a ella.
- Los correos de quienes usaron el formulario salieron de la hoja el
  27-10-2026: están en el almacén privado del Apps Script y la API se los da
  al bot (ADR 0001 de app_edu). El CSV público ya no tiene ninguno.
- Para escribir al autor de un recurso (por ejemplo, si una comprobación
  automática ve que ya no se abre), el bot le escribe por Telegram: puede
  hacerlo con cualquiera que le haya hablado, y quien da de alta un recurso le
  ha hablado. Los del formulario, por correo hasta que lo recuperen con
  /misrecursos. No se pide correo a los nuevos (Juanjo, 27-10-2026).

## Riesgos y limitaciones

- La clave del bot da acceso de escritura a la hoja: está solo en
  `~/.config/credenciales/catalogo-vce.json` y en las credenciales del NAS;
  en el repositorio público del catálogo va solo su huella SHA-256.
- Lo que se lee del recurso y lo que escribe la persona se procesa en
  Anthropic (Estados Unidos), como el resto del bot.
- El CSV publicado tarda unos minutos en reflejar los cambios.
- El mínimo solo ve lo que el bot puede leer. Los errores de lógica escondidos
  en el código (una regla de cálculo mal planteada) no los detecta: con la
  instrucción de comprobar cada error paso a paso deja de señalarlos, y sin
  ella los señalaba con motivos en parte falsos (validación del 30-10-2026).
  Se prefiere dejar pasar un error sutil a rechazar con un motivo inexacto.
- El rechazo de una mudanza no ofrece revisión manual: el recurso sigue
  publicado con su enlace anterior y su autor puede comentarlo en el grupo.

## Validación

30-10-2026 (punto 5c):
- 29 recursos del repositorio tomados al azar, con la primera versión del
  criterio: el mínimo rechazó 2. En los dos había un error real (la práctica
  de monotonía de funciones logarítmicas decide creciente o decreciente solo
  por el signo de `a`; en el ajuste de reacciones, una ecuación con el hierro
  sin igualar), pero el motivo del segundo daba por malas ecuaciones que
  están bien. Con la instrucción de citar solo el error más claro y
  comprobado, los dos pasan, y el resto ya pasaba con la versión más estricta.
  Unos 0,03 USD por recurso.
- Primero la comprobación de la mudanza iba en la instrucción de los cambios:
  Haiku pasó a rehacer la descripción en 9 de 10 cambios que no la pedían
  (antes, 0 de 10). Se sacó a una llamada aparte y volvió a 0 de 10.
- `pruebas/simular_catalogo.py`: un recurso sencillo y completo entra; una
  página con «Próximamente» y una con sumas de fracciones mal resueltas no;
  tampoco una mudanza a una página a medio hacer; el rechazo ofrece «Pedir una
  revisión», la petición llega a Juanjo con las razones y «Cumple» enseña la
  ficha al autor, una sola vez. 76 comprobaciones bien en dos pasadas seguidas.

27-10-2026:
- Ficha de «Atzar a l'aula» (https://ja.cat/atzar) a partir de su página:
  descripción fiel, listas correctas, 0,012 USD.
- API: lectura de las 347 filas; alta, cambio, rechazo del duplicado y baja
  de una fila de prueba, borrada en el acto.
