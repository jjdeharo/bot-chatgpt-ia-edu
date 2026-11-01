# SPDX-License-Identifier: AGPL-3.0-or-later
"""Lo que dice el bot, en castellano, catalán, gallego, euskera e inglés.

El bot habla en el idioma en que le escribe cada persona y, mientras no ha
escrito nada, en el de su Telegram; si no es uno de estos cinco, en castellano
(ADR 0005). Las traducciones son automáticas, hechas con IA, sin revisión
profesional. Lo que falte en un idioma sale en castellano.

Las fichas del repositorio y de la biblioteca no se traducen: son contenido
común y van en castellano.
"""

LENGUAS = ("es", "ca", "gl", "eu", "en")

ES = {
    "al_menos_uno": 'Tiene que quedar al menos un grupo marcado.',
    "quitado_biblioteca": 'Quitado de la Biblioteca digital.',
    "b_quitar_biblioteca": 'Quitarlo de la Biblioteca',
    "buscando_en": 'Buscando en: {grupos}.',
    "b_mantener": 'Mantenerlo',
    "b_quitar_grupo": 'Quitarlo del grupo',
    "no_quitar_ya": 'Ya no puedo quitarlo: Telegram solo deja borrar los mensajes durante 48 horas. Pídeselo a quien administra el grupo.',
    "mantenido": 'De acuerdo, se queda publicado.',
    "quitado_grupo": 'Quitado del grupo.',
    "pregunta_compartir": '¿Quieres compartirlo también en «¡Comparte tu App!» del grupo Vibe Coding Educativo? Todavía no se publicará nada: antes te enseñaré el mensaje para que lo revises, lo cambies o lo canceles.',
    "vista_compartir": 'Este es el mensaje que publicaría en «¡Comparte tu App!», con tu nombre como autor. Puedes publicarlo, pedirme cambios, publicarlo tú o cancelarlo.',
    "compartido": 'Publicado en «¡Comparte tu App!»: {enlace}\nSi cambias de idea, puedes quitarlo con el botón de abajo durante las próximas 48 horas.',
    "publicalo_tu": 'Aquí tienes el texto para que lo publiques tú en «¡Comparte tu App!»: https://t.me/vceduca/7674',
    "no_compartir": 'De acuerdo, no lo comparto.',
    "b_si": 'Sí',
    "b_lo_publico_yo": 'Lo publico yo',
    "b_anteriores": "Anteriores",
    "b_siguientes": "Siguientes",
    "seguidas": "Me has hecho muchas preguntas seguidas y necesito un respiro. Vuelve a escribirme dentro de un rato y seguimos.",
    "aviso_freno": ("Aviso del Bot de IA Educativa: hoy se han gastado {usd:.2f} USD, más del doble de lo que toca por día para no pasar del tope del mes ({diario:.2f} USD). Hasta mañana se aplican los cupos por persona: {cupo} preguntas, {docs} documentos y {recursos} recursos."),
    # Perfil del bot (setMyDescription y setMyShortDescription): aquí va la autoría.
    "perfil": 'Busco en los grupos ChatGPT-IA-edu, Vibe Coding Educativo y EduMedia-IAG quién dijo algo, cuándo y en qué mensaje, y qué documentos de la Biblioteca digital tratan un tema. También añado documentos a la Biblioteca y recursos educativos al repositorio de Vibe Coding Educativo. Uso Claude, una IA de Anthropic. Creado por @jjdeharo.',
    "perfil_corto": 'Busca en ChatGPT-IA-edu, Vibe Coding Educativo y EduMedia-IAG, y añade documentos y recursos.',
    "licencia_cerrada": 'No lo añado todavía: su licencia ({licencia}) no deja compartir el código. El repositorio admite licencias abiertas: de código abierto o Creative Commons. Si no sabes cuál elegir, pregúntamelo: te recomiendo una según lo que quieras permitir y te explico cómo ponerla. Tienes más información en https://vibe-coding-educativo.github.io/vibe-responsable/es/capitulo-9.html. Después envíame otra vez el recurso: el archivo HTML, un ZIP o el enlace a su repositorio de GitHub.',
    "de_pago": "No puedo añadirlo: el repositorio es solo para recursos gratuitos, sin versiones de pago ni freemium, y este no lo parece ({detalle}).",
    "sin_licencia": 'No lo añado todavía: el repositorio pide que el código esté publicado con una licencia abierta, y no encuentro ninguna en el código ni en su repositorio. Si no sabes cuál elegir, pregúntamelo: te recomiendo una según lo que quieras permitir y te explico cómo ponerla. Tienes más información en https://vibe-coding-educativo.github.io/vibe-responsable/es/capitulo-9.html. Después envíame otra vez el recurso: el archivo HTML, un ZIP o el enlace a su repositorio de GitHub.',
    "licencia_visible": "Un consejo: la licencia ({licencia}) está en el repositorio, así que el recurso cumple, pero quien abre la página no la ve. Para que cualquiera sepa que puede reutilizarlo, pon una línea visible en el pie, como «Licencia {licencia}», y otra al principio del código: <!-- SPDX-License-Identifier: {spdx} -->. Si lo has hecho con una IA, pídele que añada esas dos líneas. Es una recomendación, no un requisito.",
    "cambio_licencia_cerrada": 'No guardo el cambio: su licencia ({licencia}) no deja compartir el código, y el repositorio solo admite licencias abiertas: de código abierto o Creative Commons. Si no sabes cuál elegir, pregúntamelo: te recomiendo una según lo que quieras permitir y te explico cómo ponerla. Tienes más información en https://vibe-coding-educativo.github.io/vibe-responsable/es/capitulo-9.html. Cuando la hayas cambiado, pulsa «Cambiar algo» otra vez.',
    "cambio_sin_licencia": 'No guardo el cambio: el repositorio pide que el código esté publicado con una licencia abierta, y no encuentro ninguna en el código ni en su repositorio. Si no sabes cuál elegir, pregúntamelo: te recomiendo una según lo que quieras permitir y te explico cómo ponerla. Tienes más información en https://vibe-coding-educativo.github.io/vibe-responsable/es/capitulo-9.html. Cuando la hayas puesto, pulsa «Cambiar algo» otra vez.',
    # La ayuda se arma con los apartados que tocan a cada persona según sus grupos.
    "inicio": ("Hola. Soy el bot de los grupos [ChatGPT-IA-edu](https://t.me/ChatGPTedu), "
               "[Vibe Coding Educativo](https://t.me/vceduca) y [EduMedia-IAG](https://t.me/EduMediaIAG). Te ayudo con esto:"),
    "ayuda_buscar": (
        "🔍 Buscar en los grupos. Pregúntame con tus palabras quién dijo algo, cuándo, qué documentos "
        "de la Biblioteca digital de ChatGPT-IA-edu o qué recursos del repositorio de Vibe Coding Educativo "
        "tratan un tema, y te respondo con el enlace de cada uno. Busco en los tres grupos a la vez; si quieres "
        "solo uno o dos, nómbralos. Por ejemplo: "
        "«¿quién habló de evaluar con IA el curso pasado?», «¿hay guías sobre IA en infantil?», "
        "«¿hay alguna aplicación para practicar probabilidad?» o "
        "«¿qué se ha dicho en Vibe Coding Educativo sobre publicar en GitHub Pages?»."),
    "ayuda_biblioteca": (
        "📄 Añadir un documento a la Biblioteca digital de ChatGPT-IA-edu. Envíame aquí el archivo en PDF "
        "(hasta 20 MB) y yo me encargo de todo: compruebo que trate de IA en educación y que no esté ya en "
        "la biblioteca, preparo su ficha y te la enseño. Si te parece bien, lo publico con tu nombre. Si su "
        "licencia no permite compartirlo, publico solo la ficha."),
    "ayuda_recurso": (
        "📱 Añadir un recurso educativo digital al [repositorio de Vibe Coding Educativo](https://vibe-coding-educativo.github.io/app_edu/)"
        ". Envíame su enlace: leo el recurso, preparo su "
        "ficha y te la enseño; si te parece bien, la publico. Tiene que ser gratuito y tener el código "
        "publicado con una licencia abierta. Con /misrecursos puedes cambiar o quitar los tuyos cuando quieras."),
    "ayuda_menu": 'Todas las opciones están en el menú: el botón «Menú», a la izquierda de donde escribes.',
    "ayuda_final": (
        "Cómo funciono: soy un programa que usa Claude, una IA de Anthropic. Lo que me escribes, los "
        "mensajes de los grupos que encuentro y lo que me envías se procesan en servidores de "
        "Anthropic, en Estados Unidos. Solo guardo las preguntas que no consigo responder o que marcas con 👎, sin tu nombre ni tu cuenta, para mejorar el bot, y las borro a los 60 días. Puedo equivocarme: comprueba siempre "
        "el mensaje enlazado. Te hablo en el idioma en que me escribes."),
    "traduccion": "",
    "buscar": 'Escríbeme lo que buscas, con tus palabras. Busco en los grupos marcados; toca uno para marcarlo o desmarcarlo. Lo mantendré mientras sigamos hablando.',
    "biblioteca": "Envíame el documento en PDF (hasta 20 MB) y preparo su ficha.",
    "solo_chatgpt": "Añadir documentos a la Biblioteca digital es cosa de los miembros de ChatGPT-IA-edu. Entrar es libre: únete al grupo y vuelve a enviármelo. Este es el grupo: https://t.me/ChatGPTedu",
    "solo_vce": ("El repositorio de recursos es de la comunidad Vibe Coding Educativo; para añadir los tuyos, "
                 "únete al grupo: https://t.me/vceduca"),
    "no_miembro": "Lo siento, solo puedo responder a quien forma parte de los grupos ChatGPT-IA-edu (https://t.me/ChatGPTedu), Vibe Coding Educativo (https://t.me/vceduca) o EduMedia-IAG (https://t.me/EduMediaIAG). Entrar es libre: únete a cualquiera y vuelve a escribirme.",
    "no_autorizado": "Todavía estoy en pruebas. Pronto estaré abierto a los grupos.",
    "cupo": "Has llegado a las {cupo} preguntas de hoy. Mañana podrás seguir.",
    "tope": "Este mes se ha agotado el presupuesto del bot. Volverá a funcionar el día 1.",
    "error": "Algo ha fallado al buscar. Prueba otra vez en un momento.",
    "solo_texto": "Por ahora solo entiendo mensajes escritos y capturas de pantalla. Escríbeme la pregunta, por favor.",
    "aviso_80": ("Aviso del Bot de IA Educativa: este mes se han gastado {usd:.2f} USD de los {tope:.0f} del tope "
                 "({n} preguntas). Al llegar al tope dejaré de responder hasta el día 1. Para subirlo: "
                 "TOPE_MES_USD en el compose del NAS y el límite del espacio de trabajo en la Console."),
    "solo_privado": "Hola, {nombre}. Soy el Bot de IA Educativa. En el grupo no puedo contestarte, pero por privado sí. Escríbeme aquí: https://t.me/{usuario}",
    "solo_privado_comando": "Hola, {nombre}. Soy el Bot de IA Educativa. Esto no funciona en el grupo, pero por privado sí. Ábrelo aquí: https://t.me/{usuario}?start={comando}",
    "no_pdf": "Para añadir un documento a la Biblioteca digital, envíamelo en PDF.",
    "grande": ("Este archivo pesa {mb:.0f} MB y Telegram solo deja a los bots descargar archivos de hasta "
               "20 MB, así que no puedo leerlo. Puedes subirlo tú directamente a la Biblioteca digital "
               "(https://t.me/ChatGPTedu/21753) y preparar su ficha con https://chatgpt-ia-edu.github.io/resumen/"),
    "cupo_docs": "Ya me has enviado {docs} documentos hoy. Mañana podrás enviar más.",
    "leyendo": "Recibido. Lo leo, compruebo si encaja en la biblioteca y preparo la ficha. Tardo un minuto.",
    "sin_texto": ("No puedo leer el texto de este PDF: parece escaneado como imagen. Puedes subirlo tú "
                  "directamente a la Biblioteca digital (https://t.me/ChatGPTedu/21753) y preparar su "
                  "ficha con https://chatgpt-ia-edu.github.io/resumen/"),
    "ajeno": "No puedo añadirlo: la Biblioteca digital es para documentos sobre inteligencia artificial en educación, y este trata de otra cosa ({tema}).",
    "repetido": "Este documento ya está en la Biblioteca digital: {enlace}",
    "vista": ("Esta es la ficha. Si te parece bien, publicaré en la Biblioteca digital el documento con "
              "«Aportado por {autor}» y la ficha en respuesta."),
    "vista_sin_archivo": ("Esta es la ficha. Su licencia no permite compartir el archivo, así que publicaré "
                          "en la Biblioteca digital solo la ficha, con «Aportado por {autor}»."),
    "publicado": 'Publicado en la Biblioteca digital: {enlace}\nSi cambias de idea, puedes quitarlo con el botón de abajo durante las próximas 48 horas.',
    "cancelado": "De acuerdo, no lo publico.",
    "caducado": "Esta ficha ya no está disponible. Si quieres publicarlo, envíame otra vez el documento.",
    "sustituido": "Esa vista previa ya no es la última: te he preparado otra después. Usa los botones del último mensaje.",
    "error_doc": "Algo ha fallado al preparar la ficha. Prueba otra vez en un rato.",
    # Repositorio de recursos de Vibe Coding Educativo
    "recurso": ("Envíame el enlace del recurso (la dirección que abre cualquiera). Si el enlace no deja ver "
                "su código, también me sirven el archivo HTML, un ZIP o el enlace a su repositorio de GitHub."),
    "leyendo_recurso": "Recibido. Abro el recurso, lo leo y preparo su ficha. Tardo un minuto.",
    "ya_esta_tuyo": "Este recurso ya está en el repositorio y es tuyo: {enlace}\nPara cambiarlo, usa /misrecursos.",
    "url_ocupada": "No cambio el enlace: ese ya está en el repositorio con otro recurso: {enlace}",
    "ya_esta_ajeno": ("Este recurso ya está en el repositorio, a nombre de {autor}: {enlace}\nSi es tuyo y lo "
                      "diste de alta con el formulario, usa /misrecursos para recuperarlo."),
    "falta_info": ("No consigo ver qué hace el recurso desde el enlace ({motivo}). Envíame el archivo HTML o un "
                   "ZIP con el código, el enlace a su repositorio de GitHub, o cuéntame en un mensaje qué hace "
                   "y cómo se usa."),
    "no_educativo": "No puedo añadirlo: el repositorio es para recursos educativos, y este no lo parece ({motivo}). Si crees que me equivoco, pulsa «Pedir una revisión» y lo mirará una persona.",
    "sin_minimo": "Todavía no lo añado: el repositorio es para recursos que ya se puedan usar en clase, y a este le falta algo ({motivo}). Cuando lo tengas listo, vuelve a mandarme el enlace. Si crees que me equivoco, pulsa «Pedir una revisión» y lo mirará una persona.",
    "b_pedir_revision": "Pedir una revisión",
    "por_que_revision": "Cuéntame en un mensaje por qué crees que debería entrar. Lo leerá la persona que lo revise.",
    "revision_pedida": "Hecho: pasa a revisión manual. Te avisaré cuando se decida.",
    "revision_ya_pedida": "Este recurso ya está en revisión manual. Te avisaré cuando se decida.",
    "rechazo_revisado_si": "Revisado a mano: «{titulo}» puede entrar en el repositorio. Sigo con el alta.",
    "rechazo_revisado_no": "Revisado a mano: «{titulo}» no entra en el repositorio. Si lo cambias, puedes volver a mandarlo con /repositorio.",
    "mudanza_no_entra": "No cambio el enlace: lo que hay en el nuevo no entra en el repositorio ({motivo}). La ficha sigue como estaba.",
    "vista_recurso": ("Esta es la ficha. Si te parece bien, la publico en el repositorio de Vibe Coding Educativo. "
                      "Si quieres cambiar algo, pulsa «Cambiar algo» y dímelo con tus palabras."),
    "que_cambio": ("Dime qué quieres cambiar, con tus palabras. Vuelvo a mirar el recurso, así que también puedo "
                   "revisar o rehacer cualquier dato. Por ejemplo: «quita Bachillerato», «el autor es Ana Pérez», "
                   "«rehaz la descripción», «revisa los idiomas» o «revisa la ficha entera»."),
    "que_cambio_mensaje": ("Dime qué quieres cambiar del mensaje, con tus palabras. Por ejemplo: «más corto» o "
                           "«di que también sirve para FP»."),
    "vista_cambio": "Así queda. Si te parece bien, pulsa «Publicar»; si no, «Cambiar algo» otra vez.",
    "publicado_recurso": ("Publicado. Lo verás el primero de la lista en el repositorio: {enlace}\n"
                          "Para cambiarlo o quitarlo más adelante, usa /misrecursos."),
    "modificado_recurso": "Hecho. En unos minutos se verá el cambio en el repositorio: {enlace}",
    "cancelado_recurso": "De acuerdo, lo dejo como estaba.",
    "caducado_recurso": "Esta ficha ya no está disponible. Envíame otra vez el enlace del recurso.",
    "cupo_recursos": "Ya has preparado {recursos} fichas de recursos hoy. Mañana podrás preparar más.",
    "error_recurso": "Algo ha fallado con el repositorio. Prueba otra vez en un rato.",
    "grande_recurso": "Este archivo pesa más de 20 MB y Telegram no deja a los bots descargarlo.",
    "archivo_sin_enlace": ("Antes de enviarme el código, envíame el enlace del recurso: la dirección que "
                           "abrirá la gente desde el repositorio."),
    "mis_recursos": "Estos son tus recursos en el repositorio. Pulsa uno para cambiarlo o quitarlo.",
    "sin_recursos": ("No tengo ningún recurso a tu nombre. Si diste de alta alguno con el formulario, "
                     "escríbeme el correo con el que lo hiciste y te mando un código para comprobar que es tuyo."),
    "otro_correo": "Escríbeme el correo con el que diste de alta tus recursos en el formulario.",
    "no_es_correo": "Eso no parece una dirección de correo. Usa /misrecursos y vuelve a escribirla, por ejemplo nombre@gmail.com.",
    "correo_sin_recursos": "Con ese correo no hay ningún recurso en el repositorio. Revisa que esté bien escrito.",
    "codigo_enviado": ("Te he enviado un código a {correo} (mira también en correo no deseado). "
                       "Escríbemelo aquí."),
    "codigo_mal": "Ese código no es correcto. Revisa el correo y escríbemelo otra vez.",
    "codigo_agotado": "Ese código ya no vale después de varios intentos fallidos. Usa /misrecursos y te mando otro.",
    "codigo_ok": "Comprobado. Desde ahora puedo gestionar los recursos de {correo}.",
    "borrar_seguro": "¿Seguro que quieres quitar «{titulo}» del repositorio? No se puede deshacer.",
    "borrado": "Quitado del repositorio. En unos minutos dejará de verse.",
    "no_tuyo": "Ese recurso no está a tu nombre, así que no puedo cambiarlo. Si es tuyo y lo diste de alta con el formulario, usa /misrecursos para recuperarlo.",
    # Botones
    "b_publicar": "Publicar",
    "b_cambiar": "Cambiar algo",
    "b_cancelar": "Cancelar",
    "b_quitar": "Quitar",
    # «Ya lo he corregido» y avisos de la revisión del repositorio (ADR 0013)
    "b_corregido": 'Ya lo he corregido',
    "b_si_la_tiene": 'Sí la tiene: revisión manual',
    "mis_recursos_avisos": 'Los que llevan ⚠️ tienen un aviso de la revisión del repositorio: pulsa uno para ver qué le falta.',
    "mis_recursos_sin_licencia": 'Los que llevan ℹ️ no tienen licencia: seguirán en el repositorio, pero te recomendamos añadirla.',
    "aviso_A": 'ℹ️ No hemos encontrado ninguna licencia, ni en la página ni en su repositorio. Como se publicó antes de que el repositorio la exigiera, seguirá en él igualmente, pero te recomendamos añadirla (por ejemplo, una línea en el pie: «Código bajo licencia AGPL v3 · contenidos bajo CC BY-SA 4.0») y pulsar «Ya lo he corregido». Cómo elegirla: https://vibe-coding-educativo.github.io/vibe-responsable/es/capitulo-9.html',
    "aviso_B": '⚠️ Aviso de la revisión del repositorio: el enlace no se abre ({motivo}). Si se ha mudado, pulsa «Cambiar algo» y escribe el enlace nuevo; si ya no existe, pulsa «Quitar». Si el {plazo} sigue sin abrirse, se eliminará del repositorio.',
    "aviso_C": '⚠️ Aviso de la revisión del repositorio: es un GPT de ChatGPT. OpenAI los retira el 11 de diciembre de 2026, y el repositorio solo admite recursos cuyo código se pueda examinar, así que ese día se eliminará del repositorio. Si lo rehaces como una aplicación con su código y una licencia abierta, puedes añadirla con /repositorio.',
    "aviso_D": '⚠️ Aviso de la revisión del repositorio: la página dice «Todos los derechos reservados». El repositorio solo admite programas de código abierto, que cualquiera pueda examinar, compartir y adaptar. Cámbialo por una licencia abierta antes del {plazo} y pulsa «Ya lo he corregido». Cómo elegirla: https://vibe-coding-educativo.github.io/vibe-responsable/es/capitulo-9.html',
    "aviso_ya_no": 'Este recurso ya no tiene ningún aviso pendiente.',
    "comprobando": 'Lo compruebo. Tardo unos segundos.',
    "aviso_plataforma": 'No puedo leer por mi cuenta las apps de Gemini, Claude o AI Studio, así que pasa a revisión manual. Si sigue faltando algo, te avisaré.',
    "aviso_no_abre": 'Sigue sin abrirse. {problema} Si se ha mudado, pulsa «Cambiar algo» en el recurso y escribe el enlace nuevo.',
    "aviso_resuelto": 'Comprobado: ya tiene licencia ({licencia}). El aviso queda resuelto y el recurso sigue en el repositorio. ¡Gracias!',
    "aviso_de_pago": 'Ya tiene licencia, pero parece de pago o freemium: {detalle}. El repositorio solo admite recursos gratuitos. Si me equivoco, pulsa otra vez «Ya lo he corregido» cuando lo hayas cambiado, o coméntalo en el grupo.',
    "aviso_sin_licencia": 'Todavía no encuentro ninguna licencia, ni en la página ni en su repositorio. Si acabas de ponerla, espera unos minutos, porque la web tarda en actualizarse, y vuelve a pulsar «Ya lo he corregido». Si ya la tiene y no la encuentro (por ejemplo, porque solo aparece al cargar la página), pulsa el botón y pasará a revisión manual.',
    "aviso_dice_que_si": 'Hecho: pasa a revisión manual. Si se encuentra la licencia, el aviso quedará resuelto y te avisaré.',
    "aviso_revisado_si": 'Revisado a mano: «{titulo}» cumple y el aviso queda resuelto. ¡Gracias!',
    "aviso_revisado_no": 'Revisado a mano: a «{titulo}» todavía le falta lo que decía el aviso. Cuando lo arregles, vuelve a pulsar «Ya lo he corregido» en /misrecursos.',
    # Para Juanjo solo (sin traducir: texto() cae en el castellano)
    "aviso_a_juanjo": 'Revisión del repositorio: tienes que comprobar «{titulo}», de {autor}.\n{url}\n\nAviso: {motivo}.\n{caso}\n\nMira si tiene una licencia abierta y si es gratuito.',
    "revisar_aviso_plataforma": 'Ha pulsado «Ya lo he corregido», pero es una app de Gemini, Claude o AI Studio y el bot no puede leerla.',
    "revisar_aviso_dice_que_si": 'Ha pulsado «Ya lo he corregido», el bot no ha encontrado la licencia y su autor dice que sí la tiene.',
    "b_cumple": 'Cumple',
    "b_no_cumple": 'No cumple',
    "revision_que_licencia": '«{titulo}»: escribe la licencia para la hoja, como «AGPL v3 (código) · CC BY-NC-SA 4.0 (contenidos)», o «-» para dejarla vacía.',
    "revision_hecha": 'Hecho: «{titulo}» queda corregido y se lo he dicho a su autor.',
    "revision_no_hecha": 'Hecho: el aviso de «{titulo}» sigue pendiente y se lo he dicho a su autor.',
    "revision_ya_no": 'Ese aviso ya no está por revisar.',
    "revision_sin_hoja": 'No he podido poner la licencia en la hoja: ponla a mano.',
    "rechazo_a_juanjo": 'Revisión del repositorio: el bot ha rechazado «{titulo}», de {autor}, y su autor pide que lo mire una persona.\n{url}\n\nMotivo del bot: {motivo}.\nLo que dice su autor: {razones}\n\nMira si es un recurso educativo que ya se puede usar en clase. «Cumple» sigue el alta (pago, licencia y ficha).',
    "nuevo_biblioteca": "Nuevo documento en la Biblioteca digital, aportado por {autor}: «{titulo}»\n{enlace}",
    "nuevo_recurso": "Nuevo recurso en el repositorio de Vibe Coding Educativo, de {autor}: «{titulo}»\n{enlace}",
    "rechazo_hecho": 'Hecho: «{titulo}» puede entrar y su autor sigue con el alta.',
    "rechazo_no_hecho": 'Hecho: «{titulo}» queda fuera y se lo he dicho a su autor.',
    "b_si_quitar": "Sí, quitarlo",
    "b_no": "No",
    "b_nuevo_recurso": "Añadir un recurso nuevo",
    "b_otro_correo": "Añadir los de otro correo",
    # Menú (setMyCommands)
    "c_buscar": "Buscar en los grupos",
    "c_biblioteca": "Añadir a la Biblioteca",
    "c_repositorio": "Añadir al repositorio",
    "c_misrecursos": "Gestionar tus recursos",
    "c_ayuda": "Qué hago y cómo",
    "valoracion_si": "¡Gracias!",
    "valoracion_no": "Gracias. Guardo la pregunta, sin nada tuyo, para mejorar.",
    "valoracion_antigua": "Gracias.",
    "respuesta_vacia": "No he encontrado nada que responda a eso. Prueba a decirlo con otras palabras o a concretar más.",
    "codigo": "Soy software libre (AGPL v3), versión {version}: el código está en https://github.com/jjdeharo/bot-chatgpt-ia-edu.",
}

