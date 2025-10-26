"""
Articles API Endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from models.database import get_db
from models import ArticleSchema
from services.storage_service import storage_service

router = APIRouter()


@router.get("/", response_model=List[ArticleSchema])
async def get_articles(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    source: Optional[str] = None,
    language: Optional[str] = None,
    country: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get articles with filters and pagination
    """
    articles = storage_service.get_articles(
        db=db,
        limit=limit,
        offset=offset,
        source=source,
        language=language,
        country=country,
        search_query=search
    )
    return articles


@router.get("/{article_id}", response_model=ArticleSchema)
async def get_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    """
    Get single article by ID
    """
    article = storage_service.get_article_by_id(article_id, db)
    if not article:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.get("/count/total")
async def count_articles(
    source: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Count articles with optional source filter
    """
    count = storage_service.count_articles(db=db, source=source)
    return {"count": count}
