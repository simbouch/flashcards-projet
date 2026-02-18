"""Unit tests for Q/A parsing utilities.

These tests must NOT load the actual HuggingFace model.
"""

from src.model import parse_qa_pairs


def test_parse_qa_pairs_basic_french():
    text = """Q: Qu'est-ce que Python ?
R: Un langage de programmation.
Q: A quoi sert une variable ?
R: A stocker une valeur.
"""
    cards = parse_qa_pairs(text)
    assert len(cards) == 2
    assert cards[0]["question"].lower().startswith("qu")
    assert "langage" in cards[0]["answer"].lower()


def test_parse_qa_pairs_accepts_english_answer_prefix():
    text = """Q: What is a list?
A: A collection of items.
"""
    cards = parse_qa_pairs(text)
    assert len(cards) == 1
    assert "collection" in cards[0]["answer"].lower()


def test_parse_qa_pairs_multiline_answer():
    text = """Q: Explain JWT
R: JSON Web Token.
It is commonly used for stateless auth.
"""
    cards = parse_qa_pairs(text)
    assert len(cards) == 1
    assert "stateless" in cards[0]["answer"].lower()


def test_parse_qa_pairs_inline_qr_same_line():
    text = "Q: Capital of France? R: Paris"
    cards = parse_qa_pairs(text)
    assert len(cards) == 1
    assert cards[0]["answer"].strip().lower() == "paris"


def test_parse_qa_pairs_fallback_non_empty_when_unparseable():
    text = "This output does not follow the expected format."
    cards = parse_qa_pairs(text)
    assert len(cards) == 1
    assert cards[0]["question"]
    assert cards[0]["answer"]

