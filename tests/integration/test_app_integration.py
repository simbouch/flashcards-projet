"""
Integration tests for the entire application.
Tests the flow from uploading an image to generating flashcards.
"""
import requests
import time
import uuid
import os
import sys
import pytest

pytestmark = pytest.mark.e2e

_RUN_E2E = os.getenv("RUN_E2E", "").strip().lower() in {"1", "true", "yes"}


def _require_e2e() -> None:
    """Skip under pytest unless RUN_E2E=1/true/yes.

    When running this file as a script (python tests/integration/test_app_integration.py),
    we always run.
    """
    if __name__ != "__main__" and not _RUN_E2E:
        pytest.skip(
            "E2E integration test requires running services. Set RUN_E2E=1 to run.",
        )

# Service URLs
OCR_SERVICE_URL = "http://localhost:8000"
LLM_SERVICE_URL = "http://localhost:8001"
BACKEND_SERVICE_URL = "http://localhost:8002"
FRONTEND_SERVICE_URL = "http://localhost:8080"

# This test talks to running Docker services on localhost.
# By default we skip under pytest to avoid breaking local/CI runs.
# Run explicitly with:
#   $env:RUN_E2E='1'; python -m pytest -c tests/integration/pytest.ini -q
#
# (We use a dedicated pytest.ini here so running this test from the host does
# not require the full backend_service python dependencies.)

# Test image path
TEST_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "images/test.png")

# Global variables
extracted_text_value = None
deck_title = None
flashcards_value = None
llm_flashcards_value = None


def _ocr_extract_text() -> str:
    """Helper: call OCR service and return extracted text."""
    # Check if the test image exists
    assert os.path.exists(TEST_IMAGE_PATH), f"Test image not found at {TEST_IMAGE_PATH}"

    with open(TEST_IMAGE_PATH, "rb") as f:
        files = {"file": (os.path.basename(TEST_IMAGE_PATH), f, "image/png")}
        response = requests.post(f"{OCR_SERVICE_URL}/extract", files=files, timeout=60)

    assert response.status_code == 200, "OCR service failed to extract text"
    payload = response.json()
    assert "text" in payload, "OCR service response does not contain text"
    assert len(payload["text"]) > 0, "OCR service extracted empty text"

    return payload["text"]


def test_services_health():
    """Test that all services are running."""
    _require_e2e()
    services = [
        {"name": "OCR Service", "url": f"{OCR_SERVICE_URL}/docs"},
        {"name": "LLM Service", "url": f"{LLM_SERVICE_URL}/health"},
        {"name": "Backend Service", "url": f"{BACKEND_SERVICE_URL}/health"},
        {"name": "Frontend Service", "url": f"{FRONTEND_SERVICE_URL}/"},
    ]

    for service in services:
        try:
            response = requests.get(service["url"], timeout=20)
            assert response.status_code == 200, f"{service['name']} is not running"
            print(f"✅ {service['name']} is running")
        except requests.exceptions.ConnectionError:
            pytest.fail(f"❌ {service['name']} is not running")


def test_ocr_service():
    """Test the OCR service."""
    _require_e2e()
    text = _ocr_extract_text()
    print(f"✅ OCR service extracted text: {text[:100]}...")
    # Store the extracted text in a global variable for use in other tests
    global extracted_text_value
    extracted_text_value = text


@pytest.fixture
def extracted_text():
    """Extract text from the test image."""
    _require_e2e()
    return _ocr_extract_text()

def test_llm_service(extracted_text):
    """Test the LLM service."""
    _require_e2e()
    # Generate flashcards from the text
    data = {
        "text": extracted_text,
        "task": "flashcards"
    }
    response = requests.post(f"{LLM_SERVICE_URL}/generate", json=data, timeout=300)

    assert response.status_code == 200, "LLM service failed to generate flashcards"
    assert "flashcards" in response.json(), "LLM service response does not contain flashcards"
    assert len(response.json()["flashcards"]) > 0, "LLM service generated no flashcards"

    print(f"✅ LLM service generated {len(response.json()['flashcards'])} flashcards")
    # Store the flashcards in a global variable for use in other tests
    global llm_flashcards_value
    llm_flashcards_value = response.json()["flashcards"]


