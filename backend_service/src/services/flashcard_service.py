"""
Service for flashcard operations.
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from db_module import crud, models, schemas
from ..logger_config import logger

def get_flashcard_by_id(db: Session, flashcard_id: str) -> Optional[models.Flashcard]:
    """
    Get a flashcard by ID.
    
    Args:
        db: Database session
        flashcard_id: Flashcard ID
        
    Returns:
        Flashcard object or None if not found
    """
    logger.debug(f"Getting flashcard with ID: {flashcard_id}")
    return db.query(models.Flashcard).filter(models.Flashcard.id == flashcard_id).first()

def get_flashcards_by_deck(db: Session, deck_id: str) -> List[models.Flashcard]:
    """
    Get all flashcards for a deck.
    
    Args:
        db: Database session
        deck_id: Deck ID
        
    Returns:
        List of flashcard objects
    """
    logger.debug(f"Getting flashcards for deck: {deck_id}")
    return db.query(models.Flashcard).filter(models.Flashcard.deck_id == deck_id).all()

def create_flashcard(db: Session, flashcard: schemas.FlashcardCreate) -> models.Flashcard:
    """
    Create a new flashcard.
    
    Args:
        db: Database session
        flashcard: Flashcard data
        
    Returns:
        Created flashcard object
    """
    logger.debug(f"Creating flashcard for deck: {flashcard.deck_id}")
    return crud.create_flashcard(db, flashcard)

def update_flashcard(db: Session, flashcard_id: str, flashcard: schemas.FlashcardUpdate) -> Optional[models.Flashcard]:
    """
    Update a flashcard.
    
    Args:
        db: Database session
        flashcard_id: Flashcard ID
        flashcard: Updated flashcard data
        
    Returns:
        Updated flashcard object or None if not found
    """
    logger.debug(f"Updating flashcard: {flashcard_id}")
    return crud.update_flashcard(db, flashcard_id, flashcard)

def delete_flashcard(db: Session, flashcard_id: str) -> bool:
    """
    Delete a flashcard.
    
    Args:
        db: Database session
        flashcard_id: Flashcard ID
        
    Returns:
        True if deleted, False if not found
    """
    logger.debug(f"Deleting flashcard: {flashcard_id}")
    return crud.delete_flashcard(db, flashcard_id)
