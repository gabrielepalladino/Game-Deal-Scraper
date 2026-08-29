import requests
from config import ITAD_API_KEY


def search_games(query):
    """Cerca giochi su IsThereAnyDeal usando endpoint /games/search/v1"""

    url = "https://api.isthereanydeal.com/games/search/v1"

    # Autenticazione - può essere header o parametro query
    headers = {
        "ITAD-API-Key": ITAD_API_KEY
    }

    # Parametri corretti secondo la documentazione ufficiale
    params = {
        "title": query,      # Nome gioco (obbligatorio)
        "results": 20        # Numero risultati (1-100, default 20)
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=5
        )

        response.raise_for_status()

        # L'API ritorna direttamente un array di giochi
        games = response.json()
        
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