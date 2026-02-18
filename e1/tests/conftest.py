from __future__ import annotations

import sys
from pathlib import Path


def pytest_configure() -> None:
    """Make `e1/src` importable for all E1 tests."""

    repo_root = Path(__file__).resolve().parents[2]
    e1_src = (repo_root / "e1" / "src").resolve()
    if str(e1_src) not in sys.path:
        sys.path.insert(0, str(e1_src))