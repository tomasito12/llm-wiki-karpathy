"""CLI for executing Stage 2 synthesis calls."""

from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path

from src.ingest_review.paths import load_repo_dotenv
from src.wiki_synthesis.executor import SynthesisRunReport, run_synthesis
from src.wiki_synthesis.openai_provider import OpenAISynthesisProvider
from src.wiki_synthesis.planner import load_graph_export

LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build the wiki-synthesis-run argument parser."""
    root = load_repo_dotenv()
    parser = argparse.ArgumentParser(
        prog="wiki-synthesis-run",
        description="Run controlled Stage 2 synthesis calls and write cache entries.",
    )
    parser.add_argument(
        "--graph-path",
        type=Path,
        default=root / "state" / "wiki_render_graph.json",
        help="Path to the wiki-render graph export.",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=root / "state" / "synthesis",
        help="Directory for Stage 2 synthesis cache entries.",
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
        help="Only run one graph category, for example topic, glossary, trend, or how_to.",
    )
    parser.add_argument(
        "--entity",
        default=None,
        help="Only run one entity id, for example glossary:fine-tuning.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=1,
        help="Maximum number of synthesis calls to run. Defaults to 1.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Plan calls without making API requests or writing cache files.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Required for real API calls and cache writes.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the run report as JSON.",
    )
    return parser


def main() -> int:
    """Run controlled Stage 2 synthesis."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args()
    if not args.dry_run and not args.yes:
        LOGGER.error("Refusing real synthesis run without --yes. Use --dry-run to preview.")
        return 2
    if args.limit < 1:
        LOGGER.error("--limit must be at least 1")
        return 2
    graph = load_graph_export(args.graph_path.resolve())
    if args.dry_run:
        provider = _DryRunProvider()
        report = run_synthesis(
            graph,
            cache_dir=args.cache_dir.resolve(),
            provider=provider,
            model=args.model,
            category=args.category,
            entity=args.entity,
            limit=args.limit,
            dry_run=True,
        )
    else:
        if not os.environ.get("OPENAI_API_KEY"):
            LOGGER.error("OPENAI_API_KEY is not set. Add it to .env or export it.")
            return 2
        provider = OpenAISynthesisProvider()
        try:
            report = run_synthesis(
                graph,
                cache_dir=args.cache_dir.resolve(),
                provider=provider,
                model=args.model,
                category=args.category,
                entity=args.entity,
                limit=args.limit,
                dry_run=False,
            )
        finally:
            provider.close()
    if args.json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    else:
        _print_text_report(report)
    LOGGER.info(
        "wiki-synthesis-run complete planned=%d called=%d written=%d dry_run=%s",
        report.planned,
        report.called,
        report.written,
        report.dry_run,
    )
    return 0


class _DryRunProvider:
    """Provider placeholder used only because dry-run never calls providers."""

    def synthesize(
        self, *_args: object, **_kwargs: object
    ) -> tuple[dict[str, object], dict[str, object]]:
        """Raise if a dry-run unexpectedly tries to call a provider."""
        msg = "Dry-run provider should not be called"
        raise RuntimeError(msg)


def _print_text_report(report: SynthesisRunReport) -> None:
    """Print a human-readable run report."""
    data = report.to_dict()
    print(
        "wiki-synthesis-run "
        f"planned={data['planned']} called={data['called']} "
        f"written={data['written']} dry_run={data['dry_run']}"
    )
    for item in data["items"]:
        print(
            f"{item['action']}\t{item['state']}\t{item['entity_id']}\t"
            f"{item['current_input_hash']}\t{item['cache_path']}"
        )


if __name__ == "__main__":
    raise SystemExit(main())
