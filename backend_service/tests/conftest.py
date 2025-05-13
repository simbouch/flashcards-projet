"""
Pytest configuration for backend service tests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend_service.src.main import app
from db_module.database import get_db

# Create a test client
@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)

# Use the db_session fixture from db_module
@pytest.fixture
def db_session():
    """Get a test database session."""
    # Import here to avoid circular imports
    from db_module.tests.conftest import db_session as test_db_session
    return next(test_db_session())

# Use the test_user fixture from db_module
@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    # Import here to avoid circular imports
    from db_module.tests.conftest import test_user as conftest_test_user
    return conftest_test_user(db_session)
