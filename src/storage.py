"""Persistence layer for saving and loading indexes."""

from __future__ import annotations

from pathlib import Path

from indexer import InvertedIndex


class Storage:
    """Read/write search indexes from disk."""

    def save(self, index: InvertedIndex, output_path: Path) -> None:
        """Persist the index to disk."""
        # TODO: Serialize index structure in a stable JSON format.
        # TODO: Ensure parent directories are created safely.
        _ = (index, output_path)

    def load(self, input_path: Path) -> InvertedIndex:
        """Load an index from disk."""
        # TODO: Validate file presence and schema before loading.
        # TODO: Return clear exceptions/messages on read/parse errors.
        _ = input_path
        return {}

