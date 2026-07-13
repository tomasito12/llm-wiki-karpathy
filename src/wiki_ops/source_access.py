"""Verify local full-text access through the generated private vault."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

from src.wiki_contract.layout import is_managed_relative_path
from src.wiki_render.source_text import MISSING_SOURCE_TEXT_PLACEHOLDER

FULL_SOURCE_TEXT_HEADING = "## Full source text"
SOURCE_WIKILINK_PATTERN = re.compile(r"\[\[(?P<target>sources/[^|\]#]+)(?:[|#][^\]]*)?\]\]")
LOCAL_RAW_LINK_PATTERNS = (
    re.compile(r"\[\[[^|\]]*raw/readwise/[^|\]]+\.md(?:\|[^\]]*)?\]\]"),
    re.compile(r"\[[^\]]+\]\((?:file://|\.\.?/)[^)]*raw/readwise/[^)]+\.md\)"),
)


@dataclass(frozen=True)
class SourceAccessStatus:
    """Coverage and integrity facts for local source-text access."""

    wiki_dir_exists: bool
    source_pages_total: int
    embedded_full_text: int
    locally_linked_source_text: int
    external_url_only: int
    malformed_pages: list[str]
    source_id_mismatches: list[str]
    source_pages_missing_raw_markdown: list[str]
    graph_sources: int | None
    graph_sources_missing_pages: list[str]
    source_links_total: int
    broken_source_link_targets: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable source-access report."""
        return asdict(self)


def collect_source_access_status(
    *,
    wiki_dir: Path,
    raw_dir: Path,
    graph_path: Path,
) -> tuple[SourceAccessStatus, list[str]]:
    """Inspect generated source pages and return coverage with warnings.

    Args:
        wiki_dir: Generated wiki output root.
        raw_dir: Canonical Readwise raw export directory.
        graph_path: Current wiki-render graph export.

    Returns:
        A source-access status snapshot and actionable warning messages.
    """
    if not wiki_dir.is_dir():
        status = SourceAccessStatus(
            wiki_dir_exists=False,
            source_pages_total=0,
            embedded_full_text=0,
            locally_linked_source_text=0,
            external_url_only=0,
            malformed_pages=[],
            source_id_mismatches=[],
            source_pages_missing_raw_markdown=[],
            graph_sources=None,
            graph_sources_missing_pages=[],
            source_links_total=0,
            broken_source_link_targets=[],
        )
        return status, [f"Source access cannot be verified; wiki directory missing: {wiki_dir}"]

    source_dir = wiki_dir / "sources"
    source_pages = sorted(source_dir.glob("*.md")) if source_dir.is_dir() else []
    page_ids: set[str] = set()
    embedded_full_text = 0
    locally_linked_source_text = 0
    external_url_only = 0
    malformed_pages: list[str] = []
    source_id_mismatches: list[str] = []
    missing_raw_markdown: list[str] = []

    for page_path in source_pages:
        relative_path = page_path.relative_to(wiki_dir).as_posix()
        try:
            text = page_path.read_text(encoding="utf-8")
            frontmatter = _parse_frontmatter(text)
        except (OSError, UnicodeError, yaml.YAMLError, ValueError):
            malformed_pages.append(relative_path)
            continue
        source_id = str(frontmatter.get("source_id") or "").strip()
        if not source_id:
            malformed_pages.append(relative_path)
            continue
        page_ids.add(source_id)
        if page_path.stem != source_id:
            source_id_mismatches.append(relative_path)
        if not (raw_dir / f"{source_id}.md").is_file():
            missing_raw_markdown.append(relative_path)
        if _has_embedded_full_text(text, frontmatter):
            embedded_full_text += 1
        elif _has_local_raw_link(text):
            locally_linked_source_text += 1
        else:
            external_url_only += 1

    graph_source_ids = _load_graph_source_ids(graph_path)
    missing_graph_pages = (
        sorted(graph_source_ids - page_ids) if graph_source_ids is not None else []
    )
    source_links_total, broken_link_targets = _inspect_source_links(
        wiki_dir=wiki_dir,
        page_ids=page_ids,
    )
    status = SourceAccessStatus(
        wiki_dir_exists=True,
        source_pages_total=len(source_pages),
        embedded_full_text=embedded_full_text,
        locally_linked_source_text=locally_linked_source_text,
        external_url_only=external_url_only,
        malformed_pages=malformed_pages,
        source_id_mismatches=source_id_mismatches,
        source_pages_missing_raw_markdown=missing_raw_markdown,
        graph_sources=len(graph_source_ids) if graph_source_ids is not None else None,
        graph_sources_missing_pages=missing_graph_pages,
        source_links_total=source_links_total,
        broken_source_link_targets=broken_link_targets,
    )
    return status, _build_source_access_warnings(status, graph_path=graph_path)


