## LLM Benchmarks — Evidence (tracked)

This folder is **committed to git** and contains a small set of benchmark JSON files
exported by `src/benchmark_flashcards.py` via `--evidence-dir`.

Purpose:
- Keep a stable, reviewable history of *which models were tested* and *what we observed*
  (latency, output stability, basic quality heuristics).

Notes:
- Raw/local runs are written to `src/_benchmarks/` (gitignored).
- Do **not** put huge artifacts here (model weights, caches). Only JSON summaries.
