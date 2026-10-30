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
                        "y te digo de dónde sale cada cosa."),
    "ayuda_final": ("ℹ️ Ten en cuenta: puedo equivocarme, así que comprueba lo importante en el mensaje o el "
                    "documento que cito. Lo que me escribes se procesa con Claude, una IA de Anthropic, en "
                    "servidores de Estados Unidos. Solo guardo, de forma anónima, las preguntas que no consigo "
                    "responder, para mejorar, y las borro a los 60 días. Respondo a los miembros del grupo "
                    "eXeLearning. Me ha creado @jjdeharo."),
    "traduccion": "",
    "perfil": ("Soy Karla, una asistente para resolver dudas sobre eXeLearning. Busco en su manual, en la "
               "documentación del programa y de sus complementos y en las conversaciones del grupo de Telegram "
               "eXeLearning, y digo de dónde sale cada respuesta. No soy una persona: soy un programa que usa "
               "Claude, una IA de Anthropic. Creada por @jjdeharo."),
    "perfil_corto": "Resuelvo dudas sobre eXeLearning con su manual, su documentación y lo hablado en el grupo.",
    "c_ayuda": "Cómo funciono",
    "no_miembro": ("Solo respondo a los miembros del grupo eXeLearning (https://t.me/exelearning). Entrar es "
                   "libre: únete y vuelve a escribirme."),
    "no_autorizado": "Todavía estoy en pruebas. Pronto estaré abierta al grupo eXeLearning.",
    "solo_privado": "Solo respondo por privado: escríbeme en https://t.me/{usuario}",
    "solo_texto": "Escríbeme la pregunta en texto.",
    "error": "Algo ha fallado al buscar. Prueba otra vez en un momento.",
    "cupo": "Has llegado a las {cupo} preguntas de hoy. Mañana podrás seguir.",
    "tope": "Este mes se ha agotado mi presupuesto. Volveré a responder el día 1.",
    "seguidas": "Me has hecho muchas consultas seguidas. Sigue dentro de un rato.",
    # Solo para Juanjo, en castellano.
    "aviso_freno": ("Aviso de Karla bot: hoy se han gastado {usd:.2f} USD, más del doble de lo que toca por día "
                    "para no pasar del tope del mes ({diario:.2f} USD). Hasta mañana, {cupo} preguntas por persona."),
    "aviso_80": ("Aviso de Karla bot: este mes se han gastado {usd:.2f} USD de los {tope:.0f} del tope "
                 "({n} preguntas)."),
    "aviso_reserva": ("Aviso de Karla bot: este mes se han gastado {usd:.2f} USD. Desde ahora responde con "
                      "Claude Haiku, más barato, hasta el día 1."),
    "incidencia_vista": '📝 Este es el aviso de error que enviaría al equipo que desarrolla eXeLearning. Se publica como «incidencia» (issue, en inglés) en GitHub, la web donde el equipo apunta los fallos del programa para corregirlos. Es pública y va en inglés, la lengua del proyecto. No lleva tu nombre ni ningún dato tuyo: la envío yo, Karla bot. Sirve para avisar de errores del programa, no para resolver dudas de uso.\n\nRevísala y, si está bien, pulsa «Enviar al equipo». Si no la envías, no se publica nada.',
    "b_enviar": 'Enviar al equipo',
    "b_no_enviar": 'No enviar',
    "incidencia_abierta": 'Enviada. Puedes seguirla en este enlace, sin necesidad de cuenta, para ver qué responde el equipo y si lo corrige: {url}',
    "incidencia_cancelada": 'De acuerdo, no he enviado nada.',
    "incidencia_caducada": 'Este borrador ya no está disponible. Si quieres avisar del error, vuelve a contármelo.',
    "incidencia_tope": 'Hoy ya se han enviado {n} avisos de error al equipo, el máximo de un día. Prueba mañana o cuéntalo en el grupo eXeLearning.',
    "incidencia_error": 'No he podido enviar el aviso. Prueba más tarde o cuéntalo en el grupo eXeLearning.',
}

