"""Tests for Stage 12 benchmark helpers."""

from __future__ import annotations

import json
from pathlib import Path

from scripts import benchmark
from scripts.benchmark_fixtures import FakeSession


def test_run_benchmark_report_structure_offline() -> None:
    """Offline benchmark should return expected report keys."""
    report = benchmark.run_benchmark(mode="offline", runs=1)

    assert set(report.keys()) == {"generated_at", "mode", "runs", "counts", "timings_ms"}
    assert report["mode"] == "offline"
    assert report["runs"] == 1
    assert set(report["counts"].keys()) == {
        "pages",
        "documents_indexed",
        "vocabulary_size",
        "total_tokens",
    }
    assert set(report["timings_ms"].keys()) == {
        "crawl",
        "index_build",
        "save_index",
        "load_index",
        "search_single_term",
        "search_multi_term",
        "phrase_search",
        "ranked_search",
        "suggestions",
    }


def test_offline_mode_uses_fake_session_only(
    monkeypatch,
) -> None:
    """Offline mode should inject FakeSession and zero delay."""

    def fake_crawl(
        start_url: str = "https://quotes.toscrape.com/",
        delay_seconds: float = 6.0,
        timeout_seconds: float = 10.0,
        session: object | None = None,
    ) -> list[object]:
        assert start_url == "https://quotes.toscrape.com/"
        assert delay_seconds == 0.0
        assert timeout_seconds == 10.0
        assert isinstance(session, FakeSession)
        return []

    monkeypatch.setattr(benchmark, "crawl_quotes_site", fake_crawl)

    report = benchmark.run_benchmark(mode="offline", runs=1)
    assert report["counts"]["pages"] == 0


def test_write_json_report(tmp_path: Path) -> None:
    """JSON report writer should create parseable benchmark output."""
    report = benchmark.run_benchmark(mode="offline", runs=1)
    output_path = tmp_path / "bench.json"

    benchmark.write_json_report(report, output_path)

    assert output_path.exists()
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded["mode"] == "offline"
    assert "timings_ms" in loaded


def test_format_terminal_report_contains_sections() -> None:
    """Terminal formatter should include count and timing sections."""
    report = benchmark.run_benchmark(mode="offline", runs=1)

    formatted = benchmark.format_terminal_report(report)

    assert "Benchmark Report" in formatted
    assert "Counts:" in formatted
    assert "Timings (ms):" in formatted
    assert "search_single_term" in formatted
    assert "phrase_search" in formatted
