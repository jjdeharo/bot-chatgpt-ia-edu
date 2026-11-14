# SPDX-License-Identifier: AGPL-3.0-or-later
"""El final del plazo de los avisos de la revisión del repositorio de VCE (ADR 0039, tras el 0013).

El día que vence un plazo, a las 9:00 de Madrid, el bot vuelve a mirar los avisos que siguen pendientes:

- B (el enlace no se abre) y D (derechos reservados): con la misma comprobación que «Ya lo he corregido». Los que
  ya cumplen quedan «corregido», con su licencia en la hoja. Un B que ya se abre pero sigue sin licencia no se
  retira: el aviso solo hablaba del enlace, y lo publicado antes del bot sin licencia se queda (Juanjo,
  29-10-2026); pasa a recomendación, como los A.
- C (los GPT): no tienen arreglo; solo se mira que sigan en el repositorio.
- Lo que ya no está en el repositorio con ese enlace (su autor lo quitó o lo mudó) queda «sin_ficha».

Después le manda a Juanjo, por privado, la lista de los que siguen sin cumplir, cada uno con su casilla, y dos
botones: «Retirar los marcados» y «No retirar ninguno». Nada se retira sin ese toque. Al retirar, cada ficha se
guarda antes entera en datos/retirados.json (con su dueño y su aviso) y se puede devolver con
`avisos.py restaurar URL`. Retirado lo del primer plazo, se desfija el aviso del grupo (FIJADO).

Los A (sin licencia) no se retiran nunca: no entran aquí.

Lo hecho con cada plazo se apunta en datos/plazos.json, para no repetirlo y para que los botones sigan valiendo
tras un reinicio del bot.
"""
import json
from datetime import date, datetime, time, timezone
from zoneinfo import ZoneInfo

import catalogo
from grupos import DATOS

MADRID = ZoneInfo("Europe/Madrid")
HORA = time(9, 0)                # por la mañana, después del aviso del diario de las 7:00
RETIRABLES = ("B", "C", "D")     # los A no se retiran nunca (Juanjo, 29-10-2026)
ESTADO = DATOS / "plazos.json"
RETIRADOS = DATOS / "retirados.json"
# El aviso fijado en Vibe Coding Educativo (https://t.me/vceduca/14274): se desfija al confirmar la retirada
# del primer plazo (Juanjo, 27-10-2026).
FIJADO = {"2026-11-29": ("vce", 14274)}

TITULO_GPT = "los GPT de ChatGPT, que OpenAI retira hoy"
TITULO_OTROS = "los enlaces que no se abren y las licencias incompatibles"


def ahora_local(ahora: datetime | None = None) -> datetime:
    return (ahora or datetime.now(timezone.utc)).astimezone(MADRID)


def leer_estado() -> dict:
    try:
        return json.loads(ESTADO.read_text())
    except (OSError, ValueError):
        return {}


def guardar_estado(d: dict) -> None:
    tmp = ESTADO.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=1))
    tmp.replace(ESTADO)


def leer_retirados() -> dict:
    try:
        return json.loads(RETIRADOS.read_text())
    except (OSError, ValueError):
        return {}


def guardar_retirados(d: dict) -> None:
    tmp = RETIRADOS.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=1))
    tmp.replace(RETIRADOS)


def vencido(avisos: dict | None = None, ahora: datetime | None = None) -> str | None:
    """El plazo que toca revisar ya: el más antiguo que ha llegado a su día a las 9:00, con algún aviso retirable
    sin resolver, y que no se ha revisado aún. Si el bot estaba parado, se revisa al volver."""
    local = ahora_local(ahora)
    hechos = leer_estado()
    avisos = catalogo.leer_avisos() if avisos is None else avisos
    plazos = sorted({a["plazo"] for a in avisos.values()
                     if a.get("tipo") in RETIRABLES and a.get("estado") in ("pendiente", "por_revisar") and a.get("plazo")})
    for p in plazos:
        if p in hechos:
            continue
        if local >= datetime.combine(date.fromisoformat(p), HORA, tzinfo=MADRID):
            return p
    return None


