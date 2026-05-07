"""In-memory query processing utilities over an inverted index."""

from __future__ import annotations

from indexer import InvertedIndex, Posting
from tokenizer import tokenize


def _normalized_query_terms(query: str) -> list[str]:
    """Return deduplicated normalized query terms in first-seen order."""
    terms: list[str] = []
    seen_terms: set[str] = set()
    for token in tokenize(query):
        if token.term in seen_terms:
            continue
        seen_terms.add(token.term)
        terms.append(token.term)
    return terms


def get_term_postings(index: InvertedIndex, term_or_query: str) -> dict[str, Posting]:
    """Return postings for the first normalized query token.

    Behavior:
    - normalize input through tokenizer.tokenize
    - return {} when no token is produced
    - if multiple tokens exist, use only the first token
    - return {} for unknown terms
    """
    tokens = tokenize(term_or_query)
    if not tokens:
        return {}

    term = tokens[0].term
    return index.postings.get(term, {})


def find_documents(index: InvertedIndex, query: str) -> list[str]:
    """Find document IDs matching a query using unranked AND semantics.

    Behavior:
    - normalize query with tokenizer.tokenize
    - return [] for empty/invalid queries
    - deduplicate repeated terms
    - single-term query returns sorted matching doc IDs
    - multi-term query returns sorted intersection of doc IDs
    """
    terms = _normalized_query_terms(query)
    if not terms:
        return []

    first_term_postings = index.postings.get(terms[0])
    if not first_term_postings:
        return []

    matching_doc_ids = set(first_term_postings.keys())

    for term in terms[1:]:
        term_postings = index.postings.get(term)
        if not term_postings:
            return []
        matching_doc_ids &= set(term_postings.keys())
        if not matching_doc_ids:
            return []

    return sorted(matching_doc_ids)

