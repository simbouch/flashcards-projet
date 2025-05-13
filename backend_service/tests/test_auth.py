"""
Tests for authentication endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from db_module import crud, models, schemas
from db_module.database import get_db
from backend_service.src.main import app
from backend_service.src.config import settings

# Create a test client
client = TestClient(app)

# Override the dependency to use the test database
@pytest.fixture
def db_override(monkeypatch):
    """Override the database dependency."""
    # Import here to avoid circular imports
    from db_module.tests.conftest import db_session as test_db_session

    # Override the get_db dependency
    def override_get_db():
        try:
            db = next(test_db_session())
            yield db
        finally:
            db.close()

    monkeypatch.setattr("db_module.database.get_db", override_get_db)

    # Don't return anything, this fixture just sets up the override

@pytest.fixture
def test_db():
    """Get a test database session."""
    from db_module.tests.conftest import db_session as test_db_session
    return next(test_db_session())

@pytest.fixture
def test_user(test_db):
    """Create a test user."""
    # Import here to avoid circular imports
    from db_module.tests.conftest import test_user as conftest_test_user
    return conftest_test_user(test_db)

@pytest.fixture
def test_refresh_token(test_db, test_user):
    """Create a test refresh token."""
    # Import here to avoid circular imports
    from db_module.tests.conftest import test_refresh_token as conftest_test_refresh_token
    return conftest_test_refresh_token(test_db, test_user)

def test_login(db_override, test_user):
    """Test login endpoint."""
    # Test with correct credentials
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.username,
            "password": "Password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    # Test with incorrect password
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.username,
            "password": "WrongPassword"
        }
    )
    assert response.status_code == 401

    # Test with non-existent username
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistentuser",
            "password": "Password123"
        }
    )
    assert response.status_code == 401

def test_refresh_token(db_override, test_refresh_token, test_db):
    """Test refresh token endpoint."""
    # Test with valid refresh token
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": test_refresh_token.token}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    # Verify old token is revoked
    db_token = crud.get_refresh_token(test_db, test_refresh_token.token)
    assert db_token.revoked is True

    # Test with revoked token
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": test_refresh_token.token}
    )
    assert response.status_code == 401

    # Test with non-existent token
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "nonexistenttoken"}
    )
    assert response.status_code == 401

def test_logout(db_override, test_refresh_token, test_db):
    """Test logout endpoint."""
    # Test with valid refresh token
    response = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": test_refresh_token.token}
    )
    assert response.status_code == 204

    # Verify token is revoked
    db_token = crud.get_refresh_token(test_db, test_refresh_token.token)
    assert db_token.revoked is True

    # Test with already revoked token
    response = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": test_refresh_token.token}
    )
    assert response.status_code == 204  # Should still return 204 even if token is already revoked

    # Test with non-existent token
    response = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": "nonexistenttoken"}
    )
    assert response.status_code == 204  # Should still return 204 even if token doesn't exist
