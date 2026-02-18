from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from .hashing import sha256_text
from .paths import paths_from_config
from .sqlite_utils import connect


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


_CTRL_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F]")


def normalize_text(text: str) -> str:
    s = text.replace("\u00a0", " ")
    s = _CTRL_RE.sub(" ", s)
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def guess_language(text: str) -> Optional[str]:
    if not text:
        return None
    ascii_chars = sum(1 for c in text if ord(c) < 128)
    ratio = ascii_chars / max(1, len(text))
    return "en" if ratio > 0.95 else "unknown"


def quality_score(text: str) -> float:
    if not text:
        return 0.0
    length_component = min(1.0, len(text) / 1000.0)
    alpha = sum(1 for c in text if c.isalpha())
    alpha_ratio = alpha / max(1, len(text))
    return round(length_component * alpha_ratio, 4)


def run_cleaning(config: dict) -> Dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[3]
    p = paths_from_config(config, repo_root)

    run_id = str(uuid.uuid4())
    started_at = _utc_now_iso()
    params_json = json.dumps({"min_len": 50}, ensure_ascii=False)

    inserted = 0
    ignored = 0

    with connect(p.flashcards2_db) as conn:
        conn.execute(
            "INSERT INTO runs(run_id, source, started_at, status, params_json) VALUES (?, ?, ?, ?, ?)",
            (run_id, "cleaning", started_at, "running", params_json),
        )

        rows = conn.execute("SELECT id, raw_text, raw_meta_json FROM raw_items ORDER BY id").fetchall()
        for raw_id, raw_text, raw_meta_json in rows:
            clean = normalize_text(raw_text or "")
            if len(clean) < 50:
                continue

            lang = guess_language(clean)
            score = quality_score(clean)
            content_hash = sha256_text(clean)

            meta: Dict[str, Any]
            try:
                meta = json.loads(raw_meta_json) if raw_meta_json else {}
            except Exception:
                meta = {"raw_meta_json": raw_meta_json}
            meta["quality_rule"] = "len>=50"

            created_at = _utc_now_iso()
            ins = conn.execute(
                """
                INSERT OR IGNORE INTO clean_items(
                    run_id, raw_item_id, clean_text, language, quality_score, clean_meta_json, created_at, content_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    int(raw_id),
                    clean,
                    lang,
                    float(score),
                    json.dumps(meta, ensure_ascii=False),
                    created_at,
                    content_hash,
                ),
            )
            if ins.rowcount == 1:
                inserted += 1
            else:
                ignored += 1

        conn.execute(
            "UPDATE runs SET ended_at = ?, status = ? WHERE run_id = ?",
            (_utc_now_iso(), "success", run_id),
        )

    return {"run_id": run_id, "inserted": inserted, "ignored": ignored}
