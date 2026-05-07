# Design Notes

## Goal

Build a compact, explainable search engine that is easy to demo in a 5-minute coursework video while still supporting high-mark features.

## Architectural Principles

- Keep modules focused on one responsibility.
- Keep data flow explicit between crawl -> parse -> tokenize -> index -> search.
- Keep decisions testable with small, deterministic units.
- Keep advanced features explainable rather than over-engineered.

## Planned Module Responsibilities

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

1. Implement crawl + parse with mocked network tests.
2. Implement tokenizer + indexer with edge-case tests.
3. Implement storage with file-format validation tests.
4. Implement search (single, multi-word, phrase) + ranking.
5. Wire CLI commands and add integration tests.
6. Add benchmarks and refine README/video narrative.

## Assumptions and Constraints

- Primary crawl target is `https://quotes.toscrape.com/`.
- Most tests should mock network I/O.
- Live crawling must respect a 6-second politeness delay.
- The design should stay simple enough for oral justification.

