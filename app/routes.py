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
    query = request.args.get('query', '').strip()
    max_price = request.args.get('max_price', '')
    
    # Validazione base
    if not query:
        return jsonify({'error': 'Query richiesta'}), 400
    
    # Converti max_price a numero (se inserito)
    try:
        max_price = float(max_price) if max_price else None
    except ValueError:
        return jsonify({'error': 'Prezzo massimo non valido'}), 400
    
    # Chiama la funzione di ricerca (ritorna già ordinati per prezzo)
    print(f"DEBUG - Ricerca per: {query}, max_price: {max_price}")
    games = search_games(query)
    print(f"DEBUG - Giochi trovati: {len(games)}")
    
    # Filtra per prezzo se specificato
    if max_price:
        games = [
            g for g in games 
            if g.get('lowest_price') and float(g.get('lowest_price', float('inf'))) <= max_price
        ]
        print(f"DEBUG - Giochi dopo filtro prezzo: {len(games)}")
    
    # I giochi sono già ordinati per prezzo grazie a search_games()
    # Ritorna i risultati
    return render_template('results.html', games=games, query=query)