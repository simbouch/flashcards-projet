## LLM benchmarking (Flashcards generation)

This document explains **how we benchmarked LLM models** for the flashcards generator.

### Goals

- Compare candidate models on:
  - **Initialization time** (cold start)
  - **Generation latency** (per request)
  - **Output stability / basic quality** (valid Q/A, duplicates)
- Keep reproducible **evidence artifacts** for the RNCP deliverables.

### Where results are stored

- Local/raw runs (auto-generated, not committed):
  - `llm_service/src/_benchmarks/` *(gitignored)*
- Evidence runs (selected results committed to git):
  - `llm_service/src/benchmarks_evidence/`

### How to run a benchmark

Run inside the llm-service container:

```bash
# Example: benchmark a candidate model and save an evidence copy
docker compose run --rm llm-service \
  python -m src.benchmark_flashcards \
  --model-name "Qwen/Qwen2.5-0.5B-Instruct" \
  --runs 2 --warmup 1 --num-cards 5 --max-chars 1200 \
  --tag "cpu" \
  --evidence-dir /app/src/benchmarks_evidence
```

Notes:
- The LLM service post-processes model output to **filter/deduplicate** cards and **cap** to the requested count (makes benchmarks comparable across models).
- You can tweak generation via env vars (useful for benchmarking): `LLM_TEMPERATURE`, `LLM_TOP_P`, `LLM_REPETITION_PENALTY`, `LLM_CHUNK_GEN_ATTEMPTS`.
- For larger CPU models, you may hit Docker memory limits (OOM / exit 137). You can try `LLM_CPU_DTYPE=float16` (or `bfloat16`) and/or increase Docker Desktop memory.

### How to run end-to-end (upload → OCR → LLM → flashcards)

We use host-level integration tests (talking to running Docker services):

```powershell
$env:RUN_E2E='1'
python -m pytest -c tests/integration/pytest.ini -q
```

If you want to restart the LLM service with a different model (no code change):

```powershell
$env:LLM_MODEL_NAME='Qwen/Qwen2.5-0.5B-Instruct'
docker compose up -d --force-recreate llm-service
```

### Interpreting metrics (quick)

- `init_seconds`: cold start cost for model + tokenizer load
- `latency_mean` / `latency_p95`: generation speed
- `card_metrics`:
  - `valid`: Q/A pairs meeting minimal length checks
  - `unique_questions`: rough duplicate detector (higher is better)

### Evidence summary (tracked)

The following benchmark runs are committed under `llm_service/src/benchmarks_evidence/`.

| Model | Evidence file | init_seconds | Latency mean (per case) | Cards returned (total/unique) | Notes / verdict |
|---|---|---:|---:|---:|---|
| `Qwen/Qwen2.5-0.5B-Instruct` | `benchmark_Qwen_Qwen2.5-0.5B-Instruct_v2_1771638748.json` | **12.1s** | **39–55s** | **3–5 / 3–5** | Best overall quality (valid + diverse). **Selected default** (docker-compose default updated). |
| `bigscience/bloom-560m` | `benchmark_bigscience_bloom-560m_v2_1771636554.json` | 13.1s | 103–159s | 1–2 / 1–2 | Under-generates + long answers; slower than Qwen. |
| `distilgpt2` | `benchmark_distilgpt2_distilgpt2_v1_1771650464.json` | 196.1s | 4–19s | 1 / 1 | Non-instruct model: doesn’t follow strict Q/R format → parsing fallback → under-generates. |
| `gpt2` | `benchmark_gpt2_gpt2_v1_1771659183.json` | 134.2s | 57–76s | 1 / 1 | Non-instruct model: very slow and under-generates (format mismatch → fallback). |
| `EleutherAI/gpt-neo-125M` | `benchmark_EleutherAI_gpt-neo-125M_gptneo125m_v1_1771661549.json` | 66.1s | 94–96s | 1–3 / 1–3 | Slightly better count on some cases, but still too slow + inconsistent formatting. |
| `TinyLlama/TinyLlama-1.1B-Chat-v1.0` (float32) | `benchmark_TinyLlama_TinyLlama-1.1B-Chat-v1.0_failed_exit137_2026-02-20.json` | — | — | — | OOM killed (exit 137) under Docker memory limit. |
| `TinyLlama/TinyLlama-1.1B-Chat-v1.0` (`LLM_CPU_DTYPE=float16`) | `benchmark_TinyLlama_TinyLlama-1.1B-Chat-v1.0_tinyllama_fp16_v2_1771647009.json` | 1274.9s | 223–364s | 1 / 1 | Extremely slow on CPU and still under-generates (parsing fallback). Skip for default. |

Notes:
- Benchmarks must be deterministic and non-blocking: we intentionally **do not** call `nltk.download()` at runtime inside the container (fallback sentence splitting is used when punkt data is missing).
- Cold start: llm-service now does **non-blocking** startup; use `/health` (liveness) and `/ready` (model readiness) if you need to distinguish “HTTP up” vs “model loaded”.
