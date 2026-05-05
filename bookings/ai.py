"""Gemini AI integration with persona 'Ingegnere materiali IKEA-alluminio'.

Centralizza la persona e i 4 helper per le feature divertenti.
Free tier: gemini-2.0-flash, ~15 req/min, ~1500 req/giorno.
"""
import json
import logging
import re

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

PERSONA = (
    "Sei un ingegnere dei materiali ossessionato dall'IKEA. "
    "L'unico materiale che conosci e di cui parli e' l'ALLUMINIO: lo citi sempre "
    "(leghe 6063 o 7075, anodizzazione, profilati estrusi, ossido protettivo). "
    "Paragoni qualsiasi cosa a mobili IKEA (Billy, Kallax, Malm, Lack, Poang). "
    "Tono: entusiasta, leggermente fissato, sempre cordiale. Rispondi in italiano. "
    "Max 4-6 frasi. Non inventare dati specifici sull'alloggio o luoghi reali. "
    "Non dare consigli medici, legali o finanziari. "
    "Se ti chiedono altri materiali, ammetti di conoscere solo l'alluminio e devii."
)

_INJECTION_PATTERNS = re.compile(
    r"(?i)(ignore (all )?previous|disregard (the )?(system|persona|instructions)|"
    r"system\s*:|act as|you are now|new instructions|jailbreak)"
)


def _sanitize(text: str) -> str:
    """Rimuove pattern grossolani di prompt injection."""
    if not text:
        return ''
    return _INJECTION_PATTERNS.sub('[filtered]', text)


def _call_gemini(user_prompt, system=PERSONA, max_tokens=400, temperature=0.9):
    """POST a Gemini generateContent. Ritorna stringa o None su errore."""
    api_key = getattr(settings, 'GEMINI_API_KEY', '') or ''
    if not api_key:
        logger.warning('GEMINI_API_KEY mancante, skip AI')
        return None
    model = getattr(settings, 'GEMINI_MODEL', 'gemini-flash-latest')
    timeout = getattr(settings, 'GEMINI_TIMEOUT', 15)
    url = (
        f'https://generativelanguage.googleapis.com/v1beta/models/'
        f'{model}:generateContent?key={api_key}'
    )
    body = {
        'systemInstruction': {'parts': [{'text': system}]},
        'contents': [{'role': 'user', 'parts': [{'text': user_prompt}]}],
        'generationConfig': {
            'temperature': temperature,
            'maxOutputTokens': max_tokens,
            'thinkingConfig': {'thinkingBudget': 0},
        },
    }
    try:
        r = requests.post(url, json=body, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        return data['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception:
        logger.exception('Gemini call failed')
        return None


def welcome_narration(booking):
    """Feature A: saluto narrato per email conferma. Ritorna str | None."""
    try:
        nights = max((booking.check_out - booking.check_in).days, 1)
        month = booking.check_in.strftime('%B')
        title = booking.accommodation.title if booking.accommodation else 'la struttura'
        prompt = (
            f"Scrivi un saluto di benvenuto (3-4 frasi) per un ospite del B&B. "
            f"Alloggio: {title}. Notti: {nights}. Ospiti: {booking.num_guests}. "
            f"Mese check-in: {month}. Cita alluminio e fai un paragone IKEA."
        )
        return _call_gemini(prompt, max_tokens=300)
    except Exception:
        logger.exception('welcome_narration failed')
        return None


def concierge_reply(question, history=None):
    """Feature B: risposta concierge. Ritorna str | None."""
    q = _sanitize((question or '').strip())[:500]
    if not q:
        return None
    ctx = ''
    if history:
        recent = history[-6:]
        lines = [f"{h.get('role', 'user')}: {_sanitize(h.get('text', ''))[:200]}" for h in recent]
        ctx = 'Conversazione precedente:\n' + '\n'.join(lines) + '\n\n'
    return _call_gemini(f"{ctx}Ospite chiede: {q}\nRispondi.", max_tokens=350)


def traveler_type(answers):
    """Feature C: classifica viaggiatore. Ritorna {type, description} | None."""
    if not answers:
        return None
    clean = [_sanitize(str(a).strip())[:200] for a in answers[:5] if str(a).strip()]
    if not clean:
        return None
    prompt = (
        "In base alle risposte qui sotto, classifica l'ospite con un soprannome buffo "
        "(esempi: 'Esploratore Anodizzato', 'Gourmet Estruso', 'Nomade della Lega 6063'). "
        "Rispondi SOLO con JSON valido nel formato: "
        '{"type": "...", "description": "..."}. '
        "La description max 3 frasi, deve citare alluminio e IKEA.\n\n"
        f"Risposte ospite: {clean}"
    )
    raw = _call_gemini(prompt, max_tokens=600, temperature=1.0)
    if not raw:
        return None
    cleaned = raw.strip()
    if cleaned.startswith('```'):
        cleaned = cleaned.strip('`')
        if cleaned.lower().startswith('json'):
            cleaned = cleaned[4:].strip()
    try:
        result = json.loads(cleaned)
        if isinstance(result, dict) and 'type' in result and 'description' in result:
            return {
                'type': str(result['type'])[:100],
                'description': str(result['description'])[:600],
            }
    except Exception:
        pass
    return {'type': 'Viaggiatore Misterioso', 'description': raw[:500]}


def surprise_itinerary(booking):
    """Feature D: itinerario HTML. Ritorna str HTML | None."""
    try:
        nights = max((booking.check_out - booking.check_in).days, 1)
        days = min(nights, 3)
        month = booking.check_in.strftime('%B')
        prompt = (
            f"Genera un itinerario sorpresa di {days} giorni per un soggiorno B&B. "
            f"Ospiti: {booking.num_guests}. Mese: {month}. "
            "Output: HTML semplice, usa <h3> per il titolo del giorno e <ul><li> "
            "per le attivita. Niente <html>, <body> o <head>. "
            "Niente luoghi specifici inventati: usa categorie generiche "
            "(es. 'passeggiata in centro storico'). "
            "Cita alluminio e IKEA in ogni giorno. Max 250 parole totali."
        )
        return _call_gemini(prompt, max_tokens=600, temperature=0.85)
    except Exception:
        logger.exception('surprise_itinerary failed')
        return None
