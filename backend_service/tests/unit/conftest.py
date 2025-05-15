"""
Pytest configuration for unit tests.
This file contains fixtures specific to unit tests.
"""
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from backend_service.src.main import app
from db_module import schemas

@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return MagicMock()

@pytest.fixture
def mock_user():
    """Create a mock user."""
    user = MagicMock()
    user.id = 1
    user.email = "test@example.com"
    user.username = "testuser"
    user.hashed_password = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # Hashed version of "Password123"
    user.full_name = "Test User"
    user.is_active = True
    user.is_superuser = False
    return user

@pytest.fixture
def client_with_mocked_db(mock_db):
    """Create a test client with a mocked database."""
    # Override the get_db dependency
    def override_get_db():
        try:
            yield mock_db
        finally:
            pass
    
    # Set the override before creating the client
    app.dependency_overrides["get_db"] = override_get_db
    
    # Create and yield the client
    with TestClient(app) as test_client:
        yield test_client
    
    # Clear the override after the test
    app.dependency_overrides.clear()
