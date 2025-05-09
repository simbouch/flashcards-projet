"""
Tests for the LLM service API.
"""
import pytest
from fastapi.testclient import TestClient
import json

def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "llm"

def test_health_check(client, mock_flashcard_generator):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "healthy" in data["message"]

def test_generate_flashcards(client, mock_flashcard_generator):
    """Test the generate flashcards endpoint."""
    request_data = {
        "text": "This is a test text for generating flashcards.",
        "num_cards": 5
    }
    
    response = client.post(
        "/generate",
        json=request_data
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "flashcards" in data
    assert "metadata" in data
    
    # Check flashcards
    assert len(data["flashcards"]) > 0
    assert "question" in data["flashcards"][0]
    assert "answer" in data["flashcards"][0]
    
    # Check metadata
    assert data["metadata"]["text_length"] == len(request_data["text"])
    assert data["metadata"]["requested_cards"] == request_data["num_cards"]
    assert data["metadata"]["generated_cards"] > 0
    assert data["metadata"]["processing_time_seconds"] >= 0

def test_generate_flashcards_empty_text(client):
    """Test the generate flashcards endpoint with empty text."""
    request_data = {
        "text": "",
        "num_cards": 5
    }
    
    response = client.post(
        "/generate",
        json=request_data
    )
    
    assert response.status_code == 422  # Validation error

def test_generate_flashcards_invalid_num_cards(client):
    """Test the generate flashcards endpoint with invalid num_cards."""
    # Test with num_cards < 1
    request_data = {
        "text": "This is a test text.",
        "num_cards": 0
    }
    
    response = client.post(
        "/generate",
        json=request_data
    )
    
    assert response.status_code == 422  # Validation error
    
    # Test with num_cards > 20
    request_data = {
        "text": "This is a test text.",
        "num_cards": 21
    }
    
    response = client.post(
        "/generate",
        json=request_data
    )
    
    assert response.status_code == 422  # Validation error

def test_generate_flashcards_from_chunks(client, mock_flashcard_generator):
    """Test the generate flashcards from chunks endpoint."""
    request_data = {
        "chunks": [
            "This is the first chunk of text.",
            "This is the second chunk of text."
        ],
        "num_cards": 5
    }
    
    response = client.post(
        "/generate/chunks",
        json=request_data
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "flashcards" in data
    assert "metadata" in data
    
    # Check flashcards
    assert len(data["flashcards"]) > 0
    assert "question" in data["flashcards"][0]
    assert "answer" in data["flashcards"][0]
    
    # Check metadata
    assert data["metadata"]["chunks"] == len(request_data["chunks"])
    assert data["metadata"]["requested_cards"] == request_data["num_cards"]
    assert data["metadata"]["generated_cards"] > 0
    assert data["metadata"]["processing_time_seconds"] >= 0

def test_generate_flashcards_from_chunks_empty_chunks(client):
    """Test the generate flashcards from chunks endpoint with empty chunks."""
    request_data = {
        "chunks": [],
        "num_cards": 5
    }
    
    response = client.post(
        "/generate/chunks",
        json=request_data
    )
    
    assert response.status_code == 422  # Validation error

def test_generate_flashcards_from_chunks_empty_chunk(client):
    """Test the generate flashcards from chunks endpoint with an empty chunk."""
    request_data = {
        "chunks": ["This is a valid chunk", ""],
        "num_cards": 5
    }
    
    response = client.post(
        "/generate/chunks",
        json=request_data
    )
    
    assert response.status_code == 422  # Validation error
