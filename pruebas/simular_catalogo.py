# SPDX-License-Identifier: AGPL-3.0-or-later
"""Simula conversaciones con el bot sobre el menú y el catálogo, sin Telegram ni la hoja de verdad.

Telegram y la hoja se sustituyen por imitaciones que apuntan lo que el bot
envía; Claude sí es el de verdad (unos 0,03 USD por pasada). Comprueba los
permisos por grupo, el alta con cambio, los duplicados, «Mis recursos», el
código por correo, quitar un recurso y el idioma en que habla el bot.

Uso: simular_catalogo.py [URL]
"""
import sys
import tempfile
import threading
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "scripts"))
import anthropic  # noqa: E402

import bot  # noqa: E402
import catalogo  # noqa: E402
import consultar  # noqa: E402

URL = sys.argv[1] if len(sys.argv) > 1 else "https://jjdeharo.github.io/miae/es/"  # CC BY-SA, en su repositorio
VCE, CHATGPT, AMBOS, EDUMEDIA = 101, 102, 103, 104


class TelegramFalso:
    def __init__(self):
        self.enviados, self.editados, self.borrados = [], [], []

    def __call__(self, metodo, espera=30, **p):
        if metodo == "getChatMember":
            suyo = {VCE: {"vce"}, CHATGPT: {"chatgpt"}, AMBOS: {"vce", "chatgpt"},
                    EDUMEDIA: {"edumedia"}}.get(p["user_id"], set())
            clave = next(g.clave for g in bot.grupos.ACTIVOS.values() if g.id == p["chat_id"])
            return {"status": "member"} if clave in suyo else None
        if metodo in ("sendMessage",):
            self.enviados.append((p["chat_id"], p["text"], p.get("reply_markup")))
        if metodo == "sendRichMessage":  # respuestas y /estado (Bot API 10.1)
            r = p["rich_message"]
            self.enviados.append((p["chat_id"], r.get("markdown") or r.get("html"), p.get("reply_markup")))
        if metodo in ("editMessageText", "editMessageReplyMarkup"):
            self.editados.append(p)
        if metodo == "deleteMessage":
            self.borrados.append(p)
        if metodo in ("sendMessage", "sendDocument", "sendRichMessage"):
            self.ultimo_id = getattr(self, "ultimo_id", 100) + 1
            return {"message_id": self.ultimo_id}
        return {"message_id": 1}


class HojaFalsa:
    def __init__(self):
        self.lista = [{catalogo.COLUMNAS["url"]: "https://ejemplo.org/antigua", catalogo.COLUMNAS["titulo"]: "Antigua",
                       catalogo.COLUMNAS["autor"]: "Ana", catalogo.COL_CORREO: "ana@ejemplo.org",
                       **{catalogo.COLUMNAS[k]: "" for k in ("descripcion", "tipo", "niveles", "areas",
                                                              "palabras_clave", "idiomas")}}]
        self.correos = []

    def filas(self):
        return self.lista

    def buscar(self, url):
        return next((f for f in self.lista if catalogo.normalizar(f[catalogo.COLUMNAS["url"]]) == catalogo.normalizar(url)), None)

    def alta(self, f):
        self.lista.append({**catalogo.a_fila(f), catalogo.COL_CORREO: ""})

    def modificar(self, url, f):
        fila = self.buscar(url)
        fila.update(catalogo.a_fila(f))

    def borrar(self, url):
        self.lista = [f for f in self.lista if catalogo.normalizar(f[catalogo.COLUMNAS["url"]]) != catalogo.normalizar(url)]

    def enviar_codigo(self, correo, codigo):
        self.correos.append((correo, codigo))
        return [f[catalogo.COLUMNAS["url"]] for f in self.lista if f[catalogo.COL_CORREO] == correo]


def responder_falso(texto, historial=None, ambito=None, lengua=None):
    """La búsqueda no se prueba aquí; sí que «añade … enlace» se convierta en un recurso, como hace Claude."""
    enlace = texto.split()[-1]
    if texto.startswith("añade") and enlace.startswith("http"):
        return {"texto": "", "accion": {"recurso": enlace}, "uso": {"usd": 0, "llamadas": []}}
    if texto.startswith("caracoles"):
        return {"texto": "No encuentro nada.", "uso": {"usd": 0, "llamadas": []}, "sin_resolver": "sin resultado"}
    return {"texto": "(búsqueda)", "uso": {"usd": 0, "llamadas": ['buscar_mensajes({"consulta": "x"})']},
            "ambito": ambito}


