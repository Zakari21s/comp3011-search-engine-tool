"""Unit tests for Stage 5 in-memory search behavior."""

from __future__ import annotations

from src.indexer import InvertedIndex, Posting
from src.search import (
    find_documents,
    find_phrase_documents,
    get_term_postings,
    suggest_query_terms,
)


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


def test_find_phrase_documents_two_word_positive_case() -> None:
    """Two-word phrase should match when positions are consecutive."""
    index = InvertedIndex(
        postings={
            "good": {"doc_a": Posting(frequency=1, positions=[0])},
            "friends": {"doc_a": Posting(frequency=1, positions=[1])},
        },
        doc_lengths={"doc_a": 2},
    )
    assert find_phrase_documents(index, "good friends") == ["doc_a"]


def test_find_phrase_documents_two_word_non_consecutive_negative_case() -> None:
    """Two-word phrase should fail when terms are non-consecutive."""
    index = InvertedIndex(
        postings={
            "good": {"doc_a": Posting(frequency=1, positions=[0])},
            "friends": {"doc_a": Posting(frequency=1, positions=[2])},
        },
        doc_lengths={"doc_a": 3},
    )
    assert find_phrase_documents(index, "good friends") == []


def test_find_phrase_documents_three_word_positive_case() -> None:
    """Three-word phrase should match when all offsets align."""
    index = InvertedIndex(
        postings={
            "to": {"doc_a": Posting(frequency=1, positions=[0])},
            "be": {"doc_a": Posting(frequency=1, positions=[1])},
            "free": {"doc_a": Posting(frequency=1, positions=[2])},
        },
        doc_lengths={"doc_a": 3},
    )
    assert find_phrase_documents(index, "to be free") == ["doc_a"]


def test_find_phrase_documents_unknown_term_returns_empty() -> None:
    """Unknown phrase terms should return no matches."""
    index = InvertedIndex(
        postings={"known": {"doc_a": Posting(frequency=1, positions=[0])}},
        doc_lengths={"doc_a": 1},
    )
    assert find_phrase_documents(index, "known unknown") == []


def test_find_phrase_documents_multiple_docs_returns_only_true_matches() -> None:
    """Only documents with real consecutive phrase matches should be returned."""
    index = InvertedIndex(
        postings={
            "good": {
                "doc_b": Posting(frequency=1, positions=[3]),
                "doc_a": Posting(frequency=1, positions=[0]),
                "doc_c": Posting(frequency=1, positions=[1]),
            },
            "friends": {
                "doc_b": Posting(frequency=1, positions=[4]),
                "doc_a": Posting(frequency=1, positions=[1]),
                "doc_c": Posting(frequency=1, positions=[4]),
            },
        },
        doc_lengths={"doc_a": 3, "doc_b": 6, "doc_c": 6},
    )
    assert find_phrase_documents(index, "good friends") == ["doc_a", "doc_b"]


def test_find_phrase_documents_one_word_phrase_works() -> None:
    """Single-word phrase should behave like single-term retrieval."""
    index = _sample_index()
    assert find_phrase_documents(index, "life") == ["doc_a", "doc_b"]


def test_find_phrase_documents_normalization_case_and_punctuation() -> None:
    """Phrase search should normalize input using tokenizer behavior."""
    index = InvertedIndex(
        postings={
            "good": {"doc_a": Posting(frequency=1, positions=[0])},
            "friends": {"doc_a": Posting(frequency=1, positions=[1])},
        },
        doc_lengths={"doc_a": 2},
    )
    assert find_phrase_documents(index, "GoOd, FRIENDS!!!") == ["doc_a"]


def test_find_phrase_documents_repeated_term_phrase_requires_all_offsets() -> None:
    """Repeated-term phrase should require all consecutive occurrences."""
    index = InvertedIndex(
        postings={
            "no": {
                "doc_good": Posting(frequency=3, positions=[0, 1, 2]),
                "doc_bad": Posting(frequency=3, positions=[0, 1, 3]),
            }
        },
        doc_lengths={"doc_good": 3, "doc_bad": 4},
    )
    assert find_phrase_documents(index, "no no no") == ["doc_good"]


