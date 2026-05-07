"""Unit tests for Stage 6 crawler behavior."""

from __future__ import annotations

from dataclasses import dataclass

import pytest
import requests

import crawler
from crawler import crawl_quotes_site
from parser import ParsedPage


@dataclass(slots=True)
class FakeResponse:
    """Minimal fake response object for crawler tests."""

    status_code: int
    text: str


class FakeSession:
    """Deterministic fake requests session for crawler tests."""

    def __init__(
        self,
        responses: dict[str, FakeResponse],
        errors: dict[str, Exception] | None = None,
    ) -> None:
        self._responses = responses
        self._errors = errors or {}
        self.requested_urls: list[str] = []
        self.closed = False

    def get(self, url: str, timeout: float = 10.0) -> FakeResponse:
        _ = timeout
        self.requested_urls.append(url)
        if url in self._errors:
            raise self._errors[url]
        if url not in self._responses:
            raise AssertionError(f"Unexpected URL requested in test: {url}")
        return self._responses[url]

    def close(self) -> None:
        self.closed = True


def _quote_page_html(quote: str, author: str, next_href: str | None = None) -> str:
    """Build a minimal Quotes to Scrape-like HTML document."""
    next_part = ""
    if next_href is not None:
        next_part = f'<ul class="pager"><li class="next"><a href="{next_href}">Next</a></li></ul>'

    return (
        "<html><head><title>Quotes to Scrape</title></head><body>"
        f'<div class="quote"><span class="text">{quote}</span>'
        f'<small class="author">{author}</small>'
        '<div class="tags"><a class="tag">test</a></div></div>'
        f"{next_part}</body></html>"
    )


def test_single_page_crawl_returns_one_parsed_page() -> None:
    """A single page with no next link should return one ParsedPage."""
    start = "https://quotes.toscrape.com/"
    session = FakeSession(
        responses={
            start: FakeResponse(
                status_code=200,
                text=_quote_page_html('"Alpha quote"', "Author A"),
            )
        }
    )

    pages = crawl_quotes_site(start_url=start, delay_seconds=0, session=session)

    assert len(pages) == 1
    assert pages[0].url == start
    assert pages[0].quotes_count == 1


def test_multi_page_pagination_chain_returns_pages_in_order() -> None:
    """Crawler should follow next links sequentially in discovery order."""
    start = "https://quotes.toscrape.com/"
    page2 = "https://quotes.toscrape.com/page/2/"
    page3 = "https://quotes.toscrape.com/page/3/"
    session = FakeSession(
        responses={
            start: FakeResponse(200, _quote_page_html('"Page one"', "Author 1", "/page/2/")),
            page2: FakeResponse(200, _quote_page_html('"Page two"', "Author 2", "/page/3/")),
            page3: FakeResponse(200, _quote_page_html('"Page three"', "Author 3")),
        }
    )

    pages = crawl_quotes_site(start_url=start, delay_seconds=0, session=session)

    assert [page.url for page in pages] == [start, page2, page3]


def test_relative_next_links_are_resolved_correctly() -> None:
    """Relative pagination links should resolve against current page URL."""
    start = "https://quotes.toscrape.com/"
    next_url = "https://quotes.toscrape.com/page/2/"
    session = FakeSession(
        responses={
            start: FakeResponse(200, _quote_page_html('"Root"', "Author", "page/2/")),
            next_url: FakeResponse(200, _quote_page_html('"Second"', "Author")),
        }
    )

    pages = crawl_quotes_site(start_url=start, delay_seconds=0, session=session)
    assert [page.url for page in pages] == [start, next_url]


def test_duplicate_next_links_are_not_crawled_twice() -> None:
    """Repeatedly discovered URLs should only be fetched once."""
    start = "https://quotes.toscrape.com/"
    page2 = "https://quotes.toscrape.com/page/2/"
    page3 = "https://quotes.toscrape.com/page/3/"
    session = FakeSession(
        responses={
            start: FakeResponse(200, _quote_page_html('"Start"', "A", "/page/2/")),
            page2: FakeResponse(200, _quote_page_html('"Second"', "B", "/page/3/")),
            page3: FakeResponse(200, _quote_page_html('"Third"', "C", "/page/2/")),
        }
    )

    pages = crawl_quotes_site(start_url=start, delay_seconds=0, session=session)

    assert [page.url for page in pages] == [start, page2, page3]
    assert session.requested_urls.count(page2) == 1


