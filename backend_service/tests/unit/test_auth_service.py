"""
Unit tests for the authentication service.
These tests use mocks to isolate the authentication service from its dependencies.
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from jose import jwt

from backend_service.src.auth.jwt import create_access_token
from backend_service.src.config import settings
from db_module import crud, schemas

@pytest.mark.auth
def test_create_access_token():
    """Test creating an access token."""
    # Arrange
    user_id = 1
    expires_delta = timedelta(minutes=15)

    # Act
    token = create_access_token({"sub": str(user_id)}, expires_delta)

    # Assert
    assert token is not None
    assert isinstance(token, str)

@pytest.mark.auth
def test_decode_token():
    """Test decoding an access token."""
    # Arrange
    user_id = 1
    expires_delta = timedelta(minutes=15)
    token = create_access_token({"sub": str(user_id)}, expires_delta)

    # Act
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM]
    )

    # Assert
    assert payload is not None
    assert payload.get("sub") == str(user_id)

@pytest.mark.auth
def test_password_hashing():
    """Test password hashing and verification."""
    # Arrange
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    plain_password = "Password123"

    # Act
    hashed_password = pwd_context.hash(plain_password)
    result = pwd_context.verify(plain_password, hashed_password)

    # Assert
    assert result is True

@pytest.mark.auth
@patch("db_module.crud.get_user_by_username")
@patch("db_module.crud.verify_password")
def test_authenticate_user(mock_verify, mock_get_user):
    """Test authenticating a user with mocked database."""
    # Arrange
    username = "testuser"
    password = "Password123"

    # Mock the user
    mock_user = MagicMock()
    mock_user.hashed_password = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # Hashed version of "Password123"
    mock_user.is_active = True

    # Configure the mocks
    mock_get_user.return_value = mock_user
    mock_verify.return_value = True

    # Act
    from db_module.crud import authenticate_user
    db = MagicMock()
    user = authenticate_user(db, username, password)

    # Assert
    assert user is not None
    mock_get_user.assert_called_once_with(db, username)
    mock_verify.assert_called_once_with(password, mock_user.hashed_password)
