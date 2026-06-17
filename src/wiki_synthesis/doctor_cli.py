"""CLI for Stage 2 synthesis preflight checks."""

from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path

from src.ingest_review.paths import load_repo_dotenv
from src.wiki_synthesis.doctor import DoctorReport, run_doctor
from src.wiki_synthesis.planner import load_graph_export

LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build the wiki-synthesis-doctor argument parser."""
    root = load_repo_dotenv()
    parser = argparse.ArgumentParser(
        prog="wiki-synthesis-doctor",
        description="Run preflight checks before Stage 2 synthesis.",
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
        help="Only check one graph category, for example topic, glossary, trend, or how_to.",
    )
    parser.add_argument(
        "--entity",
        default=None,
        help="Only check one entity id, for example glossary:fine-tuning.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=1,
        help="Maximum number of planned targets to inspect. Defaults to 1.",
    )
    parser.add_argument(
        "--include-single-source",
        action="store_true",
        help="Include single-source pages as readable summary candidates.",
    )
    parser.add_argument(
        "--require-api-key",
        action="store_true",
        help="Fail if OPENAI_API_KEY is not set.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the doctor report as JSON.",
    )
    return parser


def main() -> int:
    """Run synthesis preflight checks."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args()
    graph_path = args.graph_path.resolve()
    graph = load_graph_export(graph_path)
    report = run_doctor(
        graph,
        graph_path=graph_path,
        cache_dir=args.cache_dir.resolve(),
        preview_dir=args.preview_dir.resolve(),
        report_dir=args.report_dir.resolve(),
        model=args.model,
        category=args.category,
        entity=args.entity,
        include_single_source=args.include_single_source,
        limit=args.limit,
        require_api_key=args.require_api_key,
    )
    if args.json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    else:
        _print_text_report(report)
    LOGGER.info(
        "wiki-synthesis-doctor complete ready=%s checks=%d",
        report.ready,
        len(report.checks),
    )
    return report.exit_code


def _print_text_report(report: DoctorReport) -> None:
    """Print a human-readable doctor report."""
    print(
        "wiki-synthesis-doctor "
        f"ready={report.ready} model={report.model} "
        f"planned={report.plan.summary.shown} cache_errors={report.cache_lint.errors}"
    )
    for check in report.checks:
        print(f"{check.status}\t{check.name}\t{check.message}")
    for entry in report.plan.entries:
        print(
            f"plan\t{entry.state}\t{entry.entity_id}\t"
            f"sources={entry.source_count}\tevidence={entry.evidence_count}"
        )


if __name__ == "__main__":
    raise SystemExit(main())
