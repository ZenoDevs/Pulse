"""
Test Topic Clustering with real articles
"""
import sys
sys.path.insert(0, '/Users/Edoardo.dng/Desktop/Pulse/Pulse/backend')

from services.topic_service import topic_service
from services.storage_service import storage_service
from models.database import init_db, SessionLocal

print("=" * 70)
print("TESTING TOPIC CLUSTERING (PHASE 2 POC)")
print("=" * 70)

# 1. Initialize database (create topics table if not exists)
print("\n1️⃣  Initializing database...")
try:
    init_db()
    print("✅ Database initialized")
except Exception as e:
    print(f"⚠️  Database already initialized or error: {e}")

# 2. Check how many articles we have
print("\n2️⃣  Checking available articles...")
articles = storage_service.get_articles(limit=100)
print(f"✅ Found {len(articles)} articles in database")

if len(articles) < 3:
    print("\n❌ Not enough articles for clustering (minimum 3 required)")
    print("   Run scraping first to get more articles")
    sys.exit(1)

# Show article breakdown
from collections import Counter
sources = Counter(art.source for art in articles)
languages = Counter(art.language for art in articles)
countries = Counter(art.country for art in articles)

print(f"\n📊 Article breakdown:")
print(f"   Sources: {dict(sources)}")
print(f"   Languages: {dict(languages)}")
print(f"   Countries: {dict(countries)}")

# 3. Test clustering
print("\n3️⃣  Testing BERTopic clustering...")
print("   (This will download the embedding model on first run - ~500MB)")
print("   (May take 1-2 minutes...)\n")

try:
    # Cluster and save topics
    topics = topic_service.cluster_and_save_topics(
        days_back=30,  # Use all articles
        min_cluster_size=2  # Allow small clusters for testing
    )
    
    print(f"\n✅ Successfully created {len(topics)} topics!")
    
    # Refresh articles from DB to see topic_id
    articles = storage_service.get_articles(limit=100)
    
    # Refresh topics from DB to avoid detached session errors
    from models.topic import Topic
    db_session = SessionLocal()
    topics_refreshed = db_session.query(Topic).all()
    
    # Display topics
    print("\n4️⃣  Topic Summary:")
    print("=" * 70)
    
    for topic in topics_refreshed:
        print(f"\n📌 {topic.topic_id}: {topic.label}")
        print(f"   Keywords: {', '.join(topic.keywords[:5])}")
        print(f"   Country: {topic.country} | Sector: {topic.sector}")
        print(f"   First seen: {topic.first_seen}")
        
        # Count articles in this topic
        topic_articles = [art for art in articles if art.topic_id == topic.topic_id]
        print(f"   Articles: {len(topic_articles)}")
        
        # Show sources
        topic_sources = list(set(art.source for art in topic_articles))
        print(f"   Sources: {', '.join(topic_sources)}")
    
    db_session.close()
    
    print("\n" + "=" * 70)
    print(f"✅ POC SUCCESS! {len(topics)} topics created from {len(articles)} articles")
    print("=" * 70)
    
    # Next steps
    print("\n📋 Next Steps:")
    print("   1. ✅ Topic clustering works!")
    print("   2. ⏭️  Create metrics_service.py to calculate Pulse metrics")
    print("   3. ⏭️  Create /api/topics endpoints")
    print("   4. ⏭️  Update frontend to display real topics")
    
except Exception as e:
    print(f"\n❌ Clustering failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
