"""Utilities to determine how many flashcards to generate for a document.

We intentionally keep this logic in the backend so that:
- The frontend does not need to expose a setting for most users.
- We can tune the heuristic without changing the API.

LLM service currently validates `num_cards` with an upper bound (le=20).
"""

from __future__ import annotations

import math
import re


_WORD_RE = re.compile(r"[A-Za-zÀ-ÿ0-9]+(?:'[A-Za-zÀ-ÿ0-9]+)?")


def estimate_num_cards_for_text(
    text: str,
    *,
    min_cards: int,
    max_cards: int = 20,
    words_per_card: int = 250,
) -> int:
    """Estimate a good number of flashcards based on extracted text size.

    The heuristic uses an approximate *words-per-card* ratio and clamps the
    result between `min_cards` and `max_cards`.
    """

    min_cards_i = max(1, int(min_cards))
    max_cards_i = max(min_cards_i, int(max_cards))
    words_per_card_i = max(1, int(words_per_card))

    if not text or not str(text).strip():
        return min_cards_i

    words = len(_WORD_RE.findall(text))
    if words <= 0:
        # Fallback for unusual languages/text without word boundaries.
        chars = len(str(text).strip())
        estimated = int(math.ceil(chars / 1200))
    else:
        estimated = int(math.ceil(words / words_per_card_i))

    return max(min_cards_i, min(max_cards_i, estimated))
