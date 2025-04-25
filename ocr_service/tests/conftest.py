# ocr_service/tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from ocr_service.src.main import app
from pathlib import Path
import pytesseract

# 1) TestClient fixture, scope module so we only build it once
@pytest.fixture(scope="module")
def client():
    return TestClient(app)

# 2) Autouse fixture to patch out real OCR: always return a dummy text
@pytest.fixture(autouse=True)
def mock_tesseract(monkeypatch):
    """
    Replace pytesseract.image_to_string with a stub
    that ignores its inputs and returns fixed text.
    """
    monkeypatch.setattr(
        pytesseract,
        "image_to_string",
        lambda image, lang: "texte factice OCR"
    )

# 3) img_bytes fixture unchanged: reads your test.png
@pytest.fixture
def img_bytes():
    fixtures_dir = Path(__file__).parent / "fixtures"
    return (fixtures_dir / "test.png").read_bytes()
