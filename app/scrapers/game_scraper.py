import time
from threading import Lock
from urllib.parse import urlencode

import requests

from config import ITAD_API_KEY


SEARCH_CACHE_TTL_SECONDS = 10 * 60
SEARCH_CACHE_MAX_ITEMS = 128
_request_session = requests.Session()
_search_cache = {}
_search_cache_lock = Lock()


def _normalise_cache_value(value):
    if isinstance(value, float):
        return round(value, 2)
    if isinstance(value, str):
        return value.strip().lower()
    return value


def _make_cache_key(query, limit, max_price=None):
    return (query.strip().lower(), int(limit), _normalise_cache_value(max_price))


def _get_cached_search(cache_key):
    now = time.monotonic()
    with _search_cache_lock:
        cached = _search_cache.get(cache_key)
        if not cached:
            return None

        expires_at, games = cached
        if expires_at <= now:
            _search_cache.pop(cache_key, None)
            return None

        return games


def _set_cached_search(cache_key, games):
    expires_at = time.monotonic() + SEARCH_CACHE_TTL_SECONDS
    with _search_cache_lock:
        if len(_search_cache) >= SEARCH_CACHE_MAX_ITEMS:
            oldest_key = next(iter(_search_cache))
            _search_cache.pop(oldest_key, None)
        _search_cache[cache_key] = (expires_at, games)


def search_games(query, limit=100, max_price=None):
    """
    Cerca giochi su IsThereAnyDeal usando endpoint /games/search/v1.

    La ricerca completa viene salvata in cache per rendere istantanei i cambi
    pagina o per_page della stessa query. I prezzi sono recuperati in batch con
    una sola chiamata API, evitando una richiesta HTTP per ogni gioco.

    Args:
        query: Titolo del gioco da cercare
        limit: Numero massimo di risultati (max 100)
        max_price: Prezzo massimo opzionale da applicare prima della cache

    Returns:
        Lista di giochi con prezzi ordinati per rilevanza e prezzo
    """

    # Limita a max 100 per l'API ITAD
    limit = min(int(limit), 100)
    cache_key = _make_cache_key(query, limit, max_price)
    cached_games = _get_cached_search(cache_key)
    if cached_games is not None:
        print(f"DEBUG - Cache hit per ricerca: {query}")
        return cached_games

    url = "https://api.isthereanydeal.com/games/search/v1"

    headers = {
        "ITAD-API-Key": ITAD_API_KEY
    }

    params = {
        "title": query,
        "results": limit
    }

    try:
        response = _request_session.get(url, headers=headers, params=params, timeout=5)
        response.raise_for_status()
        games = response.json()

        # Gestisci sia array che dict
        if isinstance(games, dict):
            games = games.get('data', [])

        print(f"DEBUG - Giochi trovati (prima del ranking): {len(games) if isinstance(games, list) else 0}")

        if not isinstance(games, list):
            print(f"ERROR - Risposta non è una lista: {type(games)}")
            return []

        # Applica ranking intelligente PRIMA di recuperare i prezzi
        games = rank_games(games, query)
        print(f"DEBUG - Giochi dopo ranking: {len(games)}")

        # Recupera i prezzi in batch invece di fare una richiesta per ogni gioco.
        games_with_deals = get_games_deals(games)

        # Filtra per prezzo prima di salvare in cache, così le pagine successive
        # riusano lo stesso risultato già pronto.
        if max_price is not None:
            games_with_deals = [
                g for g in games_with_deals
                if g.get('lowest_price') and float(g.get('lowest_price', float('inf'))) <= max_price
            ]
            print(f"DEBUG - Giochi dopo filtro prezzo: {len(games_with_deals)}")

        # Ordina per prezzo (dal più basso al più alto)
        games_with_deals.sort(
            key=lambda x: x.get('lowest_price') if x.get('lowest_price') else float('inf')
        )

        _set_cached_search(cache_key, games_with_deals)
        return games_with_deals

    except requests.exceptions.RequestException as e:
        print(f"Errore API: {e}")
        return []
    except ValueError as e:
        print(f"Errore JSON: {e}")
        return []


