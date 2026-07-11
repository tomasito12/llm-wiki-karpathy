"""Controlled batch execution for ranked Stage 2 synthesis candidates."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

from src.pipeline.atomic import atomic_write_json
from src.wiki_synthesis.executor import SynthesisProvider, run_synthesis
from src.wiki_synthesis.review import build_review_preview
from src.wiki_synthesis.selection import (
    SelectedEntry,
    count_changed_candidates,
    select_synthesis_candidates,
)

DEFAULT_BATCH_LIMIT = 5
NEXT_ACTIONS = (
    "hatch run wiki-synthesis-cache-lint",
    "hatch run wiki-render --dry-run",
)


class ProviderFactory(Protocol):
    """Factory that creates one synthesis provider per batch item."""

    def __call__(self) -> SynthesisProvider:
        """Return a fresh provider instance."""


@dataclass(frozen=True)
class BatchItemResult:
    """One batch item outcome."""

    entity_id: str
    state: str
    action: str
    score: int
    cache_path: str
    preview_path: str
    error: str = ""
    token_usage: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable batch item."""
        return asdict(self)


@dataclass(frozen=True)
class BatchReport:
    """Summary of one synthesis batch run."""

    dry_run: bool
    selected: int
    attempted: int
    called: int
    written: int
    failed: int
    reviews: int
    items: list[BatchItemResult]
    failures: list[dict[str, Any]]
    audit_report_path: str
    elapsed_seconds: float
    remaining_changed_count: int | None
    model: str
    next_actions: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable batch report."""
        return {
            "dry_run": self.dry_run,
            "selected": self.selected,
            "attempted": self.attempted,
            "called": self.called,
            "written": self.written,
            "failed": self.failed,
            "reviews": self.reviews,
            "audit_report_path": self.audit_report_path,
            "items": [item.to_dict() for item in self.items],
            "failures": self.failures,
            "remaining_changed_count": self.remaining_changed_count,
            "model": self.model,
            "next_actions": self.next_actions,
        }


def run_synthesis_batch(
    graph: dict[str, Any],
    *,
    cache_dir: Path,
    preview_dir: Path,
    report_dir: Path,
    provider_factory: ProviderFactory | None,
    model: str,
    category: str | None = None,
    entity: str | None = None,
    include_single_source: bool = False,
    limit: int = DEFAULT_BATCH_LIMIT,
    dry_run: bool = True,
    between_calls: float = 0,
    continue_on_error: bool = False,
    write_audit: bool = True,
    sleep_fn: Callable[[float], None] = time.sleep,
    progress_fn: Callable[[str], None] | None = None,
    now_fn: Callable[[], datetime] | None = None,
) -> BatchReport:
    """Execute a bounded batch of ranked synthesis candidates."""
    started = time.monotonic()
    selection = select_synthesis_candidates(
        graph,
        cache_dir=cache_dir,
        category=category,
        entity=entity,
        include_single_source=include_single_source,
        limit=limit,
    )
    items: list[BatchItemResult] = []
    failures: list[dict[str, Any]] = []
    attempted = 0
    called = 0
    written = 0
    failed = 0
    reviews = 0

    for index, selected in enumerate(selection.entries):
        if dry_run:
            items.append(_planned_item(selected))
            continue
        if provider_factory is None:
            msg = "provider_factory is required for real batch runs"
            raise ValueError(msg)
        provider = provider_factory()
        provider_reached = False
        try:
            run_report = run_synthesis(
                graph,
                cache_dir=cache_dir,
                provider=provider,
                model=model,
                entity=selected.entity_id,
                include_single_source=include_single_source,
                limit=1,
                dry_run=False,
                now_fn=now_fn,
            )
            if run_report.called > 0:
                provider_reached = True
                attempted += 1
                called += 1
            if run_report.called == 0 or run_report.written == 0:
                error = "entity is not executable or synthesis produced no cache write"
                if run_report.items:
                    error = run_report.items[0].reason or error
                failed += 1
                failures.append(_failure_record(selected, error))
                items.append(_failed_item(selected, error))
                if not continue_on_error:
                    break
                continue
            written += 1
            run_item = run_report.items[0]
            review_report, _rendered = build_review_preview(
                graph,
                entity_id=selected.entity_id,
                cache_dir=cache_dir,
                preview_dir=preview_dir,
                dry_run=False,
            )
            reviews += 1
            items.append(
                BatchItemResult(
                    entity_id=selected.entity_id,
                    state=selected.state,
                    action="written",
                    score=selected.score,
                    cache_path=run_item.cache_path,
                    preview_path=review_report.preview_path,
                    token_usage=run_item.token_usage,
                )
            )
        except Exception as exc:
            if not provider_reached:
                attempted += 1
                provider_reached = True
            if "Provider returned invalid synthesis cache" in str(exc):
                called += 1
            failed += 1
            error = str(exc)
            failures.append(_failure_record(selected, error))
            items.append(_failed_item(selected, error))
            if not continue_on_error:
                break
        finally:
            _close_provider(provider)
        if provider_reached and between_calls > 0 and index < len(selection.entries) - 1:
            _emit_progress(
                progress_fn,
                f"waiting {selected.entity_id} index={index + 1} "
                f"total={len(selection.entries)} seconds={between_calls}",
            )
            sleep_fn(between_calls)

    remaining_changed_count = count_changed_candidates(
        graph,
        cache_dir=cache_dir,
        category=category,
        entity=entity,
        include_single_source=include_single_source,
    )
    report = BatchReport(
        dry_run=dry_run,
        selected=len(selection.entries),
        attempted=attempted,
        called=called,
        written=written,
        failed=failed,
        reviews=reviews,
        items=items,
        failures=failures,
        audit_report_path="",
        elapsed_seconds=round(time.monotonic() - started, 3),
        remaining_changed_count=remaining_changed_count,
        model=model,
        next_actions=list(NEXT_ACTIONS),
    )
    if not dry_run and write_audit:
        audit_path = write_batch_audit_report(
            report,
            report_dir=report_dir,
            selection=selection,
            options={
                "category": category,
                "entity": entity,
                "limit": limit,
                "include_single_source": include_single_source,
                "between_calls": between_calls,
                "continue_on_error": continue_on_error,
            },
        )
        report = BatchReport(
            dry_run=report.dry_run,
            selected=report.selected,
            attempted=report.attempted,
            called=report.called,
            written=report.written,
            failed=report.failed,
            reviews=report.reviews,
            items=report.items,
            failures=report.failures,
            audit_report_path=str(audit_path),
            elapsed_seconds=report.elapsed_seconds,
            remaining_changed_count=report.remaining_changed_count,
            model=report.model,
            next_actions=report.next_actions,
        )
    return report


def write_batch_audit_report(
    report: BatchReport,
    *,
    report_dir: Path,
    selection: Any,
    options: dict[str, Any],
    now: datetime | None = None,
) -> Path:
    """Write a timestamped batch audit report."""
    timestamp = _timestamp(now or datetime.now(UTC))
    path = report_dir / f"{timestamp}-batch.json"
    payload = {
        "created_at": timestamp,
        "options": options,
        "selected_entries": [entry.to_dict() for entry in selection.entries],
        "completed_entries": [item.to_dict() for item in report.items if item.action == "written"],
        "failed_entries": report.failures,
        "skipped_entries": [item.to_dict() for item in report.items if item.action == "planned"],
        "attempted": report.attempted,
        "called": report.called,
        "written": report.written,
        "preview_count": report.reviews,
        "dry_run": report.dry_run,
        "elapsed_seconds": report.elapsed_seconds,
        "remaining_changed_count": report.remaining_changed_count,
        "model": report.model,
        "items": [item.to_dict() for item in report.items],
        "failures": report.failures,
    }
    atomic_write_json(path, payload)
    return path


def format_batch_text(report: BatchReport) -> str:
    """Render a human-readable batch report."""
    lines = [
        "wiki-synthesis-batch "
        f"selected={report.selected} attempted={report.attempted} "
        f"called={report.called} written={report.written} "
        f"failed={report.failed} dry_run={report.dry_run}",
    ]
    for item in report.items:
        if report.dry_run:
            lines.append(f"planned {item.entity_id} score={item.score}")
        elif item.action == "written":
            lines.append(f"run written {item.state} {item.entity_id} {item.cache_path}")
        else:
            lines.append(f"run failed {item.entity_id} {item.error}")
    if report.audit_report_path:
        lines.append(f"audit_report {report.audit_report_path}")
    for action in report.next_actions:
        lines.append(f"next {action}")
    return "\n".join(lines)


def _planned_item(selected: SelectedEntry) -> BatchItemResult:
    """Return a dry-run batch item."""
    return BatchItemResult(
        entity_id=selected.entity_id,
        state=selected.state,
        action="planned",
        score=selected.score,
        cache_path="",
        preview_path="",
    )


def _failed_item(selected: SelectedEntry, error: str) -> BatchItemResult:
    """Return a failed batch item."""
    return BatchItemResult(
        entity_id=selected.entity_id,
        state=selected.state,
        action="failed",
        score=selected.score,
        cache_path="",
        preview_path="",
        error=error,
    )


def _failure_record(selected: SelectedEntry, error: str) -> dict[str, Any]:
    """Return one failure record for audit output."""
    return {
        "entity_id": selected.entity_id,
        "state": selected.state,
        "score": selected.score,
        "error": error,
    }


def _close_provider(provider: SynthesisProvider) -> None:
    """Close a provider when it exposes a close hook."""
    close = getattr(provider, "close", None)
    if callable(close):
        close()


def _emit_progress(progress_fn: Callable[[str], None] | None, message: str) -> None:
    """Emit one progress line when a callback is configured."""
    if progress_fn is not None:
        progress_fn(message)


def _timestamp(value: datetime) -> str:
    """Return a filesystem-safe UTC timestamp."""
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).replace(microsecond=0).strftime("%Y%m%dT%H%M%SZ")
