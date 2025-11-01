"""
Health Monitoring API
Provides status information about scheduled jobs and system health
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.database import get_db
from models.article import Article
from models.topic import Topic
from jobs.scheduler import get_scheduler_status
from datetime import datetime, timedelta

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def get_health(db: Session = Depends(get_db)):
    """
    Get comprehensive health status of the Pulse system
    
    Returns:
    - Scheduler status and job info
    - Database statistics
    - Data freshness metrics
    """
    
    # Get scheduler status
    scheduler_status = get_scheduler_status()
    
    # Database statistics
    total_articles = db.query(Article).count()
    total_topics = db.query(Topic).count()
    
    # Articles by source
    articles_by_source = {}
    for source in ['ansa', 'reddit', 'hackernews']:
        count = db.query(Article).filter(Article.source == source).count()
        articles_by_source[source] = count
    
    # Recent articles (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(hours=24)
    recent_articles = db.query(Article).filter(
        Article.scraped_at >= yesterday
    ).count()
    
    # Latest article timestamp
    latest_article = db.query(Article).order_by(
        Article.published_at.desc()
    ).first()
    
    latest_article_time = None
    data_freshness = "unknown"
    
    if latest_article:
        latest_article_time = latest_article.published_at.isoformat()
        age_hours = (datetime.utcnow() - latest_article.published_at).total_seconds() / 3600
        
        if age_hours < 3:
            data_freshness = "fresh"
        elif age_hours < 24:
            data_freshness = "recent"
        elif age_hours < 72:
            data_freshness = "stale"
        else:
            data_freshness = "very_stale"
    
    # Topics info
    topics_info = {
        'total': total_topics,
        'with_metrics': db.query(Topic).filter(Topic.pulse_score.isnot(None)).count()
    }
    
    # System health summary
    health_status = "healthy"
    issues = []
    
    if total_articles == 0:
        health_status = "critical"
        issues.append("No articles in database")
    elif data_freshness in ["stale", "very_stale"]:
        health_status = "warning"
        issues.append(f"Data is {data_freshness} (latest article: {age_hours:.1f}h ago)")
    elif recent_articles == 0:
        health_status = "warning"
        issues.append("No articles scraped in last 24 hours")
    
    if scheduler_status['status'] != 'running':
        health_status = "critical"
        issues.append("Scheduler is not running")
    
    if scheduler_status.get('scraping_stats', {}).get('last_error'):
        if health_status == "healthy":
            health_status = "warning"
        issues.append(f"Last scraping error: {scheduler_status['scraping_stats']['last_error']}")
    
    return {
        'status': health_status,
        'timestamp': datetime.utcnow().isoformat(),
        'issues': issues,
        'scheduler': scheduler_status,
        'database': {
            'total_articles': total_articles,
            'articles_by_source': articles_by_source,
            'recent_articles_24h': recent_articles,
            'latest_article': latest_article_time,
            'data_freshness': data_freshness
        },
        'topics': topics_info
    }


@router.get("/simple")
async def get_simple_health():
    """
    Simple health check for uptime monitoring
    Returns 200 OK if the API is running
    """
    return {
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat()
    }


@router.post("/trigger-scraping")
async def trigger_scraping():
    """
    Manually trigger the scraping job
    Useful for testing or on-demand updates
    """
    from jobs.scheduler import scrape_all_sources
    import asyncio
    
    # Run scraping in background
    asyncio.create_task(scrape_all_sources())
    
    return {
        'status': 'triggered',
        'message': 'Scraping job started',
        'timestamp': datetime.utcnow().isoformat()
    }
