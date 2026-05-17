"""Resolve publication (venue) labels from Readwise fields and source URLs."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

import yaml

from src.pipeline.atomic import atomic_write_text

_HOST_PUBLICATION: dict[str, str] = {
    "medium.com": "Medium",
    "substack.com": "Substack",
    "openai.com": "OpenAI",
    "anthropic.com": "Anthropic",
    "arxiv.org": "arXiv",
    "github.com": "GitHub",
    "huggingface.co": "Hugging Face",
    "techcrunch.com": "TechCrunch",
    "theverge.com": "The Verge",
    "wired.com": "WIRED",
    "nytimes.com": "The New York Times",
    "wsj.com": "The Wall Street Journal",
    "ieee.org": "IEEE",
    "spectrum.ieee.org": "IEEE Spectrum",
    "technologyreview.com": "MIT Technology Review",
    "venturebeat.com": "VentureBeat",
    "theinformation.com": "The Information",
    "semianalysis.com": "SemiAnalysis",
    "lesswrong.com": "LessWrong",
    "simonwillison.net": "Simon Willison's Weblog",
}

_SUFFIX_PUBLICATION: dict[str, str] = {
    "medium.com": "Medium",
    "substack.com": "Substack",
    "openai.com": "OpenAI",
    "anthropic.com": "Anthropic",
    "arxiv.org": "arXiv",
    "github.io": "GitHub Pages",
}

_TOKEN_LABELS: dict[str, str] = {
    "ieee": "IEEE",
    "arxiv": "arXiv",
    "ai": "AI",
    "ml": "ML",
}


def _host_from_url(source_url: str | None) -> str | None:
    if not source_url or not str(source_url).strip():
        return None
    parsed = urlparse(str(source_url).strip())
    host = (parsed.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    return host or None


def _author_matches_site(site: str, author: str | None) -> bool:
    if not author:
        return False
    return site.strip().casefold() == author.strip().casefold()


def derive_publication_from_url(source_url: str | None) -> str | None:
    """Infer a venue label from *source_url* when Readwise does not provide ``site_name``."""
    host = _host_from_url(source_url)
    if not host:
        return None
    if host in _HOST_PUBLICATION:
        return _HOST_PUBLICATION[host]
    for suffix, label in _SUFFIX_PUBLICATION.items():
        if host == suffix or host.endswith(f".{suffix}"):
            return label
    parts = host.split(".")
    if len(parts) < 2:
        return None
    tld = parts[-1]
    common_tlds = {"com", "org", "net", "io", "ai", "co", "uk", "de"}
    label_token = parts[-2] if tld in common_tlds else parts[0]
    if label_token in {"www", "blog", "news", "m", "amp"}:
        return None
    if label_token in _TOKEN_LABELS:
        return _TOKEN_LABELS[label_token]
    if len(label_token) <= 2:
        return None
    return label_token.replace("-", " ").title()


def resolve_publication(
    site_name: str | None,
    source_url: str | None,
    *,
    author: str | None = None,
) -> str | None:
    """Return best publication/venue label from Readwise ``site_name`` and/or URL."""
    if site_name is not None:
        site = str(site_name).strip()
        if site and not _author_matches_site(site, author):
            return site
    return derive_publication_from_url(source_url)


def _format_md_with_frontmatter(frontmatter: dict[str, object], body: str) -> str:
    dumped = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False, allow_unicode=True)
    body_text = body.lstrip("\n")
    if body_text and not body_text.endswith("\n"):
        body_text += "\n"
    return f"---\n{dumped}---\n\n{body_text}"


def backfill_publication_in_md_file(md_path: Path) -> bool:
    """Set or refresh ``publication`` in a Readwise sidecar when derivable.

    Returns True when the file was rewritten.
    """
    from src.ingest_review.extract import parse_markdown_frontmatter

    text = md_path.read_text(encoding="utf-8")
    frontmatter, body = parse_markdown_frontmatter(text)
    if not frontmatter:
        return False

    source_url = frontmatter.get("source_url")
    url_str = str(source_url) if source_url else None
    author_raw = frontmatter.get("author")
    author = str(author_raw) if author_raw else None

    resolved = resolve_publication(
        frontmatter.get("site_name") or frontmatter.get("publication"),
        url_str,
        author=author,
    )
    if not resolved:
        return False

    existing = frontmatter.get("publication")
    if existing is not None and str(existing).strip() == resolved:
        return False

    frontmatter["publication"] = resolved
    if "site_name" in frontmatter and str(frontmatter.get("site_name") or "").strip() == resolved:
        del frontmatter["site_name"]

    atomic_write_text(md_path, _format_md_with_frontmatter(frontmatter, body))
    return True


def backfill_publications_in_raw_dir(raw_dir: Path) -> tuple[int, int]:
    """Backfill ``publication`` on all ``*.md`` sidecars under *raw_dir*.

    Returns ``(updated_count, skipped_count)``.
    """
    if not raw_dir.is_dir():
        return 0, 0
    updated = 0
    skipped = 0
    for md_path in sorted(raw_dir.glob("*.md")):
        if backfill_publication_in_md_file(md_path):
            updated += 1
        else:
            skipped += 1
    return updated, skipped
