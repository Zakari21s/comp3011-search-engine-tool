"""Unit tests for Stage 7 command handling in main.py."""

from __future__ import annotations

from pathlib import Path

import pytest

from indexer import InvertedIndex, Posting
from main import handle_build, handle_find, handle_load, handle_print


def _sample_index() -> InvertedIndex:
    """Create a small deterministic index fixture."""
    return InvertedIndex(
        postings={
            "life": {
                "doc_b": Posting(frequency=2, positions=[3, 1]),
                "doc_a": Posting(frequency=1, positions=[0]),
            }
        },
        doc_lengths={"doc_a": 2, "doc_b": 3},
        doc_metadata={},
    )


def test_handle_build_calls_crawl_then_index_then_save() -> None:
    """Build should call crawl, build_index, and save_index in order."""
    call_order: list[str] = []
    index_path = Path("tmp/test-index.json")
    expected_pages = ["p1", "p2"]
    expected_index = _sample_index()

    def fake_crawl() -> list[str]:
        call_order.append("crawl")
        return expected_pages

    def fake_build_index(pages: list[str]) -> InvertedIndex:
        call_order.append("build_index")
        assert pages == expected_pages
        return expected_index

    def fake_save(index: InvertedIndex, path: Path) -> None:
        call_order.append("save_index")
        assert index == expected_index
        assert path == index_path

    exit_code, built_index = handle_build(
        index_path=index_path,
        crawl_fn=fake_crawl,
        build_index_fn=fake_build_index,
        save_index_fn=fake_save,
    )

    assert exit_code == 0
    assert built_index == expected_index
    assert call_order == ["crawl", "build_index", "save_index"]


def test_handle_load_success() -> None:
    """Load should return index and success exit code."""
    expected_index = _sample_index()

    def fake_load(path: Path) -> InvertedIndex:
        assert path == Path("tmp/index.json")
        return expected_index

    exit_code, loaded = handle_load(
        index_path=Path("tmp/index.json"),
        load_index_fn=fake_load,
    )

    assert exit_code == 0
    assert loaded == expected_index


def test_handle_load_missing_file_returns_error_code() -> None:
    """Load should map missing file to exit code 1."""

    def fake_load(_: Path) -> InvertedIndex:
        raise FileNotFoundError("missing")

    exit_code, loaded = handle_load(
        index_path=Path("tmp/missing.json"),
        load_index_fn=fake_load,
    )

    assert exit_code == 1
    assert loaded is None


def test_handle_print_known_word_outputs_postings(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Print should show sorted postings for known words."""
    index = _sample_index()

    exit_code, returned_index = handle_print("life", current_index=index)
    captured = capsys.readouterr()

    assert exit_code == 0
    assert returned_index is index
    assert "Postings for 'life':" in captured.out
    assert "- doc_a: frequency=1, positions=[0]" in captured.out
    assert "- doc_b: frequency=2, positions=[1, 3]" in captured.out


def test_handle_print_unknown_word(capsys: pytest.CaptureFixture[str]) -> None:
    """Print should provide a friendly message when no postings exist."""
    index = _sample_index()

    exit_code, returned_index = handle_print("unknown", current_index=index)
    captured = capsys.readouterr()

    assert exit_code == 0
    assert returned_index is index
    assert "No postings found for 'unknown'." in captured.out


def test_handle_find_shows_matching_documents(capsys: pytest.CaptureFixture[str]) -> None:
    """Find should list matching documents in deterministic order."""
    index = _sample_index()

    def fake_find(_: InvertedIndex, query: str) -> list[str]:
        assert query == "life wisdom"
        return ["doc_z", "doc_a"]

    exit_code, returned_index = handle_find(
        "life wisdom",
        current_index=index,
        find_documents_fn=fake_find,
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert returned_index is index
    assert "Matching documents:" in captured.out
    assert "- doc_a" in captured.out
    assert "- doc_z" in captured.out


def test_handle_find_no_results(capsys: pytest.CaptureFixture[str]) -> None:
    """Find should handle no-match queries without error."""
    index = _sample_index()

    def fake_find(_: InvertedIndex, __: str) -> list[str]:
        return []

    exit_code, returned_index = handle_find(
        "life unknown",
        current_index=index,
        find_documents_fn=fake_find,
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert returned_index is index
    assert "No matching documents found." in captured.out


def test_handle_find_empty_query_returns_error(capsys: pytest.CaptureFixture[str]) -> None:
    """Find should return user error for empty/whitespace query."""
    index = _sample_index()

    exit_code, returned_index = handle_find("   ", current_index=index)
    captured = capsys.readouterr()

    assert exit_code == 1
    assert returned_index is index
    assert "Query cannot be empty." in captured.out
