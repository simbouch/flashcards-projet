from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, List, Optional

import urllib.request

from .hashing import sha256_text
from .paths import paths_from_config
from .sqlite_utils import connect


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._skip_depth = 0
        self._chunks: List[str] = []

    def handle_starttag(self, tag: str, attrs):
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1
        if tag in {"p", "br", "li", "h1", "h2", "h3"}:
            self._chunks.append("\n")

    def handle_endtag(self, tag: str):
        if tag in {"script", "style", "noscript"} and self._skip_depth > 0:
            self._skip_depth -= 1
        if tag in {"p", "li"}:
            self._chunks.append("\n")

    def handle_data(self, data: str):
        if self._skip_depth > 0:
            return
        s = data.strip()
        if not s:
            return
        self._chunks.append(s)

    def text(self) -> str:
        raw = " ".join(self._chunks)
        raw = re.sub(r"[ \t\r\f\v]+", " ", raw)
        raw = re.sub(r"\n\s+", "\n", raw)
        raw = re.sub(r"\n{3,}", "\n\n", raw)
        return raw.strip()


def html_to_text(html: str) -> str:
    parser = _TextExtractor()
    parser.feed(html)
    return parser.text()


def fetch_html(
    url: str,
    *,
    user_agent: str,
    timeout_seconds: int = 10,
) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
        raw = resp.read()
    # best effort decode
    return raw.decode("utf-8", errors="replace")


@dataclass(frozen=True)
class ScrapeStats:
    run_id: str
    inserted: int
    ignored: int
    errors: int


def run_web_scraping(config: dict) -> Dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[3]
    p = paths_from_config(config, repo_root)
    scfg = config.get("scraping", {})

    seed_urls: List[str] = scfg.get("seed_urls", [])
    timeout_seconds = int(scfg.get("timeout_seconds", 10))
    user_agent = scfg.get("user_agent") or config.get("wikipedia_api", {}).get(
        "user_agent", "flashcards-e1-scraper/1.0"
    )

    run_id = str(uuid.uuid4())
    started_at = _utc_now_iso()
    params_json = json.dumps(
        {"seed_urls": seed_urls, "timeout_seconds": timeout_seconds},
        ensure_ascii=False,
    )

    inserted = 0
    ignored = 0
    errors = 0

    with connect(p.flashcards2_db) as conn:
        conn.execute(
            "INSERT INTO runs(run_id, source, started_at, status, params_json) VALUES (?, ?, ?, ?, ?)",
            (run_id, "web_scraping", started_at, "running", params_json),
        )

        for url in seed_urls:
            try:
                html = fetch_html(url, user_agent=user_agent, timeout_seconds=timeout_seconds)
                text = html_to_text(html)
                if len(text) < 200:
                    # too small to be useful as a corpus example
                    continue

                meta = {"url": url}
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
                        "web_scrape",
                        url,
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
            except Exception:
                errors += 1
                continue

        conn.execute(
            "UPDATE runs SET ended_at = ?, status = ?, error_count = ? WHERE run_id = ?",
            (_utc_now_iso(), "success" if errors == 0 else "partial", errors, run_id),
        )

    return {"run_id": run_id, "inserted": inserted, "ignored": ignored, "errors": errors}
