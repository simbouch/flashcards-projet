"""
CRUD operations for database models.
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from . import models, schemas
from loguru import logger
from typing import List, Optional, Dict, Any, Union
from passlib.context import CryptContext
import uuid
import secrets
from datetime import datetime, timedelta

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hash a password for storing."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a stored password against a provided password."""
    return pwd_context.verify(plain_password, hashed_password)

# User CRUD operations
def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user."""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        id=str(uuid.uuid4()),
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hashed_password,
        role=models.UserRole.USER.value
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"Created user: {db_user.username}")
        return db_user
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Failed to create user: {e}")
        raise ValueError("Username or email already exists")

def get_user(db: Session, user_id: str) -> Optional[models.User]:
    """Get a user by ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get a user by email."""
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Get a user by username."""
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """Get a list of users."""
    return db.query(models.User).offset(skip).limit(limit).all()

def update_user(db: Session, user_id: str, user_update: schemas.UserUpdate) -> Optional[models.User]:
    """Update a user."""
    db_user = get_user(db, user_id)
    if db_user:
        update_data = user_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
        logger.info(f"Updated user: {db_user.username}")
        return db_user
    return None

def delete_user(db: Session, user_id: str) -> bool:
    """Delete a user."""
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        logger.info(f"Deleted user: {db_user.username}")
        return True
    return False

# Document CRUD operations
def create_document(db: Session, document: schemas.DocumentCreate, owner_id: str, file_path: str) -> models.Document:
    """Create a new document."""
    db_document = models.Document(
        id=str(uuid.uuid4()),
        filename=document.filename,
        mime_type=document.mime_type,
        file_path=file_path,
        owner_id=owner_id,
        status=models.DocumentStatus.UPLOADED.value
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    logger.info(f"Created document: {db_document.filename}")
    return db_document

def get_document(db: Session, document_id: str) -> Optional[models.Document]:
    """Get a document by ID."""
    return db.query(models.Document).filter(models.Document.id == document_id).first()

def get_documents_by_owner(db: Session, owner_id: str, skip: int = 0, limit: int = 100) -> List[models.Document]:
    """Get documents by owner ID."""
    return db.query(models.Document).filter(models.Document.owner_id == owner_id).offset(skip).limit(limit).all()

def update_document_status(db: Session, document_id: str, status: str, error_message: Optional[str] = None) -> Optional[models.Document]:
    """Update a document's status."""
    db_document = get_document(db, document_id)
    if db_document:
        db_document.status = status
        if error_message:
            db_document.error_message = error_message
        db.commit()
        db.refresh(db_document)
        logger.info(f"Updated document status: {db_document.filename} -> {status}")
        return db_document
    return None

def delete_document(db: Session, document_id: str) -> bool:
    """Delete a document."""
    db_document = get_document(db, document_id)
    if db_document:
        db.delete(db_document)
        db.commit()
        logger.info(f"Deleted document: {db_document.filename}")
        return True
    return False

# ExtractedText CRUD operations
def create_extracted_text(db: Session, extracted_text: schemas.ExtractedTextCreate) -> models.ExtractedText:
    """Create extracted text for a document."""
    db_extracted_text = models.ExtractedText(
        id=str(uuid.uuid4()),
        content=extracted_text.content,
        document_id=extracted_text.document_id
    )
    db.add(db_extracted_text)
    db.commit()
    db.refresh(db_extracted_text)
    logger.info(f"Created extracted text for document: {extracted_text.document_id}")
    return db_extracted_text

def get_extracted_text_by_document(db: Session, document_id: str) -> Optional[models.ExtractedText]:
    """Get extracted text by document ID."""
    return db.query(models.ExtractedText).filter(models.ExtractedText.document_id == document_id).first()

def delete_extracted_text(db: Session, extracted_text_id: str) -> bool:
    """Delete extracted text."""
    db_extracted_text = db.query(models.ExtractedText).filter(models.ExtractedText.id == extracted_text_id).first()
    if db_extracted_text:
        db.delete(db_extracted_text)
        db.commit()
        logger.info(f"Deleted extracted text: {extracted_text_id}")
        return True
    return False

# Deck CRUD operations
def create_deck(db: Session, deck: schemas.DeckCreate, owner_id: str) -> models.Deck:
    """Create a new deck."""
    db_deck = models.Deck(
        id=str(uuid.uuid4()),
        title=deck.title,
        description=deck.description,
        is_public=deck.is_public,
        owner_id=owner_id,
        document_id=deck.document_id
    )
    db.add(db_deck)
    db.commit()
    db.refresh(db_deck)
    logger.info(f"Created deck: {db_deck.title}")
    return db_deck

def get_deck(db: Session, deck_id: str) -> Optional[models.Deck]:
    """Get a deck by ID."""
    return db.query(models.Deck).filter(models.Deck.id == deck_id).first()

def get_decks_by_owner(db: Session, owner_id: str, skip: int = 0, limit: int = 100) -> List[models.Deck]:
    """Get decks by owner ID."""
    return db.query(models.Deck).filter(models.Deck.owner_id == owner_id).offset(skip).limit(limit).all()

def get_public_decks(db: Session, skip: int = 0, limit: int = 100) -> List[models.Deck]:
    """Get public decks."""
    return db.query(models.Deck).filter(models.Deck.is_public == True).offset(skip).limit(limit).all()

def update_deck(db: Session, deck_id: str, deck_update: schemas.DeckUpdate) -> Optional[models.Deck]:
    """Update a deck."""
    db_deck = get_deck(db, deck_id)
    if db_deck:
        update_data = deck_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_deck, key, value)
        db.commit()
        db.refresh(db_deck)
        logger.info(f"Updated deck: {db_deck.title}")
        return db_deck
    return None

