# GenAI Usage Log

This coursework is a Green AI assessment. I used AI as a development assistant, but all submitted code was reviewed, tested, and understood by me.

## Entry Template

### Date:
### Tool used:
### Task:
### Prompt summary:
### AI suggestion:
### What I accepted:
### What I changed/rejected:
### Manual checks performed:
### What I learned:

## Entry 1

### Date:
2026-05-07
### Tool used:
Cursor (Codex 5.3)
### Task:
Scaffolded Coursework 2 project structure and placeholder modules/tests/docs.
### Prompt summary:
Create a professional, modular Python skeleton for the search engine tool with typed files, docstrings, TODOs, tests folder, docs, and config files while preserving `docs/genai_log.md`.
### AI suggestion:
Create architecture-aligned module placeholders (`crawler`, `parser`, `tokenizer`, `indexer`, `storage`, `search`, `ranking`, `cli`, `main`), placeholder pytest files, and documentation/config files (`README`, testing strategy, design notes, `pytest.ini`, `requirements.txt`, `.gitignore`).
### What I accepted:
Most of the proposed project skeleton and module responsibilities, including type hints, docstrings, TODO markers, and minimal placeholder tests.
### What I changed/rejected:
No full feature logic was implemented yet to keep scope appropriate for initial setup.
### Manual checks performed:
Reviewed generated structure and ran lint diagnostics on `src` and `tests` (no linter issues found). Attempted to run tests; `pytest` command is not yet installed in the active environment.
### What I learned:
A clean, explainable architecture from day one makes it easier to justify design decisions and scale tests toward outstanding-mark criteria.

## Entry 2

### Date:
2026-05-07
### Tool used:
Cursor (Codex 5.3)
### Task:
Implemented Stage 1 tokenizer module and tokenizer unit tests.
### Prompt summary:
Implement only `tokenizer.py` with a lightweight `Token` dataclass and `tokenize(text: str) -> list[Token]`, then add tests for normalization, punctuation, spacing, positions, and numeric handling.
### AI suggestion:
Use a simple regex-based tokenizer with lowercase normalization, punctuation as separators, 0-based order positions, and exclusion of pure numeric tokens; cover edge cases with focused pytest tests.
### What I accepted:
Dataclass-based token representation, single public tokenizer function, and nine unit tests covering required Stage 1 behaviors.
### What I changed/rejected:
Kept implementation intentionally minimal (no stemming/stop-word filtering) for explainability and coursework scope.
### Manual checks performed:
Ran `pytest` to verify tokenizer tests and existing placeholder tests pass.
### What I learned:
Order-based token positions keep phrase-search readiness while preserving a straightforward implementation suitable for demonstration.

## Entry 3

### Date:
2026-05-07
### Tool used:
Cursor (Codex 5.3)
### Task:
Implemented Stage 2 parser module and parser unit tests for Quotes to Scrape HTML extraction.
### Prompt summary:
Implement only `parser.py` with a lightweight `ParsedPage` dataclass and `parse_page(html: str, url: str = "")`, extracting quote text, authors, and tags from `div.quote` blocks while handling malformed/empty HTML defensively.
### AI suggestion:
Use BeautifulSoup with targeted selectors for structured quote extraction, normalize whitespace, keep parser content-focused (no crawling/link logic), and add focused tests for deterministic ordering, malformed inputs, missing fields, and noise filtering.
### What I accepted:
Dataclass-based parse output, one public parsing function, deterministic search text construction (quote -> author -> tags), robust empty/malformed handling, and ten parser unit tests aligned with coursework edge cases.
### What I changed/rejected:
Did not add next-page extraction or nested quote models to avoid blurring crawler/parser responsibilities and to keep Stage 2 explainable.
### Manual checks performed:
Ran `pytest` to verify parser tests and existing test suite behavior.
### What I learned:
Structured extraction gives cleaner retrieval-ready text than full-page scraping while remaining simple enough to justify in the coursework demonstration.

## Entry 4

### Date:
2026-05-07
### Tool used:
Cursor (Codex 5.3)
### Task:
Implemented Stage 3 in-memory indexer and Stage 3 unit tests.
### Prompt summary:
Implement only `indexer.py` to build an in-memory inverted index from `ParsedPage` objects using tokenizer output, with per-term frequencies and positions, per-document metadata and lengths, deterministic fallback IDs, and first-write-wins duplicate URL handling.
### AI suggestion:
Use small dataclasses for `Posting`, `DocumentMetadata`, and `InvertedIndex`, keep one public `build_index(...)` function, and add focused tests for indexing correctness, edge cases, and tokenizer integration.
### What I accepted:
Dataclass-based index structures, deterministic missing-URL IDs (`doc_n`), first-write-wins duplicate URL policy, and a dedicated `test_indexer.py` suite covering required Stage 3 scenarios.
### What I changed/rejected:
Did not add ranking, storage serialization, crawler coupling, or query logic to keep Stage 3 scoped, explainable, and aligned with separation-of-concerns rules.
### Manual checks performed:
Ran `pytest` to verify Stage 3 tests and existing suite behavior.
### What I learned:
A dictionary-backed inverted index with lightweight dataclasses is simple to explain, easy to test, and provides the exact signals needed for later search, phrase matching, and TF-IDF stages.

