# Implementation Summary

## Current Project Status
Stages 1-11 are complete (tokenizer, parser, indexer, storage, core search, crawler, CLI integration, TF-IDF ranking module, ranked CLI `find` integration, phrase search with positional matching, and no-match query suggestions).

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
- add benchmarking and coverage checks
- complete README/documentation polish and final video preparation

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
feature/query-suggestions
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

---

# Stage 4 Update (Storage)
- replaced `Storage` class scaffold with module-level APIs: `save_index(index: InvertedIndex, path: Path)` and `load_index(path: Path) -> InvertedIndex`
- implemented explicit JSON serialization/deserialization helpers: `_index_to_dict(...)` and `_index_from_dict(...)`
- persisted schema includes `schema_version`, `postings`, `doc_lengths`, and `doc_metadata`, with explicit conversion of `Posting` and `DocumentMetadata`
- save path handling now uses `pathlib.Path`, UTF-8 JSON output, and automatic parent directory creation
- load path handling now provides defensive validation and clear errors for missing files, invalid JSON, missing keys, wrong top-level types, and unsupported schema versions
- added dedicated Stage 4 unit tests for round-trips, directory creation, JSON validity, error scenarios, and dataclass reconstruction correctness

---

# Stage 5 Update (Search)
- replaced the placeholder class-based search scaffold with module-level APIs: `get_term_postings(index, term_or_query)` and `find_documents(index, query)`
- query normalization now consistently reuses `tokenize(...)` so search behavior is case-insensitive and punctuation-insensitive
- `get_term_postings(...)` now returns postings for the first normalized token and defensively returns `{}` for empty/unknown inputs
- `find_documents(...)` now supports deterministic unranked retrieval: single-word lookup and multi-word AND intersection with repeated-term deduplication
- Stage 5 intentionally excludes ranking/TF-IDF, phrase search, and CLI formatting to keep separation of concerns and maintain explainable scope
- added dedicated Stage 5 unit tests for normalization, empty/unknown handling, AND semantics, repeated terms, and deterministic ordering

---

# Stage 6 Update (Crawler)
- replaced placeholder crawler scaffold with module-level API `crawl_quotes_site(...) -> list[ParsedPage]`
- crawler now uses `requests.Session` (with optional injected test session), sequential queue-based traversal, same-host enforcement, and visited URL deduplication
- added URL normalization that removes fragments and pagination discovery using `li.next > a[href]` with `urljoin(...)`
- integrated parser handoff via `parse_page(response.text, url=current_url)` so crawler output is ready for `build_index(...)`
- implemented coursework politeness enforcement with default 6-second delay between live requests using `time.monotonic()` and `time.sleep(...)`, while allowing `delay_seconds=0` for tests
- added dedicated mocked crawler tests for pagination flow, deduplication, same-host behavior, non-200/exception handling, politeness timing behavior, and parser integration

---

# Stage 7 Update (CLI Integration)
- implemented argparse command parsing in `cli.py` for `build`, `load`, `print <word>`, and `find <query terms...>` while keeping parsing separate from command logic
- implemented `main.py` command handlers that connect existing Stage 1-6 APIs: `build` (crawl -> index -> save), `load`, `print`, and `find`
- added default index persistence path `data/index.json` using `pathlib.Path` and deterministic output ordering for postings and find results
- added user-facing handling for missing/invalid index files, empty find queries, unknown print terms, and no-match find results with consistent exit codes (`0` success, `1` expected user errors)
- added lightweight dependency injection seams in command handlers so tests can pass fake crawler/storage/search functions without network or filesystem coupling
- added Stage 7 unit tests in `test_cli.py` and `test_main.py` covering parser behavior, command flow wiring, and required edge-case handling

---

# Stage 8 Update (Ranking)
- replaced placeholder ranking scaffold with module-level TF-IDF API `rank_documents(index, query, candidate_doc_ids=None)` in `ranking.py`
- kept a lightweight `RankedResult` dataclass (`doc_id`, `score`) and added private helpers for query normalization, TF, and IDF to keep implementation explainable
- ranking now uses tokenizer-normalized deduplicated query terms, ignores unknown terms, supports OR-based candidate discovery (or caller-provided candidates), and excludes non-positive scores
- scoring uses normalized TF (`frequency / doc_length`) and smoothed IDF (`ln((N + 1)/(df + 1)) + 1`) with deterministic sorting by `(-score, doc_id)`
- added dedicated Stage 8 tests in `test_ranking.py` for edge cases, TF/IDF effects, multi-term accumulation, candidate restriction behavior, normalization, tie-breaking, and return types

---

# Stage 9 Update (Ranked CLI Find)
- updated `main.py` `handle_find(...)` to compose Stage 5 candidate retrieval (`find_documents`) with Stage 8 ranking (`rank_documents`) without changing module responsibilities
- preserved AND semantics by passing candidate document IDs from `find_documents(...)` into `rank_documents(..., candidate_doc_ids=...)`
- changed CLI find output to ranked format: `Matching documents (ranked):` followed by `- <doc_id>  score=<tfidf>` with four decimal places
- kept behavior for empty query (`exit 1`), no-match paths (`exit 0`), and existing `build`/`load`/`print` command behavior unchanged
- expanded `test_main.py` with Stage 9 coverage for ranked output formatting, candidate handoff, no-candidate short-circuiting, empty-ranked fallback, empty-query short-circuiting, and real search+ranking composition

---

# Stage 10 Update (Phrase Search)
- added positional phrase retrieval in `search.py` through `find_phrase_documents(index, phrase)` and private helper `_has_consecutive_phrase(...)`
- phrase retrieval uses tokenizer normalization without deduplicating terms, so repeated-term phrases like `no no no` require true consecutive offsets
- phrase matching pipeline remains explainable and small: first reuse existing AND candidate filtering (`find_documents`), then apply positional offset checks only to candidate documents
- updated `main.py` `handle_find(...)` to route only fully double-quoted queries (`"..."`) to phrase search, while mismatched quotes fall back to normal AND behavior
- preserved Stage 9 ranked output by passing phrase candidates to `rank_documents(..., candidate_doc_ids=...)` and keeping the output format/tie-breaking unchanged
- expanded `test_search.py` and `test_main.py` with Stage 10 phrase behavior coverage (positive/negative phrase cases, repeated terms, normalization, routing, no-match behavior, and integration with real ranking)

---

# Stage 11 Update (Query Suggestions)
- added public `suggest_query_terms(index, query, max_suggestions=3)` in `search.py` using tokenizer normalization, unknown-term deduplication, and vocabulary-only matching from `sorted(index.postings.keys())`
- implemented lightweight typo suggestions with Python standard library `difflib.get_close_matches(...)` and conservative fixed cutoff (`0.8`) for explainable precision-first behavior
- kept retrieval behavior unchanged: suggestions are informational only, never auto-rewrite queries, and never trigger automatic retry/fuzzy retrieval
- updated `main.py` `handle_find(...)` no-match branch (AND and phrase paths) to print optional guidance:
  - `No matching documents found.`
  - `Did you mean:`
  - `- <unknown> -> <suggestion1>, <suggestion2>, ...`
- expanded `test_search.py` and `test_main.py` with Stage 11 coverage for single-term typos, no-close-match fallback, multi-term/phrase handling, deduplication, max-suggestion limits, deterministic formatting/order, and suggestion-call path behavior