# SPDX-License-Identifier: AGPL-3.0-or-later
"""Lo que dice Karla bot, en castellano, catalán, gallego, euskera e inglés.

Karla habla en femenino y deja claro que no es una persona (Juanjo, 27-10-2026).
Como en el Bot de IA Educativa (ADR 0005), habla en el idioma en que le escriben
y, mientras no han escrito nada, en el de su Telegram; las traducciones son
automáticas, hechas con IA, sin revisión profesional. Lo que falte en un idioma
sale en castellano. Los avisos para Juanjo van solo en castellano.
"""
from textos import LENGUAS, lengua_de_telegram  # noqa: F401 — los mismos cinco idiomas

__all__ = ["LENGUAS", "lengua_de_telegram", "texto"]

ES = {
    "inicio": ("Hola, soy Karla, una asistente para resolver dudas sobre [eXeLearning](https://exelearning.net). "
               "No soy una persona: soy un programa que usa inteligencia artificial."),
    "ayuda_preguntar": ("🔎 Pregúntame lo que quieras. Escríbeme tu duda con tus palabras: cómo se hace algo, "
                        "por qué el programa se comporta de una manera o cómo publicar tu recurso en Moodle, "
                        "Procomún u otra plataforma. Busco en el manual, en la documentación del programa y de sus "
                        "complementos y en lo que se ha hablado en el grupo [eXeLearning](https://t.me/exelearning), "
                        "y te digo de dónde sale cada cosa. Puedes mandarme una captura de pantalla o el archivo .elpx de tu proyecto con la duda, o contármela en una nota de voz. Si lo que "
                        "cuentas es un fallo del programa, busco si ya está avisado y, si quieres, preparo el aviso para el "
                        "equipo que lo desarrolla."),
    "ayuda_final": ("ℹ️ Ten en cuenta: puedo equivocarme, así que comprueba lo importante en el mensaje o el "
                    "documento que cito. Lo que me escribes se procesa con Claude, una IA de Anthropic, en "
                    "servidores de Estados Unidos. Solo guardo las preguntas que no consigo "
                    "responder o que marcas con 👎, sin tu nombre ni tu cuenta, para mejorar, y las borro a los 60 días. Respondo a los miembros del grupo "
                    "eXeLearning. Me ha creado @jjdeharo."),
    "traduccion": "",
    "perfil": ("Soy Karla, una asistente para resolver dudas sobre eXeLearning. Busco en su manual, en la "
               "documentación del programa y de sus complementos y en las conversaciones del grupo de Telegram "
               "eXeLearning, y digo de dónde sale cada respuesta. No soy una persona: soy un programa que usa "
               "Claude, una IA de Anthropic. Creada por @jjdeharo."),
    "perfil_corto": "Resuelvo dudas sobre eXeLearning con su manual, su documentación y lo hablado en el grupo.",
    "c_ayuda": "Cómo funciono",
    "no_miembro": "Lo siento, solo puedo responder a quien forma parte del grupo eXeLearning (https://t.me/exelearning). Entrar es libre: únete y vuelve a escribirme.",
    "no_autorizado": "Todavía estoy en pruebas. Pronto estaré abierta al grupo eXeLearning.",
    "solo_privado": "Hola, {nombre}. Soy Karla bot, la asistente de eXeLearning. En el grupo no puedo contestarte, pero por privado sí. Escríbeme aquí: https://t.me/{usuario}",
    "solo_privado_comando": "Hola, {nombre}. Soy Karla bot, la asistente de eXeLearning. Esto no funciona en el grupo, pero por privado sí. Ábrelo aquí: https://t.me/{usuario}?start={comando}",
    "solo_texto": "Por ahora solo entiendo mensajes escritos, capturas de pantalla, notas de voz y archivos .elpx. Escríbeme la pregunta, por favor.",
    "error": "Algo ha fallado al buscar. Prueba otra vez en un momento.",
    "cupo": "Has llegado a las {cupo} preguntas de hoy. Mañana podrás seguir.",
    "tope": "Este mes se ha agotado mi presupuesto. Volveré a responder el día 1.",
    "seguidas": "Me has hecho muchas preguntas seguidas y necesito un respiro. Vuelve a escribirme dentro de un rato y seguimos.",
    # Solo para Juanjo, en castellano.
    "aviso_freno": ("Aviso de Karla bot: hoy se han gastado {usd:.2f} USD, más del doble de lo que toca por día "
                    "para no pasar del tope del mes ({diario:.2f} USD). Hasta mañana, {cupo} preguntas por persona."),
    "aviso_80": ("Aviso de Karla bot: este mes se han gastado {usd:.2f} USD de los {tope:.0f} del tope "
                 "({n} preguntas)."),
    "nueva_incidencia": ("Karla bot ha abierto una incidencia en GitHub a petición de {autor}: «{titulo}»\n{url}"),
    "aviso_reserva": ("Aviso de Karla bot: este mes se han gastado {usd:.2f} USD. Desde ahora responde con "
                      "Claude Haiku, más barato, hasta el día 1."),
    "incidencia_vista": '📝 Este es el aviso de error que enviaría al equipo que desarrolla eXeLearning. Se publica como «incidencia» (issue, en inglés) en GitHub, la web donde el equipo apunta los fallos del programa para corregirlos. Es pública y va en inglés, la lengua del proyecto. No lleva tu nombre ni ningún dato tuyo: la envío yo, Karla bot. Sirve para avisar de errores del programa, no para resolver dudas de uso.\n\nRevísala y, si está bien, pulsa «Enviar al equipo». Si no la envías, no se publica nada.',
    "b_enviar": 'Enviar al equipo',
    # Para Juanjo solo (sin traducir: texto() cae en el castellano)
    "equipo_pregunta": "Equipo de eXeLearning: {nombre} (@{cuenta} en GitHub) ha aportado {n} cambios en los últimos seis meses. {grupo}\n\n¿Es del equipo? Si lo es, Karla tomará sus respuestas en el grupo como oficiales.",
    "equipo_parecido": "En el grupo parece ser «{autor}»{usuario}.",
    "equipo_sin_parecido": "No he encontrado a nadie parecido en el grupo: si es del equipo, Karla sabrá su nombre, pero no podrá marcar sus mensajes.",
    "b_es_equipo": "Es del equipo",
    "b_no_equipo": "No lo es",
    "equipo_si": "Hecho: {nombre} queda en el equipo.",
    "equipo_no": "Hecho: {nombre} no es del equipo y no volveré a preguntar.",
    "equipo_ya_no": "Eso ya está decidido.",
    "b_no_enviar": 'No enviar',
    "incidencia_abierta": 'Enviada. Puedes seguirla en este enlace, sin necesidad de cuenta, para ver qué responde el equipo y si lo corrige: {url}',
    "incidencia_cancelada": 'De acuerdo, no he enviado nada.',
    "incidencia_caducada": 'Este borrador ya no está disponible. Si quieres avisar del error, vuelve a contármelo.',
    "sustituido": 'Ese borrador ya no es el último: te he preparado otro después. Usa los botones del último mensaje.',
    "incidencia_tope": 'Hoy ya se han enviado {n} avisos de error al equipo, el máximo de un día. Prueba mañana o cuéntalo en el grupo eXeLearning.',
    "incidencia_error": 'No he podido enviar el aviso. Prueba más tarde o cuéntalo en el grupo eXeLearning.',
    "valoracion_si": "¡Gracias!",
    "valoracion_no": "Gracias. Guardo la pregunta, sin nada tuyo, para mejorar.",
    "valoracion_antigua": "Gracias.",
    "escuchando": "Te escucho. Tardo unos segundos en pasar el audio a texto.",
    "entendido": "He entendido: «{texto}»",
    "audio_largo": "El audio dura más de {minutos} minutos. Mándame uno más corto o escríbeme la duda.",
    "sin_voz": "Ahora mismo no puedo escuchar audios. Escríbeme la pregunta, por favor.",
    "audio_vacio": "No he entendido nada en el audio. Prueba otra vez o escríbeme la pregunta.",
    "seguir_pregunta": "¿Quieres que te avise aquí cuando el equipo responda o cierre el aviso? Para eso guardo tu cuenta junto al número del aviso hasta que se cierre.",
    "b_si_avisar": "Sí, avísame",
    "b_no_avisar": "No hace falta",
    "seguir_si": "De acuerdo: te avisaré aquí de cada respuesta del equipo y de cuándo se cierre.",
    "seguir_no": "De acuerdo, no te avisaré. Puedes seguirlo en el enlace cuando quieras.",
    "incidencia_novedad": "Novedad en tu aviso «{titulo}». {autor} ha escrito:\n\n{texto}\n\n{url}",
    "incidencia_cerrada": "El equipo ha cerrado tu aviso «{titulo}» ({motivo}). Dejo de seguirlo. {url}",
    "archivo_grande": "Ese archivo pesa más de 20 MB y Telegram no deja a los bots descargarlo. Cuéntame la duda con palabras o una captura.",
    "respuesta_vacia": "No he encontrado nada que responda a eso. Prueba a decirlo con otras palabras o a concretar más.",
    # Preguntar en el grupo (ADR 0023)
    "b_preguntar_grupo": "Preguntar en el grupo",
    "vista_pregunta": "Así la publicaré en el grupo, con tu nombre. Si alguien le responde allí, te lo haré llegar aquí durante {dias} días; para eso guardo tu cuenta junto a ese mensaje durante ese tiempo.",
    "vista_pregunta_fotos": "Las imágenes que me enviaste irán con ella.",
    "b_publicar_en": "Publicar en {grupo}",
    "pregunta_caducada": "Esa pregunta ya no se puede llevar al grupo. Si quieres, vuelve a hacérmela.",
    "pregunta_no": "De acuerdo, no la publico.",
    "pregunta_tope": "Hoy ya has llevado {n} preguntas al grupo, el máximo por día. Mañana podrás llevar más.",
    "pregunta_error": "No he podido publicarla en el grupo. Prueba otra vez dentro de un rato.",
    "pregunta_publicada": "Publicada en {grupo}: {enlace}\nSi alguien le responde allí, te lo haré llegar aquí durante {dias} días. Si cambias de idea, puedes quitarla con el botón de abajo durante las próximas 48 horas.",
    "b_quitar_pregunta": "Quitarla del grupo",
    "pregunta_quitada": "Quitada del grupo.",
    "no_quitar_pregunta": "Ya no puedo quitarla: Telegram solo deja borrar los mensajes durante 48 horas. Pídeselo a quien administra el grupo.",
    "respuesta_en_grupo": "{quien} ha respondido en el grupo a la pregunta que llevé por ti:\n«{extracto}»\n{enlace}",
    "solo_imagenes": "Solo ha enviado imágenes.",
    "pregunta_en_grupo": "<b>Pregunta de {autor} que no he sabido responder</b>\nNo he encontrado la respuesta ni en la documentación de eXeLearning ni en lo hablado en el grupo. ¿Alguien puede ayudar?\n<blockquote>{pregunta}</blockquote>\nSi sabes la respuesta, contesta aquí en el grupo respondiendo a este mensaje, y se la haré llegar a {nombre} por privado.",
    "b_cancelar": "Cancelar",
    "codigo": "Soy software libre (AGPL v3), versión {version}: el código está en https://github.com/jjdeharo/bot-chatgpt-ia-edu.",
}

