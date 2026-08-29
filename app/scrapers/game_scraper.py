import requests
from config import ITAD_API_KEY


def search_games(query):
    """Cerca giochi su IsThereAnyDeal usando endpoint /games/search/v1"""

    url = "https://api.isthereanydeal.com/games/search/v1"

    headers = {
        "ITAD-API-Key": ITAD_API_KEY
    }

    params = {
        "title": query,
        "results": 20
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=5
        )

        response.raise_for_status()

        data = response.json()
        
        # 🔍 Gestisci entrambi i casi
        if isinstance(data, list):
            # La risposta è già una lista
            games = data
        elif isinstance(data, dict):
            # La risposta è un dizionario con chiave 'data'
            games = data.get('data', [])
        else:
            games = []
        
        print(f"DEBUG - Giochi trovati: {len(games)}")
        if games:
            print(f"DEBUG - Primo gioco: {games[0]}")

        return games if isinstance(games, list) else []

    except requests.exceptions.RequestException as e:
        print(f"Errore API: {e}")
        return []
    except ValueError as e:
        print(f"Errore JSON: {e}")
        return []