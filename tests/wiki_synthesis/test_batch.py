"""Tests for Stage 2 synthesis batch execution."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.wiki_synthesis.batch import run_synthesis_batch, write_batch_audit_report
from src.wiki_synthesis.prompts import PromptBundle
from src.wiki_synthesis.selection import select_synthesis_candidates
from tests.wiki_synthesis.test_selection import _graph_with_candidates, _page


def test_batch_dry_run_does_not_call_provider(tmp_path: Path) -> None:
    """Dry-run batch should plan selected entries without provider calls."""
    graph = _graph_with_candidates(
        [
            _page(entity_id="topic:one", category="topic", slug="one", title="One"),
            _page(entity_id="topic:two", category="topic", slug="two", title="Two"),
        ]
    )

    report = run_synthesis_batch(
        graph,
        cache_dir=tmp_path / "cache",
        preview_dir=tmp_path / "previews",
        report_dir=tmp_path / "runs",
        provider_factory=RaisingProviderFactory(),
        model="test-model",
        limit=2,
        dry_run=True,
    )

    assert report.selected == 2
    assert report.called == 0
    assert report.written == 0
    assert report.failed == 0
    assert all(item.action == "planned" for item in report.items)
    assert not (tmp_path / "cache").exists()


def test_batch_real_run_writes_cache_preview_and_audit(tmp_path: Path) -> None:
    """Real batch runs should write cache, previews, and one audit report."""
    graph = _graph_with_candidates(
        [_page(entity_id="topic:one", category="topic", slug="one", title="One")]
    )

    report = run_synthesis_batch(
        graph,
        cache_dir=tmp_path / "cache",
        preview_dir=tmp_path / "previews",
        report_dir=tmp_path / "runs",
        provider_factory=StaticProviderFactory(_provider_payload()),
        model="test-model",
        limit=1,
        dry_run=False,
        now_fn=lambda: datetime(2026, 6, 16, 12, 0, tzinfo=UTC),
    )

    assert report.called == 1
    assert report.written == 1
    assert report.reviews == 1
    assert report.failed == 0
    assert report.audit_report_path.endswith("-batch.json")
    assert (tmp_path / "cache" / "topic" / "one.json").exists()
    assert (tmp_path / "previews" / "topic" / "one.md").exists()
    audit = json.loads(Path(report.audit_report_path).read_text(encoding="utf-8"))
    assert audit["written"] == 1
    assert audit["preview_count"] == 1


def test_batch_stops_on_first_error_by_default(tmp_path: Path) -> None:
    """Batch should stop after the first failed item unless told to continue."""
    graph = _graph_with_candidates(
        [
            _page(entity_id="topic:one", category="topic", slug="one", title="One"),
            _page(entity_id="topic:two", category="topic", slug="two", title="Two"),
        ]
    )

    report = run_synthesis_batch(
        graph,
        cache_dir=tmp_path / "cache",
        preview_dir=tmp_path / "previews",
        report_dir=tmp_path / "runs",
        provider_factory=FailingProviderFactory(),
        model="test-model",
        limit=2,
        dry_run=False,
    )

    assert report.selected == 2
    assert report.failed == 1
    assert report.attempted == 1
    assert report.called == 0
    assert len(report.items) == 1
    assert report.items[0].action == "failed"


def test_batch_failed_provider_counts_attempted_in_audit(tmp_path: Path) -> None:
    """Provider failures should count as attempted even when called stays zero."""
    graph = _graph_with_candidates(
        [_page(entity_id="topic:one", category="topic", slug="one", title="One")]
    )

    report = run_synthesis_batch(
        graph,
        cache_dir=tmp_path / "cache",
        preview_dir=tmp_path / "previews",
        report_dir=tmp_path / "runs",
        provider_factory=FailingProviderFactory(),
        model="test-model",
        limit=1,
        dry_run=False,
    )

    assert report.failed == 1
    assert report.attempted == 1
    assert report.called == 0
    audit = json.loads(Path(report.audit_report_path).read_text(encoding="utf-8"))
    assert audit["attempted"] == 1
    assert audit["called"] == 0


def test_batch_can_continue_on_error(tmp_path: Path) -> None:
    """Continue-on-error should attempt all selected items."""
    graph = _graph_with_candidates(
        [
            _page(entity_id="topic:one", category="topic", slug="one", title="One"),
            _page(entity_id="topic:two", category="topic", slug="two", title="Two"),
        ]
    )

    report = run_synthesis_batch(
        graph,
        cache_dir=tmp_path / "cache",
        preview_dir=tmp_path / "previews",
        report_dir=tmp_path / "runs",
        provider_factory=FailingProviderFactory(),
        model="test-model",
        limit=2,
        dry_run=False,
        continue_on_error=True,
    )

    assert report.selected == 2
    assert report.failed == 2
    assert report.attempted == 2
    assert report.called == 0
    assert len(report.items) == 2


def test_format_batch_text_uses_state_for_written_items() -> None:
    """Written item lines should not repeat the action label."""
    from src.wiki_synthesis.batch import BatchItemResult, BatchReport, format_batch_text

    report = BatchReport(
        dry_run=False,
        selected=1,
        attempted=1,
        called=1,
        written=1,
        failed=0,
        reviews=1,
        items=[
            BatchItemResult(
                entity_id="topic:one",
                state="new",
                action="written",
                score=90,
                cache_path="state/synthesis/topic/one.json",
                preview_path="state/synthesis_previews/topic/one.md",
            )
        ],
        failures=[],
        audit_report_path="",
        elapsed_seconds=1.0,
        remaining_changed_count=0,
        model="test-model",
        next_actions=[],
    )

    text = format_batch_text(report)

    assert "run written new topic:one state/synthesis/topic/one.json" in text
    assert "run written written" not in text


def test_batch_sleeps_between_calls_but_not_after_last(tmp_path: Path) -> None:
    """Batch should sleep between API calls only, not after the final call."""
    graph = _graph_with_candidates(
        [
            _page(entity_id="topic:one", category="topic", slug="one", title="One"),
            _page(entity_id="topic:two", category="topic", slug="two", title="Two"),
        ]
    )
    sleeps: list[float] = []

    report = run_synthesis_batch(
        graph,
        cache_dir=tmp_path / "cache",
        preview_dir=tmp_path / "previews",
        report_dir=tmp_path / "runs",
        provider_factory=StaticProviderFactory(_provider_payload()),
        model="test-model",
        limit=2,
        dry_run=False,
        between_calls=300,
        sleep_fn=sleeps.append,
        now_fn=lambda: datetime(2026, 6, 16, 12, 0, tzinfo=UTC),
    )

    assert report.called == 2
    assert sleeps == [300.0]


def test_batch_dry_run_does_not_sleep(tmp_path: Path) -> None:
    """Dry-run batch should never sleep between items."""
    graph = _graph_with_candidates(
        [
            _page(entity_id="topic:one", category="topic", slug="one", title="One"),
            _page(entity_id="topic:two", category="topic", slug="two", title="Two"),
        ]
    )
    sleeps: list[float] = []

    run_synthesis_batch(
        graph,
        cache_dir=tmp_path / "cache",
        preview_dir=tmp_path / "previews",
        report_dir=tmp_path / "runs",
        provider_factory=None,
        model="test-model",
        limit=2,
        dry_run=True,
        between_calls=300,
        sleep_fn=sleeps.append,
    )

    assert sleeps == []


def test_write_batch_audit_report_uses_batch_suffix(tmp_path: Path) -> None:
    """Batch audit reports should use the -batch.json suffix."""
    graph = _graph_with_candidates(
        [_page(entity_id="topic:one", category="topic", slug="one", title="One")]
    )
    selection = select_synthesis_candidates(graph, cache_dir=tmp_path / "cache", limit=1)
    report = run_synthesis_batch(
        graph,
        cache_dir=tmp_path / "cache",
        preview_dir=tmp_path / "previews",
        report_dir=tmp_path / "runs",
        provider_factory=StaticProviderFactory(_provider_payload()),
        model="test-model",
        limit=1,
        dry_run=False,
        write_audit=False,
        now_fn=lambda: datetime(2026, 6, 16, 12, 0, tzinfo=UTC),
    )
    path = write_batch_audit_report(
        report,
        report_dir=tmp_path / "runs",
        selection=selection,
        options={"limit": 1},
        now=datetime(2026, 7, 10, 22, 0, tzinfo=UTC),
    )

    assert path.name == "20260710T220000Z-batch.json"


class StaticProviderFactory:
    """Factory returning a static successful provider."""

    def __init__(self, payload: dict[str, Any]) -> None:
        """Store the provider payload."""
        self.payload = payload

    def __call__(self) -> StaticProvider:
        """Return a provider with the stored payload."""
        return StaticProvider(self.payload)


class FailingProviderFactory:
    """Factory returning a provider that always fails."""

    def __call__(self) -> FailingProvider:
        """Return a failing provider."""
        return FailingProvider()


class RaisingProviderFactory:
    """Factory that should never be invoked in dry-run."""

    def __call__(self) -> RaisingProvider:
        """Return a provider that fails if called."""
        return RaisingProvider()


class StaticProvider:
    """Provider returning a predefined payload."""

    def __init__(self, payload: dict[str, Any]) -> None:
        """Store the payload."""
        self.payload = payload

    def synthesize(
        self, bundle: PromptBundle, *, model: str
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Return the stored payload."""
        return self.payload, {
            "request_id": f"test-{bundle.entity_id}-{model}",
            "token_usage": {"total_tokens": 123},
        }

    def close(self) -> None:
        """No-op close hook for batch lifecycle tests."""


