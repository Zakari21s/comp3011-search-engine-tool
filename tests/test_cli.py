"""Unit tests for Stage 7 CLI argument parsing."""

from __future__ import annotations

from cli import parse_args


def test_parse_build_command() -> None:
    """Parser should recognize the build command."""
    args = parse_args(["build"])
    assert args.command == "build"


def test_parse_load_command() -> None:
    """Parser should recognize the load command."""
    args = parse_args(["load"])
    assert args.command == "load"


def test_parse_print_command_with_word() -> None:
    """Parser should capture the required print word argument."""
    args = parse_args(["print", "life"])
    assert args.command == "print"
    assert args.word == "life"


def test_parse_find_command_with_query_terms() -> None:
    """Parser should capture one-or-more query terms for find."""
    args = parse_args(["find", "life", "wisdom"])
    assert args.command == "find"
    assert args.query_terms == ["life", "wisdom"]
