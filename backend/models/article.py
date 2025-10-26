"""
Modelli dati per gli articoli/contenuti
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

Base = declarative_base()


class Article(Base):
    """Modello SQLAlchemy per articoli nel DB relazionale"""
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False, index=True)  # ansa, reddit, youtube, etc
    source_id = Column(String(255), unique=True, index=True)  # ID univoco dalla fonte
    
    title = Column(Text, nullable=False)
    content = Column(Text)
    url = Column(Text)
    
    published_at = Column(DateTime, index=True)
    scraped_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Metadata
    country = Column(String(10), index=True)  # IT, GB, DE, etc
    language = Column(String(10), index=True)  # it, en, de
    sector = Column(String(50), index=True)   # News, Tech, Sport, etc
    
    # Metrics
    engagement_score = Column(Float, default=0.0)  # like, upvotes, views
    authority_score = Column(Float, default=0.0)   # autorevolezza fonte
    
    # ML fields
    embedding_vector = Column(JSON)  # Salviamo come JSON per PostgreSQL
    topic_id = Column(Integer, index=True)  # ID del topic BERTopic
    sentiment_score = Column(Float)
    
    # Extra metadata
    raw_metadata = Column(JSON)  # Dati specifici della fonte
    
    # Indexes
    __table_args__ = (
        Index('idx_published_country', 'published_at', 'country'),
        Index('idx_topic_published', 'topic_id', 'published_at'),
    )


class ArticleSchema(BaseModel):
    """Schema Pydantic per validazione API"""
    id: Optional[int] = None
    source: str
    source_id: str
    title: str
    content: Optional[str] = None
    url: Optional[str] = None
    published_at: Optional[datetime] = None
    country: Optional[str] = None
    language: Optional[str] = None
    sector: Optional[str] = None
    engagement_score: float = 0.0
    sentiment_score: Optional[float] = None
    
    class Config:
        from_attributes = True


class ArticleCreate(BaseModel):
    """Schema per creazione articolo"""
    source: str
    source_id: str
    title: str
    content: Optional[str] = None
    url: Optional[str] = None
    published_at: Optional[datetime] = None
    raw_metadata: Optional[dict] = None
