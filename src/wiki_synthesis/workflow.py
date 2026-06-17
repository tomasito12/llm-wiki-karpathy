"""High-level Stage 2 synthesis workflow orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

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