class FailingProvider:
    """Provider that raises on every call."""

    def synthesize(
        self, bundle: PromptBundle, *, model: str
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Raise to simulate a failed synthesis call."""
        msg = f"synthesis failed for {bundle.entity_id}"
        raise RuntimeError(msg)

    def close(self) -> None:
        """No-op close hook."""


class RaisingProvider:
    """Provider that fails if called."""

    def synthesize(
        self, bundle: PromptBundle, *, model: str
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Raise because dry-run should not invoke providers."""
        msg = f"unexpected provider call for {bundle.entity_id}"
        raise AssertionError(msg)

    def close(self) -> None:
        """No-op close hook."""


def _provider_payload() -> dict[str, Any]:
    """Return a complete provider synthesis payload."""
    return {
        "executive_synthesis": "Example synthesis.",
        "practical_example": {
            "title": "Example",
            "example": "An example workflow.",
            "why_it_helps": "It clarifies the tradeoff.",
            "basis": "illustrative",
        },
        "workflow_variants": [],
        "what_to_remember": ["Remember this."],
        "consensus": ["Shared claim."],
        "tensions": ["Open tension."],
        "evidence_quality": ["Two supporting sources."],
        "practical_takeaway": "Apply carefully.",
        "context_card": {
            "use_this_page_when": "Answering example questions.",
            "best_for_questions_about": ["example"],
            "not_enough_for": ["edge cases"],
            "strongest_sources": ["Source A"],
            "related_tags": ["ai-engineering"],
        },
    }
