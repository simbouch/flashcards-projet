"""
Tests for database models.
"""
import pytest
from db_module.models import (
    User, Document, ExtractedText, Deck, Flashcard,
    StudySession, StudyRecord, UserRole, DocumentStatus
)
from sqlalchemy.exc import IntegrityError
import uuid

def test_user_model(db_session):
    """Test the User model."""
    user = User(
        id=str(uuid.uuid4()),
        email="user@example.com",
        username="testuser",
        hashed_password="hashed_password",
        full_name="Test User",
        role=UserRole.USER.value
    )
    db_session.add(user)
    db_session.commit()
    
    # Test retrieval
    retrieved_user = db_session.query(User).filter_by(username="testuser").first()
    assert retrieved_user is not None
    assert retrieved_user.email == "user@example.com"
    assert retrieved_user.full_name == "Test User"
    assert retrieved_user.role == UserRole.USER.value
    assert retrieved_user.is_active is True
    
    # Test unique constraints
    duplicate_user = User(
        id=str(uuid.uuid4()),
        email="user@example.com",  # Duplicate email
        username="uniqueuser",
        hashed_password="hashed_password"
    )
    db_session.add(duplicate_user)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
    
    duplicate_user = User(
        id=str(uuid.uuid4()),
        email="unique@example.com",
        username="testuser",  # Duplicate username
        hashed_password="hashed_password"
    )
    db_session.add(duplicate_user)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

def test_document_model(db_session, test_user):
    """Test the Document model."""
    document = Document(
        id=str(uuid.uuid4()),
        filename="test.pdf",
        file_path="/path/to/test.pdf",
        mime_type="application/pdf",
        status=DocumentStatus.UPLOADED.value,
        owner_id=test_user.id
    )
    db_session.add(document)
    db_session.commit()
    
    # Test retrieval
    retrieved_document = db_session.query(Document).filter_by(filename="test.pdf").first()
    assert retrieved_document is not None
    assert retrieved_document.file_path == "/path/to/test.pdf"
    assert retrieved_document.mime_type == "application/pdf"
    assert retrieved_document.status == DocumentStatus.UPLOADED.value
    assert retrieved_document.owner_id == test_user.id
    
    # Test relationship with User
    assert retrieved_document.owner.id == test_user.id

def test_extracted_text_model(db_session, test_document):
    """Test the ExtractedText model."""
    extracted_text = ExtractedText(
        id=str(uuid.uuid4()),
        content="This is some extracted text for testing.",
        document_id=test_document.id
    )
    db_session.add(extracted_text)
    db_session.commit()
    
    # Test retrieval
    retrieved_text = db_session.query(ExtractedText).filter_by(document_id=test_document.id).first()
    assert retrieved_text is not None
    assert retrieved_text.content == "This is some extracted text for testing."
    
    # Test relationship with Document
    assert retrieved_text.document.id == test_document.id
    
    # Test unique constraint on document_id
    duplicate_text = ExtractedText(
        id=str(uuid.uuid4()),
        content="Duplicate text",
        document_id=test_document.id  # Duplicate document_id
    )
    db_session.add(duplicate_text)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

def test_deck_model(db_session, test_user, test_document):
    """Test the Deck model."""
    deck = Deck(
        id=str(uuid.uuid4()),
        title="Test Deck",
        description="A deck for testing",
        owner_id=test_user.id,
        document_id=test_document.id
    )
    db_session.add(deck)
    db_session.commit()
    
    # Test retrieval
    retrieved_deck = db_session.query(Deck).filter_by(title="Test Deck").first()
    assert retrieved_deck is not None
    assert retrieved_deck.description == "A deck for testing"
    assert retrieved_deck.owner_id == test_user.id
    assert retrieved_deck.document_id == test_document.id
    
    # Test relationships
    assert retrieved_deck.owner.id == test_user.id
    assert retrieved_deck.document.id == test_document.id

def test_flashcard_model(db_session, test_deck):
    """Test the Flashcard model."""
    flashcard = Flashcard(
        id=str(uuid.uuid4()),
        question="What is the capital of France?",
        answer="Paris",
        deck_id=test_deck.id
    )
    db_session.add(flashcard)
    db_session.commit()
    
    # Test retrieval
    retrieved_flashcard = db_session.query(Flashcard).filter_by(deck_id=test_deck.id).first()
    assert retrieved_flashcard is not None
    assert retrieved_flashcard.question == "What is the capital of France?"
    assert retrieved_flashcard.answer == "Paris"
    
    # Test relationship with Deck
    assert retrieved_flashcard.deck.id == test_deck.id

def test_study_session_model(db_session, test_user, test_deck):
    """Test the StudySession model."""
    study_session = StudySession(
        id=str(uuid.uuid4()),
        user_id=test_user.id,
        deck_id=test_deck.id
    )
    db_session.add(study_session)
    db_session.commit()
    
    # Test retrieval
    retrieved_session = db_session.query(StudySession).filter_by(user_id=test_user.id).first()
    assert retrieved_session is not None
    assert retrieved_session.deck_id == test_deck.id
    
    # Test relationships
    assert retrieved_session.user.id == test_user.id
    assert retrieved_session.deck.id == test_deck.id

def test_study_record_model(db_session, test_flashcard):
    """Test the StudyRecord model."""
    # First create a study session
    study_session = StudySession(
        id=str(uuid.uuid4()),
        user_id=test_flashcard.deck.owner_id,
        deck_id=test_flashcard.deck_id
    )
    db_session.add(study_session)
    db_session.commit()
    
    # Now create a study record
    study_record = StudyRecord(
        id=str(uuid.uuid4()),
        is_correct=True,
        session_id=study_session.id,
        flashcard_id=test_flashcard.id
    )
    db_session.add(study_record)
    db_session.commit()
    
    # Test retrieval
    retrieved_record = db_session.query(StudyRecord).filter_by(session_id=study_session.id).first()
    assert retrieved_record is not None
    assert retrieved_record.is_correct is True
    assert retrieved_record.ease_factor == 2.5  # Default value
    assert retrieved_record.interval == 0  # Default value
    
    # Test relationships
    assert retrieved_record.session.id == study_session.id
    assert retrieved_record.flashcard.id == test_flashcard.id