def test_find_phrase_documents_empty_like_phrases_return_empty() -> None:
    """Empty and non-tokenizing phrase inputs should return no matches."""
    index = _sample_index()
    assert find_phrase_documents(index, "") == []
    assert find_phrase_documents(index, "   ") == []
    assert find_phrase_documents(index, "!!! ???") == []
    assert find_phrase_documents(index, "123 456") == []


def test_find_phrase_documents_deterministic_lexical_ordering() -> None:
    """Phrase results should return doc IDs in lexical order."""
    index = InvertedIndex(
        postings={
            "a": {
                "doc_z": Posting(frequency=1, positions=[0]),
                "doc_m": Posting(frequency=1, positions=[0]),
                "doc_a": Posting(frequency=1, positions=[0]),
            },
            "b": {
                "doc_z": Posting(frequency=1, positions=[1]),
                "doc_m": Posting(frequency=1, positions=[1]),
                "doc_a": Posting(frequency=1, positions=[1]),
            },
        },
        doc_lengths={"doc_z": 2, "doc_m": 2, "doc_a": 2},
    )
    assert find_phrase_documents(index, "a b") == ["doc_a", "doc_m", "doc_z"]


def test_suggest_query_terms_single_word_typo_returns_suggestion() -> None:
    """Unknown single-word typo should suggest close known vocabulary term."""
    index = _sample_index()
    assert suggest_query_terms(index, "lif") == {"lif": ["life"]}


def test_suggest_query_terms_unknown_with_no_close_match_returns_empty() -> None:
    """Unknown term with no close vocabulary should return empty mapping."""
    index = _sample_index()
    assert suggest_query_terms(index, "qzxv") == {}


def test_suggest_query_terms_multi_word_suggests_only_unknown_terms() -> None:
    """Known terms should be skipped while unknown terms receive suggestions."""
    index = _sample_index()
    assert suggest_query_terms(index, "life wisdm") == {"wisdm": ["wisdom"]}


def test_suggest_query_terms_repeated_unknown_term_is_deduplicated() -> None:
    """Repeated unknown query term should appear only once in output."""
    index = _sample_index()
    assert suggest_query_terms(index, "lif lif") == {"lif": ["life"]}


def test_suggest_query_terms_deterministic_ordering_of_unknown_terms() -> None:
    """Suggestion map key order should follow first-seen unknown term order."""
    index = _sample_index()
    assert list(suggest_query_terms(index, "authr wisdm").keys()) == ["authr", "wisdm"]


def test_suggest_query_terms_phrase_style_input_tokenizes_correctly() -> None:
    """Quoted/punctuated phrase-like input should still normalize via tokenizer."""
    index = _sample_index()
    assert suggest_query_terms(index, '"LiFe, wisdm!!!"') == {"wisdm": ["wisdom"]}


def test_suggest_query_terms_respects_max_suggestions_limit() -> None:
    """Maximum suggestions should cap close matches per unknown term."""
    index = InvertedIndex(
        postings={
            "friend": {"doc_a": Posting(frequency=1, positions=[0])},
            "friends": {"doc_b": Posting(frequency=1, positions=[0])},
            "fiend": {"doc_c": Posting(frequency=1, positions=[0])},
            "fried": {"doc_d": Posting(frequency=1, positions=[0])},
        },
        doc_lengths={"doc_a": 1, "doc_b": 1, "doc_c": 1, "doc_d": 1},
    )
    suggestions = suggest_query_terms(index, "freind", max_suggestions=2)
    assert suggestions
    assert len(suggestions["freind"]) <= 2


def test_suggest_query_terms_comes_only_from_known_vocabulary() -> None:
    """Every suggestion candidate must come from index vocabulary only."""
    index = _sample_index()
    suggestions = suggest_query_terms(index, "lif authr")
    known_terms = set(index.postings.keys())
    assert suggestions
    for matches in suggestions.values():
        assert matches
        assert set(matches).issubset(known_terms)

