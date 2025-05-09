"""
Study session endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, List
from sqlalchemy.orm import Session
from datetime import datetime

from db_module import crud, models, schemas
from db_module.database import get_db
from ...auth.jwt import get_current_active_user
from ...logger_config import logger

router = APIRouter()

@router.post("/sessions", response_model=schemas.StudySession)
async def create_study_session(
    session_in: schemas.StudySessionCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create a new study session.
    """
    # Check if deck exists
    deck = crud.get_deck(db, session_in.deck_id)
    if not deck:
        logger.warning(f"Deck not found: {session_in.deck_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )
    
    # Check if user is the owner or the deck is public or shared
    if deck.owner_id != current_user.id and not deck.is_public:
        # Check if deck is shared with user
        if current_user not in deck.shared_with:
            logger.warning(f"User {current_user.username} attempted to create study session for deck {session_in.deck_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
    
    # Create study session
    session = models.StudySession(
        id=crud.generate_uuid(),
        user_id=current_user.id,
        deck_id=session_in.deck_id
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    logger.info(f"Study session created: {session.id}")
    return session

@router.get("/sessions", response_model=List[schemas.StudySession])
async def read_study_sessions(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Retrieve study sessions for the current user.
    """
    # Get study sessions
    sessions = db.query(models.StudySession).filter(
        models.StudySession.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return sessions

@router.get("/sessions/{session_id}", response_model=schemas.StudySession)
async def read_study_session(
    session_id: str,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get study session by ID.
    """
    # Get study session
    session = db.query(models.StudySession).filter(
        models.StudySession.id == session_id
    ).first()
    
    if not session:
        logger.warning(f"Study session not found: {session_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session not found"
        )
    
    # Check if user is the owner
    if session.user_id != current_user.id:
        logger.warning(f"User {current_user.username} attempted to access study session {session_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return session

@router.put("/sessions/{session_id}/end", response_model=schemas.StudySession)
async def end_study_session(
    session_id: str,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    End a study session.
    """
    # Get study session
    session = db.query(models.StudySession).filter(
        models.StudySession.id == session_id
    ).first()
    
    if not session:
        logger.warning(f"Study session not found: {session_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session not found"
        )
    
    # Check if user is the owner
    if session.user_id != current_user.id:
        logger.warning(f"User {current_user.username} attempted to end study session {session_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if session is already ended
    if session.ended_at:
        logger.warning(f"Study session already ended: {session_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Study session already ended"
        )
    
    # End session
    session.ended_at = datetime.utcnow()
    db.commit()
    db.refresh(session)
    
    logger.info(f"Study session ended: {session.id}")
    return session

@router.post("/records", response_model=schemas.StudyRecord)
async def create_study_record(
    record_in: schemas.StudyRecordCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create a new study record.
    """
    # Check if session exists
    session = db.query(models.StudySession).filter(
        models.StudySession.id == record_in.session_id
    ).first()
    
    if not session:
        logger.warning(f"Study session not found: {record_in.session_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session not found"
        )
    
    # Check if user is the owner of the session
    if session.user_id != current_user.id:
        logger.warning(f"User {current_user.username} attempted to create study record for session {record_in.session_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if flashcard exists
    flashcard = crud.get_flashcard(db, record_in.flashcard_id)
    if not flashcard:
        logger.warning(f"Flashcard not found: {record_in.flashcard_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found"
        )
    
    # Check if flashcard belongs to the session's deck
    if flashcard.deck_id != session.deck_id:
        logger.warning(f"Flashcard {record_in.flashcard_id} does not belong to deck {session.deck_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Flashcard does not belong to the session's deck"
        )
    
    # Create study record
    record = models.StudyRecord(
        id=crud.generate_uuid(),
        session_id=record_in.session_id,
        flashcard_id=record_in.flashcard_id,
        is_correct=record_in.is_correct
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    
    logger.info(f"Study record created: {record.id}")
    return record

@router.get("/records", response_model=List[schemas.StudyRecord])
async def read_study_records(
    session_id: str,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Retrieve study records for a session.
    """
    # Check if session exists
    session = db.query(models.StudySession).filter(
        models.StudySession.id == session_id
    ).first()
    
    if not session:
        logger.warning(f"Study session not found: {session_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session not found"
        )
    
    # Check if user is the owner of the session
    if session.user_id != current_user.id:
        logger.warning(f"User {current_user.username} attempted to access study records for session {session_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Get study records
    records = db.query(models.StudyRecord).filter(
        models.StudyRecord.session_id == session_id
    ).offset(skip).limit(limit).all()
    
    return records
