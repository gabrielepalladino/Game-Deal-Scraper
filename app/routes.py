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
    query = request.form.get('query')  # Il valore di name="query"
    max_price = request.form.get('max_price')  # Il valore di name="max_price"
    
    # Validazione base
    if not query:
        return jsonify({'error': 'Query richiesta'}), 400
    
    # Converti max_price a numero (se inserito)
    max_price = float(max_price) if max_price else None
    
    # Chiama la tua funzione Python
    games = search_games(query)
    
    # Filtra per prezzo se specificato
    if max_price:
        games = [g for g in games if g.get('price', float('inf')) <= max_price]
    
    # Ritorna i risultati come JSON (o HTML template)
    return render_template('results.html', games=games, query=query)