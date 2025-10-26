"""
Database connection e sessione management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import Generator
from config import settings
import os

# Supporto SQLite per dev locale e PostgreSQL per prod
database_url = settings.DATABASE_URL

# Se DATABASE_URL non è configurato, usa SQLite
if not database_url or database_url == "postgresql://user:password@localhost:5432/pulse":
    # SQLite per testing locale
    db_path = os.path.join(os.path.dirname(__file__), '..', 'pulse.db')
    database_url = f"sqlite:///{db_path}"
    print(f"⚠️  Using SQLite: {db_path}")

# Engine con config dinamica
if database_url.startswith("sqlite"):
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency per FastAPI - fornisce sessione DB"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Inizializza il database creando tutte le tabelle"""
    from models.article import Article, Base
    from models.topic import Topic
    Base.metadata.create_all(bind=engine)
    print(f"✅ Created tables: {Base.metadata.tables.keys()}")