CA = {
    "inicio": ("Hola, soc la Karla, una assistent per resoldre dubtes sobre [eXeLearning](https://exelearning.net). "
               "No soc una persona: soc un programa que fa servir intel·ligència artificial."),
    "ayuda_preguntar": ("🔎 Pregunta'm el que vulguis. Escriu-me el teu dubte amb les teves paraules: com es fa "
                        "una cosa, per què el programa es comporta d'una manera o com publicar el teu recurs a "
                        "Moodle, Procomún o una altra plataforma. Cerco al manual, a la documentació del programa i "
                        "dels seus complements i en el que s'ha parlat al grup [eXeLearning](https://t.me/exelearning), "
                        "i et dic d'on surt cada cosa."),
    "ayuda_final": ("ℹ️ Tingues en compte: em puc equivocar, així que comprova el que sigui important al missatge "
                    "o al document que cito. El que m'escrius es processa amb Claude, una IA d'Anthropic, en "
                    "servidors dels Estats Units. Només guardo, de forma anònima, les preguntes que no aconsegueixo "
                    "respondre, per millorar, i les esborro als 60 dies. Responc als membres del grup eXeLearning. "
                    "M'ha creat @jjdeharo."),
    "traduccion": "Traducció automàtica feta amb IA, sense revisió professional.",
    "perfil": ("Soc la Karla, una assistent per resoldre dubtes sobre eXeLearning. Cerco al seu manual, a la "
               "documentació del programa i dels seus complements i a les converses del grup de Telegram "
               "eXeLearning, i dic d'on surt cada resposta. No soc una persona: soc un programa que fa servir "
               "Claude, una IA d'Anthropic. Creada per @jjdeharo."),
    "perfil_corto": "Resolc dubtes sobre eXeLearning amb el seu manual, la documentació i el que s'ha parlat al grup.",
    "c_ayuda": "Com funciono",
    "no_miembro": ("Només responc als membres del grup eXeLearning (https://t.me/exelearning). Entrar-hi és "
                   "lliure: uneix-t'hi i torna'm a escriure."),
    "no_autorizado": "Encara estic en proves. Aviat estaré oberta al grup eXeLearning.",
    "solo_privado": "Només responc en privat: escriu-me a https://t.me/{usuario}",
    "solo_texto": "Escriu-me la pregunta en text.",
    "error": "Alguna cosa ha fallat en cercar. Torna-ho a provar d'aquí a una estona.",
    "cupo": "Has arribat a les {cupo} preguntes d'avui. Demà podràs continuar.",
    "tope": "Aquest mes s'ha esgotat el meu pressupost. Tornaré a respondre el dia 1.",
    "seguidas": "M'has fet moltes consultes seguides. Continua d'aquí a una estona.",
    "incidencia_vista": "📝 Aquest és l'avís d'error que enviaria a l'equip que desenvolupa eXeLearning. Es publica com a «incidència» (issue, en anglès) a GitHub, el web on l'equip anota les errades del programa per corregir-les. És pública i va en anglès, la llengua del projecte. No porta el teu nom ni cap dada teva: l'envio jo, Karla bot. Serveix per avisar d'errors del programa, no per resoldre dubtes d'ús.\n\nRevisa-la i, si està bé, prem «Enviar a l'equip». Si no l'envies, no es publica res.",
    "b_enviar": "Enviar a l'equip",
    "b_no_enviar": 'No enviar',
    "incidencia_abierta": "Enviada. La pots seguir en aquest enllaç, sense necessitat de compte, per veure què respon l'equip i si ho corregeix: {url}",
    "incidencia_cancelada": "D'acord, no he enviat res.",
    "incidencia_caducada": "Aquest esborrany ja no està disponible. Si vols avisar de l'error, torna-m'ho a explicar.",
    "incidencia_tope": "Avui ja s'han enviat {n} avisos d'error a l'equip, el màxim d'un dia. Prova-ho demà o explica-ho al grup eXeLearning.",
    "incidencia_error": "No he pogut enviar l'avís. Prova-ho més tard o explica-ho al grup eXeLearning.",
}

