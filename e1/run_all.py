import argparse
import json
from pathlib import Path


def _load_config(config_path: Path) -> dict:
    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    parser = argparse.ArgumentParser(description="E1 pipeline runner (isolated)")
    parser.add_argument(
        "--config",
        default="e1/config/config.json",
        help="Path to config JSON (default: e1/config/config.json)",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    config_path = (repo_root / args.config).resolve()
    config = _load_config(config_path)

    # Make e1/src importable
    import sys

    sys.path.insert(0, str((repo_root / "e1" / "src").resolve()))

    from e1_pipeline.db_init import init_all_dbs
    from e1_pipeline.wikipedia_api import run_wikipedia_api_collection
    from e1_pipeline.wikimedia_spark import run_wikimedia_titles_spark
    from e1_pipeline.wikipedia_etl import run_wikipedia_etl
    from e1_pipeline.file_ingest import run_file_ingestion
    from e1_pipeline.web_scraping import run_web_scraping
    from e1_pipeline.cleaning import run_cleaning
    from e1_pipeline.export_dataset import run_export_dataset

    init_all_dbs(config)
    print("[E1] DBs initialized OK")

    # Minimal step 1 (C1 - service web): Wikipedia API collection
    try:
        stats = run_wikipedia_api_collection(config)
        print(f"[E1] Wikipedia API: inserted={stats['inserted']} ignored={stats['ignored']} run_id={stats['run_id']}")
    except Exception as e:
        # Do not crash the whole pipeline on network issues
        print(f"[E1] Wikipedia API step skipped/failed: {e}")

    # Optional step (C1 - big data): Wikimedia dump titles via PySpark
    try:
        stats = run_wikimedia_titles_spark(config)
        print(
            "[E1] Wikimedia dump (Spark): status={status} inserted={inserted} ignored={ignored} dump={dump_path} run_id={run_id}".format(
                status=stats.get("status"),
                inserted=stats.get("inserted"),
                ignored=stats.get("ignored"),
                dump_path=stats.get("dump_path"),
                run_id=stats.get("run_id"),
            )
        )
    except Exception as e:
        print(f"[E1] Wikimedia dump (Spark) step skipped/failed: {e}")

    # Minimal step (ETL): staging Wikipedia DB -> flashcards2 raw_items
    try:
        stats = run_wikipedia_etl(config)
        print(
            "[E1] Wikipedia ETL: inserted={inserted} ignored={ignored} pages={pages} titles={titles} run_id={run_id}".format(
                inserted=stats["inserted"],
                ignored=stats["ignored"],
                pages=stats["inserted_pages"],
                titles=stats["inserted_titles"],
                run_id=stats["run_id"],
            )
        )
    except Exception as e:
        print(f"[E1] Wikipedia ETL step skipped/failed: {e}")

    # Minimal step 2 (C1 - fichiers): CSV/JSON/XML ingestion
    try:
        stats = run_file_ingestion(config)
        print(
            f"[E1] File ingestion: inserted={stats['inserted']} ignored={stats['ignored']} run_id={stats['run_id']}"
        )
    except Exception as e:
        print(f"[E1] File ingestion step skipped/failed: {e}")

    # Minimal step 3 (C1 - page web): scraping
    try:
        stats = run_web_scraping(config)
        print(
            f"[E1] Web scraping: inserted={stats['inserted']} ignored={stats['ignored']} errors={stats['errors']} run_id={stats['run_id']}"
        )
    except Exception as e:
        print(f"[E1] Web scraping step skipped/failed: {e}")

    # Minimal step 4 (C3): cleaning
    try:
        stats = run_cleaning(config)
        print(f"[E1] Cleaning: inserted={stats['inserted']} ignored={stats['ignored']} run_id={stats['run_id']}")
    except Exception as e:
        print(f"[E1] Cleaning step skipped/failed: {e}")

    # Minimal step 5 (A2): export dataset (CSV + JSONL)
    try:
        stats = run_export_dataset(config)
        print(
            "[E1] Export: rows={rows} csv={csv_path} jsonl={jsonl_path} run_id={run_id}".format(
                rows=stats["rows_count"],
                csv_path=stats["csv_path"],
                jsonl_path=stats["jsonl_path"],
                run_id=stats["run_id"],
            )
        )
    except Exception as e:
        print(f"[E1] Export step skipped/failed: {e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
