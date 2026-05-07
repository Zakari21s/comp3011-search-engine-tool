"""Crawling logic for fetching pages and discovering links."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol


class HttpClient(Protocol):
    """Protocol for HTTP clients used by the crawler."""

    def get(self, url: str, timeout: float = 10.0) -> str:
        """Return raw HTML content for the provided URL."""


@dataclass(slots=True)
class CrawlResult:
    """Container for a crawled page."""

    url: str
    html: str
    discovered_links: list[str]


class Crawler:
    """Crawl seed URLs and collect page HTML/link metadata."""

    def __init__(self, client: HttpClient, politeness_delay_seconds: float = 6.0) -> None:
        self._client = client
        self._politeness_delay_seconds = politeness_delay_seconds

    def crawl(self, seed_urls: Iterable[str], max_pages: int = 50) -> list[CrawlResult]:
        """Crawl a set of seed URLs and return page-level crawl results."""
        # TODO: Implement BFS/queue traversal with domain and duplicate controls.
        # TODO: Enforce politeness delay between live requests.
        # TODO: Handle request failures gracefully and continue crawling.
        _ = (seed_urls, max_pages)
        return []

