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


def test_process_document_passes_scaled_num_cards(monkeypatch, tmp_path):
    """Ensure process_document computes num_cards dynamically and passes it to the LLM client."""
    from types import SimpleNamespace

    from backend_service.src.api.endpoints import documents as documents_module
    from backend_service.src.config import settings

    # Ensure min default is stable for this test
    monkeypatch.setattr(settings, "DEFAULT_NUM_CARDS_PER_DOCUMENT", 5)

    # Fake DB session
    class _FakeDB:
        def close(self):
            return None

    monkeypatch.setattr(documents_module, "SessionLocalFactory", lambda: _FakeDB())

    # Stub CRUD methods used by the pipeline
    monkeypatch.setattr(documents_module.crud, "update_document_status", lambda *a, **k: None)
    monkeypatch.setattr(documents_module.crud, "create_extracted_text", lambda *a, **k: None)
    monkeypatch.setattr(
        documents_module.crud,
        "get_document",
        lambda *a, **k: SimpleNamespace(filename="f.pdf", owner_id="u1"),
    )
    monkeypatch.setattr(
        documents_module.crud,
        "create_deck",
        lambda *a, **k: SimpleNamespace(id="deck1"),
    )
    monkeypatch.setattr(documents_module.crud, "create_flashcard", lambda *a, **k: None)

    # OCR returns a large text to force scaling above default
    big_text = "word " * 20_000

    async def _fake_extract_text(*a, **k):
        return {"text": big_text}

    monkeypatch.setattr(documents_module.ocr_client, "extract_text", _fake_extract_text)

    called = {}

    async def _fake_generate_flashcards(text: str, num_cards: int = 5):
        called["num_cards"] = num_cards
        return {"flashcards": [{"question": "Q1", "answer": "A1"}] * min(num_cards, 1)}

    monkeypatch.setattr(documents_module.llm_client, "generate_flashcards", _fake_generate_flashcards)

    import asyncio

    asyncio.run(documents_module.process_document("doc1", tmp_path / "x.pdf"))

    assert called["num_cards"] >= 5
    assert called["num_cards"] <= 20
