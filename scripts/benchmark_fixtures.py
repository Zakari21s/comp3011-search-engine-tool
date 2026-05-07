"""Synthetic fixtures for offline benchmark mode."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin


@dataclass(slots=True)
class FakeResponse:
    """Minimal fake response compatible with crawler session usage."""

    status_code: int
    text: str


class FakeSession:
    """Deterministic fake requests session used by benchmark offline mode."""

    def __init__(
        self,
        responses: dict[str, FakeResponse],
    ) -> None:
        self._responses = responses
        self.requested_urls: list[str] = []
        self.closed = False

    def get(self, url: str, timeout: float = 10.0) -> FakeResponse:
        """Return fixture response for URL and record request history."""
        _ = timeout
        self.requested_urls.append(url)
        if url not in self._responses:
            raise RuntimeError(f"No fixture response for URL: {url}")
        return self._responses[url]

    def close(self) -> None:
        """Mirror requests.Session close lifecycle."""
        self.closed = True


def make_quotes_page_html(
    quote_text: str,
    author: str,
    tags: list[str],
    next_href: str | None = None,
) -> str:
    """Build a tiny Quotes-to-Scrape-style HTML page."""
    tag_html = "".join(f'<a class="tag">{tag}</a>' for tag in tags)
    next_html = ""
    if next_href:
        next_html = (
            '<ul class="pager"><li class="next">'
            f'<a href="{next_href}">Next</a>'
            "</li></ul>"
        )

    return (
        "<html><head><title>Quotes to Scrape</title></head><body>"
        '<div class="quote">'
        f'<span class="text">{quote_text}</span>'
        f'<small class="author">{author}</small>'
        f'<div class="tags">{tag_html}</div>'
        "</div>"
        f"{next_html}"
        "</body></html>"
    )


def make_pagination_fixture_chain(
    start_url: str = "https://quotes.toscrape.com/",
) -> dict[str, FakeResponse]:
    """Create a deterministic 3-page pagination chain for offline benchmarks."""
    page_two_url = urljoin(start_url, "/page/2/")
    page_three_url = urljoin(start_url, "/page/3/")

    return {
        start_url: FakeResponse(
            status_code=200,
            text=make_quotes_page_html(
                quote_text='"Life is about making an impact."',
                author="Kevin Kruse",
                tags=["life", "impact"],
                next_href="/page/2/",
            ),
        ),
        page_two_url: FakeResponse(
            status_code=200,
            text=make_quotes_page_html(
                quote_text='"Whatever the mind can conceive and believe."',
                author="Napoleon Hill",
                tags=["mind", "believe"],
                next_href="/page/3/",
            ),
        ),
        page_three_url: FakeResponse(
            status_code=200,
            text=make_quotes_page_html(
                quote_text='"Strive not to be a success, but rather to be of value."',
                author="Albert Einstein",
                tags=["success", "value"],
                next_href=None,
            ),
        ),
    }
