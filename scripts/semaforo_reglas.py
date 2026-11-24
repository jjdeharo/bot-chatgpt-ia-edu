#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Semáforo de privacidad (ADR 0053): las reglas. De lo que semaforo_auditar.py vio de una
aplicación al color que va a la hoja del repositorio, con los criterios del anexo I de las
Orientaciones del INTEF (v3.0, junio 2026): VERDE si no trata datos personales, AMARILLO si
los trata (servicios de datos, inicio de sesión, contadores de visitas, envíos a servidores
ajenos), ROJO si sigue a quien la visita con analítica comercial. Viene de la guía de
privacidad (su ADR 0006). Las fichas de escenarios siguen el formato de la guía del INTEF
aunque aquí solo se usan el color y la evidencia.
"""

from __future__ import annotations

import re
import unicodedata
from datetime import date
from urllib.parse import urlparse

# Dominios de backend real (excluye api.github.com que solo lee metadatos/versión pública)
BACKENDS_REALES = {
    "firestore.googleapis.com",
    "identitytoolkit.googleapis.com",
    "securetoken.googleapis.com",
    "firebaseio.com",
    "supabase.co",
    "script.google.com",
    "geody.onrender.com",
    "0.peerjs.com",
    "peerjs.com",
}

# Analítica comercial de terceros con seguimiento de personas (ROJO). Se compara por sufijo:
# «region1.google-analytics.com» cuenta como «google-analytics.com».
ANALITICA_COMERCIAL = {
    "facebook.net",
    "connect.facebook.net",
    "hotjar.com",
    "clarity.ms",
    "mixpanel.com",
    "segment.io",
    "heap.io",
    "mc.yandex.ru",
    "google-analytics.com",
    "region1.google-analytics.com",
    "www.googletagmanager.com",
    "googletagmanager.com",
    "api2.amplitude.com",
    "sr-client-cfg.amplitude.com",
}

# Dominios de Canva Sites (el INTEF valora Canva como AMARILLO)
DOMINIOS_CANVA = (".my.canva.site", "canvacode.com")

# Licencias libres o de código abierto reconocidas
RE_LICENCIA_LIBRE = re.compile(
    r"(agpl|gpl|lgpl|mit\b|apache|bsd|mpl|isc|eupl|unlicense|cc0|código abierto|software libre|open source|dominio público)",
    re.I,
)


def es_comercial(host: str) -> bool:
    return any(host == d or host.endswith("." + d) for d in ANALITICA_COMERCIAL)


def fecha_de(r: dict, por_defecto: str) -> str:
    """La fecha en que se inspeccionó esta aplicación, en dd/mm/aaaa."""
    f = r.get("fecha_auditoria") or ""
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", f):
        a, m, d = f.split("-")
        return f"{d}/{m}/{a}"
    return por_defecto


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def slugify(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:64] or "app-vce"


def mapear_categoria_vce(tipo: str, areas: str) -> str:
    """Asigna una categoría legible y coherente con el buscador a partir del tipo de recurso VCE."""
    t = (tipo or "").split(",")[0].strip()
    if t:
        return f"VCE · {t}"
    a = (areas or "").split(",")[0].strip()
    if a:
        return f"VCE · {a}"
    return "VCE · Otros recursos"


def evaluar_app(r: dict, fecha_es: str) -> dict | None:
    """
    Devuelve la estructura normalizada compatible con guia-intef.json o None si no es
    evaluable como aplicación web (repositorios de código en github.com, HTTP 404, descargas).
    """
    http = r.get("http_status", 0)
    if r.get("error") or http == 0 or http >= 400:
        return None
    fecha_es = fecha_de(r, fecha_es)

    url_final = r.get("url_final") or r["url"]
    host = urlparse(url_final).netloc.lower()
    if host == "github.com":
        return None

    terc = r.get("terceros", {})
    analitica = list(terc.get("analitica", []))
    backends = [b for b in terc.get("backend_api", []) if b != "api.github.com"]
    fuentes = list(terc.get("fuentes_externas", []))
    cdns = list(terc.get("cdn_librerias", []))
    medios = list(terc.get("medios_mapas", []))
    otros_terc = list(terc.get("otros_terceros", []))
    senales = list(r.get("senales_codigo", []))
    # Contadores de visitas y analítica sin fines comerciales (Umami, Plausible, Matomo,
    # contadores gratuitos, telemetría de errores): tratan la IP y datos del dispositivo (AMARILLO).
    YA_TRATADOS = {"googleads.g.doubleclick.net", "static.doubleclick.net", "static.cloudflareinsights.com"}
    contadores = sorted({a for a in analitica if not es_comercial(a) and a not in YA_TRATADOS})
    # Lo que la página MANDA a un servidor ajeno (POST o balizas), aunque no sea un servicio conocido.
    conocidos = set(backends) | set(analitica)
    envios = sorted({h for h in r.get("envios_terceros", []) if h not in conocidos})
    if "umami" in senales:  # el contador Umami manda cada visita a su servidor, sea cual sea el dominio
        contadores = sorted(set(contadores) | set(envios)) or ["contador Umami"]
        envios = []
    inputs = list(r.get("inputs_personales", []))
    cookies = list(r.get("cookies", []))

    es_libre = "SI" if RE_LICENCIA_LIBRE.search(r.get("licencia", "")) else "X"
    es_embebible = "SI" if r.get("embebible", True) else "X"

    escenarios = []
    evidencia = []

    # 1. Plataformas externas concretas (coherentes con las valoraciones del INTEF v3.0)
    if host == "chatgpt.com" or host.endswith(".chatgpt.com"):
        evidencia.append("Alojada en ChatGPT (OpenAI). Valoración alineada con la ficha oficial de ChatGPT en la guía del INTEF.")
        escenarios = [
            {
                "semaforo": "VERDE",
                "software_libre": es_libre,
                "requiere_registro": "Puede emplearse con y sin registro.",
                "otros": "Recurso del repositorio VCE alojado en ChatGPT (OpenAI). " + (f"Licencia declarada: {r['licencia']}." if r.get("licencia") else ""),
                "enlaces_otros": [],
                "politica_privacidad_texto": "https://openai.com/policies/eu-privacy-policy/",
                "enlaces_privacidad": ["https://openai.com/policies/eu-privacy-policy/"],
                "fecha_comprobacion": fecha_es,
                "profesorado": "Siempre y cuando se utilice la opción sin registro, no se aporte ningún dato de carácter personal y se sigan las Advertencias y Orientaciones del INTEF.",
                "alumnado": "Siempre y cuando se cumplan, referidos al alumnado, los requisitos establecidos en el apartado «Profesorado».",
                "embebible": "X",
                "accesibilidad_texto": "X",
                "enlaces_accesibilidad": [],
            },
            {
                "semaforo": "AMARILLO",
                "software_libre": es_libre,
                "requiere_registro": "SÍ (con cuenta de OpenAI).",
                "otros": "Evaluación técnica orientativa (Anexo I del INTEF) si se usa con registro.",
                "enlaces_otros": [],
                "politica_privacidad_texto": "https://openai.com/policies/eu-privacy-policy/",
                "enlaces_privacidad": ["https://openai.com/policies/eu-privacy-policy/"],
                "fecha_comprobacion": fecha_es,
                "profesorado": "Con registro, requiere evaluación previa y autorización del centro o Administración Educativa siguiendo las Advertencias y Orientaciones.",
                "alumnado": "No debe registrarse el alumnado salvo autorización expresa del centro y cumplimiento de todos los requisitos legales.",
                "embebible": "X",
                "accesibilidad_texto": "X",
                "enlaces_accesibilidad": [],
            },
        ]

    elif host in ("gemini.google.com", "g.co", "aistudio.google.com", "ai.studio", "accounts.google.com"):
        evidencia.append(f"Alojada en servicios de Google ({host}). Requiere cuenta de Google; alineada con la ficha de Gemini del INTEF.")
        escenarios = [{
            "semaforo": "AMARILLO",
            "software_libre": es_libre,
            "requiere_registro": "SÍ (cuenta de Google).",
            "otros": f"Recurso del repositorio VCE alojado en Google ({host}). Sujeto a la política de privacidad de Google.",
            "enlaces_otros": [],
            "politica_privacidad_texto": "https://policies.google.com/privacy?hl=es",
            "enlaces_privacidad": ["https://policies.google.com/privacy?hl=es"],
            "fecha_comprobacion": fecha_es,
            "profesorado": "Requiere cuenta de Google. Utilizar únicamente si el centro o la Administración Educativa dispone de acuerdo/autorización y siguiendo las Advertencias y Orientaciones.",
            "alumnado": "Solo si cuenta con autorización del centro y cuenta corporativa gestionada, sin aportar datos personales innecesarios.",
            "embebible": "X",
            "accesibilidad_texto": "X",
            "enlaces_accesibilidad": [],
        }]

    elif host == "claude.ai" or host.endswith(".claude.ai"):
        evidencia.append("Alojada en Claude (Anthropic). Alineada con la ficha de Claude en la guía del INTEF.")
        escenarios = [{
            "semaforo": "AMARILLO",
            "software_libre": es_libre,
            "requiere_registro": "SÍ (puede permitir visualización sin registro, pero la interacción requiere cuenta).",
            "otros": "Recurso del repositorio VCE alojado en Claude (Anthropic).",
            "enlaces_otros": [],
            "politica_privacidad_texto": "https://www.anthropic.com/legal/privacy",
            "enlaces_privacidad": ["https://www.anthropic.com/legal/privacy"],
            "fecha_comprobacion": fecha_es,
            "profesorado": "Seguir lo establecido en las Advertencias y Orientaciones del INTEF; en caso de uso con cuenta, requiere autorización previa del centro.",
            "alumnado": "No debe registrarse el alumnado; en su caso, solo visualizar contenido público sin aportar datos personales.",
            "embebible": "X",
            "accesibilidad_texto": "X",
            "enlaces_accesibilidad": [],
        }]

    elif host == "sites.google.com":
        evidencia.append("Alojada en Google Sites. Infraestructura de Google; conviene comprobar los elementos incrustados.")
        escenarios = [{
            "semaforo": "AMARILLO",
            "software_libre": es_libre,
            "requiere_registro": "NO (para visualizar); plataforma gestionada por Google.",
            "otros": "Recurso del repositorio VCE publicado en Google Sites. Se recomienda verificar que no incorpore formularios o recursos que recojan datos del alumnado.",
            "enlaces_otros": [],
            "politica_privacidad_texto": "https://policies.google.com/privacy?hl=es",
            "enlaces_privacidad": ["https://policies.google.com/privacy?hl=es"],
            "fecha_comprobacion": fecha_es,
            "profesorado": "Siguiendo siempre lo establecido en los apartados Advertencias y Orientaciones, comprobando si el centro dispone de cobertura para servicios de Google.",
            "alumnado": "No aportar datos personales y cumplir los requisitos establecidos para el profesorado.",
            "embebible": es_embebible,
            "accesibilidad_texto": "X",
            "enlaces_accesibilidad": [],
        }]

    elif any(host.endswith(d) for d in DOMINIOS_CANVA) or (host == "eaciweb.net" and ("o13855.ingest.us.sentry.io" in analitica or any("canva" in c.get("domain", "") for c in cookies))):
        evidencia.append(f"Alojada o servida mediante Canva ({host}); carga telemetría de Canva (Sentry/Cloudflare). Alineada con Canva en la guía del INTEF (AMARILLO).")
        escenarios = [{
            "semaforo": "AMARILLO",
            "software_libre": es_libre,
            "requiere_registro": "NO (para visualizar); servida desde Canva.",
            "otros": "Recurso publicado en Canva Sites / Canva Code; carga telemetría técnica del proveedor (Sentry y Cloudflare). Valoración alineada con Canva en el INTEF.",
            "enlaces_otros": [],
            "politica_privacidad_texto": "https://www.canva.com/es_es/politicas-legales/privacy-policy/",
            "enlaces_privacidad": ["https://www.canva.com/es_es/politicas-legales/privacy-policy/"],
            "fecha_comprobacion": fecha_es,
            "profesorado": "Requiere tener en cuenta las condiciones de Canva y seguir lo establecido en los apartados Advertencias y Orientaciones.",
            "alumnado": "Solo consulta sin registro ni aportación de datos personales y cumpliendo los requisitos del apartado Profesorado.",
            "embebible": es_embebible,
            "accesibilidad_texto": "X",
            "enlaces_accesibilidad": [],
        }]

    # 2. Analítica comercial real (ROJO)
    elif any(es_comercial(a) for a in analitica):
        encontrados = sorted({a for a in analitica if es_comercial(a)})
        evidencia.append(f"Carga analítica comercial de seguimiento de terceros: {', '.join(encontrados)}.")
        escenarios = [{
            "semaforo": "ROJO",
            "software_libre": es_libre,
            "requiere_registro": "NO",
            "otros": f"En la inspección técnica en navegador se detectó carga de analítica comercial de terceros ({', '.join(encontrados)}).",
            "enlaces_otros": [],
            "politica_privacidad_texto": "No verificada en esta inspección automatizada.",
            "enlaces_privacidad": [],
            "fecha_comprobacion": fecha_es,
            "profesorado": "No se recomienda su uso mientras mantenga seguimiento de analítica comercial de terceros sin consentimiento ni cobertura legal. Si el docente decide consultarla, lo hará bajo su responsabilidad.",
            "alumnado": "NO debe ser empleada por el alumnado mientras realice seguimiento mediante analítica de terceros.",
            "embebible": es_embebible,
            "accesibilidad_texto": "X",
            "enlaces_accesibilidad": [],
        }]

    # 3. Backends reales, login propio, Apps Script, PeerJS o vídeo YouTube / telemetría Cloudflare (AMARILLO)
    elif (
        any(b in BACKENDS_REALES for b in backends)
        or host in ("pasos.edumind.es", "liga.edumind.es", "script.google.com")
        or ("firebase" in senales and "github_navega" not in url_final)
        or "google_forms" in senales
        or ("googleads.g.doubleclick.net" in analitica)
        or ("static.cloudflareinsights.com" in analitica)
        or contadores
        or envios
    ):
        detalles = []
        if host in ("pasos.edumind.es", "liga.edumind.es"):
            detalles.append("Exige inicio de sesión en servidor propio")
        if host == "script.google.com" or "script.google.com" in backends or "google_forms" in senales:
            detalles.append("Utiliza Google Apps Script / servicios de Google")
        fb = [b for b in backends if "firestore" in b or "firebase" in b or "identitytoolkit" in b]
        if fb or ("firebase" in senales and "github_navega" not in url_final):
            detalles.append("Conecta con Firebase / Firestore (Google)")
        if "geody.onrender.com" in backends:
            detalles.append("Conecta con servidor externo propio (geody.onrender.com)")
        if any("peerjs" in b for b in backends):
            detalles.append("Utiliza servidor de señalización PeerJS (0.peerjs.com) para conexión entre dispositivos")
        if "googleads.g.doubleclick.net" in analitica:
            detalles.append("Incluye vídeo de YouTube embebido que realiza peticiones a doubleclick.net")
        if "static.cloudflareinsights.com" in analitica:
            detalles.append("Carga analítica web sin cookies de Cloudflare (cloudflareinsights.com)")
        if contadores:
            detalles.append("Envía datos de cada visita (página, idioma, pantalla, IP) a un contador de visitas o servicio de analítica (" + ", ".join(contadores[:3]) + ")")
        if envios:
            detalles.append("Envía datos a un servidor externo (" + ", ".join(envios[:3]) + ")")

        evidencia.extend(detalles)
        pide_reg = "SÍ" if host in ("pasos.edumind.es", "liga.edumind.es") else "NO (o según función)"
        escenarios = [{
            "semaforo": "AMARILLO",
            "software_libre": es_libre,
            "requiere_registro": pide_reg,
            "otros": "Inspección técnica (Anexo I): " + "; ".join(detalles) + ".",
            "enlaces_otros": [],
            "politica_privacidad_texto": "Consultar aviso legal / privacidad en la propia aplicación.",
            "enlaces_privacidad": [],
            "fecha_comprobacion": fecha_es,
            "profesorado": "Antes de emplearla con datos reales del alumnado, comprobar qué datos se envían al servicio externo y solicitar valoración del centro siguiendo las Advertencias y Orientaciones.",
            "alumnado": "No introducir datos personales reales salvo autorización expresa del centro y cumplimiento de los requisitos del apartado Profesorado.",
            "embebible": es_embebible,
            "accesibilidad_texto": "X",
            "enlaces_accesibilidad": [],
        }]

    # 4. VERDE (autocontenida o estática con CDN/fuentes externas, sin registro ni envío de datos)
    else:
        notas = []
        if not fuentes and not cdns and not otros_terc and not medios:
            notas.append("Web estática autocontenida: sin registro, sin analítica ni peticiones a servidores externos.")
        else:
            partes_ext = []
            if fuentes:
                partes_ext.append("tipografías externas (" + ", ".join(sorted(set(fuentes))[:3]) + ")")
            if cdns:
                partes_ext.append("bibliotecas desde CDN (" + ", ".join(sorted(set(cdns))[:3]) + ")")
            if medios:
                partes_ext.append("medios o mapas externos (" + ", ".join(sorted(set(medios))[:2]) + ")")
            if otros_terc:
                partes_ext.append("recursos estáticos de terceros (" + ", ".join(sorted(set(otros_terc))[:2]) + ")")
            notas.append("Aplicación estática en el navegador sin registro ni envío de datos personales; carga " + "; ".join(partes_ext) + ".")

        # Aviso específico si ofrece campos locales para nombres del alumnado (p. ej. AulaMap, Rúbrica)
        tiene_nombres_locales = any(
            re.search(r"(student|alumno|alumne|nombre)", inp, re.I) for inp in inputs
        )
        if tiene_nombres_locales:
            notas.append("Incluye campos locales para nombres en el navegador: los datos no salen del dispositivo, pero conviene evitar datos reales del alumnado fuera de dispositivos del centro o usar códigos.")

        evidencia.extend(notas)
        escenarios = [{
            "semaforo": "VERDE",
            "software_libre": es_libre,
            "requiere_registro": "NO",
            "otros": " ".join(notas),
            "enlaces_otros": [],
            "politica_privacidad_texto": "No realiza tratamiento remoto de datos personales según la inspección técnica en navegador.",
            "enlaces_privacidad": [],
            "fecha_comprobacion": fecha_es,
            "profesorado": "Siempre y cuando no se aporten datos de carácter personal y se sigan los apartados Advertencias y Orientaciones del INTEF.",
            "alumnado": "Siempre y cuando se cumplan, referidos al alumnado, los requisitos establecidos en el apartado «Profesorado».",
            "embebible": es_embebible,
            "accesibilidad_texto": "X",
            "enlaces_accesibilidad": [],
        }]

    cat_vce = mapear_categoria_vce(r.get("tipo", ""), r.get("areas", ""))
    return {
        "titulo": r["titulo"],
        "autor": r.get("autor", ""),
        "url": r["url"],
        "url_final": url_final,
        "descripcion": r.get("descripcion", ""),
        "categoria": cat_vce,
        "categoria_id": slugify(cat_vce),
        "subcategoria": r.get("areas") or None,
        "niveles": r.get("niveles", ""),
        "idiomas": r.get("idiomas", ""),
        "licencia": r.get("licencia", ""),
        "evidencia": evidencia,
        "escenarios": escenarios,
    }


def motivo_no_evaluable(r: dict) -> str:
    http = r.get("http_status", 0)
    host = urlparse(r.get("url_final") or r["url"]).netloc.lower()
    if host == "github.com" and not r.get("error") and 0 < http < 400:
        return "Enlaza al código en GitHub, no a una aplicación que se pueda abrir."
    if http >= 400:
        return f"La página no se abre (error {http})."
    return "La página no se abre."


def semaforo_resumido(escenarios: list[dict]) -> str:
    """VERDE, AMARILLO, ROJO o, si hay dos escenarios (sin y con registro), «VERDE/AMARILLO»."""
    vistos = []
    for e in escenarios:
        if e.get("semaforo") and e["semaforo"] not in vistos:
            vistos.append(e["semaforo"])
    return "/".join(vistos) or "SIN EVALUAR"


def resumen(r: dict, hoy: date | None = None) -> dict:
    """De lo que se vio de una aplicación a lo que va a la hoja: {"semaforo", "motivo", "fecha"}."""
    fecha = r.get("fecha_auditoria") or (hoy or date.today()).isoformat()
    evaluada = evaluar_app(r, fecha_de({"fecha_auditoria": fecha}, (hoy or date.today()).strftime("%d/%m/%Y")))
    if not evaluada:
        return {"semaforo": "SIN EVALUAR", "motivo": motivo_no_evaluable(r), "fecha": fecha}
    return {"semaforo": semaforo_resumido(evaluada["escenarios"]),
            "motivo": " ".join(evaluada["evidencia"])[:300], "fecha": fecha}
