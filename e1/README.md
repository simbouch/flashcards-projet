## E1 — Data pipeline (isolated)

This folder contains an **isolated E1 data pipeline**.

Constraints respected:
- no changes to existing API/DB/OCR services
- everything lives under `e1/`
- two SQLite databases generated at runtime:
  - `e1/data/wikipedia_external.db` (staging Wikipedia)
  - `e1/data/flashcards2.db` (final cleaned/aggregated dataset)

### Docs (for the RNCP E1 evidence)

- Merise (C4): `e1/docs/merise.md`
- RGPD (C4): `e1/docs/rgpd.md`
- C5 proof (existing API): `e1/docs/c5_api_proof.md`

### Run (all steps)

```bash
python e1/run_all.py
```

### Checklist (incremental)

- [x] Init 2 SQLite DBs: `wikipedia_external.db` (staging) + `flashcards2.db` (final)
- [x] C1 service web: collect pages via Wikipedia API → `wikipedia_external.db.wiki_pages_raw`
- [x] ETL: copy Wikipedia staging (`wikipedia_external.db`) → `flashcards2.db.raw_items`
- [x] C1 fichiers: ingest CSV/JSON/XML samples → `flashcards2.db.raw_items`
- [x] C1 big data: Wikimedia titles dump via PySpark → `wikipedia_external.db.wiki_titles_raw` (requires PySpark + Java; dump download is optional via config)
- [x] C1 web scraping: collect text from web pages → `flashcards2.db.raw_items`
- [*] C1/C2 SQL + CRUD: already covered by the existing project API/CRUD (no extra implementation in `e1/`)
- [-] C1 NoSQL: not included (SQLite-only for E1 scope)
- [x] C3 cleaning: normalize + deduplicate + quality scoring → `flashcards2.db.clean_items`
- [x] A2 export: export dataset (CSV + JSONL) → `e1/data/exports/` + `flashcards2.db.datasets`

### Run tests

Recommended (pytest):

```bash
python -m pytest -c e1/pytest.ini -q e1/tests
```

Legacy (unittest runner):

```bash
python -m unittest discover -s e1/tests -p "test_*.py" -v
```
