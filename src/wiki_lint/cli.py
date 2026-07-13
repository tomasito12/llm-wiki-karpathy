"""CLI for wiki schema/link validation."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from src.readwise.sync import _repo_root
from src.wiki_lint.validator import validate_wiki
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
    issues = validate_wiki(wiki_dir, include_non_managed=args.include_non_managed)
    if not issues:
        print(f"wiki-lint: ok ({wiki_dir})")
        return 0
    print(f"wiki-lint: {len(issues)} issue(s)")
    for issue in issues:
        print(f"{issue.path}: {issue.message}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
