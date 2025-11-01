"""
FastAPI main application
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from models.database import init_db

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Inizializzazione app"""
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    init_db()
    print("✅ Database initialized")
    
    # Initialize scheduler for automated jobs
    from jobs.scheduler import init_scheduler
    init_scheduler()
    print("✅ Scheduler initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Graceful shutdown"""
    from jobs.scheduler import shutdown_scheduler
    shutdown_scheduler()
    print("👋 Scheduler shutdown complete")


@app.get("/")
async def root():
    """Health check"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/api/v1/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }


# Import API routers
from api import articles, scraping, stats, topics, health

app.include_router(articles.router, prefix="/api/articles", tags=["articles"])
app.include_router(scraping.router, prefix="/api/scraping", tags=["scraping"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
app.include_router(topics.router, tags=["topics"])  # Already has /api/topics prefix
app.include_router(health.router, prefix="/api")  # /api/health
