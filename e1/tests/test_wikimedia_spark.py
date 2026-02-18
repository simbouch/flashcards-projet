import gzip
import os
import sys
from pathlib import Path

import pytest


def test_wikimedia_titles_spark_inserts_rows_from_local_gz(tmp_path: Path):
    pytest.importorskip("pyspark")

    # Skip cleanly if Spark cannot start (missing Java, etc.)
    try:
        os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
        os.environ.setdefault("PYSPARK_DRIVER_PYTHON", sys.executable)
        from pyspark.sql import SparkSession

        spark = (
            SparkSession.builder.master("local[1]")
            .appName("e1-spark-smoke")
            .config("spark.ui.enabled", "false")
            .config("spark.pyspark.python", sys.executable)
            .config("spark.pyspark.driver.python", sys.executable)
            .getOrCreate()
        )
        spark.stop()
    except Exception as e:
        pytest.skip(f"Spark not available: {e}")

    dump_path = tmp_path / "titles.gz"
    with gzip.open(dump_path, "wt", encoding="utf-8") as f:
        f.write("Python\n")
        f.write("Machine learning\n")
        f.write("\n")

    config = {
        "paths": {
            "wikipedia_external_db": str(tmp_path / "wikipedia_external.db"),
            "flashcards2_db": str(tmp_path / "flashcards2.db"),
            "data_dir": str(tmp_path),
            "exports_dir": str(tmp_path / "exports"),
            "dumps_dir": str(tmp_path / "dumps"),
        },
        "wikimedia_dump": {
            "titles_dump_path": str(dump_path),
            "dump_version": "test-dump",
            "auto_download": False,
            "max_titles": 10,
            "spark_master": "local[1]",
        },
    }

    from e1_pipeline.db_init import init_all_dbs
    from e1_pipeline.sqlite_utils import connect
    from e1_pipeline.wikimedia_spark import run_wikimedia_titles_spark

    init_all_dbs(config)
    stats = run_wikimedia_titles_spark(config)

    assert stats["status"] == "success"
    assert stats["inserted"] == 2

    with connect(Path(config["paths"]["wikipedia_external_db"])) as conn:
        rows = conn.execute("SELECT title, dump_version FROM wiki_titles_raw ORDER BY id").fetchall()
    assert [r[0] for r in rows] == ["Python", "Machine learning"]
    assert rows[0][1] == "test-dump"
