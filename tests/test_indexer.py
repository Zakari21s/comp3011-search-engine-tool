"""Unit tests for Stage 3 in-memory inverted index behavior."""

from __future__ import annotations

from indexer import build_index
from parser import ParsedPage


def test_build_index_empty_input_returns_empty_structure() -> None:
    """Empty input should produce an empty but valid index object."""
    index = build_index([])
    assert index.postings == {}
    assert index.doc_lengths == {}
    assert index.doc_metadata == {}


def test_build_index_one_page_postings_frequency_and_positions() -> None:
    """One page should create postings with correct counts and positions."""
    page = ParsedPage(
        url="https://quotes.toscrape.com/page/1/",
        title="Quotes Page 1",
        search_text="Life is beautiful life",
        quotes_count=1,
        authors=[],
        tags=[],
    )
    index = build_index([page])
    doc_id = "https://quotes.toscrape.com/page/1/"

    assert index.doc_lengths[doc_id] == 4
    assert index.postings["life"][doc_id].frequency == 2
    assert index.postings["life"][doc_id].positions == [0, 3]
    assert index.postings["is"][doc_id].frequency == 1
    assert index.postings["beautiful"][doc_id].positions == [2]


def test_build_index_repeated_terms_keep_all_positions() -> None:
    """Repeated terms should increment frequency and preserve position order."""
    page = ParsedPage(
        url="https://quotes.toscrape.com/page/2/",
        title="Repeated Terms",
        search_text="echo echo echo",
        quotes_count=1,
        authors=[],
        tags=[],
    )
    index = build_index([page])
    doc_id = "https://quotes.toscrape.com/page/2/"

    assert index.postings["echo"][doc_id].frequency == 3
    assert index.postings["echo"][doc_id].positions == [0, 1, 2]


def test_build_index_multiple_pages_share_term_in_multi_doc_postings() -> None:
    """Shared terms should map to postings for multiple documents."""
    page_one = ParsedPage(
        url="https://quotes.toscrape.com/page/1/",
        title="Page One",
        search_text="life wisdom",
        quotes_count=1,
        authors=[],
        tags=[],
    )
    page_two = ParsedPage(
        url="https://quotes.toscrape.com/page/2/",
        title="Page Two",
        search_text="life courage",
        quotes_count=1,
        authors=[],
        tags=[],
    )
    index = build_index([page_one, page_two])

    assert set(index.postings["life"].keys()) == {
        "https://quotes.toscrape.com/page/1/",
        "https://quotes.toscrape.com/page/2/",
    }
    assert index.postings["wisdom"]["https://quotes.toscrape.com/page/1/"].frequency == 1
    assert index.postings["courage"]["https://quotes.toscrape.com/page/2/"].frequency == 1


def test_build_index_empty_search_text_stores_metadata_and_zero_length() -> None:
    """Empty search text should still store doc metadata and length zero."""
    page = ParsedPage(
        url="https://quotes.toscrape.com/page/3/",
        title="Empty Page",
        search_text="",
        quotes_count=0,
        authors=[],
        tags=[],
    )
    index = build_index([page])
    doc_id = "https://quotes.toscrape.com/page/3/"

    assert index.doc_lengths[doc_id] == 0
    assert doc_id in index.doc_metadata
    assert index.postings == {}


def test_build_index_duplicate_urls_use_first_write_wins() -> None:
    """Later pages with the same URL should be skipped."""
    first_page = ParsedPage(
        url="https://quotes.toscrape.com/page/4/",
        title="First Version",
        search_text="alpha beta",
        quotes_count=1,
        authors=[],
        tags=[],
    )
    second_page = ParsedPage(
        url="https://quotes.toscrape.com/page/4/",
        title="Second Version",
        search_text="gamma delta",
        quotes_count=9,
        authors=[],
        tags=[],
    )
    index = build_index([first_page, second_page])
    doc_id = "https://quotes.toscrape.com/page/4/"

    assert index.doc_metadata[doc_id].title == "First Version"
    assert "alpha" in index.postings
    assert "gamma" not in index.postings
    assert index.doc_lengths[doc_id] == 2


def test_build_index_missing_url_generates_deterministic_doc_ids() -> None:
    """Missing URLs should use deterministic fallback IDs in order."""
    first_page = ParsedPage(
        url="",
        title="No Url One",
        search_text="first content",
        quotes_count=1,
        authors=[],
        tags=[],
    )
    second_page = ParsedPage(
        url="",
        title="No Url Two",
        search_text="second content",
        quotes_count=2,
        authors=[],
        tags=[],
    )
    index = build_index([first_page, second_page])

    assert "doc_0" in index.doc_metadata
    assert "doc_1" in index.doc_metadata
    assert index.doc_metadata["doc_0"].title == "No Url One"
    assert index.doc_metadata["doc_1"].title == "No Url Two"


def test_build_index_tokenizer_integration_lowercase_and_punctuation() -> None:
    """Indexing should respect tokenizer lowercase and punctuation behavior."""
    page = ParsedPage(
        url="https://quotes.toscrape.com/page/5/",
        title="Tokenizer Integration",
        search_text="Hello, WORLD! Hello.",
        quotes_count=1,
        authors=[],
        tags=[],
    )
    index = build_index([page])
    doc_id = "https://quotes.toscrape.com/page/5/"

    assert "hello" in index.postings
    assert "world" in index.postings
    assert "Hello" not in index.postings
    assert index.postings["hello"][doc_id].frequency == 2
    assert index.postings["hello"][doc_id].positions == [0, 2]


def test_build_index_stores_document_metadata() -> None:
    """Document metadata should be retained for each indexed document."""
    page = ParsedPage(
        url="https://quotes.toscrape.com/page/6/",
        title="Metadata Title",
        search_text="metadata test",
        quotes_count=7,
        authors=["A"],
        tags=["t"],
    )
    index = build_index([page])
    metadata = index.doc_metadata["https://quotes.toscrape.com/page/6/"]

    assert metadata.url == "https://quotes.toscrape.com/page/6/"
    assert metadata.title == "Metadata Title"
    assert metadata.quotes_count == 7
