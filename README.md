# COMP3011 Coursework 2 - Search Engine Tool

A modular Python search engine for `https://quotes.toscrape.com/`, built with clear separation of concerns and explainable retrieval behaviour.

## Project Overview

The tool crawls quote pages, parses and tokenises text, builds an inverted index with frequencies and positions, persists it as JSON, and supports CLI retrieval with ranking, phrase search, and suggestion hints.

Stages 1-12 are implemented and tested. Stage 13 focuses on documentation polish.

## Implemented Features

- Polite crawler with a 6-second default delay between live requests
- Structured parser for quotes, authors, and tags
- Tokeniser with normalisation and positional tracking
- Inverted index with per-document term frequency and positions
- JSON save/load with schema validation
- CLI commands: `build`, `load`, `print`, `find`
- TF-IDF ranked output for `find`
- Phrase search using positional matching
- Query suggestions for unknown terms when no matches are found
- Lightweight benchmarking script (offline, existing index, and live modes)

## Installation and Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run commands from the project root. The CLI uses `data/index.json` as the default index path.

## Command Usage

### Build index

```bash
python -m src.main build
```

Crawls the site, builds the index, and saves it to `data/index.json`.

### Load index

```bash
python -m src.main load
```

Loads the saved index and prints basic corpus counts.

### Print postings for one term

```bash
python -m src.main print life
```

Prints postings for the normalised term, including frequency and positions per document.

### Find documents (ranked)

```bash
python -m src.main find life value
```

Runs AND-style matching on query terms, then ranks candidate documents with TF-IDF.

### Phrase search

```bash
python -m src.main find '"to be"'
```

Use a fully quoted query to trigger phrase search. Phrase matches are then ranked and printed.

## Ranked Search and Suggestions

- `find` output is ranked using TF-IDF and shown as `score=<value>` with four decimal places.
- Suggestions are shown only when no documents match and unknown terms have close vocabulary matches.
- Suggestions are informational only; the query is not auto-corrected.

## Testing and Coverage

Run all tests:

```bash
pytest
```

Run tests with coverage for `src/`:

```bash
pytest --cov=src --cov-report=term-missing
```

Current measured coverage: 90% across `src/`.

The suite includes unit tests for core modules plus command-handler integration-style tests for `build`, `load`, `print`, and `find`.

## Benchmarking

Run benchmark script:

```bash
python scripts/benchmark.py --mode offline --output both
```

Useful modes:
- `offline`: deterministic fixture-based run (recommended for repeatable checks)
- `existing`: measures operations using an existing index file
- `live`: performs real crawling (includes crawler politeness delay)

JSON benchmark reports can be written with `--json-path`.
Benchmarking is optional and intended for evaluation rather than correctness testing.

## Limitations and Assumptions

- Crawl scope is focused on `quotes.toscrape.com` pagination.
- The tokenisation strategy is intentionally simple; no stemming or lemmatisation is used.
- Suggestions are heuristic string matches, not semantic correction.
- Live benchmark timings depend on network conditions and polite crawl delays.

## Green AI / GenAI Disclosure

AI was used as a development assistant for planning, implementation support, and debugging. All generated suggestions were manually reviewed, and behaviour was validated through tests and manual checks before acceptance.

A dated record of AI-assisted decisions is provided in `docs/genai_log.md`.

## Further Documentation

- `docs/design_notes.md` - architecture and design rationale
- `docs/testing_strategy.md` - testing scope and quality strategy
- `docs/implementation_summary.md` - concise implementation status
- `docs/implementation_plan.md` - staged implementation roadmap
- `docs/genai_log.md` - Green AI usage log

