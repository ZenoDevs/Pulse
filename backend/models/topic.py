"""
Modelli per i Topic e le metriche Pulse
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

Base = declarative_base()


class Topic(Base):
    """Topic individuato da BERTopic"""
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, unique=True, index=True)  # ID BERTopic
    
    label = Column(String(255))
    keywords = Column(JSON)  # Lista di keyword principali
    description = Column(Text)
    
    # Metriche Pulse
    pulse_score = Column(Float, index=True)
    volume = Column(Integer)        # Numero articoli
    velocity = Column(Float)        # Crescita % nelle ultime 24h
    spread = Column(Integer)        # Numero fonti diverse
    authority = Column(Float)       # Media authority_score degli articoli
    novelty = Column(Float)         # Quanto è "nuovo" il topic
    variance = Column(Float)        # Varianza sentimenti
    
    sentiment_avg = Column(Float)
    
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
    topic_id: int
    label: str
    keywords: List[str]
    description: Optional[str] = None
    
    pulse_score: float
    volume: int
    velocity: float
    spread: int
    sentiment_avg: Optional[float] = None
    
    country: Optional[str] = None
    sector: Optional[str] = None
    
    first_seen: datetime
    last_updated: datetime
    
    class Config:
        from_attributes = True


class TopicWithSources(TopicSchema):
    """Topic con lista fonti"""
    sources: List[str] = []
    sample_articles: List[dict] = []
