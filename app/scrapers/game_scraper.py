import requests
from config import ITAD_API_KEY


def search_games(query, limit=100):
    """
    Cerca giochi su IsThereAnyDeal usando endpoint /games/search/v1
    
    Args:
        query: Titolo del gioco da cercare
        limit: Numero massimo di risultati (max 100)
    
    Returns:
        Lista di giochi con prezzi ordinati per rilevanza e prezzo
    """

    url = "https://api.isthereanydeal.com/games/search/v1"

    headers = {
        "ITAD-API-Key": ITAD_API_KEY
    }

    # Limita a max 100 per l'API ITAD
    limit = min(int(limit), 100)
    
    params = {
        "title": query,
        "results": limit
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)
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
        
        # Ora per ogni gioco, recupera i prezzi/deals
        games_with_deals = []
        for game in games:
            game_with_deals = get_game_deals(game)
            if game_with_deals:  # Filtra i None (giochi esclusi)
                games_with_deals.append(game_with_deals)
        
        # Ordina per prezzo (dal più basso al più alto)
        games_with_deals.sort(
            key=lambda x: x.get('lowest_price') if x.get('lowest_price') else float('inf')
        )
        
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
    
    Criteri di ranking (dal più importante al meno importante):
    1. Esatto match del titolo
    2. Gioco principale (type="game") vs DLC/Bundle
    3. Qualità della corrispondenza con il titolo (edit distance)
    4. Popolarità approssimativa
    
    Args:
        games: Lista di giochi dall'API
        query: Query di ricerca originale
    
    Returns:
        Lista ordinata per rilevanza
    """
    
    query_lower = query.lower().strip()
    
    def calculate_relevance_score(game):
        """Calcola uno score di rilevanza (più alto = più rilevante)"""
        title = game.get('title', '').lower()
        game_type = game.get('type', 'game')
        
        score = 0
        
        # Criterio 1: Esatto match (massima priorità)
        if title == query_lower:
            score += 10000
        # Se il titolo contiene esattamente la query (es. "Cyberpunk 2077" contiene "Cyberpunk")
        elif title.startswith(query_lower):
            score += 5000
        elif query_lower in title:
            score += 2000
        
        # Criterio 2: Tipo di gioco (i giochi principali vengono prima dei DLC/bundle)
        if game_type == 'game':
            score += 500
        elif game_type == 'dlc':
            score += 100
        elif game_type == 'bundle':
            score += 50
        
        # Criterio 3: Lunghezza del titolo (titoli più specifici hanno priorità)
        # Es. "Cyberpunk 2077" (2 parole) prima di "Cyberpunk 2077: Phantom Liberty" (4 parole)
        title_words = len(title.split())
        if title_words <= 4:  # Titoli brevi e specifici
            score += 300 - (title_words * 10)
        
        # Criterio 4: Mature content (deprioritizza)
        if game.get('mature', False):
            score -= 100
        
        return score
    
    # Ordina i giochi per score (decrescente = più rilevante per primo)
    ranked_games = sorted(games, key=calculate_relevance_score, reverse=True)
    
    # Debug: stampa i primi 5 giochi con il loro score
    for idx, game in enumerate(ranked_games[:5]):
        score = calculate_relevance_score(game)
        print(f"  [{idx+1}] {game.get('title')} ({game.get('type')}) - Score: {score}")
    
    return ranked_games


def get_game_deals(game):
    """
    Recupera i prezzi e le offerte per un gioco specifico usando POST
    
    Ritorna:
    - game dict se il gioco ha un prezzo valido
    - None se il gioco è gratuito, non disponibile o non ha deals
    """
    
    game_id = game.get('id')
    game_title = game.get('title', 'Sconosciuto')
    
    if not game_id:
        print(f"WARNING - Gioco senza 'id': {game_title}")
        return None
    
    url = "https://api.isthereanydeal.com/games/prices/v3"
    
    headers = {
        "ITAD-API-Key": ITAD_API_KEY,
        "Content-Type": "application/json"
    }
    
    # L'endpoint /games/prices/v3 richiede POST con array di ID nel body
    payload = [game_id]
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=5)
        
        if response.status_code == 404:
            print(f"⚠️  {game_title} - Non trovato (404)")
            return None
        
        response.raise_for_status()
        
        data = response.json()
        
        # La risposta è un array, il primo elemento contiene i dati del gioco
        if isinstance(data, list) and data:
            game_prices = data[0]
            
            # Estrai i deals
            deals = game_prices.get('deals', [])
            
            # Il primo deal è il prezzo più basso
            if deals:
                first_deal = deals[0]
                
                # Estrai prezzo e negozio dal primo deal
                price_info = first_deal.get('price', {})
                lowest_price = price_info.get('amount')
                
                # FILTRO: Escludi giochi gratis (prezzo 0) o senza prezzo
                if lowest_price == 0 or lowest_price is None:
                    print(f"⊘ {game_title} - Escluso (gioco gratuito o prezzo non disponibile)")
                    return None
                
                shop_info = first_deal.get('shop', {})
                shop_name = shop_info.get('name', 'Unknown')
                
                # Aggiungi le informazioni di prezzo al gioco
                game['lowest_price'] = lowest_price
                game['best_shop'] = shop_name
                
                # Estrai i dettagli di tutti i negozi
                game['deals'] = extract_deals_from_prices(deals)
                
                price_str = f"€{lowest_price:.2f}" if lowest_price else "N/A"
                print(f"✓ {game_title} - Prezzo: {price_str} ({shop_name})")
                return game
            else:
                print(f"⊘ {game_title} - Escluso (nessun deal disponibile)")
                return None
        
        print(f"⊘ {game_title} - Escluso (risposta API vuota)")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"Errore nel recupero deals per {game_title}: {e}")
        return None
    except (ValueError, AttributeError, KeyError) as e:
        print(f"Errore nel parsing deals per {game_title}: {e}")
        return None


def extract_deals_from_prices(deals):
    """Estrae una lista formattata di negozi e prezzi dai deals"""
    
    extracted_deals = []
    
    if isinstance(deals, list) and deals:
        # Itera sui deals disponibili (max 15)
        for idx, deal in enumerate(deals[:15]):
            try:
                # Estrai i dati dello shop
                shop_info = deal.get('shop', {}) if isinstance(deal.get('shop'), dict) else {}
                shop_name = shop_info.get('name', 'Unknown')
                
                # Estrai il prezzo
                price_info = deal.get('price', {}) if isinstance(deal.get('price'), dict) else {}
                price = price_info.get('amount')
                
                # Converti a float se necessario
                if price and isinstance(price, str):
                    price = float(price)
                
                if price:  # Includi solo se ha un prezzo
                    extracted_deal = {
                        'shop_name': shop_name,
                        'shop_logo': '',
                        'price': float(price) if price else None,
                        'url': deal.get('url', ''),
                        'is_best': idx == 0,  # Il primo è il migliore
                        'original_price': None,
                        'discount_price': None
                    }
                    extracted_deals.append(extracted_deal)
            except (ValueError, TypeError, AttributeError) as e:
                print(f"WARNING - Errore nel parsing deal {idx}: {e}")
                continue
    
    return extracted_deals