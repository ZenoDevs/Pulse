# Pulse 🚀

**Real-time Trend Intelligence Platform**

AI-powered trend monitoring and analysis system designed to identify emerging topics before they go mainstream, with predictive capabilities for 24-48h forecasting.

---

## 🎯 Overview

Pulse aggregates content from multiple sources (RSS, Reddit, YouTube, GDELT, Hacker News), processes it with NLP and ML to detect emerging trends, calculate proprietary "Pulse" metrics (volume, velocity, spread, authority, novelty), and forecast which topics will become mainstream in the next 24-48 hours.

### Key Features

- ✅ **Multi-Source Ingestion**: RSS, Reddit, YouTube, GDELT, Hacker News
- ✅ **Topic Discovery**: BERTopic with multilingual embeddings
- ✅ **Pulse Metrics**: Volume, Velocity, Spread, Authority, Novelty, Variance
- ✅ **On-Demand Search**: Research agent for specific topics
- 🚧 **Forecasting**: ETS/Holt-Winters for trend prediction (in development)
- 🚧 **Alert System**: Email/Slack notifications (in development)
- 🚧 **Report Generator**: PDF executive summaries (in development)

---

## 📁 Project Structure

```
Pulse/
├── backend/                 # Python Backend (FastAPI)
│   ├── api/                 # REST API endpoints
│   ├── config/              # Configuration (settings.py)
│   ├── jobs/                # Scheduled jobs (Celery)
│   ├── models/              # Database models (SQLAlchemy + Pydantic)
│   ├── scrapers/            # Modular web scrapers
│   │   ├── base_scraper.py  # Base interface
│   │   ├── ansa_scraper.py  # ANSA news
│   │   ├── reddit_scraper.py # Reddit
│   │   ├── hackernews_scraper.py # Hacker News
│   │   └── registry.py      # Scraper registry
│   ├── services/            # Business logic (NLP, ML, forecasting)
│   ├── main.py              # FastAPI app
│   ├── requirements.txt     # Python dependencies
│   └── test_scrapers.py     # CLI tool for testing scrapers
│
├── frontend/                # React + Vite Frontend
│   ├── src/
│   │   ├── App.jsx          # Main component
│   │   ├── main.jsx         # Entry point
│   │   └── index.css        # Tailwind CSS
│   ├── package.json
│   └── vite.config.js
│
├── data/                    # Data storage (gitignored)
├── docs/                    # Documentation
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **PostgreSQL 14+**
- **Redis** (per Celery)
- **MongoDB** (opzionale, per content store)

### 1. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials (DB, Reddit API, etc)

# Initialize database
# Make sure PostgreSQL is running
python -c "from models.database import init_db; init_db()"

# Start development server
uvicorn main:app --reload --port 8000
```

### 2. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 3. Test Scrapers

```bash
cd backend
python test_scrapers.py "intelligenza artificiale" --sources ansa reddit hackernews --max-pages 3
```

---

## 🗺️ Roadmap

### ✅ **Week 1-2: Ingestion & Analytics Base** (Completed)
- [x] Project structure setup
- [x] Modular scrapers (ANSA, Reddit, HackerNews)
- [x] Database schema (PostgreSQL)
- [x] Base UI with React wireframe
- [ ] Parser/Normalizer + Deduplication
- [ ] Language Detection/Geo tagging
- [ ] Job scheduler (Celery)

### 🚧 **Week 3: Topic & Pulse** (In Progress)
- [ ] Multilingual embeddings (sentence-transformers)
- [ ] BERTopic integration
- [ ] Pulse metrics calculation (volume, velocity, spread, etc)
- [ ] PulseScore formula
- [ ] API endpoints for Top Topics
- [ ] Topic details with citations (RAG)

### 📅 **Week 4: On-Demand Search**
- [ ] Search agent (query generation)
- [ ] Ephemeral index for custom searches
- [ ] Multi-source result fusion
- [ ] UI: search box with live/on-demand badges

### 📅 **Week 5: Forecast MVP**
- [ ] ETS/Holt-Winters on topics with sufficient history
- [ ] Confidence bands + heuristic fallback
- [ ] sMAPE metrics for internal evaluation

### 📅 **Week 6: Alerts & Reports**
- [ ] Alert rules (country/category/threshold)
- [ ] Email/Slack webhooks
- [ ] PDF report generator (executive summary)
- [ ] Quality logging (accuracy, lead-time)

### 📅 **Month 2-3: Advanced Prediction**
- [ ] Labeled historical data collection
- [ ] 48h mainstream classifier
- [ ] Sector-specific threshold tuning
- [ ] Hardening (job monitoring, retry, API quotas)

---

## 🧪 Testing & Development

### Testing Scrapers

```bash
# Test single scraper
python test_scrapers.py "bitcoin" --sources reddit --max-pages 2

# Test multiple scrapers with CSV output
python test_scrapers.py "AI" --sources ansa hackernews reddit --output results.csv --days-back 7
```

### API Testing

With backend running:

```bash
# Health check
curl http://localhost:8000/api/v1/health

# TODO: More endpoints when implemented
```

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM (PostgreSQL)
- **Celery** - Task queue
- **Redis** - Cache & message broker
- **BeautifulSoup** - Web scraping
- **PRAW** - Reddit API
- **sentence-transformers** - Embeddings multilingue
- **BERTopic** - Topic modeling
- **statsmodels/prophet** - Time series forecasting

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Lucide React** - Icons
- **Axios** - HTTP client

### Infrastructure
- **PostgreSQL** - Database relazionale
- **MongoDB** - Content store (opzionale)
- **Docker** - Containerization (TODO)

---

## 📊 Database Schema

### Articles Table
```sql
- id (PK)
- source (ansa, reddit, youtube, gdelt, hn)
- source_id (unique)
- title, content, url
- published_at, scraped_at
- country, language, sector
- engagement_score, authority_score
- embedding_vector (JSON), topic_id
- sentiment_score
- raw_metadata (JSON)
```

### Topics Table
```sql
- id (PK), topic_id (BERTopic ID)
- label, keywords (JSON), description
- pulse_score, volume, velocity, spread
- authority, novelty, variance, sentiment_avg
- country, sector
- first_seen, last_updated
- history (JSON) # per forecasting
```

---

## 🔑 Environment Variables

Create `backend/.env` based on `.env.example`:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/pulse_db
MONGO_URL=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379/0

# Reddit API (get from https://www.reddit.com/prefs/apps)
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_secret
REDDIT_USER_AGENT=PulseBot/1.0

# GDELT & YouTube (optional)
# GDELT_API_KEY=
# YOUTUBE_API_KEY=

# Scraping
SCRAPING_INTERVAL_MINUTES=10
MAX_PAGES_PER_SOURCE=10

# ML
EMBEDDINGS_MODEL=sentence-transformers/paraphrase-multilingual-mpnet-base-v2
MIN_TOPIC_SIZE=5
```

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file.

---

## 📧 Contact

For questions or support, open an Issue on GitHub.

---

**Status**: MVP in development (Week 2/12)
