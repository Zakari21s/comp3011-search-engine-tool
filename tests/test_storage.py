"""Unit tests for Stage 4 storage persistence behavior."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from indexer import DocumentMetadata, InvertedIndex, Posting
from storage import _index_to_dict, load_index, save_index


def _sample_index() -> InvertedIndex:
    """Create a representative non-empty index for persistence tests."""
    return InvertedIndex(
        postings={
            "life": {
                "https://quotes.toscrape.com/page/1/": Posting(
                    frequency=2,
                    positions=[0, 3],
                ),
                "doc_0": Posting(frequency=1, positions=[1]),
            },
            "wisdom": {
                "https://quotes.toscrape.com/page/1/": Posting(
                    frequency=1,
                    positions=[2],
                ),
            },
        },
        doc_lengths={
            "https://quotes.toscrape.com/page/1/": 4,
            "doc_0": 2,
        },
        doc_metadata={
            "https://quotes.toscrape.com/page/1/": DocumentMetadata(
                url="https://quotes.toscrape.com/page/1/",
                title="Quotes Page 1",
                quotes_count=1,
            ),
            "doc_0": DocumentMetadata(
                url="",
                title="Fallback Doc",
                quotes_count=0,
            ),
        },
    )


def test_save_and_load_round_trip_for_normal_index(tmp_path: Path) -> None:
    """A normal populated index should survive save/load round-trip."""
    path = tmp_path / "index.json"
    source = _sample_index()

    save_index(source, path)
    loaded = load_index(path)

    assert loaded == source


def test_save_and_load_round_trip_for_empty_index(tmp_path: Path) -> None:
    """An empty index should round-trip cleanly."""
    path = tmp_path / "empty.json"
    source = InvertedIndex()

    save_index(source, path)
    loaded = load_index(path)

    assert loaded == source


def test_save_index_creates_parent_directories(tmp_path: Path) -> None:
    """save_index should create missing parent directories automatically."""
    path = tmp_path / "nested" / "deeper" / "index.json"

    save_index(_sample_index(), path)

    assert path.exists()
    assert path.parent.exists()


def test_saved_file_contains_valid_json(tmp_path: Path) -> None:
    """Saved index file should parse as valid JSON with required keys."""
    path = tmp_path / "index.json"
    save_index(_sample_index(), path)

    data = json.loads(path.read_text(encoding="utf-8"))

    assert data["schema_version"] == 1
    assert "postings" in data
    assert "doc_lengths" in data
    assert "doc_metadata" in data


def test_load_index_raises_file_not_found_for_missing_file(tmp_path: Path) -> None:
    """Missing index files should raise FileNotFoundError with path context."""
    missing = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError, match="Index file not found"):
        load_index(missing)


def test_load_index_raises_value_error_for_malformed_json(tmp_path: Path) -> None:
    """Malformed JSON should raise ValueError with clear message."""
    path = tmp_path / "bad.json"
    path.write_text("{ this is not valid json", encoding="utf-8")

    with pytest.raises(ValueError, match="not valid JSON"):
        load_index(path)


def test_load_index_raises_value_error_for_missing_required_key(
    tmp_path: Path,
) -> None:
    """Missing top-level schema keys should raise ValueError."""
    path = tmp_path / "missing_key.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "postings": {},
                "doc_lengths": {},
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="missing required key 'doc_metadata'"):
        load_index(path)


def test_load_index_raises_value_error_for_unsupported_schema_version(
    tmp_path: Path,
) -> None:
    """Unsupported schema versions should fail defensively."""
    path = tmp_path / "bad_version.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 2,
                "postings": {},
                "doc_lengths": {},
                "doc_metadata": {},
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Unsupported schema_version"):
        load_index(path)


def test_loaded_postings_are_posting_dataclass_instances(tmp_path: Path) -> None:
    """Loaded postings should be Posting dataclass instances, not dicts."""
    path = tmp_path / "index.json"
    save_index(_sample_index(), path)
    loaded = load_index(path)

    posting = loaded.postings["life"]["https://quotes.toscrape.com/page/1/"]
    assert isinstance(posting, Posting)


def test_loaded_metadata_are_documentmetadata_dataclass_instances(
    tmp_path: Path,
) -> None:
    """Loaded metadata entries should be DocumentMetadata dataclass instances."""
    path = tmp_path / "index.json"
    save_index(_sample_index(), path)
    loaded = load_index(path)

    metadata = loaded.doc_metadata["https://quotes.toscrape.com/page/1/"]
    assert isinstance(metadata, DocumentMetadata)


def test_index_to_dict_produces_expected_schema() -> None:
    """Internal serializer should produce the simple documented schema."""
    data = _index_to_dict(_sample_index())

    assert data["schema_version"] == 1
    assert data["postings"]["life"]["https://quotes.toscrape.com/page/1/"] == {
        "frequency": 2,
        "positions": [0, 3],
    }
    assert data["doc_lengths"]["doc_0"] == 2
    assert data["doc_metadata"]["doc_0"] == {
        "url": "",
        "title": "Fallback Doc",
        "quotes_count": 0,
    }
