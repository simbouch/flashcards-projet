from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from .hashing import sha256_text
from .paths import paths_from_config
from .sqlite_utils import connect


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _download_file(url: str, dest_path: Path, timeout_seconds: int = 60) -> None:
    """Download `url` to `dest_path` (streaming) using stdlib only."""
    import urllib.request

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "flashcards-e1-pipeline/1.0"})
    with urllib.request.urlopen(req, timeout=timeout_seconds) as r:
        with dest_path.open("wb") as f:
            while True:
                chunk = r.read(1024 * 1024)
                if not chunk:
                    break
                f.write(chunk)


def _get_dump_path(dumps_dir: Path, titles_dump_url: str, explicit_path: str | None) -> Path:
    if explicit_path:
        return Path(explicit_path)
    return dumps_dir / Path(titles_dump_url).name


def _spark_take_titles(dump_path: Path, max_titles: int, spark_master: str) -> List[str]:
    """Read up to `max_titles` lines from the dump using Spark local mode."""
    try:
        from pyspark.sql import SparkSession  # type: ignore
    except Exception as e:  # pragma: no cover
        raise RuntimeError("PySpark is not available. Install with: python -m pip install pyspark") from e

    # On Windows, Spark may fail if it tries to resolve `python` from PATH.
    # Pin PySpark to the currently running interpreter.
    import os
    import sys

    os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
    os.environ.setdefault("PYSPARK_DRIVER_PYTHON", sys.executable)

    spark = (
        SparkSession.builder.master(spark_master)
        .appName("e1-wikimedia-titles")
        .config("spark.ui.enabled", "false")
        .config("spark.pyspark.python", sys.executable)
        .config("spark.pyspark.driver.python", sys.executable)
        .getOrCreate()
    )
    try:
        # Use DataFrame built-in functions (JVM-side) to avoid spawning Python workers.
        from pyspark.sql import functions as F  # type: ignore

        df = spark.read.text(str(dump_path)).select(F.trim(F.col("value")).alias("title"))
        df = df.where(F.col("title").isNotNull() & (F.col("title") != ""))
        rows = df.limit(int(max_titles)).collect()
        return [r["title"] for r in rows]
    finally:
        spark.stop()


def _as_rows(
    run_id: str,
    titles: Iterable[str],
    dump_version: str,
    fetched_at: str,
) -> List[Tuple[str, str, int, str, str, str]]:
    rows: List[Tuple[str, str, int, str, str, str]] = []
    for t in titles:
        rows.append((run_id, t, len(t), dump_version, fetched_at, sha256_text(t)))
    return rows


def run_wikimedia_titles_spark(config: dict) -> Dict[str, Any]:
    """C1 Big Data: process Wikimedia titles dump via PySpark into wikipedia_external.db."""
    repo_root = Path(__file__).resolve().parents[3]
    p = paths_from_config(config, repo_root)

    cfg = config.get("wikimedia_dump", {})
    titles_dump_url = cfg.get(
        "titles_dump_url",
        "https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-all-titles-in-ns0.gz",
    )
    dump_version = cfg.get("dump_version", "enwiki-latest-all-titles-in-ns0")
    explicit_path = cfg.get("titles_dump_path")
    dump_path = _get_dump_path(p.dumps_dir, titles_dump_url, explicit_path)

    auto_download = bool(cfg.get("auto_download", False))
    max_titles = int(cfg.get("max_titles", 5000))
    spark_master = cfg.get("spark_master", "local[*]")
    timeout_seconds = int(cfg.get("timeout_seconds", 60))

    run_id = str(uuid.uuid4())
    started_at = _utc_now_iso()
    fetched_at = started_at

    params_json = json.dumps(
        {
            "dump_path": str(dump_path),
            "dump_version": dump_version,
            "max_titles": max_titles,
            "spark_master": spark_master,
            "auto_download": auto_download,
        },
        ensure_ascii=False,
    )

    inserted = 0
    ignored = 0
    status = "success"

    with connect(p.wikipedia_external_db) as conn:
        conn.execute(
            "INSERT INTO runs(run_id, source, started_at, status, params_json) VALUES (?, ?, ?, ?, ?)",
            (run_id, "wikimedia_dump_spark", started_at, "running", params_json),
        )

        if not dump_path.exists():
            if auto_download:
                _download_file(titles_dump_url, dump_path, timeout_seconds=timeout_seconds)
            else:
                status = "skipped"
                conn.execute(
                    "UPDATE runs SET ended_at = ?, status = ? WHERE run_id = ?",
                    (_utc_now_iso(), status, run_id),
                )
                return {
                    "run_id": run_id,
                    "status": status,
                    "inserted": 0,
                    "ignored": 0,
                    "dump_path": str(dump_path),
                }

        titles = _spark_take_titles(dump_path=dump_path, max_titles=max_titles, spark_master=spark_master)
        rows = _as_rows(run_id=run_id, titles=titles, dump_version=dump_version, fetched_at=fetched_at)

        before = conn.total_changes
        conn.executemany(
            """
            INSERT OR IGNORE INTO wiki_titles_raw(
                run_id, title, title_length, dump_version, fetched_at, content_hash
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        inserted = conn.total_changes - before
        ignored = len(rows) - inserted

        conn.execute(
            "UPDATE runs SET ended_at = ?, status = ? WHERE run_id = ?",
            (_utc_now_iso(), status, run_id),
        )

    return {
        "run_id": run_id,
        "status": status,
        "inserted": inserted,
        "ignored": ignored,
        "dump_path": str(dump_path),
        "max_titles": max_titles,
    }