def _parse_frontmatter(text: str) -> dict[str, object]:
    """Parse and validate YAML frontmatter from a generated source page."""
    if not text.startswith("---"):
        raise ValueError("missing YAML frontmatter")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("unterminated YAML frontmatter")
    payload = yaml.safe_load(parts[1])
    if not isinstance(payload, dict):
        raise ValueError("frontmatter is not a mapping")
    return payload


def _has_embedded_full_text(text: str, frontmatter: dict[str, object]) -> bool:
    """Return whether metadata and page content confirm embedded full text."""
    if frontmatter.get("source_text_available") is not True:
        return False
    _, separator, body = text.partition(FULL_SOURCE_TEXT_HEADING)
    if not separator:
        return False
    content = body.strip()
    return bool(content and not content.startswith(MISSING_SOURCE_TEXT_PLACEHOLDER))


def _has_local_raw_link(text: str) -> bool:
    """Return whether a page contains a clickable local raw Markdown link."""
    return any(pattern.search(text) for pattern in LOCAL_RAW_LINK_PATTERNS)


def _load_graph_source_ids(graph_path: Path) -> set[str] | None:
    """Load source ids from the current render graph when available."""
    if not graph_path.is_file():
        return None
    try:
        payload = json.loads(graph_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict) or not isinstance(payload.get("sources"), list):
        return None
    source_ids: set[str] = set()
    for item in payload["sources"]:
        if not isinstance(item, dict):
            continue
        source_id = str(item.get("source_id") or "").strip()
        if source_id:
            source_ids.add(source_id)
    return source_ids


def _inspect_source_links(*, wiki_dir: Path, page_ids: set[str]) -> tuple[int, list[str]]:
    """Count source wikilinks outside source pages and identify broken targets."""
    link_count = 0
    broken_targets: set[str] = set()
    for page_path in sorted(wiki_dir.rglob("*.md")):
        try:
            relative_path = page_path.relative_to(wiki_dir)
        except ValueError:
            continue
        relative_text = relative_path.as_posix()
        if not is_managed_relative_path(relative_text) or relative_path.parts[0] == "sources":
            continue
        try:
            text = page_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        for match in SOURCE_WIKILINK_PATTERN.finditer(text):
            link_count += 1
            target = match.group("target").removesuffix(".md")
            source_id = Path(target).name
            if source_id not in page_ids:
                broken_targets.add(target)
    return link_count, sorted(broken_targets)


def _build_source_access_warnings(
    status: SourceAccessStatus,
    *,
    graph_path: Path,
) -> list[str]:
    """Return actionable warnings for incomplete source access."""
    warnings: list[str] = []
    if status.graph_sources is None:
        warnings.append(f"Source access graph comparison unavailable: {graph_path}")
    if status.malformed_pages:
        warnings.append(f"Source access: {len(status.malformed_pages)} source pages are malformed.")
    if status.source_id_mismatches:
        warnings.append(
            "Source access: "
            f"{len(status.source_id_mismatches)} source page filenames do not match source_id."
        )
    if status.source_pages_missing_raw_markdown:
        warnings.append(
            "Source access: "
            f"{len(status.source_pages_missing_raw_markdown)} source pages have no canonical "
            "raw Markdown file."
        )
    if status.external_url_only:
        warnings.append(
            "Source access: "
            f"{status.external_url_only} source pages expose neither embedded full text nor "
            "a local raw Markdown link."
        )
    if status.graph_sources_missing_pages:
        warnings.append(
            "Source access: "
            f"{len(status.graph_sources_missing_pages)} graph sources have no generated "
            "source page."
        )
    if status.broken_source_link_targets:
        warnings.append(
            "Source access: "
            f"{len(status.broken_source_link_targets)} source wikilink targets are broken."
        )
    return warnings
