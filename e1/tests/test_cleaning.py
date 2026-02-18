from pathlib import Path


def test_cleaning_creates_clean_items_and_is_idempotent(tmp_path: Path):
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
    from e1_pipeline.sqlite_utils import connect
    from e1_pipeline.hashing import sha256_text
    from e1_pipeline.cleaning import run_cleaning

    init_all_dbs(config)

    long_text = "Hello world. " * 40  # > 50 chars
    short_text = "too short"

    with connect(Path(config["paths"]["flashcards2_db"])) as conn:
        conn.execute(
            """
            INSERT INTO raw_items(run_id, source, external_id, raw_text, raw_meta_json, fetched_at, content_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "r1",
                "file_csv",
                "x1",
                long_text,
                "{}",
                "2020-01-01T00:00:00Z",
                sha256_text(long_text),
            ),
        )
        conn.execute(
            """
            INSERT INTO raw_items(run_id, source, external_id, raw_text, raw_meta_json, fetched_at, content_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "r2",
                "file_csv",
                "x2",
                short_text,
                "{}",
                "2020-01-01T00:00:00Z",
                sha256_text(short_text),
            ),
        )

    stats1 = run_cleaning(config)
    assert stats1["inserted"] == 1

    stats2 = run_cleaning(config)
    assert stats2["inserted"] == 0
    assert stats2["ignored"] >= 1

    with connect(Path(config["paths"]["flashcards2_db"])) as conn:
        rows = conn.execute(
            "SELECT clean_text, quality_score, content_hash FROM clean_items ORDER BY id"
        ).fetchall()

    assert len(rows) == 1
    assert len(rows[0][0]) >= 50
    assert rows[0][1] > 0
    assert rows[0][2] == sha256_text(rows[0][0])
