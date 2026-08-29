from flask import render_template, request, jsonify
from app import app
from app.scrapers.game_scraper import search_games

# Route per mostrare la homepage
@app.route('/')
def index():
    return render_template('index.html')

# Route che riceve i dati dal form
@app.route('/search', methods=['GET'])
def search():
    # Ricevi i parametri dal form HTML
    query = request.args.get('query', '').strip() #USA REQUEST.ARGS NON REQUEST.FORM
    max_price = request.args.get('max_price', '')
    
    # Validazione base
    if not query:
        return jsonify({'error': 'Query richiesta'}), 400
    
    # Converti max_price a numero (se inserito)
    max_price = float(max_price) if max_price else None
    
    # Chiama la funzione di ricerca
    print(f"DEBUG - Ricerca per: {query}, max_price: {max_price}")
    games = search_games(query)
    print(f"DEBUG - Giochi trovati: {len(games)}")
    print(f"DEBUG - Giochi: {games}")
    
    # Filtra per prezzo se specificato
    if max_price and games:
        games = [
            g for g in games 
            if isinstance(g, dict) and g.get('price') and float(g.get('price', float('inf'))) <= max_price
        ]
    
    # Ritorna i risultati
    return render_template('results.html', games=games, query=query)