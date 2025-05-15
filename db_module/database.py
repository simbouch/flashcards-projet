"""
Database connection and session management for the flashcards application.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from loguru import logger
from pathlib import Path
import sys

# Configure logger
# Use a shared logs directory that both services can access
# Determine the log directory based on environment
# In Docker, logs should go to /app/logs
# In development, logs should go to ./logs
log_dir = Path("/app/logs" if os.path.exists("/app/logs") else "./logs")
log_dir.mkdir(exist_ok=True, parents=True)

logger.remove()
logger.add(
    sys.stdout,
    level="DEBUG",
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# Add file logging with proper error handling
try:
    log_file = str(log_dir / "db_{time:YYYY-MM-DD}.log")
    logger.add(
        log_file,
        level="DEBUG",
        rotation="00:00",
        retention="7 days",
        backtrace=True,
        diagnose=True,
        enqueue=True
    )
    logger.info(f"DB module logging to file: {log_file}")
except Exception as e:
    logger.warning(f"Could not set up file logging for DB module: {str(e)}")
    logger.info("Continuing with stdout logging only")

# Get database URL from environment or use default SQLite file
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", "sqlite:///./flashcards.db"
)

# Create engine with proper settings for SQLite
connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true"
)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """
    Dependency for FastAPI endpoints that need a database session.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        logger.debug("Database session created")
        yield db
    finally:
        db.close()
        logger.debug("Database session closed")

def init_db():
    """
    Initialize the database by creating all tables.
    Should be called when the application starts.
    """
    logger.info(f"Initializing database at {SQLALCHEMY_DATABASE_URL}")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")
