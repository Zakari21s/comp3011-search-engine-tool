# Testing Strategy

## Objective

Achieve strong confidence and target >85% coverage through a balanced test suite that remains fast and deterministic.

## Test Layers

- **Unit tests**
  - Parser extraction behavior
  - Token normalization rules
  - Index posting generation (frequency and positions)
  - Ranking calculations and tie-breaking

- **Integration tests**
  - Build/load/print/find command flows
  - End-to-end pipeline with mocked crawl inputs
  - Planned: ranked CLI `find` output flow (ordering + score visibility)

- **Edge-case tests**
  - Empty queries
  - Unknown words
  - Planned: phrase search misses/hits
  - Planned: query suggestions for near-miss/unknown terms
  - Punctuation and case-insensitivity
  - Missing index file or invalid index schema

## Mocking Policy

- Mock HTTP requests in most tests.
- Keep a small number of opt-in live tests (if needed) separate and clearly marked.
- Avoid flaky timing assertions by isolating politeness-delay logic.

## Coverage and Quality Gates

- Start with smoke tests for scaffold integrity.
- Expand tests alongside each module implementation.
- Run `pytest -q` locally before each commit.
- Planned: benchmark helper/script checks for build/search timing output.
- Planned: coverage reporting (`pytest --cov`) and threshold verification.

