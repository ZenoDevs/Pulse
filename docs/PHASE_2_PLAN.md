# Phase 2: Topic Detection & Pulse Metrics

**Goal**: Transform scattered articles into topic clusters with meaningful metrics that show the "pulse" of trends.

**Timeline**: 2-3 weeks
**Status**: 🚧 In Planning

---

## 🎯 Objectives

1. **Automatic Topic Clustering**: Group similar articles using NLP
2. **Pulse Metrics**: Calculate metrics that quantify topic intensity and growth
3. **Real Dashboard**: Frontend displays REAL topics (no more mock data)
4. **Topic Evolution**: Track how topics evolve over time

---

## 📦 Deliverables

### Backend
- [ ] Service: `topic_service.py` - BERTopic integration & clustering
- [ ] Service: `metrics_service.py` - Pulse metrics calculation
- [ ] Model: `topic.py` - Updated with all necessary fields
- [ ] API: `/api/topics/` - CRUD topics
- [ ] API: `/api/topics/{id}/history` - Time series for topic
- [ ] Migration: Add foreign key `articles.topic_id`
- [ ] Job: Topic recalculation scheduler

### Frontend
- [ ] Fetch real topics from API (remove mock `groupArticlesByTopic`)
- [ ] Display real metrics in topic cards
- [ ] Add sparkline for velocity trend
- [ ] Topic drawer with history chart

### Testing
- [ ] Unit test: `test_topic_service.py`
- [ ] Unit test: `test_metrics_service.py`
- [ ] Integration test: End-to-end clustering pipeline

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    ARTICLES (existing)                   │
│   id, title, content, language, country, scraped_at    │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │   TOPIC SERVICE      │
        │  - sentence-transformers │
        │  - BERTopic clustering   │
        │  - Label generation      │
        └──────────┬───────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │   METRICS SERVICE    │
        │  - Volume calculation│
        │  - Velocity (delta)  │
        │  - Spread (sources)  │
        │  - Authority scores  │
        │  - Novelty index     │
        │  - PulseScore formula│
        └──────────┬───────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│                    TOPICS (new)                          │
│  id, topic_id, label, keywords, pulse_score, volume,   │
│  velocity, spread, authority, novelty, sentiment_avg,   │
│  country, sector, first_seen, last_updated, history    │
└─────────────────────────────────────────────────────────┘
                   │
                   ▼ (1-to-many)
┌─────────────────────────────────────────────────────────┐
│           ARTICLES.topic_id (foreign key)               │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Technical Stack

### New Dependencies
```txt
# NLP & ML
sentence-transformers==2.2.2      # Multilingual embeddings
bertopic==0.15.0                  # Topic modeling
umap-learn==0.5.4                 # Dimensionality reduction
hdbscan==0.8.33                   # Clustering algorithm

# Optional (advanced features)
# spacy==3.7.0                    # NER & advanced NLP
# transformers==4.35.0            # Hugging Face models
```

### Models to Use
- **Embeddings**: `paraphrase-multilingual-mpnet-base-v2` (supports 50+ languages)
- **BERTopic**: Default settings + custom stopwords
- **Min cluster size**: 3-5 articles (configurabile)

---

## 📊 Pulse Metrics Formulas

### 1. Volume
```python
volume = count(articles in topic in last 24h)
```

### 2. Velocity
```python
velocity = (volume_now - volume_24h_ago) / volume_24h_ago
# Range: -1.0 to +∞
# Example: +0.5 = +50% growth in 24h
```

### 3. Spread
```python
spread = count(distinct sources for topic)
# Range: 1 to N (number of sources)
# High spread = topic discussed across multiple sources
```

### 4. Authority
```python
# Weighted by source credibility
authority_scores = {
    'ansa': 0.9,
    'reuters': 0.95,
    'reddit': 0.4,
    'hackernews': 0.6,
    'twitter': 0.3
}
authority = sum(authority_scores[article.source] for article in topic) / volume
# Range: 0.0 to 1.0
```

