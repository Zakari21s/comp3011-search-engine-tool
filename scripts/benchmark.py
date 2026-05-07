"""Lightweight benchmark runner for Stage 12."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
import statistics
import sys
import tempfile
import time
from typing import Any, Callable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from crawler import crawl_quotes_site
from indexer import InvertedIndex, build_index
from ranking import rank_documents
from search import find_documents, find_phrase_documents, suggest_query_terms
from storage import load_index, save_index

from benchmark_fixtures import FakeSession, make_pagination_fixture_chain

BENCHMARK_RUNS = 3
DEFAULT_JSON_REPORT_PATH = Path("data/benchmark.json")
DEFAULT_INDEX_PATH = Path("data/index.json")
DEFAULT_SINGLE_QUERY = "life"
DEFAULT_MULTI_QUERY = "life value"
DEFAULT_PHRASE_QUERY = "to be"
DEFAULT_SUGGESTION_QUERY = "lif valye"


def _time_call(func: Callable[[], Any], runs: int) -> dict[str, float]:
    """Time a callable and return average/min in milliseconds."""
    durations_ms: list[float] = []
    for _ in range(runs):
        started = time.perf_counter()
        func()
        durations_ms.append((time.perf_counter() - started) * 1000.0)
    return {
        "average": statistics.mean(durations_ms),
        "min": min(durations_ms),
    }


def run_benchmark(
    mode: str = "offline",
    runs: int = BENCHMARK_RUNS,
    *,
    start_url: str = "https://quotes.toscrape.com/",
    index_path: Path = DEFAULT_INDEX_PATH,
) -> dict[str, Any]:
    """Run benchmark suite and return a structured report."""
    timings_ms: dict[str, dict[str, float] | dict[str, Any]] = {}
    pages_count = 0

    if mode == "offline":
        fixture_responses = make_pagination_fixture_chain(start_url=start_url)

        def crawl_call() -> list[Any]:
            session = FakeSession(fixture_responses)
            return crawl_quotes_site(
                start_url=start_url,
                delay_seconds=0.0,
                timeout_seconds=10.0,
                session=session,
            )

        pages: list[Any] = []

        def crawl_and_capture() -> None:
            nonlocal pages
            pages = crawl_call()

        timings_ms["crawl"] = _time_call(crawl_and_capture, runs)
        if not pages:
            pages = crawl_call()
        pages_count = len(pages)
        timings_ms["index_build"] = _time_call(lambda: build_index(pages), runs)
        index = build_index(pages)

    elif mode == "live":
        pages: list[Any] = []

        def crawl_and_capture() -> None:
            nonlocal pages
            pages = crawl_quotes_site(start_url=start_url)

        timings_ms["crawl"] = _time_call(crawl_and_capture, runs)
        if not pages:
            pages = crawl_quotes_site(start_url=start_url)
        pages_count = len(pages)
        timings_ms["index_build"] = _time_call(lambda: build_index(pages), runs)
        index = build_index(pages)

    elif mode == "existing":
        timings_ms["crawl"] = {"average": 0.0, "min": 0.0}
        timings_ms["index_build"] = {"average": 0.0, "min": 0.0}
        timings_ms["load_index"] = _time_call(lambda: load_index(index_path), runs)
        index = load_index(index_path)
        pages_count = len(index.doc_lengths)
    else:
        raise ValueError(f"Unsupported benchmark mode: {mode}")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_index_path = Path(temp_dir) / "benchmark-index.json"
        timings_ms["save_index"] = _time_call(lambda: save_index(index, temp_index_path), runs)
        timings_ms["load_index"] = _time_call(lambda: load_index(temp_index_path), runs)

    timings_ms["search_single_term"] = {
        "query": DEFAULT_SINGLE_QUERY,
        **_time_call(lambda: find_documents(index, DEFAULT_SINGLE_QUERY), runs),
    }
    timings_ms["search_multi_term"] = {
        "query": DEFAULT_MULTI_QUERY,
        **_time_call(lambda: find_documents(index, DEFAULT_MULTI_QUERY), runs),
    }
    timings_ms["phrase_search"] = {
        "query": DEFAULT_PHRASE_QUERY,
        **_time_call(lambda: find_phrase_documents(index, DEFAULT_PHRASE_QUERY), runs),
    }

    def ranked_search_call() -> None:
        candidates = find_documents(index, DEFAULT_MULTI_QUERY)
        rank_documents(index, DEFAULT_MULTI_QUERY, candidate_doc_ids=candidates)

    timings_ms["ranked_search"] = {
        "query": DEFAULT_MULTI_QUERY,
        **_time_call(ranked_search_call, runs),
    }
    timings_ms["suggestions"] = {
        "query": DEFAULT_SUGGESTION_QUERY,
        **_time_call(
            lambda: suggest_query_terms(index, DEFAULT_SUGGESTION_QUERY, max_suggestions=3),
            runs,
        ),
    }

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "mode": mode,
        "runs": runs,
        "counts": {
            "pages": pages_count,
            "documents_indexed": len(index.doc_lengths),
            "vocabulary_size": len(index.postings),
            "total_tokens": sum(index.doc_lengths.values()),
        },
        "timings_ms": timings_ms,
    }


def format_terminal_report(report: dict[str, Any]) -> str:
    """Render a readable terminal report."""
    counts = report["counts"]
    lines = [
        "Benchmark Report",
        f"Generated: {report['generated_at']}",
        f"Mode: {report['mode']}",
        f"Runs per metric: {report['runs']}",
        "",
        "Counts:",
        f"- pages: {counts['pages']}",
        f"- documents_indexed: {counts['documents_indexed']}",
        f"- vocabulary_size: {counts['vocabulary_size']}",
        f"- total_tokens: {counts['total_tokens']}",
        "",
        "Timings (ms):",
    ]

    for metric_name, metric_payload in report["timings_ms"].items():
        query_prefix = ""
        if isinstance(metric_payload, dict) and "query" in metric_payload:
            query_prefix = f" query='{metric_payload['query']}'"
        average = metric_payload["average"]
        minimum = metric_payload["min"]
        lines.append(
            f"- {metric_name}:{query_prefix} avg={average:.3f} min={minimum:.3f}"
        )

    return "\n".join(lines)


def write_json_report(report: dict[str, Any], path: Path) -> None:
    """Persist benchmark report as pretty JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run lightweight project benchmarks.")
    parser.add_argument(
        "--mode",
        choices=("offline", "existing", "live"),
        default="offline",
        help="Benchmark data source mode.",
    )
    parser.add_argument(
        "--output",
        choices=("terminal", "json", "both"),
        default="both",
        help="Output format.",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=BENCHMARK_RUNS,
        help="Number of runs per metric.",
    )
    parser.add_argument(
        "--index-path",
        type=Path,
        default=DEFAULT_INDEX_PATH,
        help="Existing index path for existing mode.",
    )
    parser.add_argument(
        "--json-path",
        type=Path,
        default=DEFAULT_JSON_REPORT_PATH,
        help="Path to write JSON benchmark report.",
    )
    return parser


def main() -> int:
    """Run benchmark script from CLI."""
    args = _build_parser().parse_args()
    if args.runs <= 0:
        print("Runs must be > 0.")
        return 1

    report = run_benchmark(
        mode=args.mode,
        runs=args.runs,
        index_path=args.index_path,
    )

    if args.output in ("terminal", "both"):
        print(format_terminal_report(report))
    if args.output in ("json", "both"):
        write_json_report(report, args.json_path)
        print(f"JSON report written to '{args.json_path}'.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
