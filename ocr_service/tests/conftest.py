# ocr_service/tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import pytesseract
import os
from unittest.mock import Mock, patch

# Mock Redis for testing
@pytest.fixture(autouse=True)
def mock_redis():
    """Mock Redis connection for testing"""
    with patch('redis.Redis') as mock_redis_class:
        mock_redis_instance = Mock()
        mock_redis_class.return_value = mock_redis_instance
        yield mock_redis_instance

# Mock rate limiter for testing
@pytest.fixture(autouse=True)
def mock_limiter():
    """Mock the rate limiter to avoid Redis dependency"""
    with patch('ocr_service.src.main.limiter') as mock_limiter:
        # Make the limiter decorator a no-op
        mock_limiter.limit = lambda *args, **kwargs: lambda func: func
        yield mock_limiter

# Set test environment
@pytest.fixture(autouse=True)
def test_environment():
    """Set environment variables for testing"""
    os.environ['TESTING'] = 'true'
    os.environ['REDIS_URL'] = 'redis://localhost:6379'
    yield
    # Cleanup
    if 'TESTING' in os.environ:
        del os.environ['TESTING']

# 1) TestClient fixture, scope module so we only build it once
@pytest.fixture(scope="module")
def client():
    # Import app after mocking is set up
    from ocr_service.src.main import app
    return TestClient(app)

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
