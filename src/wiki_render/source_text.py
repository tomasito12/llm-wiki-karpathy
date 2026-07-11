"""Load raw source Markdown for generated source pages."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from src.wiki_render.models import RenderedFile, SourceRecord

MISSING_SOURCE_TEXT_PLACEHOLDER = (
    "Full source text is not available locally. Raw metadata is listed above."
)
DEFAULT_MIN_SOURCE_TEXT_AVAILABLE_RATIO = 0.5


@dataclass(frozen=True)
class SourceText:
    """Resolved full source text for one source page."""

    available: bool
    text: str
    mode: str
    source: str


@dataclass(frozen=True)
class SourceTextCoverage:
    """Availability counts for rendered source pages."""

    total: int
    available: int
    missing: int

    @property
    def available_ratio(self) -> float:
        """Return the fraction of source pages with full text available."""
        if self.total == 0:
            return 1.0
        return self.available / self.total


def load_raw_source_markdown(
    source: SourceRecord,
    *,
    raw_dir: Path,
    repo_root: Path | None = None,
) -> SourceText:
    """Load raw Markdown for a source from configured raw paths.

    Resolution order:

    1. ``raw_dir / "<source_id>.md"``
    2. ``repo_root / raw_md_rel_path`` when ``raw_md_rel_path`` is set

    Args:
        source: Reviewed source record to load text for.
        raw_dir: Configured raw Readwise export directory.
        repo_root: Optional repository root for ``raw_md_rel_path`` fallback.

    Returns:
        :class:`SourceText` with availability metadata and body text.
    """
    candidates: list[Path] = [raw_dir / f"{source.source_id}.md"]
    if repo_root is not None and source.raw_md_rel_path:
        candidates.append((repo_root / source.raw_md_rel_path).resolve())
    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if resolved.is_file():
            return SourceText(
                available=True,
                text=resolved.read_text(encoding="utf-8"),
                mode="full",
                source="raw_markdown",
            )
    return SourceText(
        available=False,
        text=MISSING_SOURCE_TEXT_PLACEHOLDER,
        mode="missing",
        source="none",
    )


def summarize_source_text_coverage(files: list[RenderedFile]) -> SourceTextCoverage:
    """Count how many rendered source pages include full raw text."""
    total = 0
    available = 0
    for file in files:
        if not file.relative_path.startswith("sources/"):
            continue
        total += 1
        frontmatter = _parse_frontmatter(file.text)
        if frontmatter.get("source_text_available") is True:
            available += 1
    return SourceTextCoverage(
        total=total,
        available=available,
        missing=total - available,
    )


def evaluate_source_text_coverage(
    coverage: SourceTextCoverage,
    *,
    min_available_ratio: float = DEFAULT_MIN_SOURCE_TEXT_AVAILABLE_RATIO,
) -> str | None:
    """Return a warning message when source full text coverage is suspiciously low."""
    if coverage.total == 0:
        return None
    if coverage.available_ratio >= min_available_ratio:
        return None
    return (
        "Low source full-text coverage: "
        f"{coverage.available}/{coverage.total} source pages have source_text_available=true "
        f"({coverage.available_ratio:.1%}). "
        "Check --raw-dir, --paths-config, or LLM_WIKI_PATHS_CONFIG. "
        "Use --require-source-text to fail instead of continuing."
    )


def _parse_frontmatter(text: str) -> dict[str, object]:
    """Parse YAML frontmatter from a rendered markdown document."""
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    payload = yaml.safe_load(parts[1])
    if not isinstance(payload, dict):
        return {}
    return payload
