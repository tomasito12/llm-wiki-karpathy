"""Collect read-only operational status for the wiki system."""

from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from src.ingest_review.review_queue_status import status_from_artifact
from src.wiki_synthesis.cache_lint import lint_synthesis_cache
from src.wiki_synthesis.planner import load_graph_export, plan_from_graph


@dataclass(frozen=True)
class OpsStatusConfig:
    """Filesystem paths used to collect wiki operations status."""

    repo_root: Path
    raw_dir: Path
    reviews_dir: Path
    wiki_dir: Path
    graph_path: Path
    manifest_path: Path
    synthesis_cache_dir: Path
    preview_dir: Path
    run_dir: Path
    backup_dir: Path


@dataclass(frozen=True)
class SourceStatus:
    """Counts for Readwise raw export files."""

    raw_html: int
    raw_markdown: int
    paired: int
    incomplete: int


@dataclass(frozen=True)
class ReviewStatus:
    """Counts for human review artifacts."""

    artifacts: int
    finished: int
    in_progress: int
    malformed: int


@dataclass(frozen=True)
class RenderStatus:
    """Presence and summary counts for wiki render state."""

    wiki_dir_exists: bool
    graph_exists: bool
    manifest_exists: bool
    graph_sources: int | None
    graph_knowledge_pages: int | None


@dataclass(frozen=True)
class SynthesisPlanStatus:
    """Changed-only synthesis planning counts."""

    new: int | None
    stale: int | None
    unchanged: int | None
    skipped_single_source: int | None
    skipped_evidence_object: int | None


@dataclass(frozen=True)
class SynthesisStatus:
    """Stage 2 synthesis cache health and planning summary."""

    cache_entries: int
    fresh: int | None
    stale: int | None
    errors: int | None
    missing: int | None
    plan: SynthesisPlanStatus


@dataclass(frozen=True)
class ArtifactStatus:
    """Git and local artifact classification."""

    uncommitted_durable: int
    uncommitted_synthesis_cache: int
    uncommitted_render_outputs: int
    uncommitted_previews: int
    uncommitted_runs: int
    uncommitted_backups: int
    backups_present: bool
    uncommitted_other: int


