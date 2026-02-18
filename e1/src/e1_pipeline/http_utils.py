from __future__ import annotations

import json
import urllib.request
from typing import Any, Dict


def get_json(url: str, *, user_agent: str, timeout_seconds: int = 10) -> Dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": user_agent,
            "Accept": "application/json",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    return json.loads(raw)
