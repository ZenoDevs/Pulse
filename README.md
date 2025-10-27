# Pulse 🚀

**Real-time Trend Intelligence Platform**

AI-powered trend monitoring and analysis system designed to identify emerging topics before they go mainstream, with predictive capabilities for 24-48h forecasting.

---

## 🎯 Overview

Pulse aggregates content from multiple sources (RSS, Reddit, YouTube, GDELT, Hacker News), processes it with NLP and ML to detect emerging trends, calculate proprietary "Pulse" metrics (volume, velocity, spread, authority, novelty), and forecast which topics will become mainstream in the next 24-48 hours.

### Key Features

- ✅ **Multi-Source Ingestion**: Modular scraper system (ANSA, Reddit, HackerNews)
- ✅ **Content Processing**: HTML cleaning, date normalization, deduplication
- ✅ **Language Detection**: Automatic language & country detection with entity extraction
- ✅ **REST API**: Complete FastAPI backend with articles, stats, scraping, and topics endpoints
- ✅ **Real-time Dashboard**: React frontend with topic cards, filters, and live metrics
- ✅ **Storage Service**: SQLite database with full CRUD operations
- ✅ **Topic Discovery**: ML-based clustering with sentence-transformers + K-Means
- ✅ **Pulse Metrics**: Volume, Velocity, Spread, Authority, Novelty, PulseScore
- 🚧 **Forecasting**: ETS/Holt-Winters for trend prediction (planned)

---

## 📁 Project Structure

```
Pulse/
├── backend/                 # Python Backend (FastAPI)
│   ├── api/                 # REST API endpoints
│   │   ├── articles.py      # Article CRUD & filtering
│   │   ├── stats.py         # Statistics & analytics
│   │   ├── scraping.py      # Scraper management & triggers
│   │   └── topics.py        # Topics, metrics & clustering
│   ├── config/              # Configuration (settings.py)
│   ├── models/              # Database models (SQLAlchemy + Pydantic)
│   │   ├── database.py      # DB setup & session management
│   │   ├── article.py       # Article model & schemas
│   │   └── topic.py         # Topic model (planned)
│   ├── scrapers/            # Modular web scrapers
│   │   ├── base_scraper.py  # Base interface
│   │   ├── ansa_scraper.py  # ANSA news (RSS)
│   │   ├── reddit_scraper.py # Reddit (PRAW)
│   │   ├── hackernews_scraper.py # Hacker News
│   │   └── registry.py      # Scraper registry
│   ├── services/            # Business logic
│   │   ├── parser_service.py    # HTML cleaning & normalization
│   │   ├── language_service.py  # Language detection & geo-tagging
│   │   ├── storage_service.py   # Database operations
│   │   ├── topic_service.py     # ML clustering & topic detection
│   │   └── metrics_service.py   # Pulse metrics calculation
│   ├── main.py              # FastAPI app with CORS
│   ├── requirements.txt     # Python dependencies
│   └── test_*.py            # Unit tests for services
│
├── frontend/                # React + Vite Frontend
│   ├── src/
│   │   ├── services/
│   │   │   └── api.js       # API client & data transformers
│   │   ├── App.jsx          # Main dashboard component
│   │   ├── App.full.jsx     # Backup of full UI
│   │   ├── main.jsx         # Entry point
│   │   └── index.css        # Tailwind CSS
│   ├── package.json
│   ├── vite.config.js       # Vite config with proxy
│   └── tailwind.config.js
│
├── data/                    # SQLite database (gitignored)
├── docs/                    # Documentation
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **SQLite** (included, no setup needed)

### 1. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Database will be auto-created on first run

# Start development server
uvicorn main:app --reload --port 8000

# API docs available at: http://localhost:8000/docs
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

### 3. Run Scrapers

```bash
# Using FastAPI endpoint (recommended)
curl -X POST http://localhost:8000/api/scraping/run \
  -H "Content-Type: application/json" \
  -d '{"source": "ansa", "max_articles": 20}'

