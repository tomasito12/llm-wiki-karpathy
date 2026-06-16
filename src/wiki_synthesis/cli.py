"""CLI for Stage 2 synthesis planning."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from src.ingest_review.paths import repo_root
from src.wiki_synthesis.models import SynthesisPlan
from src.wiki_synthesis.planner import load_graph_export, plan_from_graph

LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build the wiki-synthesis-plan argument parser."""
    root = repo_root()
    parser = argparse.ArgumentParser(
        prog="wiki-synthesis-plan",
        description="Plan Stage 2 synthesis work without making LLM calls.",
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


def main() -> int:
    """Plan Stage 2 synthesis work."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args()
    graph = load_graph_export(args.graph_path.resolve())
    plan = plan_from_graph(
        graph,
        cache_dir=args.cache_dir.resolve(),
        category=args.category,
        entity=args.entity,
        include_single_source=args.include_single_source,
        changed_only=args.changed_only,
        limit=args.limit,
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
        f"skipped_evidence_object={summary.skipped_evidence_object}"
    )
    for entry in plan.entries:
        print(
            f"{entry.state}\t{entry.entity_id}\t"
            f"sources={entry.source_count}\tevidence={entry.evidence_count}\t{entry.title}"
        )


if __name__ == "__main__":
    raise SystemExit(main())
