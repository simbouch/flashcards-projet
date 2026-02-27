from backend_service.src.services.flashcard_count import estimate_num_cards_for_text


def test_estimate_num_cards_respects_min_and_max():
    # Empty/whitespace => min
    assert estimate_num_cards_for_text("", min_cards=5, max_cards=20) == 5
    assert estimate_num_cards_for_text("   ", min_cards=5, max_cards=20) == 5

    # Very small text => min
    assert estimate_num_cards_for_text("hello world", min_cards=5, max_cards=20) == 5

    # Big text => capped at max
    big = "word " * 100_000
    assert estimate_num_cards_for_text(big, min_cards=5, max_cards=20) == 20


def test_estimate_num_cards_scales_with_words():
    # 250 words/card heuristic: 750 words => 3 cards, but clamped to min=1
    text = "word " * 750
    assert estimate_num_cards_for_text(text, min_cards=1, max_cards=20, words_per_card=250) == 3