## Entry 5

### Date:
2026-05-07
### Tool used:
Cursor (Codex 5.3)
### Task:
Implemented Stage 4 storage persistence and storage unit tests.
### Prompt summary:
Replace the placeholder storage scaffold with module-level JSON persistence functions for `InvertedIndex`, add defensive load validation/error handling, and create tests for round-trip behavior and malformed inputs.
### AI suggestion:
Use a simple versioned JSON schema (`schema_version`, `postings`, `doc_lengths`, `doc_metadata`), explicit dataclass conversion helpers, `pathlib.Path` file operations with UTF-8, and focused pytest cases for both success and failure paths.
### What I accepted:
Function-based API (`save_index`, `load_index`), explicit `_index_to_dict`/`_index_from_dict` helpers, clear `FileNotFoundError`/`ValueError` messaging, and a dedicated `test_storage.py` suite aligned with coursework edge cases.
### What I changed/rejected:
Did not add custom exception classes, atomic writes, compression, or schema migration logic to keep Stage 4 scope narrow and explainable.
### Manual checks performed:
Ran `pytest` to verify the full suite, including the new storage tests.
### What I learned:
Keeping persistence schema small and explicit improves explainability, makes failure cases easier to test, and cleanly prepares future CLI `build/load` flows without extra abstraction.

## Entry 6

### Date:
2026-05-07
### Tool used:
Cursor (Codex 5.3)
### Task:
Implemented Stage 5 in-memory search functions and Stage 5 search unit tests.
### Prompt summary:
Replace placeholder `search.py` with simple typed retrieval APIs (`get_term_postings`, `find_documents`) using tokenizer-based normalization, deterministic single-term and AND multi-term matching, plus edge-case tests.
### AI suggestion:
Keep Stage 5 focused on unranked in-memory lookup over `InvertedIndex`, deduplicate repeated query terms, sort doc IDs for deterministic behavior, and defer phrase search/ranking/CLI formatting to later stages.
### What I accepted:
Function-based search module, tokenizer-driven normalization, defensive empty/unknown handling, lexical ordering for deterministic output, and a full `tests/test_search.py` suite aligned with Stage 5 requirements.
### What I changed/rejected:
Did not introduce new result dataclasses, ranking hooks, phrase matching, or suggestion logic to avoid over-engineering and preserve clear module boundaries.
### Manual checks performed:
Ran `pytest` across the test suite after implementation.
### What I learned:
Using tokenizer normalization inside search keeps behavior consistent across indexing and querying while remaining simple to explain in coursework demonstration.

## Entry 7

### Date:
2026-05-07
### Tool used:
Cursor (Codex 5.3)
### Task:
Implemented Stage 6 crawler module and mocked crawler unit tests.
### Prompt summary:
Replace placeholder `crawler.py` with a typed module-level `crawl_quotes_site(...)` API that crawls quotes.toscrape.com sequentially, enforces 6-second politeness between live requests, follows pagination, avoids duplicate URLs, integrates with `parse_page(...)`, and handles failures defensively; add mocked tests only.
### AI suggestion:
Use a simple queue + visited set traversal with URL normalization (fragment removal), same-host filtering, `requests.Session` reuse with optional injection for tests, and a focused test suite that validates pagination, deduplication, error handling, and politeness behavior via monkeypatching.
### What I accepted:
Implemented the module-level crawler API with parser integration and defensive request handling, plus a dedicated mocked `test_crawler.py` covering required Stage 6 scenarios including delay behavior.
### What I changed/rejected:
Did not add retries, robots.txt handling, concurrency, or crawler-specific result dataclasses to keep Stage 6 explainable and within coursework scope.
### Manual checks performed:
Ran `pytest` after implementation to verify crawler tests and full suite behavior.
### What I learned:
Keeping crawler logic transport-focused and parser/indexer boundaries explicit makes the build pipeline easy to explain while still supporting robust, testable crawling behavior.

## Entry 8

