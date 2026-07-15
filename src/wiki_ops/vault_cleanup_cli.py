"""CLI for conservative vault orphan and duplicate cleanup."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from src.ingest_review.paths import repo_root
from src.wiki_ops.vault_cleanup import (
    REAL_VAULT_CLEANUP_REQUIREMENT,
    VaultCleanupValidationError,
    build_vault_cleanup_plan,
    execute_vault_cleanup,
    format_vault_cleanup_complete_text,
    format_vault_cleanup_dry_run_text,
)
from src.wiki_paths.cli_helpers import (
    add_paths_config_argument,
    load_paths_for_cli,
)
from src.wiki_paths.config import WikiPathsConfigError

LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build the wiki-vault-cleanup argument parser."""
    parser = argparse.ArgumentParser(
        prog="wiki-vault-cleanup",
        description=(
            "Plan or execute cleanup of stale vault orphans and exact duplicate markdown files."
        ),
    )
    add_paths_config_argument(parser)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root directory (default: detected repo root).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview vault cleanup candidates without deleting files.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Execute real vault cleanup after validating the release manifest.",
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
        "--allow-path-mismatch",
        action="store_true",
        help="Allow cleanup when release manifest paths differ from current config.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Plan or execute vault orphan and duplicate cleanup."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args(argv)
    repo = (args.repo_root or repo_root()).resolve()

    if args.yes and args.dry_run:
        LOGGER.error("Cannot combine --dry-run with --yes")
        return 2
    if args.yes and not args.after_release:
        LOGGER.error("%s", REAL_VAULT_CLEANUP_REQUIREMENT)
        return 2

    try:
        paths = load_paths_for_cli(args, repo_root_override=repo)
    except WikiPathsConfigError as exc:
        LOGGER.error("%s", exc)
        return 2

    dry_run = not args.yes
    plan = build_vault_cleanup_plan(
        paths,
        repo_root=repo,
        dry_run=dry_run,
        after_release=args.after_release,
        allow_path_mismatch=args.allow_path_mismatch,
    )

    if args.yes:
        if plan.blocked:
            for reason in plan.blocked_reasons:
                LOGGER.error("%s", reason)
            return 2
        try:
            result = execute_vault_cleanup(
                plan,
                paths,
                repo_root=repo,
                allow_path_mismatch=args.allow_path_mismatch,
            )
        except VaultCleanupValidationError as exc:
            for reason in exc.reasons:
                LOGGER.error("%s", reason)
            return 2
        if args.json:
            print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
        else:
            print(
                format_vault_cleanup_complete_text(
                    result,
                    after_release=args.after_release,
                )
            )
        LOGGER.info("wiki-vault-cleanup complete")
        return 0

    if args.json:
        print(json.dumps(plan.to_dict(), indent=2, sort_keys=True))
    else:
        print(format_vault_cleanup_dry_run_text(plan))
    LOGGER.info("wiki-vault-cleanup dry-run complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
