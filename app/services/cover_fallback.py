import re
import time
from threading import Lock

import requests


CHEAPSHARK_GAMES_URL = "https://www.cheapshark.com/api/1.0/games"
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
    """Cerca su CheapShark una copertina alternativa per ``title``.

    CheapShark non richiede credenziali e restituisce miniature provenienti dagli
    store. Anche i risultati negativi vengono messi in cache per non ripetere una
    richiesta esterna a ogni errore del browser.
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
            CHEAPSHARK_GAMES_URL,
            params={"title": title, "limit": 10, "exact": 0},
            timeout=4,
        )
        response.raise_for_status()
        results = response.json()
    except (requests.RequestException, ValueError):
        return None

    if not isinstance(results, list):
        return None

    exact_matches = [
        result for result in results
        if isinstance(result, dict)
        and _normalise_title(str(result.get("external", ""))) == cache_key
    ]
    candidates = exact_matches or results
    cover_url = next(
        (
            result.get("thumb")
            for result in candidates
            if isinstance(result, dict)
            and isinstance(result.get("thumb"), str)
            and result["thumb"].startswith(("https://", "http://"))
        ),
        None,
    )
    if cover_url and cover_url.startswith("http://"):
        cover_url = f"https://{cover_url.removeprefix('http://')}"

    _set_cached_cover(cache_key, cover_url)
    return cover_url
