import json
from pathlib import Path


def test_export_writes_csv_and_jsonl_and_registers_datasets(tmp_path: Path):
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
    from e1_pipeline.export_dataset import run_export_dataset

    init_all_dbs(config)
    clean_text = "Hello export " * 20

    with connect(Path(config["paths"]["flashcards2_db"])) as conn:
        conn.execute(
            """
            INSERT INTO clean_items(
                run_id, raw_item_id, clean_text, language, quality_score, clean_meta_json, created_at, content_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "r1",
                None,
                clean_text,
                "en",
                0.5,
                json.dumps({"source": "test"}),
                "2020-01-01T00:00:00Z",
                sha256_text(clean_text),
            ),
        )

    stats = run_export_dataset(config)
    csv_path = Path(stats["csv_path"])
    jsonl_path = Path(stats["jsonl_path"])
    assert csv_path.exists()
    assert jsonl_path.exists()
    assert stats["rows_count"] == 1

    csv_lines = csv_path.read_text(encoding="utf-8").splitlines()
    assert len(csv_lines) >= 2

    jsonl_lines = jsonl_path.read_text(encoding="utf-8").splitlines()
    assert len(jsonl_lines) == 1
    obj = json.loads(jsonl_lines[0])
    assert obj["language"] == "en"
    assert isinstance(obj["clean_meta_json"], dict)

    with connect(Path(config["paths"]["flashcards2_db"])) as conn:
        ds = conn.execute("SELECT format, rows_count FROM datasets ORDER BY id").fetchall()
    assert [d[0] for d in ds] == ["csv", "jsonl"]
    assert [d[1] for d in ds] == [1, 1]
