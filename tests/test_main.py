"""Unit tests for command handling in main.py."""

from __future__ import annotations

from pathlib import Path

import pytest

from indexer import InvertedIndex, Posting
from ranking import RankedResult, rank_documents
from main import handle_build, handle_find, handle_load, handle_print
from search import find_documents, find_phrase_documents


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


def test_handle_find_outputs_ranked_results_with_scores(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Find should print ranked documents with four-decimal TF-IDF scores."""
    index = _sample_index()
    ranking_called_with: dict[str, object] = {}

    def fake_find(_: InvertedIndex, query: str) -> list[str]:
        assert query == "life wisdom"
        return ["doc_a", "doc_z"]

    def fake_rank(
        _: InvertedIndex,
        query: str,
        candidate_doc_ids: list[str] | None = None,
    ) -> list[RankedResult]:
        ranking_called_with["query"] = query
        ranking_called_with["candidate_doc_ids"] = candidate_doc_ids
        return [
            RankedResult(doc_id="doc_z", score=0.42),
            RankedResult(doc_id="doc_a", score=0.1),
        ]

    exit_code, returned_index = handle_find(
        "life wisdom",
        current_index=index,
        find_documents_fn=fake_find,
        rank_documents_fn=fake_rank,
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert returned_index is index
    assert ranking_called_with["query"] == "life wisdom"
    assert ranking_called_with["candidate_doc_ids"] == ["doc_a", "doc_z"]
    assert "Matching documents (ranked):" in captured.out
    assert "- doc_z  score=0.4200" in captured.out
    assert "- doc_a  score=0.1000" in captured.out


def test_handle_find_quoted_query_calls_phrase_search(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Quoted queries should route through phrase retrieval."""
    index = _sample_index()
    phrase_calls: list[str] = []
    and_calls = 0

    def fake_phrase_find(_: InvertedIndex, phrase: str) -> list[str]:
        phrase_calls.append(phrase)
        return ["doc_a"]

    def fake_find(_: InvertedIndex, __: str) -> list[str]:
        nonlocal and_calls
        and_calls += 1
        return ["doc_b"]

    def fake_rank(
        _: InvertedIndex,
        __: str,
        candidate_doc_ids: list[str] | None = None,
    ) -> list[RankedResult]:
        assert candidate_doc_ids == ["doc_a"]
        return [RankedResult(doc_id="doc_a", score=1.0)]

    exit_code, _ = handle_find(
        '"life wisdom"',
        current_index=index,
        find_documents_fn=fake_find,
        find_phrase_documents_fn=fake_phrase_find,
        rank_documents_fn=fake_rank,
    )
    _captured = capsys.readouterr()
    assert exit_code == 0
    assert phrase_calls == ["life wisdom"]
    assert and_calls == 0


def test_handle_find_phrase_passes_inner_phrase_to_ranking(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Ranker should receive inner phrase text without quotes."""
    index = _sample_index()
    ranking_called_with: dict[str, object] = {}

    def fake_phrase_find(_: InvertedIndex, phrase: str) -> list[str]:
        assert phrase == "good friends"
        return ["doc_a", "doc_b"]

    def fake_rank(
        _: InvertedIndex,
        query: str,
        candidate_doc_ids: list[str] | None = None,
    ) -> list[RankedResult]:
        ranking_called_with["query"] = query
        ranking_called_with["candidate_doc_ids"] = candidate_doc_ids
        return [RankedResult(doc_id="doc_a", score=0.8)]

    exit_code, _ = handle_find(
        '"good friends"',
        current_index=index,
        find_phrase_documents_fn=fake_phrase_find,
        rank_documents_fn=fake_rank,
    )
    _captured = capsys.readouterr()
    assert exit_code == 0
    assert ranking_called_with["query"] == "good friends"
    assert ranking_called_with["candidate_doc_ids"] == ["doc_a", "doc_b"]


def test_handle_find_phrase_no_match_returns_success_with_message(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Quoted phrase with no matches should return exit 0."""
    index = _sample_index()

    def fake_phrase_find(_: InvertedIndex, __: str) -> list[str]:
        return []

    exit_code, _ = handle_find(
        '"missing phrase"',
        current_index=index,
        find_phrase_documents_fn=fake_phrase_find,
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "No matching documents found." in captured.out


def test_handle_find_non_quoted_query_uses_normal_find_path(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Non-quoted queries should keep Stage 9 AND retrieval path."""
    index = _sample_index()
    and_calls: list[str] = []
    phrase_calls = 0

    def fake_find(_: InvertedIndex, query: str) -> list[str]:
        and_calls.append(query)
        return ["doc_a"]

    def fake_phrase_find(_: InvertedIndex, __: str) -> list[str]:
        nonlocal phrase_calls
        phrase_calls += 1
        return []

    def fake_rank(
        _: InvertedIndex,
        __: str,
        candidate_doc_ids: list[str] | None = None,
    ) -> list[RankedResult]:
        assert candidate_doc_ids == ["doc_a"]
        return [RankedResult(doc_id="doc_a", score=0.3)]

    exit_code, _ = handle_find(
        "life wisdom",
        current_index=index,
        find_documents_fn=fake_find,
        find_phrase_documents_fn=fake_phrase_find,
        rank_documents_fn=fake_rank,
    )
    _captured = capsys.readouterr()
    assert exit_code == 0
    assert and_calls == ["life wisdom"]
    assert phrase_calls == 0


def test_handle_find_mismatched_quote_falls_back_to_and_path(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Mismatched quote should not trigger phrase mode."""
    index = _sample_index()
    and_calls: list[str] = []

    def fake_find(_: InvertedIndex, query: str) -> list[str]:
        and_calls.append(query)
        return ["doc_a"]

    def fake_rank(
        _: InvertedIndex,
        __: str,
        candidate_doc_ids: list[str] | None = None,
    ) -> list[RankedResult]:
        return [RankedResult(doc_id="doc_a", score=0.3)]

    exit_code, _ = handle_find(
        '"good friends',
        current_index=index,
        find_documents_fn=fake_find,
        rank_documents_fn=fake_rank,
    )
    _captured = capsys.readouterr()
    assert exit_code == 0
    assert and_calls == ['"good friends']


def test_handle_find_no_candidates_does_not_call_ranking(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """When AND candidate retrieval is empty, ranking should not run."""
    index = _sample_index()
    ranking_call_count = 0

    def fake_find(_: InvertedIndex, __: str) -> list[str]:
        return []

    def fake_rank(
        _: InvertedIndex,
        __: str,
        candidate_doc_ids: list[str] | None = None,
    ) -> list[RankedResult]:
        nonlocal ranking_call_count
        ranking_call_count += 1
        return []

    exit_code, returned_index = handle_find(
        "life unknown",
        current_index=index,
        find_documents_fn=fake_find,
        rank_documents_fn=fake_rank,
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert returned_index is index
    assert ranking_call_count == 0
    assert "No matching documents found." in captured.out


def test_handle_find_empty_query_returns_error(capsys: pytest.CaptureFixture[str]) -> None:
    """Find should return user error for empty/whitespace query."""
    index = _sample_index()
    search_call_count = 0
    ranking_call_count = 0

    def fake_find(_: InvertedIndex, __: str) -> list[str]:
        nonlocal search_call_count
        search_call_count += 1
        return ["doc_a"]

    def fake_rank(
        _: InvertedIndex,
        __: str,
        candidate_doc_ids: list[str] | None = None,
    ) -> list[RankedResult]:
        nonlocal ranking_call_count
        ranking_call_count += 1
        return [RankedResult(doc_id="doc_a", score=1.0)]

    exit_code, returned_index = handle_find(
        "   ",
        current_index=index,
        find_documents_fn=fake_find,
        rank_documents_fn=fake_rank,
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert returned_index is index
    assert search_call_count == 0
    assert ranking_call_count == 0
    assert "Query cannot be empty." in captured.out


def test_handle_find_empty_ranked_results_fallback_to_no_match(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Find should handle unexpected empty ranking output gracefully."""
    index = _sample_index()

    def fake_find(_: InvertedIndex, __: str) -> list[str]:
        return ["doc_a"]

    def fake_rank(
        _: InvertedIndex,
        __: str,
        candidate_doc_ids: list[str] | None = None,
    ) -> list[RankedResult]:
        assert candidate_doc_ids == ["doc_a"]
        return []

    exit_code, returned_index = handle_find(
        "life",
        current_index=index,
        find_documents_fn=fake_find,
        rank_documents_fn=fake_rank,
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert returned_index is index
    assert "No matching documents found." in captured.out


def test_handle_find_integration_with_real_search_and_ranking(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Find should compose real AND retrieval with real TF-IDF ranking."""
    index = InvertedIndex(
        postings={
            "life": {
                "doc_a": Posting(frequency=1, positions=[0]),
                "doc_b": Posting(frequency=3, positions=[0, 1, 2]),
            },
            "wisdom": {
                "doc_a": Posting(frequency=1, positions=[1]),
                "doc_b": Posting(frequency=1, positions=[3]),
            },
        },
        doc_lengths={"doc_a": 4, "doc_b": 4},
    )

    exit_code, returned_index = handle_find(
        "life wisdom",
        current_index=index,
        find_documents_fn=find_documents,
        rank_documents_fn=rank_documents,
    )
    captured = capsys.readouterr()
    output_lines = captured.out.strip().splitlines()

    assert exit_code == 0
    assert returned_index is index
    assert output_lines[0] == "Matching documents (ranked):"
    assert output_lines[1].startswith("- doc_b  score=")
    assert output_lines[2].startswith("- doc_a  score=")


def test_handle_find_phrase_integration_with_real_phrase_search_and_ranking(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Quoted find should compose real phrase retrieval and ranking."""
    index = InvertedIndex(
        postings={
            "good": {
                "doc_a": Posting(frequency=1, positions=[0]),
                "doc_b": Posting(frequency=2, positions=[0, 3]),
            },
            "friends": {
                "doc_a": Posting(frequency=1, positions=[1]),
                "doc_b": Posting(frequency=1, positions=[1]),
            },
        },
        doc_lengths={"doc_a": 2, "doc_b": 4},
    )

    exit_code, returned_index = handle_find(
        '"good friends"',
        current_index=index,
        find_phrase_documents_fn=find_phrase_documents,
        rank_documents_fn=rank_documents,
    )
    captured = capsys.readouterr()
    output_lines = captured.out.strip().splitlines()

    assert exit_code == 0
    assert returned_index is index
    assert output_lines[0] == "Matching documents (ranked):"
    assert output_lines[1].startswith("- doc_a  score=")
    assert output_lines[2].startswith("- doc_b  score=")
