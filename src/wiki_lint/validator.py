"""Validate generated wiki markdown against shared wiki_contract rules."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.wiki_contract.categories import (
    CATEGORY_BY_FRONTMATTER,
    MERGED_GRAPH_CATEGORIES,
    spec_for_frontmatter,
)
from src.wiki_contract.frontmatter import required_fields_for
from src.wiki_contract.headings import (
    EVIDENCE_SECTION_HEADING,
    SOURCE_FULL_TEXT_HEADING,
    SYNTHESIS_EVIDENCE_INDEX_HEADING,
    required_h2_headings_for,
)
from src.wiki_contract.layout import is_lint_skipped_path

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
HEADING_RE = re.compile(r"^(##+)\s+(.+?)\s*$", re.MULTILINE)
MONTHLY_PATH_RE = re.compile(r"^[^/]+/(?:\d{4}-\d{2}|unknown)/[^/]+\.md$")


@dataclass(frozen=True)
class WikiLintIssue:
    """One wiki validation finding."""

    path: str
    message: str


@dataclass(frozen=True)
class WikiPage:
    """Parsed wiki markdown page."""

    path: Path
    relpath: str
    frontmatter: dict[str, Any]
    body: str

    @property
    def category(self) -> str | None:
        """Return frontmatter ``category`` if present."""
        value = self.frontmatter.get("category")
        return str(value) if isinstance(value, str) else None


def parse_frontmatter_value(raw: str) -> str | list[str]:
    """Parse the scalar/list subset of YAML used by this wiki."""
    text = raw.strip()
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        if not inner:
            return []
        return [part.strip().strip("\"'") for part in inner.split(",")]
    return text.strip("\"'")


def parse_markdown(path: Path, wiki_root: Path) -> WikiPage:
    """Parse frontmatter and body from one markdown file."""
    text = path.read_text(encoding="utf-8")
    frontmatter: dict[str, Any] = {}
    body = text
    if text.startswith("---\n"):
        try:
            _start, yaml_text, body = text.split("---\n", maxsplit=2)
        except ValueError:
            yaml_text = ""
        current_list_key: str | None = None
        for line in yaml_text.splitlines():
            if not line.strip():
                continue
            if line.startswith("  - ") and current_list_key is not None:
                values = frontmatter.setdefault(current_list_key, [])
                if isinstance(values, list):
                    values.append(line[4:].strip().strip("\"'"))
                continue
            if ":" not in line:
                current_list_key = None
                continue
            key, value = line.split(":", maxsplit=1)
            key = key.strip()
            value = value.strip()
            if value:
                frontmatter[key] = parse_frontmatter_value(value)
                current_list_key = None
            else:
                frontmatter[key] = []
                current_list_key = key
    return WikiPage(
        path=path,
        relpath=path.relative_to(wiki_root).as_posix(),
        frontmatter=frontmatter,
        body=body,
    )


def extract_headings(body: str, *, level: int = 2) -> list[str]:
    """Return headings at the requested markdown level without hashes."""
    return [
        match.group(2).strip()
        for match in HEADING_RE.finditer(body)
        if len(match.group(1)) == level
    ]


def extract_managed_h2_headings(body: str, *, stop_after: str) -> list[str]:
    """Return level-2 headings from the managed prefix ending at ``stop_after``.

    Headings that appear after the ``stop_after`` section heading are ignored so
    embedded raw source Markdown can contain its own ``##`` headings.
    """
    headings: list[str] = []
    for match in HEADING_RE.finditer(body):
        if len(match.group(1)) != 2:
            continue
        heading = match.group(2).strip()
        headings.append(heading)
        if heading == stop_after:
            break
    return headings


def managed_source_lint_body(
    body: str,
    *,
    stop_before: str = SOURCE_FULL_TEXT_HEADING,
) -> str:
    """Return the managed source-page body prefix before embedded raw text."""
    pattern = rf"^##\s+{re.escape(stop_before)}\s*$"
    match = re.search(pattern, body, re.MULTILINE)
    if match is None:
        return body
    return body[: match.start()]


def extract_wikilinks(body: str) -> list[str]:
    """Return wikilink targets from markdown body."""
    return [match.group(1).strip() for match in WIKILINK_RE.finditer(body)]


def read_wiki_pages(wiki_root: Path, *, include_non_managed: bool = False) -> dict[str, WikiPage]:
    """Read markdown files below ``wiki_root`` keyed by relative path."""
    pages: dict[str, WikiPage] = {}
    for path in sorted(wiki_root.rglob("*.md")):
        page = parse_markdown(path, wiki_root)
        if not include_non_managed and is_lint_skipped_path(page.relpath):
            continue
        pages[page.relpath] = page
    return pages


def validate_wiki(wiki_root: Path, *, include_non_managed: bool = False) -> list[WikiLintIssue]:
    """Validate generated wiki markdown files below ``wiki_root``."""
    pages = read_wiki_pages(wiki_root, include_non_managed=include_non_managed)
    issues: list[WikiLintIssue] = []
    for page in pages.values():
        issues.extend(validate_page(page, pages))
    return sorted(issues, key=lambda issue: (issue.path, issue.message))


def validate_page(page: WikiPage, pages: dict[str, WikiPage]) -> list[WikiLintIssue]:
    """Validate one page against shared contracts."""
    issues: list[WikiLintIssue] = []
    category = page.category
    if category is None:
        issues.append(WikiLintIssue(page.relpath, "missing frontmatter category"))
        return issues
    if category not in CATEGORY_BY_FRONTMATTER:
        issues.append(WikiLintIssue(page.relpath, f"unsupported category: {category}"))
        return issues

    for key in required_fields_for(category):
        if not page.frontmatter.get(key):
            issues.append(WikiLintIssue(page.relpath, f"missing frontmatter key: {key}"))

    issues.extend(_validate_derived_paths(page))
    issues.extend(_validate_headings(page))
    issues.extend(_validate_path_shape(page))
    issues.extend(_validate_merged_sections(page))
    issues.extend(validate_wikilinks(page, pages))
    return issues


def _validate_derived_paths(page: WikiPage) -> list[WikiLintIssue]:
    """Ensure derived metadata values are repo-relative markdown paths."""
    issues: list[WikiLintIssue] = []
    for key, value in page.frontmatter.items():
        if not key.startswith("derived_"):
            continue
        if key == "derived_pages":
            paths = value if isinstance(value, list) else []
        else:
            paths = value if isinstance(value, list) else []
        for entry in paths:
            text = str(entry).strip()
            if not text.endswith(".md"):
                issues.append(
                    WikiLintIssue(page.relpath, f"{key} value must be a .md path: {text}")
                )
            if text.startswith("/") or text.startswith("wiki/"):
                issues.append(
                    WikiLintIssue(page.relpath, f"{key} value must be wiki-relative: {text}")
                )
    return issues


def _validate_headings(page: WikiPage) -> list[WikiLintIssue]:
    """Validate fixed heading contracts when defined."""
    category = page.category
    if category is None:
        return []
    expected = required_h2_headings_for(category)
    if expected is None:
        return []
    if category == "source":
        actual = extract_managed_h2_headings(
            page.body,
            stop_after=SOURCE_FULL_TEXT_HEADING,
        )
    else:
        actual = extract_headings(page.body)
    if actual != list(expected):
        return [
            WikiLintIssue(
                page.relpath, f"unexpected h2 headings: {actual}; expected {list(expected)}"
            )
        ]
    return []


def _validate_path_shape(page: WikiPage) -> list[WikiLintIssue]:
    """Validate evidence page monthly path layout."""
    category = page.category
    if category is None:
        return []
    spec = spec_for_frontmatter(category)
    if not spec.uses_monthly_path:
        return []
    if not MONTHLY_PATH_RE.match(page.relpath):
        return [
            WikiLintIssue(
                page.relpath,
                f"expected monthly path {spec.folder}/YYYY-MM/<basename>.md",
            )
        ]
    return []


def _validate_merged_sections(page: WikiPage) -> list[WikiLintIssue]:
    """Validate merged knowledge page body sections."""
    category = page.category
    if category is None:
        return []
    graph_category = spec_for_frontmatter(category).graph_category
    if graph_category not in MERGED_GRAPH_CATEGORIES:
        return []
    issues: list[WikiLintIssue] = []
    required_evidence_heading = _required_evidence_heading(page)
    if required_evidence_heading not in page.body:
        issues.append(WikiLintIssue(page.relpath, f"missing section: {required_evidence_heading}"))
    source_count = page.frontmatter.get("source_count")
    source_ids = page.frontmatter.get("source_ids")
    if isinstance(source_count, int) and source_count >= 1:
        if not isinstance(source_ids, list) or not source_ids:
            issues.append(WikiLintIssue(page.relpath, "source_ids required when source_count >= 1"))
    return issues


def _required_evidence_heading(page: WikiPage) -> str:
    """Return the evidence heading expected for a merged knowledge page."""
    if page.frontmatter.get("synthesis_state") in {"synthesized", "stale"}:
        return SYNTHESIS_EVIDENCE_INDEX_HEADING
    return EVIDENCE_SECTION_HEADING


def validate_wikilinks(page: WikiPage, pages: dict[str, WikiPage]) -> list[WikiLintIssue]:
    """Validate that wikilink targets resolve to markdown files where appropriate."""
    body = page.body
    if page.category == "source":
        body = managed_source_lint_body(body)
    issues: list[WikiLintIssue] = []
    for target in extract_wikilinks(body):
        normalized = normalize_wikilink_target(target)
        if normalized is None:
            continue
        candidates = [f"{normalized}.md", f"{normalized}/index.md"]
        if not any(candidate in pages for candidate in candidates):
            issues.append(WikiLintIssue(page.relpath, f"broken wikilink: [[{target}]]"))
    return issues


def normalize_wikilink_target(target: str) -> str | None:
    """Normalize a wikilink target to a wiki-root relative path or None to skip."""
    clean = target.strip().strip("/")
    if not clean or clean.startswith("http"):
        return None
    if clean.startswith("wiki/"):
        clean = clean.removeprefix("wiki/")
    if clean.endswith(".md"):
        clean = clean.removesuffix(".md")
    if "/" not in clean:
        return None
    return clean
