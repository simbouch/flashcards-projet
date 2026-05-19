# Project Documentation

This folder contains the reference documentation for the Flashcards application:
data model, database schema, LLM benchmarking methodology, and admin account
management.

## Contents

| Document | Purpose |
|---|---|
| [database_mcd.md](database_mcd.md) | Conceptual Data Model (entities and relationships) |
| [database_mpd.md](database_mpd.md) | Physical Data Model (tables, columns, constraints) |
| [database_schema.md](database_schema.md) | Database class diagram and overview |
| [database_diagrams/](database_diagrams/) | Rendered MCD / MLD / MPD diagrams (PNG) |
| [llm_benchmarking.md](llm_benchmarking.md) | LLM benchmarking methodology, commands and evidence locations |
| [admin_system_users.md](admin_system_users.md) | Initial admin bootstrap and the reserved `system` account |
| [MONITORING_GUIDE.md](MONITORING_GUIDE.md) | Monitoring walkthrough — Prometheus, Grafana, Alertmanager |
| [SECURITY.md](SECURITY.md) | Security policy and vulnerability reporting |
| [PRIVACY.md](PRIVACY.md) | Privacy policy for the application |

> Mermaid diagrams render natively on GitHub and in VS Code with the Mermaid
> extension. You can also paste the code blocks into the
> [Mermaid Live Editor](https://mermaid.live/).

## Database overview

The schema is organised around the following groups of entities (full details in
[database_schema.md](database_schema.md)):

- **Users and authentication** — `users`, `refresh_tokens`
- **Documents and processing** — `documents`, `extracted_texts`
- **Flashcards and decks** — `decks`, `flashcards`, `user_deck_association`
- **Study and review** — `study_sessions`, `study_records`

## Implementation references

The runtime implementation lives in:

- `db_module/models.py` — SQLAlchemy ORM models
- `db_module/database.py` — engine and session configuration
- `db_module/schemas.py` — Pydantic schemas for API validation
- `db_module/crud.py` — CRUD helpers used by the backend service

## Design notes

- **UUID primary keys** for security and portability between environments.
- **Association tables** (e.g. `user_deck_association`) for many-to-many links.
- **Timestamps** (`created_at`, `updated_at`) on user-facing entities.
- **Enumerations** for document status and user roles to keep values consistent.
- **SQLite by default** for local development; the schema is portable to
  PostgreSQL by switching `DATABASE_URL`.
