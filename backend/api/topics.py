"""
Topics API Endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from models.database import get_db
from models.topic import Topic, TopicSchema, TopicWithSources
from models.article import Article
from services.metrics_service import metrics_service

router = APIRouter(prefix="/api/topics", tags=["topics"])


@router.get("", response_model=List[TopicWithSources])
def get_topics(
    limit: int = Query(default=20, ge=1, le=100),
    sort_by: str = Query(default="pulse_score", regex="^(pulse_score|volume|velocity|novelty|last_updated)$"),
    country: Optional[str] = None,
    sector: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of topics with metrics
    
    Query params:
    - limit: max topics to return (default 20)
    - sort_by: sorting field (pulse_score, volume, velocity, novelty, last_updated)
    - country: filter by country (ITA, USA, GLOBAL, etc)
    - sector: filter by sector (Tech, Politics, etc)
    
    Returns:
        List of topics with article counts and sources
    """
    query = db.query(Topic)
    
    # Filtri opzionali
    if country:
        query = query.filter(Topic.country == country.upper())
    if sector:
        query = query.filter(Topic.sector == sector)
    
    # Sorting
    if sort_by == "pulse_score":
        query = query.order_by(Topic.pulse_score.desc())
    elif sort_by == "volume":
        query = query.order_by(Topic.volume.desc())
    elif sort_by == "velocity":
        query = query.order_by(Topic.velocity.desc())
    elif sort_by == "novelty":
        query = query.order_by(Topic.novelty.desc())
    elif sort_by == "last_updated":
        query = query.order_by(Topic.last_updated.desc())
    
    topics = query.limit(limit).all()
    
    # Arricchisci con counts e sources
    results = []
    for topic in topics:
        articles = db.query(Article).filter(Article.topic_id == topic.topic_id).all()
        
        sources = list(set(art.source for art in articles if art.source))
        
        topic_dict = {
            **topic.__dict__,
            'article_count': len(articles),
            'sources': sources
        }
        
        results.append(TopicWithSources(**topic_dict))
    
    return results


@router.get("/{topic_id}", response_model=TopicWithSources)
def get_topic(
    topic_id: str,
    db: Session = Depends(get_db)
):
    """
    Get single topic by ID with all details
    
    Args:
        topic_id: Topic ID (es. "topic_0")
    
    Returns:
        Topic with metrics, articles, and sources
    """
    topic = db.query(Topic).filter(Topic.topic_id == topic_id).first()
    
    if not topic:
        raise HTTPException(status_code=404, detail=f"Topic {topic_id} not found")
    
    # Query articoli
    articles = db.query(Article).filter(Article.topic_id == topic_id).all()
    sources = list(set(art.source for art in articles if art.source))
    
    topic_dict = {
        **topic.__dict__,
        'article_count': len(articles),
        'sources': sources
    }
    
    return TopicWithSources(**topic_dict)


@router.get("/{topic_id}/articles")
def get_topic_articles(
    topic_id: str,
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Get all articles belonging to a topic
    
    Args:
        topic_id: Topic ID
        limit: max articles to return
    
    Returns:
        List of articles
    """
    # Verifica topic exists
    topic = db.query(Topic).filter(Topic.topic_id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail=f"Topic {topic_id} not found")
    
    articles = db.query(Article).filter(
        Article.topic_id == topic_id
    ).order_by(
        Article.published_at.desc()
    ).limit(limit).all()
    
    return articles


@router.post("/{topic_id}/refresh")
def refresh_topic_metrics(
    topic_id: str,
    db: Session = Depends(get_db)
):
    """
    Manually refresh metrics for a specific topic
    
    Args:
        topic_id: Topic ID
    
    Returns:
        Updated metrics
    """
    topic = db.query(Topic).filter(Topic.topic_id == topic_id).first()
    
    if not topic:
        raise HTTPException(status_code=404, detail=f"Topic {topic_id} not found")
    
    # Query articoli
    articles = db.query(Article).filter(Article.topic_id == topic_id).all()
    
    if not articles:
        raise HTTPException(status_code=400, detail="No articles found for topic")
    
    # Ricalcola metrics
    metrics = metrics_service.calculate_all_metrics(topic, articles, db)
    
    return {
        "topic_id": topic_id,
        "metrics": metrics,
        "article_count": len(articles)
    }


@router.post("/refresh-all")
def refresh_all_metrics(db: Session = Depends(get_db)):
    """
    Refresh metrics for all topics
    
    Should be called periodically (e.g., via cron job)
    
    Returns:
        Number of topics updated
    """
    updated_count = metrics_service.update_all_topics_metrics(db)
    
    return {
        "status": "success",
        "topics_updated": updated_count
    }
