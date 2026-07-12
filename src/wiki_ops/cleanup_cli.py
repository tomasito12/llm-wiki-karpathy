"""CLI for conservative temporary artifact cleanup."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from src.ingest_review.paths import repo_root
from src.wiki_ops.cleanup import (
    CLEANUP_ALLOWLIST,
    CleanupValidationError,
    build_cleanup_plan,
    execute_cleanup,
    format_cleanup_complete_text,
    format_cleanup_dry_run_text,
)
from src.wiki_paths.cli_helpers import (
    add_paths_config_argument,
    load_paths_for_cli,
    paths_with_cleanup_cli_overrides,
)
from src.wiki_paths.config import WikiPathsConfigError

LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build the wiki-cleanup argument parser."""
    parser = argparse.ArgumentParser(
        prog="wiki-cleanup",
        description="Plan or execute conservative cleanup of temporary wiki artifacts.",
    )
    add_paths_config_argument(parser)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root directory (default: detected repo root).",
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
        "--dry-run",
        action="store_true",
        help="Preview cleanup candidates without deleting files.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Execute real cleanup after validating the release manifest.",
    )
    parser.add_argument(
        "--after-release",
        default=None,
        help="Release manifest id required for real cleanup.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print cleanup plan or result as JSON.",
    )
    parser.add_argument(
        "--area",
        action="append",
        default=None,
        help="Limit cleanup to one allowed temporary area. Repeatable.",
    )
    parser.add_argument(
        "--allow-path-mismatch",
        action="store_true",
        help="Allow cleanup when release manifest paths differ from current config.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Plan or execute temporary artifact cleanup."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args(argv)
    repo = (args.repo_root or repo_root()).resolve()

    if args.yes and args.dry_run:
        LOGGER.error("Cannot combine --dry-run with --yes")
        return 2
    if args.yes and not args.after_release:
        LOGGER.error("Real cleanup requires --after-release <release_id>")
        return 2

    try:
        paths = paths_with_cleanup_cli_overrides(
            args,
            load_paths_for_cli(args, repo_root_override=repo),
        )
    except WikiPathsConfigError as exc:
        LOGGER.error("%s", exc)
        return 2

    try:
        selected_areas = _parse_selected_areas(args.area)
    except ValueError as exc:
        LOGGER.error("%s", exc)
        return 2

    dry_run = not args.yes
    plan = build_cleanup_plan(
        paths,
        dry_run=dry_run,
        after_release=args.after_release,
        selected_areas=selected_areas,
        allow_path_mismatch=args.allow_path_mismatch,
    )

    if args.yes:
        if plan.blocked:
            for reason in plan.blocked_reasons:
                LOGGER.error("%s", reason)
            return 2
        try:
            result = execute_cleanup(
                plan,
                paths,
                allow_path_mismatch=args.allow_path_mismatch,
            )
        except CleanupValidationError as exc:
            for reason in exc.reasons:
                LOGGER.error("%s", reason)
            return 2
        if args.json:
            print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
        else:
            print(
                format_cleanup_complete_text(
                    result,
                    after_release=args.after_release,
                )
            )
        if result.partial:
            LOGGER.error("Cleanup stopped before all candidates were deleted.")
            return 2
        LOGGER.info("wiki-cleanup complete")
        return 0

    if args.json:
        print(json.dumps(plan.to_dict(), indent=2, sort_keys=True))
    else:
        print(format_cleanup_dry_run_text(plan))
    LOGGER.info("wiki-cleanup dry-run complete")
    return 0


def _parse_selected_areas(values: list[str] | None) -> frozenset[str] | None:
    """Validate optional repeatable ``--area`` values."""
    if not values:
        return None
    selected = frozenset(values)
    unknown = selected - CLEANUP_ALLOWLIST
    if unknown:
        unknown_list = ", ".join(sorted(unknown))
        msg = f"Unknown or non-allowed cleanup area(s): {unknown_list}"
        raise ValueError(msg)
    return selected


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
