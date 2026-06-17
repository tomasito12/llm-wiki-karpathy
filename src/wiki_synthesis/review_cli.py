"""CLI for reviewing Stage 2 synthesis cache output before wiki-render."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from src.ingest_review.paths import repo_root
from src.wiki_synthesis.planner import load_graph_export
from src.wiki_synthesis.review import SynthesisReviewPreview, build_review_preview

LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build the wiki-synthesis-review argument parser."""
    root = repo_root()
    parser = argparse.ArgumentParser(
        prog="wiki-synthesis-review",
        description="Render a local preview for one Stage 2 synthesis cache entry.",
    )
    parser.add_argument(
        "--graph-path",
        type=Path,
        default=root / "state" / "wiki_render_graph.json",
        help="Path to the wiki-render graph export.",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=root / "state" / "synthesis",
        help="Directory containing Stage 2 synthesis cache entries.",
    )
    parser.add_argument(
        "--preview-dir",
        type=Path,
        default=root / "state" / "synthesis_previews",
        help="Directory for rendered markdown previews.",
    )
    parser.add_argument(
        "--entity",
        required=True,
        help="Entity id to review, for example glossary:fine-tuning.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Render and report without writing the preview file.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the review report as JSON.",
    )
    return parser


def main() -> int:
    """Render a Stage 2 synthesis review preview."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args()
    graph = load_graph_export(args.graph_path.resolve())
    report, _rendered = build_review_preview(
        graph,
        entity_id=args.entity,
        cache_dir=args.cache_dir.resolve(),
        preview_dir=args.preview_dir.resolve(),
        dry_run=args.dry_run,
    )
    if args.json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    else:
        _print_text_report(report)
    LOGGER.info(
        "wiki-synthesis-review complete entity=%s state=%s preview=%s dry_run=%s",
        report.entity_id,
        report.validation_state,
        report.preview_path,
        args.dry_run,
    )
    return 0


def _print_text_report(report: SynthesisReviewPreview) -> None:
    """Print a human-readable review report."""
    print(
        "wiki-synthesis-review "
        f"entity={report.entity_id} validation={report.validation_state} "
        f"rendered={report.rendered_synthesis_state}"
    )
    print(f"target_path\t{report.target_path}")
    print(f"cache_path\t{report.cache_path}")
    print(f"preview_path\t{report.preview_path}")
    print(f"current_input_hash\t{report.current_input_hash}")
    print(f"cached_input_hash\t{report.cached_input_hash or 'none'}")
    print(f"reason\t{report.validation_reason}")


if __name__ == "__main__":
    raise SystemExit(main())
