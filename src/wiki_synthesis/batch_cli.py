"""CLI for controlled Stage 2 synthesis batch execution."""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

from src.ingest_review.paths import load_repo_dotenv
from src.wiki_paths.cli_helpers import (
    add_paths_config_argument,
    load_paths_for_cli,
    resolve_cli_path,
)
from src.wiki_paths.config import WikiPathsConfigError
from src.wiki_synthesis.batch import (
    DEFAULT_BATCH_LIMIT,
    format_batch_text,
    run_synthesis_batch,
)
from src.wiki_synthesis.openai_provider import OpenAISynthesisProvider
from src.wiki_synthesis.planner import load_graph_export

LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build the wiki-synthesis-batch argument parser."""
    load_repo_dotenv()
    parser = argparse.ArgumentParser(
        prog="wiki-synthesis-batch",
        description="Execute a bounded batch of ranked Stage 2 synthesis candidates.",
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
        help="Directory for Stage 2 synthesis cache entries.",
    )
    parser.add_argument(
        "--preview-dir",
        type=Path,
        default=None,
        help="Directory for rendered review previews.",
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=None,
        help="Directory for batch audit reports.",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get(
            "WIKI_SYNTHESIS_OPENAI_MODEL",
            os.environ.get("INGEST_OPENAI_MODEL", "gpt-4o-mini"),
        ),
        help="OpenAI model name.",
    )
    parser.add_argument(
        "--category",
        default=None,
        help="Only batch one graph category, for example topic or glossary.",
    )
    parser.add_argument(
        "--entity",
        default=None,
        help="Only batch one entity id, for example topic:provenance-tracking.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_BATCH_LIMIT,
        help="Maximum number of selected candidates to process.",
    )
    parser.add_argument(
        "--include-single-source",
        action="store_true",
        help="Include single-source knowledge pages in selection.",
    )
    parser.add_argument(
        "--between-calls",
        type=float,
        default=0,
        help="Pause in seconds between actual API calls.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Select candidates without API calls or file writes.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Required for real API calls and cache writes.",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue processing remaining candidates after a failure.",
    )
    parser.add_argument(
        "--no-audit-log",
        action="store_true",
        help="Skip writing a real-run batch audit report.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the batch report as JSON.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run a bounded Stage 2 synthesis batch."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args(argv)
    if not args.dry_run and not args.yes:
        LOGGER.error("Refusing real synthesis batch without --yes. Use --dry-run to preview.")
        return 2
    if args.limit < 1:
        LOGGER.error("--limit must be at least 1")
        return 2
    if not args.dry_run and not os.environ.get("OPENAI_API_KEY"):
        LOGGER.error("OPENAI_API_KEY is not set. Add it to .env or export it.")
        return 2
    try:
        paths = load_paths_for_cli(args)
    except WikiPathsConfigError as exc:
        LOGGER.error("%s", exc)
        return 2
    graph_path = resolve_cli_path(args.graph_path, configured=paths.graph_path)
    cache_dir = resolve_cli_path(args.cache_dir, configured=paths.synthesis_dir)
    preview_dir = resolve_cli_path(args.preview_dir, configured=paths.preview_dir)
    report_dir = resolve_cli_path(args.report_dir, configured=paths.run_dir)
    graph = load_graph_export(graph_path)
    provider_factory = None if args.dry_run else _OpenAIProviderFactory()
    progress_lines: list[str] = []

    def _progress(message: str) -> None:
        progress_lines.append(message)
        if not args.json:
            print(message)

    report = run_synthesis_batch(
        graph,
        cache_dir=cache_dir,
        preview_dir=preview_dir,
        report_dir=report_dir,
        provider_factory=provider_factory,
        model=args.model,
        category=args.category,
        entity=args.entity,
        include_single_source=args.include_single_source,
        limit=args.limit,
        dry_run=args.dry_run,
        between_calls=args.between_calls,
        continue_on_error=args.continue_on_error,
        write_audit=not args.no_audit_log,
        progress_fn=_progress,
    )
    if args.json:
        payload = report.to_dict()
        payload["progress"] = progress_lines
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(format_batch_text(report))
    LOGGER.info(
        "wiki-synthesis-batch complete selected=%d attempted=%d called=%d "
        "written=%d failed=%d dry_run=%s",
        report.selected,
        report.attempted,
        report.called,
        report.written,
        report.failed,
        report.dry_run,
    )
    return 1 if report.failed else 0


class _OpenAIProviderFactory:
    """Create one OpenAI provider per batch item."""

    def __call__(self) -> OpenAISynthesisProvider:
        """Return a fresh OpenAI synthesis provider."""
        return OpenAISynthesisProvider()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