### Date:
2026-05-07
### Tool used:
Cursor (Codex 5.3)
### Task:
Implemented Stage 7 CLI integration (`build`, `load`, `print`, `find`) and Stage 7 unit tests.
### Prompt summary:
Wire existing crawler/indexer/storage/search APIs through `cli.py` and `main.py` with deterministic output, user-friendly error handling, typed dependency injection for testability, and no interactive shell yet.
### AI suggestion:
Keep `cli.py` parser-only, keep command execution in `main.py`, use `data/index.json` as default path, map expected user errors to exit code `1`, and test command handlers with injected fake functions to avoid live network requests.
### What I accepted:
Argparse subcommands for required coursework commands, handler-based orchestration in `main.py`, deterministic sorted output for postings/find results, explicit edge-case messaging, and dedicated `test_cli.py`/`test_main.py`.
### What I changed/rejected:
Deferred interactive shell, ranking/TF-IDF, phrase search, and query suggestions to later stages to keep Stage 7 focused and explainable.
### Manual checks performed:
Ran `pytest` to validate existing tests plus new CLI integration tests.
### What I learned:
A thin parser + handler architecture gives strong testability and clean separation of concerns while still producing a smooth, demonstration-ready command workflow.

## Entry 9

### Date:
2026-05-07
### Tool used:
Cursor (Codex 5.3)
### Task:
Implemented Stage 8 TF-IDF ranking module and ranking unit tests.
### Prompt summary:
Replace ranking placeholder code with a simple functional TF-IDF API (`rank_documents`) using tokenizer-based query normalization, deterministic tie-breaking, optional candidate restriction, and focused Stage 8 tests; then update implementation summary and GenAI log.
### AI suggestion:
Use a lightweight `RankedResult` dataclass plus small helper functions for deduplicated query normalization, normalized TF, and smoothed IDF, then score with `sum(tf * idf)` and sort by descending score then ascending doc ID.
### What I accepted:
Implemented module-level ranking with the specified TF-IDF formula, edge-case handling for empty/unknown queries, and deterministic ranking behavior; added a dedicated `tests/test_ranking.py` suite covering required Stage 8 scenarios.
### What I changed/rejected:
Did not integrate ranking into `search.py` or CLI yet, and did not add phrase scoring/suggestions/BM25 to keep Stage 8 focused, explainable, and aligned with coursework scope.
### Manual checks performed:
Ran `pytest` across the project after adding ranking and tests.
### What I learned:
A small, composable ranking module with explicit formulas and deterministic output is straightforward to explain in a short demo while still improving retrieval quality.

## Entry 10

### Date:
2026-05-07
### Tool used:
Cursor (Codex 5.3)
### Task:
Implemented Stage 9 by integrating TF-IDF ranking into CLI `find` output.
### Prompt summary:
Wire existing `find_documents` AND candidate retrieval with `rank_documents` scoring in `main.py`, print ranked results with 4-decimal scores, preserve exit-code behavior, and add focused `test_main.py` coverage.
### AI suggestion:
Keep architecture unchanged by composing existing Stage 5 and Stage 8 APIs in `handle_find`, pass `candidate_doc_ids` into ranking to preserve AND semantics, and use deterministic output from ranking with simple score formatting.
### What I accepted:
Added `rank_documents`/`RankedResult` integration in `main.py`, introduced `SCORE_DECIMAL_PLACES = 4`, and updated tests for ranked output, dependency-injected ranking calls, no-candidate and empty-ranked fallbacks, and empty-query short-circuit behavior.
### What I changed/rejected:
Did not modify `search.py`, `ranking.py`, or `cli.py`, and did not add OR retrieval, phrase search, suggestions, or new CLI flags to keep Stage 9 small and explainable.
### Manual checks performed:
Ran `pytest` after implementation to verify Stage 9 changes against the existing suite.
### What I learned:
Composing retrieval and ranking at the command-handler boundary gives clearer explainability than embedding ranking deeper in search logic while still improving practical output quality.

## Entry 11

### Date:
2026-05-07
### Tool used:
Cursor (Codex 5.3)
### Task:
Implemented Stage 10 phrase search using positional index data and integrated phrase routing into ranked CLI `find`.
### Prompt summary:
Add `find_phrase_documents` in `search.py` using `Posting.positions` for consecutive-term matching, detect only fully quoted phrases in `main.py`, preserve existing AND and TF-IDF behavior for non-phrase queries, and add comprehensive no-network tests.
### AI suggestion:
Keep phrase retrieval in `search.py` as a two-step pipeline (AND candidate filter, then positional offset validation), route quoted queries in `main.py` to phrase retrieval while passing candidate docs into existing ranker, and maintain deterministic ordering and output formatting.
### What I accepted:
Added a small typed phrase-search API (`find_phrase_documents` + `_has_consecutive_phrase`), integrated quoted-query routing in `handle_find`, and expanded `test_search.py`/`test_main.py` with phrase matching, routing, edge-case, and integration coverage.
### What I changed/rejected:
Did not modify tokenizer/indexer/ranking/CLI parser modules, did not add new CLI flags or query suggestions, and kept quote detection intentionally simple (only starts+ends with `\"`).
### Manual checks performed:
Ran `pytest` after implementation to verify all Stage 10 behavior and regressions.
### What I learned:
A positional phrase matcher can stay explainable and deterministic by reusing existing AND retrieval as a candidate filter and applying lightweight consecutive-offset checks only where needed.