CA = {
    "al_menos_uno": 'Hi ha de quedar com a mínim un grup marcat.',
    "quitado_biblioteca": 'Tret de la Biblioteca digital.',
    "b_quitar_biblioteca": "Treure'l de la Biblioteca",
    "buscando_en": 'Cercant a: {grupos}.',
    "b_mantener": 'Mantenir-lo',
    "b_quitar_grupo": "Treure'l del grup",
    "no_quitar_ya": 'Ja no el puc treure: Telegram només deixa esborrar els missatges durant 48 hores. Demana-ho a qui administra el grup.',
    "mantenido": "D'acord, es queda publicat.",
    "quitado_grupo": 'Tret del grup.',
    "pregunta_compartir": "Vols compartir-lo també a «¡Comparte tu App!» del grup Vibe Coding Educativo? Encara no es publicarà res: abans t'ensenyaré el missatge perquè el revisis, el canviïs o el cancel·lis.",
    "vista_compartir": 'Aquest és el missatge que publicaria a «¡Comparte tu App!», amb el teu nom. El pots publicar, demanar-me canvis, publicar-lo tu o cancel·lar-lo.',
    "compartido": "Publicat a «¡Comparte tu App!»: {enlace}\nSi canvies d'idea, el pots treure amb el botó de sota durant les properes 48 hores.",
    "publicalo_tu": 'Aquí tens el text perquè el publiquis tu a «¡Comparte tu App!»: https://t.me/vceduca/7674',
    "no_compartir": "D'acord, no el comparteixo.",
    "b_si": 'Sí',
    "b_lo_publico_yo": 'El publico jo',
    "b_anteriores": "Anteriors",
    "b_siguientes": "Següents",
    "seguidas": "M'has fet moltes preguntes seguides i necessito un respir. Torna'm a escriure d'aquí a una estona i continuem.",
    # Perfil del bot (setMyDescription y setMyShortDescription): aquí va la autoría.
    "perfil": "Cerco als grups ChatGPT-IA-edu, Vibe Coding Educativo i EduMedia-IAG qui va dir alguna cosa, quan i en quin missatge, i quins documents de la Biblioteca digital tracten un tema. També afegeixo documents a la Biblioteca i recursos educatius al repositori de Vibe Coding Educativo. Faig servir Claude, una IA d'Anthropic. Creat per @jjdeharo.",
    "perfil_corto": 'Cerca a ChatGPT-IA-edu, Vibe Coding Educativo i EduMedia-IAG, i afegeix documents i recursos.',
    "licencia_cerrada": "Encara no l'afegeixo: la seva llicència ({licencia}) no deixa compartir el codi. El repositori admet llicències obertes: de codi obert o Creative Commons. Si no saps quina triar, pregunta-m'ho: et recomano una segons el que vulguis permetre i t'explico com posar-la. Tens més informació a https://vibe-coding-educativo.github.io/vibe-responsable/ca/capitulo-9.html. Després envia'm una altra vegada el recurs: el fitxer HTML, un ZIP o l'enllaç al seu repositori de GitHub.",
    "de_pago": "No el puc afegir: el repositori és només per a recursos gratuïts, sense versions de pagament ni freemium, i aquest no ho sembla ({detalle}).",
    "sin_licencia": "Encara no l'afegeixo: el repositori demana que el codi estigui publicat amb una llicència oberta, i no en trobo cap ni al codi ni al seu repositori. Si no saps quina triar, pregunta-m'ho: et recomano una segons el que vulguis permetre i t'explico com posar-la. Tens més informació a https://vibe-coding-educativo.github.io/vibe-responsable/ca/capitulo-9.html. Després envia'm una altra vegada el recurs: el fitxer HTML, un ZIP o l'enllaç al seu repositori de GitHub.",
    "licencia_visible": "Un consell: la llicència ({licencia}) és al repositori, així que el recurs compleix, però qui obre la pàgina no la veu. Perquè tothom sàpiga que el pot reutilitzar, posa una línia visible al peu, com ara «Llicència {licencia}», i una altra al principi del codi: <!-- SPDX-License-Identifier: {spdx} -->. Si l'has fet amb una IA, demana-li que afegeixi aquestes dues línies. És una recomanació, no un requisit.",
    "cambio_licencia_cerrada": "No deso el canvi: la seva llicència ({licencia}) no deixa compartir el codi, i el repositori només admet llicències obertes: de codi obert o Creative Commons. Si no saps quina triar, pregunta-m'ho: et recomano una segons el que vulguis permetre i t'explico com posar-la. Tens més informació a https://vibe-coding-educativo.github.io/vibe-responsable/ca/capitulo-9.html. Quan l'hagis canviada, prem «Canviar alguna cosa» una altra vegada.",
    "cambio_sin_licencia": "No deso el canvi: el repositori demana que el codi estigui publicat amb una llicència oberta, i no en trobo cap ni al codi ni al seu repositori. Si no saps quina triar, pregunta-m'ho: et recomano una segons el que vulguis permetre i t'explico com posar-la. Tens més informació a https://vibe-coding-educativo.github.io/vibe-responsable/ca/capitulo-9.html. Quan l'hagis posada, prem «Canviar alguna cosa» una altra vegada.",
    "inicio": ("Hola. Soc el bot dels grups [ChatGPT-IA-edu](https://t.me/ChatGPTedu), "
               "[Vibe Coding Educativo](https://t.me/vceduca) i [EduMedia-IAG](https://t.me/EduMediaIAG). T'ajudo amb això:"),
    "ayuda_buscar": (
        "🔍 Cercar als grups. Pregunta'm amb les teves paraules qui va dir alguna cosa, quan, quins documents "
        "de la Biblioteca digital de ChatGPT-IA-edu o quins recursos del repositori de Vibe Coding Educativo "
        "tracten un tema, i et responc amb l'enllaç de cadascun. Cerco als tres grups alhora; si en vols només "
        "un o dos, anomena'ls. Per exemple: "
        "«qui va parlar d'avaluar amb IA el curs passat?», «hi ha guies sobre IA a infantil?», "
        "«hi ha alguna aplicació per practicar probabilitat?» o "
        "«què s'ha dit a Vibe Coding Educativo sobre publicar a GitHub Pages?»."),
    "ayuda_biblioteca": (
        "📄 Afegir un document a la Biblioteca digital de ChatGPT-IA-edu. Envia'm aquí el fitxer en PDF "
        "(fins a 20 MB) i jo m'encarrego de tot: comprovo que tracti d'IA en educació i que no sigui ja a "
        "la biblioteca, en preparo la fitxa i te l'ensenyo. Si et sembla bé, el publico amb el teu nom. Si la "
        "seva llicència no permet compartir-lo, publico només la fitxa."),
    "ayuda_recurso": (
        "📱 Afegir un recurs educatiu digital al [repositori de Vibe Coding Educativo](https://vibe-coding-educativo.github.io/app_edu/)"
        ". Envia'm l'enllaç: llegeixo el recurs, en preparo "
        "la fitxa i te l'ensenyo; si et sembla bé, la publico. Ha de ser gratuït i tenir el codi publicat "
        "amb una llicència oberta. Amb /misrecursos pots canviar o treure els teus quan vulguis."),
    "ayuda_menu": "Totes les opcions són al menú: el botó «Menú», a l'esquerra d'on escrius.",
    "ayuda_final": (
        "Com funciono: soc un programa que fa servir Claude, una IA d'Anthropic. El que m'escrius, els "
        "missatges dels grups que trobo i el que m'envies es processen en servidors d'Anthropic, als "
        "Estats Units. Només guardo les preguntes que no aconsegueixo respondre o que marques amb 👎, sense el teu nom ni el teu compte, per millorar el bot, i les esborro al cap de 60 dies. Em puc equivocar: comprova sempre el missatge "
        "enllaçat. Et parlo en l'idioma en què m'escrius."),
    "traduccion": "Textos traduïts automàticament amb IA, sense revisió professional.",
    "buscar": "Escriu-me el que cerques, amb les teves paraules. Cerco als grups marcats; toca'n un per marcar-lo o desmarcar-lo. Ho mantindré mentre continuem parlant.",
    "biblioteca": "Envia'm el document en PDF (fins a 20 MB) i en preparo la fitxa.",
    "solo_chatgpt": "Afegir documents a la Biblioteca digital és cosa dels membres de ChatGPT-IA-edu. Entrar-hi és lliure: uneix-te al grup i torna-me'l a enviar. Aquest és el grup: https://t.me/ChatGPTedu",
    "solo_vce": ("El repositori de recursos és de la comunitat Vibe Coding Educativo; per afegir-hi els teus, "
                 "uneix-te al grup: https://t.me/vceduca"),
    "no_miembro": "Ho sento, només puc respondre a qui forma part dels grups ChatGPT-IA-edu (https://t.me/ChatGPTedu), Vibe Coding Educativo (https://t.me/vceduca) o EduMedia-IAG (https://t.me/EduMediaIAG). Entrar-hi és lliure: uneix-te a qualsevol d'ells i torna'm a escriure.",
    "no_autorizado": "Encara estic en proves. Aviat estaré obert als grups.",
    "cupo": "Has arribat a les {cupo} preguntes d'avui. Demà podràs continuar.",
    "tope": "Aquest mes s'ha esgotat el pressupost del bot. Tornarà a funcionar el dia 1.",
    "error": "Alguna cosa ha fallat en cercar. Torna-ho a provar d'aquí a un moment.",
    "solo_texto": "De moment només entenc missatges escrits i captures de pantalla. Escriu-me la pregunta, si us plau.",
    "solo_privado": "Hola, {nombre}. Soc el Bot de IA Educativa. Al grup no et puc respondre, però en privat sí. Escriu-me aquí: https://t.me/{usuario}",
    "solo_privado_comando": "Hola, {nombre}. Soc el Bot de IA Educativa. Això no funciona al grup, però en privat sí. Obre-ho aquí: https://t.me/{usuario}?start={comando}",
    "no_pdf": "Per afegir un document a la Biblioteca digital, envia-me'l en PDF.",
    "grande": ("Aquest fitxer pesa {mb:.0f} MB i Telegram només deixa als bots baixar fitxers de fins a "
               "20 MB, així que no el puc llegir. El pots pujar tu directament a la Biblioteca digital "
               "(https://t.me/ChatGPTedu/21753) i preparar-ne la fitxa amb https://chatgpt-ia-edu.github.io/resumen/"),
    "cupo_docs": "Avui ja m'has enviat {docs} documents. Demà en podràs enviar més.",
    "leyendo": "Rebut. El llegeixo, comprovo si encaixa a la biblioteca i en preparo la fitxa. Trigo un minut.",
    "sin_texto": ("No puc llegir el text d'aquest PDF: sembla escanejat com a imatge. El pots pujar tu "
                  "directament a la Biblioteca digital (https://t.me/ChatGPTedu/21753) i preparar-ne la "
                  "fitxa amb https://chatgpt-ia-edu.github.io/resumen/"),
    "ajeno": "No el puc afegir: la Biblioteca digital és per a documents sobre intel·ligència artificial en educació, i aquest tracta d'una altra cosa ({tema}).",
    "repetido": "Aquest document ja és a la Biblioteca digital: {enlace}",
    "vista": ("Aquesta és la fitxa, en castellà com tota la biblioteca. Si et sembla bé, publicaré a la "
              "Biblioteca digital el document amb «Aportado por {autor}» i la fitxa en resposta."),
    "vista_sin_archivo": ("Aquesta és la fitxa, en castellà com tota la biblioteca. La seva llicència no permet "
                          "compartir el fitxer, així que publicaré a la Biblioteca digital només la fitxa, amb "
                          "«Aportado por {autor}»."),
    "publicado": "Publicat a la Biblioteca digital: {enlace}\nSi canvies d'idea, el pots treure amb el botó de sota durant les properes 48 hores.",
    "cancelado": "D'acord, no el publico.",
    "caducado": "Aquesta fitxa ja no està disponible. Si vols publicar-lo, envia'm una altra vegada el document.",
    "sustituido": "Aquesta vista prèvia ja no és l'última: n'he preparat una altra després. Fes servir els botons de l'últim missatge.",
    "error_doc": "Alguna cosa ha fallat en preparar la fitxa. Torna-ho a provar d'aquí a una estona.",
    "recurso": ("Envia'm l'enllaç del recurs (l'adreça que obre qualsevol persona). Si l'enllaç no deixa veure "
                "el codi, també em serveixen el fitxer HTML, un ZIP o l'enllaç al seu repositori de GitHub."),
    "leyendo_recurso": "Rebut. Obro el recurs, el llegeixo i en preparo la fitxa. Trigo un minut.",
    "ya_esta_tuyo": "Aquest recurs ja és al repositori i és teu: {enlace}\nPer canviar-lo, fes servir /misrecursos.",
    "url_ocupada": "No canvio l'enllaç: aquest ja és al repositori amb un altre recurs: {enlace}",
    "ya_esta_ajeno": ("Aquest recurs ja és al repositori, a nom de {autor}: {enlace}\nSi és teu i el vas donar "
                      "d'alta amb el formulari, fes servir /misrecursos per recuperar-lo."),
    "falta_info": ("No aconsegueixo veure què fa el recurs des de l'enllaç ({motivo}). Envia'm el fitxer HTML o "
                   "un ZIP amb el codi, l'enllaç al seu repositori de GitHub, o explica'm en un missatge què fa "
                   "i com es fa servir."),
    "no_educativo": "No el puc afegir: el repositori és per a recursos educatius, i aquest no ho sembla ({motivo}). Si creus que m'equivoco, prem «Demanar una revisió» i el mirarà una persona.",
    "sin_minimo": "Encara no l'afegeixo: el repositori és per a recursos que ja es puguin fer servir a classe, i a aquest li falta alguna cosa ({motivo}). Quan el tinguis a punt, torna a enviar-me l'enllaç. Si creus que m'equivoco, prem «Demanar una revisió» i el mirarà una persona.",
    "b_pedir_revision": "Demanar una revisió",
    "por_que_revision": "Explica'm en un missatge per què creus que hauria d'entrar. Ho llegirà la persona que el revisi.",
    "revision_pedida": "Fet: passa a revisió manual. T'avisaré quan es decideixi.",
    "revision_ya_pedida": "Aquest recurs ja és en revisió manual. T'avisaré quan es decideixi.",
    "rechazo_revisado_si": "Revisat a mà: «{titulo}» pot entrar al repositori. Continuo amb l'alta.",
    "rechazo_revisado_no": "Revisat a mà: «{titulo}» no entra al repositori. Si el canvies, pots tornar a enviar-lo amb /repositorio.",
    "mudanza_no_entra": "No canvio l'enllaç: el que hi ha al nou no entra al repositori ({motivo}). La fitxa continua com estava.",
    "vista_recurso": ("Aquesta és la fitxa, en castellà com tot el repositori. Si et sembla bé, la publico al "
                      "repositori de Vibe Coding Educativo. Si vols canviar alguna cosa, prem «Canviar alguna "
                      "cosa» i digues-m'ho amb les teves paraules."),
    "que_cambio": ("Digues-me què vols canviar, amb les teves paraules. Torno a mirar el recurs, així que també "
                   "puc revisar o refer qualsevol dada. Per exemple: «treu Batxillerat», «l'autora és Anna Puig», "
                   "«refés la descripció», «revisa els idiomes» o «revisa tota la fitxa»."),
    "que_cambio_mensaje": ("Digues-me què vols canviar del missatge, amb les teves paraules. Per exemple: "
                           "«més curt» o «digues que també serveix per a FP»."),
    "vista_cambio": "Queda així. Si et sembla bé, prem «Publicar»; si no, «Canviar alguna cosa» una altra vegada.",
    "publicado_recurso": ("Publicat. El veuràs el primer de la llista al repositori: {enlace}\n"
                          "Per canviar-lo o treure'l més endavant, fes servir /misrecursos."),
    "modificado_recurso": "Fet. D'aquí a uns minuts es veurà el canvi al repositori: {enlace}",
    "cancelado_recurso": "D'acord, ho deixo com estava.",
    "caducado_recurso": "Aquesta fitxa ja no està disponible. Envia'm una altra vegada l'enllaç del recurs.",
    "cupo_recursos": "Avui ja has preparat {recursos} fitxes de recursos. Demà en podràs preparar més.",
    "error_recurso": "Alguna cosa ha fallat amb el repositori. Torna-ho a provar d'aquí a una estona.",
    "grande_recurso": "Aquest fitxer pesa més de 20 MB i Telegram no deixa als bots baixar-lo.",
    "archivo_sin_enlace": ("Abans d'enviar-me el codi, envia'm l'enllaç del recurs: l'adreça que obrirà la "
                           "gent des del repositori."),
    "mis_recursos": "Aquests són els teus recursos al repositori. Prem-ne un per canviar-lo o treure'l.",
    "sin_recursos": ("No tinc cap recurs a nom teu. Si en vas donar d'alta algun amb el formulari, "
                     "escriu-me el correu amb què ho vas fer i t'envio un codi per comprovar que és teu."),
    "otro_correo": "Escriu-me el correu amb què vas donar d'alta els teus recursos al formulari.",
    "no_es_correo": "Això no sembla una adreça de correu. Fes servir /misrecursos i torna-la a escriure, per exemple nom@gmail.com.",
    "correo_sin_recursos": "Amb aquest correu no hi ha cap recurs al repositori. Revisa que estigui ben escrit.",
    "codigo_enviado": ("T'he enviat un codi a {correo} (mira també al correu brossa). "
                       "Escriu-me'l aquí."),
    "codigo_mal": "Aquest codi no és correcte. Revisa el correu i torna-me'l a escriure.",
    "codigo_agotado": "Aquest codi ja no és vàlid després de diversos intents fallits. Fes servir /misrecursos i te n'envio un altre.",
    "codigo_ok": "Comprovat. A partir d'ara puc gestionar els recursos de {correo}.",
    "borrar_seguro": "Segur que vols treure «{titulo}» del repositori? No es pot desfer.",
    "borrado": "Tret del repositori. D'aquí a uns minuts deixarà de veure's.",
    "no_tuyo": "Aquest recurs no és a nom teu, així que no el puc canviar. Si és teu i el vas donar d'alta amb el formulari, fes servir /misrecursos per recuperar-lo.",
    "b_publicar": "Publicar",
    "b_cambiar": "Canviar alguna cosa",
    "b_cancelar": "Cancel·lar",
    "b_quitar": "Treure",
    # «Ya lo he corregido» y avisos de la revisión del repositorio (ADR 0013)
    "b_corregido": 'Ja ho he corregit',
    "b_si_la_tiene": 'Sí que en té: revisió manual',
    "mis_recursos_avisos": 'Els que porten ⚠️ tenen un avís de la revisió del repositori: prem-ne un per veure què li falta.',
    "mis_recursos_sin_licencia": 'Els que porten ℹ️ no tenen llicència: continuaran al repositori, però et recomanem afegir-la.',
    "aviso_A": "ℹ️ No hem trobat cap llicència, ni a la pàgina ni al seu repositori. Com que es va publicar abans que el repositori l'exigís, hi continuarà igualment, però et recomanem afegir-la (per exemple, una línia al peu: «Codi sota llicència AGPL v3 · continguts sota CC BY-SA 4.0») i prémer «Ja ho he corregit». Com triar-la: https://vibe-coding-educativo.github.io/vibe-responsable/ca/capitulo-9.html",
    "aviso_B": "⚠️ Avís de la revisió del repositori: l'enllaç no s'obre ({motivo}). Si s'ha traslladat, prem «Canviar alguna cosa» i escriu l'enllaç nou; si ja no existeix, prem «Treure». Si el {plazo} continua sense obrir-se, s'eliminarà del repositori.",
    "aviso_C": "⚠️ Avís de la revisió del repositori: és un GPT de ChatGPT. OpenAI els retira l'11 de desembre de 2026, i el repositori només admet recursos el codi dels quals es pugui examinar, així que aquell dia s'eliminarà del repositori. Si el refàs com una aplicació amb el seu codi i una llicència oberta, la pots afegir amb /repositorio.",
    "aviso_D": '⚠️ Avís de la revisió del repositori: la pàgina diu «Tots els drets reservats». El repositori només admet programes de codi obert, que qualsevol pugui examinar, compartir i adaptar. Canvia-ho per una llicència oberta abans del {plazo} i prem «Ja ho he corregit». Com triar-la: https://vibe-coding-educativo.github.io/vibe-responsable/ca/capitulo-9.html',
    "aviso_ya_no": 'Aquest recurs ja no té cap avís pendent.',
    "comprobando": 'Ho comprovo. Trigo uns segons.',
    "aviso_plataforma": "No puc llegir pel meu compte les aplicacions de Gemini, Claude o AI Studio, així que passa a revisió manual. Si encara falta alguna cosa, t'avisaré.",
    "aviso_no_abre": "Continua sense obrir-se. {problema} Si s'ha traslladat, prem «Canviar alguna cosa» al recurs i escriu l'enllaç nou.",
    "aviso_resuelto": "Comprovat: ja té llicència ({licencia}). L'avís queda resolt i el recurs continua al repositori. Gràcies!",
    "aviso_de_pago": "Ja té llicència, però sembla de pagament o freemium: {detalle}. El repositori només admet recursos gratuïts. Si m'equivoco, prem un altre cop «Ja ho he corregit» quan ho hagis canviat, o comenta-ho al grup.",
    "aviso_sin_licencia": "Encara no trobo cap llicència, ni a la pàgina ni al seu repositori. Si l'acabes de posar, espera uns minuts, perquè la web triga a actualitzar-se, i torna a prémer «Ja ho he corregit». Si ja en té i no la trobo (per exemple, perquè només apareix en carregar la pàgina), prem el botó i passarà a revisió manual.",
    "aviso_dice_que_si": "Fet: passa a revisió manual. Si es troba la llicència, l'avís quedarà resolt i t'avisaré.",
    "aviso_revisado_si": "Revisat a mà: «{titulo}» compleix i l'avís queda resolt. Gràcies!",
    "aviso_revisado_no": "Revisat a mà: a «{titulo}» encara li falta el que deia l'avís. Quan ho arreglis, torna a prémer «Ja ho he corregit» a /misrecursos.",
    "b_si_quitar": "Sí, treure'l",
    "b_no": "No",
    "b_nuevo_recurso": "Afegir un recurs nou",
    "b_otro_correo": "Afegir els d'un altre correu",
    "c_buscar": "Cercar als grups",
    "c_biblioteca": "Afegir a la Biblioteca",
    "c_repositorio": "Afegir al repositori",
    "c_misrecursos": "Els teus recursos",
    "c_ayuda": "Què faig i com",
    "valoracion_si": "Gràcies!",
    "valoracion_no": "Gràcies. Guardo la pregunta, sense res teu, per millorar.",
    "valoracion_antigua": "Gràcies.",
    "respuesta_vacia": "No he trobat res que respongui a això. Prova a dir-ho amb altres paraules o a concretar més.",
    "codigo": "Soc programari lliure (AGPL v3), versió {version}: el codi és a https://github.com/jjdeharo/bot-chatgpt-ia-edu.",
}

