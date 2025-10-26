"""
Test Database & Storage Service
End-to-end: scrape -> parse -> detect language -> save DB -> retrieve
"""
from models.database import init_db, engine
from models import Article
from scrapers import scraper_registry
from services.parser_service import parser_service
from services.language_service import language_service
from services.storage_service import storage_service
from datetime import datetime, timedelta

print("=" * 60)
print("DATABASE & STORAGE SERVICE TEST")
print("=" * 60)

# Step 1: Init database
print("\n1️⃣  Initializing database...")
try:
    init_db()
    print("✅ Database initialized")
    
    # Verifica tabelle create
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"   Tables: {tables}")
    
except Exception as e:
    print(f"❌ Database init error: {e}")
    exit(1)

# Step 2: Scrape articles
print("\n2️⃣  Scraping articles from ANSA...")
try:
    df = scraper_registry.scrape_all(
        query="tecnologia",
        sources=['ansa'],
        max_pages=1
    )
    print(f"✅ Scraped {len(df)} raw articles")
    
except Exception as e:
    print(f"❌ Scraping error: {e}")
    exit(1)

# Step 3: Parse articles
print("\n3️⃣  Parsing and normalizing...")
try:
    articles = parser_service.parse_dataframe(df)
    print(f"✅ Parsed {len(articles)} articles")
    
except Exception as e:
    print(f"❌ Parsing error: {e}")
    exit(1)

# Step 4: Language detection & enrichment
print("\n4️⃣  Detecting language and country...")
try:
    enriched = []
    for article in articles:
        article_dict = article.model_dump()
        enriched_dict = language_service.enrich_article(article_dict)
        
        # Update article object
        from models import ArticleCreate
        enriched_article = ArticleCreate(**enriched_dict)
        enriched.append(enriched_article)
    
    print(f"✅ Enriched {len(enriched)} articles")
    
    # Sample enriched article
    if enriched:
        sample = enriched[0]
        print(f"\n   Sample enriched article:")
        print(f"   - Title: {sample.title[:50]}...")
        print(f"   - Language: {sample.language}")
        print(f"   - Country: {sample.country}")
    
except Exception as e:
    print(f"❌ Enrichment error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Step 5: Save to database
print("\n5️⃣  Saving articles to database...")
try:
    saved = storage_service.save_articles(enriched)
    print(f"✅ Saved {len(saved)} articles")
    
    if saved:
        print(f"   First article ID: {saved[0].id}")
    
except Exception as e:
    print(f"❌ Storage error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Step 6: Retrieve from database
print("\n6️⃣  Retrieving articles from database...")
try:
    # Get all articles
    all_articles = storage_service.get_articles(limit=50)
    print(f"✅ Retrieved {len(all_articles)} articles")
    
    # Get with filters
    italian_articles = storage_service.get_articles(language='it', limit=10)
    print(f"   Italian articles: {len(italian_articles)}")
    
    # Search query
    tech_articles = storage_service.get_articles(search_query='tecnologia', limit=10)
    print(f"   Tech articles: {len(tech_articles)}")
    
except Exception as e:
    print(f"❌ Retrieval error: {e}")
    import traceback
    traceback.print_exc()

# Step 7: Get statistics
print("\n7️⃣  Getting database statistics...")
try:
    stats = storage_service.get_article_stats()
    print(f"✅ Statistics:")
    print(f"   Total articles: {stats['total_articles']}")
    print(f"   Last 24h: {stats['last_24h']}")
    print(f"   By source: {stats['by_source']}")
    print(f"   By language: {stats['by_language']}")
    print(f"   By country: {stats['by_country']}")
    
except Exception as e:
    print(f"❌ Stats error: {e}")

# Step 8: Count articles
print("\n8️⃣  Testing count queries...")
try:
    total = storage_service.count_articles()
    print(f"   Total count: {total}")
    
    ansa_count = storage_service.count_articles(source='ansa')
    print(f"   ANSA articles: {ansa_count}")
    
    yesterday = datetime.now() - timedelta(days=1)
    recent = storage_service.count_articles(start_date=yesterday)
    print(f"   Recent (24h): {recent}")
    
except Exception as e:
    print(f"❌ Count error: {e}")

print("\n" + "=" * 60)
print("✅ DATABASE & STORAGE TEST COMPLETED")
print("=" * 60)
