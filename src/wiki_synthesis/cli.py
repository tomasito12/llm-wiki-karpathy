"""CLI for Stage 2 synthesis planning."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from src.ingest_review.review_scope import finished_source_ids
from src.wiki_paths.cli_helpers import (
    add_paths_config_argument,
    load_paths_for_cli,
    resolve_cli_path,
)
from src.wiki_paths.config import WikiPathsConfigError
from src.wiki_synthesis.models import SynthesisPlan
from src.wiki_synthesis.planner import load_graph_export, plan_from_graph

LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build the wiki-synthesis-plan argument parser."""
    parser = argparse.ArgumentParser(
        prog="wiki-synthesis-plan",
        description="Plan Stage 2 synthesis work without making LLM calls.",
    )
    add_paths_config_argument(parser)
    parser.add_argument(
        "--graph-path",
        type=Path,
        default=None,
        help="Path to the wiki-render graph export.",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=None,
        help="Directory containing Stage 2 synthesis cache entries.",
    )
    parser.add_argument(
        "--category",
        default=None,
        help="Only plan one graph category, for example topic, trend, how_to, or tool.",
    )
    parser.add_argument(
        "--entity",
        default=None,
        help="Only plan one entity id, for example topic:agentic-coding-workflows.",
    )
    parser.add_argument(
        "--include-single-source",
        action="store_true",
        help="Include single-source knowledge pages in synthesis planning.",
    )
    parser.add_argument(
        "--changed-only",
        action="store_true",
        help="Show only entries that would need synthesis work.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit displayed plan entries after filtering.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON instead of a text summary.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Plan Stage 2 synthesis work."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args(argv)
    try:
        paths = load_paths_for_cli(args)
    except WikiPathsConfigError as exc:
        LOGGER.error("%s", exc)
        return 2
    graph_path = resolve_cli_path(args.graph_path, configured=paths.graph_path)
    cache_dir = resolve_cli_path(args.cache_dir, configured=paths.synthesis_dir)
    reviews_dir = resolve_cli_path(None, configured=paths.reviews_dir)
    graph = load_graph_export(graph_path)
    plan = plan_from_graph(
        graph,
        cache_dir=cache_dir,
        category=args.category,
        entity=args.entity,
        include_single_source=args.include_single_source,
        changed_only=args.changed_only,
        limit=args.limit,
        finished_source_ids=finished_source_ids(reviews_dir),
    )
    if args.json:
        print(json.dumps(plan.to_dict(), indent=2, sort_keys=True))
    else:
        _print_text_plan(plan)
    return 0


def _print_text_plan(plan: SynthesisPlan) -> None:
    """Print a human-readable synthesis plan."""
    summary = plan.summary
    print(
        "wiki-synthesis-plan "
        f"total={summary.total} shown={summary.shown} "
        f"new={summary.new} stale={summary.stale} unchanged={summary.unchanged} "
        f"skipped_single_source={summary.skipped_single_source} "
        f"skipped_in_progress_source={summary.skipped_in_progress_source} "
        f"skipped_evidence_object={summary.skipped_evidence_object}"
    )
    for entry in plan.entries:
        print(
            f"{entry.state}\t{entry.entity_id}\t"
            f"sources={entry.source_count}\tevidence={entry.evidence_count}\t{entry.title}"
        )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
