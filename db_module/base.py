"""
Base module for SQLAlchemy models.
This module ensures all models are registered with SQLAlchemy's metadata.
"""
from db_module.database import Base

# Import all models to ensure they're registered with Base.metadata
from db_module.models import (
    User,
    Document,
    ExtractedText,
    Deck,
    Flashcard,
    RefreshToken,
    StudySession,
    StudyRecord
)

# This ensures that all models are registered with Base.metadata
__all__ = [
    "Base",
    "User",
    "Document",
    "ExtractedText",
    "Deck",
    "Flashcard",
    "RefreshToken",
    "StudySession",
    "StudyRecord"
]
