"""Command-line interface helpers for search engine actions."""

from __future__ import annotations

from argparse import ArgumentParser, Namespace


def build_parser() -> ArgumentParser:
    """Create and return the root CLI parser."""
    parser = ArgumentParser(description="COMP3011 Search Engine Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # TODO: Add detailed options for each command as implementation grows.
    subparsers.add_parser("build", help="Crawl pages and build an index")
    subparsers.add_parser("load", help="Load an index from disk")
    subparsers.add_parser("print", help="Print index statistics/content")

    find_parser = subparsers.add_parser("find", help="Search for a query")
    find_parser.add_argument("query", type=str, help="Query string to search")

    return parser


def parse_args(argv: list[str] | None = None) -> Namespace:
    """Parse CLI arguments from argv or sys.argv."""
    return build_parser().parse_args(argv)

