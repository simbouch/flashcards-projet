# E1 — Wikipedia Data Pipeline

A self-contained data collection and preparation pipeline that harvests text from
Wikipedia and other public sources, cleans it, and exports it as structured datasets
(CSV / JSONL) ready for downstream use (e.g., flashcard generation).

The pipeline is **fully isolated** — it does not modify any running application service
and generates its own SQLite databases under `e1/data/`.

## How it works

```
Wikipedia API ─┐
Wikimedia dump ─┤─▶ staging DB ─▶ ETL ─┐
Web scraping  ─┤                        ├─▶ raw_items ─▶ cleaning ─▶ clean_items ─▶ export
CSV / JSON    ─┘                        │
                                        └─ (direct ingest)
```

### Data stores

| File | Role |
|---|---|
| `e1/data/wikipedia_external.db` | Staging — raw pages and title dumps from Wikipedia/Wikimedia |
| `e1/data/flashcards2.db` | Final dataset — unified raw items, cleaned items, export records |

Both databases are generated at runtime and are excluded from version control via
`e1/.gitignore`.

## Pipeline steps

1. **DB initialisation** — creates both SQLite databases and all tables on first run.
2. **Wikipedia API** — fetches article pages for configured keywords → `wiki_pages_raw`.
3. **Wikimedia dump** — processes a Wikimedia titles dump with PySpark → `wiki_titles_raw`
   *(optional; requires Java + PySpark; controlled by `auto_download` in `config.json`)*.
4. **Web scraping** — follows seed URLs and extracts text → `raw_items`.
5. **File ingest** — imports CSV, JSON, and XML sample files → `raw_items`.
6. **ETL** — copies Wikipedia staging data into the final `flashcards2.db.raw_items`.
7. **Cleaning** — normalises, deduplicates (SHA-256 hash), and quality-scores text → `clean_items`.
8. **Export** — writes the cleaned dataset to `e1/data/exports/` as CSV and JSONL.

## Configuration

All runtime parameters live in `e1/config/config.json`:

- `wikipedia_api.keywords` — search terms for article collection
- `wikipedia_api.search_limit` — maximum articles per keyword
- `wikimedia_dump.auto_download` — whether to download the full Wikimedia dump
- `wikimedia_dump.max_titles` — title limit when processing the dump
- `scraping.seed_urls` — starting URLs for the web scraper

## Running the pipeline

Run all steps in sequence:

```bash
python e1/run_all.py
```

## Tests

```bash
python -m pytest -c e1/pytest.ini -q e1/tests
```

Test coverage: DB initialisation, Wikipedia API client, ETL, file ingest, web scraping,
PySpark title processing, cleaning, and export.

## Documentation

| File | Description |
|---|---|
| [`docs/merise.md`](docs/merise.md) | Data model — MCD, MLD and physical schema for both SQLite databases |
| [`docs/rgpd.md`](docs/rgpd.md) | Privacy note — data minimisation, retention, and GDPR considerations |

## Dependencies

Install from `e1/requirements.txt`:

```bash
pip install -r e1/requirements.txt
```

> **Note:** PySpark step additionally requires Java 8+ on the host machine.
> It is skipped automatically when `auto_download` is `false` in `config.json`.
