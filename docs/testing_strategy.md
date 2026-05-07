# Testing Strategy

## Objective

Achieve strong confidence and target >85% coverage through a balanced test suite that remains fast and deterministic.

## Test Layers

- **Unit tests**
  - Parser extraction behavior
  - Token normalization rules
  - Index posting generation (frequency and positions)
  - Ranking calculations and tie-breaking
  - Storage schema validation and error handling
  - Search behaviour (single term, multi-term AND, phrase matching, suggestions)
  - Crawler behaviour with mocked HTTP and politeness logic

- **Integration-style tests**
  - `build`, `load`, `print`, and `find` command-handler flows
  - Ranked CLI `find` output flow (ordering and score visibility)
  - Phrase routing and no-match suggestion output in CLI flows

- **Edge-case tests**
  - Empty queries
  - Unknown words
  - Phrase search misses/hits, including repeated terms
  - Query suggestions for near-miss/unknown terms
  - Punctuation and case-insensitivity
  - Missing index file or invalid index schema

- **Benchmark tests**
  - Benchmark report structure and timing fields
  - Terminal formatter output
  - JSON report writing and path handling

## Mocking Policy

- Mock HTTP requests in most tests.
- Keep a small number of opt-in live tests (if needed) separate and clearly marked.
- Avoid flaky timing assertions by isolating politeness-delay logic.

## Coverage and Quality Gates

- Start with smoke tests for scaffold integrity.
- Expand tests alongside each module implementation.
- Run `pytest -q` locally before each commit.
- Validate benchmark helper/script output through dedicated tests.
- Use `pytest --cov=src --cov-report=term-missing` for coverage checks.

## Residual Limitations

- Most command flow tests are integration-style handler tests rather than full subprocess end-to-end tests.
- Coverage tooling is configured for `src/`; benchmark scripts are tested but excluded from coverage measurement.

