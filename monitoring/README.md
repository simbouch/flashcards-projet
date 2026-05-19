# Monitoring Stack

Prometheus, Grafana, Alertmanager and supporting exporters that observe
the Flashcards application. The stack is defined in
[`docker-compose.monitoring.yml`](../docker-compose.monitoring.yml) and the
configuration lives in this folder.

## Components

| Container | Port | Role |
|---|---|---|
| `prometheus` | 9090 | Metrics scraping and storage |
| `grafana` | 3000 | Dashboards and visualisation |
| `alertmanager` | 9093 | Alert routing |
| `node-exporter` | 9100 | Host-level metrics |
| `cadvisor` | 8081 | Container metrics |
| `redis-exporter` | 9121 | Redis metrics |

Two MLflow tracking servers (`mlflow-ocr` on `5000`, `mlflow-llm` on `5001`)
are defined in the main `docker-compose.yml` and complement this stack.

## Layout

```
monitoring/
├── prometheus.yml       # Scrape config and targets
├── alert_rules.yml      # Alerting rules (severity, thresholds)
├── alertmanager.yml     # Alertmanager routing and receivers
└── grafana/
    ├── provisioning/    # Datasources and dashboard provisioning
    └── dashboards/      # JSON dashboards (auto-loaded by Grafana)
```

## Run

```bash
# Application services
docker compose up -d

# Monitoring stack (alongside the app)
docker compose -f docker-compose.monitoring.yml up -d
```

## Access

| Service | URL | Credentials |
|---|---|---|
| Grafana | <http://localhost:3000> | `admin` / `flashcards2024` |
| Prometheus | <http://localhost:9090> | — |
| Alertmanager | <http://localhost:9093> | — |
| cAdvisor | <http://localhost:8081> | — |
| Node Exporter | <http://localhost:9100/metrics> | — |
| Redis Exporter | <http://localhost:9121/metrics> | — |

Grafana credentials are configured via `GF_SECURITY_ADMIN_USER` and
`GF_SECURITY_ADMIN_PASSWORD` in `docker-compose.monitoring.yml`.

## Application metrics endpoints

Each FastAPI service exposes a Prometheus endpoint that the stack scrapes:

- Backend — <http://localhost:8002/metrics>
- LLM — <http://localhost:8001/metrics>
- OCR — <http://localhost:8000/metrics>

## More

A more detailed walkthrough (architecture, key metrics, dashboards and
alert thresholds) is available in
[`MONITORING_GUIDE.md`](../MONITORING_GUIDE.md).
