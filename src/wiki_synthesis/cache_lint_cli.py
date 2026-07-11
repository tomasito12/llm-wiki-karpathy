"""CLI for linting Stage 2 synthesis cache entries."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from src.wiki_paths.cli_helpers import (
    add_paths_config_argument,
    load_paths_for_cli,
    resolve_cli_path,
)
from src.wiki_paths.config import WikiPathsConfigError
from src.wiki_synthesis.cache_lint import CacheLintReport, lint_synthesis_cache
from src.wiki_synthesis.planner import load_graph_export

LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build the wiki-synthesis-cache-lint argument parser."""
    parser = argparse.ArgumentParser(
        prog="wiki-synthesis-cache-lint",
        description="Validate Stage 2 synthesis cache entries against the current graph.",
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
        help="Only lint one graph category, for example topic, glossary, trend, or how_to.",
    )
    parser.add_argument(
        "--entity",
        default=None,
        help="Only lint one entity id, for example glossary:fine-tuning.",
    )
    parser.add_argument(
        "--include-missing",
        action="store_true",
        help="Report missing cache entries for matching graph pages as errors.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the lint report as JSON.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Lint Stage 2 synthesis cache entries."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args(argv)
    try:
        paths = load_paths_for_cli(args)
    except WikiPathsConfigError as exc:
        LOGGER.error("%s", exc)
        return 2
    graph_path = resolve_cli_path(args.graph_path, configured=paths.graph_path)
    cache_dir = resolve_cli_path(args.cache_dir, configured=paths.synthesis_dir)
    graph = load_graph_export(graph_path)
    report = lint_synthesis_cache(
        graph,
        cache_dir=cache_dir,
        category=args.category,
        entity=args.entity,
        include_missing=args.include_missing,
    )
    if args.json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    else:
        _print_text_report(report)
    LOGGER.info(
        "wiki-synthesis-cache-lint complete checked=%d ok=%d warnings=%d errors=%d",
        report.checked,
        report.ok,
        report.warnings,
        report.errors,
    )
    return report.exit_code


def _print_text_report(report: CacheLintReport) -> None:
    """Print a human-readable lint report."""
    print(
        "wiki-synthesis-cache-lint "
        f"checked={report.checked} ok={report.ok} "
        f"warnings={report.warnings} errors={report.errors}"
    )
    for item in report.items:
        print(
            f"{item.severity}\t{item.state}\t{item.entity_id}\t"
            f"{item.current_input_hash}\t{item.cache_path}\t{item.reason}"
        )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
