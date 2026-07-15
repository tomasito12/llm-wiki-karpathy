"""CLI for wiki schema/link validation."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from src.readwise.sync import _repo_root
from src.wiki_lint.validator import validate_wiki
from src.wiki_lint.vault_hygiene import collect_vault_hygiene_status, format_vault_hygiene_text
from src.wiki_paths.cli_helpers import (
    add_paths_config_argument,
    load_paths_for_cli,
    resolve_cli_path,
)
from src.wiki_paths.config import WikiPathsConfigError

LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build the wiki-lint parser."""
    parser = argparse.ArgumentParser(
        prog="wiki-lint",
        description="Validate generated wiki markdown against shared wiki_contract rules.",
    )
    add_paths_config_argument(parser)
    parser.add_argument(
        "--wiki-dir",
        type=Path,
        default=None,
        help="Wiki root directory (default: configured wiki_dir, or <repo>/wiki).",
    )
    parser.add_argument(
        "--include-non-managed",
        action="store_true",
        help="Also lint preserved/manual paths outside managed folders.",
    )
    parser.add_argument(
        "--skip-hygiene",
        action="store_true",
        help="Skip vault hygiene checks against the render manifest.",
    )
    parser.add_argument(
        "--hygiene-only",
        action="store_true",
        help="Run vault hygiene checks only; skip wiki_contract validation.",
    )
    parser.add_argument(
        "--hygiene-json",
        action="store_true",
        help="Print vault hygiene findings as JSON.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run wiki validation and print findings."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args(argv)
    repo = _repo_root().resolve()
    try:
        paths = load_paths_for_cli(args, repo_root_override=repo)
    except WikiPathsConfigError as exc:
        LOGGER.error("%s", exc)
        return 2
    wiki_dir = resolve_cli_path(args.wiki_dir, configured=paths.wiki_dir)
    exit_code = 0

    if not args.hygiene_only:
        issues = validate_wiki(wiki_dir, include_non_managed=args.include_non_managed)
        if issues:
            exit_code = 1
            print(f"wiki-lint: {len(issues)} contract issue(s)")
            for issue in issues:
                print(f"{issue.path}: {issue.message}")
        else:
            print(f"wiki-lint: contract ok ({wiki_dir})")

    if args.skip_hygiene:
        return exit_code

    hygiene_status, hygiene_warnings = collect_vault_hygiene_status(
        wiki_dir=wiki_dir,
        manifest_path=paths.manifest_path,
        reviews_dir=paths.reviews_dir,
        raw_dir=paths.raw_dir,
        repo_root=repo,
        synthesis_cache_dir=paths.synthesis_dir,
    )
    if args.hygiene_json:
        print(json.dumps(hygiene_status.to_dict(), indent=2, sort_keys=True))
    else:
        print(format_vault_hygiene_text(hygiene_status))
        for warning in hygiene_warnings:
            print(f"warning: {warning}")
        for item in hygiene_status.safe_delete_candidates[:20]:
            print(f"orphan\t{item.path}\t{item.reason}")
        if len(hygiene_status.safe_delete_candidates) > 20:
            remaining = len(hygiene_status.safe_delete_candidates) - 20
            print(f"... {remaining} more safe-delete orphan(s)")
        for group in hygiene_status.duplicate_groups[:10]:
            extras = [path for path in group.paths if path != group.recommended_keep]
            print(f"duplicate\tkeep={group.recommended_keep}\tremove={','.join(extras)}")
        if len(hygiene_status.duplicate_groups) > 10:
            remaining = len(hygiene_status.duplicate_groups) - 10
            print(f"... {remaining} more duplicate group(s)")

    if hygiene_status.safe_delete_candidates or hygiene_status.duplicate_groups:
        exit_code = 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
