"""
Storage Service
Gestisce salvataggio e recupero articoli dal database
"""
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from models import Article, ArticleCreate
from models.database import SessionLocal


class StorageService:
    """Servizio per storage e query articoli"""
    
    def save_articles(
        self, 
        articles: List[ArticleCreate], 
        db: Optional[Session] = None
    ) -> List[Article]:
        """
        Salva lista di articoli nel DB
        Salta duplicati basati su (source, source_id)
        """
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            saved = []
            
            for article_data in articles:
                # Check se già esiste
                existing = db.query(Article).filter(
                    and_(
                        Article.source == article_data.source,
                        Article.source_id == article_data.source_id
                    )
                ).first()
                
                if existing:
                    print(f"⚠️  Duplicate skipped: {article_data.source}:{article_data.source_id}")
                    continue
                
                # Crea nuovo article
                article_dict = article_data.model_dump()
                
                # Entities va in raw_metadata se presente
                if 'entities' in article_dict:
                    if not article_dict.get('raw_metadata'):
                        article_dict['raw_metadata'] = {}
                    article_dict['raw_metadata']['entities'] = article_dict.pop('entities')
                
                article = Article(**article_dict)
                db.add(article)
                saved.append(article)
            
            db.commit()
            
            for article in saved:
                db.refresh(article)
            
            print(f"✅ Saved {len(saved)} articles to database")
            return saved
            
        except Exception as e:
            db.rollback()
            print(f"❌ Storage error: {e}")
            raise
        finally:
            if should_close:
                db.close()
    
    def get_articles(
        self,
        db: Optional[Session] = None,
        limit: int = 100,
        offset: int = 0,
        source: Optional[str] = None,
        language: Optional[str] = None,
        country: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        search_query: Optional[str] = None
    ) -> List[Article]:
        """
        Recupera articoli con filtri
        """
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            query = db.query(Article)
            
            # Filtri
            if source:
                query = query.filter(Article.source == source)
            
            if language:
                query = query.filter(Article.language == language)
            
            if country:
                query = query.filter(Article.country == country)
            
            if start_date:
                query = query.filter(Article.published_at >= start_date)
            
            if end_date:
                query = query.filter(Article.published_at <= end_date)
            
            if search_query:
                search_pattern = f"%{search_query}%"
                query = query.filter(
                    or_(
                        Article.title.ilike(search_pattern),
                        Article.content.ilike(search_pattern)
                    )
                )
            
            # Ordina per data decrescente
            query = query.order_by(desc(Article.published_at))
            
            # Paginazione
            articles = query.limit(limit).offset(offset).all()
            
            return articles
            
        finally:
            if should_close:
                db.close()
    
    def get_article_by_id(
        self, 
        article_id: int, 
        db: Optional[Session] = None
    ) -> Optional[Article]:
        """Recupera singolo articolo per ID"""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            return db.query(Article).filter(Article.id == article_id).first()
        finally:
            if should_close:
                db.close()
    
    def count_articles(
        self,
        db: Optional[Session] = None,
        source: Optional[str] = None,
        start_date: Optional[datetime] = None
    ) -> int:
        """Conta articoli con filtri"""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            query = db.query(func.count(Article.id))
            
            if source:
                query = query.filter(Article.source == source)
            
            if start_date:
                query = query.filter(Article.published_at >= start_date)
            
            return query.scalar()
            
        finally:
            if should_close:
                db.close()
    
    def get_article_stats(self, db: Optional[Session] = None) -> Dict:
        """Statistiche generali sugli articoli"""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            total = db.query(func.count(Article.id)).scalar()
            
            # Count per source
            by_source = db.query(
                Article.source,
                func.count(Article.id).label('count')
            ).group_by(Article.source).all()
            
            # Count per language
            by_language = db.query(
                Article.language,
                func.count(Article.id).label('count')
            ).group_by(Article.language).all()
            
            # Count per country
            by_country = db.query(
                Article.country,
                func.count(Article.id).label('count')
            ).group_by(Article.country).all()
            
            # Last 24h
            yesterday = datetime.now() - timedelta(days=1)
            last_24h = db.query(func.count(Article.id)).filter(
                Article.published_at >= yesterday
            ).scalar()
            
            return {
                'total_articles': total,
                'last_24h': last_24h,
                'by_source': {src: count for src, count in by_source},
                'by_language': {lang: count for lang, count in by_language if lang},
                'by_country': {country: count for country, count in by_country if country}
            }
            
        finally:
            if should_close:
                db.close()


# Singleton instance
storage_service = StorageService()