### 5. Novelty
```python
# How "fresh" is the topic
hours_since_first_seen = (now - topic.first_seen).total_seconds() / 3600
novelty = 1.0 / (1.0 + hours_since_first_seen / 24.0)
# Range: 0.0 to 1.0
# New topics have novelty ~1.0, old topics decay toward 0.0
```

### 6. PulseScore (Composite)
```python
# Weighted combination
pulse_score = (
    volume * 0.25 +
    (velocity + 1.0) * 0.3 +  # Normalize velocity to [0, ∞)
    spread * 0.15 +
    authority * 100 * 0.15 +
    novelty * 100 * 0.15
)
# Range: roughly 0 to 100+
# High score = hot emerging trend
```

**Formula tunable via config:**
```python
PULSE_WEIGHTS = {
    'volume': 0.25,
    'velocity': 0.30,
    'spread': 0.15,
    'authority': 0.15,
    'novelty': 0.15
}
```

---

## 🗄️ Database Schema Updates

### Topics Table (New)
```sql
CREATE TABLE topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id VARCHAR(50) UNIQUE NOT NULL,  -- BERTopic cluster ID
    label VARCHAR(255) NOT NULL,           -- Auto-generated label
    keywords JSON,                         -- ["keyword1", "keyword2", ...]
    description TEXT,                      -- Summary of topic
    
    -- Pulse Metrics
    pulse_score FLOAT DEFAULT 0.0,
    volume INTEGER DEFAULT 0,
    velocity FLOAT DEFAULT 0.0,
    spread INTEGER DEFAULT 0,
    authority FLOAT DEFAULT 0.0,
    novelty FLOAT DEFAULT 0.0,
    variance FLOAT DEFAULT 0.0,
    sentiment_avg FLOAT DEFAULT 0.0,
    
    -- Classification
    country VARCHAR(10),                   -- Primary country
    sector VARCHAR(50),                    -- News, Tech, Finance, etc.
    
    -- Timestamps
    first_seen DATETIME NOT NULL,
    last_updated DATETIME NOT NULL,
    
    -- Time series for forecasting
    history JSON                           -- [{"timestamp": "...", "volume": 10, ...}, ...]
)
```

### Articles Table (Update)
```sql
ALTER TABLE articles ADD COLUMN topic_id VARCHAR(50);
ALTER TABLE articles ADD FOREIGN KEY (topic_id) REFERENCES topics(topic_id);
CREATE INDEX idx_articles_topic_id ON articles(topic_id);
```

---

## 🔄 Clustering Pipeline

### Step-by-Step Process

**1. Data Preparation**
```python
# Get all articles from last 7 days
articles = storage_service.get_articles(days_back=7)

# Prepare text for embedding
texts = [f"{art.title}. {art.content[:500]}" for art in articles]
```

**2. Generate Embeddings**
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
embeddings = model.encode(texts, show_progress_bar=True)
```

**3. Cluster with BERTopic**
```python
from bertopic import BERTopic

topic_model = BERTopic(
    language='multilingual',
    min_topic_size=3,
    nr_topics='auto'
)

topics, probs = topic_model.fit_transform(texts, embeddings)
```

**4. Extract Topic Info**
```python
topic_info = topic_model.get_topic_info()

for topic_id in topic_info['Topic']:
    if topic_id == -1:  # Skip outliers
        continue
    
    # Get top keywords
    keywords = topic_model.get_topic(topic_id)[:10]
    
    # Get articles in this cluster
    cluster_articles = [art for art, t in zip(articles, topics) if t == topic_id]
    
    # Generate label (use most representative title)
    label = cluster_articles[0].title
    
    # Save to DB
    topic = Topic(
        topic_id=f"topic_{topic_id}",
        label=label,
        keywords=[kw[0] for kw in keywords],
        first_seen=min(art.published_at for art in cluster_articles),
        last_updated=datetime.now()
    )
    db.add(topic)
