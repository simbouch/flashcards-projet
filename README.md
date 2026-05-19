# Flashcards Project

A microservice-based application that turns documents (PDF or image) into
study flashcards. Text is extracted by an OCR service, an LLM service
generates question / answer pairs from the extracted text, and a FastAPI
backend exposes the full workflow through a Vue.js frontend. A complete
monitoring stack (Prometheus, Grafana, Alertmanager) and two MLflow
tracking servers are bundled for observability and experiment tracking.

## Architecture

```
┌────────────┐   HTTPS    ┌──────────────┐   HTTP    ┌──────────────┐
│  Frontend  │ ─────────▶ │   Backend    │ ────────▶ │ OCR service  │
│  (Vue 3)   │            │  (FastAPI)   │           │ (Tesseract)  │
└────────────┘            └──────┬───────┘           └──────────────┘
                                 │
                                 │ HTTP                ┌──────────────┐
                                 ├────────────────────▶│ LLM service  │
                                 │                     │ (Transformers)│
                                 │                     └──────────────┘
                                 │
                                 ▼
                          ┌──────────────┐         ┌──────────────┐
                          │   db_module  │         │    Redis     │
                          │ (SQLAlchemy) │         │ (rate limit) │
                          └──────────────┘         └──────────────┘
```

The monitoring stack scrapes the `/metrics` endpoint of each FastAPI service,
plus Node Exporter, cAdvisor and Redis Exporter.

## Services

| Service | Port | Description | README |
|---|---|---|---|
| Frontend | 8080 | Vue 3 SPA served by Nginx | [frontend_service](frontend_service/README.md) |
| Backend | 8002 | FastAPI REST API | [backend_service](backend_service/README.md) |
| OCR | 8000 | Text extraction (Tesseract) | [ocr_service](ocr_service/README.md) |
| LLM | 8001 | Flashcard generation (Transformers) | [llm_service](llm_service/README.md) |
| Database module | — | SQLAlchemy models and CRUD | [db_module](db_module/README.md) |
| MLflow (OCR) | 5000 | Experiment tracking for OCR | — |
| MLflow (LLM) | 5001 | Experiment tracking for LLM | — |
| Redis | 6379 | Rate-limiting backend | — |
| Monitoring | 3000 / 9090 / 9093 | Grafana / Prometheus / Alertmanager | [monitoring](monitoring/README.md) |

## Requirements

- Docker and Docker Compose v2
- ~6 GB of available RAM for the LLM container (configurable)

## Quick start

```bash
git clone <repository-url>
cd flashcards-project
cp .env.example .env       # adjust values as needed
docker compose up -d
```

Optionally start the monitoring stack:

```bash
docker compose -f docker-compose.monitoring.yml up -d
```

Once the containers are healthy:

| URL | Purpose |
|---|---|
| <http://localhost:8080> | Web application |
| <http://localhost:8002/docs> | Backend OpenAPI documentation |
| <http://localhost:8000/docs> | OCR service OpenAPI documentation |
| <http://localhost:8001/docs> | LLM service OpenAPI documentation |
| <http://localhost:3000> | Grafana (default `admin` / `flashcards2024`) |
| <http://localhost:9090> | Prometheus |
| <http://localhost:5000> / <http://localhost:5001> | MLflow (OCR / LLM) |

## Configuration

Environment variables are loaded from `.env` (see `.env.example` for a
template). Per-service settings, including the optional initial admin
bootstrap, are described in each service README and in
[`docs/admin_system_users.md`](docs/admin_system_users.md).

The default JWT secret in `.env.example` is a placeholder and **must** be
replaced before any non-local deployment.

## Tests

Each service ships its own pytest suite. From the repository root:

```bash
docker compose exec backend-service pytest
docker compose exec llm-service pytest
docker compose exec ocr-service pytest
```

The backend test layout is described in
[`backend_service/tests/README.md`](backend_service/tests/README.md).

## Documentation

Project-level documentation lives under [`docs/`](docs/README.md):

- Data model — MCD, MPD, schema and rendered diagrams
- LLM benchmarking methodology
- Admin and system user management

Operational guides:

- [`docs/MONITORING_GUIDE.md`](docs/MONITORING_GUIDE.md) — Detailed monitoring walkthrough
- [`docs/SECURITY.md`](docs/SECURITY.md) — Security policy and reporting
- [`docs/PRIVACY.md`](docs/PRIVACY.md) — Privacy policy

## Repository layout

```
flashcards-project/
├── backend_service/     # FastAPI backend
├── frontend_service/    # Vue.js 3 SPA
├── llm_service/         # Flashcard generation service
├── ocr_service/         # OCR service
├── db_module/           # Shared SQLAlchemy models / Alembic
├── mlflow/              # MLflow tracking Dockerfiles
├── monitoring/          # Prometheus, Grafana, Alertmanager config
├── docs/                # Data model and reference documentation
├── tests/               # Cross-service integration tests
├── docker-compose.yml
├── docker-compose.monitoring.yml
└── .env.example
```

## License

See [`LICENSE`](LICENSE).