CA = {
    "inicio": ("Hola, soc la Karla, una assistent per resoldre dubtes sobre [eXeLearning](https://exelearning.net). "
               "No soc una persona: soc un programa que fa servir intel·ligència artificial."),
    "ayuda_preguntar": ("🔎 Pregunta'm el que vulguis. Escriu-me el teu dubte amb les teves paraules: com es fa "
                        "una cosa, per què el programa es comporta d'una manera o com publicar el teu recurs a "
                        "Moodle, Procomún o una altra plataforma. Cerco al manual, a la documentació del programa i "
                        "dels seus complements i en el que s'ha parlat al grup [eXeLearning](https://t.me/exelearning), "
                        "i et dic d'on surt cada cosa. Em pots enviar una captura de pantalla o el fitxer .elpx del teu projecte amb el dubte, o explicar-me'l en una nota de veu. Si el que "
                        "expliques és una errada del programa, busco si ja està avisada i, si vols, preparo l'avís per a "
                        "l'equip que el desenvolupa."),
    "ayuda_final": ("ℹ️ Tingues en compte: em puc equivocar, així que comprova el que sigui important al missatge "
                    "o al document que cito. El que m'escrius es processa amb Claude, una IA d'Anthropic, en "
                    "servidors dels Estats Units. Només guardo les preguntes que no aconsegueixo "
                    "respondre o que marques amb 👎, sense el teu nom ni el teu compte, per millorar, i les esborro als 60 dies. Responc als membres del grup eXeLearning. "
                    "M'ha creat @jjdeharo."),
    "traduccion": "Traducció automàtica feta amb IA, sense revisió professional.",
    "perfil": ("Soc la Karla, una assistent per resoldre dubtes sobre eXeLearning. Cerco al seu manual, a la "
               "documentació del programa i dels seus complements i a les converses del grup de Telegram "
               "eXeLearning, i dic d'on surt cada resposta. No soc una persona: soc un programa que fa servir "
               "Claude, una IA d'Anthropic. Creada per @jjdeharo."),
    "perfil_corto": "Resolc dubtes sobre eXeLearning amb el seu manual, la documentació i el que s'ha parlat al grup.",
    "c_ayuda": "Com funciono",
    "no_miembro": "Ho sento, només puc respondre a qui forma part del grup eXeLearning (https://t.me/exelearning). Entrar-hi és lliure: uneix-t'hi i torna'm a escriure.",
    "no_autorizado": "Encara estic en proves. Aviat estaré oberta al grup eXeLearning.",
    "solo_privado": "Hola, {nombre}. Soc la Karla bot, l'assistent d'eXeLearning. Al grup no et puc respondre, però en privat sí. Escriu-me aquí: https://t.me/{usuario}",
    "solo_privado_comando": "Hola, {nombre}. Soc la Karla bot, l'assistent d'eXeLearning. Això no funciona al grup, però en privat sí. Obre-ho aquí: https://t.me/{usuario}?start={comando}",
    "solo_texto": "De moment només entenc missatges escrits, captures de pantalla, notes de veu i fitxers .elpx. Escriu-me la pregunta, si us plau.",
    "error": "Alguna cosa ha fallat en cercar. Torna-ho a provar d'aquí a una estona.",
    "cupo": "Has arribat a les {cupo} preguntes d'avui. Demà podràs continuar.",
    "tope": "Aquest mes s'ha esgotat el meu pressupost. Tornaré a respondre el dia 1.",
    "seguidas": "M'has fet moltes preguntes seguides i necessito un respir. Torna'm a escriure d'aquí a una estona i continuem.",
    "incidencia_vista": "📝 Aquest és l'avís d'error que enviaria a l'equip que desenvolupa eXeLearning. Es publica com a «incidència» (issue, en anglès) a GitHub, el web on l'equip anota les errades del programa per corregir-les. És pública i va en anglès, la llengua del projecte. No porta el teu nom ni cap dada teva: l'envio jo, Karla bot. Serveix per avisar d'errors del programa, no per resoldre dubtes d'ús.\n\nRevisa-la i, si està bé, prem «Enviar a l'equip». Si no l'envies, no es publica res.",
    "b_enviar": "Enviar a l'equip",
    "b_no_enviar": 'No enviar',
    "incidencia_abierta": "Enviada. La pots seguir en aquest enllaç, sense necessitat de compte, per veure què respon l'equip i si ho corregeix: {url}",
    "incidencia_cancelada": "D'acord, no he enviat res.",
    "incidencia_caducada": "Aquest esborrany ja no està disponible. Si vols avisar de l'error, torna-m'ho a explicar.",
    "sustituido": "Aquest esborrany ja no és l'últim: n'he preparat un altre després. Fes servir els botons de l'últim missatge.",
    "incidencia_tope": "Avui ja s'han enviat {n} avisos d'error a l'equip, el màxim d'un dia. Prova-ho demà o explica-ho al grup eXeLearning.",
    "incidencia_error": "No he pogut enviar l'avís. Prova-ho més tard o explica-ho al grup eXeLearning.",
    "valoracion_si": "Gràcies!",
    "valoracion_no": "Gràcies. Guardo la pregunta, sense res teu, per millorar.",
    "valoracion_antigua": "Gràcies.",
    "escuchando": "T'escolto. Trigo uns segons a passar l'àudio a text.",
    "entendido": "He entès: «{texto}»",
    "audio_largo": "L'àudio dura més de {minutos} minuts. Envia-me'n un de més curt o escriu-me el dubte.",
    "sin_voz": "Ara mateix no puc escoltar àudios. Escriu-me la pregunta, si us plau.",
    "audio_vacio": "No he entès res a l'àudio. Torna-ho a provar o escriu-me la pregunta.",
    "seguir_pregunta": "Vols que t'avisi aquí quan l'equip respongui o tanqui l'avís? Per fer-ho guardo el teu compte amb el número de l'avís fins que es tanqui.",
    "b_si_avisar": "Sí, avisa'm",
    "b_no_avisar": "No cal",
    "seguir_si": "D'acord: t'avisaré aquí de cada resposta de l'equip i de quan es tanqui.",
    "seguir_no": "D'acord, no t'avisaré. Pots seguir-lo a l'enllaç quan vulguis.",
    "incidencia_novedad": "Novetat al teu avís «{titulo}». {autor} ha escrit:\n\n{texto}\n\n{url}",
    "incidencia_cerrada": "L'equip ha tancat el teu avís «{titulo}» ({motivo}). Deixo de seguir-lo. {url}",
    "archivo_grande": "Aquest fitxer pesa més de 20 MB i Telegram no deixa als bots baixar-lo. Explica'm el dubte amb paraules o una captura.",
    "respuesta_vacia": "No he trobat res que respongui a això. Prova a dir-ho amb altres paraules o a concretar més.",
    # Preguntar en el grupo (ADR 0023)
    "b_preguntar_grupo": "Preguntar al grup",
    "vista_pregunta": "Així la publicaré al grup, amb el teu nom. Si algú hi respon, t'ho faré arribar aquí durant {dias} dies; per això guardo el teu compte amb aquest missatge durant aquest temps.",
    "vista_pregunta_fotos": "Les imatges que em vas enviar hi aniran.",
    "b_publicar_en": "Publicar a {grupo}",
    "pregunta_caducada": "Aquesta pregunta ja no es pot portar al grup. Si vols, torna-me-la a fer.",
    "pregunta_no": "D'acord, no la publico.",
    "pregunta_tope": "Avui ja has portat {n} preguntes al grup, el màxim per dia. Demà en podràs portar més.",
    "pregunta_error": "No l'he pogut publicar al grup. Torna-ho a provar d'aquí a una estona.",
    "pregunta_publicada": "Publicada a {grupo}: {enlace}\nSi algú hi respon, t'ho faré arribar aquí durant {dias} dies. Si canvies d'idea, la pots treure amb el botó de sota durant les properes 48 hores.",
    "b_quitar_pregunta": "Treure-la del grup",
    "pregunta_quitada": "Treta del grup.",
    "no_quitar_pregunta": "Ja no la puc treure: Telegram només deixa esborrar els missatges durant 48 hores. Demana-ho a qui administra el grup.",
    "respuesta_en_grupo": "{quien} ha respost al grup la pregunta que hi vaig portar per tu:\n«{extracto}»\n{enlace}",
    "b_cancelar": "Cancel·lar",
    "codigo": "Soc programari lliure (AGPL v3), versió {version}: el codi és a https://github.com/jjdeharo/bot-chatgpt-ia-edu.",
}

