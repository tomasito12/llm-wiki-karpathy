"""CLI for unattended synchronous ingest pre-analysis."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from src.ingest_batch.preanalyze import (
    PreanalyzeProgress,
    PreanalyzeResult,
    preanalyze_pending_with_repo_defaults,
)
from src.ingest_review.paths import load_repo_dotenv
from src.ingest_review.schema import PROMPT_VERSION


def build_parser() -> argparse.ArgumentParser:
    """Construct the ``ingest-preanalyze`` argument parser."""
    root = load_repo_dotenv()
    parser = argparse.ArgumentParser(
        prog="ingest-preanalyze",
        description="Pre-analyze pending Readwise exports with the synchronous review pipeline.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        metavar="N",
        help="Maximum number of pending sources to process (default: 50).",
    )
    parser.add_argument(
        "--skip-existing",
        dest="skip_existing",
        action="store_true",
        default=True,
        help="Skip sources whose review.json already exists (default).",
    )
    parser.add_argument(
        "--no-skip-existing",
        dest="skip_existing",
        action="store_false",
        help="Do not skip existing review.json files if they are selected.",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("INGEST_OPENAI_MODEL", "gpt-4o-mini"),
        help="OpenAI model name (default: INGEST_OPENAI_MODEL or gpt-4o-mini).",
    )
    parser.add_argument(
        "--prompt-version",
        default=PROMPT_VERSION,
        help=f"Prompt version to record (default: {PROMPT_VERSION}).",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=root / "raw" / "readwise",
        help="Readwise export directory (default: <repo>/raw/readwise).",
    )
    parser.add_argument(
        "--reviews-dir",
        type=Path,
        default=root / "state" / "reviews",
        help="Review artifacts directory (default: <repo>/state/reviews).",
    )
    parser.add_argument(
        "--wiki-root",
        type=Path,
        default=root / "wiki",
        help="Wiki root directory (default: <repo>/wiki).",
    )
    parser.add_argument(
        "--between-articles",
        type=float,
        default=float(os.environ.get("INGEST_BETWEEN_ARTICLES_DELAY", "0")),
        metavar="SECONDS",
        help=(
            "Pause between articles after closing the OpenAI client "
            "(default: INGEST_BETWEEN_ARTICLES_DELAY or 0). "
            "Use 600 for a 10-minute manual-ingest rhythm."
        ),
    )
    return parser


def format_result_summary(result: PreanalyzeResult) -> str:
    """Return a concise text summary for one pre-analysis result."""
    return (
        f"Pre-analysis complete: selected {result.selected}, "
        f"processed {len(result.processed)}, skipped {len(result.skipped)}, "
        f"failed {len(result.failed)}, elapsed {result.elapsed_seconds:.1f}s."
    )


def main(argv: list[str] | None = None) -> int:
    """Run ``ingest-preanalyze`` from command-line arguments."""
    args = build_parser().parse_args(argv)
    root = load_repo_dotenv()
    if not os.environ.get("OPENAI_API_KEY"):
        print(
            "OPENAI_API_KEY is not set. Add it to .env at the repo root or export it.",
            file=sys.stderr,
        )
        return 2

    raw_dir = args.raw_dir.expanduser().resolve()
    reviews_root = args.reviews_dir.expanduser().resolve()
    wiki_root = args.wiki_root.expanduser().resolve()
    if not raw_dir.is_dir():
        print(f"raw-dir is not a directory: {raw_dir}", file=sys.stderr)
        return 1

    reviews_root.mkdir(parents=True, exist_ok=True)

    def print_progress(progress: PreanalyzeProgress) -> None:
        """Print one progress line."""
        suffix = f" - {progress.message}" if progress.message else ""
        print(
            f"[{progress.index}/{progress.total}] {progress.status}: {progress.source_id}{suffix}",
            flush=True,
        )

    result = preanalyze_pending_with_repo_defaults(
        repo_root=root,
        raw_dir=raw_dir,
        reviews_root=reviews_root,
        wiki_root=wiki_root,
        model=args.model,
        prompt_version=args.prompt_version,
        limit=args.limit,
        skip_existing=args.skip_existing,
        between_articles_seconds=args.between_articles,
        on_progress=print_progress,
    )
    print(format_result_summary(result))
    if result.failed:
        for failure in result.failed:
            print(f"FAILED {failure.source_id}: {failure.message}", file=sys.stderr)
    return 1 if result.all_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
