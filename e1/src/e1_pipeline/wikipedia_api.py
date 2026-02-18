from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import urlencode

from .hashing import sha256_text
from .http_utils import get_json
from .paths import paths_from_config
from .sqlite_utils import connect


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def wikipedia_search(
    *,
    base_url: str,
    keyword: str,
    limit: int,
    user_agent: str,
    timeout_seconds: int = 10,
) -> List[Dict[str, Any]]:
    params = {
        "action": "query",
        "list": "search",
        "format": "json",
        "srsearch": keyword,
        "srlimit": limit,
        "utf8": 1,
    }
    url = f"{base_url}?{urlencode(params)}"
    data = get_json(url, user_agent=user_agent, timeout_seconds=timeout_seconds)
    return data.get("query", {}).get("search", [])


def wikipedia_extract_plaintext(
    *,
    base_url: str,
    page_id: int,
    user_agent: str,
    timeout_seconds: int = 10,
) -> str:
    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": 1,
        "exsectionformat": "plain",
        "format": "json",
        "pageids": str(page_id),
        "utf8": 1,
    }
    url = f"{base_url}?{urlencode(params)}"
    data = get_json(url, user_agent=user_agent, timeout_seconds=timeout_seconds)
    pages = data.get("query", {}).get("pages", {})
    page = pages.get(str(page_id), {})
    return (page.get("extract") or "").strip()


def run_wikipedia_api_collection(config: dict) -> Dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[3]
    p = paths_from_config(config, repo_root)
    wcfg = config.get("wikipedia_api", {})

    base_url = wcfg.get("base_url", "https://en.wikipedia.org/w/api.php")
    user_agent = wcfg.get("user_agent", "flashcards-e1-pipeline/1.0")
    keywords = wcfg.get("keywords", ["machine learning"])
    limit = int(wcfg.get("search_limit", 5))
    timeout_seconds = int(wcfg.get("timeout_seconds", 10))

    run_id = str(uuid.uuid4())
    started_at = _utc_now_iso()

    params_json = json.dumps({"keywords": keywords, "limit": limit}, ensure_ascii=False)
    inserted = 0
    ignored = 0

    with connect(p.wikipedia_external_db) as conn:
        conn.execute(
            "INSERT INTO runs(run_id, source, started_at, status, params_json) VALUES (?, ?, ?, ?, ?)",
            (run_id, "wikipedia_api", started_at, "running", params_json),
        )

        for kw in keywords:
            results = wikipedia_search(
                base_url=base_url,
                keyword=kw,
                limit=limit,
                user_agent=user_agent,
                timeout_seconds=timeout_seconds,
            )
            for r in results:
                page_id = int(r.get("pageid")) if r.get("pageid") is not None else None
                title = (r.get("title") or "").strip()
                if not page_id or not title:
                    continue

                text = wikipedia_extract_plaintext(
                    base_url=base_url,
                    page_id=page_id,
                    user_agent=user_agent,
                    timeout_seconds=timeout_seconds,
                )
                if not text:
                    continue

                url = f"https://en.wikipedia.org/?curid={page_id}"
                content_hash = sha256_text(text)
                fetched_at = _utc_now_iso()
                cur = conn.execute(
                    """
                    INSERT OR IGNORE INTO wiki_pages_raw(
                        run_id, title, page_id, url, content_raw, fetched_at, content_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (run_id, title, page_id, url, text, fetched_at, content_hash),
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