GL = {
    "al_menos_uno": 'Ten que quedar polo menos un grupo marcado.',
    "quitado_biblioteca": 'Quitado da Biblioteca dixital.',
    "b_quitar_biblioteca": 'Quitalo da Biblioteca',
    "buscando_en": 'Buscando en: {grupos}.',
    "b_mantener": 'Mantelo',
    "b_quitar_grupo": 'Quitalo do grupo',
    "no_quitar_ya": 'Xa non podo quitalo: Telegram só deixa borrar as mensaxes durante 48 horas. Pídello a quen administra o grupo.',
    "mantenido": 'De acordo, queda publicado.',
    "quitado_grupo": 'Quitado do grupo.',
    "pregunta_compartir": 'Queres compartilo tamén en «¡Comparte tu App!» do grupo Vibe Coding Educativo? Aínda non se publicará nada: antes ensinareiche a mensaxe para que a revises, a cambies ou a canceles.',
    "vista_compartir": 'Esta é a mensaxe que publicaría en «¡Comparte tu App!», co teu nome. Podes publicala, pedirme cambios, publicala ti ou cancelala.',
    "compartido": 'Publicado en «¡Comparte tu App!»: {enlace}\nSe cambias de idea, podes quitalo co botón de abaixo durante as próximas 48 horas.',
    "publicalo_tu": 'Aquí tes o texto para que o publiques ti en «¡Comparte tu App!»: https://t.me/vceduca/7674',
    "no_compartir": 'De acordo, non o comparto.',
    "b_si": 'Si',
    "b_lo_publico_yo": 'Publícoo eu',
    "b_anteriores": "Anteriores",
    "b_siguientes": "Seguintes",
    "seguidas": "Fixéchesme moitas preguntas seguidas e necesito un respiro. Volve escribirme dentro dun anaco e seguimos.",
    # Perfil del bot (setMyDescription y setMyShortDescription): aquí va la autoría.
    "perfil": 'Busco nos grupos ChatGPT-IA-edu, Vibe Coding Educativo e EduMedia-IAG quen dixo algo, cando e en que mensaxe, e que documentos da Biblioteca dixital tratan un tema. Tamén engado documentos á Biblioteca e recursos educativos ao repositorio de Vibe Coding Educativo. Uso Claude, unha IA de Anthropic. Creado por @jjdeharo.',
    "perfil_corto": 'Busca en ChatGPT-IA-edu, Vibe Coding Educativo e EduMedia-IAG, e engade documentos e recursos.',
    "licencia_cerrada": 'Aínda non o engado: a súa licenza ({licencia}) non deixa compartir o código. O repositorio admite licenzas abertas: de código aberto ou Creative Commons. Se non sabes cal escoller, pregúntamo: recoméndoche unha segundo o que queiras permitir e explícoche como poñela. Tes máis información en https://vibe-coding-educativo.github.io/vibe-responsable/gl/capitulo-9.html. Despois envíame outra vez o recurso: o ficheiro HTML, un ZIP ou a ligazón ao seu repositorio de GitHub.',
    "de_pago": "Non podo engadilo: o repositorio é só para recursos gratuítos, sen versións de pagamento nin freemium, e este non o parece ({detalle}).",
    "sin_licencia": 'Aínda non o engado: o repositorio pide que o código estea publicado cunha licenza aberta, e non atopo ningunha nin no código nin no seu repositorio. Se non sabes cal escoller, pregúntamo: recoméndoche unha segundo o que queiras permitir e explícoche como poñela. Tes máis información en https://vibe-coding-educativo.github.io/vibe-responsable/gl/capitulo-9.html. Despois envíame outra vez o recurso: o ficheiro HTML, un ZIP ou a ligazón ao seu repositorio de GitHub.',
    "licencia_visible": "Un consello: a licenza ({licencia}) está no repositorio, así que o recurso cumpre, pero quen abre a páxina non a ve. Para que calquera saiba que pode reutilizalo, pon unha liña visible no pé, como «Licenza {licencia}», e outra ao principio do código: <!-- SPDX-License-Identifier: {spdx} -->. Se o fixeches cunha IA, pídelle que engada esas dúas liñas. É unha recomendación, non un requisito.",
    "cambio_licencia_cerrada": 'Non gardo o cambio: a súa licenza ({licencia}) non deixa compartir o código, e o repositorio só admite licenzas abertas: de código aberto ou Creative Commons. Se non sabes cal escoller, pregúntamo: recoméndoche unha segundo o que queiras permitir e explícoche como poñela. Tes máis información en https://vibe-coding-educativo.github.io/vibe-responsable/gl/capitulo-9.html. Cando a cambies, preme «Cambiar algo» outra vez.',
    "cambio_sin_licencia": 'Non gardo o cambio: o repositorio pide que o código estea publicado cunha licenza aberta, e non atopo ningunha nin no código nin no seu repositorio. Se non sabes cal escoller, pregúntamo: recoméndoche unha segundo o que queiras permitir e explícoche como poñela. Tes máis información en https://vibe-coding-educativo.github.io/vibe-responsable/gl/capitulo-9.html. Cando a poñas, preme «Cambiar algo» outra vez.',
    "inicio": ("Ola. Son o bot dos grupos [ChatGPT-IA-edu](https://t.me/ChatGPTedu), "
               "[Vibe Coding Educativo](https://t.me/vceduca) e [EduMedia-IAG](https://t.me/EduMediaIAG). Axúdoche con isto:"),
    "ayuda_buscar": (
        "🔍 Buscar nos grupos. Pregúntame coas túas palabras quen dixo algo, cando, que documentos "
        "da Biblioteca dixital de ChatGPT-IA-edu ou que recursos do repositorio de Vibe Coding Educativo "
        "tratan un tema, e respóndoche coa ligazón de cada un. Busco nos tres grupos á vez; se queres só un "
        "ou dous, nómeaos. Por exemplo: "
        "«quen falou de avaliar con IA o curso pasado?», «hai guías sobre IA en infantil?», "
        "«hai algunha aplicación para practicar probabilidade?» ou "
        "«que se dixo en Vibe Coding Educativo sobre publicar en GitHub Pages?»."),
    "ayuda_biblioteca": (
        "📄 Engadir un documento á Biblioteca dixital de ChatGPT-IA-edu. Envíame aquí o ficheiro en PDF "
        "(ata 20 MB) e eu encárgome de todo: comprobo que trate de IA en educación e que non estea xa na "
        "biblioteca, preparo a súa ficha e ensínocha. Se che parece ben, publícoo co teu nome. Se a súa "
        "licenza non permite compartilo, publico só a ficha."),
    "ayuda_recurso": (
        "📱 Engadir un recurso educativo dixital ao [repositorio de Vibe Coding Educativo](https://vibe-coding-educativo.github.io/app_edu/)"
        ". Envíame a súa ligazón: leo o recurso, preparo a "
        "súa ficha e ensínocha; se che parece ben, publícoa. Ten que ser gratuíto e ter o código "
        "publicado cunha licenza aberta. Con /misrecursos podes cambiar ou quitar os teus cando queiras."),
    "ayuda_menu": 'Todas as opcións están no menú: o botón «Menú», á esquerda de onde escribes.',
    "ayuda_final": (
        "Como funciono: son un programa que usa Claude, unha IA de Anthropic. O que me escribes, as "
        "mensaxes dos grupos que atopo e o que me envías procésanse en servidores de Anthropic, nos "
        "Estados Unidos. Só gardo as preguntas que non consigo responder ou que marcas con 👎, sen o teu nome nin a túa conta, para mellorar o bot, e bórroas aos 60 días. Podo equivocarme: comproba sempre a mensaxe "
        "ligada. Fálote no idioma no que me escribes."),
    "traduccion": "Textos traducidos automaticamente con IA, sen revisión profesional.",
    "buscar": 'Escríbeme o que buscas, coas túas palabras. Busco nos grupos marcados; toca un para marcalo ou desmarcalo. Mantereino mentres sigamos falando.',
    "biblioteca": "Envíame o documento en PDF (ata 20 MB) e preparo a súa ficha.",
    "solo_chatgpt": "Engadir documentos á Biblioteca dixital é cousa dos membros de ChatGPT-IA-edu. Entrar é libre: únete ao grupo e volve envialo. Este é o grupo: https://t.me/ChatGPTedu",
    "solo_vce": ("O repositorio de recursos é da comunidade Vibe Coding Educativo; para engadir os teus, "
                 "únete ao grupo: https://t.me/vceduca"),
    "no_miembro": "Síntoo, só podo responder a quen forma parte dos grupos ChatGPT-IA-edu (https://t.me/ChatGPTedu), Vibe Coding Educativo (https://t.me/vceduca) ou EduMedia-IAG (https://t.me/EduMediaIAG). Entrar é libre: únete a calquera deles e volve escribirme.",
    "no_autorizado": "Aínda estou en probas. Pronto estarei aberto aos grupos.",
    "cupo": "Chegaches ás {cupo} preguntas de hoxe. Mañá poderás seguir.",
    "tope": "Este mes esgotouse o orzamento do bot. Volverá funcionar o día 1.",
    "error": "Algo fallou ao buscar. Proba outra vez nun momento.",
    "solo_texto": "Polo de agora só entendo mensaxes escritas e capturas de pantalla. Escríbeme a pregunta, por favor.",
    "solo_privado": "Ola, {nombre}. Son o Bot de IA Educativa. No grupo non podo contestarche, pero en privado si. Escríbeme aquí: https://t.me/{usuario}",
    "solo_privado_comando": "Ola, {nombre}. Son o Bot de IA Educativa. Isto non funciona no grupo, pero en privado si. Ábreo aquí: https://t.me/{usuario}?start={comando}",
    "no_pdf": "Para engadir un documento á Biblioteca dixital, envíamo en PDF.",
    "grande": ("Este ficheiro pesa {mb:.0f} MB e Telegram só deixa aos bots descargar ficheiros de ata "
               "20 MB, así que non podo lelo. Podes subilo ti directamente á Biblioteca dixital "
               "(https://t.me/ChatGPTedu/21753) e preparar a súa ficha con https://chatgpt-ia-edu.github.io/resumen/"),
    "cupo_docs": "Hoxe xa me enviaches {docs} documentos. Mañá poderás enviar máis.",
    "leyendo": "Recibido. Léoo, comprobo se encaixa na biblioteca e preparo a ficha. Tardo un minuto.",
    "sin_texto": ("Non podo ler o texto deste PDF: parece escaneado como imaxe. Podes subilo ti "
                  "directamente á Biblioteca dixital (https://t.me/ChatGPTedu/21753) e preparar a súa "
                  "ficha con https://chatgpt-ia-edu.github.io/resumen/"),
    "ajeno": "Non podo engadilo: a Biblioteca dixital é para documentos sobre intelixencia artificial en educación, e este trata doutra cousa ({tema}).",
    "repetido": "Este documento xa está na Biblioteca dixital: {enlace}",
    "vista": ("Esta é a ficha, en castelán como toda a biblioteca. Se che parece ben, publicarei na "
              "Biblioteca dixital o documento con «Aportado por {autor}» e a ficha en resposta."),
    "vista_sin_archivo": ("Esta é a ficha, en castelán como toda a biblioteca. A súa licenza non permite "
                          "compartir o ficheiro, así que publicarei na Biblioteca dixital só a ficha, con "
                          "«Aportado por {autor}»."),
    "publicado": 'Publicado na Biblioteca dixital: {enlace}\nSe cambias de idea, podes quitalo co botón de abaixo durante as próximas 48 horas.',
    "cancelado": "De acordo, non o publico.",
    "caducado": "Esta ficha xa non está dispoñible. Se queres publicalo, envíame outra vez o documento.",
    "sustituido": "Esa vista previa xa non é a última: preparei outra despois. Usa os botóns da última mensaxe.",
    "error_doc": "Algo fallou ao preparar a ficha. Proba outra vez nun anaco.",
    "recurso": ("Envíame a ligazón do recurso (o enderezo que abre calquera). Se a ligazón non deixa ver "
                "o seu código, tamén me serven o ficheiro HTML, un ZIP ou a ligazón ao seu repositorio de GitHub."),
    "leyendo_recurso": "Recibido. Abro o recurso, léoo e preparo a súa ficha. Tardo un minuto.",
    "ya_esta_tuyo": "Este recurso xa está no repositorio e é teu: {enlace}\nPara cambialo, usa /misrecursos.",
    "url_ocupada": "Non cambio a ligazón: esa xa está no repositorio con outro recurso: {enlace}",
    "ya_esta_ajeno": ("Este recurso xa está no repositorio, a nome de {autor}: {enlace}\nSe é teu e o deches de "
                      "alta co formulario, usa /misrecursos para recuperalo."),
    "falta_info": ("Non consigo ver que fai o recurso desde a ligazón ({motivo}). Envíame o ficheiro HTML ou un "
                   "ZIP co código, a ligazón ao seu repositorio de GitHub, ou cóntame nunha mensaxe que fai "
                   "e como se usa."),
    "no_educativo": "Non podo engadilo: o repositorio é para recursos educativos, e este non o parece ({motivo}). Se cres que me equivoco, preme «Pedir unha revisión» e mirarao unha persoa.",
    "sin_minimo": "Aínda non o engado: o repositorio é para recursos que xa se poidan usar na aula, e a este fáltalle algo ({motivo}). Cando o teñas listo, volve mandarme a ligazón. Se cres que me equivoco, preme «Pedir unha revisión» e mirarao unha persoa.",
    "b_pedir_revision": "Pedir unha revisión",
    "por_que_revision": "Cóntame nunha mensaxe por que cres que debería entrar. Lerao a persoa que o revise.",
    "revision_pedida": "Feito: pasa a revisión manual. Avisareite cando se decida.",
    "revision_ya_pedida": "Este recurso xa está en revisión manual. Avisareite cando se decida.",
    "rechazo_revisado_si": "Revisado a man: «{titulo}» pode entrar no repositorio. Sigo coa alta.",
    "rechazo_revisado_no": "Revisado a man: «{titulo}» non entra no repositorio. Se o cambias, podes volver mandalo con /repositorio.",
    "mudanza_no_entra": "Non cambio a ligazón: o que hai na nova non entra no repositorio ({motivo}). A ficha segue como estaba.",
    "vista_recurso": ("Esta é a ficha, en castelán como todo o repositorio. Se che parece ben, publícoa no "
                      "repositorio de Vibe Coding Educativo. Se queres cambiar algo, preme «Cambiar algo» e "
                      "dímo coas túas palabras."),
    "que_cambio": ("Dime que queres cambiar, coas túas palabras. Volvo mirar o recurso, así que tamén podo "
                   "revisar ou refacer calquera dato. Por exemplo: «quita Bacharelato», «a autora é Ana Pérez», "
                   "«refai a descrición», «revisa os idiomas» ou «revisa a ficha enteira»."),
    "que_cambio_mensaje": ("Dime que queres cambiar da mensaxe, coas túas palabras. Por exemplo: «máis curta» "
                           "ou «di que tamén serve para FP»."),
    "vista_cambio": "Así queda. Se che parece ben, preme «Publicar»; se non, «Cambiar algo» outra vez.",
    "publicado_recurso": ("Publicado. Verálo o primeiro da lista no repositorio: {enlace}\n"
                          "Para cambialo ou quitalo máis adiante, usa /misrecursos."),
    "modificado_recurso": "Feito. Nuns minutos verase o cambio no repositorio: {enlace}",
    "cancelado_recurso": "De acordo, déixoo como estaba.",
    "caducado_recurso": "Esta ficha xa non está dispoñible. Envíame outra vez a ligazón do recurso.",
    "cupo_recursos": "Hoxe xa preparaches {recursos} fichas de recursos. Mañá poderás preparar máis.",
    "error_recurso": "Algo fallou co repositorio. Proba outra vez nun anaco.",
    "grande_recurso": "Este ficheiro pesa máis de 20 MB e Telegram non deixa aos bots descargalo.",
    "archivo_sin_enlace": ("Antes de enviarme o código, envíame a ligazón do recurso: o enderezo que abrirá "
                           "a xente desde o repositorio."),
    "mis_recursos": "Estes son os teus recursos no repositorio. Preme un para cambialo ou quitalo.",
    "sin_recursos": ("Non teño ningún recurso ao teu nome. Se deches de alta algún co formulario, "
                     "escríbeme o correo co que o fixeches e mándoche un código para comprobar que é teu."),
    "otro_correo": "Escríbeme o correo co que deches de alta os teus recursos no formulario.",
    "no_es_correo": "Iso non parece un enderezo de correo. Usa /misrecursos e volve escribilo, por exemplo nome@gmail.com.",
    "correo_sin_recursos": "Con ese correo non hai ningún recurso no repositorio. Revisa que estea ben escrito.",
    "codigo_enviado": ("Envieiche un código a {correo} (mira tamén no correo lixo). "
                       "Escríbemo aquí."),
    "codigo_mal": "Ese código non é correcto. Revisa o correo e escríbemo outra vez.",
    "codigo_agotado": "Ese código xa non vale despois de varios intentos fallidos. Usa /misrecursos e mándoche outro.",
    "codigo_ok": "Comprobado. Desde agora podo xestionar os recursos de {correo}.",
    "borrar_seguro": "Seguro que queres quitar «{titulo}» do repositorio? Non se pode desfacer.",
    "borrado": "Quitado do repositorio. Nuns minutos deixará de verse.",
    "no_tuyo": "Ese recurso non está ao teu nome, así que non podo cambialo. Se é teu e o deches de alta co formulario, usa /misrecursos para recuperalo.",
    "b_publicar": "Publicar",
    "b_cambiar": "Cambiar algo",
    "b_cancelar": "Cancelar",
    "b_quitar": "Quitar",
    # «Ya lo he corregido» y avisos de la revisión del repositorio (ADR 0013)
    "b_corregido": 'Xa o corrixín',
    "b_si_la_tiene": 'Si que a ten: revisión manual',
    "mis_recursos_avisos": 'Os que levan ⚠️ teñen un aviso da revisión do repositorio: preme un para ver que lle falta.',
    "mis_recursos_sin_licencia": 'Os que levan ℹ️ non teñen licenza: seguirán no repositorio, pero recomendámosche engadila.',
    "aviso_A": 'ℹ️ Non atopamos ningunha licenza, nin na páxina nin no seu repositorio. Como se publicou antes de que o repositorio a esixise, seguirá nel igualmente, pero recomendámosche engadila (por exemplo, unha liña no pé: «Código baixo licenza AGPL v3 · contidos baixo CC BY-SA 4.0») e premer «Xa o corrixín». Como escollela: https://vibe-coding-educativo.github.io/vibe-responsable/gl/capitulo-9.html',
    "aviso_B": '⚠️ Aviso da revisión do repositorio: a ligazón non se abre ({motivo}). Se se mudou, preme «Cambiar algo» e escribe a ligazón nova; se xa non existe, preme «Quitar». Se o {plazo} segue sen abrirse, eliminarase do repositorio.',
    "aviso_C": '⚠️ Aviso da revisión do repositorio: é un GPT de ChatGPT. OpenAI retíraos o 11 de decembro de 2026, e o repositorio só admite recursos cuxo código se poida examinar, así que ese día eliminarase do repositorio. Se o refás como unha aplicación co seu código e unha licenza aberta, podes engadila con /repositorio.',
    "aviso_D": '⚠️ Aviso da revisión do repositorio: a páxina di «Todos os dereitos reservados». O repositorio só admite programas de código aberto, que calquera poida examinar, compartir e adaptar. Cámbiao por unha licenza aberta antes do {plazo} e preme «Xa o corrixín». Como escollela: https://vibe-coding-educativo.github.io/vibe-responsable/gl/capitulo-9.html',
    "aviso_ya_no": 'Este recurso xa non ten ningún aviso pendente.',
    "comprobando": 'Compróboo. Tardo uns segundos.',
    "aviso_plataforma": 'Non podo ler pola miña conta as aplicacións de Gemini, Claude ou AI Studio, así que pasa a revisión manual. Se segue faltando algo, avisareite.',
    "aviso_no_abre": 'Segue sen abrirse. {problema} Se se mudou, preme «Cambiar algo» no recurso e escribe a ligazón nova.',
    "aviso_resuelto": 'Comprobado: xa ten licenza ({licencia}). O aviso queda resolto e o recurso segue no repositorio. Grazas!',
    "aviso_de_pago": 'Xa ten licenza, pero parece de pagamento ou freemium: {detalle}. O repositorio só admite recursos gratuítos. Se me equivoco, preme outra vez «Xa o corrixín» cando o cambiases, ou coméntao no grupo.',
    "aviso_sin_licencia": 'Aínda non atopo ningunha licenza, nin na páxina nin no seu repositorio. Se acabas de poñela, agarda uns minutos, porque a web tarda en actualizarse, e volve premer «Xa o corrixín». Se xa a ten e non a atopo (por exemplo, porque só aparece ao cargar a páxina), preme o botón e pasará a revisión manual.',
    "aviso_dice_que_si": 'Feito: pasa a revisión manual. Se se atopa a licenza, o aviso quedará resolto e avisareite.',
    "aviso_revisado_si": 'Revisado a man: «{titulo}» cumpre e o aviso queda resolto. Grazas!',
    "aviso_revisado_no": 'Revisado a man: a «{titulo}» aínda lle falta o que dicía o aviso. Cando o arranxes, volve premer «Xa o corrixín» en /misrecursos.',
    "b_si_quitar": "Si, quitalo",
    "b_no": "Non",
    "b_nuevo_recurso": "Engadir un recurso novo",
    "b_otro_correo": "Engadir os doutro correo",
    "c_buscar": "Buscar nos grupos",
    "c_biblioteca": "Engadir á Biblioteca",
    "c_repositorio": "Engadir ao repositorio",
    "c_misrecursos": "Os teus recursos",
    "c_ayuda": "Que fago e como",
    "valoracion_si": "Grazas!",
    "valoracion_no": "Grazas. Gardo a pregunta, sen nada teu, para mellorar.",
    "valoracion_antigua": "Grazas.",
    "respuesta_vacia": "Non atopei nada que responda a iso. Proba a dicilo con outras palabras ou a concretar máis.",
    "codigo": "Son software libre (AGPL v3), versión {version}: o código está en https://github.com/jjdeharo/bot-chatgpt-ia-edu.",
}

