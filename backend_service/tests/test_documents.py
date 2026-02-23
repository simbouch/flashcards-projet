import pytest


def _login_and_get_token(client, username: str, password: str) -> str:
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": password},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_upload_document_too_large_returns_413(client, test_user, monkeypatch, tmp_path):
    # Make uploads write into a temp dir
    from backend_service.src.config import settings
    monkeypatch.setattr(settings, "UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE", 10)

    token = _login_and_get_token(client, test_user.username, "Password123")

    # 11 bytes > 10
    files = {"file": ("big.png", b"0123456789A", "image/png")}
    resp = client.post(
        "/api/v1/documents",
        files=files,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 413


def test_upload_document_small_file_ok(client, test_user, monkeypatch, tmp_path):
    # Avoid running the real background pipeline in unit tests
    from backend_service.src.api.endpoints import documents as documents_module
    from backend_service.src.config import settings

    monkeypatch.setattr(settings, "UPLOAD_DIR", tmp_path)

    async def _noop_process_document(document_id: str, file_path, deck_title=None, deck_is_public: bool = False):
        return None

    monkeypatch.setattr(documents_module, "process_document", _noop_process_document)

    token = _login_and_get_token(client, test_user.username, "Password123")

    files = {"file": ("small.png", b"hello", "image/png")}
    resp = client.post(
        "/api/v1/documents",
        files=files,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["filename"] == "small.png"
    assert data["status"] is not None


def test_upload_document_passes_title_to_background_task(client, test_user, monkeypatch, tmp_path):
    """Ensure multipart form field 'title' is accepted and passed to the background task."""
    from backend_service.src.api.endpoints import documents as documents_module
    from backend_service.src.config import settings

    monkeypatch.setattr(settings, "UPLOAD_DIR", tmp_path)

    called = {}

    async def _capture_process_document(document_id: str, file_path, deck_title=None, deck_is_public: bool = False):
        called["deck_title"] = deck_title
        return None

    monkeypatch.setattr(documents_module, "process_document", _capture_process_document)

    token = _login_and_get_token(client, test_user.username, "Password123")
    files = {"file": ("small.png", b"hello", "image/png")}
    resp = client.post(
        "/api/v1/documents",
        files=files,
        data={"title": "My Deck Title"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200
    assert called.get("deck_title") == "My Deck Title"


def test_upload_document_passes_is_public_to_background_task(client, test_user, monkeypatch, tmp_path):
    """Ensure multipart form field 'is_public' is accepted and passed to the background task."""
    from backend_service.src.api.endpoints import documents as documents_module
    from backend_service.src.config import settings

    monkeypatch.setattr(settings, "UPLOAD_DIR", tmp_path)

    called = {}

    async def _capture_process_document(document_id: str, file_path, deck_title=None, deck_is_public: bool = False):
        called["deck_is_public"] = deck_is_public
        return None

    monkeypatch.setattr(documents_module, "process_document", _capture_process_document)

    token = _login_and_get_token(client, test_user.username, "Password123")
    files = {"file": ("small.png", b"hello", "image/png")}
    resp = client.post(
        "/api/v1/documents",
        files=files,
        data={"is_public": "true"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200
    assert called.get("deck_is_public") is True