# Or test individual scrapers directly
cd backend
python -c "
from scrapers.registry import ScraperRegistry
scraper = ScraperRegistry.get_scraper('ansa')
articles = scraper.scrape(max_articles=10)
print(f'Scraped {len(articles)} articles')
"
```

### 4. API Endpoints

- `GET /api/articles/` - List all articles (with filters: source, country, language, limit)
- `GET /api/stats/overview` - Get statistics (total, by source, language, country)
- `GET /api/scraping/sources` - List available scrapers
- `POST /api/scraping/run` - Trigger scraping for a source
- `GET /api/topics` - List topics with Pulse metrics (sort by pulse_score, volume, velocity, novelty)
- `GET /api/topics/:id` - Get single topic with details
- `GET /api/topics/:id/articles` - Get all articles for a topic
- `POST /api/topics/:id/refresh` - Recalculate metrics for a topic
- `POST /api/topics/refresh-all` - Refresh all topics metrics

---

## 🗺️ Roadmap

### ✅ **Phase 1: Core Infrastructure** (Completed)
- [x] Project structure setup
- [x] Modular scraper system with base interface
- [x] ANSA scraper (RSS feed)
- [x] Reddit scraper (PRAW)
- [x] HackerNews scraper
- [x] Database schema (SQLite with SQLAlchemy)
- [x] Parser Service (HTML cleaning, date normalization, deduplication)
- [x] Language Service (langdetect, country detection, entity extraction)
- [x] Storage Service (save_articles, get_articles, statistics)
- [x] REST API (FastAPI with CORS)
- [x] React frontend with Tailwind CSS
- [x] API integration layer (services/api.js)
- [x] Real-time dashboard with filters

### ✅ **Phase 2: Topic Detection & Analytics** (Completed)
- [x] Sentence-transformers for multilingual embeddings (paraphrase-multilingual-mpnet-base-v2)
- [x] Custom K-Means clustering for topic detection
- [x] Topic model & database schema with all metrics
- [x] Pulse metrics calculation (volume, velocity, spread, authority, novelty)
- [x] PulseScore composite formula implementation
- [x] Topic clustering algorithm with TF-IDF keyword extraction
- [x] Enhanced API endpoints for topics (GET /api/topics, /api/topics/:id, /api/topics/:id/articles)
- [x] Topic detail drawer with real-time metrics
- [x] Frontend integration with live data from ML clustering
- [x] Automatic topic-article linking with topic_id foreign key

### � **Phase 3: Scheduled Jobs & Automation** (Next)
- [ ] Celery setup for background tasks
- [ ] Scheduled scraping jobs (configurable intervals)
- [ ] Automatic topic recalculation
- [ ] Job monitoring & error handling

### 📅 **Phase 4: Advanced Features**
- [ ] Search functionality across articles
- [ ] Time series forecasting (ETS/Holt-Winters)
- [ ] Alert system (email/Slack webhooks)
- [ ] PDF report generator
- [ ] User authentication & authorization

### 📅 **Phase 5: Production Ready**
- [ ] Docker containerization
- [ ] PostgreSQL migration (from SQLite)
- [ ] Redis caching layer
- [ ] API rate limiting & quotas
- [ ] Monitoring & logging (Sentry, Prometheus)
- [ ] CI/CD pipeline

---

## 🧪 Testing & Development

### Testing Scrapers

```bash
# Test single scraper
python test_scrapers.py "bitcoin" --sources reddit --max-pages 2

# Test multiple scrapers with CSV output
python test_scrapers.py "AI" --sources ansa hackernews reddit --output results.csv --days-back 7
```

### Running Tests

```bash
cd backend

# Test parser service
python test_parser.py

# Test language service
python test_language_service.py

# Test storage service
python test_storage.py

# Test scrapers
python test_scrapers.py
```

### API Testing

With backend running on port 8000:

```bash
# Get all articles
curl http://localhost:8000/api/articles/

# Get statistics
curl http://localhost:8000/api/stats/overview

# Get articles from specific source
curl http://localhost:8000/api/articles/?source=ansa

# Trigger scraping
curl -X POST http://localhost:8000/api/scraping/run \
  -H "Content-Type: application/json" \
  -d '{"source": "ansa", "max_articles": 20}'
