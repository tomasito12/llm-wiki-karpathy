"""CLI for wiki schema/link validation."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.readwise.sync import _repo_root
from src.wiki_lint.validator import validate_wiki


def build_parser() -> argparse.ArgumentParser:
    """Build the wiki-lint parser."""
    parser = argparse.ArgumentParser(
        prog="wiki-lint",
        description="Validate wiki markdown contracts, links, and index parity.",
    )
    parser.add_argument(
        "--wiki-dir",
        type=Path,
        default=_repo_root() / "wiki",
        help="Wiki root directory (default: <repo>/wiki).",
    )
    return parser


def main() -> int:
    """Run wiki validation and print findings."""
    args = build_parser().parse_args()
    wiki_dir = args.wiki_dir.resolve()
    issues = validate_wiki(wiki_dir)
    if not issues:
        print(f"wiki-lint: ok ({wiki_dir})")
        return 0
    print(f"wiki-lint: {len(issues)} issue(s)")
    for issue in issues:
        print(f"{issue.path}: {issue.message}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
