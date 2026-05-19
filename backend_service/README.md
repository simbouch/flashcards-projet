# Backend Service

FastAPI application that exposes the Flashcards REST API. It orchestrates the
OCR and LLM services, persists data through `db_module`, and handles
authentication, authorization, rate limiting and Prometheus metrics.

## Responsibilities

- Authentication (JWT access + refresh tokens) and user management.
- Document upload, validation and proxying to the OCR service.
- Deck and flashcard CRUD, including AI-generated decks via the LLM service.
- Study sessions and review history.
- Admin operations (user listing, role updates, account deletion).
- Health checks (`/health`), Prometheus metrics (`/metrics`) and OpenAPI
  documentation (`/docs`).

## API surface

The router is mounted under `settings.API_V1_STR` (default `/api/v1`) and
organised by domain:

| Prefix | Source | Purpose |
|---|---|---|
| `/auth` | `src/api/endpoints/auth.py` | Register, login, refresh, logout |
| `/users` | `src/api/endpoints/users.py` | Profile, password change |
| `/admin` | `src/api/endpoints/admin.py` | Admin-only user management |
| `/documents` | `src/api/endpoints/documents.py` | Upload, OCR, retrieval |
| `/decks` | `src/api/endpoints/decks.py` | Deck CRUD and sharing |
| `/flashcards` | `src/api/endpoints/flashcards.py` | Card CRUD |
| `/study` | `src/api/endpoints/study.py` | Sessions and review records |

Top-level routes: `GET /`, `GET /health`, `GET /metrics`, `GET /docs`.

## Layout

```
backend_service/
├── Dockerfile
├── requirements.txt
└── src/
    ├── main.py              # FastAPI app, lifespan, CORS, Prometheus
    ├── config.py            # Pydantic settings (env-driven)
    ├── logger_config.py     # Loguru configuration
    ├── api/
    │   ├── deps.py          # Dependency injection (auth, DB session)
    │   └── endpoints/       # Route modules listed above
    ├── auth/                # Password hashing, token helpers
    ├── middleware/          # Rate limiter (slowapi + Redis)
    ├── scripts/             # bootstrap_admin, create_native_decks
    └── services/            # OCR and LLM HTTP clients
```

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./data/flashcards.db` | SQLAlchemy URL |
| `OCR_SERVICE_URL` | `http://ocr-service:8000` | OCR base URL |
| `LLM_SERVICE_URL` | `http://llm-service:8001` | LLM base URL |
| `LLM_SERVICE_TIMEOUT_SECONDS` | `300` | LLM HTTP timeout |
| `REDIS_URL` | `redis://redis:6379` | Backing store for rate limiting |
| `JWT_SECRET_KEY` | `supersecretkey` | **Override in production** |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token TTL |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | `30` | Refresh token TTL |
| `UPLOAD_DIR` | `./uploads` | Document upload destination |
| `MAX_UPLOAD_SIZE` | `10485760` | Max upload size in bytes (10 MB) |
| `CORS_ORIGINS` | `http://localhost:8080,...` | Comma-separated allowed origins |
| `INITIAL_ADMIN_USERNAME` | _empty_ | Optional admin bootstrap username |
| `INITIAL_ADMIN_PASSWORD` | _empty_ | Required to create admin on startup |
| `INITIAL_ADMIN_EMAIL` | _empty_ | Optional admin email |
| `INITIAL_ADMIN_FULL_NAME` | _empty_ | Optional admin full name |
| `INITIAL_ADMIN_ALLOW_PROMOTE_EXISTING` | `false` | Promote existing user to admin |

See [`docs/admin_system_users.md`](../docs/admin_system_users.md) for the
admin bootstrap workflow.

## Run

The service is normally started through Docker Compose from the repository
root:

```bash
docker compose up -d backend-service
```

Locally:

```bash
cd backend_service
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8002 --reload
```

The API will be available at `http://localhost:8002`, with interactive docs
at `http://localhost:8002/docs`.

## Tests

```bash
# Inside the container
docker compose exec backend-service pytest

# Or locally
cd backend_service
pytest
```

Test layout, fixtures and markers are documented in
[`tests/README.md`](tests/README.md) and
[`tests/TESTING_GUIDE.md`](tests/TESTING_GUIDE.md).
