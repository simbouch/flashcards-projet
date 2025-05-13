"""
Deck management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, List
from sqlalchemy.orm import Session

from db_module import crud, models, schemas
from db_module.database import get_db
from ...auth.jwt import get_current_active_user
from ...logger_config import logger

router = APIRouter()

@router.post("/", response_model=schemas.Deck)
async def create_deck(
    deck_in: schemas.DeckCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create a new deck.
    """
    # Check if document exists and user is the owner
    if deck_in.document_id:
        document = crud.get_document(db, deck_in.document_id)
        if not document:
            logger.warning(f"Document not found: {deck_in.document_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        if document.owner_id != current_user.id:
            logger.warning(f"User {current_user.username} attempted to create deck for document {deck_in.document_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

    # Create deck
    deck = crud.create_deck(db, deck_in, current_user.id)
    logger.info(f"Deck created: {deck.id}")
    return deck

@router.get("/", response_model=List[schemas.Deck])
async def read_decks(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Retrieve decks.
    """
    decks = crud.get_decks_by_owner(
        db, current_user.id, skip=skip, limit=limit
    )
    return decks

@router.get("/public", response_model=List[schemas.Deck])
async def read_public_decks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> Any:
    """
    Retrieve public decks.
    """
    decks = crud.get_public_decks(db, skip=skip, limit=limit)
    return decks



@router.get("/{deck_id}", response_model=schemas.DeckWithFlashcards)
async def read_deck(
    deck_id: str,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get deck by ID.
    """
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
            logger.warning(f"User {current_user.username} attempted to access deck {deck_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

    # Get flashcards for the deck
    flashcards = crud.get_flashcards_by_deck(db, deck_id)

    # Create response
    response = schemas.DeckWithFlashcards(
        **deck.__dict__,
        flashcards=flashcards
    )

    return response

@router.put("/{deck_id}", response_model=schemas.Deck)
async def update_deck(
    deck_id: str,
    deck_in: schemas.DeckUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update a deck.
    """
    deck = crud.get_deck(db, deck_id)
    if not deck:
        logger.warning(f"Deck not found: {deck_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )

    # Check if user is the owner
    if deck.owner_id != current_user.id:
        logger.warning(f"User {current_user.username} attempted to update deck {deck_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Update deck
    deck = crud.update_deck(db, deck_id, deck_in)
    logger.info(f"Deck updated: {deck.id}")
    return deck

@router.delete("/{deck_id}", response_model=schemas.Deck)
async def delete_deck(
    deck_id: str,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete a deck.
    """
    deck = crud.get_deck(db, deck_id)
    if not deck:
        logger.warning(f"Deck not found: {deck_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )

    # Check if user is the owner
    if deck.owner_id != current_user.id:
        logger.warning(f"User {current_user.username} attempted to delete deck {deck_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Delete deck
    crud.delete_deck(db, deck_id)
    logger.info(f"Deck deleted: {deck_id}")
    return deck

@router.post("/{deck_id}/share/{user_id}", response_model=schemas.Deck)
async def share_deck(
    deck_id: str,
    user_id: str,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Share a deck with another user.
    """
    deck = crud.get_deck(db, deck_id)
    if not deck:
        logger.warning(f"Deck not found: {deck_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )

    # Check if user is the owner
    if deck.owner_id != current_user.id:
        logger.warning(f"User {current_user.username} attempted to share deck {deck_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Check if target user exists
    user = crud.get_user(db, user_id)
    if not user:
        logger.warning(f"User not found: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Share deck
    success = crud.share_deck(db, deck_id, user_id)
    if not success:
        logger.error(f"Failed to share deck {deck_id} with user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to share deck"
        )

    logger.info(f"Deck {deck_id} shared with user {user_id}")
    return deck
