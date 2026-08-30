# 🎮 Game Deal Scraper

Una web app che **ricerca e aggrega le offerte più convenienti per videogiochi** da negozi online globali, utilizzando l'API di [IsThereAnyDeal](https://isthereanydeal.com/).

![Flask](https://img.shields.io/badge/Flask-2.3.3-green)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![BeautifulSoup4](https://img.shields.io/badge/BeautifulSoup4-4.12.2-yellow)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📋 Caratteristiche

✅ **Ricerca in tempo reale** — Cerca qualsiasi videogioco e ottieni i prezzi attuali da molteplici negozi  
✅ **Filtri avanzati** — Filtra per prezzo massimo, piattaforma, e altro  
✅ **Dashboard responsive** — Interfaccia moderna e mobile-friendly  
✅ **Integrazione API** — Sfrutta l'API pubblica di IsThereAnyDeal per dati sempre aggiornati  
✅ **Copertine resilienti** — Usa automaticamente la copertina verticale dello Steam Store se quella ITAD è assente o non caricabile
✅ **Zero scraping complesso** — Nessun web scraping, solo API pulite e stabili  
✅ **Wishlist locale** — Salva i giochi preferiti nel browser, senza account

---

## 🚀 Quickstart

### Prerequisiti

- Python 3.8 o superiore
- pip (gestore pacchetti Python)
- Git (opzionale, per clonare il repo)

### Installazione

1. **Clona il repository**
   ```bash
   git clone https://github.com/gabrielepalladino/Game-Deal-Scraper.git
   cd Game-Deal-Scraper
   ```

2. **Crea un virtual environment**
   ```bash
   python -m venv venv
   
   # Su Linux/Mac:
   source venv/bin/activate
   
   # Su Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   
   # Su Windows (CMD):
   venv\Scripts\activate.bat
   ```

3. **Installa le dipendenze**
   ```bash
   pip install -r requirements.txt
   ```

4. **Avvia l'app**
   ```bash
   python run.py
   ```

5. **Apri il browser**
   ```
   http://localhost:5000
   ```

---

## 📁 Struttura del Progetto

```
game-deal-scraper/
│
├── app/                          # Pacchetto principale Flask
│   ├── __init__.py              # Inizializzazione app Flask
│   ├── routes.py                # Route HTTP (homepage, ricerca, risultati)
│   └── scrapers/                # Moduli di data fetching
│       ├── __init__.py
│       └── game_scraper.py      # Logica di ricerca API IsThereAnyDeal
│
├── templates/                    # Template HTML Jinja2
│   ├── base.html                # Layout base (navbar, footer)
│   ├── index.html               # Homepage / form di ricerca
│   └── results.html             # Pagina risultati con giochi
│
├── static/                       # File statici (CSS, JS, immagini)
│   ├── css/
│   │   └── style.css            # Stile principale
│   └── js/
│       └── filters.js           # Logica filtri lato client
│
├── data/                         # Cache e storage dati
│   └── .gitkeep
│
├── run.py                       # Entry point (avvia l'app)
├── config.py                    # Configurazioni (porte, timeout, etc)
├── requirements.txt             # Dipendenze Python
├── .gitignore                   # File ignorati da Git
└── README.md                    # Questo file
```

---

## 🔧 Uso dell'App

### Ricerca semplice

1. Vai sulla homepage
2. Scrivi il nome del gioco nel campo "Cerca"
3. (Opzionale) Specifica un prezzo massimo
4. Clicca "Cerca"
5. Vedi i risultati con prezzi da vari negozi

### Filtri disponibili

| Filtro | Descrizione |
|--------|------------|
| **Query** | Nome del gioco (es: "Elden Ring", "Baldur's Gate 3") |
| **Prezzo massimo** | Mostra solo giochi sotto questo prezzo |
| (Futuro) **Piattaforma** | Filtra per PC, PlayStation, Xbox, etc |
| (Futuro) **Valutazione** | Mostra solo giochi con rating sopra la soglia |

---

## 📦 Dipendenze

| Libreria | Versione | Utilizzo |
|----------|----------|----------|
| Flask | 2.3.3 | Web framework Python |
| BeautifulSoup4 | 4.12.2 | Parsing HTML (future) |
| requests | 2.31.0 | HTTP requests per API |
| python-dotenv | 1.0.0 | Gestione variabili d'ambiente |

Tutte le dipendenze sono elencate in `requirements.txt`.

---

## 🔐 Configurazione

### File `.env` (opzionale)

Se IsThereAnyDeal richiede un'API key in futuro, crea un file `.env` alla root:

```env
ISTHEREANYDEAL_API_KEY=tua_api_key_qui
```

**⚠️ IMPORTANTE**: Non committare `.env` su GitHub. È già in `.gitignore`.

### Variabili di configurazione

Nel file `config.py` puoi personalizzare:

```python
DEBUG = True              # Modalità debug Flask
PORT = 5000              # Porta di ascolto
API_TIMEOUT = 5          # Timeout richieste API (secondi)
```

---

## 🌐 API Utilizzata

**IsThereAnyDeal** — https://isthereanydeal.com/api/v2/docs/ per ricerca e prezzi.

**Steam Store Search** — fallback pubblico senza API key usato esclusivamente per
individuare l'app id e mostrare la relativa copertina verticale ufficiale.

### Endpoint principali

| Endpoint | Utilizzo |
|----------|----------|
| `/v01/search/search/` | Ricerca giochi per query |
| `/v01/game/info/` | Dettagli e prezzi di un gioco specifico |

Consulta la [documentazione ufficiale](https://isthereanydeal.com/api/v2/docs/) per altri endpoint e parametri.

---

## 🛠️ Sviluppo Locale

### Avviare in modalità debug

```bash
python run.py
```

L'app è automaticamente in modalità debug. Ricaricamento automatico al cambio file.

### Test dell'API

Prova la ricerca direttamente in Python:

```python
from app.scrapers.game_scraper import search_games

games = search_games("elden ring")
for game in games[:3]:
    print(f"{game['title']} (ID: {game['id']})")
```

### Aggiungere una nuova route

In `app/routes.py`:

```python
@app.route('/api/games/<query>')
def api_games(query):
    """API endpoint che ritorna JSON"""
    games = search_games(query)
    return jsonify(games)
```

---

## 🚧 Roadmap (Funzionalità future)

- [ ] **Filtro per piattaforma** (PC, PlayStation, Xbox, Nintendo)
- [ ] **Filtro per valutazione** (Metacritic, IGDb)
- [ ] **Storico prezzi** (grafico dell'andamento prezzi nel tempo)
- [ ] **Notifiche** (avvisa quando un gioco scende sotto un certo prezzo)
- [x] **Wishlist** (salva giochi preferiti in locale)
- [ ] **Integrazione Twitch/YouTube** (link a trailer)
- [ ] **Database persistente** (SQLite/PostgreSQL)
- [ ] **Deploy su cloud** (Heroku, Vercel, Railway)

---

## 📚 Documentazione e Risorse

### Python & Flask

- [Flask Official Docs](https://flask.palletsprojects.com/)
- [Jinja2 Templating](https://jinja.palletsprojects.com/)
- [Requests Library](https://requests.readthedocs.io/)

### Web Scraping (per future evoluzioni)

- [BeautifulSoup Docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Selenium (per JavaScript-heavy sites)](https://selenium-python.readthedocs.io/)

### IsThereAnyDeal

- [API Documentation](https://isthereanydeal.com/api/v2/docs/)
- [Website](https://isthereanydeal.com/)

---

## 🤝 Contribuire

Le pull request sono benvenute! Per cambiamenti importanti:

1. Fai un fork del repository
2. Crea un branch (`git checkout -b feature/nuova-feature`)
3. Commit dei cambiamenti (`git commit -am 'Aggiungi nuova feature'`)
4. Push al branch (`git push origin feature/nuova-feature`)
5. Apri una Pull Request

---

## 📄 Licenza

Questo progetto è distribuito sotto licenza **MIT**. Vedi il file `LICENSE` per i dettagli.

---

## 👨‍💻 Autore

**Gabriele Palladino**  
GitHub: [@gabrielepalladino](https://github.com/gabrielepalladino)

---

## ❓ FAQ

**D: Come faccio a cercare un gioco specifico?**  
R: Scrivi il nome nel form della homepage. L'app cercherà tutti i giochi con quel nome.

**D: Che negozi sono supportati?**  
R: IsThereAnyDeal aggrega prezzi da 600+ negozi online (Steam, GOG, Epic Games Store, Ubisoft+, etc).

**D: Posso usare questa app in produzione?**  
R: Attualmente è un progetto di sviluppo. Per produzione, usa un server WSGI (gunicorn, uWSGI).

**D: Come aggiorno i dati?**  
R: Ogni ricerca chiama l'API di IsThereAnyDeal in tempo reale. Non c'è caching locale.

**D: Posso contribuire?**  
R: Assolutamente! Vedi la sezione "Contribuire" sopra.

---

## 📞 Supporto

Se hai domande, problemi o suggerimenti:

- 🐛 **Bug report**: Apri un [Issue](https://github.com/gabrielepalladino/Game-Deal-Scraper/issues)
- 💬 **Discussioni**: Usa le [Discussions](https://github.com/gabrielepalladino/Game-Deal-Scraper/discussions)

---

**Made with ❤️ by Gabriele Palladino**  
Last updated: August 28, 2026
