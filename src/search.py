"""Query processing and retrieval orchestration."""

from __future__ import annotations

from dataclasses import dataclass

from indexer import InvertedIndex
from ranking import RankedResult


@dataclass(slots=True)
class SearchResponse:
    """Container for search output and optional suggestion text."""

    query: str
    results: list[RankedResult]
    suggestion: str | None = None


class SearchEngine:
    """Handle query parsing, matching, phrase checks, and ranking."""

    def __init__(self, index: InvertedIndex) -> None:
        self._index = index

    def find(self, query: str) -> SearchResponse:
        """Search the index and return ranked matches."""
        # TODO: Handle single-word queries.
        # TODO: Handle multi-word queries and phrase search using positions.
        # TODO: Add query suggestions for unknown terms.
        _ = query
        return SearchResponse(query=query, results=[], suggestion=None)

