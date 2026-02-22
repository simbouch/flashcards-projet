# RNCP E2 — Développement / Déploiement / Exploitation

## What to prove (goal)
- You can **package, deploy, run, and operate** the application reliably.
- You can show repeatable build/run steps + basic production concerns.

## Evidence checklist (repo + screenshots)

### Containerization / deployment
- [ ] `docker-compose.yml` defines the microservices and their ports/volumes.
  - Evidence: `docker-compose.yml`
- [ ] Each service has a Dockerfile.
  - Evidence: `backend_service/Dockerfile`, `ocr_service/Dockerfile`, `llm_service/Dockerfile`, `frontend_service/Dockerfile`
- [ ] Environment-based configuration (URLs, secrets, model selection).
  - Evidence: services read env vars (see `backend_service/src/config.py`, `llm_service/src/main.py`)
- [ ] Runbook: start/stop + health.
  - Evidence (commands to capture):
    - `docker compose up -d`
    - `docker compose ps`
    - `docker compose logs -n 200 backend-service llm-service ocr-service`

### CI/CD and release
- [ ] CI runs lint/tests/builds.
  - Evidence: `.github/workflows/ci.yml`
- [ ] Release workflow builds & pushes images.
  - Evidence: `.github/workflows/release.yml`
- [ ] Screenshot evidence: GitHub Actions run (green) for `dev`.

### Observability (monitoring)
- [ ] Prometheus scraping configured for services.
  - Evidence: `monitoring/prometheus.yml`
- [ ] Grafana dashboards/provisioning present.
  - Evidence: `monitoring/grafana/provisioning/**`, `monitoring/grafana/dashboards/**`
- [ ] Screenshot evidence: Grafana dashboard (overview or per-service).

## Report scaffold (copy/paste headings)
1. **Architecture & deployment target**
   - Microservices overview, ports, service-to-service calls.
2. **Packaging**
   - Dockerfiles, docker-compose, volumes, env variables.
3. **Runbook**
   - Commands to run locally; how to validate readiness.
4. **CI/CD**
   - What the pipeline checks; branch strategy.
5. **Operations / monitoring**
   - Metrics endpoints, Prometheus + Grafana, example alerts (if any).
6. **Risks & mitigations**
   - Cold starts (LLM), timeouts, resource constraints (CPU/RAM), secrets handling.
