import json
from pathlib import Path
from unittest.mock import patch


class _FakeHTTPResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def read(self):
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_collection_inserts_rows(tmp_path: Path):
    config = {
        "paths": {
            "wikipedia_external_db": str(tmp_path / "wikipedia_external.db"),
            "flashcards2_db": str(tmp_path / "flashcards2.db"),
            "data_dir": str(tmp_path),
            "exports_dir": str(tmp_path / "exports"),
            "dumps_dir": str(tmp_path / "dumps"),
        },
        "wikipedia_api": {
            "base_url": "https://example.test/w/api.php",
            "user_agent": "test-agent",
            "keywords": ["ml"],
            "search_limit": 1,
            "timeout_seconds": 1,
        },
    }

    from e1_pipeline.db_init import init_all_dbs
    from e1_pipeline.wikipedia_api import run_wikipedia_api_collection
    from e1_pipeline.sqlite_utils import connect

    init_all_dbs(config)

    search_payload = {"query": {"search": [{"pageid": 123, "title": "Machine learning"}]}}
    extract_payload = {
        "query": {"pages": {"123": {"pageid": 123, "extract": "Some text about ML."}}}
    }

    def _fake_urlopen(req, timeout=10):
        url = req.full_url
        if "list=search" in url:
            return _FakeHTTPResponse(search_payload)
        return _FakeHTTPResponse(extract_payload)

    with patch("urllib.request.urlopen", side_effect=_fake_urlopen):
        stats = run_wikipedia_api_collection(config)

    assert stats["inserted"] == 1

    with connect(Path(config["paths"]["wikipedia_external_db"])) as conn:
        rows = conn.execute("SELECT title, page_id FROM wiki_pages_raw").fetchall()
    assert len(rows) == 1
    assert rows[0][0] == "Machine learning"
    assert rows[0][1] == 123
