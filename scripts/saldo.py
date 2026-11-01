# SPDX-License-Identifier: AGPL-3.0-or-later
"""Si Anthropic deja de atender a un bot por falta de saldo o por un límite de gasto, se avisa a Juanjo (ADR 0024).

El tope propio de cada bot (TOPE_MES_USD) ya avisa al 80 %. Esto cubre lo que corta Anthropic: los
créditos de la organización, que comparten todas sus claves, o el límite de gasto del espacio de trabajo
en la Console. Se avisa una vez, y no se vuelve a avisar hasta que una llamada haya ido bien. A quien
preguntaba no se le cuenta nada de dinero (Juanjo, 01-11-2026: «Los problemas económicos no deben
transmitirse al usuario»).
"""
import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path

import anthropic

from grupos import DATOS

# La API responde 400 al quedarse sin créditos y al llegar al límite de gasto de la organización o del
# espacio de trabajo, 429 al llegar al tope mensual del nivel de uso y 402 si falla la facturación
# (https://platform.claude.com/docs/en/api/errors, consultada el 01-11-2026). El 429 corriente, el de
# demasiadas peticiones, no es esto: se distingue por el mensaje.
PATRON = re.compile(r"credit balance|usage limit|spend limit|spend cap", re.IGNORECASE)


def mensaje(error: anthropic.APIStatusError) -> str:
    cuerpo = error.body if isinstance(error.body, dict) else {}
    return str((cuerpo.get("error") or {}).get("message") or error.message)


def sin_saldo(error: BaseException) -> bool:
    if not isinstance(error, anthropic.APIStatusError):
        return False
    return error.status_code == 402 or (error.status_code in (400, 429) and bool(PATRON.search(mensaje(error))))


def cred() -> Path:
    return Path(os.environ.get("BOT_CRED", Path.home() / ".config/credenciales/bot-chatgpt-ia-edu.json"))


def marca() -> Path:
    """Una por bot: el índice usa la clave y la cuenta del Bot de IA Educativa y comparte la suya."""
    return DATOS / f"aviso-saldo-{cred().stem}"


def texto_aviso(error: anthropic.APIStatusError) -> str:
    nombre = "Karla bot" if "karla" in cred().stem else "el Bot de IA Educativa"
    m = mensaje(error)
    if "credit balance" in m.lower():
        causa = ("Se han acabado los créditos de la API (los del plan, que comparten todas las claves). "
                 "Vuelven con el siguiente cobro del plan.")
    elif error.status_code == 402:
        causa = "Anthropic indica un problema de facturación."
    else:
        causa = "Ha llegado a un límite de gasto de la Console de Claude."
    return (f"Aviso de {nombre}: Anthropic ha dejado de atenderlo y no puede responder a nadie. {causa}\n\n"
            f"Mensaje de Anthropic: «{m}»\n\nNo volveré a avisar hasta que haya vuelto a funcionar.")


def avisar(error: anthropic.APIStatusError) -> None:
    """Por el propio bot, como el aviso del 80 %. Si el aviso falla, se intenta en la siguiente llamada."""
    if marca().exists():
        return
    try:
        token = json.loads(cred().read_text())["token"]
        datos = urllib.parse.urlencode({"chat_id": int(os.environ.get("JUANJO") or 0),
                                        "text": texto_aviso(error)}).encode()
        urllib.request.urlopen(f"https://api.telegram.org/bot{token}/sendMessage", datos, timeout=30)
        marca().write_text(mensaje(error))
    except Exception as falla:  # noqa: BLE001 — el aviso no puede tumbar al bot
        print(f"saldo: no se pudo avisar a Juanjo: {type(falla).__name__}: {falla}", flush=True)


def vigilar(crear):
    """Envuelve messages.create: avisa si falta saldo y deja pasar el error como antes."""
    def create(*args, **kwargs):
        try:
            respuesta = crear(*args, **kwargs)
        except anthropic.APIStatusError as error:
            if sin_saldo(error):
                avisar(error)
            raise
        if marca().exists():  # vuelve a funcionar: el siguiente corte se avisará
            marca().unlink(missing_ok=True)
        return respuesta
    return create


def cliente(clave: Path) -> anthropic.Anthropic:
    """El cliente de Claude de los bots, con la vigilancia del saldo en todas sus llamadas."""
    c = anthropic.Anthropic(api_key=clave.read_text().strip())
    c.messages.create = vigilar(c.messages.create)
    c.beta.messages.create = vigilar(c.beta.messages.create)
    return c
