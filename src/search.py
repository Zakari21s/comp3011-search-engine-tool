"""In-memory query processing utilities over an inverted index."""

from __future__ import annotations
import difflib

from src.indexer import InvertedIndex, Posting
from src.tokenizer import tokenize


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


def _has_consecutive_phrase(index: InvertedIndex, terms: list[str], doc_id: str) -> bool:
    """Return True when phrase terms appear consecutively in a document."""
    if not terms:
        return False

    position_sets_by_term: dict[str, set[int]] = {}
    for term in terms:
        if term in position_sets_by_term:
            continue

        posting = index.postings.get(term, {}).get(doc_id)
        if posting is None:
            return False
        position_sets_by_term[term] = set(posting.positions)

    first_positions = position_sets_by_term[terms[0]]
    for start_position in first_positions:
        has_phrase_match = True
        for offset, term in enumerate(terms[1:], start=1):
            target_position = start_position + offset
            if target_position not in position_sets_by_term[term]:
                has_phrase_match = False
                break
        if has_phrase_match:
            return True

    return False


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


def find_phrase_documents(index: InvertedIndex, phrase: str) -> list[str]:
    """Find document IDs where phrase terms occur consecutively.

    Behavior:
    - normalize phrase with tokenizer.tokenize
    - preserve duplicate phrase terms
    - return [] for empty/invalid phrases
    - use existing AND retrieval as a candidate filter
    - perform positional matching only on candidate docs
    - return sorted matching doc IDs
    """
    phrase_terms = [token.term for token in tokenize(phrase)]
    if not phrase_terms:
        return []

    candidate_doc_ids = find_documents(index, " ".join(phrase_terms))
    if not candidate_doc_ids:
        return []

    matching_doc_ids = [
        doc_id
        for doc_id in candidate_doc_ids
        if _has_consecutive_phrase(index, phrase_terms, doc_id)
    ]
    return sorted(matching_doc_ids)


def suggest_query_terms(
    index: InvertedIndex,
    query: str,
    max_suggestions: int = 3,
) -> dict[str, list[str]]:
    """Suggest close known terms for unknown query tokens.

    Behavior:
    - normalizes query terms with tokenizer.tokenize
    - considers only unknown terms against known index vocabulary
    - deduplicates repeated unknown terms
    - returns deterministic suggestions per unknown term
    - uses conservative similarity cutoff for explainable precision
    """
    if max_suggestions <= 0:
        return {}

    known_terms = sorted(index.postings.keys())
    if not known_terms:
        return {}

    unknown_terms: list[str] = []
    seen_unknown_terms: set[str] = set()
    for token in tokenize(query):
        if token.term in index.postings or token.term in seen_unknown_terms:
            continue
        seen_unknown_terms.add(token.term)
        unknown_terms.append(token.term)

    if not unknown_terms:
        return {}

    suggestions: dict[str, list[str]] = {}
    for unknown_term in unknown_terms:
        close_matches = difflib.get_close_matches(
            unknown_term,
            known_terms,
            n=max_suggestions,
            cutoff=0.8,
        )
        if close_matches:
            suggestions[unknown_term] = close_matches

    return suggestions

