"""
Configuration management per Pulse
Usa pydantic-settings per gestire env variables
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Configurazione applicazione"""
    
    # App settings
    APP_NAME: str = "Pulse"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str = "postgresql://pulse:pulse@localhost:5432/pulse_db"
    MONGO_URL: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "pulse_content"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # API Keys
    REDDIT_CLIENT_ID: Optional[str] = None
    REDDIT_CLIENT_SECRET: Optional[str] = None
    REDDIT_USER_AGENT: str = "PulseBot/1.0"
    
    GDELT_API_KEY: Optional[str] = None
    YOUTUBE_API_KEY: Optional[str] = None
    
    # Scraping settings
    SCRAPING_INTERVAL_MINUTES: int = 10
    MAX_PAGES_PER_SOURCE: int = 10
    REQUEST_TIMEOUT_SECONDS: int = 30
    
    # ML settings
    EMBEDDINGS_MODEL: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    MIN_TOPIC_SIZE: int = 5
    BERT_TOPIC_N_GRAM_RANGE: tuple = (1, 3)
    
    # Storage
    DATA_DIR: str = "./data"
    LOGS_DIR: str = "./logs"
    
    # API settings
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Singleton instance
settings = Settings()


def get_settings() -> Settings:
    """Dependency injection per FastAPI"""
    return settings
