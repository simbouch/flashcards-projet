"""
Logger configuration for the LLM service.
"""
import sys
from loguru import logger
from pathlib import Path

# Ensure the log directory exists relative to this module
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Remove default sink
logger.remove()

# Development sink: colored console output
logger.add(
    sys.stdout,
    level="DEBUG",
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
           "<level>{message}</level>",
    backtrace=True,
    diagnose=True
)

# File sink for local dev: writes into llm_service/logs
logger.add(
    str(LOG_DIR / "llm_{time:YYYY-MM-DD}.log"),
    level="DEBUG",
    rotation="00:00",     # rotate at midnight
    retention="7 days",   # keep logs for 7 days
    backtrace=True,
    diagnose=True,
    enqueue=True
)
