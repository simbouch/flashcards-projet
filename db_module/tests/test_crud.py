"""
Tests for CRUD operations.
"""
import pytest
from db_module import crud, schemas, models
from sqlalchemy.exc import IntegrityError
import uuid

def test_create_user(db_session):
    """Test creating a user."""
    user_data = schemas.UserCreate(
        email="newuser@example.com",
        username="newuser",
        password="Password123",
        full_name="New User"
    )
    user = crud.create_user(db_session, user_data)
    assert user.email == "newuser@example.com"
    assert user.username == "newuser"
    assert user.full_name == "New User"
    assert user.role == models.UserRole.USER.value
    assert user.is_active is True
    assert user.hashed_password != "Password123"  # Password should be hashed

def test_create_duplicate_user(db_session, test_user):
    """Test creating a user with duplicate email or username."""
    # Duplicate email
    user_data = schemas.UserCreate(
        email=test_user.email,
        username="uniqueuser",
        password="Password123"
    )
    with pytest.raises(ValueError):
        crud.create_user(db_session, user_data)
    
    # Duplicate username
    user_data = schemas.UserCreate(
        email="unique@example.com",
        username=test_user.username,
        password="Password123"
    )
    with pytest.raises(ValueError):
        crud.create_user(db_session, user_data)

def test_get_user(db_session, test_user):
    """Test getting a user by ID."""
    user = crud.get_user(db_session, test_user.id)
    assert user is not None
    assert user.id == test_user.id
    assert user.email == test_user.email
    
    # Test non-existent user
    non_existent_id = str(uuid.uuid4())
    user = crud.get_user(db_session, non_existent_id)
    assert user is None

def test_get_user_by_email(db_session, test_user):
    """Test getting a user by email."""
    user = crud.get_user_by_email(db_session, test_user.email)
    assert user is not None
    assert user.id == test_user.id
    
    # Test non-existent email
    user = crud.get_user_by_email(db_session, "nonexistent@example.com")
    assert user is None

def test_get_user_by_username(db_session, test_user):
    """Test getting a user by username."""
    user = crud.get_user_by_username(db_session, test_user.username)
    assert user is not None
    assert user.id == test_user.id
    
    # Test non-existent username
    user = crud.get_user_by_username(db_session, "nonexistentuser")
    assert user is None

def test_update_user(db_session, test_user):
    """Test updating a user."""
    user_update = schemas.UserUpdate(
        full_name="Updated Name",
        is_active=False
    )
    updated_user = crud.update_user(db_session, test_user.id, user_update)
    assert updated_user is not None
    assert updated_user.full_name == "Updated Name"
    assert updated_user.is_active is False
    
    # Test non-existent user
    non_existent_id = str(uuid.uuid4())
    updated_user = crud.update_user(db_session, non_existent_id, user_update)
    assert updated_user is None

def test_delete_user(db_session, test_user):
    """Test deleting a user."""
    result = crud.delete_user(db_session, test_user.id)
    assert result is True
    
    # Verify user is deleted
    user = crud.get_user(db_session, test_user.id)
    assert user is None
    
    # Test deleting non-existent user
    non_existent_id = str(uuid.uuid4())
    result = crud.delete_user(db_session, non_existent_id)
    assert result is False

def test_create_document(db_session, test_user):
    """Test creating a document."""
    document_data = schemas.DocumentCreate(
        filename="document.pdf",
        mime_type="application/pdf"
    )
    document = crud.create_document(
        db_session, 
        document_data, 
        owner_id=test_user.id,
        file_path="/path/to/document.pdf"
    )
    assert document.filename == "document.pdf"
    assert document.mime_type == "application/pdf"
    assert document.file_path == "/path/to/document.pdf"
    assert document.owner_id == test_user.id
    assert document.status == models.DocumentStatus.UPLOADED.value

def test_get_document(db_session, test_document):
    """Test getting a document by ID."""
    document = crud.get_document(db_session, test_document.id)
    assert document is not None
    assert document.id == test_document.id
    
    # Test non-existent document
    non_existent_id = str(uuid.uuid4())
    document = crud.get_document(db_session, non_existent_id)
    assert document is None

