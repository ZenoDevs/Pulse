"""
Modelli per i Topic e le metriche Pulse
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

# Import Base from database to use same declarative base
from models.database import Base


class Topic(Base):
    """Topic individuato da BERTopic"""
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(String(50), unique=True, index=True)  # e.g., "topic_0", "topic_1"
    
    label = Column(String(255))
    keywords = Column(JSON)  # Lista di keyword principali
    description = Column(Text)
    
    # Metriche Pulse
    pulse_score = Column(Float, index=True, default=0.0)
    volume = Column(Integer, default=0)        # Numero articoli
    velocity = Column(Float, default=0.0)      # Crescita % nelle ultime 24h
    spread = Column(Integer, default=0)        # Numero fonti diverse
    authority = Column(Float, default=0.0)     # Media authority_score degli articoli
    novelty = Column(Float, default=0.0)       # Quanto è "nuovo" il topic
    variance = Column(Float, default=0.0)      # Varianza sentimenti
    
    sentiment_avg = Column(Float, default=0.0)
    
    # Metadata
    country = Column(String(10), index=True)
    sector = Column(String(50), index=True)
    
    # Tracking temporale
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Storico metriche per forecasting
    history = Column(JSON)  # [{timestamp, pulse_score, volume, ...}, ...]


class TopicSchema(BaseModel):
    """Schema per API"""
    id: int
    topic_id: str  # Changed to string
    label: str
    keywords: List[str]
    description: Optional[str] = None
    
    pulse_score: float
    volume: int
    velocity: float
    spread: int
    authority: float = 0.0
    novelty: float = 0.0
    sentiment_avg: Optional[float] = None
    
    country: Optional[str] = None
    sector: Optional[str] = None
    
    first_seen: datetime
    last_updated: datetime
    
    class Config:
        from_attributes = True


class TopicWithSources(TopicSchema):
    """Topic con lista fonti e count articoli"""
    sources: List[str] = []
    article_count: int = 0
    sample_articles: List[dict] = []
