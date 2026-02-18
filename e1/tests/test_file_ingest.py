from pathlib import Path


def test_file_ingestion_inserts_rows(tmp_path: Path):
    (tmp_path / "samples").mkdir(parents=True, exist_ok=True)
    (tmp_path / "samples" / "sample.csv").write_text(
        "title,text\nA,Hello from CSV\n",
        encoding="utf-8",
    )
    (tmp_path / "samples" / "sample.json").write_text(
        '[{"id":"j1","text":"Hello from JSON"}]',
        encoding="utf-8",
    )
    (tmp_path / "samples" / "sample.xml").write_text(
        "<?xml version=\"1.0\"?><items><item id=\"x1\"><text>Hello from XML</text></item></items>",
        encoding="utf-8",
    )

    config = {
        "paths": {
            "wikipedia_external_db": str(tmp_path / "wikipedia_external.db"),
            "flashcards2_db": str(tmp_path / "flashcards2.db"),
            "data_dir": str(tmp_path),
            "exports_dir": str(tmp_path / "exports"),
            "dumps_dir": str(tmp_path / "dumps"),
        },
        "file_sources": {"samples_dir": str(tmp_path / "samples")},
    }

    from e1_pipeline.db_init import init_all_dbs
    from e1_pipeline.file_ingest import run_file_ingestion
    from e1_pipeline.sqlite_utils import connect

    init_all_dbs(config)
    stats = run_file_ingestion(config)
    assert stats["inserted"] == 3

    with connect(Path(config["paths"]["flashcards2_db"])) as conn:
        rows = conn.execute("SELECT source, raw_text FROM raw_items ORDER BY id").fetchall()
    assert len(rows) == 3
    assert rows[0][0] == "file_csv"
