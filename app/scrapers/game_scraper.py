import requests
from config import ITAD_API_KEY


def search_games(query):
    """Cerca giochi su IsThereAnyDeal"""

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

        games = response.json()

        return games

    except requests.exceptions.RequestException as e:
        print(f"Errore API: {e}")
        return []
