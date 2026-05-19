# OCR Service

FastAPI microservice that extracts text from images and PDFs using
Tesseract OCR with OpenCV / Pillow preprocessing. Results are tracked in
MLflow and exposed through Prometheus metrics.

## Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness probe |
| `POST` | `/extract` | Extract text from an uploaded image or PDF |
| `GET` | `/metrics` | Prometheus exposition (auto-instrumented) |

`/extract` accepts a `multipart/form-data` upload (`file` field). Allowed
formats include common image types and PDF (PDF support requires PyMuPDF,
which is included in `requirements.txt`).

Rate limiting through `slowapi` defaults to `50/min` and `10/min` on
`/extract`. Redis is used when `REDIS_URL` is reachable, with an in-memory
fallback for testing.

## Layout

```
ocr_service/
├── dockerfile
├── requirements.txt
└── src/
    ├── main.py            # FastAPI app, routing, rate limit, metrics
    ├── mlflow_tracker.py  # MLflow run helpers
    └── logger_config.py
```

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `REDIS_URL` | `redis://redis:6379` | Rate-limit backend |
| `MLFLOW_TRACKING_URI` | `http://mlflow-ocr:5000` | MLflow server URL |
| `MLFLOW_EXPERIMENT_NAME` | `ocr_service_tracking` | MLflow experiment name |
| `TESTING` | `false` | Switches rate limiter to in-memory mode |

## Run

```bash
docker compose up -d ocr-service
```

Locally (Tesseract must be installed and on `PATH`):

```bash
cd ocr_service
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

The service is reachable at <http://localhost:8000> with OpenAPI docs at
`/docs`. The MLflow UI for OCR runs at <http://localhost:5000>.

## Tests

```bash
docker compose exec ocr-service pytest
```

or locally:

```bash
cd ocr_service
pytest
```
