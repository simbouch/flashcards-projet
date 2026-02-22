# RNCP E3 — Qualité / Tests / Validation

## What to prove (goal)
- You ensure **code quality** and **functional correctness** with tests + tooling.
- You can validate the full pipeline (upload → OCR → LLM → flashcards).

## Evidence checklist (repo + commands)

### Automated tests
- [ ] Unit tests exist for core services.
  - Evidence: `backend_service/tests/`, `db_module/tests/`, `ocr_service/tests/`, `llm_service/tests/`
- [ ] Integration/E2E tests exist (host talking to running Docker services).
  - Evidence: `tests/integration/` + `tests/integration/pytest.ini`
- [ ] Central pytest config / markers.
  - Evidence: `pytest.ini`

### Linting / static checks
- [ ] Frontend lint script exists.
  - Evidence: `frontend_service/package.json` (script `lint`)
- [ ] Backend linting in CI.
  - Evidence: `.github/workflows/ci.yml` (flake8)

### AI-specific validation
- [ ] LLM benchmarking methodology + tracked evidence artifacts.
  - Evidence: `docs/llm_benchmarking.md`, `llm_service/src/benchmarks_evidence/`
- [ ] Output parsing robustness (handles edge cases like markdown fences).
  - Evidence: `llm_service/src/model.py::parse_qa_pairs` + `llm_service/tests/test_model_parsing.py`

## Report scaffold (copy/paste headings)
1. **Test strategy**
   - Unit vs integration; what is mocked and what is real.
2. **Coverage of critical flows**
   - Upload pipeline, auth, admin actions (if included), deck/flashcards.
3. **Quality gates**
   - Linting, CI checks, failure handling.
4. **AI validation**
   - Benchmark approach, constraints (OOM), chosen model rationale.
5. **Known limitations**
   - What is not tested yet and why; plan to improve.