GL = {
    "inicio": ("Ola, son Karla, unha asistente para resolver dúbidas sobre [eXeLearning](https://exelearning.net). "
               "Non son unha persoa: son un programa que usa intelixencia artificial."),
    "ayuda_preguntar": ("🔎 Pregúntame o que queiras. Escríbeme a túa dúbida coas túas palabras: como se fai "
                        "algo, por que o programa se comporta dunha maneira ou como publicar o teu recurso en "
                        "Moodle, Procomún ou outra plataforma. Busco no manual, na documentación do programa e dos "
                        "seus complementos e no que se falou no grupo [eXeLearning](https://t.me/exelearning), e "
                        "dígoche de onde sae cada cousa. Podes mandarme unha captura de pantalla ou o ficheiro .elpx do teu proxecto coa dúbida, ou contarma nunha nota de voz. Se o que "
                        "contas é un fallo do programa, busco se xa está avisado e, se queres, preparo o aviso para o "
                        "equipo que o desenvolve."),
    "ayuda_final": ("ℹ️ Ten en conta: podo equivocarme, así que comproba o importante na mensaxe ou no documento "
                    "que cito. O que me escribes procésase con Claude, unha IA de Anthropic, en servidores dos "
                    "Estados Unidos. Só gardo as preguntas que non consigo responder ou que marcas con 👎, sen o teu nome nin a túa conta, para "
                    "mellorar, e bórroas aos 60 días. Respondo aos membros do grupo eXeLearning. Creoume @jjdeharo."),
    "traduccion": "Tradución automática feita con IA, sen revisión profesional.",
    "perfil": ("Son Karla, unha asistente para resolver dúbidas sobre eXeLearning. Busco no seu manual, na "
               "documentación do programa e dos seus complementos e nas conversas do grupo de Telegram "
               "eXeLearning, e digo de onde sae cada resposta. Non son unha persoa: son un programa que usa "
               "Claude, unha IA de Anthropic. Creada por @jjdeharo."),
    "perfil_corto": "Resolvo dúbidas sobre eXeLearning co seu manual, a súa documentación e o falado no grupo.",
    "c_ayuda": "Como funciono",
    "no_miembro": "Síntoo, só podo responder a quen forma parte do grupo eXeLearning (https://t.me/exelearning). Entrar é libre: únete e volve escribirme.",
    "no_autorizado": "Aínda estou en probas. Pronto estarei aberta ao grupo eXeLearning.",
    "solo_privado": "Ola, {nombre}. Son Karla bot, a asistente de eXeLearning. No grupo non podo contestarche, pero en privado si. Escríbeme aquí: https://t.me/{usuario}",
    "solo_privado_comando": "Ola, {nombre}. Son Karla bot, a asistente de eXeLearning. Isto non funciona no grupo, pero en privado si. Ábreo aquí: https://t.me/{usuario}?start={comando}",
    "solo_texto": "Polo de agora só entendo mensaxes escritas, capturas de pantalla, notas de voz e ficheiros .elpx. Escríbeme a pregunta, por favor.",
    "error": "Algo fallou ao buscar. Proba outra vez nun momento.",
    "cupo": "Chegaches ás {cupo} preguntas de hoxe. Mañá poderás seguir.",
    "tope": "Este mes esgotouse o meu orzamento. Volverei responder o día 1.",
    "seguidas": "Fixéchesme moitas preguntas seguidas e necesito un respiro. Volve escribirme dentro dun anaco e seguimos.",
    "incidencia_vista": '📝 Este é o aviso de erro que lle enviaría ao equipo que desenvolve eXeLearning. Publícase como «incidencia» (issue, en inglés) en GitHub, a web onde o equipo anota os fallos do programa para corrixilos. É pública e vai en inglés, a lingua do proxecto. Non leva o teu nome nin ningún dato teu: envíoa eu, Karla bot. Serve para avisar de erros do programa, non para resolver dúbidas de uso.\n\nRevísaa e, se está ben, preme «Enviar ao equipo». Se non a envías, non se publica nada.',
    "b_enviar": 'Enviar ao equipo',
    "b_no_enviar": 'Non enviar',
    "incidencia_abierta": 'Enviada. Podes seguila nesta ligazón, sen necesidade de conta, para ver que responde o equipo e se o corrixe: {url}',
    "incidencia_cancelada": 'De acordo, non enviei nada.',
    "incidencia_caducada": 'Este borrador xa non está dispoñible. Se queres avisar do erro, volve contarmo.',
    "sustituido": 'Ese borrador xa non é o último: preparei outro despois. Usa os botóns da última mensaxe.',
    "incidencia_tope": 'Hoxe xa se enviaron {n} avisos de erro ao equipo, o máximo dun día. Proba mañá ou cóntao no grupo eXeLearning.',
    "incidencia_error": 'Non puiden enviar o aviso. Proba máis tarde ou cóntao no grupo eXeLearning.',
    "valoracion_si": "Grazas!",
    "valoracion_no": "Grazas. Gardo a pregunta, sen nada teu, para mellorar.",
    "valoracion_antigua": "Grazas.",
    "escuchando": "Escóitote. Tardo uns segundos en pasar o audio a texto.",
    "entendido": "Entendín: «{texto}»",
    "audio_largo": "O audio dura máis de {minutos} minutos. Mándame un máis curto ou escríbeme a dúbida.",
    "sin_voz": "Agora mesmo non podo escoitar audios. Escríbeme a pregunta, por favor.",
    "audio_vacio": "Non entendín nada no audio. Proba outra vez ou escríbeme a pregunta.",
    "seguir_pregunta": "Queres que che avise aquí cando o equipo responda ou peche o aviso? Para iso gardo a túa conta xunto ao número do aviso ata que se peche.",
    "b_si_avisar": "Si, avísame",
    "b_no_avisar": "Non fai falta",
    "seguir_si": "De acordo: avisareite aquí de cada resposta do equipo e de cando se peche.",
    "seguir_no": "De acordo, non che avisarei. Podes seguilo na ligazón cando queiras.",
    "incidencia_novedad": "Novidade no teu aviso «{titulo}». {autor} escribiu:\n\n{texto}\n\n{url}",
    "incidencia_cerrada": "O equipo pechou o teu aviso «{titulo}» ({motivo}). Deixo de seguilo. {url}",
    "archivo_grande": "Ese ficheiro pesa máis de 20 MB e Telegram non deixa aos bots descargalo. Cóntame a dúbida con palabras ou unha captura.",
    "respuesta_vacia": "Non atopei nada que responda a iso. Proba a dicilo con outras palabras ou a concretar máis.",
    # Preguntar en el grupo (ADR 0023)
    "b_preguntar_grupo": "Preguntar no grupo",
    "vista_pregunta": "Así a publicarei no grupo, co teu nome. Se alguén lle responde alí, fareicho chegar aquí durante {dias} días; para iso gardo a túa conta xunto a esa mensaxe durante ese tempo.",
    "vista_pregunta_fotos": "As imaxes que me enviaches irán con ela.",
    "b_publicar_en": "Publicar en {grupo}",
    "pregunta_caducada": "Esa pregunta xa non se pode levar ao grupo. Se queres, vólvema facer.",
    "pregunta_no": "De acordo, non a publico.",
    "pregunta_tope": "Hoxe xa levaches {n} preguntas ao grupo, o máximo por día. Mañá poderás levar máis.",
    "pregunta_error": "Non puiden publicala no grupo. Proba outra vez dentro dun anaco.",
    "pregunta_publicada": "Publicada en {grupo}: {enlace}\nSe alguén lle responde alí, fareicho chegar aquí durante {dias} días. Se cambias de idea, podes quitala co botón de abaixo durante as próximas 48 horas.",
    "b_quitar_pregunta": "Quitala do grupo",
    "pregunta_quitada": "Quitada do grupo.",
    "no_quitar_pregunta": "Xa non podo quitala: Telegram só deixa borrar as mensaxes durante 48 horas. Pídello a quen administra o grupo.",
    "respuesta_en_grupo": "{quien} respondeu no grupo á pregunta que levei por ti:\n«{extracto}»\n{enlace}",
    "b_cancelar": "Cancelar",
    "codigo": "Son software libre (AGPL v3), versión {version}: o código está en https://github.com/jjdeharo/bot-chatgpt-ia-edu.",
}