EU = {
    "al_menos_uno": 'Gutxienez talde bat markatuta geratu behar da.',
    "quitado_biblioteca": 'Liburutegi digitaletik kenduta.',
    "b_quitar_biblioteca": 'Liburutegitik kendu',
    "buscando_en": 'Hemen bilatzen: {grupos}.',
    "b_mantener": 'Mantendu',
    "b_quitar_grupo": 'Taldetik kendu',
    "no_quitar_ya": 'Ezin dut kendu jada: Telegramek 48 orduz bakarrik uzten du mezuak ezabatzen. Eskatu taldea kudeatzen duenari.',
    "mantenido": 'Ados, argitaratuta geratzen da.',
    "quitado_grupo": 'Taldetik kenduta.',
    "pregunta_compartir": 'Vibe Coding Educativo taldeko «¡Comparte tu App!» gaian ere partekatu nahi duzu? Oraindik ez da ezer argitaratuko: aurretik mezua erakutsiko dizut, berrikusi, aldatu edo bertan behera uzteko.',
    "vista_compartir": 'Hau da «¡Comparte tu App!» gaian argitaratuko nukeen mezua, zure izenarekin. Argitaratu dezakezu, aldaketak eskatu, zuk zeuk argitaratu edo bertan behera utzi.',
    "compartido": '«¡Comparte tu App!» gaian argitaratua: {enlace}\nIritziz aldatzen baduzu, beheko botoiarekin ken dezakezu hurrengo 48 orduetan.',
    "publicalo_tu": 'Hona hemen testua, zuk zeuk «¡Comparte tu App!» gaian argitaratzeko: https://t.me/vceduca/7674',
    "no_compartir": 'Ados, ez dut partekatzen.',
    "b_si": 'Bai',
    "b_lo_publico_yo": 'Nik argitaratuko dut',
    "b_anteriores": "Aurrekoak",
    "b_siguientes": "Hurrengoak",
    "seguidas": "Galdera asko egin dizkidazu jarraian eta atseden pixka bat behar dut. Idatzi berriro pixka bat barru eta jarraituko dugu.",
    # Perfil del bot (setMyDescription y setMyShortDescription): aquí va la autoría.
    "perfil": 'ChatGPT-IA-edu, Vibe Coding Educativo eta EduMedia-IAG taldeetan bilatzen dut nork esan zuen zerbait, noiz eta zein mezutan, eta Liburutegi digitaleko zein dokumentuk jorratzen duten gai bat. Dokumentuak gehitzen ditut Liburutegira eta baliabide hezitzaileak Vibe Coding Educativo-ren biltegira. Claude erabiltzen dut, Anthropic-en IA bat. Egilea: @jjdeharo.',
    "perfil_corto": 'ChatGPT-IA-edu, Vibe Coding Educativo eta EduMedia-IAG-en bilatzen du; dokumentuak eta baliabideak gehitzen ditu.',
    "licencia_cerrada": 'Oraindik ez dut gehitzen: haren lizentziak ({licencia}) ez du kodea partekatzen uzten. Biltegiak lizentzia irekiak onartzen ditu: kode irekikoak edo Creative Commons. Zein aukeratu ez badakizu, galdetu niri: baimendu nahi duzunaren arabera bat gomendatuko dizut eta nola jarri azalduko dizut. Informazio gehiago: https://vibe-coding-educativo.github.io/vibe-responsable/eu/capitulo-9.html. Gero bidali berriro baliabidea: HTML fitxategia, ZIP bat edo haren GitHub biltegiaren esteka.',
    "de_pago": "Ezin dut gehitu: biltegia doako baliabideetarako bakarrik da, ordainpeko bertsiorik eta freemiumik gabe, eta hau ez dirudi halakoa ({detalle}).",
    "sin_licencia": 'Oraindik ez dut gehitzen: biltegiak kodea lizentzia ireki batekin argitaratuta egotea eskatzen du, eta ez dut bat ere aurkitzen ez kodean ez haren biltegian. Zein aukeratu ez badakizu, galdetu niri: baimendu nahi duzunaren arabera bat gomendatuko dizut eta nola jarri azalduko dizut. Informazio gehiago: https://vibe-coding-educativo.github.io/vibe-responsable/eu/capitulo-9.html. Gero bidali berriro baliabidea: HTML fitxategia, ZIP bat edo haren GitHub biltegiaren esteka.',
    "licencia_visible": "Aholku bat: lizentzia ({licencia}) biltegian dago, beraz baliabideak baldintzak betetzen ditu, baina orria irekitzen duenak ez du ikusten. Edonork jakin dezan berrerabil dezakeela, jarri lerro ikusgai bat orri-oinean, adibidez «{licencia} lizentzia», eta beste bat kodearen hasieran: <!-- SPDX-License-Identifier: {spdx} -->. IA batekin egin baduzu, eskatu bi lerro horiek gehitzeko. Gomendio bat da, ez baldintza bat.",
    "cambio_licencia_cerrada": 'Ez dut aldaketa gordetzen: haren lizentziak ({licencia}) ez du kodea partekatzen uzten, eta biltegiak lizentzia irekiak bakarrik onartzen ditu: kode irekikoak edo Creative Commons. Zein aukeratu ez badakizu, galdetu niri: baimendu nahi duzunaren arabera bat gomendatuko dizut eta nola jarri azalduko dizut. Informazio gehiago: https://vibe-coding-educativo.github.io/vibe-responsable/eu/capitulo-9.html. Aldatu ondoren, sakatu berriro «Zerbait aldatu».',
    "cambio_sin_licencia": 'Ez dut aldaketa gordetzen: biltegiak kodea lizentzia ireki batekin argitaratuta egotea eskatzen du, eta ez dut bat ere aurkitzen ez kodean ez haren biltegian. Zein aukeratu ez badakizu, galdetu niri: baimendu nahi duzunaren arabera bat gomendatuko dizut eta nola jarri azalduko dizut. Informazio gehiago: https://vibe-coding-educativo.github.io/vibe-responsable/eu/capitulo-9.html. Jarri ondoren, sakatu berriro «Zerbait aldatu».',
    "inicio": ("Kaixo. [ChatGPT-IA-edu](https://t.me/ChatGPTedu), "
               "[Vibe Coding Educativo](https://t.me/vceduca) eta [EduMedia-IAG](https://t.me/EduMediaIAG) taldeen bota naiz. Hauetan laguntzen dizut:"),
    "ayuda_buscar": (
        "🔍 Taldeetan bilatu. Galdetu zure hitzekin nork esan zuen zerbait, noiz, ChatGPT-IA-edu "
        "taldeko Liburutegi digitaleko zein dokumentuk edo Vibe Coding Educativo-ren biltegiko zein baliabidek "
        "jorratzen duten gai bat, eta bakoitzaren estekarekin erantzungo dizut. Hiru taldeetan bilatzen dut aldi "
        "berean; bat edo bi bakarrik nahi badituzu, aipatu. "
        "Adibidez: «nork hitz egin zuen iaz IArekin ebaluatzeaz?», «ba al dago haur hezkuntzako IA gidarik?», "
        "«ba al dago probabilitatea lantzeko aplikaziorik?» "
        "edo «zer esan da Vibe Coding Educativo taldean GitHub Pages-en argitaratzeaz?»."),
    "ayuda_biblioteca": (
        "📄 Dokumentu bat gehitu ChatGPT-IA-edu taldeko Liburutegi digitalera. Bidali hona PDF fitxategia "
        "(20 MB arte) eta nik egingo dut dena: egiaztatuko dut hezkuntzako IAri buruzkoa dela eta "
        "liburutegian ez dagoela, haren fitxa prestatuko dut eta erakutsiko dizut. Ados bazaude, zure "
        "izenarekin argitaratuko dut. Haren lizentziak partekatzen uzten ez badu, fitxa bakarrik argitaratuko dut."),
    "ayuda_recurso": (
        "📱 Baliabide hezitzaile digital bat gehitu [Vibe Coding Educativo taldearen biltegira](https://vibe-coding-educativo.github.io/app_edu/)"
        ". Bidali haren esteka: baliabidea irakurriko dut, "
        "haren fitxa prestatuko dut eta erakutsiko dizut; ados bazaude, argitaratuko dut. Doakoa izan behar "
        "du, eta kodea lizentzia ireki batekin argitaratuta. /misrecursos komandoarekin zureak aldatu edo "
        "kendu ditzakezu nahi duzunean."),
    "ayuda_menu": 'Aukera guztiak menuan dituzu: «Menua» botoia, idazten duzun lekuaren ezkerrean.',
    "ayuda_final": (
        "Nola funtzionatzen dudan: Claude erabiltzen duen programa bat naiz, Anthropic-en IA bat. Idazten "
        "didazuna, taldeetan aurkitzen ditudan mezuak eta bidaltzen didazuna Anthropic-en zerbitzarietan "
        "prozesatzen dira, Ameriketako Estatu Batuetan. Erantzun ezin ditudan galderak edo 👎 batekin markatzen dituzunak bakarrik gordetzen ditut, zure izenik eta konturik gabe, bota hobetzeko, eta 60 egunera ezabatzen ditut. Oker egon naiteke: "
        "egiaztatu beti estekatutako mezua. Idazten didazun hizkuntzan hitz egiten dizut."),
    "traduccion": "Testuak IArekin automatikoki itzuliak, berrikuspen profesionalik gabe.",
    "buscar": 'Idatzi zer bilatzen duzun, zure hitzekin. Markatutako taldeetan bilatzen dut; ukitu bat markatzeko edo desmarkatzeko. Hitz egiten jarraitzen dugun bitartean mantenduko dut.',
    "biblioteca": "Bidali dokumentua PDFn (20 MB arte) eta haren fitxa prestatuko dut.",
    "solo_chatgpt": "Liburutegi digitalera dokumentuak gehitzea ChatGPT-IA-edu taldeko kideen kontua da. Sartzea librea da: batu zaitez taldera eta bidali berriro. Hau da taldea: https://t.me/ChatGPTedu",
    "solo_vce": ("Baliabideen biltegia Vibe Coding Educativo komunitatearena da; zureak gehitzeko, "
                 "batu taldera: https://t.me/vceduca"),
    "no_miembro": "Sentitzen dut, ChatGPT-IA-edu (https://t.me/ChatGPTedu), Vibe Coding Educativo (https://t.me/vceduca) edo EduMedia-IAG (https://t.me/EduMediaIAG) taldeetako kideei bakarrik erantzun diezaieket. Sartzea librea da: batu zaitez edozeinetara eta idatzi berriro.",
    "no_autorizado": "Oraindik probetan nago. Laster egongo naiz taldeentzat irekita.",
    "cupo": "Gaurko {cupo} galderetara iritsi zara. Bihar jarraitu ahal izango duzu.",
    "tope": "Hilabete honetan botaren aurrekontua agortu da. Hilaren 1ean berriro ibiliko da.",
    "error": "Zerbait gaizki atera da bilatzean. Saiatu berriro une batean.",
    "solo_texto": "Oraingoz idatzizko mezuak eta pantaila-argazkiak bakarrik ulertzen ditut. Idatzi galdera, mesedez.",
    "solo_privado": "Kaixo, {nombre}. IA Educativa bota naiz. Taldean ezin dizut erantzun, baina pribatuan bai. Idatzi hemen: https://t.me/{usuario}",
    "solo_privado_comando": "Kaixo, {nombre}. IA Educativa bota naiz. Hau ez dabil taldean, baina pribatuan bai. Ireki hemen: https://t.me/{usuario}?start={comando}",
    "no_pdf": "Liburutegi digitalera dokumentu bat gehitzeko, bidali PDFn.",
    "grande": ("Fitxategi honek {mb:.0f} MB ditu, eta Telegramek 20 MB arteko fitxategiak bakarrik uzten "
               "dizkie botei deskargatzen; beraz, ezin dut irakurri. Zuk zeuk igo dezakezu Liburutegi "
               "digitalera (https://t.me/ChatGPTedu/21753) eta haren fitxa prestatu "
               "https://chatgpt-ia-edu.github.io/resumen/ orriarekin"),
    "cupo_docs": "Gaur {docs} dokumentu bidali dizkidazu jada. Bihar gehiago bidali ahal izango dituzu.",
    "leyendo": "Jasota. Irakurri, liburutegian sartzen den egiaztatu eta fitxa prestatuko dut. Minutu bat behar dut.",
    "sin_texto": ("Ezin dut PDF honen testua irakurri: irudi gisa eskaneatuta dagoela dirudi. Zuk zeuk igo "
                  "dezakezu Liburutegi digitalera (https://t.me/ChatGPTedu/21753) eta haren fitxa prestatu "
                  "https://chatgpt-ia-edu.github.io/resumen/ orriarekin"),
    "ajeno": "Ezin dut gehitu: Liburutegi digitala hezkuntzako adimen artifizialari buruzko dokumentuetarako da, eta honek beste gai bat jorratzen du ({tema}).",
    "repetido": "Dokumentu hau Liburutegi digitalean dago jada: {enlace}",
    "vista": ("Hau da fitxa, gaztelaniaz liburutegi osoa bezala. Ados bazaude, dokumentua «Aportado por "
              "{autor}» testuarekin argitaratuko dut Liburutegi digitalean, eta fitxa erantzun gisa."),
    "vista_sin_archivo": ("Hau da fitxa, gaztelaniaz liburutegi osoa bezala. Haren lizentziak ez du fitxategia "
                          "partekatzen uzten; beraz, fitxa bakarrik argitaratuko dut Liburutegi digitalean, "
                          "«Aportado por {autor}» testuarekin."),
    "publicado": 'Liburutegi digitalean argitaratua: {enlace}\nIritziz aldatzen baduzu, beheko botoiarekin ken dezakezu hurrengo 48 orduetan.',
    "cancelado": "Ados, ez dut argitaratzen.",
    "caducado": "Fitxa hau ez dago eskuragarri. Argitaratu nahi baduzu, bidali berriro dokumentua.",
    "sustituido": "Aurrebista hori ez da azkena: beste bat prestatu dut gero. Erabili azken mezuaren botoiak.",
    "error_doc": "Zerbait gaizki atera da fitxa prestatzean. Saiatu berriro geroxeago.",
    "recurso": ("Bidali baliabidearen esteka (edonork irekitzen duen helbidea). Estekak kodea ikusten uzten ez "
                "badu, HTML fitxategia, ZIP bat edo haren GitHub biltegiaren esteka ere balio didate."),
    "leyendo_recurso": "Jasota. Baliabidea ireki, irakurri eta haren fitxa prestatuko dut. Minutu bat behar dut.",
    "ya_esta_tuyo": "Baliabide hau biltegian dago jada, eta zurea da: {enlace}\nAldatzeko, erabili /misrecursos.",
    "url_ocupada": "Ez dut esteka aldatzen: beste baliabide batekin dago jada biltegian: {enlace}",
    "ya_esta_ajeno": ("Baliabide hau biltegian dago jada, {autor}(r)en izenean: {enlace}\nZurea bada eta "
                      "formularioarekin eman bazenuen alta, erabili /misrecursos berreskuratzeko."),
    "falta_info": ("Ezin dut estekatik ikusi baliabideak zer egiten duen ({motivo}). Bidali HTML fitxategia edo "
                   "kodea duen ZIP bat, haren GitHub biltegiaren esteka, edo kontatu mezu batean zer egiten "
                   "duen eta nola erabiltzen den."),
    "no_educativo": "Ezin dut gehitu: biltegia baliabide hezitzaileetarako da, eta hau ez dirudi halakoa ({motivo}). Oker nagoela uste baduzu, sakatu «Berrikusteko eskatu» eta pertsona batek begiratuko du.",
    "sin_minimo": "Oraindik ez dut gehitzen: biltegia ikasgelan dagoeneko erabil daitezkeen baliabideetarako da, eta honi zerbait falta zaio ({motivo}). Prest duzunean, bidali berriro esteka. Oker nagoela uste baduzu, sakatu «Berrikusteko eskatu» eta pertsona batek begiratuko du.",
    "b_pedir_revision": "Berrikusteko eskatu",
    "por_que_revision": "Esan mezu batean zergatik uste duzun sartu beharko lukeela. Berrikusten duen pertsonak irakurriko du.",
    "revision_pedida": "Eginda: eskuzko berrikuspenera doa. Erabakitzen denean jakinaraziko dizut.",
    "revision_ya_pedida": "Baliabide hau eskuzko berrikuspenean dago jada. Erabakitzen denean jakinaraziko dizut.",
    "rechazo_revisado_si": "Eskuz berrikusita: «{titulo}» biltegian sar daiteke. Altarekin jarraituko dut.",
    "rechazo_revisado_no": "Eskuz berrikusita: «{titulo}» ez da biltegian sartzen. Aldatzen baduzu, berriro bidal dezakezu /repositorio erabiliz.",
    "mudanza_no_entra": "Ez dut esteka aldatzen: esteka berrian dagoena ez da biltegian sartzen ({motivo}). Fitxak lehen bezala jarraitzen du.",
    "vista_recurso": ("Hau da fitxa, gaztelaniaz biltegi osoa bezala. Ados bazaude, Vibe Coding Educativo "
                      "biltegian argitaratuko dut. Zerbait aldatu nahi baduzu, sakatu «Zerbait aldatu» eta "
                      "esan zure hitzekin."),
    "que_cambio": ("Esan zer aldatu nahi duzun, zure hitzekin. Baliabidea berriro begiratzen dut, beraz edozein "
                   "datu berrikusi edo berregin dezaket. Adibidez: «kendu Batxilergoa», «egilea Ane Agirre da», "
                   "«berregin deskribapena», «berrikusi hizkuntzak» edo «berrikusi fitxa osoa»."),
    "que_cambio_mensaje": ("Esan mezuan zer aldatu nahi duzun, zure hitzekin. Adibidez: «laburragoa» edo "
                           "«esan LHrako ere balio duela»."),
    "vista_cambio": "Horrela geratzen da. Ados bazaude, sakatu «Argitaratu»; bestela, «Zerbait aldatu» berriro.",
    "publicado_recurso": ("Argitaratua. Biltegiko zerrendan lehena ikusiko duzu: {enlace}\n"
                          "Geroago aldatzeko edo kentzeko, erabili /misrecursos."),
    "modificado_recurso": "Eginda. Minutu batzuk barru ikusiko da aldaketa biltegian: {enlace}",
    "cancelado_recurso": "Ados, zegoen bezala uzten dut.",
    "caducado_recurso": "Fitxa hau ez dago eskuragarri. Bidali berriro baliabidearen esteka.",
    "cupo_recursos": "Gaur {recursos} baliabide-fitxa prestatu dituzu jada. Bihar gehiago prestatu ahal izango dituzu.",
    "error_recurso": "Zerbait gaizki atera da biltegiarekin. Saiatu berriro geroxeago.",
    "grande_recurso": "Fitxategi honek 20 MB baino gehiago ditu, eta Telegramek ez die botei deskargatzen uzten.",
    "archivo_sin_enlace": ("Kodea bidali aurretik, bidali baliabidearen esteka: jendeak biltegitik irekiko "
                           "duen helbidea."),
    "mis_recursos": "Hauek dira biltegian dituzun baliabideak. Sakatu bat aldatzeko edo kentzeko.",
    "sin_recursos": ("Ez daukat baliabiderik zure izenean. Formularioarekin bakarren bati alta eman bazenion, "
                     "idatzi erabili zenuen helbide elektronikoa eta kode bat bidaliko dizut zurea dela egiaztatzeko."),
    "otro_correo": "Idatzi formularioan baliabideei alta emateko erabili zenuen helbide elektronikoa.",
    "no_es_correo": "Hori ez dirudi helbide elektronikoa. Erabili /misrecursos eta idatzi berriro, adibidez izena@gmail.com.",
    "correo_sin_recursos": "Helbide horrekin ez dago baliabiderik biltegian. Egiaztatu ondo idatzita dagoela.",
    "codigo_enviado": ("Kode bat bidali dizut {correo} helbidera (begiratu zabor-postan ere). "
                       "Idatzi hemen."),
    "codigo_mal": "Kode hori ez da zuzena. Begiratu posta eta idatzi berriro.",
    "codigo_agotado": "Kode horrek ez du balio hainbat saiakera huts egin ondoren. Erabili /misrecursos eta beste bat bidaliko dizut.",
    "codigo_ok": "Egiaztatuta. Hemendik aurrera {correo} helbidearen baliabideak kudea ditzaket.",
    "borrar_seguro": "Ziur «{titulo}» biltegitik kendu nahi duzula? Ezin da desegin.",
    "borrado": "Biltegitik kenduta. Minutu batzuk barru ez da gehiago ikusiko.",
    "no_tuyo": "Baliabide hori ez dago zure izenean, beraz ezin dut aldatu. Zurea bada eta formularioarekin eman bazenuen alta, erabili /misrecursos berreskuratzeko.",
    "b_publicar": "Argitaratu",
    "b_cambiar": "Zerbait aldatu",
    "b_cancelar": "Utzi",
    "b_quitar": "Kendu",
    # «Ya lo he corregido» y avisos de la revisión del repositorio (ADR 0013)
    "b_corregido": 'Zuzendu dut',
    "b_si_la_tiene": 'Badauka: eskuzko berrikuspena',
    "mis_recursos_avisos": '⚠️ dutenek biltegiaren berrikuspeneko ohar bat dute: sakatu bat zer falta zaion ikusteko.',
    "mis_recursos_sin_licencia": 'ℹ️ dutenek ez dute lizentziarik: biltegian jarraituko dute, baina gehitzea gomendatzen dizugu.',
    "aviso_A": 'ℹ️ Ez dugu lizentziarik aurkitu, ez orrian ez bere biltegian. Biltegiak lizentzia eskatu aurretik argitaratu zenez, bertan jarraituko du hala ere, baina gehitzea gomendatzen dizugu (adibidez, lerro bat orri-oinean: «Kodea AGPL v3 lizentziapean · edukiak CC BY-SA 4.0 lizentziapean») eta «Zuzendu dut» sakatzea. Nola aukeratu: https://vibe-coding-educativo.github.io/vibe-responsable/eu/capitulo-9.html',
    "aviso_B": '⚠️ Biltegiaren berrikuspeneko oharra: esteka ez da irekitzen ({motivo}). Lekuz aldatu bada, sakatu «Zerbait aldatu» eta idatzi esteka berria; jada ez badago, sakatu «Kendu». {plazo} egunean oraindik irekitzen ez bada, biltegitik ezabatuko da.',
    "aviso_C": '⚠️ Biltegiaren berrikuspeneko oharra: ChatGPTko GPT bat da. OpenAIk 2026ko abenduaren 11n kenduko ditu, eta biltegiak kodea azter daitekeen baliabideak bakarrik onartzen ditu; beraz, egun horretan biltegitik ezabatuko da. Bere kodea eta lizentzia irekia dituen aplikazio gisa berregiten baduzu, /repositorio erabiliz gehi dezakezu.',
    "aviso_D": '⚠️ Biltegiaren berrikuspeneko oharra: orriak «Eskubide guztiak erreserbatuta» dio. Biltegiak kode irekiko programak bakarrik onartzen ditu, edonork aztertu, partekatu eta egokitu ditzakeenak. Aldatu ezazu lizentzia ireki batengatik {plazo} baino lehen eta sakatu «Zuzendu dut». Nola aukeratu: https://vibe-coding-educativo.github.io/vibe-responsable/eu/capitulo-9.html',
    "aviso_ya_no": 'Baliabide honek ez du oharrik zain.',
    "comprobando": 'Egiaztatzen ari naiz. Segundo batzuk behar ditut.',
    "aviso_plataforma": 'Ezin ditut neure kabuz irakurri Gemini, Claude edo AI Studioko aplikazioak; beraz, eskuz berrikusiko da. Zerbait falta bada oraindik, abisatuko dizut.',
    "aviso_no_abre": 'Oraindik ez da irekitzen. {problema} Lekuz aldatu bada, sakatu «Zerbait aldatu» baliabidean eta idatzi esteka berria.',
    "aviso_resuelto": 'Egiaztatuta: badu lizentzia ({licencia}). Oharra konpondu da eta baliabidea biltegian jarraitzen du. Eskerrik asko!',
    "aviso_de_pago": 'Badu lizentzia, baina ordainpekoa edo freemium dirudi: {detalle}. Biltegiak doako baliabideak bakarrik onartzen ditu. Oker banago, sakatu berriro «Zuzendu dut» aldatu duzunean, edo aipatu taldean.',
    "aviso_sin_licencia": 'Oraindik ez dut lizentziarik aurkitzen, ez orrian ez bere biltegian. Jarri berri baduzu, itxaron minutu batzuk, webgunea eguneratzeko denbora behar baita, eta sakatu berriro «Zuzendu dut». Badauka eta ez badut aurkitzen (adibidez, orria kargatzean bakarrik agertzen delako), sakatu botoia eta eskuz berrikusiko da.',
    "aviso_dice_que_si": 'Eginda: eskuz berrikusiko da. Lizentzia aurkitzen bada, oharra konponduta geratuko da eta abisatuko dizut.',
    "aviso_revisado_si": 'Eskuz berrikusita: «{titulo}» baldintzak betetzen ditu eta oharra konponduta dago. Eskerrik asko!',
    "aviso_revisado_no": 'Eskuz berrikusita: «{titulo}»-ri oraindik falta zaio oharrak zioena. Konpontzen duzunean, sakatu berriro «Zuzendu dut» /misrecursos atalean.',
    "b_si_quitar": "Bai, kendu",
    "b_no": "Ez",
    "b_nuevo_recurso": "Baliabide berri bat gehitu",
    "b_otro_correo": "Beste helbide batekoak gehitu",
    "c_buscar": "Bilatu taldeetan",
    "c_biblioteca": "Gehitu Liburutegira",
    "c_repositorio": "Gehitu biltegira",
    "c_misrecursos": "Kudeatu zure baliabideak",
    "c_ayuda": "Zer egiten dudan eta nola",
    "valoracion_si": "Eskerrik asko!",
    "valoracion_no": "Eskerrik asko. Galdera gordetzen dut, zure daturik gabe, hobetzeko.",
    "valoracion_antigua": "Eskerrik asko.",
    "respuesta_vacia": "Ez dut horri erantzuten dion ezer aurkitu. Saiatu beste hitz batzuekin esaten edo gehiago zehazten.",
    "codigo": "Software librea naiz (AGPL v3), {version} bertsioa: kodea hemen dago: https://github.com/jjdeharo/bot-chatgpt-ia-edu.",
}

