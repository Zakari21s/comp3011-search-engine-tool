"""TF-IDF ranking utilities for retrieval."""

from __future__ import annotations

from dataclasses import dataclass
import math

from src.indexer import InvertedIndex
from src.tokenizer import tokenize


@dataclass(slots=True)
class RankedResult:
    """Represent one scored document result."""

    doc_id: str
    score: float


def _normalise_query_terms(query: str) -> list[str]:
    """Return deduplicated normalized query terms in first-seen order."""
    terms: list[str] = []
    seen_terms: set[str] = set()
    for token in tokenize(query):
        if token.term in seen_terms:
            continue
        seen_terms.add(token.term)
        terms.append(token.term)
    return terms


def _term_frequency(index: InvertedIndex, term: str, doc_id: str) -> float:
    """Return normalized term frequency for one term-document pair."""
    term_postings = index.postings.get(term)
    if not term_postings:
        return 0.0

    posting = term_postings.get(doc_id)
    if posting is None:
        return 0.0

    doc_length = index.doc_lengths.get(doc_id, 0)
    if doc_length <= 0:
        return 0.0

    return posting.frequency / doc_length


def _inverse_document_frequency(index: InvertedIndex, term: str) -> float:
    """Return smoothed IDF: ln((N + 1) / (df + 1)) + 1."""
    total_documents = len(index.doc_lengths)
    if total_documents == 0:
        return 0.0

    document_frequency = len(index.postings.get(term, {}))
    return math.log((total_documents + 1) / (document_frequency + 1)) + 1.0


def rank_documents(
    index: InvertedIndex,
    query: str,
    candidate_doc_ids: list[str] | None = None,
) -> list[RankedResult]:
    """Rank candidate documents using simple TF-IDF scoring.

    Behavior:
    - normalizes query via tokenizer and deduplicates terms
    - ignores unknown terms
    - when candidate_doc_ids is None, ranks OR-matched docs from known terms
    - when candidate_doc_ids is provided, only those docs are scored
    - excludes docs with non-positive final scores
    - returns deterministic ordering by (-score, doc_id)
    """
    if not index.doc_lengths:
        return []

    query_terms = _normalise_query_terms(query)
    if not query_terms:
        return []

    known_terms = [term for term in query_terms if term in index.postings]
    if not known_terms:
        return []

    if candidate_doc_ids is None:
        candidate_docs: set[str] = set()
        for term in known_terms:
            candidate_docs.update(index.postings[term].keys())
    else:
        candidate_docs = set(candidate_doc_ids)

    if not candidate_docs:
        return []

    idf_by_term = {term: _inverse_document_frequency(index, term) for term in known_terms}
    ranked_results: list[RankedResult] = []

    for doc_id in candidate_docs:
        score = 0.0
        for term in known_terms:
            tf = _term_frequency(index, term, doc_id)
            if tf <= 0.0:
                continue
            score += tf * idf_by_term[term]

        if score > 0.0:
            ranked_results.append(RankedResult(doc_id=doc_id, score=score))

    ranked_results.sort(key=lambda result: (-result.score, result.doc_id))
    return ranked_results

