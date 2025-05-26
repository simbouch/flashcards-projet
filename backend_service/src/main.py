"""
Main FastAPI application for the backend service.
"""
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import os
from pathlib import Path
from contextlib import asynccontextmanager

from .config import settings
from .logger_config import logger
from .api import api_router
from db_module.database import init_db
from .scripts.create_native_decks import create_native_decks
from .middleware import limiter, rate_limit_handler, check_redis_health

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for the FastAPI application."""
    # Startup events
    logger.info("Starting backend service")

    # Initialize database
    init_db()

    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Create native decks (deleting existing ones)
    try:
        logger.info("Creating native decks...")
        create_native_decks(delete_existing=True)
        logger.info("Native decks created successfully")
    except Exception as e:
        logger.error(f"Error creating native decks: {str(e)}")

    # Check Redis connection for rate limiting
    if check_redis_health():
        logger.info("Redis connection established for rate limiting")
    else:
        logger.warning("Redis connection failed - rate limiting may not work properly")

    logger.info("Backend service started successfully")

    yield

    # Shutdown events
    logger.info("Shutting down backend service")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Add rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"status": "ok", "service": "backend"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    redis_healthy = check_redis_health()
    return {
        "status": "ok",
        "message": "Backend service is healthy",
        "version": "0.1.0",
        "redis_status": "healthy" if redis_healthy else "unhealthy",
        "rate_limiting": "enabled" if redis_healthy else "disabled"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.exception(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