EU = {
    "inicio": ("Kaixo, Karla naiz, [eXeLearning](https://exelearning.net)-i buruzko zalantzak argitzeko "
               "laguntzailea. Ez naiz pertsona bat: adimen artifiziala erabiltzen duen programa bat naiz."),
    "ayuda_preguntar": ("🔎 Galdetu nahi duzuna. Idatzi zure zalantza zure hitzekin: zerbait nola egiten den, "
                        "programak zergatik jokatzen duen modu batean edo zure baliabidea Moodlen, Procomúnen edo "
                        "beste plataforma batean nola argitaratu. Eskuliburuan, programaren eta bere osagarrien "
                        "dokumentazioan eta [eXeLearning](https://t.me/exelearning) taldean hitz egindakoan "
                        "bilatzen dut, eta gauza bakoitza nondik datorren esaten dizut. Zalantzarekin batera pantaila-argazki "
                        "bat edo zure proiektuaren .elpx fitxategia bidal diezadakezu, edo ahots-ohar batean kontatu. Kontatzen duzuna programaren akats bat bada, jada jakinarazita dagoen "
                        "bilatzen dut eta, nahi baduzu, garatzen duen taldearentzako oharra prestatzen dut."),
    "ayuda_final": ("ℹ️ Kontuan izan: oker egon naiteke, beraz egiaztatu garrantzitsua aipatzen dudan mezuan edo "
                    "dokumentuan. Idazten didazuna Claude-rekin prozesatzen da, Anthropic-en IA bat, Estatu "
                    "Batuetako zerbitzarietan. Erantzun ezin ditudan galderak edo 👎 batekin markatzen dituzunak bakarrik gordetzen ditut, zure "
                    "izenik eta konturik gabe, hobetzeko, eta 60 egunera ezabatzen ditut. eXeLearning taldeko kideei erantzuten "
                    "diet. @jjdeharo-k sortu nau."),
    "traduccion": "IArekin egindako itzulpen automatikoa, berrikuspen profesionalik gabe.",
    "perfil": ("Karla naiz, eXeLearning-i buruzko zalantzak argitzeko laguntzailea. Bere eskuliburuan, "
               "programaren eta bere osagarrien dokumentazioan eta eXeLearning Telegram taldeko elkarrizketetan "
               "bilatzen dut, eta erantzun bakoitza nondik datorren esaten dut. Ez naiz pertsona bat: Claude "
               "erabiltzen duen programa bat naiz, Anthropic-en IA bat. @jjdeharo-k sortua."),
    "perfil_corto": "eXeLearning-i buruzko zalantzak argitzen ditut eskuliburuarekin, dokumentazioarekin eta taldean esandakoarekin.",
    "c_ayuda": "Nola funtzionatzen dudan",
    "no_miembro": "Sentitzen dut, eXeLearning taldeko kideei bakarrik erantzun diezaieket (https://t.me/exelearning). Sartzea librea da: batu zaitez eta idatzi berriro.",
    "no_autorizado": "Oraindik probetan nago. Laster eXeLearning taldearentzat irekita egongo naiz.",
    "solo_privado": "Kaixo, {nombre}. Karla bot naiz, eXeLearning-en laguntzailea. Taldean ezin dizut erantzun, baina pribatuan bai. Idatzi hemen: https://t.me/{usuario}",
    "solo_privado_comando": "Kaixo, {nombre}. Karla bot naiz, eXeLearning-en laguntzailea. Hau ez dabil taldean, baina pribatuan bai. Ireki hemen: https://t.me/{usuario}?start={comando}",
    "solo_texto": "Oraingoz idatzizko mezuak, pantaila-argazkiak, ahots-oharrak eta .elpx fitxategiak bakarrik ulertzen ditut. Idatzi galdera, mesedez.",
    "error": "Zerbait gaizki atera da bilatzean. Saiatu berriro une batean.",
    "cupo": "Gaurko {cupo} galderetara iritsi zara. Bihar jarraitu ahal izango duzu.",
    "tope": "Hilabete honetan nire aurrekontua agortu da. Hilaren 1ean erantzungo dut berriro.",
    "seguidas": "Galdera asko egin dizkidazu jarraian eta atseden pixka bat behar dut. Idatzi berriro pixka bat barru eta jarraituko dugu.",
    "incidencia_vista": '📝 Hau da eXeLearning garatzen duen taldeari bidaliko niokeen errore-oharra. GitHuben «intzidentzia» (issue, ingelesez) gisa argitaratzen da; taldeak programaren akatsak bertan idazten ditu, zuzentzeko. Publikoa da eta ingelesez doa, proiektuaren hizkuntzan. Ez darama zure izenik ezta zure daturik ere: nik bidaltzen dut, Karla bot-ek. Programaren erroreen berri emateko da, ez erabilerari buruzko zalantzak argitzeko.\n\nBerrikusi eta, ondo badago, sakatu «Taldeari bidali». Bidaltzen ez baduzu, ez da ezer argitaratzen.',
    "b_enviar": 'Taldeari bidali',
    "b_no_enviar": 'Ez bidali',
    "incidencia_abierta": 'Bidalita. Esteka honetan jarraitu dezakezu, konturik behar gabe, taldeak zer erantzuten duen eta zuzentzen duen ikusteko: {url}',
    "incidencia_cancelada": 'Ados, ez dut ezer bidali.',
    "incidencia_caducada": 'Zirriborro hau ez dago erabilgarri. Errorearen berri eman nahi baduzu, kontatu berriro.',
    "sustituido": 'Zirriborro hori ez da azkena: beste bat prestatu dut gero. Erabili azken mezuaren botoiak.',
    "incidencia_tope": 'Gaur dagoeneko {n} errore-ohar bidali zaizkio taldeari, egun bateko gehienekoa. Saiatu bihar edo kontatu eXeLearning taldean.',
    "incidencia_error": 'Ezin izan dut oharra bidali. Saiatu geroago edo kontatu eXeLearning taldean.',
    "valoracion_si": "Eskerrik asko!",
    "valoracion_no": "Eskerrik asko. Galdera gordetzen dut, zure daturik gabe, hobetzeko.",
    "valoracion_antigua": "Eskerrik asko.",
    "escuchando": "Entzuten dizut. Segundo batzuk behar ditut audioa testu bihurtzeko.",
    "entendido": "Hau ulertu dut: «{texto}»",
    "audio_largo": "Audioak {minutos} minutu baino gehiago irauten du. Bidali laburrago bat edo idatzi zalantza.",
    "sin_voz": "Oraintxe ezin ditut audioak entzun. Idatzi galdera, mesedez.",
    "audio_vacio": "Ez dut ezer ulertu audioan. Saiatu berriro edo idatzi galdera.",
    "seguir_pregunta": "Nahi duzu taldeak erantzun edo oharra ixten duenean hemen abisatzea? Horretarako zure kontua oharraren zenbakiarekin batera gordetzen dut, itxi arte.",
    "b_si_avisar": "Bai, abisatu",
    "b_no_avisar": "Ez da beharrezkoa",
    "seguir_si": "Ados: taldearen erantzun bakoitzaren eta ixten denaren berri emango dizut hemen.",
    "seguir_no": "Ados, ez dizut abisatuko. Estekan jarraitu dezakezu nahi duzunean.",
    "incidencia_novedad": "Berritasuna zure «{titulo}» oharrean. {autor}(e)k idatzi du:\n\n{texto}\n\n{url}",
    "incidencia_cerrada": "Taldeak zure «{titulo}» oharra itxi du ({motivo}). Jarraitzeari uzten diot. {url}",
    "archivo_grande": "Fitxategi horrek 20 MB baino gehiago pisatzen du eta Telegramek ez die botei deskargatzen uzten. Kontatu zalantza hitzekin edo pantaila-argazki batekin.",
    "respuesta_vacia": "Ez dut horri erantzuten dion ezer aurkitu. Saiatu beste hitz batzuekin esaten edo gehiago zehazten.",
    # Preguntar en el grupo (ADR 0023)
    "b_preguntar_grupo": "Taldean galdetu",
    "vista_pregunta": "Honela argitaratuko dut taldean, zure izenarekin. Norbaitek han erantzuten badio, hemen jakinaraziko dizut {dias} egunez; horretarako, zure kontua mezu horrekin batera gordetzen dut denbora horretan.",
    "vista_pregunta_fotos": "Bidali dizkidazun irudiak ere joango dira.",
    "b_publicar_en": "Argitaratu: {grupo}",
    "pregunta_caducada": "Galdera hori ezin da jada taldera eraman. Nahi baduzu, egin iezadazu berriro.",
    "pregunta_no": "Ados, ez dut argitaratzen.",
    "pregunta_tope": "Gaur dagoeneko {n} galdera eraman dituzu taldera, eguneko gehienekoa. Bihar gehiago eraman ahal izango dituzu.",
    "pregunta_error": "Ezin izan dut taldean argitaratu. Saiatu berriro pixka bat barru.",
    "pregunta_publicada": "{grupo} taldean argitaratua: {enlace}\nNorbaitek han erantzuten badio, hemen jakinaraziko dizut {dias} egunez. Iritziz aldatzen baduzu, beheko botoiarekin ken dezakezu hurrengo 48 orduetan.",
    "b_quitar_pregunta": "Taldetik kendu",
    "pregunta_quitada": "Taldetik kendua.",
    "no_quitar_pregunta": "Ezin dut jada kendu: Telegramek 48 orduz bakarrik uzten du mezuak ezabatzen. Eskatu taldearen administratzaileari.",
    "respuesta_en_grupo": "{quien}(e)k taldean erantzun dio zure izenean eraman nuen galderari:\n«{extracto}»\n{enlace}",
    "b_cancelar": "Utzi",
    "codigo": "Software librea naiz (AGPL v3), {version} bertsioa: kodea hemen dago: https://github.com/jjdeharo/bot-chatgpt-ia-edu.",
}

