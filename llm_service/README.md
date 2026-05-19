# LLM Service

FastAPI microservice that generates flashcards from a block of text using a
Hugging Face transformer model. It exposes a small HTTP API consumed by the
backend, tracks experiments with MLflow, and publishes Prometheus metrics.

## Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Service identity |
| `GET` | `/health` | Liveness probe |
| `GET` | `/ready` | Readiness probe (reports model init state) |
| `POST` | `/generate` | Generate flashcards from a single text block |
| `POST` | `/generate/chunks` | Generate from pre-split chunks |
| `POST` | `/feedback` | Persist user feedback on a generation |
| `GET` | `/metrics/performance` | Model-level performance counters |
| `GET` | `/metrics` | Prometheus exposition (auto-instrumented) |

Per-IP rate limits are enforced through `slowapi` (default `30/min`,
`5/min` on `/generate*`). When `REDIS_URL` is reachable, the limiter is
backed by Redis; otherwise it falls back to in-memory storage.

## Layout

```
llm_service/
├── Dockerfile
├── requirements.txt
└── src/
    ├── main.py                  # FastAPI app, routing, rate limit, metrics
    ├── flashcard_generator.py   # High-level generation pipeline
    ├── model.py                 # Transformer loading / inference
    ├── model_evaluator.py       # Quality scoring of generated cards
    ├── data_collector.py        # User interactions + feedback persistence
    ├── mlflow_tracker.py        # MLflow run helpers
    ├── benchmark_flashcards.py  # Offline benchmarking entry point
    └── logger_config.py
```

The model is loaded asynchronously on first request (`_ensure_generator_initialized`)
so the HTTP server starts immediately and `/ready` reports the loading state.

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `MODEL_NAME` | `Qwen/Qwen2.5-0.5B-Instruct` | Hugging Face model id |
| `LLM_CPU_DTYPE` | `float32` | CPU dtype (`float32` or `float16`) |
| `REDIS_URL` | `redis://redis:6379` | Rate-limit backend |
| `MLFLOW_TRACKING_URI` | `http://mlflow-llm:5001` | MLflow server URL |
| `MLFLOW_EXPERIMENT_NAME` | `llm_service_tracking` | MLflow experiment name |
| `TESTING` | `false` | Switches rate limiter to in-memory mode |

## Run

```bash
docker compose up -d llm-service
```

Locally:

```bash
cd llm_service
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8001
```

The service is reachable at <http://localhost:8001> with OpenAPI docs at
`/docs`. MLflow UI for this service runs at <http://localhost:5001>.

## Benchmarking

A reproducible benchmarking script is included to compare models or settings:

```bash
docker compose exec llm-service python -m src.benchmark_flashcards --help
```

Methodology and command examples are documented in
[`docs/llm_benchmarking.md`](../docs/llm_benchmarking.md).

## Tests

```bash
docker compose exec llm-service pytest
```

or locally:

```bash
cd llm_service
pytest
```
