"""
Unit tests for the deck service.
These tests use mocks to isolate the deck service from its dependencies.
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from db_module import crud, schemas, models
from backend_service.src.services.deck_service import get_deck_by_id, get_decks_for_user, create_deck

@pytest.mark.decks
@pytest.mark.unit
def test_get_deck_by_id():
    """Test getting a deck by ID."""
    # Arrange
    db = MagicMock()
    deck_id = "test-deck-id"
    mock_deck = MagicMock()
    mock_deck.id = deck_id
    mock_deck.title = "Test Deck"
    mock_deck.owner_id = "test-user-id"
    
    # Configure the mock
    db.query.return_value.filter.return_value.first.return_value = mock_deck
    
    # Act
    result = get_deck_by_id(db, deck_id)
    
    # Assert
    assert result is not None
    assert result.id == deck_id
    assert result.title == "Test Deck"
    db.query.assert_called_once()

@pytest.mark.decks
@pytest.mark.unit
def test_get_deck_by_id_not_found():
    """Test getting a deck by ID when it doesn't exist."""
    # Arrange
    db = MagicMock()
    deck_id = "nonexistent-deck-id"
    
    # Configure the mock
    db.query.return_value.filter.return_value.first.return_value = None
    
    # Act
    result = get_deck_by_id(db, deck_id)
    
    # Assert
    assert result is None
    db.query.assert_called_once()

@pytest.mark.decks
@pytest.mark.unit
def test_get_decks_for_user():
    """Test getting decks for a user."""
    # Arrange
    db = MagicMock()
    user_id = "test-user-id"
    
    # Create mock decks
    mock_decks = [
        MagicMock(id="deck1", title="Deck 1", owner_id=user_id),
        MagicMock(id="deck2", title="Deck 2", owner_id=user_id)
    ]
    
    # Configure the mock
    db.query.return_value.filter.return_value.all.return_value = mock_decks
    
    # Act
    result = get_decks_for_user(db, user_id)
    
    # Assert
    assert result is not None
    assert len(result) == 2
    assert result[0].id == "deck1"
    assert result[1].id == "deck2"
    db.query.assert_called_once()

@pytest.mark.decks
@pytest.mark.unit
@patch("db_module.crud.create_deck")
def test_create_deck(mock_create_deck):
    """Test creating a deck."""
    # Arrange
    db = MagicMock()
    user_id = "test-user-id"
    deck_data = schemas.DeckCreate(
        title="New Deck",
        description="A new test deck",
        is_public=False
    )
    
    # Configure the mock
    mock_deck = MagicMock()
    mock_deck.id = "new-deck-id"
    mock_deck.title = deck_data.title
    mock_deck.description = deck_data.description
    mock_deck.is_public = deck_data.is_public
    mock_deck.owner_id = user_id
    mock_create_deck.return_value = mock_deck
    
    # Act
    result = create_deck(db, deck_data, user_id)
    
    # Assert
    assert result is not None
    assert result.id == "new-deck-id"
    assert result.title == deck_data.title
    assert result.description == deck_data.description
    assert result.is_public == deck_data.is_public
    assert result.owner_id == user_id
    mock_create_deck.assert_called_once_with(db, deck_data, user_id)