def nuevo_bot(tmp: Path):
    catalogo.DUENOS = tmp / "catalogo.json"
    catalogo.REVISIONES = tmp / "revisiones.json"
    bot.ESTADO = tmp / "estado.json"
    bot.SIN_RESOLVER = tmp / "sin-resolver.jsonl"
    bot.AUTORIZADOS = set()
    bot.ABIERTO = True
    b = object.__new__(bot.Bot)
    b.tg, b.id, b.usuario, b.token = TelegramFalso(), 1, "IAEducativa_bot", "x"
    b.memoria, b.pendientes, b.miembros = {}, {}, {}
    b.recursos = catalogo.Fichas(anthropic.Anthropic(api_key=consultar.CLAVE.read_text().strip()))
    b.hoja = HojaFalsa()
    b.espera, b.fichas_rec, b.listas, b.lenguas, b.recientes, b.compartir = {}, {}, {}, {}, {}, {}
    b.ambitos, b.rechazados, b.valorables = {}, {}, {}
    b.consultor = type("C", (), {"cliente": b.recursos.cliente,  # para detectar el idioma
                                 "responder": lambda self, texto, *a: responder_falso(texto, *a)})()
    b.en_hilo = lambda f, *a: f(*a)  # sin hilos: la prueba sigue el orden
    b.escribiendo = lambda chat: threading.Event()
    return b


def mensaje(b, uid, texto, lengua="es"):
    n = len(b.tg.enviados)
    b.atender({"chat": {"id": uid, "type": "private"}, "from": {"id": uid, "first_name": f"Persona{uid}",
               "language_code": lengua}, "text": texto, "message_id": 1})
    return b.tg.enviados[n:]


def boton(b, uid, dato):
    n = len(b.tg.enviados)
    b.boton({"id": "1", "from": {"id": uid}, "data": dato, "message": {"message_id": 7, "chat": {"id": uid}}})
    return b.tg.enviados[n:]


def olvidar_lenguas(b):
    """Borra el idioma de todos, después de esperar a las detecciones que siguen en marcha: si no, una que
    acaba tarde vuelve a poner el idioma del mensaje anterior."""
    for h in threading.enumerate():
        if getattr(getattr(h, "_target", None), "__name__", "") == "detectar_lengua":
            h.join(60)
    b.lenguas.clear()


def comprobar(nombre, condicion, salida):
    print(f"{'✓' if condicion else '✗'} {nombre}")
    if not condicion:
        for _, t, _ in salida:
            print("   ·", t[:300].replace("\n", " "))
    return condicion


