from pathlib import Path


def test_wikipedia_etl_copies_staging_into_raw_items_and_is_idempotent(tmp_path: Path):
    config = {
        "paths": {
            "wikipedia_external_db": str(tmp_path / "wikipedia_external.db"),
            "flashcards2_db": str(tmp_path / "flashcards2.db"),
            "data_dir": str(tmp_path),
            "exports_dir": str(tmp_path / "exports"),
            "dumps_dir": str(tmp_path / "dumps"),
        }
    }

    from e1_pipeline.db_init import init_all_dbs
    from e1_pipeline.hashing import sha256_text
    from e1_pipeline.sqlite_utils import connect
    from e1_pipeline.wikipedia_etl import run_wikipedia_etl

    init_all_dbs(config)

    fetched_at = "2020-01-01T00:00:00+00:00"
    page_text = "Hello from Wikipedia page"
    title_text = "Some Wikipedia Title"

    with connect(Path(config["paths"]["wikipedia_external_db"])) as src:
        src.execute(
            """
            INSERT INTO wiki_pages_raw(run_id, title, page_id, url, content_raw, fetched_at, content_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "r1",
                "Test Page",
                123,
                "https://en.wikipedia.org/?curid=123",
                page_text,
                fetched_at,
                sha256_text(page_text),
            ),
        )
        src.execute(
            """
            INSERT INTO wiki_titles_raw(run_id, title, title_length, dump_version, fetched_at, content_hash)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "r2",
                title_text,
                len(title_text),
                "enwiki-latest-all-titles-in-ns0",
                fetched_at,
                sha256_text(title_text),
            ),
        )

    stats1 = run_wikipedia_etl(config)
    assert stats1["inserted"] == 2
    assert stats1["inserted_pages"] == 1
    assert stats1["inserted_titles"] == 1

    # 2nd run should be idempotent (dedup via content_hash)
    stats2 = run_wikipedia_etl(config)
    assert stats2["inserted"] == 0
    assert stats2["ignored"] == 2

    with connect(Path(config["paths"]["flashcards2_db"])) as dst:
        rows = dst.execute("SELECT source, raw_text FROM raw_items ORDER BY id").fetchall()
    assert len(rows) == 2
    assert set(r[0] for r in rows) == {"wikipedia_api", "wikimedia_dump_titles"}