def test_non_200_responses_are_skipped() -> None:
    """Non-200 pages should not be parsed or included in results."""
    start = "https://quotes.toscrape.com/"
    session = FakeSession(
        responses={
            start: FakeResponse(500, _quote_page_html('"Should skip"', "Author")),
        }
    )

    pages = crawl_quotes_site(start_url=start, delay_seconds=0, session=session)
    assert pages == []


def test_request_exception_is_handled_without_crashing() -> None:
    """Request exceptions should be handled by skipping failed URLs."""
    start = "https://quotes.toscrape.com/"
    session = FakeSession(
        responses={},
        errors={start: requests.RequestException("network issue")},
    )

    pages = crawl_quotes_site(start_url=start, delay_seconds=0, session=session)
    assert pages == []


def test_missing_next_link_stops_crawl() -> None:
    """Crawl should end when no next pagination link exists."""
    start = "https://quotes.toscrape.com/"
    session = FakeSession(
        responses={
            start: FakeResponse(200, _quote_page_html('"Only page"', "Author")),
        }
    )

    pages = crawl_quotes_site(start_url=start, delay_seconds=0, session=session)

    assert len(pages) == 1
    assert session.requested_urls == [start]


def test_crawler_only_follows_same_host_links() -> None:
    """Out-of-host next links should be ignored."""
    start = "https://quotes.toscrape.com/"
    external = "https://example.com/page/2/"
    session = FakeSession(
        responses={
            start: FakeResponse(200, _quote_page_html('"Root"', "Author", external)),
        }
    )

    pages = crawl_quotes_site(start_url=start, delay_seconds=0, session=session)

    assert [page.url for page in pages] == [start]
    assert external not in session.requested_urls


def test_delay_zero_avoids_sleep_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    """delay_seconds=0 should avoid sleeping between requests."""
    start = "https://quotes.toscrape.com/"
    page2 = "https://quotes.toscrape.com/page/2/"
    session = FakeSession(
        responses={
            start: FakeResponse(200, _quote_page_html('"One"', "A", "/page/2/")),
            page2: FakeResponse(200, _quote_page_html('"Two"', "B")),
        }
    )
    sleep_calls: list[float] = []
    monkeypatch.setattr(crawler.time, "sleep", lambda seconds: sleep_calls.append(seconds))

    _ = crawl_quotes_site(start_url=start, delay_seconds=0, session=session)

    assert sleep_calls == []


def test_politeness_sleep_called_between_requests(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Politeness delay should sleep between consecutive requests."""
    start = "https://quotes.toscrape.com/"
    page2 = "https://quotes.toscrape.com/page/2/"
    session = FakeSession(
        responses={
            start: FakeResponse(200, _quote_page_html('"One"', "A", "/page/2/")),
            page2: FakeResponse(200, _quote_page_html('"Two"', "B")),
        }
    )
    sleep_calls: list[float] = []
    monotonic_values = iter([100.0, 100.5, 100.5, 101.0])

    monkeypatch.setattr(crawler.time, "sleep", lambda seconds: sleep_calls.append(seconds))
    monkeypatch.setattr(crawler.time, "monotonic", lambda: next(monotonic_values))

    _ = crawl_quotes_site(start_url=start, delay_seconds=6.0, session=session)

    assert len(sleep_calls) == 1
    assert sleep_calls[0] == pytest.approx(5.5)


def test_parser_integration_returns_parsed_page_with_expected_text() -> None:
    """Crawler output should be ParsedPage objects from parse_page integration."""
    start = "https://quotes.toscrape.com/"
    session = FakeSession(
        responses={
            start: FakeResponse(
                200,
                _quote_page_html('"Life is beautiful."', "Author X"),
            )
        }
    )

    pages = crawl_quotes_site(start_url=start, delay_seconds=0, session=session)

    assert len(pages) == 1
    assert isinstance(pages[0], ParsedPage)
    assert "Life is beautiful." in pages[0].search_text

