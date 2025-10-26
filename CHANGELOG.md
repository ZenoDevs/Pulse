# Changelog

Tutte le modifiche significative a questo progetto saranno documentate qui.

Il formato si basa su [Keep a Changelog](https://keepachangelog.com/it/1.0.0/),
e questo progetto aderisce a [Semantic Versioning](https://semver.org/lang/it/).

## [Unreleased]

### Planned for Phase 2
- BERTopic integration per topic modeling
- Sentence-transformers per embeddings multilingue
- Calcolo metriche Pulse (volume, velocity, spread, authority, novelty)
- Topic clustering e aggregazione
- Celery per scheduled jobs
- PostgreSQL migration da SQLite

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

[Unreleased]: https://github.com/ZenoDevs/Pulse/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/ZenoDevs/Pulse/releases/tag/v0.2.0
[0.1.0]: https://github.com/ZenoDevs/Pulse/releases/tag/v0.1.0
