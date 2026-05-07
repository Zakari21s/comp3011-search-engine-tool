# Implementation Summary

## Current Project Status
Short overview of completed implementation stages.

---

# Architecture Overview

## crawler.py
Responsibility:
- handles polite crawling
- follows pagination links
- avoids duplicate URLs

Important decisions:
- uses BFS crawling
- uses requests.Session
- enforces 6-second delay

---

## tokenizer.py
Responsibility:
- lowercase normalization
- punctuation removal
- token position tracking

Important decisions:
- regex-based tokenization
- preserves word order for phrase search

---

# Current Features
- tokenizer implemented
- unit tests passing
- position tracking supported

---

# Pending Features
- parser implementation
- inverted index builder
- persistence layer
- TF-IDF ranking

---

# Testing Status
- tokenizer tests complete
- crawler tests pending

---

# Known Limitations
- no stemming yet
- no stop-word filtering yet

---

# Important Design Principles
- keep implementation explainable
- prioritise testability
- avoid over-engineering
- coursework targets outstanding grade

---

# Branch Status
Current branch:
feature/tokenizer

---

# Stage 1 Update (Tokenizer)
- implemented `Token` dataclass with `term` and `position`
- implemented public API `tokenize(text: str) -> list[Token]`
- tokenizer lowercases text, treats punctuation as separators, preserves order, and excludes pure numbers
- positions are 0-based by token order to support later phrase search logic
- added unit tests for lowercase handling, punctuation behavior, repeated words, whitespace/empty input, spacing variants, position tracking, and numeric/alphanumeric cases