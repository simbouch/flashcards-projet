"""
Test fixtures for the LLM service.
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the FastAPI app
from src.main import app

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)

@pytest.fixture
def mock_flashcard_generator():
    """Mock the FlashcardGenerator class."""
    with patch("src.main.FlashcardGenerator") as mock_generator_class:
        # Create a mock instance
        mock_instance = MagicMock()

        # Configure the mock instance's generate_flashcards method
        async def mock_generate_flashcards(text, num_cards):
            return {
                "flashcards": [
                    {"question": "Test question 1?", "answer": "Test answer 1"},
                    {"question": "Test question 2?", "answer": "Test answer 2"}
                ],
                "metadata": {
                    "text_length": len(text),
                    "requested_cards": num_cards,
                    "generated_cards": 2,
                    "processing_time_seconds": 0.1
                }
            }

        # Configure the mock instance's generate_flashcards_from_chunks method
        async def mock_generate_flashcards_from_chunks(chunks, num_cards):
            return {
                "flashcards": [
                    {"question": "Chunk test question 1?", "answer": "Chunk test answer 1"},
                    {"question": "Chunk test question 2?", "answer": "Chunk test answer 2"}
                ],
                "metadata": {
                    "chunks": len(chunks),
                    "total_text_length": sum(len(chunk) for chunk in chunks),
                    "requested_cards": num_cards,
                    "generated_cards": 2,
                    "processing_time_seconds": 0.1
                }
            }

        mock_instance.generate_flashcards.side_effect = mock_generate_flashcards
        mock_instance.generate_flashcards_from_chunks.side_effect = mock_generate_flashcards_from_chunks

        # Configure the mock class to return the mock instance
        mock_generator_class.return_value = mock_instance

        yield mock_instance