def revisar(plazo: str, hoja, comprobar, abre, cerrojo, apuntar=lambda usd: None) -> dict:
    """Vuelve a mirar los avisos de ese plazo y deja en datos/plazos.json la lista para Juanjo.

    comprobar(url) es la de «Ya lo he corregido» (catalogo.comprobar_licencia); abre(url) dice si un enlace se abre
    (para las apps de plataforma, que no se pueden comprobar más). Devuelve lo apuntado."""
    momento = datetime.now(timezone.utc).isoformat(timespec="seconds")
    cuentas = {"corregidos": [], "sin_ficha": [], "a_recomendacion": [], "por_revisar": []}
    lista, tipos = [], set()
    avisos = catalogo.leer_avisos()
    for clave, a in avisos.items():
        if a.get("plazo") != plazo or a.get("tipo") not in RETIRABLES:
            continue
        tipos.add(a["tipo"])
        if a.get("estado") == "por_revisar":   # lo tiene Juanjo en sus manos: no se toca
            cuentas["por_revisar"].append(a.get("titulo") or clave)
            continue
        if a.get("estado") != "pendiente":
            continue
        fila = hoja.buscar(clave)
        cambio = {}
        if not fila:
            cambio = {"estado": "sin_ficha", "resuelto": momento}
            cuentas["sin_ficha"].append(a.get("titulo") or clave)
        else:
            url = fila.get(catalogo.COLUMNAS["url"]) or clave   # el de la hoja: las mayúsculas cuentan en la ruta
            item = {"clave": clave, "url": url, "titulo": fila.get(catalogo.COLUMNAS["titulo"]) or a.get("titulo", ""),
                    "autor": fila.get(catalogo.COLUMNAS["autor"], "").strip(), "tipo": a["tipo"], "marcado": True}
            if a["tipo"] == "C":
                item["nota"] = "GPT de ChatGPT"
                lista.append(item)
            else:
                try:
                    r = comprobar(url)
                except Exception as error:  # noqa: BLE001 — sin comprobar no se marca: lo decide Juanjo
                    r = {"resultado": "error", "detalle": f"no se ha podido comprobar ({type(error).__name__})"}
                if r.get("usd"):
                    apuntar(r["usd"])
                res = r["resultado"]
                if res == "cumple":
                    if r.get("licencia"):
                        hoja.poner_licencia(url, r["licencia"])
                    cambio = {"estado": "corregido", "resuelto": momento, "licencia": r.get("licencia", ""),
                              "por": "plazo"}
                    cuentas["corregidos"].append(item["titulo"])
                elif res == "plataforma":   # app de Gemini, Claude o AI Studio: solo se sabe si se abre
                    problema = abre(url)
                    if problema:
                        item["nota"] = problema
                    else:
                        item.update(nota="app de plataforma que el bot no puede comprobar: ábrela antes de marcarla",
                                    marcado=False)
                    lista.append(item)
                elif res == "no_abre":
                    item["nota"] = r.get("detalle", "no se abre")
                    lista.append(item)
                elif res == "error":
                    item.update(nota=r["detalle"] + ": míralo antes de marcarlo", marcado=False)
                    lista.append(item)
                elif a["tipo"] == "B" and res == "sin_licencia":
                    # Se abre: lo que se avisó ya está. Sin licencia, se queda como los A (Juanjo, 29-10-2026).
                    cambio = {"tipo": "A", "era": "B", "cambio_tipo": momento}
                    cuentas["a_recomendacion"].append(item["titulo"])
                elif res == "de_pago":
                    item.update(nota=f"se abre, pero es de pago: {r.get('detalle', '')}".rstrip(": "),
                                marcado=a["tipo"] == "D")
                    lista.append(item)
                else:   # D sin licencia abierta
                    item["nota"] = "sigue sin licencia abierta"
                    lista.append(item)
        if cambio:
            with cerrojo:
                d = catalogo.leer_avisos()
                if d.get(clave, {}).get("estado") == "pendiente":   # nadie lo ha resuelto mientras tanto
                    d[clave].update(cambio)
                    catalogo.guardar_avisos(d)
    registro = {"estado": "esperando", "revisado": momento, "tipos": sorted(tipos), "lista": lista, **cuentas}
    with cerrojo:
        e = leer_estado()
        e[plazo] = registro
        guardar_estado(e)
    return registro