GL = {
    "inicio": ("Ola, son Karla, unha asistente para resolver dúbidas sobre [eXeLearning](https://exelearning.net). "
               "Non son unha persoa: son un programa que usa intelixencia artificial."),
    "ayuda_preguntar": ("🔎 Pregúntame o que queiras. Escríbeme a túa dúbida coas túas palabras: como se fai "
                        "algo, por que o programa se comporta dunha maneira ou como publicar o teu recurso en "
                        "Moodle, Procomún ou outra plataforma. Busco no manual, na documentación do programa e dos "
                        "seus complementos e no que se falou no grupo [eXeLearning](https://t.me/exelearning), e "
                        "dígoche de onde sae cada cousa."),
    "ayuda_final": ("ℹ️ Ten en conta: podo equivocarme, así que comproba o importante na mensaxe ou no documento "
                    "que cito. O que me escribes procésase con Claude, unha IA de Anthropic, en servidores dos "
                    "Estados Unidos. Só gardo, de forma anónima, as preguntas que non consigo responder, para "
                    "mellorar, e bórroas aos 60 días. Respondo aos membros do grupo eXeLearning. Creoume @jjdeharo."),
    "traduccion": "Tradución automática feita con IA, sen revisión profesional.",
    "perfil": ("Son Karla, unha asistente para resolver dúbidas sobre eXeLearning. Busco no seu manual, na "
               "documentación do programa e dos seus complementos e nas conversas do grupo de Telegram "
               "eXeLearning, e digo de onde sae cada resposta. Non son unha persoa: son un programa que usa "
               "Claude, unha IA de Anthropic. Creada por @jjdeharo."),
    "perfil_corto": "Resolvo dúbidas sobre eXeLearning co seu manual, a súa documentación e o falado no grupo.",
    "c_ayuda": "Como funciono",
    "no_miembro": ("Só respondo aos membros do grupo eXeLearning (https://t.me/exelearning). Entrar é libre: "
                   "únete e volve escribirme."),
    "no_autorizado": "Aínda estou en probas. Pronto estarei aberta ao grupo eXeLearning.",
    "solo_privado": "Só respondo por privado: escríbeme en https://t.me/{usuario}",
    "solo_texto": "Escríbeme a pregunta en texto.",
    "error": "Algo fallou ao buscar. Proba outra vez nun momento.",
    "cupo": "Chegaches ás {cupo} preguntas de hoxe. Mañá poderás seguir.",
    "tope": "Este mes esgotouse o meu orzamento. Volverei responder o día 1.",
    "seguidas": "Fixéchesme moitas consultas seguidas. Segue dentro dun anaco.",
    "incidencia_vista": '📝 Este é o aviso de erro que lle enviaría ao equipo que desenvolve eXeLearning. Publícase como «incidencia» (issue, en inglés) en GitHub, a web onde o equipo anota os fallos do programa para corrixilos. É pública e vai en inglés, a lingua do proxecto. Non leva o teu nome nin ningún dato teu: envíoa eu, Karla bot. Serve para avisar de erros do programa, non para resolver dúbidas de uso.\n\nRevísaa e, se está ben, preme «Enviar ao equipo». Se non a envías, non se publica nada.',
    "b_enviar": 'Enviar ao equipo',
    "b_no_enviar": 'Non enviar',
    "incidencia_abierta": 'Enviada. Podes seguila nesta ligazón, sen necesidade de conta, para ver que responde o equipo e se o corrixe: {url}',
    "incidencia_cancelada": 'De acordo, non enviei nada.',
    "incidencia_caducada": 'Este borrador xa non está dispoñible. Se queres avisar do erro, volve contarmo.',
    "incidencia_tope": 'Hoxe xa se enviaron {n} avisos de erro ao equipo, o máximo dun día. Proba mañá ou cóntao no grupo eXeLearning.',
    "incidencia_error": 'Non puiden enviar o aviso. Proba máis tarde ou cóntao no grupo eXeLearning.',
}

