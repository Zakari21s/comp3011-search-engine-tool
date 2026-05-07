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
- stop-word filtering

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

# 7. Planned Development Stages

1. Tokenizer
2. Parser
3. Indexer
4. Storage
5. Search logic
6. Crawler
7. CLI integration
8. Ranking features
9. Testing expansion
10. Documentation and video preparation