def texto(plazo: str, r: dict) -> str:
    """El mensaje para Juanjo, en texto plano (los títulos pueden llevar < y &)."""
    dia = date.fromisoformat(plazo).strftime("%d/%m/%Y")
    solo_gpt = set(r.get("tipos") or ()) == {"C"}
    lineas = [f"Revisión del repositorio de VCE: hoy, {dia}, acaba el plazo de "
              f"{TITULO_GPT if solo_gpt else TITULO_OTROS}.", ""]
    if not solo_gpt:
        hechos = []
        if r["corregidos"]:
            hechos.append(f"• {len(r['corregidos'])} ya cumplen: quedan como corregidos.")
        if r["a_recomendacion"]:
            hechos.append(f"• {len(r['a_recomendacion'])} ya se abren, pero sin licencia: se quedan, como los "
                          "publicados antes sin licencia, con la recomendación de ponerla.")
        if r["sin_ficha"]:
            hechos.append(f"• {len(r['sin_ficha'])} ya no están en el repositorio con ese enlace (los quitó o los "
                          "mudó su autor).")
        if r["por_revisar"]:
            hechos.append(f"• {len(r['por_revisar'])} esperan tu revisión manual: no se tocan.")
        if hechos:
            lineas += ["He vuelto a comprobar los que seguían pendientes:"] + hechos + [""]
    elif r["sin_ficha"]:
        lineas += [f"{len(r['sin_ficha'])} ya no están en el repositorio (los quitó su autor).", ""]
    if not r["lista"]:
        return "\n".join(lineas + ["No queda ninguno sin cumplir: no hay nada que retirar."])
    lineas.append(f"Siguen sin cumplir ({len(r['lista'])}):")
    for n, i in enumerate(r["lista"], 1):
        lineas += [f"{n}. «{i['titulo']}»" + (f", de {i['autor']}" if i.get("autor") else ""), f"   {i['url']}",
                   f"   {i.get('nota', '')}".rstrip()]
    lineas += ["", "Marca los que quieras retirar (✅ se retira, ⬜ se queda) y confirma. Antes de quitar cada uno guardo "
               "su ficha entera, para poder devolverlo."]
    if plazo in FIJADO:
        lineas.append("Al retirarlos, desfijo el aviso de la revisión en el grupo.")
    t = "\n".join(lineas)
    return t if len(t) <= 4000 else t[:3990] + "…"


def botones(plazo: str, r: dict) -> dict:
    if r.get("estado") != "esperando" or not r["lista"]:
        return {"inline_keyboard": []}
    filas = [[{"text": f"{'✅' if i['marcado'] else '⬜'} {n}. {i['titulo'][:40]}", "callback_data": f"pz:{plazo}:{n - 1}"}]
             for n, i in enumerate(r["lista"], 1)]
    marcados = sum(i["marcado"] for i in r["lista"])
    filas.append([{"text": f"Retirar los marcados ({marcados})", "callback_data": f"pzr:{plazo}"},
                  {"text": "No retirar ninguno", "callback_data": f"pzn:{plazo}"}])
    return {"inline_keyboard": filas}


def marcar(plazo: str, n: int, cerrojo) -> dict | None:
    """Marca o desmarca uno de la lista. None si ya se decidió (un segundo toque, otro mensaje)."""
    with cerrojo:
        e = leer_estado()
        r = e.get(plazo)
        if not r or r.get("estado") != "esperando" or not 0 <= n < len(r["lista"]):
            return None
        r["lista"][n]["marcado"] = not r["lista"][n]["marcado"]
        guardar_estado(e)
        return r


