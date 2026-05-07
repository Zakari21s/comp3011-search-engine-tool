"""Unit tests for Stage 2 parser behavior."""

from __future__ import annotations

from src.parser import ParsedPage, parse_page


def test_parse_page_extracts_quote_author_and_tags() -> None:
    """Parser should extract quote text, author, and tags from a quote block."""
    html = """
    <html>
      <head><title>Quotes to Scrape</title></head>
      <body>
        <div class="quote">
          <span class="text">"Life is what happens."</span>
          <span><small class="author">John Lennon</small></span>
          <div class="tags">
            <a class="tag">life</a>
            <a class="tag">inspiration</a>
          </div>
        </div>
      </body>
    </html>
    """
    parsed = parse_page(html, url="https://quotes.toscrape.com/page/1/")
    assert parsed.url == "https://quotes.toscrape.com/page/1/"
    assert parsed.title == "Quotes to Scrape"
    assert parsed.quotes_count == 1
    assert parsed.authors == ["John Lennon"]
    assert parsed.tags == ["life", "inspiration"]
    assert parsed.search_text == '"Life is what happens." John Lennon life inspiration'


def test_parse_page_builds_search_text_in_deterministic_order() -> None:
    """search_text should follow quote -> author -> tags ordering per quote."""
    html = """
    <html>
      <body>
        <div class="quote">
          <span class="text">"First quote."</span>
          <small class="author">Author One</small>
          <div class="tags"><a class="tag">first</a><a class="tag">tag1</a></div>
        </div>
        <div class="quote">
          <span class="text">"Second quote."</span>
          <small class="author">Author Two</small>
          <div class="tags"><a class="tag">second</a><a class="tag">tag2</a></div>
        </div>
      </body>
    </html>
    """
    parsed = parse_page(html)
    assert (
        parsed.search_text
        == '"First quote." Author One first tag1 "Second quote." Author Two second tag2'
    )


def test_parse_page_extracts_title_when_present() -> None:
    """Parser should extract the page title when available."""
    html = "<html><head><title>  Quotes  Home </title></head><body></body></html>"
    assert parse_page(html).title == "Quotes Home"


def test_parse_page_returns_empty_title_when_missing() -> None:
    """Parser should default to empty title when <title> is absent."""
    html = "<html><body><div class='quote'><span class='text'>Hi</span></div></body></html>"
    assert parse_page(html).title == ""


def test_parse_page_returns_empty_parsed_page_for_empty_html() -> None:
    """Empty input should return an empty ParsedPage without raising."""
    assert parse_page("", url="https://quotes.toscrape.com/") == ParsedPage(
        url="https://quotes.toscrape.com/",
        title="",
        search_text="",
        quotes_count=0,
        authors=[],
        tags=[],
    )
    assert parse_page("   \n\t  ").quotes_count == 0


def test_parse_page_handles_malformed_html_without_exception() -> None:
    """Malformed HTML should still return a valid parse result."""
    html = (
        "<html><head><title>Bad</title></head><body><div class='quote'>"
        "<span class='text'>Broken quote"
    )
    parsed = parse_page(html)
    assert isinstance(parsed, ParsedPage)
    assert parsed.quotes_count == 1
    assert "Broken quote" in parsed.search_text


def test_parse_page_handles_missing_author_and_tags_gracefully() -> None:
    """Quote text should still be indexed when author/tags are missing."""
    html = """
    <html>
      <body>
        <div class="quote">
          <span class="text">"Standalone quote."</span>
        </div>
      </body>
    </html>
    """
    parsed = parse_page(html)
    assert parsed.quotes_count == 1
    assert parsed.authors == []
    assert parsed.tags == []
    assert parsed.search_text == '"Standalone quote."'


def test_parse_page_preserves_page_order_across_multiple_quotes() -> None:
    """Extraction should preserve quote order from the source page."""
    html = """
    <html>
      <body>
        <div class="quote"><span class="text">One</span><small class="author">A1</small></div>
        <div class="quote"><span class="text">Two</span><small class="author">A2</small></div>
      </body>
    </html>
    """
    parsed = parse_page(html)
    assert parsed.authors == ["A1", "A2"]
    assert parsed.search_text == "One A1 Two A2"


def test_parse_page_normalizes_whitespace() -> None:
    """Repeated spaces/newlines/tabs should collapse to single spaces."""
    html = """
    <html>
      <head><title>Quotes \n\t Site</title></head>
      <body>
        <div class="quote">
          <span class="text">  Quote   with \n   spacing </span>
          <small class="author">\tAuthor  Name </small>
          <div class="tags"><a class="tag"> life \n</a></div>
        </div>
      </body>
    </html>
    """
    parsed = parse_page(html)
    assert parsed.title == "Quotes Site"
    assert parsed.search_text == "Quote with spacing Author Name life"


def test_parse_page_ignores_unrelated_noise_text() -> None:
    """Parser should avoid indexing generic nav/footer page noise."""
    html = """
    <html>
      <body>
        <nav>Home About Login</nav>
        <div class="quote">
          <span class="text">Core quote text</span>
          <small class="author">Core Author</small>
          <div class="tags"><a class="tag">core</a></div>
        </div>
        <footer>Privacy Terms Contact</footer>
      </body>
    </html>
    """
    parsed = parse_page(html)
    assert parsed.search_text == "Core quote text Core Author core"
    assert "Home" not in parsed.search_text
    assert "Privacy" not in parsed.search_text
