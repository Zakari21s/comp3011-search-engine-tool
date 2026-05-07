"""Smoke tests for project scaffolding and imports."""

from __future__ import annotations


def test_project_scaffold_placeholder() -> None:
    """Keep a passing placeholder while implementation is pending."""
    assert True


def test_core_modules_importable() -> None:
    """Ensure module skeletons remain importable."""
    import cli
    import crawler
    import indexer
    import main
    import parser
    import ranking
    import search
    import storage
    import tokenizer

    assert all([cli, crawler, indexer, main, parser, ranking, search, storage, tokenizer])

