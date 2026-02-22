# RNCP E5 — Documentation / Communication

## What to prove (goal)
- You produce **clear technical documentation** and communicate how to run/maintain the system.
- You can onboard a reviewer quickly (setup, API, troubleshooting).

## Evidence checklist (repo)

### Technical documentation
- [ ] Database documentation + diagrams.
  - Evidence: `docs/database_*.md`, `docs/database_schema.md`
- [ ] Admin/system user explanation.
  - Evidence: `docs/admin_system_users.md`
- [ ] LLM benchmarking methodology.
  - Evidence: `docs/llm_benchmarking.md`

### Operational documentation
- [ ] How to run locally with Docker.
  - Evidence: top-level `README` (if present) + `docker-compose.yml`
- [ ] Troubleshooting notes (timeouts, cold start, memory limits).
  - Evidence: add to docs or link in report

### Communication artifacts (screenshots)
- [ ] Screenshots: application UI (upload → deck → study).
- [ ] Screenshots: CI green run, Grafana dashboard.

## Report scaffold (copy/paste headings)
1. **Audience & documentation scope**
2. **User guide (functional)**
   - How to use the app to generate/study flashcards.
3. **Technical guide**
   - Architecture, configuration, runbook.
4. **Ops guide**
   - Monitoring, logs, common failure modes.
5. **Appendix (evidence index)**
   - List of repo paths + screenshots.