def delete_deck(db: Session, deck_id: str) -> bool:
    """Delete a deck."""
    db_deck = get_deck(db, deck_id)
    if db_deck:
        db.delete(db_deck)
        db.commit()
        logger.info(f"Deleted deck: {db_deck.title}")
        return True
    return False

def share_deck(db: Session, deck_id: str, user_id: str) -> bool:
    """Share a deck with a user."""
    db_deck = get_deck(db, deck_id)
    db_user = get_user(db, user_id)
    if db_deck and db_user:
        db_deck.shared_with.append(db_user)
        db.commit()
        logger.info(f"Shared deck {db_deck.title} with user {db_user.username}")
        return True
    return False

# Flashcard CRUD operations
def create_flashcard(db: Session, flashcard: schemas.FlashcardCreate) -> models.Flashcard:
    """Create a new flashcard."""
    db_flashcard = models.Flashcard(
        id=str(uuid.uuid4()),
        question=flashcard.question,
        answer=flashcard.answer,
        deck_id=flashcard.deck_id
    )
    db.add(db_flashcard)
    db.commit()
    db.refresh(db_flashcard)
    logger.info(f"Created flashcard in deck: {flashcard.deck_id}")
    return db_flashcard

def get_flashcard(db: Session, flashcard_id: str) -> Optional[models.Flashcard]:
    """Get a flashcard by ID."""
    return db.query(models.Flashcard).filter(models.Flashcard.id == flashcard_id).first()

def get_flashcards_by_deck(db: Session, deck_id: str, skip: int = 0, limit: int = 100) -> List[models.Flashcard]:
    """Get flashcards by deck ID."""
    return db.query(models.Flashcard).filter(models.Flashcard.deck_id == deck_id).offset(skip).limit(limit).all()

def update_flashcard(db: Session, flashcard_id: str, flashcard_update: schemas.FlashcardUpdate) -> Optional[models.Flashcard]:
    """Update a flashcard."""
    db_flashcard = get_flashcard(db, flashcard_id)
    if db_flashcard:
        update_data = flashcard_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_flashcard, key, value)
        db.commit()
        db.refresh(db_flashcard)
        logger.info(f"Updated flashcard: {flashcard_id}")
        return db_flashcard
    return None

def delete_flashcard(db: Session, flashcard_id: str) -> bool:
    """Delete a flashcard."""
    db_flashcard = get_flashcard(db, flashcard_id)
    if db_flashcard:
        db.delete(db_flashcard)
        db.commit()
        logger.info(f"Deleted flashcard: {flashcard_id}")
        return True
    return False

# Authentication functions
def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]:
    """Authenticate a user by username and password."""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

# Refresh token operations
def create_refresh_token(db: Session, user_id: str, expires_delta: timedelta = None) -> models.RefreshToken:
    """Create a new refresh token for a user."""
    if expires_delta is None:
        expires_delta = timedelta(days=30)  # Default to 30 days

    # Generate a secure token
    token_value = secrets.token_urlsafe(64)
    expires_at = datetime.now() + expires_delta

    # Create token in database
    db_token = models.RefreshToken(
        id=str(uuid.uuid4()),
        token=token_value,
        user_id=user_id,
        expires_at=expires_at
    )

    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    logger.info(f"Created refresh token for user: {user_id}")

    return db_token

def get_refresh_token(db: Session, token: str) -> Optional[models.RefreshToken]:
    """Get a refresh token by its value."""
    return db.query(models.RefreshToken).filter(models.RefreshToken.token == token).first()

def validate_refresh_token(db: Session, token: str) -> Optional[models.User]:
    """Validate a refresh token and return the associated user if valid."""
    db_token = get_refresh_token(db, token)

    if not db_token:
        logger.warning("Refresh token not found")
        return None

    if db_token.revoked:
        logger.warning(f"Revoked refresh token used: {db_token.id}")
        return None

    if db_token.is_expired:
        logger.warning(f"Expired refresh token used: {db_token.id}")
        return None

    # Get the user associated with the token
    user = get_user(db, db_token.user_id)
    if not user or not user.is_active:
        logger.warning(f"Token for inactive or deleted user: {db_token.user_id}")
        return None

    return user

def revoke_refresh_token(db: Session, token: str) -> bool:
    """Revoke a refresh token."""
    db_token = get_refresh_token(db, token)
    if db_token:
        db_token.revoked = True
        db.commit()
        logger.info(f"Revoked refresh token: {db_token.id}")
        return True
    return False

def revoke_all_user_tokens(db: Session, user_id: str) -> int:
    """Revoke all refresh tokens for a user."""
    tokens = db.query(models.RefreshToken).filter(
        models.RefreshToken.user_id == user_id,
        models.RefreshToken.revoked == False
    ).all()

    count = 0
    for token in tokens:
        token.revoked = True
        count += 1

    db.commit()
    logger.info(f"Revoked {count} refresh tokens for user: {user_id}")
    return count

def rotate_refresh_token(db: Session, old_token: str, expires_delta: timedelta = None) -> Optional[models.RefreshToken]:
    """Revoke the old token and create a new one."""
    # Get and validate the old token
    db_token = get_refresh_token(db, old_token)
    if not db_token or db_token.revoked or db_token.is_expired:
        logger.warning(f"Attempted to rotate invalid token: {old_token}")
        return None

    # Revoke the old token
    db_token.revoked = True

    # Create a new token
    new_token = create_refresh_token(db, db_token.user_id, expires_delta)

    db.commit()
    logger.info(f"Rotated refresh token for user: {db_token.user_id}")

    return new_token
