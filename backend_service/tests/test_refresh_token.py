"""
Tests for refresh token functionality.
"""
import pytest
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from db_module import crud, models, schemas
from db_module.database import get_db

@pytest.fixture
def db():
    """Get a test database session."""
    # Import here to avoid circular imports
    from db_module.tests.conftest import db_session as test_db_session
    yield from test_db_session()

@pytest.fixture
def test_user(db):
    """Create a test user."""
    user_data = schemas.UserCreate(
        email="test@example.com",
        username="testuser",
        password="Password123",
        full_name="Test User"
    )
    
    # Check if user already exists
    existing_user = crud.get_user_by_email(db, user_data.email)
    if existing_user:
        return existing_user
    
    # Create new user
    return crud.create_user(db, user_data)

@pytest.fixture
def test_refresh_token(db, test_user):
    """Create a test refresh token."""
    # Create a refresh token with default expiration
    return crud.create_refresh_token(db, test_user.id)

def test_create_refresh_token(db, test_user):
    """Test creating a refresh token."""
    # Create a refresh token with default expiration
    refresh_token = crud.create_refresh_token(db, test_user.id)
    assert refresh_token is not None
    assert refresh_token.user_id == test_user.id
    assert refresh_token.revoked is False
    
    # Create a refresh token with custom expiration
    custom_expires = timedelta(days=60)
    refresh_token = crud.create_refresh_token(db, test_user.id, custom_expires)
    assert refresh_token is not None
    
    # Verify token was stored in the database
    token = crud.get_refresh_token(db, refresh_token.token)
    assert token is not None
    assert token.id == refresh_token.id

def test_validate_refresh_token(db, test_user, test_refresh_token):
    """Test validating a refresh token."""
    # Test with valid token
    user = crud.validate_refresh_token(db, test_refresh_token.token)
    assert user is not None
    assert user.id == test_user.id
    
    # Test with non-existent token
    user = crud.validate_refresh_token(db, "nonexistenttoken")
    assert user is None
    
    # Test with revoked token
    test_refresh_token.revoked = True
    db.commit()
    user = crud.validate_refresh_token(db, test_refresh_token.token)
    assert user is None
    
    # Reset for other tests
    test_refresh_token.revoked = False
    db.commit()
    
    # Test with expired token
    test_refresh_token.expires_at = datetime.now() - timedelta(days=1)
    db.commit()
    user = crud.validate_refresh_token(db, test_refresh_token.token)
    assert user is None
    
    # Reset for other tests
    test_refresh_token.expires_at = datetime.now() + timedelta(days=30)
    db.commit()
    
    # Test with inactive user
    test_user.is_active = False
    db.commit()
    user = crud.validate_refresh_token(db, test_refresh_token.token)
    assert user is None
    
    # Reset for other tests
    test_user.is_active = True
    db.commit()

def test_revoke_refresh_token(db, test_refresh_token):
    """Test revoking a refresh token."""
    # Test with existing token
    result = crud.revoke_refresh_token(db, test_refresh_token.token)
    assert result is True
    
    # Verify token is revoked
    token = crud.get_refresh_token(db, test_refresh_token.token)
    assert token.revoked is True
    
    # Test with non-existent token
    result = crud.revoke_refresh_token(db, "nonexistenttoken")
    assert result is False

def test_rotate_refresh_token(db, test_user):
    """Test rotating a refresh token."""
    # Create a token to rotate
    refresh_token = crud.create_refresh_token(db, test_user.id)
    
    # Test with valid token
    new_token = crud.rotate_refresh_token(db, refresh_token.token)
    assert new_token is not None
    assert new_token.id != refresh_token.id
    assert new_token.user_id == refresh_token.user_id
    
    # Verify old token is revoked
    old_token = crud.get_refresh_token(db, refresh_token.token)
    assert old_token.revoked is True
    
    # Test with revoked token
    result = crud.rotate_refresh_token(db, refresh_token.token)
    assert result is None
    
    # Test with non-existent token
    result = crud.rotate_refresh_token(db, "nonexistenttoken")
    assert result is None