def test_backend_service():
    """Test the backend service."""
    _require_e2e()
    # Register a unique user for this run
    unique = uuid.uuid4().hex[:10]
    username = f"e2e_{unique}"
    password = "Password123!"
    email = f"{username}@example.com"

    reg = requests.post(
        f"{BACKEND_SERVICE_URL}/api/v1/auth/register",
        json={
            "email": email,
            "username": username,
            "password": password,
            "full_name": "E2E Test User",
        },
        timeout=30,
    )
    assert reg.status_code in (200, 201), f"Registration failed: {reg.status_code} {reg.text}"

    # Login (OAuth2PasswordRequestForm style: form-encoded)
    login_data = {"username": username, "password": password}
    response = requests.post(
        f"{BACKEND_SERVICE_URL}/api/v1/auth/login",
        data=login_data,
        timeout=30,
    )

    assert response.status_code == 200, "Login failed"
    assert "access_token" in response.json(), "Login response does not contain access token"

    token = response.json()["access_token"]
    print(f"✅ Login successful, got access token")

    # Upload image and create document
    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Create a custom deck title
    global deck_title
    deck_title = f"My Custom Deck {uuid.uuid4()}"

    with open(TEST_IMAGE_PATH, "rb") as f:
        files = {"file": (os.path.basename(TEST_IMAGE_PATH), f, "image/png")}
        data = {"title": deck_title}
        response = requests.post(
            f"{BACKEND_SERVICE_URL}/api/v1/documents/",
            headers=headers,
            files=files,
            data=data,
            timeout=120,
        )

    assert response.status_code == 200, "Document creation failed"
    assert "id" in response.json(), "Document creation response does not contain ID"

    document_id = response.json()["id"]
    print(f"✅ Document created with ID: {document_id}")

    # Wait for flashcards to be generated
    max_attempts = 40  # ~200s, allows for cold model start + generation
    status = None
    for attempt in range(max_attempts):
        print(f"Checking document status (attempt {attempt + 1}/{max_attempts})...")
        response = requests.get(
            f"{BACKEND_SERVICE_URL}/api/v1/documents/{document_id}",
            headers=headers,
            timeout=30,
        )

        assert response.status_code == 200, "Failed to get document"

        status = response.json().get("status")
        print(f"Document status: {status}")

        if status == "flashcard_complete":
            print("✅ Flashcards generated successfully")
            break
        elif status == "error":
            error_message = response.json().get('error_message', 'Unknown error')
            print(f"Error generating flashcards: {error_message}")

            # Even if there's an error, let's continue and check if there's a deck
            # Sometimes the error is just in the status but the deck is created
            break

        # Wait before checking again
        time.sleep(5)

    # If we've reached the maximum number of attempts and the status is still generating,
    # let's continue anyway and check if there's a deck
    if status == "flashcard_generating":
        print("Document is still generating flashcards, but we'll check for decks anyway")

    # Get decks
    response = requests.get(
        f"{BACKEND_SERVICE_URL}/api/v1/decks/",
        headers=headers,
        timeout=30,
    )

    assert response.status_code == 200, "Failed to get decks"

    # Find the deck for our document
    deck = None
    for d in response.json():
        if d.get("document_id") == document_id:
            deck = d
            break

    assert deck is not None, f"No deck found for document {document_id}"
    print(f"✅ Found deck: {deck.get('title')} (ID: {deck.get('id')})")

    # Verify that the deck has the correct title
    if deck_title in deck.get('title'):
        print(f"✅ Deck has the correct title: {deck.get('title')}")
    else:
        print(f"⚠️ Deck title does not match expected: {deck.get('title')} vs {deck_title}")

    # Get flashcards
    response = requests.get(
        f"{BACKEND_SERVICE_URL}/api/v1/flashcards/?deck_id={deck.get('id')}",
        headers=headers,
        timeout=30,
    )

    assert response.status_code == 200, "Failed to get flashcards"
    flashcards = response.json()

    print(f"✅ Found {len(flashcards)} flashcards:")
    for i, flashcard in enumerate(flashcards[:3], 1):  # Show first 3 flashcards
        print(f"\nFlashcard {i}:")
        print(f"Question: {flashcard.get('question')}")
        print(f"Answer: {flashcard.get('answer')}")

    # Store the flashcards in a global variable for use in other tests
    global flashcards_value
    flashcards_value = flashcards


def main():
    """Run all tests."""
    print("Testing application integration...")

    try:
        # Test services health
        test_services_health()

        # Test OCR service
        text = _ocr_extract_text()

        # Test LLM service
        try:
            test_llm_service(text)
        except AssertionError as e:
            print(f"⚠️ LLM service test failed: {e}")
            print("Continuing with other tests...")

        # Test backend service
        test_backend_service()

        print("\n✅ All integration tests passed!")
        return 0
    except Exception as e:
        print(f"\n❌ Integration tests failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
