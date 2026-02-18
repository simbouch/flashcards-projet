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

    async def _noop_process_document(document_id: str, file_path):
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