def test_get_documents_by_owner(db_session, test_user, test_document):
    """Test getting documents by owner ID."""
    documents = crud.get_documents_by_owner(db_session, test_user.id)
    assert len(documents) == 1
    assert documents[0].id == test_document.id
    
    # Test non-existent owner
    non_existent_id = str(uuid.uuid4())
    documents = crud.get_documents_by_owner(db_session, non_existent_id)
    assert len(documents) == 0

def test_update_document_status(db_session, test_document):
    """Test updating a document's status."""
    updated_document = crud.update_document_status(
        db_session, 
        test_document.id, 
        models.DocumentStatus.OCR_COMPLETE.value
    )
    assert updated_document is not None
    assert updated_document.status == models.DocumentStatus.OCR_COMPLETE.value
    
    # Test with error message
    updated_document = crud.update_document_status(
        db_session, 
        test_document.id, 
        models.DocumentStatus.ERROR.value,
        "OCR failed"
    )
    assert updated_document.status == models.DocumentStatus.ERROR.value
    assert updated_document.error_message == "OCR failed"
    
    # Test non-existent document
    non_existent_id = str(uuid.uuid4())
    updated_document = crud.update_document_status(
        db_session, 
        non_existent_id, 
        models.DocumentStatus.OCR_COMPLETE.value
    )
    assert updated_document is None

def test_create_extracted_text(db_session, test_document):
    """Test creating extracted text."""
    extracted_text_data = schemas.ExtractedTextCreate(
        content="This is some extracted text.",
        document_id=test_document.id
    )
    extracted_text = crud.create_extracted_text(db_session, extracted_text_data)
    assert extracted_text.content == "This is some extracted text."
    assert extracted_text.document_id == test_document.id

def test_get_extracted_text_by_document(db_session, test_document, test_extracted_text):
    """Test getting extracted text by document ID."""
    extracted_text = crud.get_extracted_text_by_document(db_session, test_document.id)
    assert extracted_text is not None
    assert extracted_text.id == test_extracted_text.id
    assert extracted_text.content == test_extracted_text.content
    
    # Test non-existent document
    non_existent_id = str(uuid.uuid4())
    extracted_text = crud.get_extracted_text_by_document(db_session, non_existent_id)
    assert extracted_text is None

def test_create_deck(db_session, test_user, test_document):
    """Test creating a deck."""
    deck_data = schemas.DeckCreate(
        title="New Deck",
        description="A new deck for testing",
        document_id=test_document.id
    )
    deck = crud.create_deck(db_session, deck_data, owner_id=test_user.id)
    assert deck.title == "New Deck"
    assert deck.description == "A new deck for testing"
    assert deck.owner_id == test_user.id
    assert deck.document_id == test_document.id

def test_get_deck(db_session, test_deck):
    """Test getting a deck by ID."""
    deck = crud.get_deck(db_session, test_deck.id)
    assert deck is not None
    assert deck.id == test_deck.id
    
    # Test non-existent deck
    non_existent_id = str(uuid.uuid4())
    deck = crud.get_deck(db_session, non_existent_id)
    assert deck is None

def test_create_flashcard(db_session, test_deck):
    """Test creating a flashcard."""
    flashcard_data = schemas.FlashcardCreate(
        question="What is the capital of Germany?",
        answer="Berlin",
        deck_id=test_deck.id
    )
    flashcard = crud.create_flashcard(db_session, flashcard_data)
    assert flashcard.question == "What is the capital of Germany?"
    assert flashcard.answer == "Berlin"
    assert flashcard.deck_id == test_deck.id

def test_get_flashcards_by_deck(db_session, test_deck, test_flashcard):
    """Test getting flashcards by deck ID."""
    flashcards = crud.get_flashcards_by_deck(db_session, test_deck.id)
    assert len(flashcards) == 1
    assert flashcards[0].id == test_flashcard.id
    
    # Test non-existent deck
    non_existent_id = str(uuid.uuid4())
    flashcards = crud.get_flashcards_by_deck(db_session, non_existent_id)
    assert len(flashcards) == 0


