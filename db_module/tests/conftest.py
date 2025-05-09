"""
Test fixtures for the database module.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from db_module.database import Base
from db_module.models import User, Document, ExtractedText, Deck, Flashcard
from db_module import crud, schemas

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db_engine():
    """Create a SQLAlchemy engine for testing."""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(db_engine):
    """Create a SQLAlchemy session for testing."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user_data = schemas.UserCreate(
        email="test@example.com",
        username="testuser",
        password="Password123",
        full_name="Test User"
    )
    user = crud.create_user(db_session, user_data)
    return user

@pytest.fixture
def test_document(db_session, test_user):
    """Create a test document."""
    document_data = schemas.DocumentCreate(
        filename="test.png",
        mime_type="image/png"
    )
    document = crud.create_document(
        db_session, 
        document_data, 
        owner_id=test_user.id,
        file_path="/path/to/test.png"
    )
    return document

@pytest.fixture
def test_extracted_text(db_session, test_document):
    """Create test extracted text."""
    extracted_text_data = schemas.ExtractedTextCreate(
        content="This is some test extracted text.",
        document_id=test_document.id
    )
    extracted_text = crud.create_extracted_text(db_session, extracted_text_data)
    return extracted_text

@pytest.fixture
def test_deck(db_session, test_user, test_document):
    """Create a test deck."""
    deck_data = schemas.DeckCreate(
        title="Test Deck",
        description="A deck for testing",
        document_id=test_document.id
    )
    deck = crud.create_deck(db_session, deck_data, owner_id=test_user.id)
    return deck

@pytest.fixture
def test_flashcard(db_session, test_deck):
    """Create a test flashcard."""
    flashcard_data = schemas.FlashcardCreate(
        question="What is the capital of France?",
        answer="Paris",
        deck_id=test_deck.id
    )
    flashcard = crud.create_flashcard(db_session, flashcard_data)
    return flashcard
