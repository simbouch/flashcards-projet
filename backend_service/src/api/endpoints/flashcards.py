"""
Flashcard management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, List
from sqlalchemy.orm import Session

from db_module import crud, models, schemas
from db_module.database import get_db
from ...auth.jwt import get_current_active_user
from ...logger_config import logger

router = APIRouter()

@router.post("/", response_model=schemas.Flashcard)
async def create_flashcard(
    flashcard_in: schemas.FlashcardCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create a new flashcard.
    """
    # Check if deck exists and user is the owner
    deck = crud.get_deck(db, flashcard_in.deck_id)
    if not deck:
        logger.warning(f"Deck not found: {flashcard_in.deck_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )

    if deck.owner_id != current_user.id:
        logger.warning(f"User {current_user.username} attempted to create flashcard for deck {flashcard_in.deck_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Create flashcard
    flashcard = crud.create_flashcard(db, flashcard_in)
    logger.info(f"Flashcard created: {flashcard.id}")
    return flashcard


@router.get("/", response_model=List[schemas.Flashcard])
async def read_flashcards(
    deck_id: str,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Retrieve flashcards for a deck.
    """
    # Check if deck exists
    deck = crud.get_deck(db, deck_id)
    if not deck:
        logger.warning(f"Deck not found: {deck_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )

    # Check if user is the owner or the deck is public
    if deck.owner_id != current_user.id and not deck.is_public:
        # Check if deck is shared with user
        if current_user not in deck.shared_with:
            logger.warning(f"User {current_user.username} attempted to access flashcards for deck {deck_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

    # Get flashcards
    flashcards = crud.get_flashcards_by_deck(db, deck_id, skip=skip, limit=limit)
    return flashcards

@router.get("/{flashcard_id}", response_model=schemas.Flashcard)
async def read_flashcard(
    flashcard_id: str,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get flashcard by ID.
    """
    flashcard = crud.get_flashcard(db, flashcard_id)
    if not flashcard:
        logger.warning(f"Flashcard not found: {flashcard_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found"
        )

    # Check if user is the owner of the deck or the deck is public
    deck = crud.get_deck(db, flashcard.deck_id)
    if deck.owner_id != current_user.id and not deck.is_public:
        # Check if deck is shared with user
        if current_user not in deck.shared_with:
            logger.warning(f"User {current_user.username} attempted to access flashcard {flashcard_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

    return flashcard

@router.put("/{flashcard_id}", response_model=schemas.Flashcard)
async def update_flashcard(
    flashcard_id: str,
    flashcard_in: schemas.FlashcardUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update a flashcard.
    """
    flashcard = crud.get_flashcard(db, flashcard_id)
    if not flashcard:
        logger.warning(f"Flashcard not found: {flashcard_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found"
        )

    # Check if user is the owner of the deck
    deck = crud.get_deck(db, flashcard.deck_id)
    if deck.owner_id != current_user.id:
        logger.warning(f"User {current_user.username} attempted to update flashcard {flashcard_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Update flashcard
    flashcard = crud.update_flashcard(db, flashcard_id, flashcard_in)
    logger.info(f"Flashcard updated: {flashcard.id}")
    return flashcard

@router.delete("/{flashcard_id}", response_model=schemas.Flashcard)
async def delete_flashcard(
    flashcard_id: str,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete a flashcard.
    """
    flashcard = crud.get_flashcard(db, flashcard_id)
    if not flashcard:
        logger.warning(f"Flashcard not found: {flashcard_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found"
        )

    # Check if user is the owner of the deck
    deck = crud.get_deck(db, flashcard.deck_id)
    if deck.owner_id != current_user.id:
        logger.warning(f"User {current_user.username} attempted to delete flashcard {flashcard_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Delete flashcard
    crud.delete_flashcard(db, flashcard_id)
    logger.info(f"Flashcard deleted: {flashcard.id}")
    return flashcard