EN = {
    "al_menos_uno": 'At least one group has to stay ticked.',
    "quitado_biblioteca": 'Removed from the Digital Library.',
    "b_quitar_biblioteca": 'Remove it from the Library',
    "buscando_en": 'Searching in: {grupos}.',
    "b_mantener": 'Keep it',
    "b_quitar_grupo": 'Remove it from the group',
    "no_quitar_ya": "I can't remove it any more: Telegram only lets messages be deleted for 48 hours. Ask the group's administrators.",
    "mantenido": 'OK, it stays posted.',
    "quitado_grupo": 'Removed from the group.',
    "pregunta_compartir": 'Would you also like to share it in "¡Comparte tu App!" in the Vibe Coding Educativo group? Nothing will be posted yet: first I\'ll show you the message so you can review it, change it or cancel it.',
    "vista_compartir": 'This is the message I\'d post in "¡Comparte tu App!", under your name. You can post it, ask me for changes, post it yourself or cancel it.',
    "compartido": 'Posted in "¡Comparte tu App!": {enlace}\nIf you change your mind, you can remove it with the button below during the next 48 hours.',
    "publicalo_tu": 'Here is the text so you can post it yourself in "¡Comparte tu App!": https://t.me/vceduca/7674',
    "no_compartir": "OK, I won't share it.",
    "b_si": 'Yes',
    "b_lo_publico_yo": "I'll post it myself",
    "b_anteriores": "Previous",
    "b_siguientes": "Next",
    "seguidas": "You've asked me a lot of questions in a row and I need a breather. Write to me again in a little while and we'll carry on.",
    # Perfil del bot (setMyDescription y setMyShortDescription): aquí va la autoría.
    "perfil": 'I search the ChatGPT-IA-edu, Vibe Coding Educativo and EduMedia-IAG groups for who said something, when and in which message, and for documents in the Digital Library on a topic. I also add documents to the Library and educational resources to the Vibe Coding Educativo repository. I use Claude, an AI by Anthropic. Created by @jjdeharo.',
    "perfil_corto": 'Searches ChatGPT-IA-edu, Vibe Coding Educativo and EduMedia-IAG, and adds documents and resources.',
    "licencia_cerrada": "I'm not adding it yet: its licence ({licencia}) doesn't allow sharing the code. The repository accepts open licences: open source or Creative Commons. If you don't know which one to choose, ask me: I'll recommend one based on what you want to allow and explain how to add it. More information: https://vibe-coding-educativo.github.io/vibe-responsable/en/capitulo-9.html. Then send me the resource again: the HTML file, a ZIP or the link to its GitHub repository.",
    "de_pago": "I can't add it: the repository is only for free resources, with no paid or freemium versions, and this doesn't look like one ({detalle}).",
    "sin_licencia": "I'm not adding it yet: the repository requires the code to be published under an open licence, and I can't find one in the code or in its repository. If you don't know which one to choose, ask me: I'll recommend one based on what you want to allow and explain how to add it. More information: https://vibe-coding-educativo.github.io/vibe-responsable/en/capitulo-9.html. Then send me the resource again: the HTML file, a ZIP or the link to its GitHub repository.",
    "licencia_visible": "A tip: the licence ({licencia}) is in the repository, so the resource meets the requirements, but people who open the page can't see it. So that anyone knows they can reuse it, add a visible line in the footer, such as \"Licence: {licencia}\", and another at the start of the code: <!-- SPDX-License-Identifier: {spdx} -->. If you made it with an AI, ask it to add those two lines. It's a recommendation, not a requirement.",
    "cambio_licencia_cerrada": 'I\'m not saving the change: its licence ({licencia}) doesn\'t allow sharing the code, and the repository only accepts open licences: open source or Creative Commons. If you don\'t know which one to choose, ask me: I\'ll recommend one based on what you want to allow and explain how to add it. More information: https://vibe-coding-educativo.github.io/vibe-responsable/en/capitulo-9.html. Once you\'ve changed it, press "Change something" again.',
    "cambio_sin_licencia": 'I\'m not saving the change: the repository requires the code to be published under an open licence, and I can\'t find one in the code or in its repository. If you don\'t know which one to choose, ask me: I\'ll recommend one based on what you want to allow and explain how to add it. More information: https://vibe-coding-educativo.github.io/vibe-responsable/en/capitulo-9.html. Once you\'ve added it, press "Change something" again.',
    "inicio": ("Hello. I'm the bot of the [ChatGPT-IA-edu](https://t.me/ChatGPTedu), "
               "[Vibe Coding Educativo](https://t.me/vceduca) and [EduMedia-IAG](https://t.me/EduMediaIAG) groups. I can help you with this:"),
    "ayuda_buscar": (
        "🔍 Search the groups. Ask me in your own words who said something, when, which documents in "
        "the ChatGPT-IA-edu Digital Library or which resources in the Vibe Coding Educativo repository cover a "
        "topic, and I'll answer with a link to each one. I search all three groups at once; if you only want one "
        "or two, name them. For example: \"who talked about assessing with AI last school year?\", \"are there "
        "guides on AI in early years?\", \"is there an app to practise probability?\" or \"what has "
        "been said in Vibe Coding Educativo about publishing on GitHub Pages?\"."),
    "ayuda_biblioteca": (
        "📄 Add a document to the ChatGPT-IA-edu Digital Library. Send me the PDF file here (up to 20 MB) "
        "and I'll take care of everything: I check that it is about AI in education and not already in the "
        "library, prepare its record and show it to you. If you agree, I publish it under your name. If its "
        "licence doesn't allow sharing it, I publish only the record."),
    "ayuda_recurso": (
        "📱 Add a digital educational resource to the [Vibe Coding Educativo repository](https://vibe-coding-educativo.github.io/app_edu/)"
        ". Send me its link: I read the resource, prepare "
        "its record and show it to you; if you agree, I publish it. It must be free of charge and have its "
        "code published under an open licence. With /misrecursos you can change or remove yours whenever you like."),
    "ayuda_menu": 'All the options are in the menu: the «Menu» button, to the left of where you type.',
    "ayuda_final": (
        "How I work: I'm a program that uses Claude, an AI by Anthropic. What you write to me, the group "
        "messages I find and what you send me are processed on Anthropic's servers in the United States. "
        "I only keep the questions I can't answer or that you mark with 👎, without your name or account, to improve the bot, and I delete them after 60 days. I can make mistakes: always check the linked message. I reply in "
        "the language you write to me in."),
    "traduccion": "Texts machine-translated with AI, without professional review.",
    "buscar": "Tell me what you're looking for, in your own words. I search the ticked groups; tap one to tick or untick it. I'll keep it while we keep talking.",
    "biblioteca": "Send me the document as a PDF (up to 20 MB) and I'll prepare its record.",
    "solo_chatgpt": "Adding documents to the Digital Library is for members of ChatGPT-IA-edu. Joining is free: join the group and send it to me again. This is the group: https://t.me/ChatGPTedu",
    "solo_vce": ("The resource repository belongs to the Vibe Coding Educativo community; to add yours, "
                 "join the group: https://t.me/vceduca"),
    "no_miembro": "Sorry, I can only answer people who belong to the ChatGPT-IA-edu (https://t.me/ChatGPTedu), Vibe Coding Educativo (https://t.me/vceduca) or EduMedia-IAG (https://t.me/EduMediaIAG) groups. Joining is free: join any of them and write to me again.",
    "no_autorizado": "I'm still being tested. I'll be open to the groups soon.",
    "cupo": "You've reached today's {cupo} questions. You can continue tomorrow.",
    "tope": "The bot's budget for this month has run out. It will work again on the 1st.",
    "error": "Something went wrong while searching. Please try again in a moment.",
    "solo_texto": "For now I only understand written messages and screenshots. Please write your question.",
    "solo_privado": "Hi, {nombre}. I'm the IA Educativa Bot. I can't answer you in the group, but I can in private. Write to me here: https://t.me/{usuario}",
    "solo_privado_comando": "Hi, {nombre}. I'm the IA Educativa Bot. This doesn't work in the group, but it does in private. Open it here: https://t.me/{usuario}?start={comando}",
    "no_pdf": "To add a document to the Digital Library, send it to me as a PDF.",
    "grande": ("This file is {mb:.0f} MB and Telegram only lets bots download files of up to 20 MB, so I "
               "can't read it. You can upload it yourself to the Digital Library "
               "(https://t.me/ChatGPTedu/21753) and prepare its record with https://chatgpt-ia-edu.github.io/resumen/"),
    "cupo_docs": "You've already sent me {docs} documents today. You can send more tomorrow.",
    "leyendo": "Received. I'm reading it, checking whether it fits the library and preparing the record. It takes a minute.",
    "sin_texto": ("I can't read the text of this PDF: it seems to be scanned as an image. You can upload it "
                  "yourself to the Digital Library (https://t.me/ChatGPTedu/21753) and prepare its record "
                  "with https://chatgpt-ia-edu.github.io/resumen/"),
    "ajeno": "I can't add it: the Digital Library is for documents about artificial intelligence in education, and this one is about something else ({tema}).",
    "repetido": "This document is already in the Digital Library: {enlace}",
    "vista": ("This is the record, in Spanish like the whole library. If you agree, I'll publish the document "
              "in the Digital Library with \"Aportado por {autor}\" and the record as a reply."),
    "vista_sin_archivo": ("This is the record, in Spanish like the whole library. Its licence doesn't allow "
                          "sharing the file, so I'll publish only the record in the Digital Library, with "
                          "\"Aportado por {autor}\"."),
    "publicado": 'Published in the Digital Library: {enlace}\nIf you change your mind, you can remove it with the button below during the next 48 hours.',
    "cancelado": "OK, I won't publish it.",
    "caducado": "This record is no longer available. If you want to publish it, send me the document again.",
    "sustituido": "That preview is no longer the latest one: I prepared another after it. Use the buttons on the last message.",
    "error_doc": "Something went wrong while preparing the record. Please try again later.",
    "recurso": ("Send me the link to the resource (the address anyone can open). If the link doesn't show its "
                "code, the HTML file, a ZIP or the link to its GitHub repository also work."),
    "leyendo_recurso": "Received. I'm opening the resource, reading it and preparing its record. It takes a minute.",
    "ya_esta_tuyo": "This resource is already in the repository and it's yours: {enlace}\nTo change it, use /misrecursos.",
    "url_ocupada": "I'm not changing the link: it's already in the repository with another resource: {enlace}",
    "ya_esta_ajeno": ("This resource is already in the repository, under the name of {autor}: {enlace}\nIf it's "
                      "yours and you added it with the form, use /misrecursos to recover it."),
    "falta_info": ("I can't see what the resource does from the link ({motivo}). Send me the HTML file or a ZIP "
                   "with the code, the link to its GitHub repository, or tell me in a message what it does "
                   "and how it is used."),
    "no_educativo": 'I can\'t add it: the repository is for educational resources, and this doesn\'t look like one ({motivo}). If you think I\'m wrong, press "Request a review" and a person will look at it.',
    "sin_minimo": "I'm not adding it yet: the repository is for resources that can already be used in class, and this one is missing something ({motivo}). When it's ready, send me the link again. If you think I'm wrong, press \"Request a review\" and a person will look at it.",
    "b_pedir_revision": "Request a review",
    "por_que_revision": "Tell me in a message why you think it should be included. The person reviewing it will read it.",
    "revision_pedida": "Done: it goes to manual review. I'll let you know when it's decided.",
    "revision_ya_pedida": "This resource is already under manual review. I'll let you know when it's decided.",
    "rechazo_revisado_si": "Reviewed by hand: \"{titulo}\" can go into the repository. I'll carry on with adding it.",
    "rechazo_revisado_no": "Reviewed by hand: \"{titulo}\" doesn't go into the repository. If you change it, you can send it again with /repositorio.",
    "mudanza_no_entra": "I'm not changing the link: what's at the new one doesn't go into the repository ({motivo}). The record stays as it was.",
    "vista_recurso": ("This is the record, in Spanish like the whole repository. If you agree, I'll publish it in "
                      "the Vibe Coding Educativo repository. If you want to change something, press \"Change "
                      "something\" and tell me in your own words."),
    "que_cambio": ("Tell me what you want to change, in your own words. I look at the resource again, so I can "
                   "also review or redo any detail. For example: \"remove Bachillerato\", \"the author is Ann "
                   "Smith\", \"redo the description\", \"check the languages\" or \"review the whole record\"."),
    "que_cambio_mensaje": ("Tell me what you want to change in the message, in your own words. For example: "
                           "\"make it shorter\" or \"say it also works for vocational training\"."),
    "vista_cambio": "Here it is. If you agree, press \"Publish\"; if not, \"Change something\" again.",
    "publicado_recurso": ("Published. You'll see it first in the repository list: {enlace}\n"
                          "To change or remove it later, use /misrecursos."),
    "modificado_recurso": "Done. The change will show in the repository in a few minutes: {enlace}",
    "cancelado_recurso": "OK, I'll leave it as it was.",
    "caducado_recurso": "This record is no longer available. Send me the link to the resource again.",
    "cupo_recursos": "You've already prepared {recursos} resource records today. You can prepare more tomorrow.",
    "error_recurso": "Something went wrong with the repository. Please try again later.",
    "grande_recurso": "This file is larger than 20 MB and Telegram doesn't let bots download it.",
    "archivo_sin_enlace": ("Before sending me the code, send me the link to the resource: the address people "
                           "will open from the repository."),
    "mis_recursos": "These are your resources in the repository. Press one to change or remove it.",
    "sin_recursos": ("I don't have any resources under your name. If you added any with the form, write me "
                     "the email address you used and I'll send you a code to check that they're yours."),
    "otro_correo": "Write me the email address you used to add your resources with the form.",
    "no_es_correo": "That doesn't look like an email address. Use /misrecursos and type it again, for example name@gmail.com.",
    "correo_sin_recursos": "There are no resources in the repository with that email address. Check that it's spelled correctly.",
    "codigo_enviado": ("I've sent a code to {correo} (check your spam folder too). "
                       "Write it here."),
    "codigo_mal": "That code isn't correct. Check your email and write it again.",
    "codigo_agotado": "That code is no longer valid after several failed attempts. Use /misrecursos and I'll send you another one.",
    "codigo_ok": "Verified. From now on I can manage the resources of {correo}.",
    "borrar_seguro": "Are you sure you want to remove \"{titulo}\" from the repository? This can't be undone.",
    "borrado": "Removed from the repository. It will disappear in a few minutes.",
    "no_tuyo": "That resource isn't under your name, so I can't change it. If it's yours and you registered it with the form, use /misrecursos to recover it.",
    "b_publicar": "Publish",
    "b_cambiar": "Change something",
    "b_cancelar": "Cancel",
    "b_quitar": "Remove",
    # «Ya lo he corregido» y avisos de la revisión del repositorio (ADR 0013)
    "b_corregido": "I've fixed it",
    "b_si_la_tiene": 'It has one: manual review',
    "mis_recursos_avisos": 'The ones marked ⚠️ have a notice from the repository review: tap one to see what it is missing.',
    "mis_recursos_sin_licencia": 'The ones marked ℹ️ have no licence: they will stay in the repository, but we recommend adding one.',
    "aviso_A": "ℹ️ We could not find any licence, either on the page or in its repository. As it was published before the repository required one, it will stay there anyway, but we recommend adding one (for example, a line in the footer: “Code under AGPL v3 · content under CC BY-SA 4.0”) and tapping “I've fixed it”. How to choose one: https://vibe-coding-educativo.github.io/vibe-responsable/en/capitulo-9.html",
    "aviso_B": '⚠️ Repository review notice: the link does not open ({motivo}). If it has moved, tap “Change something” and write the new link; if it no longer exists, tap “Remove”. If it still does not open on {plazo}, it will be removed from the repository.',
    "aviso_C": '⚠️ Repository review notice: it is a ChatGPT GPT. OpenAI is retiring them on 11 December 2026, and the repository only accepts resources whose code can be examined, so it will be removed from the repository that day. If you rebuild it as an app with its code and an open licence, you can add it with /repositorio.',
    "aviso_D": "⚠️ Repository review notice: the page says “All rights reserved”. The repository only accepts open-source programs that anyone can examine, share and adapt. Change it to an open licence before {plazo} and tap “I've fixed it”. How to choose one: https://vibe-coding-educativo.github.io/vibe-responsable/en/capitulo-9.html",
    "aviso_ya_no": 'This resource has no pending notice any more.',
    "comprobando": 'Checking. It takes a few seconds.',
    "aviso_plataforma": 'I cannot read Gemini, Claude or AI Studio apps on my own, so it goes to manual review. If something is still missing, I will let you know.',
    "aviso_no_abre": 'It still does not open. {problema} If it has moved, tap “Change something” on the resource and write the new link.',
    "aviso_resuelto": 'Checked: it now has a licence ({licencia}). The notice is resolved and the resource stays in the repository. Thank you!',
    "aviso_de_pago": "It has a licence, but it looks paid or freemium: {detalle}. The repository only accepts free resources. If I am wrong, tap “I've fixed it” again once you have changed it, or mention it in the group.",
    "aviso_sin_licencia": "I still cannot find any licence, either on the page or in its repository. If you have just added it, wait a few minutes, because the website takes a while to update, and tap “I've fixed it” again. If it already has one and I cannot find it (for example, because it only appears when the page loads), tap the button and it will go to manual review.",
    "aviso_dice_que_si": 'Done: it goes to manual review. If the licence is found, the notice will be resolved and I will let you know.',
    "aviso_revisado_si": 'Checked by hand: “{titulo}” meets the requirements and the notice is resolved. Thank you!',
    "aviso_revisado_no": "Checked by hand: “{titulo}” still lacks what the notice said. When you have fixed it, tap “I've fixed it” again in /misrecursos.",
    "b_si_quitar": "Yes, remove it",
    "b_no": "No",
    "b_nuevo_recurso": "Add a new resource",
    "b_otro_correo": "Add those of another email",
    "c_buscar": "Search the groups",
    "c_biblioteca": "Add to the Library",
    "c_repositorio": "Add to the repository",
    "c_misrecursos": "Manage your resources",
    "c_ayuda": "What I do and how",
    "valoracion_si": "Thanks!",
    "valoracion_no": "Thanks. I'm keeping the question, with nothing about you, to improve.",
    "valoracion_antigua": "Thanks.",
    "respuesta_vacia": "I haven't found anything that answers that. Try saying it in other words or being more specific.",
    "codigo": "I am free software (AGPL v3), version {version}: the code is at https://github.com/jjdeharo/bot-chatgpt-ia-edu.",
}

TEXTOS = {"es": ES, "ca": CA, "gl": GL, "eu": EU, "en": EN}


def lengua_de_telegram(codigo: str | None) -> str:
    """El idioma de la app de Telegram, si es catalán, gallego o euskera; si no, castellano.

    El inglés no se toma de ahí: la app de Juanjo, en castellano, mandaba «en», y Karla bot le
    contestó en inglés a /start (27-10-2026). Quien escribe en inglés lo recibe desde su primera
    frase (ADR 0005)."""
    c = (codigo or "").lower()[:2]
    return c if c in ("ca", "gl", "eu") else "es"


def texto(lengua: str, clave: str, **datos) -> str:
    t = TEXTOS.get(lengua, ES).get(clave) or ES[clave]
    return t.format(**datos) if datos else t
