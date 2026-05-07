"""Unit tests for Stage 5 in-memory search behavior."""

from __future__ import annotations

from indexer import InvertedIndex, Posting
from search import find_documents, get_term_postings


def _sample_index() -> InvertedIndex:
    """Create a compact index fixture for retrieval tests."""
    return InvertedIndex(
        postings={
            "life": {
                "doc_b": Posting(frequency=2, positions=[1, 4]),
                "doc_a": Posting(frequency=1, positions=[0]),
            },
            "wisdom": {
                "doc_a": Posting(frequency=1, positions=[2]),
                "doc_c": Posting(frequency=1, positions=[0]),
            },
            "author": {
                "doc_a": Posting(frequency=1, positions=[3]),
            },
        },
        doc_lengths={
            "doc_a": 5,
            "doc_b": 5,
            "doc_c": 3,
        },
        doc_metadata={},
    )


def test_empty_index_returns_empty_results() -> None:
    """Empty index should return no postings and no matches."""
    index = InvertedIndex()
    assert get_term_postings(index, "life") == {}
    assert find_documents(index, "life") == []


def test_get_term_postings_returns_known_term_postings() -> None:
    """Known terms should return their postings dictionary."""
    index = _sample_index()
    postings = get_term_postings(index, "life")
    assert sorted(postings.keys()) == ["doc_a", "doc_b"]
    assert postings["doc_b"].frequency == 2


def test_get_term_postings_returns_empty_for_unknown_or_empty_input() -> None:
    """Unknown terms and empty-like inputs should return empty postings."""
    index = _sample_index()
    assert get_term_postings(index, "unknown") == {}
    assert get_term_postings(index, "") == {}
    assert get_term_postings(index, "   ") == {}
    assert get_term_postings(index, "!!!") == {}
    assert get_term_postings(index, "12345") == {}


def test_get_term_postings_uses_only_first_token_from_query() -> None:
    """When multiple tokens are provided, only the first token is used."""
    index = _sample_index()
    postings = get_term_postings(index, "life wisdom")
    assert sorted(postings.keys()) == ["doc_a", "doc_b"]


def test_query_normalization_case_and_punctuation_insensitive() -> None:
    """Query normalization should match tokenizer behavior."""
    index = _sample_index()
    assert find_documents(index, "LiFe!!!") == ["doc_a", "doc_b"]
    assert sorted(get_term_postings(index, "Wisdom??").keys()) == ["doc_a", "doc_c"]


def test_find_documents_single_word_returns_sorted_doc_ids() -> None:
    """Single-term matches should be returned in deterministic sorted order."""
    index = _sample_index()
    assert find_documents(index, "life") == ["doc_a", "doc_b"]


def test_find_documents_multi_word_uses_and_intersection() -> None:
    """Multi-term search should return docs containing all terms."""
    index = _sample_index()
    assert find_documents(index, "life author") == ["doc_a"]


def test_find_documents_multi_word_with_unknown_term_returns_empty() -> None:
    """If one term is missing, AND search should return no documents."""
    index = _sample_index()
    assert find_documents(index, "life unknown") == []


def test_find_documents_repeated_query_terms_do_not_change_results() -> None:
    """Repeated terms should be deduplicated during query processing."""
    index = _sample_index()
    assert find_documents(index, "life life") == ["doc_a", "doc_b"]
    assert find_documents(index, "life life author author") == ["doc_a"]


def test_find_documents_empty_like_queries_return_empty() -> None:
    """Empty and non-tokenizing queries should return empty results."""
    index = _sample_index()
    assert find_documents(index, "") == []
    assert find_documents(index, "   ") == []
    assert find_documents(index, "!!! ???") == []
    assert find_documents(index, "123 456") == []


def test_deterministic_ordering_stable_despite_insertion_order() -> None:
    """Output ordering should stay lexical regardless of posting insertion order."""
    index = InvertedIndex(
        postings={
            "term": {
                "doc_z": Posting(frequency=1, positions=[0]),
                "doc_m": Posting(frequency=1, positions=[1]),
                "doc_a": Posting(frequency=1, positions=[2]),
            }
        }
    )
    assert find_documents(index, "term") == ["doc_a", "doc_m", "doc_z"]

