"""Crawling logic for fetching and parsing Quotes to Scrape pages."""

from __future__ import annotations

import time
from urllib.parse import urljoin, urlsplit, urlunsplit
from typing import Callable

from bs4 import BeautifulSoup
import requests

from src.parser import ParsedPage, parse_page


def _normalize_url(url: str) -> str:
    """Normalize a URL by removing fragments."""
    split = urlsplit(url)
    return urlunsplit((split.scheme, split.netloc, split.path, split.query, ""))


def _extract_next_url(current_url: str, html: str) -> str | None:
    """Extract and resolve the next pagination URL, if present."""
    soup = BeautifulSoup(html, "html.parser")
    next_link = soup.select_one("li.next > a[href]")
    if next_link is None:
        return None

    href = next_link.get("href")
    if not isinstance(href, str) or not href.strip():
        return None

    return _normalize_url(urljoin(current_url, href))


def _is_same_host(url: str, host: str) -> bool:
    """Return True when the URL host matches the crawl start host."""
    return urlsplit(url).netloc == host


def _enforce_delay(
    delay_seconds: float,
    last_request_at: float | None,
    now_fn: Callable[[], float] | None = None,
    sleep_fn: Callable[[float], None] | None = None,
) -> None:
    """Sleep only when needed to preserve the minimum request interval."""
    if delay_seconds <= 0 or last_request_at is None:
        return

    now = now_fn or time.monotonic
    sleep = sleep_fn or time.sleep

    elapsed = now() - last_request_at
    remaining = delay_seconds - elapsed
    if remaining > 0:
        sleep(remaining)


def crawl_quotes_site(
    start_url: str = "https://quotes.toscrape.com/",
    delay_seconds: float = 6.0,
    timeout_seconds: float = 10.0,
    session: requests.Session | None = None,
) -> list[ParsedPage]:
    """Crawl Quotes to Scrape pages sequentially and return parsed pages."""
    normalized_start_url = _normalize_url(start_url)
    start_host = urlsplit(normalized_start_url).netloc
    if not start_host:
        return []

    pages: list[ParsedPage] = []
    queue: list[str] = [normalized_start_url]
    visited_urls: set[str] = set()
    last_request_at: float | None = None

    request_session = session or requests.Session()
    owns_session = session is None

    try:
        while queue:
            current_url = queue.pop(0)
            if current_url in visited_urls:
                continue
            visited_urls.add(current_url)

            _enforce_delay(delay_seconds=delay_seconds, last_request_at=last_request_at)

            try:
                response = request_session.get(current_url, timeout=timeout_seconds)
            except requests.RequestException:
                continue
            finally:
                last_request_at = time.monotonic()

            if response.status_code != 200:
                continue

            html = response.text
            pages.append(parse_page(html, url=current_url))

            next_url = _extract_next_url(current_url, html)
            if next_url is None:
                continue
            if not _is_same_host(next_url, start_host):
                continue
            if next_url in visited_urls:
                continue
            if next_url in queue:
                continue

            queue.append(next_url)
    finally:
        if owns_session:
            request_session.close()

    return pages

