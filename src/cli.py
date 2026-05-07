"""Argument parsing utilities for search engine CLI commands."""

from __future__ import annotations

from argparse import ArgumentParser, Namespace


def build_parser() -> ArgumentParser:
    """Create and return the root argparse parser."""
    parser = ArgumentParser(description="COMP3011 Search Engine Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("build", help="Crawl pages and build an index")
    subparsers.add_parser("load", help="Load an index from disk")
    print_parser = subparsers.add_parser("print", help="Print postings for one word")
    print_parser.add_argument("word", type=str, help="Word to look up in the index")

    find_parser = subparsers.add_parser("find", help="Find documents matching a query")
    find_parser.add_argument(
        "query_terms",
        nargs="+",
        type=str,
        help="One or more query terms",
    )

    return parser


def parse_args(argv: list[str] | None = None) -> Namespace:
    """Parse CLI arguments from argv or sys.argv."""
    return build_parser().parse_args(argv)