@dataclass(frozen=True)
class OpsStatus:
    """Full read-only operations status snapshot."""

    sources: SourceStatus
    reviews: ReviewStatus
    render: RenderStatus
    synthesis: SynthesisStatus
    artifacts: ArtifactStatus
    recommendations: list[str]
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable status snapshot."""
        payload = asdict(self)
        payload["synthesis"] = {
            "cache_entries": self.synthesis.cache_entries,
            "fresh": self.synthesis.fresh,
            "stale": self.synthesis.stale,
            "errors": self.synthesis.errors,
            "missing": self.synthesis.missing,
            "plan": asdict(self.synthesis.plan),
        }
        return payload


def default_config(repo_root: Path) -> OpsStatusConfig:
    """Build default status paths relative to the repository root."""
    root = repo_root.resolve()
    return OpsStatusConfig(
        repo_root=root,
        raw_dir=root / "raw" / "readwise",
        reviews_dir=root / "state" / "reviews",
        wiki_dir=root / "wiki",
        graph_path=root / "state" / "wiki_render_graph.json",
        manifest_path=root / "state" / "wiki_render_manifest.json",
        synthesis_cache_dir=root / "state" / "synthesis",
        preview_dir=root / "state" / "synthesis_previews",
        run_dir=root / "state" / "synthesis_runs",
        backup_dir=root / "state" / "synthesis_backups",
    )


def collect_ops_status(
    config: OpsStatusConfig,
    *,
    porcelain_lines: list[str] | None = None,
) -> OpsStatus:
    """Collect read-only operational status for the wiki system."""
    warnings: list[str] = []
    sources = collect_source_status(config.raw_dir)
    reviews = collect_review_status(config.reviews_dir)
    render = collect_render_status(
        wiki_dir=config.wiki_dir,
        graph_path=config.graph_path,
        manifest_path=config.manifest_path,
    )
    synthesis, synthesis_warnings = collect_synthesis_status(
        graph_path=config.graph_path,
        synthesis_cache_dir=config.synthesis_cache_dir,
    )
    warnings.extend(synthesis_warnings)
    artifacts, artifact_warnings = collect_artifact_status(
        config,
        porcelain_lines=porcelain_lines,
    )
    warnings.extend(artifact_warnings)
    status = OpsStatus(
        sources=sources,
        reviews=reviews,
        render=render,
        synthesis=synthesis,
        artifacts=artifacts,
        recommendations=[],
        warnings=warnings,
    )
    recommendations = build_recommendations(status)
    return OpsStatus(
        sources=status.sources,
        reviews=status.reviews,
        render=status.render,
        synthesis=status.synthesis,
        artifacts=status.artifacts,
        recommendations=recommendations,
        warnings=status.warnings,
    )


def collect_source_status(raw_dir: Path) -> SourceStatus:
    """Count Readwise raw export files and paired completeness."""
    if not raw_dir.is_dir():
        return SourceStatus(raw_html=0, raw_markdown=0, paired=0, incomplete=0)
    html_files = sorted(raw_dir.glob("*.html"))
    md_files = sorted(raw_dir.glob("*.md"))
    md_stems = {path.stem for path in md_files}
    html_stems = {path.stem for path in html_files}
    paired = sum(1 for stem in html_stems if stem in md_stems)
    incomplete = len(html_stems.symmetric_difference(md_stems))
    return SourceStatus(
        raw_html=len(html_files),
        raw_markdown=len(md_files),
        paired=paired,
        incomplete=incomplete,
    )


def collect_review_status(reviews_dir: Path) -> ReviewStatus:
    """Count review artifacts and finished vs in-progress state."""
    if not reviews_dir.is_dir():
        return ReviewStatus(artifacts=0, finished=0, in_progress=0, malformed=0)
    artifacts = 0
    finished = 0
    in_progress = 0
    malformed = 0
    for review_path in sorted(reviews_dir.glob("*/review.json")):
        artifacts += 1
        try:
            payload = json.loads(review_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            malformed += 1
            continue
        if not isinstance(payload, dict):
            malformed += 1
            continue
        if status_from_artifact(payload) == "finished":
            finished += 1
        else:
            in_progress += 1
    return ReviewStatus(
        artifacts=artifacts,
        finished=finished,
        in_progress=in_progress,
        malformed=malformed,
    )


def collect_render_status(
    *,
    wiki_dir: Path,
    graph_path: Path,
    manifest_path: Path,
) -> RenderStatus:
    """Report wiki render directory and graph export presence."""
    graph_exists = graph_path.is_file()
    graph_sources: int | None = None
    graph_knowledge_pages: int | None = None
    if graph_exists:
        graph_sources, graph_knowledge_pages = _graph_counts(graph_path)
    return RenderStatus(
        wiki_dir_exists=wiki_dir.is_dir(),
        graph_exists=graph_exists,
        manifest_exists=manifest_path.is_file(),
        graph_sources=graph_sources,
        graph_knowledge_pages=graph_knowledge_pages,
    )


def collect_synthesis_status(
    *,
    graph_path: Path,
    synthesis_cache_dir: Path,
) -> tuple[SynthesisStatus, list[str]]:
    """Summarize synthesis cache health and planning counts."""
    warnings: list[str] = []
    cache_entries = _count_cache_entries(synthesis_cache_dir)
    empty_plan = SynthesisPlanStatus(
        new=None,
        stale=None,
        unchanged=None,
        skipped_single_source=None,
        skipped_evidence_object=None,
    )
    if not graph_path.is_file():
        warnings.append(f"render graph missing: {graph_path}")
        return (
            SynthesisStatus(
                cache_entries=cache_entries,
                fresh=None,
                stale=None,
                errors=None,
                missing=None,
                plan=empty_plan,
            ),
            warnings,
        )
    try:
        graph = load_graph_export(graph_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        warnings.append(f"render graph unreadable: {exc}")
        return (
            SynthesisStatus(
                cache_entries=cache_entries,
                fresh=None,
                stale=None,
                errors=None,
                missing=None,
                plan=empty_plan,
            ),
            warnings,
        )
    lint_report = lint_synthesis_cache(graph, cache_dir=synthesis_cache_dir)
    plan = plan_from_graph(graph, cache_dir=synthesis_cache_dir)
    summary = plan.summary
    return (
        SynthesisStatus(
            cache_entries=cache_entries,
            fresh=lint_report.ok,
            stale=lint_report.warnings,
            errors=lint_report.errors,
            missing=summary.new,
            plan=SynthesisPlanStatus(
                new=summary.new,
                stale=summary.stale,
                unchanged=summary.unchanged,
                skipped_single_source=summary.skipped_single_source,
                skipped_evidence_object=summary.skipped_evidence_object,
            ),
        ),
        warnings,
    )


def collect_artifact_status(
    config: OpsStatusConfig,
    *,
    porcelain_lines: list[str] | None = None,
) -> tuple[ArtifactStatus, list[str]]:
    """Classify uncommitted files and local backup presence."""
    warnings: list[str] = []
    backups_present = _directory_has_entries(config.backup_dir)
    if porcelain_lines is None:
        porcelain_lines, git_warning = _read_git_porcelain(config.repo_root)
        if git_warning:
            warnings.append(git_warning)
    paths = parse_git_porcelain_paths(porcelain_lines)
    classified = classify_uncommitted_paths(config.repo_root, paths)
    return (
        ArtifactStatus(
            uncommitted_durable=classified["durable"],
            uncommitted_synthesis_cache=classified["synthesis_cache"],
            uncommitted_render_outputs=classified["render_outputs"],
            uncommitted_previews=classified["previews"],
            uncommitted_runs=classified["runs"],
            uncommitted_backups=classified["backups"],
            backups_present=backups_present,
            uncommitted_other=classified["other"],
        ),
        warnings,
    )


def parse_git_porcelain_paths(lines: list[str]) -> list[str]:
    """Extract changed file paths from ``git status --porcelain`` lines."""
    paths: list[str] = []
    for line in lines:
        stripped = line.rstrip("\n")
        if not stripped:
            continue
        if len(stripped) < 4:
            continue
        path_part = stripped[3:]
        if " -> " in path_part:
            path_part = path_part.split(" -> ", 1)[1]
        paths.append(path_part.strip())
    return paths


def classify_uncommitted_paths(repo_root: Path, paths: list[str]) -> dict[str, int]:
    """Count uncommitted paths by durable, preview, run, backup, and other classes."""
    counts = {
        "durable": 0,
        "synthesis_cache": 0,
        "render_outputs": 0,
        "previews": 0,
        "runs": 0,
        "backups": 0,
        "other": 0,
    }
    root = repo_root.resolve()
    for raw_path in paths:
        path = (root / raw_path).resolve()
        try:
            relative = path.relative_to(root).as_posix()
        except ValueError:
            counts["other"] += 1
            continue
        if _is_preview_path(relative):
            counts["previews"] += 1
        elif _is_run_path(relative):
            counts["runs"] += 1
        elif _is_backup_path(relative):
            counts["backups"] += 1
        elif _is_durable_path(relative):
            counts["durable"] += 1
            if _is_synthesis_cache_path(relative):
                counts["synthesis_cache"] += 1
            if _is_render_output_path(relative):
                counts["render_outputs"] += 1
        else:
            counts["other"] += 1
    return counts


def build_recommendations(status: OpsStatus) -> list[str]:
    """Return conservative next-action recommendations from status facts."""
    recommendations: list[str] = []
    if status.synthesis.errors:
        recommendations.append("Fix synthesis cache errors before running wiki-render.")
    elif status.synthesis.stale:
        recommendations.append("Refresh stale synthesis entries before final render.")
    elif _synthesis_cache_needs_render_check(status.artifacts):
        recommendations.append("Run hatch run wiki-render --dry-run after synthesis cache changes.")
    elif status.render.graph_exists and status.render.manifest_exists:
        recommendations.append("No render needed.")
    else:
        recommendations.append("Run hatch run wiki-render to create graph state.")
    if (
        status.synthesis.errors == 0
        and status.synthesis.stale == 0
        and status.synthesis.fresh is not None
    ):
        recommendations.append("No cache warnings.")
    if status.artifacts.uncommitted_durable:
        recommendations.append("Review and commit final synthesis cache files.")
    elif _only_temporary_artifacts_uncommitted(status.artifacts):
        recommendations.append(
            "No durable changes pending; preview/run/backup artifacts can remain local "
            "or be cleaned deliberately."
        )
    if status.artifacts.uncommitted_other:
        recommendations.append("Review uncommitted docs and code files before continuing.")
    changed_candidates = _changed_candidate_count(status.synthesis.plan)
    if changed_candidates:
        recommendations.append(
            "Optional: synthesize the next small batch from wiki-synthesis-plan."
        )
    if status.reviews.malformed:
        recommendations.append("Inspect malformed review artifacts under state/reviews/.")
    return recommendations


def format_text_report(status: OpsStatus) -> str:
    """Render a concise human-readable status report."""
    lines = ["Wiki Ops Status", ""]
    lines.extend(
        [
            "Sources",
            f"- raw html exports: {status.sources.raw_html}",
            f"- raw md exports: {status.sources.raw_markdown}",
            f"- paired exports: {status.sources.paired}",
            f"- incomplete exports: {status.sources.incomplete}",
            "",
            "Reviews",
            f"- review artifacts: {status.reviews.artifacts}",
            f"- finished: {status.reviews.finished}",
            f"- in progress: {status.reviews.in_progress}",
            f"- malformed: {status.reviews.malformed}",
            "",
            "Render",
            f"- wiki directory: {_presence_label(status.render.wiki_dir_exists)}",
            f"- graph: {_presence_label(status.render.graph_exists)}",
            f"- manifest: {_presence_label(status.render.manifest_exists)}",
        ]
    )
    if status.render.graph_sources is not None:
        lines.append(f"- graph sources: {status.render.graph_sources}")
    if status.render.graph_knowledge_pages is not None:
        lines.append(f"- graph knowledge pages: {status.render.graph_knowledge_pages}")
    lines.extend(["", "Synthesis", f"- cache entries: {status.synthesis.cache_entries}"])
    if status.synthesis.fresh is not None:
        lines.append(f"- fresh: {status.synthesis.fresh}")
    if status.synthesis.stale is not None:
        lines.append(f"- stale: {status.synthesis.stale}")
    if status.synthesis.errors is not None:
        lines.append(f"- errors: {status.synthesis.errors}")
    plan = status.synthesis.plan
    if plan.new is not None:
        lines.append(f"- changed candidates: {plan.new + (plan.stale or 0)}")
    if plan.skipped_single_source is not None:
        lines.append(f"- skipped single-source: {plan.skipped_single_source}")
    if plan.skipped_evidence_object is not None:
        lines.append(f"- skipped evidence objects: {plan.skipped_evidence_object}")
    lines.extend(
        [
            "",
            "Artifacts",
            f"- uncommitted durable files: {status.artifacts.uncommitted_durable}",
            f"- uncommitted synthesis cache files: {status.artifacts.uncommitted_synthesis_cache}",
            f"- uncommitted render output files: {status.artifacts.uncommitted_render_outputs}",
            f"- uncommitted preview files: {status.artifacts.uncommitted_previews}",
            f"- uncommitted run reports: {status.artifacts.uncommitted_runs}",
            f"- uncommitted backup files: {status.artifacts.uncommitted_backups}",
            f"- uncommitted other files: {status.artifacts.uncommitted_other}",
            f"- backups present: {'yes' if status.artifacts.backups_present else 'no'}",
        ]
    )
    if status.warnings:
        lines.extend(["", "Warnings"])
        lines.extend(f"- {warning}" for warning in status.warnings)
    lines.extend(["", "Recommended next actions"])
    if status.recommendations:
        for index, recommendation in enumerate(status.recommendations, start=1):
            lines.append(f"{index}. {recommendation}")
    else:
        lines.append("1. No actions recommended.")
    return "\n".join(lines)


def _graph_counts(graph_path: Path) -> tuple[int | None, int | None]:
    """Return source and knowledge-page counts from a graph export."""
    try:
        with graph_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None, None
    if not isinstance(payload, dict):
        return None, None
    sources = payload.get("sources")
    pages = payload.get("knowledge_pages")
    source_count = len(sources) if isinstance(sources, list) else None
    page_count = len(pages) if isinstance(pages, list) else None
    return source_count, page_count


def _count_cache_entries(synthesis_cache_dir: Path) -> int:
    """Count synthesis cache JSON files on disk."""
    if not synthesis_cache_dir.is_dir():
        return 0
    return sum(1 for _ in synthesis_cache_dir.glob("*/*.json"))


def _read_git_porcelain(repo_root: Path) -> tuple[list[str], str | None]:
    """Return porcelain lines from git or an empty list with a warning."""
    try:
        completed = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return [], f"git unavailable: {exc}"
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or "git status failed"
        return [], stderr
    output = completed.stdout
    if not output:
        return [], None
    return output.splitlines(), None


def _directory_has_entries(path: Path) -> bool:
    """Return whether a directory exists and contains at least one entry."""
    if not path.is_dir():
        return False
    return any(path.iterdir())


def _is_durable_path(relative_path: str) -> bool:
    """Return whether a repo-relative path is a durable artifact."""
    return (
        _is_render_output_path(relative_path)
        or _is_synthesis_cache_path(relative_path)
        or _is_review_artifact_path(relative_path)
    )


def _is_render_output_path(relative_path: str) -> bool:
    """Return whether a repo-relative path is generated render output."""
    if relative_path == "state/wiki_render_manifest.json":
        return True
    if relative_path == "state/wiki_render_graph.json":
        return True
    if relative_path.startswith("wiki/"):
        return True
    return False


def _is_synthesis_cache_path(relative_path: str) -> bool:
    """Return whether a repo-relative path is a final synthesis cache entry."""
    return relative_path.startswith("state/synthesis/") and relative_path.endswith(".json")


def _is_review_artifact_path(relative_path: str) -> bool:
    """Return whether a repo-relative path is a final review artifact."""
    return relative_path.startswith("state/reviews/") and relative_path.endswith("/review.json")


def _is_preview_path(relative_path: str) -> bool:
    """Return whether a repo-relative path is a synthesis preview artifact."""
    return _is_under_state_path(relative_path, "state/synthesis_previews")


def _is_run_path(relative_path: str) -> bool:
    """Return whether a repo-relative path is a synthesis run report."""
    return _is_under_state_path(relative_path, "state/synthesis_runs")


def _is_backup_path(relative_path: str) -> bool:
    """Return whether a repo-relative path is a synthesis backup artifact."""
    return _is_under_state_path(relative_path, "state/synthesis_backups")


def _is_under_state_path(relative_path: str, state_subpath: str) -> bool:
    """Return whether a path equals or is nested under a state subdirectory."""
    return relative_path == state_subpath or relative_path.startswith(f"{state_subpath}/")


def _only_temporary_artifacts_uncommitted(artifacts: ArtifactStatus) -> bool:
    """Return whether only temporary preview/run/backup artifacts are uncommitted."""
    temporary_count = (
        artifacts.uncommitted_previews + artifacts.uncommitted_runs + artifacts.uncommitted_backups
    )
    return (
        temporary_count > 0
        and not artifacts.uncommitted_durable
        and not artifacts.uncommitted_other
    )


def _synthesis_cache_needs_render_check(artifacts: ArtifactStatus) -> bool:
    """Return whether cache changes exist without matching render output changes."""
    return artifacts.uncommitted_synthesis_cache > 0 and artifacts.uncommitted_render_outputs == 0


def _changed_candidate_count(plan: SynthesisPlanStatus) -> int:
    """Return the number of synthesis candidates needing work."""
    if plan.new is None and plan.stale is None:
        return 0
    return (plan.new or 0) + (plan.stale or 0)


def _presence_label(present: bool) -> str:
    """Return a short presence label for text reports."""
    return "present" if present else "missing"
