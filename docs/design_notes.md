# Design Notes

## Goal

Build a compact, explainable search engine that is easy to demo in a 5-minute coursework video while still supporting high-mark features.

## Architectural Principles

- Keep modules focused on one responsibility.
- Keep data flow explicit between crawl -> parse -> tokenize -> index -> search.
- Keep decisions testable with small, deterministic units.
- Keep advanced features explainable rather than over-engineered.

## Module Responsibilities

- `crawler.py`: Fetch pages, follow links, enforce politeness delay.
- `parser.py`: Extract meaningful text and metadata from HTML.
- `tokenizer.py`: Normalize text into searchable tokens.
- `indexer.py`: Build inverted index with frequency and positions.
- `storage.py`: Save/load index files from disk.
- `search.py`: Process queries and coordinate retrieval.
- `ranking.py`: Score results (TF-IDF and tie-breaking policy).
- `cli.py`: Parse and validate command-line inputs.
- `main.py`: Program entrypoint and command dispatch.

## Incremental Development Plan

1. [Complete] Stage 1 - Tokenizer foundation.
2. [Complete] Stage 2 - Parser extraction.
3. [Complete] Stage 3 - Inverted index construction.
4. [Complete] Stage 4 - Index storage (save/load).
5. [Complete] Stage 5 - Core search logic (single and multi-word).
6. [Complete] Stage 6 - Crawler implementation with politeness delay.
7. [Complete] Stage 7 - CLI command integration (`build`, `load`, `print`, `find`).
8. [Complete] Stage 8 - TF-IDF ranking module implementation.
9. [Complete] Stage 9 - Integrate ranking into CLI `find` output.
10. [Complete] Stage 10 - Phrase search using positional index data.
11. [Complete] Stage 11 - Query suggestions using simple edit-distance/`difflib`.
12. [Complete] Stage 12 - Benchmarking and coverage checks.
13. [Complete] Stage 13 - README and documentation polish.
14. [Planned] Stage 14 - Final live testing and video preparation.

Notes:
- Ranking logic from `ranking.py` is wired into CLI `find` output while preserving AND candidate retrieval from `search.py`.
- Phrase search and query suggestions are implemented as advanced but explainable coursework features.

## Assumptions and Constraints

- Primary crawl target is `https://quotes.toscrape.com/`.
- Most tests should mock network I/O.
- Live crawling must respect a 6-second politeness delay.
- The design should stay simple enough for oral justification.

