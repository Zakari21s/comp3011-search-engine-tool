"""Parsing logic for extracting meaningful searchable page content."""

from __future__ import annotations

from dataclasses import dataclass
from bs4 import BeautifulSoup
from bs4.element import Tag


@dataclass(slots=True)
class ParsedPage:
    """Structured parse output for a single crawled page."""

    url: str
    title: str
    search_text: str
    quotes_count: int
    authors: list[str]
    tags: list[str]


def _normalize_whitespace(text: str) -> str:
    """Collapse repeated whitespace into single spaces."""
    return " ".join(text.split())


def parse_page(html: str, url: str = "") -> ParsedPage:
    """Parse Quotes to Scrape HTML into a content-focused structured page.

    Extraction targets quote blocks only:
    - quote text from ``span.text``
    - author from ``small.author``
    - tags from ``div.tags a.tag``
    """
    if not html or html.isspace():
        return ParsedPage(
            url=url,
            title="",
            search_text="",
            quotes_count=0,
            authors=[],
            tags=[],
        )

    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.find("title")
    title = ""
    if isinstance(title_tag, Tag):
        title = _normalize_whitespace(title_tag.get_text(" ", strip=True))

    search_parts: list[str] = []
    authors: list[str] = []
    tags: list[str] = []
    quotes_count = 0

    for quote_node in soup.select("div.quote"):
        if not isinstance(quote_node, Tag):
            continue

        quote_text_node = quote_node.select_one("span.text")
        author_node = quote_node.select_one("small.author")
        tag_nodes = quote_node.select("div.tags a.tag")

        quote_text = ""
        if isinstance(quote_text_node, Tag):
            quote_text = _normalize_whitespace(quote_text_node.get_text(" ", strip=True))

        author = ""
        if isinstance(author_node, Tag):
            author = _normalize_whitespace(author_node.get_text(" ", strip=True))

        quote_tags: list[str] = []
        for tag_node in tag_nodes:
            if not isinstance(tag_node, Tag):
                continue
            tag_text = _normalize_whitespace(tag_node.get_text(" ", strip=True))
            if tag_text:
                quote_tags.append(tag_text)

        if not quote_text and not author and not quote_tags:
            continue

        quotes_count += 1
        if quote_text:
            search_parts.append(quote_text)
        if author:
            search_parts.append(author)
            authors.append(author)
        if quote_tags:
            search_parts.extend(quote_tags)
            tags.extend(quote_tags)

    search_text = _normalize_whitespace(" ".join(search_parts))
    return ParsedPage(
        url=url,
        title=title,
        search_text=search_text,
        quotes_count=quotes_count,
        authors=authors,
        tags=tags,
    )

