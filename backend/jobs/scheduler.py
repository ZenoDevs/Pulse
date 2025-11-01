"""
APScheduler Setup - Automatic Jobs for Pulse
Handles periodic scraping, topic clustering, and maintenance
"""
import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from models.database import SessionLocal
from models.article import Article
from models.topic import Topic
from scrapers.registry import ScraperRegistry
from services.storage_service import StorageService
from services.topic_service import topic_service
from services.metrics_service import metrics_service
from models import ArticleCreate

# Global scheduler instance
scheduler = None

# Track last execution times for health monitoring
last_scraping_time = None
last_clustering_time = None
last_cleanup_time = None
scraping_stats = {
    'total_runs': 0,
    'last_articles_count': 0,
    'last_error': None
}


async def scrape_all_sources():
    """
    Scrape articles from all available sources
    Runs every 2 hours by default
    """
    global last_scraping_time, scraping_stats
    
    print("\n" + "="*70)
    print(f"🔄 SCHEDULED SCRAPING - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    try:
        registry = ScraperRegistry()
        storage = StorageService()
        total_articles = 0
        
        # Scrape from each source
        sources = ['ansa', 'reddit', 'hackernews']
        
        for source in sources:
            try:
                print(f"\n📰 Scraping {source.upper()}...")
                scraper = registry.get_scraper(source)
                
                if not scraper:
                    print(f"⚠️  Scraper {source} not available")
                    continue
                
                # Scrape articles (query can be configured)
                start_date = datetime.now() - timedelta(days=7)
                end_date = datetime.now()
                
                df = scraper.scrape(
                    query='technology',  # TODO: make configurable
                    max_pages=3,
                    start_date=start_date,
                    end_date=end_date
                )
                
                if df.empty:
                    print(f"  No articles from {source}")
                    continue
                
                # Convert to ArticleCreate objects
                articles = [ArticleCreate(**row.to_dict()) for _, row in df.iterrows()]
                
                # Save to database
                saved = storage.save_articles(articles)
                total_articles += len(saved)
                
                print(f"  ✅ {len(saved)} new articles from {source}")
                
            except Exception as e:
                print(f"  ❌ Error scraping {source}: {e}")
                scraping_stats['last_error'] = str(e)
        
        # Update tracking
        last_scraping_time = datetime.now()
        scraping_stats['total_runs'] += 1
        scraping_stats['last_articles_count'] = total_articles
        
        print(f"\n✅ Scraping complete: {total_articles} new articles")
        print("="*70 + "\n")
        
        # Trigger topic refresh if we got new articles
        if total_articles > 0:
            await refresh_topics_and_metrics()
        
    except Exception as e:
        print(f"\n❌ Scraping job failed: {e}")
        scraping_stats['last_error'] = str(e)


async def refresh_topics_and_metrics():
    """
    Recalculate topics and metrics
    Called automatically after scraping or can be triggered manually
    """
    global last_clustering_time
    
    print("\n" + "="*70)
    print(f"🧠 TOPIC REFRESH - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    try:
        db = SessionLocal()
        
        # Check if we have enough articles
        article_count = db.query(Article).count()
        print(f"📊 Total articles in DB: {article_count}")
        
        if article_count < 3:
            print("⚠️  Not enough articles for clustering (minimum 3)")
            db.close()
            return
        
        # Run clustering
        print("\n🔍 Running topic clustering...")
        topics = topic_service.cluster_and_save_topics(
            days_back=30,  # Consider articles from last 30 days
            min_cluster_size=2
        )
        
        print(f"✅ Created {len(topics)} topics")
        
        # Calculate metrics for all topics
        print("\n📈 Calculating Pulse metrics...")
        updated_count = metrics_service.update_all_topics_metrics(db)
        
        print(f"✅ Updated metrics for {updated_count} topics")
        
        # Display topics summary
        topics = db.query(Topic).order_by(Topic.pulse_score.desc()).limit(5).all()
        print(f"\n📌 Top {len(topics)} topics by PulseScore:")
        for topic in topics:
            print(f"  - {topic.label[:50]}... (score: {topic.pulse_score:.1f})")
        
        last_clustering_time = datetime.now()
        
        print("="*70 + "\n")
        
        db.close()
        
    except Exception as e:
        print(f"\n❌ Topic refresh failed: {e}")
        import traceback
        traceback.print_exc()


async def cleanup_old_data():
    """
    Clean up old articles and orphaned topics
    Runs daily at 3 AM
    """
    global last_cleanup_time
    
    print("\n" + "="*70)
    print(f"🧹 CLEANUP JOB - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    try:
        db = SessionLocal()
        
        # Delete articles older than 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        old_articles = db.query(Article).filter(
            Article.published_at < cutoff_date
        ).all()
        
        if old_articles:
            for article in old_articles:
                db.delete(article)
            db.commit()
            print(f"🗑️  Deleted {len(old_articles)} articles older than 30 days")
        else:
            print("✅ No old articles to delete")
        
        # Delete topics with no articles
        orphaned_topics = db.query(Topic).filter(
            ~Topic.topic_id.in_(
                db.query(Article.topic_id).filter(Article.topic_id.isnot(None))
            )
        ).all()
        
        if orphaned_topics:
            for topic in orphaned_topics:
                db.delete(topic)
            db.commit()
            print(f"🗑️  Deleted {len(orphaned_topics)} orphaned topics")
        else:
            print("✅ No orphaned topics to delete")
        
        last_cleanup_time = datetime.now()
        
        print("="*70 + "\n")
        
        db.close()
        
    except Exception as e:
        print(f"\n❌ Cleanup job failed: {e}")


def init_scheduler():
    """
    Initialize and start the APScheduler
    Called during FastAPI startup
    """
    global scheduler
    
    if scheduler is not None:
        print("⚠️  Scheduler already initialized")
        return scheduler
    
    scheduler = AsyncIOScheduler()
    
    # Job 1: Scrape all sources every 2 hours
    scheduler.add_job(
        scrape_all_sources,
        trigger=IntervalTrigger(hours=2),
        id='scrape_all_sources',
        name='Scrape all sources',
        replace_existing=True,
        max_instances=1  # Prevent overlapping runs
    )
    
    # Job 2: Manual topic refresh every 6 hours (backup if scraping found nothing)
    scheduler.add_job(
        refresh_topics_and_metrics,
        trigger=IntervalTrigger(hours=6),
        id='refresh_topics',
        name='Refresh topics and metrics',
        replace_existing=True,
        max_instances=1
    )
    
    # Job 3: Cleanup old data daily at 3 AM
    scheduler.add_job(
        cleanup_old_data,
        trigger=CronTrigger(hour=3, minute=0),
        id='cleanup_old_data',
        name='Cleanup old articles',
        replace_existing=True
    )
    
    scheduler.start()
    
    print("="*70)
    print("⏰ APScheduler initialized successfully!")
    print("="*70)
    print("📋 Scheduled jobs:")
    print("  1. Scrape all sources - every 2 hours")
    print("  2. Refresh topics - every 6 hours")
    print("  3. Cleanup old data - daily at 3 AM")
    print("="*70 + "\n")
    
    return scheduler


def shutdown_scheduler():
    """
    Gracefully shutdown the scheduler
    Called during FastAPI shutdown
    """
    global scheduler
    
    if scheduler and scheduler.running:
        scheduler.shutdown()
        print("⏰ Scheduler shutdown complete")


def get_scheduler_status():
    """
    Get current scheduler status and job info
    Used by health monitoring endpoint
    """
    if not scheduler:
        return {
            'status': 'not_initialized',
            'jobs': []
        }
    
    jobs_info = []
    for job in scheduler.get_jobs():
        jobs_info.append({
            'id': job.id,
            'name': job.name,
            'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
        })
    
    return {
        'status': 'running' if scheduler.running else 'stopped',
        'jobs': jobs_info,
        'last_scraping': last_scraping_time.isoformat() if last_scraping_time else None,
        'last_clustering': last_clustering_time.isoformat() if last_clustering_time else None,
        'last_cleanup': last_cleanup_time.isoformat() if last_cleanup_time else None,
        'scraping_stats': scraping_stats
    }
