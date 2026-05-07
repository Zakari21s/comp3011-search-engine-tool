# COMP3011 Coursework 2 - Implementation Plan

## 1. Project Goal

This project aims to implement a miniature search engine in Python capable of:
- crawling a website
- extracting and tokenising text
- building an inverted index
- saving/loading the index
- processing search queries

The implementation targets an outstanding-grade submission through clean architecture, strong testing, and advanced but explainable search features.

---

# 2. Planned Architecture

## crawler.py
Responsible for:
- HTTP requests
- polite crawling
- duplicate URL handling
- pagination traversal

## parser.py
Responsible for:
- HTML extraction
- text cleaning
- quote/page content extraction

## tokenizer.py
Responsible for:
- lowercase normalization
- punctuation handling
- token position tracking

## indexer.py
Responsible for:
- inverted index construction
- frequency tracking
- positional indexing

## storage.py
Responsible for:
- saving/loading index files
- JSON serialization

## search.py
Responsible for:
- query parsing
- AND search
- phrase search

## ranking.py
Responsible for:
- TF-IDF scoring
- result ranking

---

# 3. Planned Features

## Core Coursework Features
- build command
- load command
- print command
- find command
- case-insensitive search
- inverted index with frequencies and positions

## Advanced Features
- TF-IDF ranking
- phrase search
- query suggestions
- benchmarking

---

# 4. Testing Strategy

The project will use:
- pytest
- unit tests
- integration tests
- mocked HTTP requests
- edge-case testing

Target:
- above 85% test coverage

---

# 5. Git Workflow

Development will use:
- feature branches
- semantic commit messages
- incremental commits

---

# 6. AI Usage Strategy

Cursor AI and GenAI tools will be used as development assistants rather than automatic code generators.

All generated code will be:
- reviewed
- tested
- simplified if necessary
- fully understood before submission

AI usage and reflections will be documented in:
docs/genai_log.md

---

# 7. Development Stages (Updated)

Completed (Stages 1-13):
1. [Complete] Stage 1 - Tokenizer foundation
2. [Complete] Stage 2 - Parser extraction
3. [Complete] Stage 3 - Inverted index construction
4. [Complete] Stage 4 - Index storage (save/load)
5. [Complete] Stage 5 - Core search logic (single and multi-word)
6. [Complete] Stage 6 - Crawler implementation with politeness
7. [Complete] Stage 7 - CLI command flow (`build`, `load`, `print`, `find`)
8. [Complete] Stage 8 - TF-IDF ranking module implementation
9. [Complete] Stage 9 - Integrate TF-IDF ranking into CLI `find` output
10. [Complete] Stage 10 - Add phrase search using positional index data
11. [Complete] Stage 11 - Add query suggestions (simple edit-distance/`difflib`)
12. [Complete] Stage 12 - Benchmarking and coverage checks
13. [Complete] Stage 13 - README and documentation polish

Planned:
14. [Planned] Stage 14 - Final live testing and video preparation