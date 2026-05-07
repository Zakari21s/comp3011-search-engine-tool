# COMP3011 Coursework 2 - Search Engine Tool

A modular Python search engine coursework project focused on clean architecture, testability, and explainable design.

## Current Status

This repository currently contains a professional project skeleton only.
Core functionality is intentionally not implemented yet.

## Project Structure

- `src/crawler.py` - page fetching and crawl control
- `src/parser.py` - HTML content extraction
- `src/tokenizer.py` - text normalization/tokenization
- `src/indexer.py` - inverted index creation
- `src/storage.py` - index persistence
- `src/search.py` - query processing and retrieval
- `src/ranking.py` - ranking/scoring logic
- `src/cli.py` - CLI argument parsing
- `src/main.py` - executable entrypoint
- `tests/` - placeholder tests to be expanded with implementation
- `docs/design_notes.md` - architecture rationale
- `docs/testing_strategy.md` - testing plan
- `docs/genai_log.md` - AI usage log (preserved)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run Tests

```bash
pytest
```

## CLI Commands (Required)

```bash
python -m src.main
> build
> load
> print nonsense
> find good friends
```

## Next Implementation Milestones

1. Implement crawling with politeness and duplicate-link handling.
2. Implement parsing/tokenization pipeline.
3. Build inverted index with frequencies and positions.
4. Add save/load index persistence.
5. Implement search commands (single, multi-word, phrase).
6. Add ranking and suggestion features.
7. Expand tests for edge cases and integration flows.

## Coursework Focus

- Explainable architecture aligned with module boundaries.
- High test coverage with mocked HTTP for reliability.
- Incremental delivery with clear design rationale.

