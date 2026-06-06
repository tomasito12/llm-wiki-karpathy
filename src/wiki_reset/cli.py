"""Entry point for ``wiki-reset``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.wiki_reset.reset import (
    CONFIRMATION_PHRASE,
    default_feedback_db_path,
    default_ingest_manifest_path,
    default_readwise_index_path,
    default_reviews_root,
    default_wiki_render_manifest_path,
    default_wiki_root,
    readwise_library_document_count,
    run_wiki_reset,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the wiki-reset CLI."""
    parser = argparse.ArgumentParser(
        prog="wiki-reset",
        description=(
            "Delete generated wiki content while preserving operator paths (notes/, legacy/, "
            "AGENTS.md, index.md, log.md), recreate empty managed-folder shells, clear audit "
            "manifests, and reset config/review_* tag allowlists to baseline seeds. "
            "Does not touch raw/readwise exports. "
            "The Readwise export index is preserved unless --reset-readwise-index is set."
        ),
    )
    parser.add_argument(
        "--wiki-dir",
        type=Path,
        default=default_wiki_root(),
        help="Wiki root directory (default: <repo>/wiki).",
    )
    parser.add_argument(
        "--index",
        type=Path,
        default=default_readwise_index_path(),
        help="Readwise library JSON path (default: <repo>/state/readwise_library.json).",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=default_ingest_manifest_path(),
        help="Ingest manifest JSON path (default: <repo>/state/ingest_manifest.json).",
    )
    parser.add_argument(
        "--reset-readwise-index",
        action="store_true",
        help=(
            "Also clear state/readwise_library.json (export dedupe + watermark). "
            "Next readwise-sync uses the ~100-day lookback when the watermark is gone."
        ),
    )
    parser.add_argument(
        "--keep-reviews",
        action="store_true",
        help=(
            "Preserve state/reviews/ artifacts and state/review_feedback.sqlite. "
            "By default both are deleted."
        ),
    )
    parser.add_argument(
        "--keep-tag-taxonomy",
        action="store_true",
        help=(
            "Preserve config/review_tags_*.yaml and config/review_*_types.yaml. "
            "By default all are reset to minimal baseline allowlists."
        ),
    )
    parser.add_argument(
        "--keep-wiki-render-manifest",
        action="store_true",
        help="Preserve state/wiki_render_manifest.json (cleared by default).",
    )
    parser.add_argument(
        "--wiki-render-manifest",
        type=Path,
        default=default_wiki_render_manifest_path(),
        help="Wiki render manifest path (default: <repo>/state/wiki_render_manifest.json).",
    )
    parser.add_argument(
        "--confirm",
        default=None,
        metavar="PHRASE",
        help=f"Non-interactive confirmation; must be exactly {CONFIRMATION_PHRASE!r}.",
    )
    return parser


def main() -> int:
    """Run CLI; return process exit code."""
    args = build_parser().parse_args()
    phrase = CONFIRMATION_PHRASE
    index_path = args.index.resolve()

    clear_rw = args.reset_readwise_index
    clear_reviews = not args.keep_reviews
    reset_tags = not args.keep_tag_taxonomy
    doc_count = readwise_library_document_count(index_path)

    if args.confirm is not None:
        if args.confirm != phrase:
            print(
                f"Confirmation mismatch: expected {phrase!r}, got {args.confirm!r}.",
                file=sys.stderr,
            )
            return 1
        if clear_rw:
            print(
                f"NOTE: --reset-readwise-index will clear {doc_count} document(s) in {index_path}.",
                file=sys.stderr,
            )
    else:
        prompt_state = {
            "readwise_library": clear_rw,
            "ingest_manifest": True,
            "wiki_render_manifest": not args.keep_wiki_render_manifest,
            "review_state": clear_reviews,
            "tag_taxonomy": reset_tags,
        }
        prompt_summary = ", ".join(
            f"{name} {'cleared' if cleared else 'preserved'}"
            for name, cleared in sorted(prompt_state.items())
        )
        print(
            "This will DELETE generated wiki pages while preserving notes/, legacy/, and "
            f"operator hub files, then recreate empty managed-folder shells. "
            f"State: {prompt_summary}."
        )
        if clear_rw:
            print(
                f"WARNING: --reset-readwise-index will CLEAR the Readwise export index "
                f"({doc_count} document(s) in {index_path}).",
                file=sys.stderr,
            )
        print(f"Type {phrase!r} to confirm, or anything else to abort.")
        if input().strip() != phrase:
            print("Aborted.", file=sys.stderr)
            return 1

    try:
        deleted, state_results = run_wiki_reset(
            args.wiki_dir.resolve(),
            index_path,
            clear_readwise_index=clear_rw,
            manifest_path=args.manifest.resolve(),
            clear_wiki_render_manifest=not args.keep_wiki_render_manifest,
            wiki_render_manifest_path=args.wiki_render_manifest.resolve(),
            clear_reviews=clear_reviews,
            reset_tag_taxonomy_config=reset_tags,
            reviews_root=default_reviews_root(),
            feedback_db_path=default_feedback_db_path(),
        )
    except FileNotFoundError as err:
        print(str(err), file=sys.stderr)
        return 1

    state_summary = ", ".join(
        f"{name} {'cleared' if cleared else 'preserved'}"
        for name, cleared in sorted(state_results.items())
    )
    print(f"Removed {len(deleted)} wiki file(s). State: {state_summary}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
