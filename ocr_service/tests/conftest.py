# ocr_service/tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import pytesseract
import os
from unittest.mock import Mock, patch

# Set testing environment before importing app
os.environ['TESTING'] = 'true'
os.environ['REDIS_URL'] = 'memory://'

# Mock Redis for testing
@pytest.fixture(autouse=True)
def mock_redis():
    """Mock Redis connection for testing"""
    with patch('redis.Redis') as mock_redis_class:
        mock_redis_instance = Mock()
        mock_redis_class.return_value = mock_redis_instance
        yield mock_redis_instance

# Mock rate limiter for testing - more comprehensive approach
@pytest.fixture(autouse=True)
def mock_limiter():
    """Mock the rate limiter to avoid Redis dependency"""
    # Patch the actual limiter instance that gets created
    with patch('slowapi.Limiter') as mock_limiter_class, \
         patch('slowapi.extension.Limiter') as mock_ext_limiter:

        mock_limiter_instance = Mock()
        # Make limit method return a no-op decorator
        mock_limiter_instance.limit = lambda *args, **kwargs: lambda func: func
        mock_limiter_instance.hit = lambda *args, **kwargs: True
        mock_limiter_instance.test = lambda *args, **kwargs: True

        mock_limiter_class.return_value = mock_limiter_instance
        mock_ext_limiter.return_value = mock_limiter_instance

        yield mock_limiter_instance

# 1) TestClient fixture, scope module so we only build it once
@pytest.fixture(scope="module")
def client():
    # Import app after mocking is set up
    import sys
    from pathlib import Path

    # Add current directory to Python path for Docker environment
    current_dir = Path(__file__).parent.parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))

    try:
        # Try Docker/CI path first
        from src.main import app, limiter
    except ImportError:
        try:
            # Fallback to local development path
            from ocr_service.src.main import app, limiter
        except ImportError:
            # Last resort - add parent directory and try again
            parent_dir = current_dir.parent
            if str(parent_dir) not in sys.path:
                sys.path.insert(0, str(parent_dir))
            from ocr_service.src.main import app, limiter

    # Patch the limiter instance directly
    original_limit = limiter.limit
    limiter.limit = lambda *args, **kwargs: lambda func: func

    client = TestClient(app)

    # Restore after tests (though this won't be called in module scope)
    # limiter.limit = original_limit

    return client

# 2) Autouse fixture to patch out real OCR: always return a dummy text
@pytest.fixture(autouse=True)
def mock_tesseract(monkeypatch):
    """
    Replace pytesseract functions with stubs that return fixed data.
    """
    # Mock image_to_string
    monkeypatch.setattr(
        pytesseract,
        "image_to_string",
        lambda image, lang=None: "texte factice OCR"
    )

    # Mock image_to_data for confidence testing
    mock_data = {
        'text': ['texte', 'factice', 'OCR'],
        'conf': [95, 90, 85]
    }
    monkeypatch.setattr(
        pytesseract,
        "image_to_data",
        lambda image, output_type=None, lang=None: mock_data
    )

# 3) img_bytes fixture unchanged: reads your test.png
@pytest.fixture
def img_bytes():
    fixtures_dir = Path(__file__).parent / "fixtures"
    return (fixtures_dir / "test.png").read_bytes()
