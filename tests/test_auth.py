"""
Tests for authentication endpoints.

Note: These tests are duplicated in backend_service/tests/test_auth.py.
This file is kept for backward compatibility and will be removed in a future version.
Please use the tests in backend_service/tests/test_auth.py instead.
"""
import pytest
from fastapi.testclient import TestClient

from db_module import crud
from backend_service.src.main import app

# Mark these tests as deprecated
pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")

def test_login(client, db_session, test_user):
    """Test login endpoint."""
    # This test is deprecated. Use backend_service/tests/test_auth.py instead.
    pass

def test_refresh_token_endpoint(client, db_session, test_refresh_token):
    """Test refresh token endpoint."""
    # This test is deprecated. Use backend_service/tests/test_auth.py instead.
    pass

def test_logout(client, db_session, test_refresh_token):
    """Test logout endpoint."""
    # This test is deprecated. Use backend_service/tests/test_auth.py instead.
    pass
