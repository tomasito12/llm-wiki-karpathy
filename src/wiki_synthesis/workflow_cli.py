"""Primary CLI for the controlled Stage 2 synthesis workflow."""

from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path

from src.ingest_review.paths import load_repo_dotenv
from src.wiki_synthesis.openai_provider import OpenAISynthesisProvider
from src.wiki_synthesis.planner import load_graph_export
from src.wiki_synthesis.workflow import (
    SynthesisWorkflowReport,
    run_synthesis_workflow,
    write_workflow_audit_report,
)

LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build the wiki-synthesis-workflow argument parser."""
    root = load_repo_dotenv()
    parser = argparse.ArgumentParser(
        prog="wiki-synthesis-workflow",
        description="Plan, run, and review Stage 2 synthesis with one safe command.",
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
        "--preview-dir",
        type=Path,
        default=root / "state" / "synthesis_previews",
        help="Directory for rendered review previews.",
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=root / "state" / "synthesis_runs",
        help="Directory for real-run audit reports.",
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
        "--include-single-source",
        action="store_true",
        help="Include single-source pages as readable summaries. Default skips them.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Plan without API calls, cache writes, or preview writes.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Required for real API calls and cache writes.",
    )
    parser.add_argument(
        "--no-review",
        action="store_true",
        help="Skip preview rendering after successful cache writes.",
    )
    parser.add_argument(
        "--no-audit-log",
        action="store_true",
        help="Skip writing a real-run audit report.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the workflow report as JSON.",
    )
    return parser


def main() -> int:
    """Run the primary Stage 2 synthesis workflow."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args()
    if not args.dry_run and not args.yes:
        LOGGER.error("Refusing real synthesis workflow without --yes. Use --dry-run to preview.")
        return 2
    if args.limit < 1:
        LOGGER.error("--limit must be at least 1")
        return 2
    graph = load_graph_export(args.graph_path.resolve())
    if args.dry_run:
        provider = _DryRunProvider()
        report = run_synthesis_workflow(
            graph,
            cache_dir=args.cache_dir.resolve(),
            preview_dir=args.preview_dir.resolve(),
            provider=provider,
            model=args.model,
            category=args.category,
            entity=args.entity,
            include_single_source=args.include_single_source,
            limit=args.limit,
            dry_run=True,
            review=not args.no_review,
        )
    else:
        if not os.environ.get("OPENAI_API_KEY"):
            LOGGER.error("OPENAI_API_KEY is not set. Add it to .env or export it.")
            return 2
        provider = OpenAISynthesisProvider()
        try:
            report = run_synthesis_workflow(
                graph,
                cache_dir=args.cache_dir.resolve(),
                preview_dir=args.preview_dir.resolve(),
                provider=provider,
                model=args.model,
                category=args.category,
                entity=args.entity,
                include_single_source=args.include_single_source,
                limit=args.limit,
                dry_run=False,
                review=not args.no_review,
            )
        finally:
            provider.close()
    audit_path = ""
    if not args.dry_run and not args.no_audit_log:
        audit_path = str(
            write_workflow_audit_report(
                report,
                report_dir=args.report_dir.resolve(),
                options=_audit_options(args),
            )
        )
    if args.json:
        payload = report.to_dict()
        payload["audit_report_path"] = audit_path
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        _print_text_report(report, audit_path=audit_path)
    LOGGER.info(
        "wiki-synthesis-workflow complete planned=%d called=%d written=%d reviews=%d dry_run=%s",
        report.run.planned,
        report.run.called,
        report.run.written,
        len(report.reviews),
        report.run.dry_run,
    )
    return 0


def _print_text_report(report: SynthesisWorkflowReport, *, audit_path: str = "") -> None:
    """Print a human-readable workflow report."""
    run = report.run
    print(
        "wiki-synthesis-workflow "
        f"planned={run.planned} called={run.called} written={run.written} "
        f"reviews={len(report.reviews)} dry_run={run.dry_run}"
    )
    for item in run.items:
        print(
            f"run\t{item.action}\t{item.state}\t{item.entity_id}\t"
            f"{item.current_input_hash}\t{item.cache_path}"
        )
    for review in report.reviews:
        print(
            f"review\t{review.validation_state}\t{review.rendered_synthesis_state}\t"
            f"{review.entity_id}\t{review.preview_path}"
        )
    if audit_path:
        print(f"audit_report\t{audit_path}")


def _audit_options(args: argparse.Namespace) -> dict[str, object]:
    """Return CLI options worth preserving in audit reports."""
    return {
        "graph_path": str(args.graph_path),
        "cache_dir": str(args.cache_dir),
        "preview_dir": str(args.preview_dir),
        "model": str(args.model),
        "category": args.category,
        "entity": args.entity,
        "limit": args.limit,
        "include_single_source": bool(args.include_single_source),
        "review": not bool(args.no_review),
    }


class _DryRunProvider:
    """Provider placeholder used only because dry-run never calls providers."""

    def synthesize(
        self, *_args: object, **_kwargs: object
    ) -> tuple[dict[str, object], dict[str, object]]:
        """Raise if a dry-run unexpectedly tries to call a provider."""
        msg = "Dry-run provider should not be called"
        raise RuntimeError(msg)


if __name__ == "__main__":
    raise SystemExit(main())
