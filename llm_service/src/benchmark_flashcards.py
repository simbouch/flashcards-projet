"""Simple benchmarking harness for flashcard generation.

Run inside llm-service container:
  python -m src.benchmark_flashcards --runs 2 --warmup 1

It measures:
- model init time
- per-run latency
- basic output validity + duplication heuristics

Results are written under `llm_service/src/_benchmarks/` (mounted to host).

For RNCP / report evidence, you can also write a copy of the JSON output to a
tracked directory (e.g. `llm_service/src/benchmarks_evidence/`) via --evidence-dir.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import statistics
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .flashcard_generator import FlashcardGenerator


@dataclass
class CardMetrics:
    total: int
    valid: int
    empty_q: int
    empty_a: int
    unique_questions: int
    avg_q_len: float
    avg_a_len: float


def _normalize_q(q: str) -> str:
    return " ".join((q or "").strip().lower().split())


def _score_cards(cards: List[Dict[str, Any]]) -> CardMetrics:
    qs = [str(c.get("question", "") or "") for c in cards]
    ans = [str(c.get("answer", "") or "") for c in cards]

    empty_q = sum(1 for q in qs if not q.strip())
    empty_a = sum(1 for a in ans if not a.strip())

    valid = 0
    for q, a in zip(qs, ans):
        if len(q.strip()) >= 5 and len(a.strip()) >= 3:
            valid += 1

    uq = len(set(_normalize_q(q) for q in qs if q.strip()))
    q_lens = [len(q.strip()) for q in qs if q.strip()]
    a_lens = [len(a.strip()) for a in ans if a.strip()]

    return CardMetrics(
        total=len(cards),
        valid=valid,
        empty_q=empty_q,
        empty_a=empty_a,
        unique_questions=uq,
        avg_q_len=round(statistics.mean(q_lens), 2) if q_lens else 0.0,
        avg_a_len=round(statistics.mean(a_lens), 2) if a_lens else 0.0,
    )


def _default_cases(max_chars: int) -> List[Tuple[str, str]]:
    cases = [
        (
            "fr_short",
            "L'intelligence artificielle (IA) vise à créer des systèmes capables d'exécuter des tâches nécessitant habituellement l'intelligence humaine.",
        ),
        (
            "fr_medium",
            "Le cycle de l'eau décrit la circulation continue de l'eau sur Terre : évaporation, condensation, précipitations et ruissellement. "
            "L'énergie solaire alimente l'évaporation, tandis que la gravité contribue au retour de l'eau vers les océans.",
        ),
        (
            "ocr_noisy",
            "CHAPITRE 2 : Reseaux neur0naux\nUn neurone artificiel calcule une somme ponderee des entrees puis applique une fonction d'activation. "
            "Objectif: apprendre des poids pour minimiser une erreur. (ex: descente de gradient)",
        ),
    ]
    out: List[Tuple[str, str]] = []
    for name, txt in cases:
        txt = txt.strip()
        if max_chars > 0 and len(txt) > max_chars:
            txt = txt[:max_chars]
        out.append((name, txt))
    return out


async def _run_one(generator: FlashcardGenerator, text: str, num_cards: int) -> Dict[str, Any]:
    return await generator.generate_flashcards(text=text, num_cards=num_cards)


async def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--num-cards", type=int, default=5)
    p.add_argument("--runs", type=int, default=2)
    p.add_argument("--warmup", type=int, default=1)
    p.add_argument("--max-chars", type=int, default=2000)
    p.add_argument("--input-file", type=str, default="")
    p.add_argument("--model-name", type=str, default="")
    p.add_argument(
        "--out-dir",
        type=str,
        default="",
        help="Directory to write raw benchmark JSON (default: src/_benchmarks)",
    )
    p.add_argument(
        "--evidence-dir",
        type=str,
        default="",
        help="Optional directory to ALSO write a copy of the JSON for git-tracked evidence",
    )
    p.add_argument(
        "--tag",
        type=str,
        default="",
        help="Optional tag appended to output filename (e.g. 'cpu', 'rtx3060', 'v1')",
    )
    p.add_argument(
        "--notes",
        type=str,
        default="",
        help="Optional short notes saved in the JSON (e.g. 'cold-start', 'after prompt tweak')",
    )
    args = p.parse_args()

    if args.model_name:
        os.environ["MODEL_NAME"] = args.model_name

    t0 = time.perf_counter()
    generator = FlashcardGenerator()
    init_s = time.perf_counter() - t0

    model_name = getattr(getattr(generator, "model", None), "model_name", os.getenv("MODEL_NAME", ""))
    device = getattr(getattr(generator, "model", None), "device", "")

    cases = _default_cases(args.max_chars)
    if args.input_file:
        txt = Path(args.input_file).read_text(encoding="utf-8", errors="ignore")
        if args.max_chars > 0 and len(txt) > args.max_chars:
            txt = txt[: args.max_chars]
        cases = [("input_file", txt)]

    results: Dict[str, Any] = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "model_name": model_name,
        "device": device,
        "init_seconds": round(init_s, 3),
        "num_cards": args.num_cards,
        "runs": args.runs,
        "warmup": args.warmup,
        "notes": args.notes,
        "cases": [],
    }

    for case_name, text in cases:
        for _ in range(max(args.warmup, 0)):
            await _run_one(generator, text, args.num_cards)

        run_times: List[float] = []
        last_payload: Dict[str, Any] = {}
        for _ in range(max(args.runs, 1)):
            t1 = time.perf_counter()
            last_payload = await _run_one(generator, text, args.num_cards)
            run_times.append(time.perf_counter() - t1)

        cards = list(last_payload.get("flashcards") or [])
        metrics = _score_cards(cards)

        results["cases"].append(
            {
                "name": case_name,
                "text_len": len(text),
                "latency_seconds": [round(x, 3) for x in run_times],
                "latency_mean": round(statistics.mean(run_times), 3),
                "latency_p95": round(sorted(run_times)[max(0, int(0.95 * len(run_times)) - 1)], 3),
                "card_metrics": asdict(metrics),
            }
        )

        print(
            f"[{case_name}] mean={statistics.mean(run_times):.2f}s cards={metrics.total} valid={metrics.valid} uniqueQ={metrics.unique_questions}"
        )

    safe_model = (model_name or "unknown").replace("/", "_")
    tag = (args.tag or "").strip().replace(" ", "_")
    tag_part = f"_{tag}" if tag else ""
    filename = f"benchmark_{safe_model}{tag_part}_{int(time.time())}.json"

    out_dir = Path(args.out_dir) if args.out_dir else (Path(__file__).parent / "_benchmarks")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename
    payload = json.dumps(results, indent=2, ensure_ascii=False)
    out_path.write_text(payload, encoding="utf-8")
    print(f"\nWrote results to: {out_path}")

    if args.evidence_dir:
        evidence_dir = Path(args.evidence_dir)
        evidence_dir.mkdir(parents=True, exist_ok=True)
        evidence_path = evidence_dir / filename
        evidence_path.write_text(payload, encoding="utf-8")
        print(f"Wrote evidence copy to: {evidence_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

