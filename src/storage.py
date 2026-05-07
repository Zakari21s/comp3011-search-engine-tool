"""Persistence helpers for saving and loading inverted indexes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.indexer import DocumentMetadata, InvertedIndex, Posting

SCHEMA_VERSION = 1
_REQUIRED_KEYS = ("schema_version", "postings", "doc_lengths", "doc_metadata")


def _index_to_dict(index: InvertedIndex) -> dict[str, Any]:
    """Convert an InvertedIndex into a JSON-serializable dictionary."""
    postings_data: dict[str, dict[str, dict[str, Any]]] = {}
    for term, term_postings in index.postings.items():
        postings_data[term] = {}
        for doc_id, posting in term_postings.items():
            postings_data[term][doc_id] = {
                "frequency": posting.frequency,
                "positions": list(posting.positions),
            }

    metadata_data: dict[str, dict[str, Any]] = {}
    for doc_id, metadata in index.doc_metadata.items():
        metadata_data[doc_id] = {
            "url": metadata.url,
            "title": metadata.title,
            "quotes_count": metadata.quotes_count,
        }

    return {
        "schema_version": SCHEMA_VERSION,
        "postings": postings_data,
        "doc_lengths": dict(index.doc_lengths),
        "doc_metadata": metadata_data,
    }


def _require_dict(value: Any, field_name: str) -> dict[str, Any]:
    """Validate that a field is a dictionary-like mapping."""
    if not isinstance(value, dict):
        raise ValueError(f"Index field '{field_name}' must be a dictionary")
    return value


def _index_from_dict(data: dict[str, Any]) -> InvertedIndex:
    """Rebuild an InvertedIndex from loaded JSON dictionary content."""
    for key in _REQUIRED_KEYS:
        if key not in data:
            raise ValueError(f"Index file is missing required key '{key}'")

    schema_version = data["schema_version"]
    if schema_version != SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported schema_version: {schema_version} "
            f"(expected {SCHEMA_VERSION})"
        )

    postings_raw = _require_dict(data["postings"], "postings")
    doc_lengths_raw = _require_dict(data["doc_lengths"], "doc_lengths")
    doc_metadata_raw = _require_dict(data["doc_metadata"], "doc_metadata")

    postings: dict[str, dict[str, Posting]] = {}
    for term, term_postings_raw in postings_raw.items():
        if not isinstance(term, str):
            raise ValueError("Posting term keys must be strings")
        term_postings_dict = _require_dict(term_postings_raw, f"postings[{term!r}]")
        postings[term] = {}
        for doc_id, posting_raw in term_postings_dict.items():
            if not isinstance(doc_id, str):
                raise ValueError(f"Document IDs for term '{term}' must be strings")
            posting_dict = _require_dict(
                posting_raw, f"postings[{term!r}][{doc_id!r}]"
            )
            if "frequency" not in posting_dict or "positions" not in posting_dict:
                raise ValueError(
                    f"Posting for term '{term}' in doc '{doc_id}' must contain "
                    "'frequency' and 'positions'"
                )
            frequency = posting_dict["frequency"]
            positions = posting_dict["positions"]
            if not isinstance(frequency, int):
                raise ValueError(
                    f"Posting frequency for term '{term}' in doc '{doc_id}' "
                    "must be an integer"
                )
            if (
                not isinstance(positions, list)
                or not all(isinstance(pos, int) for pos in positions)
            ):
                raise ValueError(
                    f"Posting positions for term '{term}' in doc '{doc_id}' "
                    "must be a list of integers"
                )
            postings[term][doc_id] = Posting(frequency=frequency, positions=positions)

    doc_lengths: dict[str, int] = {}
    for doc_id, doc_length in doc_lengths_raw.items():
        if not isinstance(doc_id, str):
            raise ValueError("doc_lengths keys must be strings")
        if not isinstance(doc_length, int):
            raise ValueError(
                f"Document length for '{doc_id}' must be an integer"
            )
        doc_lengths[doc_id] = doc_length

    doc_metadata: dict[str, DocumentMetadata] = {}
    for doc_id, metadata_raw in doc_metadata_raw.items():
        if not isinstance(doc_id, str):
            raise ValueError("doc_metadata keys must be strings")
        metadata_dict = _require_dict(metadata_raw, f"doc_metadata[{doc_id!r}]")
        for key in ("url", "title", "quotes_count"):
            if key not in metadata_dict:
                raise ValueError(
                    f"Metadata for '{doc_id}' is missing required key '{key}'"
                )
        url = metadata_dict["url"]
        title = metadata_dict["title"]
        quotes_count = metadata_dict["quotes_count"]
        if not isinstance(url, str) or not isinstance(title, str):
            raise ValueError(
                f"Metadata for '{doc_id}' must have string 'url' and 'title'"
            )
        if not isinstance(quotes_count, int):
            raise ValueError(
                f"Metadata for '{doc_id}' must have integer 'quotes_count'"
            )
        doc_metadata[doc_id] = DocumentMetadata(
            url=url,
            title=title,
            quotes_count=quotes_count,
        )

    return InvertedIndex(
        postings=postings,
        doc_lengths=doc_lengths,
        doc_metadata=doc_metadata,
    )


def save_index(index: InvertedIndex, path: Path) -> None:
    """Save an inverted index to a JSON file on disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = _index_to_dict(index)
    path.write_text(
        json.dumps(serialized, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def load_index(path: Path) -> InvertedIndex:
    """Load an inverted index from a JSON file on disk."""
    try:
        raw_text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Index file not found: {path}") from exc

    try:
        loaded = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Index file is not valid JSON: {path}") from exc

    if not isinstance(loaded, dict):
        raise ValueError("Index file root must be a JSON object")

    return _index_from_dict(loaded)

