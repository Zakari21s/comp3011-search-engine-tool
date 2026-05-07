# Implementation Summary

## Current Status

Stages 1-13 are complete:
- Stages 1-12: functional implementation, testing, and benchmarking
- Stage 13: documentation polish

Stage 14 (final live testing and video preparation) remains planned.

## Implemented System

- `crawler.py`: polite crawling for `quotes.toscrape.com` with pagination traversal
- `parser.py`: structured quote, author, and tag extraction
- `tokenizer.py`: normalisation and positional token tracking
- `indexer.py`: inverted index construction with frequencies and positions
- `storage.py`: JSON persistence with schema validation
- `search.py`: term retrieval, AND search, phrase search, and suggestions
- `ranking.py`: TF-IDF ranking for candidate documents
- `cli.py` and `main.py`: command parsing and command handling (`build`, `load`, `print`, `find`)
- `scripts/benchmark.py`: offline/existing/live benchmark reporting

## Testing and Quality

- Test suite covers unit and integration-style command-handler flows.
- Edge cases include empty queries, unknown terms, phrase mismatches, malformed index files, and crawler failure paths.
- Coverage tooling is configured for `src/` via `pytest-cov`.

## Known Limitations

- Crawl scope is focused on the `quotes.toscrape.com` pagination path.
- Linguistic processing is intentionally simple (no stemming or lemmatisation).
- Suggestions are heuristic string matches and are shown only on no-match flows.

## Design Principles

- Keep module boundaries clear and explainable.
- Prefer deterministic, testable behaviour over unnecessary complexity.
- Maintain coursework-oriented clarity for implementation and demonstration.
