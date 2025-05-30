"""
Tests for refresh token functionality.
"""
import pytest
from datetime import datetime, timedelta

from db_module import crud, schemas

# Mark all tests in this file as auth tests
pytestmark = [pytest.mark.auth, pytest.mark.integration]

# Note: We're using the fixtures from conftest.py instead of defining our own
# This ensures consistent test database setup across all tests

def test_create_refresh_token(db_session, test_user):
    """Test creating a refresh token."""
    # Create a refresh token with default expiration
    refresh_token = crud.create_refresh_token(db_session, test_user.id)
    assert refresh_token is not None
    assert refresh_token.user_id == test_user.id
    assert refresh_token.revoked is False

    # Create a refresh token with custom expiration
    custom_expires = timedelta(days=60)
    refresh_token = crud.create_refresh_token(db_session, test_user.id, custom_expires)
    assert refresh_token is not None

    # Verify token was stored in the database
    token = crud.get_refresh_token(db_session, refresh_token.token)
    assert token is not None
    assert token.id == refresh_token.id

def test_validate_refresh_token(db_session, test_user, test_refresh_token):
    """Test validating a refresh token."""
    # Test with valid token
    user = crud.validate_refresh_token(db_session, test_refresh_token.token)
    assert user is not None
    assert user.id == test_user.id

    # Test with non-existent token
    user = crud.validate_refresh_token(db_session, "nonexistenttoken")
    assert user is None

    # Test with revoked token
    test_refresh_token.revoked = True
    db_session.commit()
    user = crud.validate_refresh_token(db_session, test_refresh_token.token)
    assert user is None

    # Reset for other tests
    test_refresh_token.revoked = False
    db_session.commit()

    # Test with expired token
    test_refresh_token.expires_at = datetime.now() - timedelta(days=1)
    db_session.commit()
    user = crud.validate_refresh_token(db_session, test_refresh_token.token)
    assert user is None

    # Reset for other tests
    test_refresh_token.expires_at = datetime.now() + timedelta(days=30)
    db_session.commit()

    # Test with inactive user
    test_user.is_active = False
    db_session.commit()
    user = crud.validate_refresh_token(db_session, test_refresh_token.token)
    assert user is None

    # Reset for other tests
    test_user.is_active = True
    db_session.commit()

def test_revoke_refresh_token(db_session, test_refresh_token):
    """Test revoking a refresh token."""
    # Test with existing token
    result = crud.revoke_refresh_token(db_session, test_refresh_token.token)
    assert result is True

    # Verify token is revoked
    token = crud.get_refresh_token(db_session, test_refresh_token.token)
    assert token.revoked is True

    # Test with non-existent token
    result = crud.revoke_refresh_token(db_session, "nonexistenttoken")
    assert result is False

def test_rotate_refresh_token(db_session, test_user):
    """Test rotating a refresh token."""
    # Create a token to rotate
    refresh_token = crud.create_refresh_token(db_session, test_user.id)

    # Test with valid token
    new_token = crud.rotate_refresh_token(db_session, refresh_token.token)
    assert new_token is not None
    assert new_token.id != refresh_token.id
    assert new_token.user_id == refresh_token.user_id

    # Verify old token is revoked
    old_token = crud.get_refresh_token(db_session, refresh_token.token)
    assert old_token.revoked is True

    # Test with revoked token
    result = crud.rotate_refresh_token(db_session, refresh_token.token)
    assert result is None

    # Test with non-existent token
    result = crud.rotate_refresh_token(db_session, "nonexistenttoken")
    assert result is None
