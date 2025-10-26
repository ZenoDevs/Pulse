"""
Scraping API Endpoints
"""
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

from scrapers import scraper_registry
from services.parser_service import parser_service
from services.language_service import language_service
from services.storage_service import storage_service

router = APIRouter()


class ScrapeRequest(BaseModel):
    query: str
    sources: Optional[List[str]] = None
    max_pages: int = 3
    days_back: int = 7


class ScrapeResponse(BaseModel):
    task_id: str
    status: str
    message: str


@router.post("/scrape")
async def scrape_articles(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """
    Trigger scraping job
    Scrapes articles from specified sources, parses, enriches, and saves to DB
    """
    import uuid
    task_id = str(uuid.uuid4())
    
    # Run scraping in background
    background_tasks.add_task(
        run_scraping_pipeline,
        query=request.query,
        sources=request.sources,
        max_pages=request.max_pages,
        days_back=request.days_back
    )
    
    return ScrapeResponse(
        task_id=task_id,
        status="started",
        message=f"Scraping job started for query: {request.query}"
    )


@router.post("/scrape-now")
async def scrape_now(request: ScrapeRequest):
    """
    Synchronous scraping (blocks until complete)
    Use for immediate results, not recommended for large queries
    """
    result = await run_scraping_pipeline(
        query=request.query,
        sources=request.sources,
        max_pages=request.max_pages,
        days_back=request.days_back
    )
    
    return result


async def run_scraping_pipeline(
    query: str,
    sources: Optional[List[str]] = None,
    max_pages: int = 3,
    days_back: int = 7
):
    """
    Complete scraping pipeline:
    1. Scrape from sources
    2. Parse and normalize
    3. Detect language & country
    4. Save to database
    """
    try:
        # Step 1: Scrape
        start_date = datetime.now() - timedelta(days=days_back)
        end_date = datetime.now()
        
        df = scraper_registry.scrape_all(
            query=query,
            sources=sources,
            max_pages=max_pages,
            start_date=start_date,
            end_date=end_date
        )
        
        if df.empty:
            return {
                "status": "success",
                "articles_scraped": 0,
                "articles_saved": 0,
                "message": "No articles found"
            }
        
        # Step 2: Parse
        articles = parser_service.parse_dataframe(df)
        
        # Step 3: Enrich
        enriched = []
        for article in articles:
            article_dict = article.model_dump()
            enriched_dict = language_service.enrich_article(article_dict)
            
            from models import ArticleCreate
            enriched_article = ArticleCreate(**enriched_dict)
            enriched.append(enriched_article)
        
        # Step 4: Save
        saved = storage_service.save_articles(enriched)
        
        return {
            "status": "success",
            "articles_scraped": len(df),
            "articles_parsed": len(articles),
            "articles_saved": len(saved),
            "message": f"Successfully processed {len(saved)} articles"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@router.get("/sources")
async def get_available_sources():
    """
    List available scraping sources
    """
    sources = list(scraper_registry.scrapers.keys())
    return {
        "sources": sources,
        "count": len(sources)
    }