EU = {
    "inicio": ("Kaixo, Karla naiz, [eXeLearning](https://exelearning.net)-i buruzko zalantzak argitzeko "
               "laguntzailea. Ez naiz pertsona bat: adimen artifiziala erabiltzen duen programa bat naiz."),
    "ayuda_preguntar": ("🔎 Galdetu nahi duzuna. Idatzi zure zalantza zure hitzekin: zerbait nola egiten den, "
                        "programak zergatik jokatzen duen modu batean edo zure baliabidea Moodlen, Procomúnen edo "
                        "beste plataforma batean nola argitaratu. Eskuliburuan, programaren eta bere osagarrien "
                        "dokumentazioan eta [eXeLearning](https://t.me/exelearning) taldean hitz egindakoan "
                        "bilatzen dut, eta gauza bakoitza nondik datorren esaten dizut."),
    "ayuda_final": ("ℹ️ Kontuan izan: oker egon naiteke, beraz egiaztatu garrantzitsua aipatzen dudan mezuan edo "
                    "dokumentuan. Idazten didazuna Claude-rekin prozesatzen da, Anthropic-en IA bat, Estatu "
                    "Batuetako zerbitzarietan. Erantzun ezin ditudan galderak bakarrik gordetzen ditut, modu "
                    "anonimoan, hobetzeko, eta 60 egunera ezabatzen ditut. eXeLearning taldeko kideei erantzuten "
                    "diet. @jjdeharo-k sortu nau."),
    "traduccion": "IArekin egindako itzulpen automatikoa, berrikuspen profesionalik gabe.",
    "perfil": ("Karla naiz, eXeLearning-i buruzko zalantzak argitzeko laguntzailea. Bere eskuliburuan, "
               "programaren eta bere osagarrien dokumentazioan eta eXeLearning Telegram taldeko elkarrizketetan "
               "bilatzen dut, eta erantzun bakoitza nondik datorren esaten dut. Ez naiz pertsona bat: Claude "
               "erabiltzen duen programa bat naiz, Anthropic-en IA bat. @jjdeharo-k sortua."),
    "perfil_corto": "eXeLearning-i buruzko zalantzak argitzen ditut eskuliburuarekin, dokumentazioarekin eta taldean esandakoarekin.",
    "c_ayuda": "Nola funtzionatzen dudan",
    "no_miembro": ("eXeLearning taldeko kideei bakarrik erantzuten diet (https://t.me/exelearning). Sartzea "
                   "librea da: batu zaitez eta idatzi berriro."),
    "no_autorizado": "Oraindik probetan nago. Laster eXeLearning taldearentzat irekita egongo naiz.",
    "solo_privado": "Pribatuan bakarrik erantzuten dut: idatzi hemen https://t.me/{usuario}",
    "solo_texto": "Idatzi galdera testuan.",
    "error": "Zerbait gaizki atera da bilatzean. Saiatu berriro une batean.",
    "cupo": "Gaurko {cupo} galderetara iritsi zara. Bihar jarraitu ahal izango duzu.",
    "tope": "Hilabete honetan nire aurrekontua agortu da. Hilaren 1ean erantzungo dut berriro.",
    "seguidas": "Kontsulta asko egin dizkidazu jarraian. Jarraitu pixka bat barru.",
    "incidencia_vista": '📝 Hau da eXeLearning garatzen duen taldeari bidaliko niokeen errore-oharra. GitHuben «intzidentzia» (issue, ingelesez) gisa argitaratzen da; taldeak programaren akatsak bertan idazten ditu, zuzentzeko. Publikoa da eta ingelesez doa, proiektuaren hizkuntzan. Ez darama zure izenik ezta zure daturik ere: nik bidaltzen dut, Karla bot-ek. Programaren erroreen berri emateko da, ez erabilerari buruzko zalantzak argitzeko.\n\nBerrikusi eta, ondo badago, sakatu «Taldeari bidali». Bidaltzen ez baduzu, ez da ezer argitaratzen.',
    "b_enviar": 'Taldeari bidali',
    "b_no_enviar": 'Ez bidali',
    "incidencia_abierta": 'Bidalita. Esteka honetan jarraitu dezakezu, konturik behar gabe, taldeak zer erantzuten duen eta zuzentzen duen ikusteko: {url}',
    "incidencia_cancelada": 'Ados, ez dut ezer bidali.',
    "incidencia_caducada": 'Zirriborro hau ez dago erabilgarri. Errorearen berri eman nahi baduzu, kontatu berriro.',
    "incidencia_tope": 'Gaur dagoeneko {n} errore-ohar bidali zaizkio taldeari, egun bateko gehienekoa. Saiatu bihar edo kontatu eXeLearning taldean.',
    "incidencia_error": 'Ezin izan dut oharra bidali. Saiatu geroago edo kontatu eXeLearning taldean.',
}

