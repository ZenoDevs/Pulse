# Changelog

Tutte le modifiche significative a questo progetto saranno documentate qui.

Il formato si basa su [Keep a Changelog](https://keepachangelog.com/it/1.0.0/),
e questo progetto aderisce a [Semantic Versioning](https://semver.org/lang/it/).

## [Unreleased]

### Planned for Phase 3
- Celery per scheduled jobs automatici
- Background tasks per scraping periodico
- Automatic topic recalculation
- PostgreSQL migration da SQLite
- Redis caching layer

## [0.3.0] - 2025-10-27

### Added - Phase 2 Complete: ML Topic Clustering & Pulse Metrics
- ✅ **Topic Service** (`services/topic_service.py`)
  - ML-based clustering con sentence-transformers
  - Embeddings multilingue 768-dim (paraphrase-multilingual-mpnet-base-v2)
  - K-Means clustering con automatic cluster count
  - TF-IDF keyword extraction
  - Auto-labeling dei topic da titoli articoli
  - Batch deduplication per evitare conflitti

- ✅ **Metrics Service** (`services/metrics_service.py`)
  - **Volume**: count articoli ultimi 24h
  - **Velocity**: crescita percentuale (-1.0 a +∞)
  - **Spread**: numero fonti distinte
  - **Authority**: credibilità media fonti (0.0-1.0)
  - **Novelty**: freschezza topic (0.0-1.0)
  - **PulseScore**: formula composita pesata
  - Update automatico di tutti i topic

- ✅ **Topics API** (`api/topics.py`)
  - `GET /api/topics` - Lista con filtri e sorting
  - `GET /api/topics/:id` - Dettagli singolo topic
  - `GET /api/topics/:id/articles` - Articoli del topic
  - `POST /api/topics/:id/refresh` - Ricalcola metrics
  - `POST /api/topics/refresh-all` - Aggiorna tutti

- ✅ **Database Schema**
  - Tabella `topics` con tutti i metrics
  - Foreign key `articles.topic_id` → `topics.topic_id`
  - TopicWithSources model con `article_count` e `sources`

- ✅ **Frontend Integration**
  - Rimosso mock `groupArticlesByTopic`
  - API client aggiornato con `getTopics()`, `getTopic()`, `getTopicArticles()`
  - `transformTopic()` per mapping backend → UI
  - Display real-time di 6 metrics: PulseScore, Volume, Velocity, Spread, Authority, Novelty
  - TrendCard con metrics reali
  - TopicDrawer con grid 3x2 per tutti i metrics

- ✅ **ML Dependencies**
  - sentence-transformers 2.3.1
  - scikit-learn 1.7.2 (K-Means, TF-IDF)
  - numpy, scipy, umap-learn, plotly

### Changed
- Storage Service ora gestisce batch deduplication
- CORS aggiornato per supportare porte 3000-3001
- Frontend carica topic da ML invece di raggruppamento client-side

### Fixed
- ARM64 Mac compatibility (dropped hdbscan, custom K-Means implementation)
- SQLAlchemy Base import issues risolti
- DetachedInstanceError nel test clustering
- UNIQUE constraint conflicts con batch deduplication
- TopicWithSources.article_count mancante nel model

### Technical Details
- 35 articoli ANSA → 4 topic clusters
- Embeddings generati in ~2.5s per 22 articoli
- Topics con labels italiani auto-generati
- Sistema end-to-end funzionante: scraping → clustering → metrics → frontend
- Test POC validato con successo

## [0.2.0] - 2025-10-27

### Added - Phase 1 Complete: Core Infrastructure
- ✅ **Parser Service** (`services/parser_service.py`)
  - Pulizia HTML con BeautifulSoup
  - Normalizzazione date multilingue
  - Deduplicazione URL intelligente
  - Test suite completa

- ✅ **Language Service** (`services/language_service.py`)
  - Language detection con langdetect
  - Country detection automatico
  - Entity extraction (persone, organizzazioni, luoghi)
  - Geo-tagging intelligente

- ✅ **Storage Service** (`services/storage_service.py`)
  - CRUD completo per articoli
  - Statistiche aggregate (per source, language, country)
  - Filtri avanzati (source, country, language, date range)
  - SQLite con SQLAlchemy

- ✅ **REST API** (`backend/main.py`, `backend/api/`)
  - FastAPI con CORS configurato
  - 10+ endpoints operativi
  - `/api/articles/` - Lista articoli con filtri
  - `/api/stats/overview` - Statistiche aggregate
  - `/api/scraping/sources` - Lista scrapers disponibili
  - `/api/scraping/run` - Trigger scraping manuale
  - Documentazione auto-generata su `/docs`

- ✅ **Frontend Dashboard** (`frontend/src/`)
  - React 18.2 con Vite 4.5
  - Tailwind CSS per styling
  - API integration layer (`services/api.js`)
  - Real-time data loading con useEffect
  - Filtri interattivi (paese, settore, ricerca)
  - Topic cards con metriche placeholder
  - Drawer per dettagli topic
  - Modalità Utente/Azienda
  - Loading states e error handling

- ✅ **Scrapers Improvements**
  - ANSA scraper con RSS feed
  - Reddit scraper con PRAW
  - HackerNews scraper
  - Registry pattern per gestione scrapers
  - Error handling robusto

### Changed
- Database migrato a SQLite (da PostgreSQL) per semplicità MVP
- Frontend proxy configurato in Vite per evitare CORS
- Struttura progetto riorganizzata con separation of concerns

### Fixed
- Vite dev server issues risolti
- CORS configuration ottimizzata
- Port conflicts (3000-3004) gestiti

### Technical Details
- 22+ articoli scraped e processati
- 3 scrapers operativi (ANSA, Reddit, HackerNews)
- Backend + Frontend completamente integrati
- API testata e funzionante
- Unit tests per tutti i services

## [0.1.0] - 2025-10-26

### Added
- Inizializzazione repository
- Struttura base progetto
- Setup iniziale scrapers modulari
- Schema database iniziale
- UI wireframe completo
- Documentazione README

[Unreleased]: https://github.com/ZenoDevs/Pulse/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/ZenoDevs/Pulse/releases/tag/v0.3.0
[0.2.0]: https://github.com/ZenoDevs/Pulse/releases/tag/v0.2.0
[0.1.0]: https://github.com/ZenoDevs/Pulse/releases/tag/v0.1.0
