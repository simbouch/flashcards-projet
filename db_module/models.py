"""
SQLAlchemy models for the flashcards application.
"""
from sqlalchemy import (
    Boolean, Column, ForeignKey, Integer, String, 
    Text, DateTime, Float, Table, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base
import uuid

def generate_uuid():
    """Generate a UUID string for use as a primary key."""
    return str(uuid.uuid4())

class UserRole(enum.Enum):
    """User roles for authorization."""
    USER = "user"
    ADMIN = "admin"

class DocumentStatus(enum.Enum):
    """Status of a document in the processing pipeline."""
    UPLOADED = "uploaded"
    OCR_PROCESSING = "ocr_processing"
    OCR_COMPLETE = "ocr_complete"
    FLASHCARD_GENERATING = "flashcard_generating"
    FLASHCARD_COMPLETE = "flashcard_complete"
    ERROR = "error"

# Association table for many-to-many relationship between users and decks
user_deck_association = Table(
    "user_deck_association",
    Base.metadata,
    Column("user_id", String(36), ForeignKey("users.id")),
    Column("deck_id", String(36), ForeignKey("decks.id")),
)

class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), default=UserRole.USER.value)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    documents = relationship("Document", back_populates="owner")
    owned_decks = relationship("Deck", back_populates="owner")
    shared_decks = relationship(
        "Deck", 
        secondary=user_deck_association,
        back_populates="shared_with"
    )
    study_sessions = relationship("StudySession", back_populates="user")

class Document(Base):
    """Document model for storing uploaded files."""
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    mime_type = Column(String(100), nullable=False)
    status = Column(String(50), default=DocumentStatus.UPLOADED.value)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign keys
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="documents")
    extracted_text = relationship("ExtractedText", back_populates="document", uselist=False)
    decks = relationship("Deck", back_populates="document")

class ExtractedText(Base):
    """Extracted text from documents using OCR."""
    __tablename__ = "extracted_texts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Foreign keys
    document_id = Column(String(36), ForeignKey("documents.id"), unique=True, nullable=False)
    
    # Relationships
    document = relationship("Document", back_populates="extracted_text")

class Deck(Base):
    """Deck of flashcards."""
    __tablename__ = "decks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign keys
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    document_id = Column(String(36), ForeignKey("documents.id"))
    
    # Relationships
    owner = relationship("User", back_populates="owned_decks")
    document = relationship("Document", back_populates="decks")
    flashcards = relationship("Flashcard", back_populates="deck")
    shared_with = relationship(
        "User", 
        secondary=user_deck_association,
        back_populates="shared_decks"
    )
    study_sessions = relationship("StudySession", back_populates="deck")

class Flashcard(Base):
    """Flashcard with question and answer."""
    __tablename__ = "flashcards"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign keys
    deck_id = Column(String(36), ForeignKey("decks.id"), nullable=False)
    
    # Relationships
    deck = relationship("Deck", back_populates="flashcards")
    study_records = relationship("StudyRecord", back_populates="flashcard")

class StudySession(Base):
    """Study session tracking."""
    __tablename__ = "study_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))
    
    # Foreign keys
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    deck_id = Column(String(36), ForeignKey("decks.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="study_sessions")
    deck = relationship("Deck", back_populates="study_sessions")
    records = relationship("StudyRecord", back_populates="session")

class StudyRecord(Base):
    """Individual flashcard study record within a session."""
    __tablename__ = "study_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    ease_factor = Column(Float, default=2.5)  # For spaced repetition algorithm
    interval = Column(Integer, default=0)  # Days until next review
    is_correct = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Foreign keys
    session_id = Column(String(36), ForeignKey("study_sessions.id"), nullable=False)
    flashcard_id = Column(String(36), ForeignKey("flashcards.id"), nullable=False)
    
    # Relationships
    session = relationship("StudySession", back_populates="records")
    flashcard = relationship("Flashcard", back_populates="study_records")
