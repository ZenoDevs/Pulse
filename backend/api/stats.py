"""
Statistics API Endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.database import get_db
from services.storage_service import storage_service

router = APIRouter()


@router.get("/overview")
async def get_stats_overview(db: Session = Depends(get_db)):
    """
    Get general statistics overview
    """
    stats = storage_service.get_article_stats(db)
    return stats


@router.get("/sources")
async def get_source_stats(db: Session = Depends(get_db)):
    """
    Get statistics by source
    """
    stats = storage_service.get_article_stats(db)
    return {
        "by_source": stats.get('by_source', {}),
        "total": stats.get('total_articles', 0)
    }


@router.get("/languages")
async def get_language_stats(db: Session = Depends(get_db)):
    """
    Get statistics by language
    """
    stats = storage_service.get_article_stats(db)
    return {
        "by_language": stats.get('by_language', {}),
        "total": stats.get('total_articles', 0)
    }


@router.get("/countries")
async def get_country_stats(db: Session = Depends(get_db)):
    """
    Get statistics by country
    """
    stats = storage_service.get_article_stats(db)
    return {
        "by_country": stats.get('by_country', {}),
        "total": stats.get('total_articles', 0)
    }
