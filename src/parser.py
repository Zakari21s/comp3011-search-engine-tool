"""Parsing logic for extracting meaningful text from pages."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ParsedDocument:
    """Parsed representation of a crawled page."""

    url: str
    title: str
    text: str


class Parser:
    """Extract searchable content and metadata from raw HTML."""

    def parse(self, url: str, html: str) -> ParsedDocument:
        """Parse a page's HTML into a structured document."""
        # TODO: Extract text from relevant page regions.
        # TODO: Remove noisy content while preserving quote context.
        # TODO: Handle malformed HTML robustly.
        _ = html
        return ParsedDocument(url=url, title="", text="")

