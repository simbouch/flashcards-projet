"""
Unit tests for the flashcard service.
These tests use mocks to isolate the flashcard service from its dependencies.
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from db_module import crud, schemas, models
from backend_service.src.services.flashcard_service import (
    get_flashcards_by_deck,
    create_flashcard,
    update_flashcard,
    delete_flashcard
)

@pytest.mark.flashcards
@pytest.mark.unit
def test_get_flashcards_by_deck():
    """Test getting flashcards by deck ID."""
    # Arrange
    db = MagicMock()
    deck_id = "test-deck-id"
    
    # Create mock flashcards
    mock_flashcards = [
        MagicMock(id="card1", question="Question 1", answer="Answer 1", deck_id=deck_id),
        MagicMock(id="card2", question="Question 2", answer="Answer 2", deck_id=deck_id)
    ]
    
    # Configure the mock
    db.query.return_value.filter.return_value.all.return_value = mock_flashcards
    
    # Act
    result = get_flashcards_by_deck(db, deck_id)
    
    # Assert
    assert result is not None
    assert len(result) == 2
    assert result[0].id == "card1"
    assert result[1].id == "card2"
    db.query.assert_called_once()

@pytest.mark.flashcards
@pytest.mark.unit
@patch("db_module.crud.create_flashcard")
def test_create_flashcard(mock_create_flashcard):
    """Test creating a flashcard."""
    # Arrange
    db = MagicMock()
    flashcard_data = schemas.FlashcardCreate(
        question="New Question",
        answer="New Answer",
        deck_id="test-deck-id"
    )
    
    # Configure the mock
    mock_flashcard = MagicMock()
    mock_flashcard.id = "new-card-id"
    mock_flashcard.question = flashcard_data.question
    mock_flashcard.answer = flashcard_data.answer
    mock_flashcard.deck_id = flashcard_data.deck_id
    mock_create_flashcard.return_value = mock_flashcard
    
    # Act
    result = create_flashcard(db, flashcard_data)
    
    # Assert
    assert result is not None
    assert result.id == "new-card-id"
    assert result.question == flashcard_data.question
    assert result.answer == flashcard_data.answer
    assert result.deck_id == flashcard_data.deck_id
    mock_create_flashcard.assert_called_once_with(db, flashcard_data)

@pytest.mark.flashcards
@pytest.mark.unit
@patch("db_module.crud.update_flashcard")
def test_update_flashcard(mock_update_flashcard):
    """Test updating a flashcard."""
    # Arrange
    db = MagicMock()
    flashcard_id = "test-card-id"
    flashcard_data = schemas.FlashcardUpdate(
        question="Updated Question",
        answer="Updated Answer"
    )
    
    # Configure the mock
    mock_flashcard = MagicMock()
    mock_flashcard.id = flashcard_id
    mock_flashcard.question = flashcard_data.question
    mock_flashcard.answer = flashcard_data.answer
    mock_update_flashcard.return_value = mock_flashcard
    
    # Act
    result = update_flashcard(db, flashcard_id, flashcard_data)
    
    # Assert
    assert result is not None
    assert result.id == flashcard_id
    assert result.question == flashcard_data.question
    assert result.answer == flashcard_data.answer
    mock_update_flashcard.assert_called_once_with(db, flashcard_id, flashcard_data)

@pytest.mark.flashcards
@pytest.mark.unit
@patch("db_module.crud.delete_flashcard")
def test_delete_flashcard(mock_delete_flashcard):
    """Test deleting a flashcard."""
    # Arrange
    db = MagicMock()
    flashcard_id = "test-card-id"
    
    # Configure the mock
    mock_delete_flashcard.return_value = True
    
    # Act
    result = delete_flashcard(db, flashcard_id)
    
    # Assert
    assert result is True
    mock_delete_flashcard.assert_called_once_with(db, flashcard_id)
