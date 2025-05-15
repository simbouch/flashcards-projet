"""
Tests for refresh token functionality.

Note: These tests are duplicated in backend_service/tests/test_refresh_token.py.
This file is kept for backward compatibility and will be removed in a future version.
Please use the tests in backend_service/tests/test_refresh_token.py instead.
"""
import pytest
from datetime import datetime, timedelta

from db_module import crud, schemas

# Mark these tests as deprecated
pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")

def test_create_refresh_token(db_session, test_user):
    """Test creating a refresh token."""
    # This test is deprecated. Use backend_service/tests/test_refresh_token.py instead.
    pass

def test_validate_refresh_token(db_session, test_user, test_refresh_token):
    """Test validating a refresh token."""
    # This test is deprecated. Use backend_service/tests/test_refresh_token.py instead.
    pass

def test_revoke_refresh_token(db_session, test_refresh_token):
    """Test revoking a refresh token."""
    # This test is deprecated. Use backend_service/tests/test_refresh_token.py instead.
    pass

def test_rotate_refresh_token(db_session, test_user):
    """Test rotating a refresh token."""
    # This test is deprecated. Use backend_service/tests/test_refresh_token.py instead.
    pass
