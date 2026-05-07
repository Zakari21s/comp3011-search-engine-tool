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