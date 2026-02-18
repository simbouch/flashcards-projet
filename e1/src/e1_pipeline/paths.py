from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class E1Paths:
    repo_root: Path
    data_dir: Path
    wikipedia_external_db: Path
    flashcards2_db: Path
    exports_dir: Path
    dumps_dir: Path


def paths_from_config(config: dict, repo_root: Path) -> E1Paths:
    p = config.get("paths", {})
    data_dir = repo_root / p.get("data_dir", "e1/data")
    wikipedia_external_db = repo_root / p.get("wikipedia_external_db", "e1/data/wikipedia_external.db")
    flashcards2_db = repo_root / p.get("flashcards2_db", "e1/data/flashcards2.db")
    exports_dir = repo_root / p.get("exports_dir", "e1/data/exports")
    dumps_dir = repo_root / p.get("dumps_dir", "e1/data/dumps")
    return E1Paths(
        repo_root=repo_root,
        data_dir=data_dir,
        wikipedia_external_db=wikipedia_external_db,
        flashcards2_db=flashcards2_db,
        exports_dir=exports_dir,
        dumps_dir=dumps_dir,
    )
