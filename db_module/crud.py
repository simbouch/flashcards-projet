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
        update_data = user_update.dict(exclude_unset=True)
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
        update_data = deck_update.dict(exclude_unset=True)
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
        update_data = flashcard_update.dict(exclude_unset=True)
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