```

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern web framework
- **SQLAlchemy** - ORM with SQLite
- **Pydantic** - Data validation
- **BeautifulSoup4** - HTML parsing
- **feedparser** - RSS feed parsing
- **PRAW** - Reddit API client
- **langdetect** - Language detection
- **sentence-transformers** - Multilingual embeddings for topic clustering
- **scikit-learn** - K-Means clustering & TF-IDF keyword extraction
- **numpy** - Numerical computing for embeddings

### Frontend
- **React 18.2** - UI framework
- **Vite 4.5** - Build tool & dev server
- **Tailwind CSS 3.4** - Utility-first CSS
- **Lucide React** - Modern icon library
- **Axios** - HTTP client (planned)

### Current Stack
- **SQLite** - Embedded database (will migrate to PostgreSQL)
- **Python 3.10+** - Backend runtime
- **Node.js 18+** - Frontend tooling

---

## 📊 Database Schema

### Articles Table (Implemented)
```sql
CREATE TABLE articles (
    id INTEGER PRIMARY KEY,
    source VARCHAR(50),           -- ansa, reddit, hackernews
    source_id VARCHAR(255) UNIQUE,
    title TEXT,
    content TEXT,
    url TEXT,
    published_at DATETIME,
    scraped_at DATETIME,
    country VARCHAR(10),          -- ITA, USA, GBR, GLOBAL, etc.
    language VARCHAR(10),         -- it, en, fr, etc.
    sector VARCHAR(50),           -- News, Tech, Sport, etc.
    entities JSON,                -- Named entities extracted
    raw_metadata JSON             -- Original scraper data
)
```

### Topics Table (Implemented in Phase 2)
```sql
CREATE TABLE topics (
    id INTEGER PRIMARY KEY,
    topic_id VARCHAR(50) UNIQUE,  -- e.g., "topic_0", "topic_1"
    label VARCHAR(255),            -- Auto-generated topic label
    keywords JSON,                 -- Top keywords from TF-IDF
    description TEXT,              -- Summary description
    pulse_score FLOAT,             -- Composite metric (weighted formula)
    volume INTEGER,                -- Articles in last 24h
    velocity FLOAT,                -- Growth rate (-1.0 to +∞)
    spread INTEGER,                -- Number of distinct sources
    authority FLOAT,               -- Source credibility (0.0-1.0)
    novelty FLOAT,                 -- Topic freshness (0.0-1.0)
    variance FLOAT,                -- Statistical variance
    sentiment_avg FLOAT,           -- Average sentiment
    country VARCHAR(10),           -- Geographic focus
    sector VARCHAR(50),            -- Category
    first_seen DATETIME,           -- First article timestamp
    last_updated DATETIME          -- Last metrics update
)
```

**Articles-Topics Link**: `articles.topic_id` → `topics.topic_id` (foreign key)

---

## 🔑 Configuration

The backend uses `backend/config/settings.py` for configuration. Key settings:

```python
# Database
DATABASE_URL = "sqlite:///./data/pulse.db"  # Auto-created

# Reddit API (optional - for Reddit scraper)
# Get credentials from: https://www.reddit.com/prefs/apps
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = "PulseBot/1.0"

# Scraping defaults
DEFAULT_MAX_ARTICLES = 50
DEFAULT_SCRAPING_TIMEOUT = 30

# Future ML settings (Phase 2)
# EMBEDDINGS_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
# MIN_TOPIC_SIZE = 5
```

Create `backend/.env` for sensitive credentials (optional):
```bash
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_secret
```

---

## 📝 License

**Proprietary License** - All Rights Reserved

This software is proprietary and confidential. Unauthorized copying, distribution, 
or use is strictly prohibited. See [LICENSE](LICENSE) file for details.

For licensing inquiries: info@zenodevs.com

---

## 📧 Contact

For questions or support, open an Issue on GitHub.

---

---

## 📸 Screenshots

### Dashboard
![Pulse Dashboard](docs/screenshots/dashboard.png)
*Real-time trend monitoring with filters by country and sector*

### Topic Details
![Topic Drawer](docs/screenshots/topic-detail.png)
*Detailed view with pulse metrics, timeline, and sources*

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## ✅ Current Status

**Phase 2 Complete** - ML-based topic clustering with real-time Pulse metrics

- ✅ 3 scrapers operational (ANSA, Reddit, HackerNews)
- ✅ Parser & Language services with NLP
- ✅ REST API with 15+ endpoints (articles, stats, scraping, topics)
- ✅ React dashboard with real-time data and live metrics
- ✅ ML topic clustering with sentence-transformers (768-dim embeddings)
- ✅ 6 Pulse metrics calculated: Volume, Velocity, Spread, Authority, Novelty, PulseScore
- ✅ 35+ articles clustered into 4 topics with automatic labeling
- ✅ Frontend displays real ML-generated topics with live metrics
- 🚧 Next: Scheduled jobs & automation (Phase 3)