```

**5. Calculate Metrics**
```python
# For each topic
for topic in topics:
    metrics = metrics_service.calculate_pulse_metrics(topic)
    topic.pulse_score = metrics['pulse_score']
    topic.volume = metrics['volume']
    topic.velocity = metrics['velocity']
    # ... etc
    db.commit()
```

**6. Update Articles**
```python
# Link articles to topics
for article, topic_id in zip(articles, topics):
    if topic_id != -1:
        article.topic_id = f"topic_{topic_id}"
        db.commit()
```

---

## 📝 Implementation Checklist

### Week 1: Core Infrastructure
- [ ] Day 1-2: Install dependencies, setup sentence-transformers
- [ ] Day 3: Create `topic_service.py` with embedding generation
- [ ] Day 4: Implement BERTopic clustering
- [ ] Day 5: Test clustering on existing 22 articles (PoC)

### Week 2: Metrics & Database
- [ ] Day 1: Create Topics table migration
- [ ] Day 2: Implement `metrics_service.py` with all 6 metrics
- [ ] Day 3: Add topic_id foreign key to articles
- [ ] Day 4: Create API endpoints for topics
- [ ] Day 5: Write unit tests

### Week 3: Frontend & Polish
- [ ] Day 1-2: Update frontend to fetch real topics
- [ ] Day 3: Visualize real metrics in cards
- [ ] Day 4: Add sparkline/chart for velocity
- [ ] Day 5: Testing end-to-end + bug fixes

---

## 🧪 Testing Strategy

### Unit Tests
```python
def test_embedding_generation():
    texts = ["Test article about AI", "Another AI article"]
    embeddings = topic_service.generate_embeddings(texts)
    assert embeddings.shape == (2, 768)  # MPNET embedding size

def test_pulse_score_calculation():
    topic = Topic(volume=10, velocity=0.5, spread=3, authority=0.8, novelty=0.9)
    score = metrics_service.calculate_pulse_score(topic)
    assert 0 <= score <= 150

def test_clustering_minimum_articles():
    # Should handle small datasets gracefully
    articles = storage_service.get_articles(limit=5)
    topics = topic_service.cluster_articles(articles)
    assert len(topics) >= 1
```

### Integration Tests
```python
def test_end_to_end_pipeline():
    # Scrape → Parse → Language → Storage → Topic → Metrics
    scraper = ScraperRegistry.get_scraper('ansa')
    raw_articles = scraper.scrape(max_articles=10)
    
    parsed = parser_service.parse_articles(raw_articles)
    processed = language_service.process_articles(parsed)
    storage_service.save_articles(processed)
    
    # Cluster
    topics = topic_service.cluster_and_create_topics()
    assert len(topics) > 0
    
    # Verify metrics calculated
    for topic in topics:
        assert topic.pulse_score > 0
        assert topic.volume > 0
```

---

## 🚀 Success Metrics

**Phase 2 is successful if:**
1. ✅ BERTopic clusters 50+ articles into 5-10 meaningful topics
2. ✅ Topics have meaningful labels (Italian/English based on content)
3. ✅ PulseScore correlates with actual "hotness" (manual validation)
4. ✅ Dashboard shows real topics with real metrics
5. ✅ Velocity correctly shows growing vs declining topics
6. ✅ System handles incremental updates (new articles → update topics)

---

## 🎓 Resources & Documentation

- BERTopic Docs: https://maartengr.github.io/BERTopic/
- sentence-transformers: https://www.sbert.net/
- Multilingual Models: https://www.sbert.net/docs/pretrained_models.html
- UMAP: https://umap-learn.readthedocs.io/

---

## 🤔 Open Questions

1. **Re-clustering frequency**: Every 1h? 6h? 24h?
2. **Topic lifecycle**: When to "archive" an old topic?
3. **Min cluster size**: 3 articles ok or too small?
4. **Outliers handling**: What to do with articles that don't match any topic?
5. **Multi-language**: Separate clusters per language or together?

---

**Next Action**: Start with Proof of Concept - test BERTopic on existing 22 articles.
