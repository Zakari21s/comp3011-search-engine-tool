"""Token extraction and normalization utilities for indexing."""

from __future__ import annotations

from dataclasses import dataclass
import re

TOKEN_PATTERN = re.compile(r"[a-z0-9']+")


@dataclass(frozen=True)
class Token:
    """Represent a normalized token and its order-based position."""

    term: str
    position: int


def tokenize(text: str) -> list[Token]:
    """Convert input text into lowercase tokens with 0-based positions.

    The tokenizer is intentionally simple and English-focused:
    - lowercases input
    - treats punctuation as separators
    - excludes pure numeric tokens
    - preserves token order for later phrase search
    """
    if not text or text.isspace():
        return []

    lowered_text = text.lower()
    tokens: list[Token] = []

    for raw_term in TOKEN_PATTERN.findall(lowered_text):
        normalized_term = raw_term.strip("'")
        if not normalized_term or normalized_term.isdigit():
            continue

        tokens.append(Token(term=normalized_term, position=len(tokens)))

    return tokens

