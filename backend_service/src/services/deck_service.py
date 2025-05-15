"""
Service for deck operations.
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from db_module import crud, models, schemas
from ..logger_config import logger

def get_deck_by_id(db: Session, deck_id: str) -> Optional[models.Deck]:
    """
    Get a deck by ID.
    
    Args:
        db: Database session
        deck_id: Deck ID
        
    Returns:
        Deck object or None if not found
    """
    logger.debug(f"Getting deck with ID: {deck_id}")
    return db.query(models.Deck).filter(models.Deck.id == deck_id).first()

def get_decks_for_user(db: Session, user_id: str) -> List[models.Deck]:
    """
    Get all decks for a user.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        List of deck objects
    """
    logger.debug(f"Getting decks for user: {user_id}")
    return db.query(models.Deck).filter(models.Deck.owner_id == user_id).all()

def get_public_decks(db: Session) -> List[models.Deck]:
    """
    Get all public decks.
    
    Args:
        db: Database session
        
    Returns:
        List of public deck objects
    """
    logger.debug("Getting public decks")
    return db.query(models.Deck).filter(models.Deck.is_public == True).all()

def create_deck(db: Session, deck: schemas.DeckCreate, user_id: str) -> models.Deck:
    """
    Create a new deck.
    
    Args:
        db: Database session
        deck: Deck data
        user_id: User ID
        
    Returns:
        Created deck object
    """
    logger.debug(f"Creating deck: {deck.title} for user: {user_id}")
    return crud.create_deck(db, deck, user_id)

def update_deck(db: Session, deck_id: str, deck: schemas.DeckUpdate) -> Optional[models.Deck]:
    """
    Update a deck.
    
    Args:
        db: Database session
        deck_id: Deck ID
        deck: Updated deck data
        
    Returns:
        Updated deck object or None if not found
    """
    logger.debug(f"Updating deck: {deck_id}")
    return crud.update_deck(db, deck_id, deck)

def delete_deck(db: Session, deck_id: str) -> bool:
    """
    Delete a deck.
    
    Args:
        db: Database session
        deck_id: Deck ID
        
    Returns:
        True if deleted, False if not found
    """
    logger.debug(f"Deleting deck: {deck_id}")
    return crud.delete_deck(db, deck_id)
