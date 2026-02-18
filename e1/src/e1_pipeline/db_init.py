from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone

from .paths import paths_from_config
from .sqlite_utils import connect


WIKIPEDIA_EXTERNAL_SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT NOT NULL UNIQUE,
        source TEXT NOT NULL,
        started_at TEXT NOT NULL,
        ended_at TEXT,
        status TEXT NOT NULL,
        params_json TEXT,
        error_count INTEGER NOT NULL DEFAULT 0
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS wiki_pages_raw (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT NOT NULL,
        title TEXT NOT NULL,
        page_id INTEGER,
        url TEXT,
        content_raw TEXT NOT NULL,
        fetched_at TEXT NOT NULL,
        content_hash TEXT NOT NULL UNIQUE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS wiki_titles_raw (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT NOT NULL,
        title TEXT NOT NULL,
        title_length INTEGER NOT NULL,
        dump_version TEXT NOT NULL,
        fetched_at TEXT NOT NULL,
        content_hash TEXT NOT NULL UNIQUE
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_wiki_pages_raw_run_id ON wiki_pages_raw(run_id);",
    "CREATE INDEX IF NOT EXISTS idx_wiki_titles_raw_run_id ON wiki_titles_raw(run_id);",
]


FLASHCARDS2_SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT NOT NULL UNIQUE,
        source TEXT NOT NULL,
        started_at TEXT NOT NULL,
        ended_at TEXT,
        status TEXT NOT NULL,
        params_json TEXT,
        error_count INTEGER NOT NULL DEFAULT 0
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS raw_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT NOT NULL,
        source TEXT NOT NULL,
        external_id TEXT,
        raw_text TEXT NOT NULL,
        raw_meta_json TEXT,
        fetched_at TEXT NOT NULL,
        content_hash TEXT NOT NULL UNIQUE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS clean_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT NOT NULL,
        raw_item_id INTEGER,
        clean_text TEXT NOT NULL,
        language TEXT,
        quality_score REAL,
        clean_meta_json TEXT,
        created_at TEXT NOT NULL,
        content_hash TEXT NOT NULL UNIQUE,
        FOREIGN KEY(raw_item_id) REFERENCES raw_items(id) ON DELETE SET NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS datasets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT NOT NULL,
        export_path TEXT NOT NULL,
        format TEXT NOT NULL,
        rows_count INTEGER NOT NULL,
        schema_json TEXT,
        created_at TEXT NOT NULL
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_raw_items_run_id ON raw_items(run_id);",
    "CREATE INDEX IF NOT EXISTS idx_clean_items_run_id ON clean_items(run_id);",
]


def _init_db(db_path: Path, statements: list[str]) -> None:
    with connect(db_path) as conn:
        for stmt in statements:
            conn.execute(stmt)


def init_all_dbs(config: dict) -> None:
    repo_root = Path(__file__).resolve().parents[3]
    p = paths_from_config(config, repo_root)

    p.data_dir.mkdir(parents=True, exist_ok=True)
    p.exports_dir.mkdir(parents=True, exist_ok=True)
    p.dumps_dir.mkdir(parents=True, exist_ok=True)

    _init_db(p.wikipedia_external_db, WIKIPEDIA_EXTERNAL_SCHEMA)
    _init_db(p.flashcards2_db, FLASHCARDS2_SCHEMA)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