def main():
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        b = nuevo_bot(Path(tmp))
        s = mensaje(b, 999, "hola")
        ok &= comprobar("quien no es de ningún grupo no entra", "solo puedo responder a quien forma parte" in s[0][1], s)
        s = mensaje(b, CHATGPT, "/ayuda")
        ok &= comprobar("la ayuda de ChatGPT-IA-edu no ofrece el catálogo",
                        "Biblioteca" in s[0][1] and bot.textos.texto("es", "ayuda_recurso")[:40] not in s[0][1], s)
        ok &= comprobar("la ayuda no ofrece ideas para las clases", "Ideas para tus clases" not in s[0][1], s)
        s = mensaje(b, VCE, "/ayuda")
        ok &= comprobar("la ayuda de VCE no ofrece la biblioteca",
                        "repositorio de Vibe" in s[0][1] and "Envíame aquí el archivo en PDF" not in s[0][1], s)
        s = mensaje(b, CHATGPT, "/repositorio")
        ok &= comprobar("ChatGPT-IA-edu no puede añadir recursos", "únete al grupo" in s[0][1], s)
        s = mensaje(b, VCE, "/biblioteca")
        ok &= comprobar("VCE no puede añadir a la biblioteca", "miembros de ChatGPT-IA-edu" in s[0][1], s)

        s = mensaje(b, VCE, "/recurso", "en") + mensaje(b, VCE, URL, "en")  # el nombre antiguo; Telegram en inglés
        ficha = b.fichas_rec.get(VCE, {}).get("ficha")
        ok &= comprobar("/recurso + enlace prepara la ficha", bool(ficha) and s[-1][2] is not None, s)
        if ficha:
            print("   ficha:", ficha["titulo"], "|", ", ".join(ficha["niveles"]))
            ok &= comprobar("la ficha va en castellano aunque Telegram esté en inglés",
                            any(p in f" {ficha['descripcion']} " for p in (" para ", " que ", " los ", " las ")), s)
        s = boton(b, VCE, "rc") + mensaje(b, VCE, "quita Bachillerato y pon que el autor es Ana Pérez")
        ficha = b.fichas_rec.get(VCE, {}).get("ficha", {})
        ok &= comprobar("el cambio se aplica", ficha.get("autor") == "Ana Pérez"
                        and "Bachillerato" not in ficha.get("niveles", []), s)
        ok &= comprobar("el cambio conserva la licencia", bool(ficha.get("licencia")), s)
        s = s_publicar = boton(b, VCE, "rp")
        ok &= comprobar("tras publicar, ofrece compartirlo avisando de que aún no se publica",
                        any("rcs" in str(x[2]) for x in s) and any("Todavía no se publicará" in x[1] for x in s), s)
        s = boton(b, VCE, "rcs")
        borrador = next((x for x in s if x[2] and "rcp" in str(x[2])), None)
        ok &= comprobar("el borrador va en tercera persona, con el nombre y el enlace, y con Cancelar",
                        borrador is not None and borrador[1].startswith("Ana Pérez") and URL in borrador[1]
                        and "rcn" in str(borrador[2]), s)
        enviados = len(b.tg.enviados)
        s = boton(b, VCE, "rcp")
        al_grupo = [x for x in b.tg.enviados[enviados:] if x[0] == bot.CATALOGO.id]
        ok &= comprobar("Publicar lo manda al tema «¡Comparte tu App!» del grupo, con botón para quitarlo",
                        len(al_grupo) == 1 and "/7674/" in s[-1][1] and "rcq:" in str(s[-1][2]), s)
        quitar = next(x["callback_data"] for fila in s[-1][2]["inline_keyboard"] for x in fila
                      if x["callback_data"].startswith("rcq:"))
        s = boton(b, VCE, quitar)
        ok &= comprobar("«Quitarlo del grupo» lo borra", s and "Quitado del grupo" in s[-1][1], s)
        s = s_publicar
        ok &= comprobar("publicar da de alta y enlaza a la web general del repositorio",
                        b.hoja.buscar(URL) is not None and any(x[1].count(catalogo.WEB) == 1 and "primero" in x[1]
                                                               and "?ids=" not in x[1] for x in s), s)
        s = mensaje(b, VCE, f"añade mi aplicación al repositorio {URL}")
        ok &= comprobar("pedirlo con sus palabras lleva al catálogo (aquí, ya está y es suyo, con enlace a su ficha)",
                        "es tuyo" in s[0][1] and f"?ids={URL}" in s[0][1], s)
        s = mensaje(b, AMBOS, URL)
        ok &= comprobar("otra persona con el mismo enlace: ya está, de otro", "a nombre de" in s[0][1], s)

        s = mensaje(b, AMBOS, "/misrecursos")
        ok &= comprobar("sin recursos, pide el correo", "correo" in s[0][1], s)
        s = mensaje(b, AMBOS, "ana@ejemplo.org")
        codigo = b.hoja.correos[-1][1] if b.hoja.correos else ""
        ok &= comprobar("manda el código al correo", "código" in s[0][1] and bool(codigo), s)
        s = mensaje(b, AMBOS, "000000" if codigo != "000000" else "111111")
        ok &= comprobar("código mal: lo dice", "no es correcto" in s[0][1], s)
        s = mensaje(b, AMBOS, codigo)
        ok &= comprobar("código bien: enseña sus recursos", any("Antigua" in str(x[2]) for x in s), s)
        s = boton(b, AMBOS, "rb:0") + boton(b, AMBOS, "rs:0")
        ok &= comprobar("quitar un recurso propio", b.hoja.buscar("https://ejemplo.org/antigua") is None, s)
        b.listas[CHATGPT] = b.hoja.filas()
        s = boton(b, CHATGPT, "rs:0")
        ok &= comprobar("no se puede quitar uno ajeno", b.hoja.buscar(URL) is not None and "no está a tu nombre" in s[0][1], s)

        b.lenguas.pop(VCE, None)
        s = mensaje(b, VCE, "/misrecursos")
        ok &= comprobar("Mis recursos enseña el publicado", any(ficha.get("titulo", "")[:60] in str(x[2]) for x in s), s)
        ok &= comprobar("Mis recursos ofrece añadir uno nuevo, que pide el enlace como /repositorio",
                        any("rnuevo" in str(x[2]) for x in s) and "enlace" in (boton(b, VCE, "rnuevo") or [("", "")])[-1][1], s)
        s = boton(b, VCE, "rm:0") + mensaje(b, VCE, "añade Primaria a los niveles") + boton(b, VCE, "rp")
        fila = b.hoja.buscar(URL) or {}
        ok &= comprobar("cambiar uno publicado", "Primaria" in fila.get(catalogo.COLUMNAS["niveles"], ""), s)
        ok &= comprobar("tras un cambio, el enlace abre solo su ficha en el repositorio",
                        s and f"?ids={URL}" in s[-1][1], s)

        # Los cambios miran otra vez el recurso (Juanjo, 28-10-2026): rehacer, revisar y la licencia del código.
        lic, des = catalogo.COLUMNAS["licencia"], catalogo.COLUMNAS["descripcion"]
        fila.update({lic: "", des: "Juego de ajedrez para aprender las aperturas clásicas."})
        s = boton(b, VCE, "rm:0") + mensaje(b, VCE, "añade Secundaria a los niveles") + boton(b, VCE, "rp")
        fila = b.hoja.buscar(URL) or {}
        print("   licencia:", fila.get(lic))
        ok &= comprobar("un cambio cualquiera completa la licencia que faltaba, leída del repositorio",
                        "CC BY-SA" in fila.get(lic, ""), s)
        ok &= comprobar("y deja igual lo que no se pide", "ajedrez" in fila.get(des, ""), s)
        s = boton(b, VCE, "rm:0") + mensaje(b, VCE, "revisa la descripción, creo que no corresponde a la aplicación")
        nueva = b.fichas_rec.get(VCE, {}).get("ficha", {})
        print("   descripción:", nueva.get("descripcion", "")[:120])
        ok &= comprobar("revisar la descripción la rehace a partir del recurso",
                        nueva.get("descripcion") and "ajedrez" not in nueva["descripcion"].lower(), s)
        s = boton(b, VCE, "rc") + mensaje(b, VCE, "la licencia es MIT")
        nueva = b.fichas_rec.get(VCE, {}).get("ficha", {})
        ok &= comprobar("la licencia no cambia porque lo pida la persona", "CC BY-SA" in nueva.get("licencia", ""), s)
        boton(b, VCE, "rx")
        leer_url = catalogo.leer_url
        catalogo.leer_url = lambda url: ("<html><body><h1>Fracciones</h1><p>Ejercicios de sumas de fracciones "
                                         "para Primaria con corrección inmediata.</p></body></html>", None)
        try:
            sin = {**catalogo.de_fila(fila), "url": "https://ejemplo.org/fr", "licencia": ""}
            b.fichas_rec[VCE] = {"ficha": sin, "modo": "modificar", "momento": time.time()}
            s = boton(b, VCE, "rc") + mensaje(b, VCE, "cambia el título a «Fracciones»")
            ok &= comprobar("sin licencia en el código, no guarda el cambio y explica cómo ponerla",
                            s and "No guardo el cambio" in s[-1][1] and b.fichas_rec[VCE]["ficha"] is sin, s)
        finally:
            catalogo.leer_url = leer_url
        b.fichas_rec.pop(VCE, None)

        # El enlace también cambia, si el recurso se ha mudado (Juanjo, 28-10-2026).
        b.hoja.lista.append({**catalogo.a_fila({"titulo": "Otra", "url": "https://ejemplo.org/otra", "autor": "Ana"}),
                             catalogo.COL_CORREO: "ana@ejemplo.org"})
        de_vce = catalogo.de_la_persona(VCE, b.hoja)
        n = next(i for i, f in enumerate(de_vce)
                 if catalogo.normalizar(f[catalogo.COLUMNAS["url"]]) == catalogo.normalizar(URL))
        b.listas[VCE] = de_vce
        s = boton(b, VCE, f"rm:{n}") + mensaje(b, VCE, "cambia la url por: https://ejemplo.org/otra")
        ok &= comprobar("no cambia el enlace al de otro recurso", s and "otro recurso" in s[-1][1], s)
        mudada = URL.replace("/es/", "/ca/") if "/es/" in URL else URL.rstrip("/") + "/index.html"
        s = boton(b, VCE, f"rm:{n}") + mensaje(b, VCE, f"cambia la url por: {mudada}") + boton(b, VCE, "rp")
        ok &= comprobar("cambia el enlace de uno publicado, sin duplicar la fila",
                        b.hoja.buscar(mudada) is not None and b.hoja.buscar(URL) is None, s)
        duenos = catalogo.leer_duenos()["recursos"]
        ok &= comprobar("y sigue siendo de quien lo publicó", duenos.get(catalogo.normalizar(mudada)) == VCE
                        and catalogo.normalizar(URL) not in duenos, s)
        b.hoja.borrar("https://ejemplo.org/otra")

        # Mis recursos por páginas: Telegram no admite más de 100 botones por mensaje
        for k in range(45):
            b.hoja.lista.append({**catalogo.a_fila({"titulo": f"Recurso {k:02d}", "url": f"https://ejemplo.org/r{k}",
                                                    "autor": "Ana"}), catalogo.COL_CORREO: "ana@ejemplo.org"})
        s = mensaje(b, AMBOS, "/misrecursos")
        botones = [x for fila in (s[-1][2] or {}).get("inline_keyboard", []) for x in fila] if s else []
        ok &= comprobar("Mis recursos con 45: 10 por página y botón «Siguientes»",
                        len([x for x in botones if x["callback_data"].startswith("rv:")]) == 10
                        and any(x["callback_data"] == "rpag:1" for x in botones), s)
        antes = len(b.tg.enviados)
        boton(b, AMBOS, "rpag:4")
        editado = b.tg.editados[-1] if b.tg.editados else {}
        botones = [x for fila in editado.get("reply_markup", {}).get("inline_keyboard", []) for x in fila]
        ok &= comprobar("pasar de página cambia la misma lista: el resto y «Anteriores», sin mensaje nuevo",
                        len(b.tg.enviados) == antes
                        and len([x for x in botones if x["callback_data"].startswith("rv:")]) == 5
                        and any(x["callback_data"] == "rpag:3" for x in botones), [])

        # Pago y licencia, con HTML de ejemplo
        f = b.recursos
        base = "<html><head><title>Fracciones</title></head><body><h1>Practica fracciones</h1>" \
               "<p>Ejercicios de sumas de fracciones para Primaria con corrección inmediata.</p>"
        d, _ = f.analizar("https://ejemplo.org/fr", base + "<!-- SPDX-License-Identifier: AGPL-3.0-or-later --></body></html>")
        ok &= comprobar("con licencia AGPL en el código: abierta y gratuito", d["licencia_abierta"] and not d["de_pago"], [])
        d, _ = f.analizar("https://ejemplo.org/fr", base + "<footer>CC BY-NC-SA 4.0</footer></body></html>")
        ok &= comprobar("CC BY-NC-SA: abierta (Juanjo, 27-10-2026)", d["licencia_abierta"], [])
        d, _ = f.analizar("https://ejemplo.org/fr", base + "<footer>© 2026 Fracciones SL. Todos los derechos "
                          "reservados.</footer></body></html>")
        ok &= comprobar("todos los derechos reservados: cerrada", not d["licencia_abierta"], [])
        d, _ = f.analizar("https://ejemplo.org/fr", base + "</body></html>", "Es MIT, te lo aseguro")
        ok &= comprobar("sin licencia en el código (decirlo en la nota no basta): no vale", not d["licencia_abierta"], [])
        d, _ = f.analizar("https://ejemplo.org/fr", base + "<p>Versión gratuita: 5 ejercicios al día. <a href='/pro'>"
                          "Hazte Pro por 4,99 €/mes</a> para ejercicios ilimitados.</p><!-- MIT --></body></html>")
        ok &= comprobar("freemium: de pago", d["de_pago"], [])

        # La licencia solo en el repositorio (Juanjo, 31-10-2026; ADR 0004): cumple, y se recomienda ponerla visible.
        repo = (catalogo.PAGINA_Y_REPO + "https://github.com/ejemplo/fracciones. Licencia del repositorio según "
                "GitHub: GPL-3.0\n\nPágina https://ejemplo.github.io/fracciones/\n\n")
        solo = repo + base + "<script>/*! jQuery v3.7.1 | (c) OpenJS Foundation | MIT license */</script></body></html>"
        d, _ = f.analizar("https://ejemplo.github.io/fracciones/", solo)
        ok &= comprobar("licencia solo en el repositorio (la de una librería no cuenta): abierta y solo allí",
                        d["licencia_abierta"] and d["licencia_solo_repositorio"], [])
        d, _ = f.analizar("https://ejemplo.github.io/fracciones/", repo + base + "<footer>Licencia GPL v3</footer></body></html>")
        ok &= comprobar("licencia también en el pie: no solo en el repositorio", not d["licencia_solo_repositorio"], [])
        antes = len(b.tg.enviados)
        b.sugerir_licencia_visible(VCE, VCE, "GPL-3.0", True, solo)
        ok &= comprobar("el consejo propone el pie y la línea SPDX",
                        len(b.tg.enviados) == antes + 1 and "SPDX-License-Identifier: GPL-3.0 -->" in b.tg.enviados[-1][1],
                        b.tg.enviados[antes:])
        b.sugerir_licencia_visible(VCE, VCE, "GPL-3.0", True, base)
        ok &= comprobar("sin haber leído la página y el repositorio, no se aconseja nada", len(b.tg.enviados) == antes + 1, [])

        # El mínimo (Juanjo, 30-10-2026; ADR 0004): fuera lo que no se puede usar; un recurso sencillo entra.
        agpl = "<!-- SPDX-License-Identifier: AGPL-3.0-or-later --></body></html>"
        d, _ = f.analizar("https://ejemplo.org/fr", base + "<script>/* genera sumas y corrige */</script>" + agpl)
        ok &= comprobar("un recurso sencillo y completo llega al mínimo", d["es_recurso_educativo"] and d["nivel_minimo"], [])
        vacia = ("<html><head><title>Fracciones</title></head><body><h1>Practica fracciones</h1>"
                 "<p>Próximamente: aquí irán los ejercicios.</p><button>Empezar</button>" + agpl)
        d, _ = f.analizar("https://ejemplo.org/vacia", vacia)
        ok &= comprobar("una página a medio hacer no llega al mínimo", d["suficiente"] and not d["nivel_minimo"], [])
        d, _ = f.analizar("https://ejemplo.org/mal", base + "<h2>Soluciones</h2><ul><li>1/2 + 1/3 = 2/5</li>"
                          "<li>1/4 + 1/4 = 2/8</li><li>2/3 + 1/3 = 3/6</li></ul>" + agpl)
        ok &= comprobar("errores de bulto en lo que enseña: no llega al mínimo", not d["nivel_minimo"], [])
        d, _ = f.admitir("https://ejemplo.org/vacia", vacia)
        ok &= comprobar("un recurso que se muda a una página a medio hacer no entra", not d["nivel_minimo"], [])

        # Pedir una revisión: el rechazo llega a Juanjo y «Cumple» sigue el alta.
        de = {"id": VCE, "first_name": "Persona", "last_name": str(VCE)}
        n = len(b.tg.enviados)
        b.recurso(VCE, VCE, de, "https://ejemplo.org/vacia", vacia)
        s = b.tg.enviados[n:]
        ok &= comprobar("el rechazo ofrece «Pedir una revisión»", s and "rr" in str(s[-1][2]), s)
        s = boton(b, VCE, "rr") + mensaje(b, VCE, "Los ejercicios se cargan al pulsar Empezar, ya funciona.")
        a_juanjo = [x for x in b.tg.enviados if x[0] == bot.JUANJO and "jrc:" in str(x[2])]
        ok &= comprobar("la petición llega a Juanjo con sus razones y los dos botones",
                        a_juanjo and "ya funciona" in a_juanjo[-1][1] and "jrn:" in str(a_juanjo[-1][2])
                        and any("revisión manual" in x[1] for x in s), s)
        if a_juanjo:
            ref = next(x["callback_data"] for fila in a_juanjo[-1][2]["inline_keyboard"] for x in fila
                       if x["callback_data"].startswith("jrc:"))
            n = len(b.tg.enviados)
            b.revisar_rechazo(ref)
            s = b.tg.enviados[n:]
            ok &= comprobar("«Cumple» se lo dice a su autor y le enseña la ficha para publicarla",
                            any(x[0] == VCE and "Revisado a mano" in x[1] for x in s)
                            and any(x[0] == VCE and "rp" in str(x[2]) for x in s)
                            and catalogo.leer_revisiones()["https://ejemplo.org/vacia"]["estado"] == "aprobado"
                            and "contenido" not in catalogo.leer_revisiones()["https://ejemplo.org/vacia"], s)
            b.revisar_rechazo(ref)
            ok &= comprobar("pulsarlo otra vez no repite el alta", "ya no está" in b.tg.enviados[-1][1], [])
        b.fichas_rec.pop(VCE, None)

        # Idioma: al principio, el de Telegram; en cuanto escribe una frase, el de la frase.
        olvidar_lenguas(b)
        s = mensaje(b, AMBOS, "/ayuda", "en")
        ok &= comprobar("sin frase y con Telegram en inglés, castellano: el inglés no se toma de la app (ADR 0005)",
                        s and "Buscar en los grupos" in s[0][1] and "machine-translated" not in s[0][1], s)
        olvidar_lenguas(b)
        s = mensaje(b, AMBOS, "/ayuda", "gl")
        ok &= comprobar("sin frase, el idioma de su Telegram (gallego), con aviso de traducción",
                        s and "sen revisión profesional" in s[0][1], s)
        olvidar_lenguas(b)
        mensaje(b, VCE, "/repositorio", "en")
        mensaje(b, VCE, "bon dia, us volia enviar la meva aplicació però abans tinc un dubte", "en")
        s = mensaje(b, VCE, "/ayuda", "en")
        ok &= comprobar("escribe en catalán: el bot pasa al catalán", s and "Cercar als grups" in s[0][1], s)
        mensaje(b, VCE, "ok", "en")
        s = mensaje(b, VCE, "/ayuda", "en")
        ok &= comprobar("un «ok» no cambia el idioma", s and "Cercar als grups" in s[0][1], s)
        mensaje(b, AMBOS, "/recurso", "gl")
        mensaje(b, AMBOS, "quería saber cómo se añade una aplicación al catálogo, por favor", "gl")
        s = mensaje(b, AMBOS, "/ayuda", "gl")
        ok &= comprobar("Telegram en gallego pero escribe en castellano: castellano", s and "Buscar en los grupos" in s[0][1], s)

        # Límites (ADR 0006): sin cupos a la vista; freno por ritmo de gasto y contra el uso automático
        s = mensaje(b, CHATGPT, "/ayuda")
        ok &= comprobar("la ayuda no anuncia cupos", s and "Cada día" not in s[0][1], s)
        for _ in range(bot.CUPO_DIA + 2):
            s = mensaje(b, CHATGPT, "consulta")
        ok &= comprobar("sin freno, más preguntas que el antiguo cupo", s and s[0][1] == "(búsqueda)", s)
        frenado, bot.frenado = bot.frenado, lambda e: True
        s = mensaje(b, CHATGPT, "consulta")
        ok &= comprobar("con el freno de gasto, entran los cupos", s and "preguntas de hoy" in s[0][1], s)
        bot.frenado = frenado
        b.recientes.clear()
        olvidar_lenguas(b)
        for _ in range(bot.SEGUIDAS_HORA):
            mensaje(b, VCE, "consulta")
        s = mensaje(b, VCE, "consulta")
        ok &= comprobar(f"más de {bot.SEGUIDAS_HORA} consultas en una hora: pide pausa", s and "seguidas" in s[0][1], s)

        # /estado: un total de los miembros, sin separar grupos ni decir nada de Juanjo (30-10-2026)
        import json as _json
        e0 = _json.loads(bot.ESTADO.read_text()) if bot.ESTADO.exists() else {}
        antes = sum(bot.sin_juanjo(e0.get("preguntas_hoy", {})).values())
        b.recientes.clear()
        mensaje(b, AMBOS, "consulta")
        mensaje(b, VCE, "consulta")
        e1 = _json.loads(bot.ESTADO.read_text())
        ok &= comprobar("quien está en varios grupos cuenta una vez",
                        sum(bot.sin_juanjo(e1["preguntas_hoy"]).values()) - antes == 2, [])
        estado = bot.informe(bot.contabilidad(e1))
        ok &= comprobar("/estado no separa grupos ni habla de Juanjo",
                        not any(x in estado for x in ("Vibe Coding", "ChatGPT-IA-edu", "Tú", "contarte")), estado)

        # Preguntas sin resolver: se guardan sin nada de quién pregunta
        b.recientes.clear()
        mensaje(b, VCE, "caracoles en Marte con IA, ¿alguien?")
        guardado = bot.SIN_RESOLVER.read_text() if bot.SIN_RESOLVER.exists() else ""
        ok &= comprobar("la pregunta sin resolver se guarda, anónima",
                        "caracoles" in guardado and str(VCE) not in guardado and "Persona" not in guardado
                        and "sin resultado" in guardado, [])

        # 👍/👎 solo bajo la última respuesta; con 👎 la pregunta va a las sin resolver (30-10-2026)
        b.recientes.clear()
        mensaje(b, CHATGPT, "primera consulta")
        id1 = b.valorables[CHATGPT]["id"]
        s = mensaje(b, CHATGPT, "segunda consulta sobre rúbricas")
        ok &= comprobar("la respuesta lleva 👍/👎", bool(s) and s[-1][2] == bot.VALORAR, s)
        ok &= comprobar("y la anterior los pierde", any(p.get("message_id") == id1 and p.get("reply_markup")
                                                        == {"inline_keyboard": []} for p in b.tg.editados), [])
        e0 = _json.loads(bot.ESTADO.read_text())
        pulsar = {"id": "1", "from": {"id": CHATGPT}, "data": "val:-",
                  "message": {"message_id": b.valorables[CHATGPT]["id"], "chat": {"id": CHATGPT}}}
        b.boton(pulsar)
        b.boton(pulsar)  # un segundo toque no cuenta dos veces
        e1 = _json.loads(bot.ESTADO.read_text())
        guardado = bot.SIN_RESOLVER.read_text()
        ok &= comprobar("👎 cuenta una vez y guarda la pregunta, anónima",
                        e1["no_utiles_mes"] - e0.get("no_utiles_mes", 0) == 1 and "segunda consulta sobre rúbricas" in guardado
                        and "valoración negativa" in guardado and str(CHATGPT) not in guardado, [])
        estado = bot.informe(bot.contabilidad(e1))
        ok &= comprobar("/estado da valoraciones, personas que vuelven y la proporción sin resolver",
                        "Respuestas no útiles 👎" in estado and "Han vuelto otro día" in estado
                        and "de los últimos 60 días (" in estado, [(0, estado, 0)])
        rico = bot.a_html(bot.bloques_estado(bot.contabilidad(e1)))
        ok &= comprobar("/estado como tabla enriquecida", "<table" in rico and "<th" in rico, [(0, rico, 0)])
        prueba = {**e1, "dias_mes": {"1": ["2026-10-29", "2026-10-30"], "2": ["2026-10-30"],
                                     str(bot.JUANJO): ["2026-10-29", "2026-10-30"]}, "dias_mes_desde": None}
        filas = {f[0]: f for f in bot.filas_uso(prueba)[0]}
        ok &= comprobar("vuelve quien pregunta en dos días; Juanjo no cuenta",
                        filas["Personas"][2] == 2 and filas["Han vuelto otro día"][2] == 1, [(0, str(filas), 0)])

        # Quien solo es de EduMedia-IAG busca en todos, pero no añade a la Biblioteca ni al repositorio
        b.recientes.clear(); olvidar_lenguas(b)
        s = mensaje(b, EDUMEDIA, "/ayuda")
        ok &= comprobar("EduMedia-IAG: la ayuda ofrece buscar, sin Biblioteca ni repositorio",
                        s and "Buscar en los grupos" in s[0][1] and "EduMediaIAG" in s[0][1]
                        and "Añadir un documento" not in s[0][1] and "Añadir un recurso" not in s[0][1], s)
        s = mensaje(b, EDUMEDIA, "/biblioteca")
        ok &= comprobar("EduMedia-IAG: /biblioteca remite a ChatGPT-IA-edu", s and "t.me/ChatGPTedu" in s[0][1], s)
        s = mensaje(b, EDUMEDIA, "/repositorio")
        ok &= comprobar("EduMedia-IAG: /repositorio remite a VCE", s and "t.me/vceduca" in s[0][1], s)
        s = mensaje(b, 999, "/ayuda")
        ok &= comprobar("quien no es de ningún grupo: los tres enlaces", s and "t.me/EduMediaIAG" in s[0][1], s)

        # /buscar: casillas de grupo; lo marcado se mantiene en la conversación y cada respuesta lo recuerda
        b.recientes.clear(); b.lenguas.clear(); b.ambitos.clear()
        s = mensaje(b, AMBOS, "/buscar")
        botones = [x for fila in (s[-1][2] or {}).get("inline_keyboard", []) for x in fila] if s else []
        ok &= comprobar("/buscar: una casilla por grupo, todas marcadas, sin «Todos»",
                        [x["callback_data"] for x in botones] == ["g:chatgpt", "g:vce", "g:edumedia"]
                        and all(x["text"].startswith("✅") for x in botones)
                        and all(len(fila) == 1 for fila in s[-1][2]["inline_keyboard"]), s)
        boton(b, AMBOS, "g:chatgpt")
        casillas = [x["text"] for fila in b.tg.editados[-1]["reply_markup"]["inline_keyboard"] for x in fila]
        ok &= comprobar("al tocar ChatGPT-IA-edu se desmarca en el mismo mensaje",
                        casillas == ["⬜ ChatGPT-IA-edu", "✅ Vibe Coding Educativo", "✅ EduMedia-IAG"], [])
        boton(b, AMBOS, "g:edumedia")
        s = boton(b, AMBOS, "g:vce")
        ok &= comprobar("no deja desmarcar el último", s and "al menos un grupo" in s[-1][1]
                        and b.ambito(AMBOS) == {"vce"}, s)
        s = mensaje(b, AMBOS, "consulta")
        ok &= comprobar("la respuesta recuerda dónde busca", s and s[-1][1].startswith("_Buscando en: Vibe"), s)
        s = mensaje(b, AMBOS, "consulta")
        ok &= comprobar("y se mantiene en la pregunta siguiente", s and "Buscando en: Vibe" in s[-1][1], s)
        boton(b, AMBOS, "g:chatgpt")
        s = mensaje(b, AMBOS, "consulta")
        ok &= comprobar("con dos de tres, los nombra", s and s[-1][1].startswith("_Buscando en: ChatGPT-IA-edu, Vibe"), s)
        boton(b, AMBOS, "g:edumedia")
        s = mensaje(b, AMBOS, "consulta")
        ok &= comprobar("con todos marcados, sin aviso", b.ambito(AMBOS) is None and s and "Buscando en" not in s[-1][1], s)
        b.ambitos[AMBOS] = (b.ambitos.get(AMBOS, (0, None))[0] - 31 * 60, {"vce"})
        s = mensaje(b, AMBOS, "consulta")
        ok &= comprobar("tras 30 minutos sin escribir, vuelve a todos", s and "Buscando en" not in s[-1][1], s)

        # Biblioteca: al publicar, 48 horas para quitarlo (documento y ficha)
        b.pendientes[CHATGPT] = {"ficha": "**GUÍA DE PRUEBA**\nFicha de prueba.", "file_id": "x", "autor": "Ana",
                                 "compartir": True, "momento": time.time()}
        s = boton(b, CHATGPT, "publicar")
        # Lo que recibe el autor: después va también el aviso a Juanjo de lo publicado (commit 8c58dda).
        suyo = next((m for m in reversed(s or []) if m[0] == CHATGPT and m[2]), None)
        quitar = next((x["callback_data"] for fila in (suyo[2] or {}).get("inline_keyboard", []) for x in fila
                       if x["callback_data"].startswith("bq:")), "") if suyo else ""
        ok &= comprobar("publicar en la Biblioteca ofrece quitarlo durante 48 horas",
                        bool(quitar) and "48 horas" in suyo[1] and len(quitar.split(":")[2].split("-")) == 2, s)
        antes = len(b.tg.borrados)
        s = boton(b, CHATGPT, quitar)
        ok &= comprobar("«Quitarlo de la Biblioteca» borra el documento y la ficha",
                        len(b.tg.borrados) - antes == 2 and any("Quitado de la Biblioteca" in m[1] for m in s
                                                                 if m[0] == CHATGPT), s)
    print("\nTodo bien" if ok else "\nHay fallos")
    return ok


if __name__ == "__main__":
    t0 = time.time()
    sys.exit(0 if main() else 1)