EN = {
    "inicio": ("Hi, I'm Karla, an assistant for questions about [eXeLearning](https://exelearning.net). "
               "I'm not a person: I'm a program that uses artificial intelligence."),
    "ayuda_preguntar": ("🔎 Ask me anything. Tell me your question in your own words: how to do something, why "
                        "the program behaves in a certain way, or how to publish your resource on Moodle, Procomún "
                        "or another platform. I search the manual, the documentation of the program and its add-ons, "
                        "and what has been said in the [eXeLearning](https://t.me/exelearning) group, and I tell you "
                        "where each answer comes from."),
    "ayuda_final": ("ℹ️ Please note: I can make mistakes, so check anything important in the message or document "
                    "I cite. What you write to me is processed with Claude, an AI by Anthropic, on servers in the "
                    "United States. I only keep, anonymously, the questions I can't answer, to improve, and I delete "
                    "them after 60 days. I answer members of the eXeLearning group. Created by @jjdeharo."),
    "traduccion": "Automatic translation made with AI, without professional review.",
    "perfil": ("I'm Karla, an assistant for questions about eXeLearning. I search its manual, the documentation of "
               "the program and its add-ons, and the conversations of the eXeLearning Telegram group, and I say "
               "where each answer comes from. I'm not a person: I'm a program that uses Claude, an AI by Anthropic. "
               "Created by @jjdeharo."),
    "perfil_corto": "I answer questions about eXeLearning with its manual, its documentation and the group's conversations.",
    "c_ayuda": "How I work",
    "no_miembro": ("I only answer members of the eXeLearning group (https://t.me/exelearning). Joining is free: "
                   "join and write to me again."),
    "no_autorizado": "I'm still being tested. I'll soon be open to the eXeLearning group.",
    "solo_privado": "I only answer in private: write to me at https://t.me/{usuario}",
    "solo_texto": "Please write your question as text.",
    "error": "Something went wrong while searching. Please try again in a moment.",
    "cupo": "You've reached today's {cupo} questions. You can continue tomorrow.",
    "tope": "My budget for this month has run out. I'll answer again on the 1st.",
    "seguidas": "You've asked me a lot of questions in a row. Please continue in a while.",
    "incidencia_vista": "📝 This is the bug report I would send to the team that develops eXeLearning. It is published as an issue on GitHub, the site where the team keeps track of the program's bugs in order to fix them. It is public and written in English, the project's language. It does not include your name or any of your details: I send it, Karla bot. It is for reporting bugs in the program, not for usage questions.\n\nReview it and, if it looks right, tap «Send to the team». If you don't send it, nothing is published.",
    "b_enviar": 'Send to the team',
    "b_no_enviar": "Don't send",
    "incidencia_abierta": "Sent. You can follow it at this link, no account needed, to see the team's reply and whether they fix it: {url}",
    "incidencia_cancelada": "All right, I haven't sent anything.",
    "incidencia_caducada": 'This draft is no longer available. If you want to report the bug, tell me about it again.',
    "incidencia_tope": '{n} bug reports have already been sent to the team today, the daily maximum. Try again tomorrow or tell the eXeLearning group.',
    "incidencia_error": "I couldn't send the report. Try again later or tell the eXeLearning group.",
}

TEXTOS = {"es": ES, "ca": CA, "gl": GL, "eu": EU, "en": EN}


def texto(lengua: str, clave: str, **datos) -> str:
    t = TEXTOS.get(lengua, ES).get(clave) or ES[clave]
    return t.format(**datos) if datos else t