def dueno_de(clave: str, fila: dict) -> int | None:
    """La cuenta de Telegram dueña del recurso: la que lo dio de alta con el bot o la que ligó su correo."""
    d = catalogo.leer_duenos()
    if clave in d["recursos"]:
        return d["recursos"][clave]
    correo = (fila.get(catalogo.COL_CORREO) or "").strip().lower()
    return next((int(u) for u, cs in d["correos"].items() if correo and correo in cs), None)


def retirar(plazo: str, hoja, cerrojo) -> dict | None:
    """Retira los marcados que siguen pendientes, guardando antes cada ficha. None si ya se decidió."""
    with cerrojo:
        e = leer_estado()
        r = e.get(plazo)
        if not r or r.get("estado") != "esperando":
            return None
        r["estado"] = "retirando"   # un segundo toque mientras tanto no retira dos veces
        guardar_estado(e)
    hechos, saltados, fallidos = [], [], []
    momento = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for i in r["lista"]:
        if not i["marcado"]:
            continue
        aviso = catalogo.aviso_de(i["clave"])
        fila = hoja.buscar(i["clave"])
        if not aviso or not fila:   # su autor lo ha corregido o quitado después de la lista
            saltados.append(i["titulo"])
            continue
        try:
            with cerrojo:
                copia = leer_retirados()
                copia[i["clave"]] = {"fila": fila, "dueno_uid": dueno_de(i["clave"], fila), "aviso": aviso,
                                     "plazo": plazo, "retirado": momento}
                guardar_retirados(copia)
            hoja.borrar(fila.get(catalogo.COLUMNAS["url"]) or i["url"])
            with cerrojo:
                d = catalogo.leer_duenos()
                d["recursos"].pop(i["clave"], None)
                catalogo.guardar_duenos(d)
                a = catalogo.leer_avisos()
                a[i["clave"]].update(estado="retirado", resuelto=momento)
                catalogo.guardar_avisos(a)
            hechos.append(i["titulo"])
        except Exception as error:  # noqa: BLE001 — los demás siguen; este queda pendiente y se dice
            fallidos.append(f"{i['titulo']} ({type(error).__name__})")
    with cerrojo:
        e = leer_estado()
        e[plazo].update(estado="retirado", decidido=momento, retirados=hechos, saltados=saltados, fallidos=fallidos)
        guardar_estado(e)
    return e[plazo]


def no_retirar(plazo: str, cerrojo) -> bool:
    with cerrojo:
        e = leer_estado()
        r = e.get(plazo)
        if not r or r.get("estado") != "esperando":
            return False
        r.update(estado="no_retirar", decidido=datetime.now(timezone.utc).isoformat(timespec="seconds"))
        guardar_estado(e)
        return True


def restaurar(url: str, hoja) -> str:
    """Devuelve al repositorio un recurso retirado, con su ficha y su dueño (avisos.py restaurar)."""
    clave = catalogo.normalizar(url)
    copia = leer_retirados()
    c = copia.get(clave)
    if not c:
        return "No está entre los retirados."
    if hoja.buscar(clave):
        return "Ya está en el repositorio."
    # Sin la fecha (la pone la hoja) ni el correo: la hoja se publica, y los correos van en el almacén privado.
    fila = {k: v for k, v in c["fila"].items() if k not in ("Marca temporal", catalogo.COL_CORREO)}
    hoja.alta_fila(fila)
    extra = ""
    if c.get("dueno_uid"):
        d = catalogo.leer_duenos()
        d["recursos"][clave] = c["dueno_uid"]
        catalogo.guardar_duenos(d)
    elif c["fila"].get(catalogo.COL_CORREO):
        extra = (f" Su autor no tenía cuenta ligada: para que vuelva a verlo en /misrecursos, añade el enlace a su "
                 f"correo ({c['fila'][catalogo.COL_CORREO]}) en las propiedades del Apps Script del catálogo.")
    a = catalogo.leer_avisos()
    if clave in a:
        a[clave].update(estado="restaurado", restaurado=datetime.now(timezone.utc).isoformat(timespec="seconds"))
        catalogo.guardar_avisos(a)
    c["restaurado"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    guardar_retirados(copia)
    return "Restaurado." + extra
