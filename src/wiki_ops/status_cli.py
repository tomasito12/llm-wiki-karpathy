"""CLI for read-only wiki operations status."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from src.ingest_review.paths import repo_root
from src.wiki_ops.status import (
    OpsStatusConfig,
    collect_ops_status,
    default_config,
    format_text_report,
)

LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build the wiki-ops-status argument parser."""
    parser = argparse.ArgumentParser(
        prog="wiki-ops-status",
        description="Summarize wiki source, review, render, synthesis, and artifact state.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root directory (default: detected repo root).",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=None,
        help="Directory containing Readwise raw exports.",
    )
    parser.add_argument(
        "--reviews-dir",
        type=Path,
        default=None,
        help="Directory containing review artifacts.",
    )
    parser.add_argument(
        "--wiki-dir",
        type=Path,
        default=None,
        help="Generated Obsidian wiki directory.",
    )
    parser.add_argument(
        "--graph-path",
        type=Path,
        default=None,
        help="Path to the wiki-render graph export.",
    )
    parser.add_argument(
        "--manifest-path",
        type=Path,
        default=None,
        help="Path to the wiki-render manifest.",
    )
    parser.add_argument(
        "--synthesis-cache-dir",
        type=Path,
        default=None,
        help="Directory containing Stage 2 synthesis cache entries.",
    )
    parser.add_argument(
        "--preview-dir",
        type=Path,
        default=None,
        help="Directory containing synthesis preview markdown files.",
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        default=None,
        help="Directory containing synthesis run audit reports.",
    )
    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=None,
        help="Directory containing synthesis backup artifacts.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the status report as JSON.",
    )
    return parser


def config_from_args(args: argparse.Namespace) -> OpsStatusConfig:
    """Build status config from parsed CLI arguments."""
    repo = (args.repo_root or repo_root()).resolve()
    defaults = default_config(repo)
    return OpsStatusConfig(
        repo_root=repo,
        raw_dir=_resolve_path_arg(args.raw_dir, defaults.raw_dir),
        reviews_dir=_resolve_path_arg(args.reviews_dir, defaults.reviews_dir),
        wiki_dir=_resolve_path_arg(args.wiki_dir, defaults.wiki_dir),
        graph_path=_resolve_path_arg(args.graph_path, defaults.graph_path),
        manifest_path=_resolve_path_arg(args.manifest_path, defaults.manifest_path),
        synthesis_cache_dir=_resolve_path_arg(
            args.synthesis_cache_dir,
            defaults.synthesis_cache_dir,
        ),
        preview_dir=_resolve_path_arg(args.preview_dir, defaults.preview_dir),
        run_dir=_resolve_path_arg(args.run_dir, defaults.run_dir),
        backup_dir=_resolve_path_arg(args.backup_dir, defaults.backup_dir),
    )


def _resolve_path_arg(explicit: Path | None, default: Path) -> Path:
    """Return an explicit CLI path or the default derived from repo root."""
    return explicit.resolve() if explicit is not None else default.resolve()


def main(argv: list[str] | None = None) -> int:
    """Collect and print wiki operations status."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args(argv)
    config = config_from_args(args)
    status = collect_ops_status(config)
    if args.json:
        print(json.dumps(status.to_dict(), indent=2, sort_keys=True))
    else:
        print(format_text_report(status))
    LOGGER.info("wiki-ops-status complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
