"""High-level Stage 2 synthesis workflow orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.pipeline.atomic import atomic_write_json
from src.wiki_synthesis.executor import SynthesisProvider, SynthesisRunReport, run_synthesis
from src.wiki_synthesis.review import SynthesisReviewPreview, build_review_preview


@dataclass(frozen=True)
class SynthesisWorkflowReport:
    """Combined report for synthesis run plus optional review previews."""

    run: SynthesisRunReport
    reviews: list[SynthesisReviewPreview]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable workflow report."""
        return {
            "run": self.run.to_dict(),
            "reviews": [review.to_dict() for review in self.reviews],
        }


def run_synthesis_workflow(
    graph: dict[str, Any],
    *,
    cache_dir: Path,
    preview_dir: Path,
    provider: SynthesisProvider,
    model: str,
    category: str | None = None,
    entity: str | None = None,
    include_single_source: bool = False,
    limit: int = 1,
    dry_run: bool = True,
    review: bool = True,
    finished_source_ids: set[str] | None = None,
) -> SynthesisWorkflowReport:
    """Run the controlled synthesis workflow and optionally render previews."""
    run_report = run_synthesis(
        graph,
        cache_dir=cache_dir,
        provider=provider,
        model=model,
        category=category,
        entity=entity,
        include_single_source=include_single_source,
        limit=limit,
        dry_run=dry_run,
        finished_source_ids=finished_source_ids,
    )
    reviews: list[SynthesisReviewPreview] = []
    if review and not dry_run:
        for item in run_report.items:
            if item.action != "written":
                continue
            review_report, _rendered = build_review_preview(
                graph,
                entity_id=item.entity_id,
                cache_dir=cache_dir,
                preview_dir=preview_dir,
                dry_run=False,
            )
            reviews.append(review_report)
    return SynthesisWorkflowReport(run=run_report, reviews=reviews)


def write_workflow_audit_report(
    report: SynthesisWorkflowReport,
    *,
    report_dir: Path,
    options: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> Path:
    """Write a timestamped audit report for a real synthesis workflow run."""
    timestamp = _timestamp(now or datetime.now(UTC))
    path = report_dir / f"{timestamp}.json"
    payload = {
        "created_at": timestamp,
        "options": options or {},
        **report.to_dict(),
    }
    atomic_write_json(path, payload)
    return path


def _timestamp(value: datetime) -> str:
    """Return a filesystem-safe UTC timestamp."""
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).replace(microsecond=0).strftime("%Y%m%dT%H%M%SZ")
