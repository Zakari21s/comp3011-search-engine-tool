# Implementation Summary

## Current Project Status
Short overview of completed implementation stages.

---

# Architecture Overview

## crawler.py
Responsibility:
- handles polite crawling
- follows pagination links
- avoids duplicate URLs

Important decisions:
- uses BFS crawling
- uses requests.Session
- enforces 6-second delay

---

## tokenizer.py
Responsibility:
- lowercase normalization
- punctuation removal
- token position tracking

Important decisions:
- regex-based tokenization
- preserves word order for phrase search

---

# Current Features
- tokenizer implemented
- unit tests passing
- position tracking supported
- parser implemented with structured quote extraction
- parser unit tests added for malformed/missing HTML and noise filtering

---

# Pending Features
- persistence layer

- search logic

- crawler integration

- TF-IDF ranking

---

# Testing Status
- tokenizer tests complete
- parser tests complete
- crawler tests pending

---

# Known Limitations
- no stemming yet
- no stop-word filtering yet

---

# Important Design Principles
- keep implementation explainable
- prioritise testability
- avoid over-engineering
- coursework targets outstanding grade

---

# Branch Status
Current branch:
feature/indexer

---

# Stage 1 Update (Tokenizer)
- implemented `Token` dataclass with `term` and `position`
- implemented public API `tokenize(text: str) -> list[Token]`
- tokenizer lowercases text, treats punctuation as separators, preserves order, and excludes pure numbers
- positions are 0-based by token order to support later phrase search logic
- added unit tests for lowercase handling, punctuation behavior, repeated words, whitespace/empty input, spacing variants, position tracking, and numeric/alphanumeric cases

---

# Stage 2 Update (Parser)
- replaced parser placeholder with public API `parse_page(html: str, url: str = "") -> ParsedPage`
- introduced `ParsedPage` dataclass with fields: `url`, `title`, `search_text`, `quotes_count`, `authors`, `tags`
- parser now extracts `div.quote` blocks only and captures quote text (`span.text`), author (`small.author`), and tags (`div.tags a.tag`)
- `search_text` is built in deterministic quote-level order: quote text -> author -> tags
- added defensive handling for empty/malformed HTML and missing fields without crashing
- normalized whitespace to improve index consistency and test determinism

---

# Stage 3 Update (Indexer)
- replaced placeholder indexer with dataclass-based in-memory model: `Posting`, `DocumentMetadata`, and `InvertedIndex`
- implemented public API `build_index(pages: Iterable[ParsedPage]) -> InvertedIndex`
- indexing now tokenizes `page.search_text` via `tokenize(...)`, storing per-term per-document frequency and token positions
- stores per-document length and metadata for all unique documents, including empty-content pages
- applies deterministic document IDs (`page.url` when present, otherwise `doc_0`, `doc_1`, ...) and first-write-wins for duplicate URLs
- added focused Stage 3 tests for empty input, postings correctness, repeated terms, multi-document terms, empty pages, duplicate URLs, fallback IDs, tokenizer integration, and metadata retention