def _create_study_session_and_record(db_session, user_id: str, deck_id: str, flashcard_id: str):
    """Helper to create a study session + record for cascade deletion tests."""
    study_session = models.StudySession(
        id=str(uuid.uuid4()),
        user_id=user_id,
        deck_id=deck_id,
    )
    db_session.add(study_session)
    db_session.commit()

    study_record = models.StudyRecord(
        id=str(uuid.uuid4()),
        is_correct=True,
        session_id=study_session.id,
        flashcard_id=flashcard_id,
    )
    db_session.add(study_record)
    db_session.commit()
    return study_session, study_record


def test_delete_flashcard_cascade_deletes_study_records(db_session, test_user, test_deck, test_flashcard):
    """Deleting a flashcard should remove dependent study records."""
    _session, record = _create_study_session_and_record(
        db_session,
        user_id=test_user.id,
        deck_id=test_deck.id,
        flashcard_id=test_flashcard.id,
    )

    flashcard_id = test_flashcard.id
    record_id = record.id

    # Precondition
    assert db_session.query(models.StudyRecord).filter_by(id=record_id).first() is not None

    ok = crud.delete_flashcard(db_session, flashcard_id)
    assert ok is True

    assert crud.get_flashcard(db_session, flashcard_id) is None
    assert (
        db_session.query(models.StudyRecord)
        .filter(models.StudyRecord.flashcard_id == flashcard_id)
        .count()
        == 0
    )


def test_delete_deck_cascade_deletes_flashcards_and_study(db_session, test_user, test_deck, test_flashcard):
    """Deleting a deck should remove flashcards and study data linked to it."""
    session, record = _create_study_session_and_record(
        db_session,
        user_id=test_user.id,
        deck_id=test_deck.id,
        flashcard_id=test_flashcard.id,
    )

    deck_id = test_deck.id
    session_id = session.id
    record_id = record.id

    ok = crud.delete_deck(db_session, deck_id)
    assert ok is True

    assert crud.get_deck(db_session, deck_id) is None
    assert db_session.query(models.Flashcard).filter_by(deck_id=deck_id).count() == 0
    assert db_session.query(models.StudySession).filter_by(deck_id=deck_id).count() == 0
    assert db_session.query(models.StudyRecord).filter_by(session_id=session_id).count() == 0
    assert db_session.query(models.StudyRecord).filter_by(id=record_id).count() == 0


def test_delete_document_cascade_deletes_decks_text_and_flashcards(
    db_session, test_document, test_extracted_text, test_deck, test_flashcard
):
    """Deleting a document should remove extracted text + decks/flashcards tied to it."""
    document_id = test_document.id
    deck_id = test_deck.id
    flashcard_id = test_flashcard.id

    ok = crud.delete_document(db_session, document_id)
    assert ok is True

    assert crud.get_document(db_session, document_id) is None
    assert crud.get_extracted_text_by_document(db_session, document_id) is None
    assert crud.get_deck(db_session, deck_id) is None
    assert crud.get_flashcard(db_session, flashcard_id) is None


def test_delete_user_cascade_deletes_owned_content_and_tokens(
    db_session,
    test_user,
    test_document,
    test_extracted_text,
    test_deck,
    test_flashcard,
    test_refresh_token,
):
    """Deleting a user should delete owned documents/decks/flashcards + tokens + study data."""
    session, record = _create_study_session_and_record(
        db_session,
        user_id=test_user.id,
        deck_id=test_deck.id,
        flashcard_id=test_flashcard.id,
    )

    user_id = test_user.id
    document_id = test_document.id
    deck_id = test_deck.id
    flashcard_id = test_flashcard.id
    refresh_token_id = test_refresh_token.id
    session_id = session.id
    record_id = record.id

    ok = crud.delete_user(db_session, user_id)
    assert ok is True

    assert crud.get_user(db_session, user_id) is None
    assert crud.get_document(db_session, document_id) is None
    assert crud.get_extracted_text_by_document(db_session, document_id) is None
    assert crud.get_deck(db_session, deck_id) is None
    assert crud.get_flashcard(db_session, flashcard_id) is None
    assert db_session.query(models.RefreshToken).filter_by(id=refresh_token_id).count() == 0
    assert db_session.query(models.StudySession).filter_by(id=session_id).count() == 0
    assert db_session.query(models.StudyRecord).filter_by(id=record_id).count() == 0
