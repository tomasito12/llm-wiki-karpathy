"""Export finished ingest review artifacts into one JSON bundle."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from src.ingest_review.artifact import load_artifact
from src.ingest_review.paths import repo_root
from src.ingest_review.review_queue_status import status_from_artifact
from src.pipeline.atomic import atomic_write_json

ReviewExportScope = Literal["finished", "all"]


def load_review_artifacts(
    reviews_root: Path,
    *,
    scope: ReviewExportScope = "finished",
) -> list[dict[str, Any]]:
    """Return review artifacts sorted by ``review_finished_at`` then title.

    Args:
        reviews_root: Directory containing ``<source_id>/review.json`` files.
        scope: ``finished`` keeps only completed reviews; ``all`` includes every artifact.
    """
    if not reviews_root.is_dir():
        return []

    artifacts: list[dict[str, Any]] = []
    for path in sorted(reviews_root.glob("*/review.json")):
        artifact = load_artifact(path)
        if not artifact:
            continue
        if scope == "finished" and status_from_artifact(artifact) != "finished":
            continue
        artifacts.append(artifact)

    def sort_key(artifact: dict[str, Any]) -> tuple[str, str]:
        analytics = artifact.get("review_analytics") or {}
        finished_at = str(analytics.get("review_finished_at") or "")
        source = artifact.get("source") or {}
        title = str(source.get("title") or "").lower()
        return (finished_at, title)

    artifacts.sort(key=sort_key)
    return artifacts


def build_finished_reviews_bundle(
    reviews_root: Path,
    *,
    scope: ReviewExportScope = "finished",
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    """Build one JSON object containing every selected review artifact."""
    artifacts = load_review_artifacts(reviews_root, scope=scope)
    when = generated_at or datetime.now(tz=UTC)
    return {
        "generated_at": when.replace(microsecond=0).isoformat(),
        "reviews_root": reviews_root.as_posix(),
        "scope": scope,
        "count": len(artifacts),
        "reviews": artifacts,
    }


def write_finished_reviews_bundle(
    output_path: Path,
    *,
    reviews_root: Path,
    scope: ReviewExportScope = "finished",
) -> Path:
    """Write the consolidated review JSON bundle to *output_path*."""
    payload = build_finished_reviews_bundle(reviews_root, scope=scope)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(output_path, payload)
    return output_path


def build_parser() -> argparse.ArgumentParser:
    """Construct CLI parser for finished review JSON export."""
    root = repo_root()
    parser = argparse.ArgumentParser(
        prog="review-summary",
        description="Export ingest review.json artifacts into one JSON bundle.",
    )
    parser.add_argument(
        "--reviews-root",
        type=Path,
        default=root / "state" / "reviews",
        help="Directory containing per-source review.json artifacts.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=root / "state" / "reviews" / "finished-reviews.json",
        help="JSON file to write.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Include in-progress and not-started reviews, not only finished ones.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    args = build_parser().parse_args(argv)
    scope: ReviewExportScope = "all" if args.all else "finished"
    path = write_finished_reviews_bundle(
        args.output,
        reviews_root=args.reviews_root,
        scope=scope,
    )
    count = len(load_review_artifacts(args.reviews_root, scope=scope))
    print(f"Wrote {count} review(s) to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
