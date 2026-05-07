"""Application entrypoint for the search engine CLI."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from src.cli import parse_args
from src.crawler import crawl_quotes_site
from src.indexer import InvertedIndex, Posting, build_index
from src.parser import ParsedPage
from src.ranking import RankedResult, rank_documents
from src.search import (
    find_documents,
    find_phrase_documents,
    get_term_postings,
    suggest_query_terms,
)
from src.storage import load_index, save_index

DEFAULT_INDEX_PATH = Path("data/index.json")
SCORE_DECIMAL_PLACES = 4


def _safe_load(
    path: Path,
    *,
    load_index_fn: Callable[[Path], InvertedIndex],
) -> tuple[InvertedIndex | None, int]:
    """Load an index from disk and map expected errors to exit codes."""
    try:
        return load_index_fn(path), 0
    except FileNotFoundError:
        print(f"Index file not found at '{path}'. Run 'build' first.")
        return None, 1
    except ValueError as exc:
        print(f"Index file is invalid: {exc}")
        return None, 1


def handle_build(
    *,
    index_path: Path = DEFAULT_INDEX_PATH,
    crawl_fn: Callable[[], list[ParsedPage]] = crawl_quotes_site,
    build_index_fn: Callable[[list[ParsedPage]], InvertedIndex] = build_index,
    save_index_fn: Callable[[InvertedIndex, Path], None] = save_index,
) -> tuple[int, InvertedIndex]:
    """Build and save an index using crawler and indexer modules."""
    pages = crawl_fn()
    index = build_index_fn(pages)
    save_index_fn(index, index_path)
    print(
        f"Built and saved index to '{index_path}' "
        f"({len(index.doc_lengths)} docs, {len(index.postings)} terms)."
    )
    return 0, index


def handle_load(
    *,
    index_path: Path = DEFAULT_INDEX_PATH,
    load_index_fn: Callable[[Path], InvertedIndex] = load_index,
) -> tuple[int, InvertedIndex | None]:
    """Load an index from disk."""
    loaded_index, exit_code = _safe_load(index_path, load_index_fn=load_index_fn)
    if loaded_index is None:
        return exit_code, None

    print(
        f"Loaded index from '{index_path}' "
        f"({len(loaded_index.doc_lengths)} docs, {len(loaded_index.postings)} terms)."
    )
    return 0, loaded_index


def _ensure_index_loaded(
    current_index: InvertedIndex | None,
    *,
    index_path: Path,
    load_index_fn: Callable[[Path], InvertedIndex],
) -> tuple[InvertedIndex | None, int]:
    """Return current index or load it from disk when needed."""
    if current_index is not None:
        return current_index, 0
    return _safe_load(index_path, load_index_fn=load_index_fn)


def handle_print(
    word: str,
    *,
    current_index: InvertedIndex | None,
    index_path: Path = DEFAULT_INDEX_PATH,
    load_index_fn: Callable[[Path], InvertedIndex] = load_index,
    get_term_postings_fn: Callable[[InvertedIndex, str], dict[str, Posting]] = get_term_postings,
) -> tuple[int, InvertedIndex | None]:
    """Print postings for a word from the loaded or persisted index."""
    index, exit_code = _ensure_index_loaded(
        current_index,
        index_path=index_path,
        load_index_fn=load_index_fn,
    )
    if index is None:
        return exit_code, None

    postings = get_term_postings_fn(index, word)
    if not postings:
        print(f"No postings found for '{word}'.")
        return 0, index

    print(f"Postings for '{word}':")
    for doc_id in sorted(postings):
        posting = postings[doc_id]
        print(
            f"- {doc_id}: frequency={posting.frequency}, "
            f"positions={sorted(posting.positions)}"
        )
    return 0, index


def handle_find(
    query: str,
    *,
    current_index: InvertedIndex | None,
    index_path: Path = DEFAULT_INDEX_PATH,
    load_index_fn: Callable[[Path], InvertedIndex] = load_index,
    find_documents_fn: Callable[[InvertedIndex, str], list[str]] = find_documents,
    find_phrase_documents_fn: Callable[[InvertedIndex, str], list[str]] = find_phrase_documents,
    suggest_query_terms_fn: Callable[
        [InvertedIndex, str, int], dict[str, list[str]]
    ] = suggest_query_terms,
    rank_documents_fn: Callable[
        [InvertedIndex, str, list[str] | None], list[RankedResult]
    ] = rank_documents,
) -> tuple[int, InvertedIndex | None]:
    """Find and print matching documents for a query."""
    if not query.strip():
        print("Query cannot be empty.")
        return 1, current_index

    index, exit_code = _ensure_index_loaded(
        current_index,
        index_path=index_path,
        load_index_fn=load_index_fn,
    )
    if index is None:
        return exit_code, None

    is_phrase_query = query.startswith('"') and query.endswith('"') and len(query) >= 2
    if is_phrase_query:
        inner_phrase = query[1:-1]
        search_query = inner_phrase
        candidate_doc_ids = find_phrase_documents_fn(index, inner_phrase)
    else:
        search_query = query
        candidate_doc_ids = find_documents_fn(index, query)

    if not candidate_doc_ids:
        print("No matching documents found.")
        suggestions = suggest_query_terms_fn(index, search_query, 3)
        if suggestions:
            print("Did you mean:")
            for unknown_term, suggested_terms in suggestions.items():
                print(f"- {unknown_term} -> {', '.join(suggested_terms)}")
        return 0, index

    ranked_results = rank_documents_fn(index, search_query, candidate_doc_ids=candidate_doc_ids)
    if not ranked_results:
        print("No matching documents found.")
        return 0, index

    print("Matching documents (ranked):")
    for result in ranked_results:
        print(f"- {result.doc_id}  score={result.score:.{SCORE_DECIMAL_PLACES}f}")
    return 0, index


def run() -> int:
    """Run the CLI command dispatcher."""
    args = parse_args()
    current_index: InvertedIndex | None = None

    if args.command == "build":
        exit_code, _built_index = handle_build()
        return exit_code

    if args.command == "load":
        exit_code, _loaded_index = handle_load()
        return exit_code

    if args.command == "print":
        exit_code, _updated_index = handle_print(args.word, current_index=current_index)
        return exit_code

    if args.command == "find":
        query = " ".join(args.query_terms)
        exit_code, _updated_index = handle_find(query, current_index=current_index)
        return exit_code

    print(f"Unsupported command '{args.command}'.")
    return 1


if __name__ == "__main__":
    raise SystemExit(run())

