from __future__ import annotations

import csv
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from .paths import paths_from_config
from .sqlite_utils import connect


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_json_loads(s: str | None) -> Any:
    if not s:
        return None
    try:
        return json.loads(s)
    except Exception:
        return s


def run_export_dataset(config: dict) -> Dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[3]
    p = paths_from_config(config, repo_root)
    p.exports_dir.mkdir(parents=True, exist_ok=True)

    run_id = str(uuid.uuid4())
    started_at = _utc_now_iso()

    csv_path = p.exports_dir / f"clean_items_{run_id}.csv"
    jsonl_path = p.exports_dir / f"clean_items_{run_id}.jsonl"

    columns: List[str] = [
        "id",
        "raw_item_id",
        "clean_text",
        "language",
        "quality_score",
        "created_at",
        "clean_meta_json",
        "content_hash",
    ]

    with connect(p.flashcards2_db) as conn:
        conn.execute(
            "INSERT INTO runs(run_id, source, started_at, status, params_json) VALUES (?, ?, ?, ?, ?)",
            (run_id, "export_dataset", started_at, "running", json.dumps({"formats": ["csv", "jsonl"]})),
        )

        rows = conn.execute(
            """
            SELECT id, raw_item_id, clean_text, language, quality_score, created_at, clean_meta_json, content_hash
            FROM clean_items
            ORDER BY id
            """
        ).fetchall()

        with csv_path.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(columns)
            for r in rows:
                w.writerow(list(r))

        with jsonl_path.open("w", encoding="utf-8") as f:
            for r in rows:
                obj = dict(zip(columns, list(r)))
                obj["clean_meta_json"] = _safe_json_loads(obj.get("clean_meta_json"))
                f.write(json.dumps(obj, ensure_ascii=False) + "\n")

        created_at = _utc_now_iso()
        schema_json = json.dumps({"columns": columns}, ensure_ascii=False)
        for export_path, fmt in [(csv_path, "csv"), (jsonl_path, "jsonl")]:
            conn.execute(
                """
                INSERT INTO datasets(run_id, export_path, format, rows_count, schema_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (run_id, str(export_path), fmt, len(rows), schema_json, created_at),
            )

        conn.execute(
            "UPDATE runs SET ended_at = ?, status = ? WHERE run_id = ?",
            (_utc_now_iso(), "success", run_id),
        )

    return {
        "run_id": run_id,
        "rows_count": len(rows),
        "csv_path": str(csv_path),
        "jsonl_path": str(jsonl_path),
    }
