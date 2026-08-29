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
        response = requests.get(url, headers=headers, params=params, timeout=5)
        response.raise_for_status()
        games = response.json()
        
        print(f"DEBUG - Giochi trovati: {len(games)}")
        
        # Ora per ogni gioco, recupera i prezzi/deals
        games_with_deals = []
        for game in games:
            game_with_deals = get_game_deals(game)
            if game_with_deals:
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


def get_game_deals(game):
    """Recupera i prezzi e le offerte per un gioco specifico"""
    
    # Il "plain" è l'identificatore corretto per l'endpoint /games/overview/v1
    # È il nome normalizzato del gioco (es: "cyberpunk-2077")
    game_plain = game.get('plain')
    
    if not game_plain:
        print(f"WARNING - Gioco senza 'plain': {game.get('title')}")
        return game  # Ritorna il gioco anche senza deals
    
    url = "https://api.isthereanydeal.com/games/overview/v1"
    
    headers = {
        "ITAD-API-Key": ITAD_API_KEY
    }
    
    # USO 'plain' INVECE DI 'id'
    params = {
        "plain": game_plain
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        # Estrai i dati delle offerte
        overview = data.get('overview', {})
        
        # Aggiungi le informazioni di prezzo al gioco
        game['lowest_price'] = overview.get('price')  # Campo principale del prezzo
        game['lowest_deal_price'] = overview.get('priceNew')  # Prezzo in offerta
        game['shop'] = overview.get('shop', {})
        
        # Prova a ottenere i dettagli dei negozi con i prezzi
        game['deals'] = extract_deals_from_list(data)
        
        print(f"✓ {game.get('title')} - Prezzo: €{game.get('lowest_price', 'N/A')}")
        
        return game
        
    except requests.exceptions.RequestException as e:
        print(f"Errore nel recupero deals per {game_plain}: {e}")
        return game  # Ritorna il gioco anche senza deals
    except ValueError as e:
        print(f"Errore JSON nei deals per {game_plain}: {e}")
        return game


def extract_deals_from_list(data):
    """Estrae una lista formattata di negozi e prezzi dai dati overview"""
    
    deals = []
    
    # I dati arrivano in formato "list" che contiene i vari negozi
    list_data = data.get('list', [])
    
    if isinstance(list_data, list) and list_data:
        # Itera sui negozi disponibili
        for idx, shop_data in enumerate(list_data[:15]):  # Top 15 negozi
            
            # Estrai i dati dello shop
            shop_info = shop_data.get('shop', {})
            shop_name = shop_info.get('name', 'Unknown')
            shop_logo = shop_info.get('logo', '')
            
            # Estrai il prezzo
            price = shop_data.get('price')
            price_new = shop_data.get('priceNew')  # Prezzo in offerta
            
            # Usa il prezzo in offerta se disponibile, altrimenti il prezzo normale
            final_price = price_new if price_new else price
            
            deal = {
                'shop_name': shop_name,
                'shop_logo': shop_logo,
                'price': final_price,
                'url': shop_data.get('url', ''),
                'is_best': idx == 0,  # Il primo è il migliore
                'original_price': price,
                'discount_price': price_new
            }
            
            if final_price:  # Includi solo se ha un prezzo
                deals.append(deal)
    
    return deals