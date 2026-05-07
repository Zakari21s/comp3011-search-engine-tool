"""Unit tests for Stage 1 tokenizer behavior."""

from __future__ import annotations

from src.tokenizer import Token, tokenize


def test_tokenize_lowercase_handling() -> None:
    """Tokenizer should lowercase all extracted terms."""
    assert tokenize("HeLLo WORLD") == [
        Token(term="hello", position=0),
        Token(term="world", position=1),
    ]


def test_tokenize_punctuation_removal() -> None:
    """Punctuation should act as separators, not tokens."""
    assert tokenize("Hello, world! This... is; fine.") == [
        Token(term="hello", position=0),
        Token(term="world", position=1),
        Token(term="this", position=2),
        Token(term="is", position=3),
        Token(term="fine", position=4),
    ]


def test_tokenize_repeated_words() -> None:
    """Repeated words should remain repeated with unique positions."""
    assert tokenize("echo echo echo") == [
        Token(term="echo", position=0),
        Token(term="echo", position=1),
        Token(term="echo", position=2),
    ]


def test_tokenize_empty_text_returns_empty_list() -> None:
    """Empty text should return no tokens."""
    assert tokenize("") == []


def test_tokenize_whitespace_only_returns_empty_list() -> None:
    """Whitespace-only text should return no tokens."""
    assert tokenize(" \n\t  ") == []


def test_tokenize_mixed_spacing_newlines_tabs() -> None:
    """Mixed whitespace should not affect token order."""
    assert tokenize("alpha\tbeta\n\ngamma   delta") == [
        Token(term="alpha", position=0),
        Token(term="beta", position=1),
        Token(term="gamma", position=2),
        Token(term="delta", position=3),
    ]


def test_tokenize_position_tracking_in_order() -> None:
    """Positions should be 0-based and increase by token order."""
    terms_and_positions = [(token.term, token.position) for token in tokenize("a b c d")]
    assert terms_and_positions == [("a", 0), ("b", 1), ("c", 2), ("d", 3)]


def test_tokenize_excludes_pure_numbers() -> None:
    """Pure numeric terms should be excluded."""
    assert tokenize("123 45 007") == []


def test_tokenize_words_with_numbers_consistent_handling() -> None:
    """Alphanumeric words should be kept while pure numbers are skipped."""
    assert tokenize("v2 model3 2026 r2d2 99bottles 123") == [
        Token(term="v2", position=0),
        Token(term="model3", position=1),
        Token(term="r2d2", position=2),
        Token(term="99bottles", position=3),
    ]
