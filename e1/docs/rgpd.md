# Privacy Note — E1 Data Pipeline

Scope: the `e1/` data collection and preparation pipeline, which operates exclusively on **publicly available data**.

## 1. Nature of data processed

**Sources:**
- Wikipedia API (public encyclopaedic content)
- Wikimedia title dumps (public page titles)
- Web scraping (public web pages, primarily Wikipedia)
- Sample CSV / JSON / XML files (for pipeline testing)

**Data type:** plain text (article content, titles, excerpts) and technical metadata (URL, page ID). No user-generated or behavioural data.

## 2. Personal data

- **Objective:** avoid any processing of personal data.
- **Residual risk:** a public web page may incidentally contain proper names.
- **Mitigation:** collection is limited to a small volume (controlled by `search_limit`, `max_titles`, etc.) and stored locally only — no publication or sharing.

## 3. Purpose and legal basis

The pipeline collects and prepares open-licence text datasets for downstream NLP and flashcard generation tasks. All source content is published under open licences (Creative Commons / Wikipedia terms of use). Processing relies on the legitimate interest of building a local, non-commercial dataset from publicly available information.

## 4. Data minimisation

- Only strictly necessary fields are stored: text content, SHA-256 hash, and minimal metadata.
- No user identifiers, email addresses, or IP addresses are stored.
- Volume is bounded by configuration parameters.

## 5. Retention

Generated databases are **local artefacts** excluded from version control (`e1/.gitignore`):

- `e1/data/wikipedia_external.db`
- `e1/data/flashcards2.db`
- `e1/data/exports/`

To delete all collected data: remove `e1/data/*.db` and `e1/data/exports/*`.

## 6. Security

- All storage is local (development machine); no network exposure.
- SHA-256 deduplication reduces redundant records and supports audit.
- The `runs` table provides full traceability (timestamps, status, parameters).

## 7. Individual rights

If personal data were to appear in a collected public page:

- **Access / erasure:** delete the relevant rows by `content_hash` or URL, or drop the database entirely.
- **Portability:** data is exportable as CSV and JSONL from `e1/data/exports/`.

## 8. Operational guidelines

- Do not configure seed URLs that target pages about private individuals.
- Keep collection volumes low.
- Retain source references (URL, `page_id`) only for audit purposes.
