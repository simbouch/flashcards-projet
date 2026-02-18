from __future__ import annotations

import csv
import json
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from .hashing import sha256_text
from .paths import paths_from_config
from .sqlite_utils import connect


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _iter_csv_rows(path: Path) -> Iterable[Tuple[str, str, Dict[str, Any]]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            title = (row.get("title") or "").strip()
            text = (row.get("text") or "").strip()
            if not text:
                continue
            external_id = f"csv:{path.name}:{i}"
            meta = {"title": title, "row": i, "file": path.name}
            yield external_id, text, meta


def _iter_json_rows(path: Path) -> Iterable[Tuple[str, str, Dict[str, Any]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        items: List[dict] = data.get("items", []) if isinstance(data.get("items"), list) else []
    elif isinstance(data, list):
        items = data
    else:
        items = []

    for i, obj in enumerate(items, start=1):
        if not isinstance(obj, dict):
            continue
        text = (obj.get("text") or "").strip()
        if not text:
            continue
        external_id = str(obj.get("id") or f"json:{path.name}:{i}")
        meta = {k: v for k, v in obj.items() if k != "text"}
        meta["file"] = path.name
        yield external_id, text, meta


def _iter_xml_rows(path: Path) -> Iterable[Tuple[str, str, Dict[str, Any]]]:
    root = ET.fromstring(path.read_text(encoding="utf-8"))
    for i, item in enumerate(root.findall(".//item"), start=1):
        text_el = item.find("text")
        text = (text_el.text or "").strip() if text_el is not None else ""
        if not text:
            continue
        external_id = (item.get("id") or f"xml:{path.name}:{i}").strip()
        title_el = item.find("title")
        title = (title_el.text or "").strip() if title_el is not None else ""
        meta = {"title": title, "file": path.name}
        yield external_id, text, meta


def run_file_ingestion(config: dict) -> Dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[3]
    p = paths_from_config(config, repo_root)

    fcfg = config.get("file_sources", {})
    samples_dir = (repo_root / fcfg.get("samples_dir", "e1/data/samples")).resolve()

    csv_path = samples_dir / "sample.csv"
    json_path = samples_dir / "sample.json"
    xml_path = samples_dir / "sample.xml"

    run_id = str(uuid.uuid4())
    started_at = _utc_now_iso()
    params_json = json.dumps(
        {"samples_dir": str(samples_dir), "files": [csv_path.name, json_path.name, xml_path.name]},
        ensure_ascii=False,
    )

    inserted = 0
    ignored = 0

    sources: List[Tuple[str, Path, Any]] = [
        ("file_csv", csv_path, _iter_csv_rows),
        ("file_json", json_path, _iter_json_rows),
        ("file_xml", xml_path, _iter_xml_rows),
    ]

    with connect(p.flashcards2_db) as conn:
        conn.execute(
            "INSERT INTO runs(run_id, source, started_at, status, params_json) VALUES (?, ?, ?, ?, ?)",
            (run_id, "file_ingestion", started_at, "running", params_json),
        )

        for source, path, iterator in sources:
            if not path.exists():
                continue
            for external_id, text, meta in iterator(path):
                content_hash = sha256_text(text)
                fetched_at = _utc_now_iso()
                cur = conn.execute(
                    """
                    INSERT OR IGNORE INTO raw_items(
                        run_id, source, external_id, raw_text, raw_meta_json, fetched_at, content_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        run_id,
                        source,
                        external_id,
                        text,
                        json.dumps(meta, ensure_ascii=False),
                        fetched_at,
                        content_hash,
                    ),
                )
                if cur.rowcount == 1:
                    inserted += 1
                else:
                    ignored += 1

        conn.execute(
            "UPDATE runs SET ended_at = ?, status = ? WHERE run_id = ?",
            (_utc_now_iso(), "success", run_id),
        )

    return {"run_id": run_id, "inserted": inserted, "ignored": ignored}
