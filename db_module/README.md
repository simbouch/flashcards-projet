# Database Module

Shared persistence layer used by the backend service. It defines the
SQLAlchemy models, Pydantic schemas, CRUD helpers and the Alembic migration
environment.

## Responsibilities

- Declarative SQLAlchemy ORM models for users, refresh tokens, documents,
  extracted texts, decks, flashcards, study sessions and study records.
- Pydantic schemas used by the backend API for request/response validation.
- CRUD functions that encapsulate query logic (`crud.py`).
- Engine, session factory and `init_db()` bootstrap (`database.py`).
- Alembic migration scaffolding under `migrations/`.

## Layout

```
db_module/
├── Dockerfile
├── alembic.ini
├── requirements.txt
├── base.py            # Declarative base
├── models.py          # ORM models
├── schemas.py         # Pydantic schemas
├── crud.py            # CRUD helpers
├── database.py        # Engine, SessionLocal, init_db()
├── migrations/        # Alembic environment and versions
└── tests/             # Model and CRUD unit tests
```

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./data/flashcards.db` | SQLAlchemy URL |

The default is a SQLite file under `data/`. The same schema is portable to
PostgreSQL by changing the URL.

## Migrations

Alembic is configured in `alembic.ini` and `migrations/env.py`. From the
repository root:

```bash
# Create a new revision based on model changes
docker compose exec db-service alembic -c alembic.ini revision --autogenerate -m "msg"

# Apply pending migrations
docker compose exec db-service alembic -c alembic.ini upgrade head
```

On a fresh container, the backend calls `init_db()` during startup which
creates the schema if no migrations are applied (development convenience).

## Documentation

The schema is documented in detail under [`docs/`](../docs):

- [`database_mcd.md`](../docs/database_mcd.md) — Conceptual data model
- [`database_mpd.md`](../docs/database_mpd.md) — Physical data model
- [`database_schema.md`](../docs/database_schema.md) — Class diagram and overview
- [`database_diagrams/`](../docs/database_diagrams) — Rendered MCD/MLD/MPD images

## Tests

```bash
cd db_module
pytest
```
