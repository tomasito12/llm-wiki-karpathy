"""Load Readwise export pairs: HTML body + markdown frontmatter metadata."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from bs4 import BeautifulSoup

from src.pipeline.source_publication import resolve_publication

# Hash the same conceptual content as ingest manifest: UTF-8 normalized extracted text
# from HTML (whitespace-collapsed lines) so small HTML wrapper changes still correlate.


def _normalize_extracted_text(text: str) -> str:
    """Collapse whitespace for stable hashing and size limits."""
    lines = [ln.strip() for ln in text.splitlines()]
    return "\n".join(ln for ln in lines if ln)


def html_body_to_plain_text(html: str, *, max_chars: int | None = None) -> str:
    """Extract human-readable plain text from HTML using BeautifulSoup.

    Args:
        html: Raw HTML document string.
        max_chars: If set, truncate normalized text to this length and append
            a ``\\n[TRUNCATED]`` marker.

    Returns:
        Normalized plain text suitable for LLM prompts and hashing.
    """
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator="\n", strip=True)
    normalized = _normalize_extracted_text(text)
    if max_chars is not None and len(normalized) > max_chars:
        return normalized[:max_chars] + "\n[TRUNCATED]"
    return normalized


def content_sha256_from_plain_text(plain_text: str) -> str:
    """Return SHA-256 hex digest of UTF-8 encoded normalized plain text."""
    return hashlib.sha256(plain_text.encode("utf-8")).hexdigest()


_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL | re.MULTILINE)


def parse_markdown_frontmatter(md_text: str) -> tuple[dict[str, Any], str]:
    """Split YAML frontmatter from markdown body.

    Returns:
        ``(metadata_dict, body_after_frontmatter)``. If no frontmatter, returns
        ``({}, full_text)``.
    """
    match = _FRONTMATTER_RE.match(md_text)
    if not match:
        return {}, md_text
    raw_yaml = match.group(1)
    try:
        meta = yaml.safe_load(raw_yaml) or {}
    except yaml.YAMLError:
        meta = {}
    if not isinstance(meta, dict):
        meta = {}
    rest = md_text[match.end() :]
    return meta, rest


@dataclass(frozen=True)
class SourceDocument:
    """One Readwise export identified by basename (``source_id``)."""

    source_id: str
    raw_html_path: Path
    raw_md_path: Path
    frontmatter: dict[str, Any]
    md_body: str
    plain_text: str
    content_sha256: str

    @property
    def canonical_url(self) -> str | None:
        """URL from Readwise metadata when present."""
        url = self.frontmatter.get("source_url")
        return str(url) if url else None

    @property
    def title(self) -> str | None:
        """Article title from frontmatter when present."""
        t = self.frontmatter.get("title")
        return str(t) if t else None

    @property
    def author(self) -> str | None:
        """Author from frontmatter when present."""
        a = self.frontmatter.get("author")
        return str(a) if a else None

    @property
    def published_date(self) -> str | None:
        """Publication date string from frontmatter when present."""
        d = self.frontmatter.get("published_date")
        return str(d) if d else None

    @property
    def publication(self) -> str | None:
        """Venue/platform from frontmatter, Readwise ``site_name``, or URL inference."""
        explicit = self.frontmatter.get("publication")
        if explicit is not None and str(explicit).strip():
            return str(explicit).strip()
        site = self.frontmatter.get("site_name")
        site_str = str(site).strip() if site else None
        return resolve_publication(site_str, self.canonical_url, author=self.author)


def load_readwise_pair(
    raw_html_path: Path,
    *,
    max_plain_text_chars: int | None = 120_000,
) -> SourceDocument:
    """Load HTML + sibling markdown for one Readwise export.

    Args:
        raw_html_path: Path to ``*.html`` under ``raw/readwise/``.
        max_plain_text_chars: Passed to :func:`html_body_to_plain_text`.

    Raises:
        FileNotFoundError: If HTML or sibling ``.md`` is missing.
    """
    raw_html_path = raw_html_path.resolve()
    if not raw_html_path.is_file():
        raise FileNotFoundError(f"HTML not found: {raw_html_path}")
    source_id = raw_html_path.stem
    raw_md_path = raw_html_path.with_suffix(".md")
    if not raw_md_path.is_file():
        raise FileNotFoundError(f"Markdown sidecar not found: {raw_md_path}")
    html = raw_html_path.read_text(encoding="utf-8", errors="replace")
    md_text = raw_md_path.read_text(encoding="utf-8", errors="replace")
    frontmatter, md_body = parse_markdown_frontmatter(md_text)
    plain = html_body_to_plain_text(html, max_chars=max_plain_text_chars)
    digest = content_sha256_from_plain_text(plain)
    return SourceDocument(
        source_id=source_id,
        raw_html_path=raw_html_path,
        raw_md_path=raw_md_path,
        frontmatter=frontmatter,
        md_body=md_body.strip(),
        plain_text=plain,
        content_sha256=digest,
    )


def list_readwise_html_sources(raw_dir: Path) -> list[Path]:
    """Return sorted ``*.html`` paths under ``raw_dir``."""
    if not raw_dir.is_dir():
        return []
    return sorted(raw_dir.glob("*.html"))


def readwise_source_status(html_path: Path) -> str:
    """Return ``complete`` if sibling ``.md`` exists, else ``incomplete``."""
    return "complete" if html_path.with_suffix(".md").is_file() else "incomplete"
