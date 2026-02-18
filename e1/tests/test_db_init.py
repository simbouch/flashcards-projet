from pathlib import Path


def test_init_all_dbs_creates_files(tmp_path: Path):
    config = {
        "paths": {
            "data_dir": str(tmp_path / "data"),
            "wikipedia_external_db": str(tmp_path / "data" / "wikipedia_external.db"),
            "flashcards2_db": str(tmp_path / "data" / "flashcards2.db"),
            "exports_dir": str(tmp_path / "data" / "exports"),
            "dumps_dir": str(tmp_path / "data" / "dumps"),
        }
    }

    from e1_pipeline.db_init import init_all_dbs

    init_all_dbs(config)
    assert (tmp_path / "data" / "wikipedia_external.db").exists()
    assert (tmp_path / "data" / "flashcards2.db").exists()