def rank_games(games, query):
    """
    Ordina i giochi per rilevanza usando un sistema di ranking intelligente.
    """

    query_lower = query.lower().strip()

    def calculate_relevance_score(game):
        """Calcola uno score di rilevanza (più alto = più rilevante)"""
        title = game.get('title', '').lower()
        game_type = game.get('type', 'game')

        score = 0

        if title == query_lower:
            score += 10000
        elif title.startswith(query_lower):
            score += 5000
        elif query_lower in title:
            score += 2000

        if game_type == 'game':
            score += 500
        elif game_type == 'dlc':
            score += 100
        elif game_type == 'bundle':
            score += 50

        title_words = len(title.split())
        if title_words <= 4:
            score += 300 - (title_words * 10)

        if game.get('mature', False):
            score -= 100

        return score

    ranked_games = sorted(games, key=calculate_relevance_score, reverse=True)

    for idx, game in enumerate(ranked_games[:5]):
        score = calculate_relevance_score(game)
        print(f"  [{idx+1}] {game.get('title')} ({game.get('type')}) - Score: {score}")

    return ranked_games


def get_games_deals(games):
    """Recupera prezzi e offerte per più giochi con una singola POST."""

    games_by_id = {game.get('id'): game for game in games if game.get('id')}
    missing_id_titles = [game.get('title', 'Sconosciuto') for game in games if not game.get('id')]

    for title in missing_id_titles:
        print(f"WARNING - Gioco senza 'id': {title}")

    if not games_by_id:
        return []

    url = "https://api.isthereanydeal.com/games/prices/v3"
    headers = {
        "ITAD-API-Key": ITAD_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = _request_session.post(url, headers=headers, json=list(games_by_id.keys()), timeout=8)

        if response.status_code == 404:
            print("⚠️  Prezzi non trovati (404)")
            return []

        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list):
            print(f"ERROR - Risposta prezzi non è una lista: {type(data)}")
            return []

        games_with_deals = []
        for game_prices in data:
            game_id = game_prices.get('id')
            game = games_by_id.get(game_id)
            if not game:
                continue

            game_with_deals = hydrate_game_with_deals(game, game_prices)
            if game_with_deals:
                games_with_deals.append(game_with_deals)

        return games_with_deals

    except requests.exceptions.RequestException as e:
        print(f"Errore nel recupero deals in batch: {e}")
        return []
    except (ValueError, AttributeError, KeyError) as e:
        print(f"Errore nel parsing deals in batch: {e}")
        return []


def hydrate_game_with_deals(game, game_prices):
    """Aggiunge al gioco le informazioni di prezzo ricevute dall'API."""

    game_title = game.get('title', 'Sconosciuto')
    deals = game_prices.get('deals', [])

    if not deals:
        print(f"⊘ {game_title} - Escluso (nessun deal disponibile)")
        return None

    first_deal = deals[0]
    price_info = first_deal.get('price', {})
    lowest_price = price_info.get('amount')

    if lowest_price == 0 or lowest_price is None:
        print(f"⊘ {game_title} - Escluso (gioco gratuito o prezzo non disponibile)")
        return None

    shop_info = first_deal.get('shop', {})
    shop_name = shop_info.get('name', 'Unknown')

    game['lowest_price'] = lowest_price
    game['best_shop'] = shop_name
    game['deals'] = extract_deals_from_prices(deals)

    price_str = f"€{lowest_price:.2f}" if lowest_price else "N/A"
    print(f"✓ {game_title} - Prezzo: {price_str} ({shop_name})")
    return game


def get_game_deals(game):
    """Compatibilità per eventuali chiamate singole esistenti."""

    deals = get_games_deals([game])
    return deals[0] if deals else None


def extract_deals_from_prices(deals):
    """Estrae una lista formattata di negozi e prezzi dai deals"""

    extracted_deals = []

    if isinstance(deals, list) and deals:
        for idx, deal in enumerate(deals[:15]):
            try:
                shop_info = deal.get('shop', {}) if isinstance(deal.get('shop'), dict) else {}
                shop_name = shop_info.get('name', 'Unknown')

                price_info = deal.get('price', {}) if isinstance(deal.get('price'), dict) else {}
                price = price_info.get('amount')

                if price and isinstance(price, str):
                    price = float(price)

                if price:
                    extracted_deal = {
                        'shop_name': shop_name,
                        'shop_logo': '',
                        'price': float(price) if price else None,
                        'url': deal.get('url', ''),
                        'is_best': idx == 0,
                        'original_price': None,
                        'discount_price': None
                    }
                    extracted_deals.append(extracted_deal)
            except (ValueError, TypeError, AttributeError) as e:
                print(f"WARNING - Errore nel parsing deal {idx}: {e}")
                continue

    return extracted_deals


def build_search_url(query, page=1, per_page=10, max_price=None):
    """Crea URL di paginazione escapati in modo sicuro."""

    params = {
        'query': query,
        'page': page,
        'per_page': per_page,
    }
    if max_price is not None:
        params['max_price'] = max_price
    return f"/search?{urlencode(params)}"
