from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from .paths import paths_from_config
from .sqlite_utils import connect


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_wikipedia_etl(config: dict) -> Dict[str, Any]:
    """Copy staging Wikipedia data into flashcards2.raw_items.

    - Source DB (staging): `wikipedia_external.db` (wiki_pages_raw, wiki_titles_raw)
    - Target DB (final): `flashcards2.db` (raw_items)

    This makes Wikipedia sources part of the same downstream pipeline:
    raw_items -> clean_items -> exports.
    """

    repo_root = Path(__file__).resolve().parents[3]
    p = paths_from_config(config, repo_root)

    cfg = config.get("wikipedia_etl", {})
    include_pages = bool(cfg.get("include_pages", True))
    include_titles = bool(cfg.get("include_titles", True))
    max_pages: Optional[int] = cfg.get("max_pages")
    max_titles: Optional[int] = cfg.get("max_titles")

    run_id = str(uuid.uuid4())
    started_at = _utc_now_iso()
    params_json = json.dumps(
        {
            "include_pages": include_pages,
            "include_titles": include_titles,
            "max_pages": max_pages,
            "max_titles": max_titles,
        },
        ensure_ascii=False,
    )

    # Read from staging DB
    pages_rows = []
    titles_rows = []
    with connect(p.wikipedia_external_db) as src:
        if include_pages:
            q = (
                "SELECT title, page_id, url, content_raw, fetched_at, content_hash "
                "FROM wiki_pages_raw ORDER BY id"
            )
            args: tuple[Any, ...] = ()
            if max_pages is not None:
                q += " LIMIT ?"
                args = (int(max_pages),)
            pages_rows = src.execute(q, args).fetchall()

        if include_titles:
            q = (
                "SELECT title, title_length, dump_version, fetched_at, content_hash "
                "FROM wiki_titles_raw ORDER BY id"
            )
            args = ()
            if max_titles is not None:
                q += " LIMIT ?"
                args = (int(max_titles),)
            titles_rows = src.execute(q, args).fetchall()

    inserted = 0
    ignored = 0
    inserted_pages = 0
    inserted_titles = 0

    # Write into final DB
    with connect(p.flashcards2_db) as dst:
        dst.execute(
            "INSERT INTO runs(run_id, source, started_at, status, params_json) VALUES (?, ?, ?, ?, ?)",
            (run_id, "wikipedia_etl", started_at, "running", params_json),
        )

        for title, page_id, url, content_raw, fetched_at, content_hash in pages_rows:
            external_id = str(page_id) if page_id is not None else (url or title)
            meta = {"title": title, "page_id": page_id, "url": url, "kind": "wiki_page"}
            cur = dst.execute(
                """
                INSERT OR IGNORE INTO raw_items(
                    run_id, source, external_id, raw_text, raw_meta_json, fetched_at, content_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    "wikipedia_api",
                    external_id,
                    content_raw,
                    json.dumps(meta, ensure_ascii=False),
                    fetched_at,
                    content_hash,
                ),
            )
            if cur.rowcount == 1:
                inserted += 1
                inserted_pages += 1
            else:
                ignored += 1

        for title, title_length, dump_version, fetched_at, content_hash in titles_rows:
            meta = {
                "dump_version": dump_version,
                "title_length": int(title_length) if title_length is not None else None,
                "kind": "wiki_title",
            }
            cur = dst.execute(
                """
                INSERT OR IGNORE INTO raw_items(
                    run_id, source, external_id, raw_text, raw_meta_json, fetched_at, content_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    "wikimedia_dump_titles",
                    title,
                    title,
                    json.dumps(meta, ensure_ascii=False),
                    fetched_at,
                    content_hash,
                ),
            )
            if cur.rowcount == 1:
                inserted += 1
                inserted_titles += 1
            else:
                ignored += 1

        dst.execute(
            "UPDATE runs SET ended_at = ?, status = ? WHERE run_id = ?",
            (_utc_now_iso(), "success", run_id),
        )

    return {
        "run_id": run_id,
        "inserted": inserted,
        "ignored": ignored,
        "inserted_pages": inserted_pages,
        "inserted_titles": inserted_titles,
    }
