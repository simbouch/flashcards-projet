import json
from pathlib import Path
from unittest.mock import patch


class _FakeHTTPResponse:
    def __init__(self, payload: bytes):
        self._payload = payload

    def read(self):
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_web_scraping_inserts_row(tmp_path: Path):
    config = {
        "paths": {
            "wikipedia_external_db": str(tmp_path / "wikipedia_external.db"),
            "flashcards2_db": str(tmp_path / "flashcards2.db"),
            "data_dir": str(tmp_path),
            "exports_dir": str(tmp_path / "exports"),
            "dumps_dir": str(tmp_path / "dumps"),
        },
        "scraping": {
            "seed_urls": ["https://example.test/page"],
            "timeout_seconds": 1,
            "user_agent": "test-agent",
        },
    }

    from e1_pipeline.db_init import init_all_dbs
    from e1_pipeline.sqlite_utils import connect
    from e1_pipeline.web_scraping import run_web_scraping

    init_all_dbs(config)

    html = (
        "<html><head><title>T</title><style>.x{}</style></head>"
        "<body><h1>Header</h1><p>" + ("hello " * 60) + "</p></body></html>"
    ).encode("utf-8")

    def _fake_urlopen(req, timeout=10):
        return _FakeHTTPResponse(html)

    with patch("urllib.request.urlopen", side_effect=_fake_urlopen):
        stats = run_web_scraping(config)

    assert stats["inserted"] == 1

    with connect(Path(config["paths"]["flashcards2_db"])) as conn:
        row = conn.execute(
            "SELECT source, external_id, raw_meta_json FROM raw_items LIMIT 1"
        ).fetchone()
    assert row[0] == "web_scrape"
    assert row[1] == "https://example.test/page"
    meta = json.loads(row[2])
    assert meta["url"] == "https://example.test/page"
