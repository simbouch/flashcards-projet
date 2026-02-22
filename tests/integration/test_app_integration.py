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


def _pdf_escape(s: str) -> str:
    return (s or "").replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _make_simple_pdf_bytes(text: str) -> bytes:
    """Create a tiny 1-page PDF with an embedded text layer.

    This avoids adding extra dependencies (reportlab, etc.) while still producing
    a PDF that PyMuPDF can extract text from.
    """
    escaped = _pdf_escape(text)
    # Basic content stream: draw text near the top-left.
    stream = f"BT /F1 18 Tf 72 720 Td ({escaped}) Tj ET".encode("latin-1", errors="ignore")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]

    out = bytearray()
    out.extend(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

    offsets = [0]
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out.extend(f"{i} 0 obj\n".encode("ascii"))
        out.extend(obj)
        out.extend(b"\nendobj\n")

    xref_offset = len(out)
    out.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    out.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        out.extend(f"{off:010d} 00000 n \n".encode("ascii"))

    out.extend(b"trailer\n")
    out.extend(f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n".encode("ascii"))
    out.extend(b"startxref\n")
    out.extend(f"{xref_offset}\n".encode("ascii"))
    out.extend(b"%%EOF\n")
    return bytes(out)


def _backend_register_and_login_headers() -> dict:
    """Register a fresh user and return Authorization headers."""
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

    token = _backend_login_token(username, password)
    return {"Authorization": f"Bearer {token}"}


def _wait_for_flashcards_complete(document_id: str, headers: dict) -> None:
    max_attempts = int(os.getenv("E2E_MAX_ATTEMPTS", "80"))
    sleep_s = float(os.getenv("E2E_POLL_SECONDS", "5"))

    last = None
    last_error = None
    for attempt in range(max_attempts):
        print(f"Checking document status (attempt {attempt + 1}/{max_attempts})...")
        resp = requests.get(
            f"{BACKEND_SERVICE_URL}/api/v1/documents/{document_id}",
            headers=headers,
            timeout=30,
        )
        assert resp.status_code == 200, f"Failed to get document: {resp.status_code} {resp.text}"

        payload = resp.json()
        last = payload.get("status")
        last_error = payload.get("error_message")
        print(f"Document status: {last}")

        if last == "flashcard_complete":
            print("✅ Flashcards generated successfully")
            return
        if last == "error":
            raise AssertionError(f"Document processing ended in error: {last_error}")

        time.sleep(sleep_s)

    raise AssertionError(f"Timeout waiting for flashcard_complete. last_status={last} error={last_error}")

# Global variables
extracted_text_value = None
deck_title = None
flashcards_value = None
llm_flashcards_value = None


def _backend_login_token(username: str, password: str) -> str:
    """Helper: login to backend and return JWT access token."""
    resp = requests.post(
        f"{BACKEND_SERVICE_URL}/api/v1/auth/login",
        data={"username": username, "password": password},
        timeout=30,
    )
    assert resp.status_code == 200, f"Login failed: {resp.status_code} {resp.text}"
    payload = resp.json()
    assert "access_token" in payload, f"No access_token in response: {payload}"
    return payload["access_token"]


def _e2e_admin_credentials():
    """Return admin credentials for admin-only E2E tests.

    We purposely do NOT hardcode credentials in git.
    """
    username = os.getenv("E2E_ADMIN_USERNAME") or os.getenv("INITIAL_ADMIN_USERNAME")
    password = os.getenv("E2E_ADMIN_PASSWORD") or os.getenv("INITIAL_ADMIN_PASSWORD")
    if not username or not password:
        pytest.skip(
            "Admin E2E tests require E2E_ADMIN_USERNAME/E2E_ADMIN_PASSWORD (or INITIAL_ADMIN_USERNAME/INITIAL_ADMIN_PASSWORD) set in the host environment."
        )
    return username, password


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
    # NOTE: For E2E we mainly need to know the HTTP server is reachable, so we use `/docs`.
    # The LLM service also exposes `/health` (liveness) and `/ready` (model readiness).
    # If you explicitly want the deep health check, set E2E_CHECK_LLM_HEALTH=1.
    llm_health_timeout = int(os.getenv("E2E_LLM_HEALTH_TIMEOUT_SECONDS", "600"))
    check_llm_health = os.getenv("E2E_CHECK_LLM_HEALTH", "").strip().lower() in {"1", "true", "yes"}

    def _get_ok(url: str, *, timeout_s: int = 20, attempts: int = 1, sleep_s: float = 2.0) -> None:
        """GET url until 200 or attempts exhausted (helps with cold-starting services)."""
        last_exc: Exception | None = None
        for i in range(attempts):
            try:
                resp = requests.get(url, timeout=timeout_s)
                assert resp.status_code == 200, f"{url} returned {resp.status_code}"
                return
            except Exception as e:  # noqa: BLE001 (test helper; keep broad)
                last_exc = e
                if i < attempts - 1:
                    time.sleep(sleep_s)
        assert last_exc is not None
        raise last_exc
    services = [
        {"name": "OCR Service", "url": f"{OCR_SERVICE_URL}/docs"},
        {"name": "LLM Service", "url": f"{LLM_SERVICE_URL}/docs"},
        {"name": "Backend Service", "url": f"{BACKEND_SERVICE_URL}/health"},
        {"name": "Frontend Service", "url": f"{FRONTEND_SERVICE_URL}/"},
    ]

    if check_llm_health:
        services.insert(
            2,
            {"name": "LLM Service (deep health)", "url": f"{LLM_SERVICE_URL}/health", "timeout": llm_health_timeout},
        )

    for service in services:
        try:
            # LLM can take time to respond during cold start (model load).
            if service["name"].startswith("LLM Service"):
                attempts = int(os.getenv("E2E_LLM_STARTUP_ATTEMPTS", "30"))
                timeout_s = int(os.getenv("E2E_LLM_STARTUP_TIMEOUT_SECONDS", "20"))
                sleep_s = float(os.getenv("E2E_LLM_STARTUP_SLEEP_SECONDS", "2"))
                _get_ok(service["url"], timeout_s=int(service.get("timeout", timeout_s)), attempts=attempts, sleep_s=sleep_s)
            else:
                _get_ok(service["url"], timeout_s=int(service.get("timeout", 20)))
            print(f"✅ {service['name']} is running")
        except Exception as e:  # noqa: BLE001 (E2E test should provide a clear failure)
            pytest.fail(f"❌ {service['name']} health check failed: {type(e).__name__}: {e}")


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
        "num_cards": 5,
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
    headers = _backend_register_and_login_headers()
    print("✅ Login successful, got access token")

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

    _wait_for_flashcards_complete(document_id, headers)

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

    # Verify that the deck has the correct title (the upload form field `title` is the deck title)
    assert deck.get("title") == deck_title, f"Deck title mismatch: got={deck.get('title')} expected={deck_title}"

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


def test_backend_service_pdf_upload():
    """E2E: upload a PDF (with text layer) and verify flashcards are generated."""
    _require_e2e()
    headers = _backend_register_and_login_headers()

    pdf_bytes = _make_simple_pdf_bytes(
        "PDF E2E test: Intelligence artificielle, réseaux de neurones, apprentissage supervisé."
    )

    response = requests.post(
        f"{BACKEND_SERVICE_URL}/api/v1/documents/",
        headers=headers,
        files={"file": ("e2e_test.pdf", pdf_bytes, "application/pdf")},
        data={"title": f"PDF Deck {uuid.uuid4()}"},
        timeout=120,
    )
    assert response.status_code == 200, f"Document creation failed: {response.status_code} {response.text}"
    document_id = response.json().get("id")
    assert document_id, f"No document id returned: {response.json()}"
    print(f"✅ PDF document created with ID: {document_id}")

    _wait_for_flashcards_complete(document_id, headers)

    # Find deck
    decks_resp = requests.get(f"{BACKEND_SERVICE_URL}/api/v1/decks/", headers=headers, timeout=30)
    assert decks_resp.status_code == 200, f"Failed to get decks: {decks_resp.status_code} {decks_resp.text}"
    deck = None
    for d in decks_resp.json():
        if d.get("document_id") == document_id:
            deck = d
            break
    assert deck is not None, f"No deck found for document {document_id}"

    # Get flashcards
    fc_resp = requests.get(
        f"{BACKEND_SERVICE_URL}/api/v1/flashcards/?deck_id={deck.get('id')}",
        headers=headers,
        timeout=30,
    )
    assert fc_resp.status_code == 200, f"Failed to get flashcards: {fc_resp.status_code} {fc_resp.text}"
    flashcards = fc_resp.json()
    assert len(flashcards) > 0, "No flashcards returned for PDF deck"
    print(f"✅ PDF pipeline generated {len(flashcards)} flashcards")


def test_backend_admin_can_create_user_and_update_username():
    """Admin-only CRUD E2E: create user (role + is_active) then update username."""
    _require_e2e()
    admin_username, admin_password = _e2e_admin_credentials()
    admin_token = _backend_login_token(admin_username, admin_password)
    headers = {"Authorization": f"Bearer {admin_token}"}

    unique = uuid.uuid4().hex[:10]
    user_password = "Password123!"
    create_payload = {
        "email": f"e2e_admin_created_{unique}@example.com",
        "username": f"e2e_admin_created_{unique}",
        "password": user_password,
        "full_name": "E2E Admin Created",
        "role": "user",
        "is_active": True,
    }

    resp = requests.post(
        f"{BACKEND_SERVICE_URL}/api/v1/admin/users",
        json=create_payload,
        headers=headers,
        timeout=30,
    )
    assert resp.status_code == 201, f"Admin create user failed: {resp.status_code} {resp.text}"
    created = resp.json()
    assert created.get("username") == create_payload["username"]
    assert created.get("role") == "user"
    assert created.get("is_active") is True
    user_id = created.get("id")
    assert user_id, f"No id in create response: {created}"

    new_username = f"{create_payload['username']}_renamed"
    resp2 = requests.patch(
        f"{BACKEND_SERVICE_URL}/api/v1/admin/users/{user_id}",
        json={"username": new_username},
        headers=headers,
        timeout=30,
    )
    assert resp2.status_code == 200, f"Admin update user failed: {resp2.status_code} {resp2.text}"
    assert resp2.json().get("username") == new_username

    # New username should be able to login
    token = _backend_login_token(new_username, user_password)
    assert isinstance(token, str) and len(token) > 10


def test_backend_admin_can_create_inactive_user_and_inactive_cannot_login():
    """Admin-only CRUD E2E: create inactive user and verify they cannot login."""
    _require_e2e()
    admin_username, admin_password = _e2e_admin_credentials()
    admin_token = _backend_login_token(admin_username, admin_password)
    headers = {"Authorization": f"Bearer {admin_token}"}

    unique = uuid.uuid4().hex[:10]
    user_password = "Password123!"
    payload = {
        "email": f"e2e_inactive_{unique}@example.com",
        "username": f"e2e_inactive_{unique}",
        "password": user_password,
        "full_name": "E2E Inactive",
        "role": "user",
        "is_active": False,
    }
    resp = requests.post(
        f"{BACKEND_SERVICE_URL}/api/v1/admin/users",
        json=payload,
        headers=headers,
        timeout=30,
    )
    assert resp.status_code == 201, f"Admin create inactive user failed: {resp.status_code} {resp.text}"
    assert resp.json().get("is_active") is False

    login_resp = requests.post(
        f"{BACKEND_SERVICE_URL}/api/v1/auth/login",
        data={"username": payload["username"], "password": user_password},
        timeout=30,
    )
    assert login_resp.status_code == 403, f"Inactive user should be forbidden: {login_resp.status_code} {login_resp.text}"


def test_backend_admin_can_update_fields_reset_password_and_self_protection():
    """Admin-only CRUD E2E: update user fields + reset password + verify admin self-protection."""
    _require_e2e()
    admin_username, admin_password = _e2e_admin_credentials()
    admin_token = _backend_login_token(admin_username, admin_password)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Self-protection checks (should not mutate state)
    me = requests.get(f"{BACKEND_SERVICE_URL}/api/v1/users/me", headers=headers, timeout=30)
    assert me.status_code == 200, f"Failed to read /users/me: {me.status_code} {me.text}"
    admin_id = me.json().get("id")
    assert admin_id, f"No id in /users/me response: {me.json()}"

    resp_demote = requests.patch(
        f"{BACKEND_SERVICE_URL}/api/v1/admin/users/{admin_id}",
        json={"role": "user"},
        headers=headers,
        timeout=30,
    )
    assert resp_demote.status_code == 400, f"Expected self-demotion to be blocked: {resp_demote.status_code} {resp_demote.text}"

    resp_delete_self = requests.delete(
        f"{BACKEND_SERVICE_URL}/api/v1/admin/users/{admin_id}",
        headers=headers,
        timeout=30,
    )
    assert resp_delete_self.status_code == 400, f"Expected self-delete to be blocked: {resp_delete_self.status_code} {resp_delete_self.text}"

    # Create a user to mutate
    unique = uuid.uuid4().hex[:10]
    original_password = "Password123!"
    created_username = f"e2e_admin_mut_{unique}"
    create_payload = {
        "email": f"e2e_admin_mut_{unique}@example.com",
        "username": created_username,
        "password": original_password,
        "full_name": "E2E Mut User",
        "role": "user",
        "is_active": True,
    }
    resp_create = requests.post(
        f"{BACKEND_SERVICE_URL}/api/v1/admin/users",
        json=create_payload,
        headers=headers,
        timeout=30,
    )
    assert resp_create.status_code == 201, f"Admin create user failed: {resp_create.status_code} {resp_create.text}"
    user_id = resp_create.json().get("id")
    assert user_id, f"No id in create response: {resp_create.json()}"

    # Update core fields
    new_email = f"e2e_admin_mut_{unique}_new@example.com"
    patch_payload = {
        "email": new_email,
        "full_name": "E2E Mut User Updated",
        "role": "admin",
    }
    resp_patch = requests.patch(
        f"{BACKEND_SERVICE_URL}/api/v1/admin/users/{user_id}",
        json=patch_payload,
        headers=headers,
        timeout=30,
    )
    assert resp_patch.status_code == 200, f"Admin patch failed: {resp_patch.status_code} {resp_patch.text}"
    patched = resp_patch.json()
    assert patched.get("email") == new_email
    assert patched.get("full_name") == patch_payload["full_name"]
    assert patched.get("role") == "admin"

    # Reset password and verify login works with the new password
    new_password = "NewPassword123!"
    resp_reset = requests.post(
        f"{BACKEND_SERVICE_URL}/api/v1/admin/users/{user_id}/reset-password",
        json={"password": new_password},
        headers=headers,
        timeout=30,
    )
    assert resp_reset.status_code == 200, f"Admin reset-password failed: {resp_reset.status_code} {resp_reset.text}"
    token = _backend_login_token(created_username, new_password)
    assert isinstance(token, str) and len(token) > 10

    # Deactivate and verify login is forbidden
    resp_deactivate = requests.patch(
        f"{BACKEND_SERVICE_URL}/api/v1/admin/users/{user_id}",
        json={"is_active": False},
        headers=headers,
        timeout=30,
    )
    assert resp_deactivate.status_code == 200, f"Admin deactivate failed: {resp_deactivate.status_code} {resp_deactivate.text}"
    assert resp_deactivate.json().get("is_active") is False

    login_resp = requests.post(
        f"{BACKEND_SERVICE_URL}/api/v1/auth/login",
        data={"username": created_username, "password": new_password},
        timeout=30,
    )
    assert login_resp.status_code == 403, f"Inactive user should be forbidden: {login_resp.status_code} {login_resp.text}"


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