EN = {
    "inicio": ("Hi, I'm Karla, an assistant for questions about [eXeLearning](https://exelearning.net). "
               "I'm not a person: I'm a program that uses artificial intelligence."),
    "ayuda_preguntar": ("🔎 Ask me anything. Tell me your question in your own words: how to do something, why "
                        "the program behaves in a certain way, or how to publish your resource on Moodle, Procomún "
                        "or another platform. I search the manual, the documentation of the program and its add-ons, "
                        "and what has been said in the [eXeLearning](https://t.me/exelearning) group, and I tell you "
                        "where each answer comes from. You can send me a screenshot or your project's .elpx file along with your question, or tell me in a voice note. If what you "
                        "describe is a bug in the program, I check whether it has already been reported and, if you want, "
                        "I prepare the report for the team that develops it."),
    "ayuda_final": ("ℹ️ Please note: I can make mistakes, so check anything important in the message or document "
                    "I cite. What you write to me is processed with Claude, an AI by Anthropic, on servers in the "
                    "United States. I only keep the questions I can't answer or that you mark with 👎, without your name or account, to improve, and I delete "
                    "them after 60 days. I answer members of the eXeLearning group. Created by @jjdeharo."),
    "traduccion": "Automatic translation made with AI, without professional review.",
    "perfil": ("I'm Karla, an assistant for questions about eXeLearning. I search its manual, the documentation of "
               "the program and its add-ons, and the conversations of the eXeLearning Telegram group, and I say "
               "where each answer comes from. I'm not a person: I'm a program that uses Claude, an AI by Anthropic. "
               "Created by @jjdeharo."),
    "perfil_corto": "I answer questions about eXeLearning with its manual, its documentation and the group's conversations.",
    "c_ayuda": "How I work",
    "no_miembro": "Sorry, I can only answer people who belong to the eXeLearning group (https://t.me/exelearning). Joining is free: join and write to me again.",
    "no_autorizado": "I'm still being tested. I'll soon be open to the eXeLearning group.",
    "solo_privado": "Hi, {nombre}. I'm Karla bot, the eXeLearning assistant. I can't answer you in the group, but I can in private. Write to me here: https://t.me/{usuario}",
    "solo_privado_comando": "Hi, {nombre}. I'm Karla bot, the eXeLearning assistant. This doesn't work in the group, but it does in private. Open it here: https://t.me/{usuario}?start={comando}",
    "solo_texto": "For now I only understand written messages, screenshots, voice notes and .elpx files. Please write your question.",
    "error": "Something went wrong while searching. Please try again in a moment.",
    "cupo": "You've reached today's {cupo} questions. You can continue tomorrow.",
    "tope": "My budget for this month has run out. I'll answer again on the 1st.",
    "seguidas": "You've asked me a lot of questions in a row and I need a breather. Write to me again in a little while and we'll carry on.",
    "incidencia_vista": "📝 This is the bug report I would send to the team that develops eXeLearning. It is published as an issue on GitHub, the site where the team keeps track of the program's bugs in order to fix them. It is public and written in English, the project's language. It does not include your name or any of your details: I send it, Karla bot. It is for reporting bugs in the program, not for usage questions.\n\nReview it and, if it looks right, tap «Send to the team». If you don't send it, nothing is published.",
    "b_enviar": 'Send to the team',
    "b_no_enviar": "Don't send",
    "incidencia_abierta": "Sent. You can follow it at this link, no account needed, to see the team's reply and whether they fix it: {url}",
    "incidencia_cancelada": "All right, I haven't sent anything.",
    "incidencia_caducada": 'This draft is no longer available. If you want to report the bug, tell me about it again.',
    "sustituido": 'That draft is no longer the latest one: I prepared another after it. Use the buttons on the last message.',
    "incidencia_tope": '{n} bug reports have already been sent to the team today, the daily maximum. Try again tomorrow or tell the eXeLearning group.',
    "incidencia_error": "I couldn't send the report. Try again later or tell the eXeLearning group.",
    "valoracion_si": "Thanks!",
    "valoracion_no": "Thanks. I'm keeping the question, with nothing about you, to improve.",
    "valoracion_antigua": "Thanks.",
    "escuchando": "I'm listening. It takes me a few seconds to turn the audio into text.",
    "entendido": "I understood: «{texto}»",
    "audio_largo": "The audio is longer than {minutos} minutes. Send me a shorter one or write your question.",
    "sin_voz": "Right now I can't listen to audio. Please write your question.",
    "audio_vacio": "I couldn't make out anything in the audio. Try again or write your question.",
    "seguir_pregunta": "Do you want me to let you know here when the team replies or closes the report? To do that I keep your account next to the report number until it is closed.",
    "b_si_avisar": "Yes, let me know",
    "b_no_avisar": "No need",
    "seguir_si": "All right: I'll let you know here about each reply from the team and when it is closed.",
    "seguir_no": "All right, I won't notify you. You can follow it at the link whenever you want.",
    "incidencia_novedad": "News on your report «{titulo}». {autor} wrote:\n\n{texto}\n\n{url}",
    "incidencia_cerrada": "The team has closed your report «{titulo}» ({motivo}). I stop following it. {url}",
    "archivo_grande": "That file is over 20 MB and Telegram doesn't let bots download it. Tell me the question in words or with a screenshot.",
    "respuesta_vacia": "I haven't found anything that answers that. Try saying it in other words or being more specific.",
    # Preguntar en el grupo (ADR 0023)
    "b_preguntar_grupo": "Ask the group",
    "vista_pregunta": "This is how I'll post it in the group, with your name. If someone replies there, I'll pass it on to you here for {dias} days; for that I keep your account with that message during that time.",
    "vista_pregunta_fotos": "The images you sent me will go with it.",
    "b_publicar_en": "Post in {grupo}",
    "pregunta_caducada": "That question can no longer be taken to the group. Ask me again if you like.",
    "pregunta_no": "OK, I won't post it.",
    "pregunta_tope": "You have already taken {n} questions to the group today, the daily maximum. You can take more tomorrow.",
    "pregunta_error": "I couldn't post it in the group. Try again in a while.",
    "pregunta_publicada": "Posted in {grupo}: {enlace}\nIf someone replies there, I'll pass it on to you here for {dias} days. If you change your mind, you can remove it with the button below for the next 48 hours.",
    "b_quitar_pregunta": "Remove it from the group",
    "pregunta_quitada": "Removed from the group.",
    "no_quitar_pregunta": "I can no longer remove it: Telegram only allows deleting messages for 48 hours. Ask the group's administrators.",
    "respuesta_en_grupo": "{quien} has replied in the group to the question I took there for you:\n«{extracto}»\n{enlace}",
    "b_cancelar": "Cancel",
    "codigo": "I am free software (AGPL v3), version {version}: the code is at https://github.com/jjdeharo/bot-chatgpt-ia-edu.",
}

TEXTOS = {"es": ES, "ca": CA, "gl": GL, "eu": EU, "en": EN}


def texto(lengua: str, clave: str, **datos) -> str:
    t = TEXTOS.get(lengua, ES).get(clave) or ES[clave]
    return t.format(**datos) if datos else t
