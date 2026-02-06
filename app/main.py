"""
PronaFlow Backend Application - Main Entry Point
FastAPI application with database, authentication, and API routing.
"""
import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.scheduled_jobs import run_workspace_purge_job
from app.api.v1.router import api_router
from app.db.session import engine
from app.db.base import Base
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.middleware.logging import LoggingMiddleware

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="PronaFlow Project Management Platform - Backend API",
    debug=settings.DEBUG
)

# Add middleware (order matters - last added is executed first)
# 1. Error handler (outermost - catches all errors)
app.add_middleware(ErrorHandlerMiddleware)

# 2. Logging middleware
app.add_middleware(LoggingMiddleware)

# 3. CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_router)


workspace_purge_stop_event: asyncio.Event | None = None
workspace_purge_task: asyncio.Task | None = None


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to PronaFlow Backend API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


# Database initialization on startup (development only)
@app.on_event("startup")
async def startup_event():
    """
    Startup event handler.
    Create database tables if they don't exist (development only).
    In production, use Alembic migrations.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {'development' if settings.DEBUG else 'production'}")
    logger.info(f"Database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'configured'}")
    
    if settings.DEBUG:
        # Create all tables in development mode
        logger.warning("DEBUG mode: Auto-creating database tables")
        Base.metadata.create_all(bind=engine)
    else:
        logger.info("Production mode: Ensure migrations are run with 'alembic upgrade head'")

    if settings.ENABLE_WORKSPACE_PURGE_JOB:
        global workspace_purge_stop_event, workspace_purge_task
        workspace_purge_stop_event = asyncio.Event()
        workspace_purge_task = asyncio.create_task(
            run_workspace_purge_job(workspace_purge_stop_event)
        )


@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler to stop background jobs.
    """
    if workspace_purge_stop_event:
        workspace_purge_stop_event.set()
    if workspace_purge_task:
        await workspace_purge_task


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
