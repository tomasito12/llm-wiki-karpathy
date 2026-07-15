"""Human-readable summaries for wiki-render runs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from src.wiki_render.source_text import SourceTextCoverage
from src.wiki_render.writer import WriteReport


@dataclass(frozen=True)
class PreviousRenderSnapshot:
    """Counts recorded in the last render manifest, when available."""

    source_count: int | None
    knowledge_page_count: int | None
    file_count: int | None


@dataclass(frozen=True)
class RenderRunSummary:
    """Facts needed to explain one wiki-render run."""

    dry_run: bool
    source_count: int
    knowledge_page_count: int
    write_report: WriteReport
    coverage: SourceTextCoverage
    previous: PreviousRenderSnapshot | None = None
    include_in_progress: bool = False
    excluded_in_progress_sources: int = 0


def load_previous_render_snapshot(manifest_path: Path) -> PreviousRenderSnapshot | None:
    """Read source, page, and file counts from an existing render manifest."""
    if not manifest_path.is_file():
        return None
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    source_count = _optional_int(payload.get("source_count"))
    knowledge_page_count = _optional_int(payload.get("knowledge_page_count"))
    files = payload.get("files")
    file_count = len(files) if isinstance(files, list) else None
    if source_count is None and knowledge_page_count is None and file_count is None:
        return None
    return PreviousRenderSnapshot(
        source_count=source_count,
        knowledge_page_count=knowledge_page_count,
        file_count=file_count,
    )


def format_render_summary_text(
    summary: RenderRunSummary,
    *,
    show_writes: bool = False,
    show_prune: bool = False,
) -> str:
    """Return a plain-language explanation of a wiki-render run."""
    report = summary.write_report
    mode = "dry-run — no files changed" if summary.dry_run else "write"
    write_label = "would write" if summary.dry_run else "written"
    prune_label = "would prune" if summary.dry_run else "pruned"
    scope_label = (
        "finished reviews + in-progress preview"
        if summary.include_in_progress
        else "finished reviews only"
    )
    lines = [
        f"Wiki Render Summary ({mode})",
        "",
        "How to read these numbers",
        f"- render scope: {scope_label}",
        "- sources: reviewed Readwise articles that get a source page (wiki/sources/*.md)",
        "- knowledge pages: aggregated wiki pages from reviews (topics, concepts, …)",
        "- output files: all generated markdown files (sources + knowledge pages + indexes)",
        f"- {write_label}: files new or different from what is on disk now",
        "- unchanged: files already on disk with identical content",
        f"- {prune_label}: stale files from the last render no longer needed",
        "- protected: in-progress preview files kept on disk and not deleted",
        "",
        "Planned output",
        _count_line("sources", summary.source_count, summary.previous, "source_count"),
        _count_line(
            "knowledge pages",
            summary.knowledge_page_count,
            summary.previous,
            "knowledge_page_count",
        ),
        _count_line("output files", report.planned, summary.previous, "file_count"),
        f"- {write_label}: {report.written}",
        f"- unchanged: {report.unchanged}",
        f"- {prune_label}: {report.pruned}",
    ]
    if report.protected_from_prune:
        lines.append(f"- protected from {prune_label}: {report.protected_from_prune}")
    if summary.excluded_in_progress_sources and not summary.include_in_progress:
        lines.append(
            f"- in-progress sources excluded from render: {summary.excluded_in_progress_sources}"
        )
    if report.skipped_prune:
        lines.append("- prune: skipped (no previous manifest to compare)")
    lines.extend(["", "Source full text"])
    if summary.coverage.total:
        lines.append(
            "- "
            f"{summary.coverage.available} of {summary.coverage.total} source pages "
            f"{'would include' if summary.dry_run else 'include'} "
            f"embedded raw text ({summary.coverage.available_ratio:.1%})"
        )
        lines.append(f"- missing: {summary.coverage.missing}")
    else:
        lines.append("- no source pages planned")
    lines.extend(["", "Next step"])
    if summary.dry_run:
        lines.append(
            "- If this looks right, run wiki-render without --dry-run to update the vault."
        )
    else:
        lines.append("- Open the vault and spot-check changed pages, then run wiki-lint.")
    if show_writes and report.write_paths:
        lines.extend(["", f"Files that {write_label}"])
        lines.extend(f"- {path}" for path in report.write_paths)
        lines.extend(["", "By folder"])
        lines.extend(f"- {line}" for line in summarize_paths_by_folder(report.write_paths))
    if show_prune and report.prune_paths:
        lines.extend(["", f"Files that {prune_label}"])
        lines.extend(f"- {path}" for path in report.prune_paths)
    return "\n".join(lines)


def summarize_paths_by_folder(paths: tuple[str, ...] | list[str]) -> list[str]:
    """Return sorted folder counts for a list of repo-relative paths."""
    counts: dict[str, int] = {}
    for path in paths:
        folder = path.split("/", 1)[0] if "/" in path else "(root)"
        counts[folder] = counts.get(folder, 0) + 1
    return [f"{folder}/: {count}" for folder, count in sorted(counts.items())]


def _count_line(
    label: str,
    current: int,
    previous: PreviousRenderSnapshot | None,
    field: str,
) -> str:
    """Format one planned-output line, optionally with a delta vs the last render."""
    if previous is None:
        return f"- {label}: {current}"
    previous_value = getattr(previous, field)
    if previous_value is None:
        return f"- {label}: {current}"
    delta = current - previous_value
    if delta == 0:
        return f"- {label}: {current} (unchanged vs last render)"
    sign = "+" if delta > 0 else ""
    return f"- {label}: {current} ({sign}{delta} vs last render: {previous_value})"


def _optional_int(value: object) -> int | None:
    """Return an int when *value* is a whole number."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None
