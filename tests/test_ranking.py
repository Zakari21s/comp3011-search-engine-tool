"""Unit tests for Stage 8 TF-IDF ranking behavior."""

from __future__ import annotations

from src.indexer import InvertedIndex, Posting
from src.ranking import RankedResult, rank_documents


def test_empty_index_returns_empty_results() -> None:
    """Ranking should return empty results when the index is empty."""
    assert rank_documents(InvertedIndex(), "life") == []


def test_empty_like_queries_return_empty_results() -> None:
    """Empty or non-tokenizing queries should return no ranked results."""
    index = InvertedIndex(
        postings={"life": {"doc_a": Posting(frequency=1, positions=[0])}},
        doc_lengths={"doc_a": 1},
    )
    assert rank_documents(index, "") == []
    assert rank_documents(index, "   ") == []
    assert rank_documents(index, "!!! ???") == []
    assert rank_documents(index, "123 456") == []


def test_unknown_only_query_returns_empty_results() -> None:
    """Queries containing only unknown terms should return no results."""
    index = InvertedIndex(
        postings={"life": {"doc_a": Posting(frequency=1, positions=[0])}},
        doc_lengths={"doc_a": 1},
    )
    assert rank_documents(index, "unknown") == []


def test_single_term_ranking_orders_higher_tf_first() -> None:
    """Higher normalized TF should rank ahead for single-term queries."""
    index = InvertedIndex(
        postings={
            "life": {
                "doc_low": Posting(frequency=1, positions=[0]),
                "doc_high": Posting(frequency=3, positions=[0, 1, 2]),
            }
        },
        doc_lengths={"doc_low": 4, "doc_high": 4},
    )
    results = rank_documents(index, "life")
    assert [result.doc_id for result in results] == ["doc_high", "doc_low"]


def test_longer_document_normalization_reduces_score_impact() -> None:
    """Same frequency in a longer document should reduce normalized TF score."""
    index = InvertedIndex(
        postings={
            "term": {
                "doc_short": Posting(frequency=2, positions=[0, 1]),
                "doc_long": Posting(frequency=2, positions=[5, 10]),
            }
        },
        doc_lengths={"doc_short": 4, "doc_long": 20},
    )
    results = rank_documents(index, "term")
    assert [result.doc_id for result in results] == ["doc_short", "doc_long"]


def test_rare_term_has_stronger_idf_effect_than_common_term() -> None:
    """Rarer terms should contribute more score due to higher IDF."""
    index = InvertedIndex(
        postings={
            "common": {
                "doc_1": Posting(frequency=1, positions=[0]),
                "doc_2": Posting(frequency=1, positions=[0]),
                "doc_3": Posting(frequency=1, positions=[0]),
            },
            "rare": {
                "doc_1": Posting(frequency=1, positions=[1]),
            },
        },
        doc_lengths={"doc_1": 2, "doc_2": 2, "doc_3": 2},
    )
    common_score = rank_documents(index, "common")[0].score
    rare_score = rank_documents(index, "rare")[0].score
    assert rare_score > common_score


def test_multi_term_query_sums_evidence_across_terms() -> None:
    """Multi-term scoring should sum TF-IDF evidence from all known terms."""
    index = InvertedIndex(
        postings={
            "life": {
                "doc_a": Posting(frequency=2, positions=[0, 2]),
                "doc_b": Posting(frequency=1, positions=[0]),
            },
            "wisdom": {
                "doc_a": Posting(frequency=1, positions=[3]),
            },
        },
        doc_lengths={"doc_a": 4, "doc_b": 4},
    )
    results = rank_documents(index, "life wisdom")
    assert [result.doc_id for result in results] == ["doc_a", "doc_b"]


def test_candidate_doc_ids_restricts_ranking_scope() -> None:
    """Provided candidate docs should limit which docs are ranked."""
    index = InvertedIndex(
        postings={
            "life": {
                "doc_a": Posting(frequency=1, positions=[0]),
                "doc_b": Posting(frequency=2, positions=[0, 1]),
            }
        },
        doc_lengths={"doc_a": 2, "doc_b": 2},
    )
    results = rank_documents(index, "life", candidate_doc_ids=["doc_a"])
    assert [result.doc_id for result in results] == ["doc_a"]


def test_candidate_doc_ids_with_no_scoring_docs_returns_empty() -> None:
    """Candidates with no positive score should yield no results."""
    index = InvertedIndex(
        postings={"life": {"doc_a": Posting(frequency=1, positions=[0])}},
        doc_lengths={"doc_a": 1},
    )
    assert rank_documents(index, "life", candidate_doc_ids=["doc_unknown"]) == []


def test_query_normalization_is_case_and_punctuation_insensitive() -> None:
    """Ranking queries should normalize case and punctuation via tokenizer."""
    index = InvertedIndex(
        postings={"life": {"doc_a": Posting(frequency=1, positions=[0])}},
        doc_lengths={"doc_a": 1},
    )
    plain = rank_documents(index, "life")
    normalized = rank_documents(index, "LiFe!!!")
    assert [result.doc_id for result in plain] == [result.doc_id for result in normalized]
    assert plain[0].score == normalized[0].score


def test_deterministic_tie_break_uses_doc_id_order() -> None:
    """Equal scores should be ordered by ascending doc_id."""
    index = InvertedIndex(
        postings={
            "life": {
                "doc_z": Posting(frequency=1, positions=[0]),
                "doc_a": Posting(frequency=1, positions=[0]),
            }
        },
        doc_lengths={"doc_z": 1, "doc_a": 1},
    )
    results = rank_documents(index, "life")
    assert [result.doc_id for result in results] == ["doc_a", "doc_z"]


def test_rank_documents_returns_rankedresult_instances() -> None:
    """Public API should return RankedResult dataclass instances."""
    index = InvertedIndex(
        postings={"life": {"doc_a": Posting(frequency=1, positions=[0])}},
        doc_lengths={"doc_a": 1},
    )
    results = rank_documents(index, "life")
    assert results
    assert all(isinstance(result, RankedResult) for result in results)
