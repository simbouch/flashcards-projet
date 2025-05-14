"""
Tests for authentication endpoints.
"""
import pytest
from fastapi.testclient import TestClient

from db_module import crud
from src.main import app

# Create a test client
client = TestClient(app)

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

def test_refresh_token_endpoint(db_override, test_refresh_token, test_db):
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
