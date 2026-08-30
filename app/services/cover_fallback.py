import re
import time
from threading import Lock

import requests


STEAM_STORE_SEARCH_URL = "https://store.steampowered.com/api/storesearch/"
STEAM_PORTRAIT_URL = (
    "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/"
    "{app_id}/library_600x900.jpg"
)
COVER_CACHE_TTL_SECONDS = 24 * 60 * 60
COVER_CACHE_MAX_ITEMS = 512

_cover_cache = {}
_cover_cache_lock = Lock()
_request_session = requests.Session()


def _normalise_title(title):
    """Rende confrontabili titoli che differiscono solo per punteggiatura."""

    return " ".join(re.sub(r"[^a-z0-9]+", " ", title.lower()).split())


def _get_cached_cover(cache_key):
    now = time.monotonic()
    with _cover_cache_lock:
        cached = _cover_cache.get(cache_key)
        if cached is None:
            return None, False

        expires_at, cover_url = cached
        if expires_at <= now:
            _cover_cache.pop(cache_key, None)
            return None, False

        return cover_url, True


def _set_cached_cover(cache_key, cover_url):
    with _cover_cache_lock:
        if len(_cover_cache) >= COVER_CACHE_MAX_ITEMS:
            _cover_cache.pop(next(iter(_cover_cache)), None)
        _cover_cache[cache_key] = (
            time.monotonic() + COVER_CACHE_TTL_SECONDS,
            cover_url,
        )


def find_fallback_cover(title):
    """Cerca nello Steam Store una copertina verticale alternativa per ``title``.

    L'endpoint pubblico di ricerca di Steam non richiede credenziali. Dal relativo
    app id viene costruito l'URL ufficiale dell'asset verticale 600x900, più adatto
    al box della UI rispetto alla miniatura orizzontale inclusa nella risposta.
    Anche i risultati negativi vengono messi in cache per evitare richieste
    ripetute a ogni errore del browser.
    """

    title = (title or "").strip()
    if not title:
        return None

    cache_key = _normalise_title(title)
    cached_cover, cache_hit = _get_cached_cover(cache_key)
    if cache_hit:
        return cached_cover

    try:
        response = _request_session.get(
            STEAM_STORE_SEARCH_URL,
            params={"term": title, "l": "italian", "cc": "IT"},
            timeout=4,
        )
        response.raise_for_status()
        results = response.json()
    except (requests.RequestException, ValueError):
        return None

    if not isinstance(results, dict) or not isinstance(results.get("items"), list):
        return None

    results = results["items"]
    exact_matches = [
        result for result in results
        if isinstance(result, dict)
        and _normalise_title(str(result.get("name", ""))) == cache_key
    ]
    candidates = exact_matches or results
    app_id = next(
        (
            result.get("id")
            for result in candidates
            if isinstance(result, dict)
            and isinstance(result.get("id"), int)
        ),
        None,
    )
    cover_url = STEAM_PORTRAIT_URL.format(app_id=app_id) if app_id else None

    _set_cached_cover(cache_key, cover_url)
    return cover_url
