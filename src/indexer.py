"""In-memory inverted index construction for parsed pages."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from src.parser import ParsedPage
from src.tokenizer import tokenize


@dataclass(slots=True)
class Posting:
    """Posting entry for one term within one document."""

    frequency: int = 0
    positions: list[int] = field(default_factory=list)


@dataclass(slots=True)
class DocumentMetadata:
    """Minimal per-document metadata retained during indexing."""

    url: str
    title: str
    quotes_count: int


@dataclass(slots=True)
class InvertedIndex:
    """In-memory index structure for term postings and document stats."""

    postings: dict[str, dict[str, Posting]] = field(default_factory=dict)
    doc_lengths: dict[str, int] = field(default_factory=dict)
    doc_metadata: dict[str, DocumentMetadata] = field(default_factory=dict)


def _resolve_doc_id(page: ParsedPage, fallback_counter: int) -> str:
    """Return URL doc ID when available, otherwise deterministic fallback."""
    if page.url:
        return page.url
    return f"doc_{fallback_counter}"


def build_index(pages: Iterable[ParsedPage]) -> InvertedIndex:
    """Build an in-memory inverted index from parsed pages.

    Behavior:
    - uses page URL as document ID when available
    - uses deterministic fallback IDs for missing URLs
    - tokenizes page.search_text with tokenizer.tokenize
    - records per-term frequency and token positions per document
    - keeps document metadata and token length for every indexed document
    - handles duplicate URLs with first-write-wins
    """
    index = InvertedIndex()
    seen_urls: set[str] = set()
    fallback_counter = 0

    for page in pages:
        if page.url and page.url in seen_urls:
            continue

        doc_id = _resolve_doc_id(page, fallback_counter)
        if not page.url:
            fallback_counter += 1
        else:
            seen_urls.add(page.url)

        tokens = tokenize(page.search_text)
        index.doc_lengths[doc_id] = len(tokens)
        index.doc_metadata[doc_id] = DocumentMetadata(
            url=page.url,
            title=page.title,
            quotes_count=page.quotes_count,
        )

        for token in tokens:
            term_postings = index.postings.setdefault(token.term, {})
            posting = term_postings.setdefault(doc_id, Posting())
            posting.frequency += 1
            posting.positions.append(token.position)

    return index

