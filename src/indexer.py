"""Inverted index construction and maintenance."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Posting:
    """Posting entry for one term within one document."""

    doc_id: str
    frequency: int
    positions: list[int] = field(default_factory=list)


InvertedIndex = dict[str, list[Posting]]


class Indexer:
    """Build and update an inverted index from token streams."""

    def __init__(self) -> None:
        self._index: InvertedIndex = {}

    @property
    def index(self) -> InvertedIndex:
        """Return the current in-memory inverted index."""
        return self._index

    def add_document(self, doc_id: str, tokens: list[str]) -> None:
        """Add one tokenized document to the index."""
        # TODO: Populate postings with frequency and positional data.
        # TODO: Keep updates deterministic for easier debugging/testing.
        _ = (doc_id, tokens)

    def clear(self) -> None:
        """Reset the in-memory index to an empty state."""
        self._index = {}

