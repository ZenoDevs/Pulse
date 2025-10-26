# Quick Start Guide - Pulse

## Primo avvio del progetto

### 1. Setup Database PostgreSQL

```bash
# Installa PostgreSQL se non già presente
brew install postgresql@14  # macOS
# oppure scarica da https://www.postgresql.org/download/

# Avvia PostgreSQL
brew services start postgresql@14

# Crea database
createdb pulse_db

# Crea utente (opzionale)
psql pulse_db
CREATE USER pulse WITH PASSWORD 'pulse';
GRANT ALL PRIVILEGES ON DATABASE pulse_db TO pulse;
```

### 2. Setup Backend

```bash
cd backend

# Virtual environment
python3 -m venv venv
source venv/bin/activate

# Installa dipendenze
pip install -r requirements.txt

# Configura .env
cp .env.example .env

# IMPORTANTE: Modifica .env con:
# - DATABASE_URL corretto
# - REDDIT_CLIENT_ID e REDDIT_CLIENT_SECRET (ottieni da reddit.com/prefs/apps)
```

### 3. Test Scrapers (senza DB)

```bash
# Test veloce - verifica che gli scrapers funzionino
python test_scrapers.py "intelligenza artificiale" --sources ansa --max-pages 2
```

Output atteso:
```
🔍 Scraping per: 'intelligenza artificiale'
📅 Range: 2025-10-19 -> 2025-10-26
📰 Fonti: ['ansa']

Scraping ansa...
  -> 24 articoli da ansa

✅ Trovati 24 articoli:
   - Fonti: {'ansa': 24}
```

### 4. Avvia Backend API

```bash
uvicorn main:app --reload --port 8000
```

Verifica: http://localhost:8000 (dovrebbe rispondere con status)

### 5. Setup Frontend

```bash
cd frontend

npm install
npm run dev
```

Apri http://localhost:3000

---

## Prossimi Step

### A. Implementare il primo Job di Scraping schedulato

Crea `backend/jobs/scraping_job.py`:

```python
from celery import Celery
from backend.scrapers import scraper_registry
from backend.models.database import SessionLocal
from backend.models import Article

app = Celery('pulse', broker='redis://localhost:6379/0')

@app.task
def scrape_and_store():
    """Job schedulato per scraping periodico"""
    queries = ["intelligenza artificiale", "politica italiana", "tecnologia"]
    
    for query in queries:
        df = scraper_registry.scrape_all(
            query=query,
            max_pages=5
        )
        
        # Salva in DB
        db = SessionLocal()
        for _, row in df.iterrows():
            article = Article(
                source=row['source'],
                source_id=row['source_id'],
                title=row['title'],
                content=row['content'],
                url=row['url'],
                published_at=row['published_at']
            )
            db.add(article)
        
        db.commit()
        db.close()
```

### B. Aggiungere Language Detection

```bash
pip install langdetect
```

Crea `backend/services/language_detector.py`:

```python
from langdetect import detect
import pandas as pd

def detect_language(text: str) -> str:
    try:
        return detect(text)
    except:
        return 'unknown'

def add_language_column(df: pd.DataFrame) -> pd.DataFrame:
    df['language'] = df['content'].apply(detect_language)
    return df
```

### C. Implementare API Endpoint per Topics

Crea `backend/api/topics.py`:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.models.database import get_db
from backend.models import Topic, TopicSchema

router = APIRouter(prefix="/topics", tags=["topics"])

@router.get("/", response_model=list[TopicSchema])
def get_top_topics(
    limit: int = 10,
    country: str = None,
    sector: str = None,
    db: Session = Depends(get_db)
):
    """Ritorna i top topic ordinati per pulse_score"""
    query = db.query(Topic).order_by(Topic.pulse_score.desc())
    
    if country:
        query = query.filter(Topic.country == country)
    if sector:
        query = query.filter(Topic.sector == sector)
    
    topics = query.limit(limit).all()
    return topics
```

Poi aggiungi in `main.py`:
```python
from backend.api import topics
app.include_router(topics.router, prefix="/api/v1")
```

---

## Troubleshooting

### Errore: "No module named 'backend'"

Assicurati di essere nella directory `Pulse/` (root del progetto) quando esegui i comandi, oppure aggiungi:

```bash
export PYTHONPATH="${PYTHONPATH}:/Users/Edoardo.dng/Desktop/Pulse/Pulse"
```

### Errore Reddit API

Se non hai ancora credenziali Reddit:
1. Vai su https://www.reddit.com/prefs/apps
2. Crea una "script app"
3. Copia client_id e client_secret in `.env`

Per ora puoi testare senza Reddit usando solo ANSA e HackerNews:
```bash
python test_scrapers.py "AI" --sources ansa hackernews
```

### Database connection error

Verifica che PostgreSQL sia attivo:
```bash
brew services list | grep postgresql
```

Testa la connessione:
```bash
psql -d pulse_db -c "SELECT version();"
```

---

## Metriche di Successo - MVP Settimana 2

- [x] Struttura progetto completa
- [x] 3+ scrapers funzionanti (ANSA, Reddit, HN)
- [x] Schema database definito
- [x] UI base con wireframe
- [ ] Primo job di scraping schedulato funzionante
- [ ] Almeno 100 articoli in DB
- [ ] API endpoint `/topics` che ritorna mock data

**Target settimana prossima**: BERTopic integration + calcolo metriche Pulse reali
