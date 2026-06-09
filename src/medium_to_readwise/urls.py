"""URL normalization and filtering for Medium Reading List imports."""

from __future__ import annotations

import re
from collections.abc import Iterable
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit

ARTICLE_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*-[a-f0-9]{8,12}$", re.IGNORECASE)

IGNORED_HOSTS = {
    "help.medium.com",
    "policy.medium.com",
}

IGNORED_PATH_PREFIXES = (
    "/about",
    "/creators",
    "/jobs",
    "/membership",
    "/m/signin",
    "/m/signout",
    "/me/",
    "/new-story",
    "/plans",
    "/policy",
    "/search",
    "/sitemap/",
    "/tag/",
    "/topics",
)

TRACKING_QUERY_KEYS = {
    "fbclid",
    "gclid",
    "gi",
    "source",
    "sk",
}


def normalize_article_url(url: str, *, base_url: str = "https://medium.com") -> str:
    """Return a stable URL key by resolving relatives and removing tracking noise."""
    resolved = urljoin(base_url, url.strip())
    parts = urlsplit(resolved)
    query_items = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if not key.lower().startswith("utm_") and key.lower() not in TRACKING_QUERY_KEYS
    ]
    normalized_path = parts.path.rstrip("/") or "/"
    return urlunsplit(
        (
            parts.scheme.lower(),
            parts.netloc.lower(),
            normalized_path,
            urlencode(query_items, doseq=True),
            "",
        )
    )


def article_slug_from_path(path: str) -> str | None:
    """Return the final path segment when ``path`` points at a Medium article."""
    segments = [segment for segment in path.strip("/").split("/") if segment]
    if not segments:
        return None
    return segments[-1]


def has_article_slug(slug: str) -> bool:
    """Return whether ``slug`` matches Medium's article-id suffix pattern."""
    return bool(ARTICLE_SLUG_RE.match(slug))


def is_medium_host(host: str) -> bool:
    """Return whether ``host`` is ``medium.com`` or a user/publication subdomain."""
    normalized = host.lower()
    return normalized == "medium.com" or normalized.endswith(".medium.com")


def is_medium_article_url(url: str) -> bool:
    """Return whether ``url`` looks like a Medium article, not a profile or nav link."""
    parts = urlsplit(url)
    host = parts.netloc.lower()
    path = parts.path.rstrip("/")
    if parts.scheme not in {"http", "https"}:
        return False
    if not host or host in IGNORED_HOSTS or not is_medium_host(host):
        return False
    if any(path.startswith(prefix) for prefix in IGNORED_PATH_PREFIXES):
        return False
    if path in {"", "/", "/p", "/latest", "/feed", "/lists", "/library"}:
        return False
    if "/list/" in path:
        return False

    slug = article_slug_from_path(path)
    if slug is None or not has_article_slug(slug):
        return False

    segments = [segment for segment in path.strip("/").split("/") if segment]
    if host == "medium.com" and len(segments) < 2:
        return False
    return True


def dedupe_urls(urls: Iterable[str]) -> list[str]:
    """Return URLs in first-seen order after normalization-based dedupe."""
    seen: set[str] = set()
    deduped: list[str] = []
    for url in urls:
        normalized = normalize_article_url(url)
        if normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(normalized)
    return deduped


def filter_article_urls(urls: Iterable[str]) -> list[str]:
    """Return deduplicated Medium article URLs and drop profiles, nav, and external links."""
    return [url for url in dedupe_urls(urls) if is_medium_article_url(url)]
