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