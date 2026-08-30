from flask import render_template, request, jsonify
from app import app
from app.scrapers.game_scraper import build_search_url, search_games
import math


# Route per mostrare la homepage
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/wishlist')
def wishlist():
    """Mostra i giochi salvati nel browser dell'utente."""
    return render_template('wishlist.html')


# Route che riceve i dati dal form
@app.route('/search', methods=['GET'])
def search():
    """
    Ricerca giochi con supporto a paginazione
    
    Query parameters:
    - query: Nome del gioco (obbligatorio)
    - max_price: Prezzo massimo (opzionale)
    - page: Numero pagina (default 1)
    - per_page: Risultati per pagina (default 10, max 50)
    """
    
    # Ricevi i parametri dal form HTML
    query = request.args.get('query', '').strip()
    max_price = request.args.get('max_price', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Validazione
    if not query:
        return jsonify({'error': 'Query richiesta'}), 400
    
    # Valida e limita per_page
    per_page = max(1, min(int(per_page), 50))  # Min 1, max 50 risultati per pagina
    
    # Assicura che page sia almeno 1
    page = max(1, int(page))
    
    # Converti max_price a numero (se inserito)
    try:
        max_price = float(max_price) if max_price else None
    except ValueError:
        return jsonify({'error': 'Prezzo massimo non valido'}), 400
    
    # Chiama la funzione di ricerca (ritorna già ordinati per prezzo e rilevanza)
    print(f"DEBUG - Ricerca per: {query}, max_price: {max_price}")
    games = search_games(query, limit=100, max_price=max_price)  # Aumentato a 100
    print(f"DEBUG - Giochi trovati: {len(games)}")
    
    # Calcola paginazione
    total_games = len(games)
    total_pages = math.ceil(total_games / per_page) if total_games > 0 else 0
    
    # Valida il numero di pagina
    if page > total_pages and total_pages > 0:
        page = total_pages
    
    # Estrai i giochi per la pagina corrente
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_games = games[start_idx:end_idx]
    
    print(f"DEBUG - Paginazione: pagina {page}/{total_pages}, risultati {start_idx}-{end_idx}")
    
    # Ritorna i risultati
    return render_template(
        'results.html',
        games=paginated_games,
        query=query,
        page=page,
        total_pages=total_pages,
        total_games=total_games,
        per_page=per_page,
        max_price=max_price,
        build_search_url=build_search_url
    )
