#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Semáforo de privacidad (ADR 0053): inspección técnica de las aplicaciones del Repositorio de
Vibe Coding Educativo en un navegador real, para aplicar después los criterios del anexo I del
INTEF (v3.0, junio 2026) en semaforo_reglas.py. Viene de la guía de privacidad (su ADR 0006),
que desde el 24-11-2026 es solo del INTEF.

De cada aplicación anota, sin decidir el semáforo:
  - redirecciones reales y estado HTTP;
  - peticiones a terceros, clasificadas (analítica, servicios de datos, tipografías,
    bibliotecas, medios, otros) y, aparte, las que ENVÍAN algo (POST, balizas);
  - cookies, inicio de sesión, campos de datos personales y señales en el código;
  - cabeceras que impiden incrustarla.

El navegador no entra en la red de casa: cualquier petición a una dirección privada se corta
(las aplicaciones las manda cualquiera, y esto corre en el NAS).
Se usa desde semaforo.py. Necesita Playwright con su Chromium.
"""

from __future__ import annotations

import asyncio
import csv
import io
import ipaddress
import json
import re
import socket
import urllib.request
from datetime import date
from urllib.parse import urlparse

CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vSj_hltRI4Q0QolINWJVcKxCMMjfpdiCkKzSdgp9d8RlGTdUU1UIKvaj"
    "-TBSkq0JQGneDhfUkSQuFzy/pub?output=csv"
)
COL_URL = "Enlace (URL) a la aplicación"

# Clasificación de dominios de terceros observados en el tráfico de red
PATRON_ANALITICA = re.compile(
    r"(google-analytics\.com|googletagmanager\.com|analytics\.google\.com|doubleclick\.net|"
    r"googlesyndication\.com|facebook\.net|connect\.facebook|clarity\.ms|hotjar\.com|"
    r"matomo|plausible\.io|umami\.is|statcounter\.com|mixpanel\.com|segment\.io|"
    r"amplitude\.com|heap\.io|sentry\.io|cloudflareinsights\.com|mc\.yandex\.ru|"
    r"freecounterstat\.com|optistats\.ovh|easycounter\.com|goatcounter\.com)",
    re.I,
)
PATRON_BACKEND_API = re.compile(
    r"(firebaseio\.com|firestore\.googleapis\.com|identitytoolkit\.googleapis\.com|"
    r"securetoken\.googleapis\.com|supabase\.co|api\.openai\.com|generativelanguage\.googleapis\.com|"
    r"api\.anthropic\.com|api\.mistral\.ai|api\.groq\.com|openrouter\.ai|"
    r"script\.google\.com|docs\.google\.com/forms|forms\.gle|airtable\.com|"
    r"formspree\.io|emailjs\.com|webhooks|discord\.com/api/webhooks|api\.telegram\.org|"
    r"firebaseapp\.com|cloudfunctions\.net|api\.github\.com|pusher\.com|ably\.io|"
    r"peerjs\.com|0\.peerjs\.com|socket\.io)",
    re.I,
)
PATRON_FUENTES = re.compile(r"(fonts\.googleapis\.com|fonts\.gstatic\.com|use\.typekit\.net|fonts\.bunny\.net)", re.I)
PATRON_CDN = re.compile(
    r"(cdn\.jsdelivr\.net|cdnjs\.cloudflare\.com|unpkg\.com|cdn\.tailwindcss\.com|"
    r"esm\.sh|code\.jquery\.com|stackpath\.bootstrapcdn\.com|maxcdn\.bootstrapcdn\.com|"
    r"kit\.fontawesome\.com|ga\.jspm\.io|cdn\.skypack\.dev|cdn\.plot\.ly|"
    r"ajax\.googleapis\.com|cdn\.bootcdn|cdn\.mathjax\.org|polyfill\.io|"
    r"cdn\.sheetjs\.com|cdn\.babylonjs\.com|threejs\.org|cdn\.ckeditor\.com|"
    r"pyodide|cdn\.datatables\.net|cdn\.quilljs\.com)",
    re.I,
)
PATRON_MEDIOS = re.compile(
    r"(tile\.openstreetmap\.org|openstreetmap\.org|cartocdn\.com|arcgisonline\.com|"
    r"youtube\.com|youtu\.be|ytimg\.com|youtube-nocookie\.com|vimeo\.com|wikimedia\.org|wikipedia\.org|"
    r"unsplash\.com|pexels\.com|pixabay\.com|iconify\.design|api\.iconify\.design|"
    r"pollinations\.ai|cataas\.com|archive\.org)",
    re.I,
)


_PUBLICOS: dict[str, bool] = {}


def host_publico(host: str) -> bool:
    """¿Todas las direcciones del nombre son públicas? Sin resolver, no: mejor cortar que entrar en casa."""
    host = (host or "").split(":")[0].strip("[]").lower()
    if not host:
        return False
    if host in _PUBLICOS:
        return _PUBLICOS[host]
    try:
        ips = {ai[4][0] for ai in socket.getaddrinfo(host, None)}
        ok = bool(ips) and all(ipaddress.ip_address(ip.split("%")[0]).is_global for ip in ips)
    except (OSError, ValueError):
        ok = False
    _PUBLICOS[host] = ok
    return ok


def url_publica(url: str) -> bool:
    u = urlparse(url or "")
    return u.scheme in ("http", "https") and host_publico(u.hostname or "")


TOPE_S = 75  # segundos como mucho por aplicación


def version_web(url: str) -> str | None:
    """Si el enlace es un repositorio de GitHub que publica una web (su página de inicio o GitHub Pages), esa web.
    Un paquete de npm o el propio GitHub no cuentan: no son una aplicación que se use en el navegador."""
    u = urlparse(url)
    if u.netloc.lower() != "github.com":
        return None
    partes = [x for x in u.path.split("/") if x]
    if len(partes) < 2:
        return None
    dueno, repo = partes[0], partes[1].removesuffix(".git")
    try:
        pet = urllib.request.Request(f"https://api.github.com/repos/{dueno}/{repo}",
                                     headers={"Accept": "application/vnd.github+json", "User-Agent": "semaforo-vce"})
        with urllib.request.urlopen(pet, timeout=20) as r:
            d = json.load(r)
    except Exception:  # noqa: BLE001 — sin la API, se queda como repositorio
        return None
    web = (d.get("homepage") or "").strip()
    if web.startswith(("http://", "https://")) and not re.search(r"(github\.com|npmjs\.com)", web, re.I):
        return web
    if d.get("has_pages"):
        return f"https://{dueno.lower()}.github.io/{repo}/"
    return None


def dominio_base(host: str) -> str:
    partes = host.lower().split(":")[0].split(".")
    return ".".join(partes[-2:]) if len(partes) >= 2 else host.lower()


def normalizar_url(u: str) -> str:
    return (u or "").strip().rstrip("/").lower()


def cargar_csv(url: str = CSV_URL) -> list[dict]:
    """Las aplicaciones activas de la hoja del repositorio, con sus columnas tal cual."""
    raw = urllib.request.urlopen(url, timeout=60).read().decode("utf-8", errors="ignore")
    rows = list(csv.DictReader(io.StringIO(raw)))
    if not rows:
        return []
    cols = list(rows[0].keys())
    # Restos del antiguo formulario (cerrado el 27-10-2026): filas que pedían borrar otra.
    col_del_flag = next((c for c in cols if "QUIERES ELIMINAR" in c.upper()), None)
    col_del_url = next((c for c in cols if "Marca la casilla" in c), None)
    eliminadas = set()
    for r in rows:
        flag = (r.get(col_del_flag, "") if col_del_flag else "").strip().lower()
        du = (r.get(col_del_url, "") if col_del_url else "").strip()
        if flag in ("sí", "si", "yes") and du:
            eliminadas.add(normalizar_url(du))

    activas, vistas = [], set()
    for r in reversed(rows):
        u = (r.get(COL_URL) or "").strip()
        n = normalizar_url(u)
        if not u.startswith(("http://", "https://")) or n in eliminadas or n in vistas:
            continue
        vistas.add(n)
        activas.append({
            "fecha": (r.get("Marca temporal") or "").strip(),
            "autor": (r.get("Tu nombre (Autor/a de la aplicación)") or "").strip(),
            "titulo": (r.get("Título de la aplicación") or "").strip(),
            "url": u,
            "descripcion": (r.get("Descripción breve") or "").strip(),
            "tipo": (r.get("Tipo de recurso") or "").strip(),
            "niveles": (r.get("Nivel o niveles educativos") or "").strip(),
            "areas": (r.get("Área o áreas de conocimiento") or "").strip(),
            "licencia": (r.get("Licencia de uso") or "").strip(),
            "idiomas": (r.get("Idiomas de la aplicación") or "").strip(),
            "hoja": r,
        })
    return activas


def clasificar_recurso(url_req: str, host_pagina: str) -> tuple[str, str]:
    parsed = urlparse(url_req)
    host = parsed.netloc.lower()
    if not host or host == host_pagina or url_req.startswith(("data:", "blob:", "about:")):
        return "propio", host
    # Mismo sitio si comparten dominio base (bilateria.org y www.bilateria.org),
    # salvo en *.github.io, donde cada subdominio es de otra persona.
    if not host.endswith(".github.io") and dominio_base(host) == dominio_base(host_pagina):
        return "propio", host
    if PATRON_ANALITICA.search(url_req):
        return "analitica", host
    if PATRON_BACKEND_API.search(url_req):
        return "backend_api", host
    if PATRON_FUENTES.search(url_req):
        return "fuentes_externas", host
    if PATRON_CDN.search(url_req):
        return "cdn_librerias", host
    if PATRON_MEDIOS.search(url_req):
        return "medios_mapas", host
    return "otros_terceros", host


JS_DOM = """() => {
  const bodyTxt = (document.body ? document.body.innerText : "").slice(0, 6000);
  const htmlSrc = document.documentElement ? document.documentElement.outerHTML.slice(0, 80000) : "";
  const loginRe = /(iniciar sesi[oó]n|sign in|log in|acceder con google|continue with google|crea una cuenta|create account)/i;
  const pideLogin = loginRe.test(bodyTxt) || Boolean(document.querySelector('input[type="password"]'));
  const inputsPers = [];
  document.querySelectorAll('input, textarea').forEach(el => {
    const t = (el.getAttribute('type') || 'text').toLowerCase();
    const meta = [el.name, el.id, el.placeholder, el.getAttribute('aria-label')].filter(Boolean).join(' ');
    if (t === 'email' || t === 'password' || t === 'tel') {
      inputsPers.push(t + (meta ? ':' + meta.slice(0, 25) : ''));
    } else if (/(correo|e-?mail|apellido|dni|tel[eé]fono|nombre del alumno|nom de l'alumne|student name)/i.test(meta)) {
      inputsPers.push(meta.slice(0, 35));
    }
  });
  const tienePriv = /(pol[ií]tica de privac|privacidad|privacitat|privacidade|pribatutasun|privacy policy|rgpd|gdpr)/i.test(bodyTxt);
  const senales = [];
  if (/firebase(app|io|store)|initializeApp\\s*\\(/i.test(htmlSrc)) senales.push('firebase');
  if (/supabase\\.co|createClient\\s*\\(/i.test(htmlSrc)) senales.push('supabase');
  if (/docs\\.google\\.com\\/forms|forms\\.gle/i.test(htmlSrc)) senales.push('google_forms');
  if (/(api\\.openai\\.com|generativelanguage\\.googleapis\\.com|api\\.anthropic\\.com)/i.test(htmlSrc)) senales.push('api_ia_directa');
  if (/gtag\\s*\\(|google-analytics|googletagmanager/i.test(htmlSrc)) senales.push('gtag');
  if (/data-website-id/i.test(htmlSrc)) senales.push('umami');
  return { title: document.title || "", pideLogin, inputsPers: inputsPers.slice(0, 8), tienePriv, senales };
}"""


async def auditar_una(sem: asyncio.Semaphore, browser, app: dict) -> dict:
    async with sem:
        res = {k: v for k, v in app.items() if k != "hoja"}
        res.update({
            "url_final": app["url"],
            "http_status": 0,
            "error": None,
            "titulo_html": "",
            "embebible": True,
            "cabeceras_frame": {},
            "terceros": {k: [] for k in (
                "analitica", "backend_api", "fuentes_externas", "cdn_librerias", "medios_mapas", "otros_terceros")},
            "envios_terceros": [],
            "cookies": [],
            "pide_login": False,
            "inputs_personales": [],
            "tiene_privacidad": False,
            "senales_codigo": [],
            "fecha_auditoria": date.today().isoformat(),
        })
        context = None
        try:
            context = await browser.new_context(
                locale="es-ES",
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
                ignore_https_errors=True,
            )
            async def guardia(route):
                url_r = route.request.url
                if url_r.startswith(("data:", "blob:")):
                    return await route.continue_()
                host = urlparse(url_r).hostname or ""
                if not await asyncio.to_thread(host_publico, host):
                    res.setdefault("bloqueadas", []).append(host)
                    return await route.abort()
                # Imágenes, vídeos y tipografías no cambian el color: basta saber a qué servidor se piden (la
                # petición ya consta), sin descargarlas. Así la pasada baja mucho lo que gasta de la fibra.
                if route.request.resource_type in ("image", "media", "font"):
                    return await route.abort()
                await route.continue_()

            await context.route("**/*", guardia)
            page = await context.new_page()
            peticiones: list[tuple[str, str, str]] = []
            page.on("request", lambda req: peticiones.append((req.url, req.method, req.resource_type)))

            destino = app["url"]
            web = await asyncio.to_thread(version_web, destino)
            if web and url_publica(web):
                res["version_web"] = destino = web
            resp = await page.goto(destino, wait_until="domcontentloaded", timeout=25000)
            # Los contadores de visitas mandan su aviso al acabar de cargar: se espera la carga, pero no más
            # de 10 s (hay páginas que no la terminan nunca, como un juego que no para), y luego 3,5 s más.
            try:
                await page.wait_for_load_state("load", timeout=10000)
            except Exception:  # noqa: BLE001 — sin carga completa, se sigue con lo que se haya visto
                pass
            await page.wait_for_timeout(3500)

            res["url_final"] = page.url
            if resp:
                res["http_status"] = resp.status
                hdrs = {k.lower(): v for k, v in resp.headers.items()}
                xfo = hdrs.get("x-frame-options", "")
                csp = hdrs.get("content-security-policy", "")
                if xfo:
                    res["cabeceras_frame"]["x-frame-options"] = xfo
                    if any(w in xfo.lower() for w in ("deny", "sameorigin")):
                        res["embebible"] = False
                m = re.search(r"frame-ancestors\s+([^;]+)", csp, re.I)
                if m:
                    fa = m.group(1).strip()
                    res["cabeceras_frame"]["frame-ancestors"] = fa
                    if "'none'" in fa or "'self'" in fa:
                        res["embebible"] = False

            host_final = urlparse(res["url_final"]).netloc.lower()
            for req_url, metodo, tipo in peticiones:
                cat, h = clasificar_recurso(req_url, host_final)
                if cat in res["terceros"] and h and h not in res["terceros"][cat]:
                    res["terceros"][cat].append(h)
                # Lo que se manda a un tercero (no solo lo que se descarga de él)
                if cat != "propio" and h and (metodo not in ("GET", "HEAD", "OPTIONS") or tipo == "ping"):
                    if h not in res["envios_terceros"]:
                        res["envios_terceros"].append(h)

            res["cookies"] = [{"name": c["name"], "domain": c["domain"]} for c in await context.cookies()]
            try:  # una página con el navegador ocupado (un juego) puede tardar en contestar: lo de la red ya está visto
                dom = await asyncio.wait_for(page.evaluate(JS_DOM), 20)
            except Exception:  # noqa: BLE001
                dom = {"title": "", "pideLogin": False, "inputsPers": [], "tienePriv": False, "senales": []}
                res["dom_sin_leer"] = True
            res["titulo_html"] = dom["title"][:120]
            res["pide_login"] = bool(dom["pideLogin"])
            res["inputs_personales"] = dom["inputsPers"]
            res["tiene_privacidad"] = bool(dom["tienePriv"])
            res["senales_codigo"] = dom["senales"]
        except Exception as exc:  # una aplicación caída no para las demás
            if "Download is starting" in str(exc):  # el enlace descarga un archivo: no es una web
                res["descarga"] = True
            else:
                res["error"] = f"{type(exc).__name__}: {str(exc).splitlines()[0][:100]}"
        finally:
            if context:
                try:
                    await context.close()
                except Exception:
                    pass
        return res


async def auditar(apps: list[dict], concurrencia: int = 3, avisar=print) -> list[dict]:
    from playwright.async_api import async_playwright

    sem = asyncio.Semaphore(concurrencia)
    hechas = 0

    async def una(browser, app):
        nonlocal hechas
        # Tope por aplicación: una página que no suelta el navegador (un juego que no para) no puede atascar
        # la pasada ni la evaluación que espera el bot. Cuenta como «no responde».
        async with sem:
            try:
                r = await asyncio.wait_for(auditar_una(asyncio.Semaphore(1), browser, app), TOPE_S)
            except asyncio.TimeoutError:
                r = {k: v for k, v in app.items() if k != "hoja"} | {
                    "url_final": app["url"], "http_status": 0, "terceros": {}, "envios_terceros": [],
                    "error": f"TimeoutError: la página no ha terminado en {TOPE_S} s",
                    "fecha_auditoria": date.today().isoformat()}
        hechas += 1
        if hechas % 25 == 0 or hechas == len(apps):
            avisar(f"  inspeccionadas {hechas}/{len(apps)}")
        return r

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            return await asyncio.gather(*(una(browser, a) for a in apps))
        finally:
            await browser.close()
