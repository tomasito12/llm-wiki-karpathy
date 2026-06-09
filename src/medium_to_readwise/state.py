"""Persistent state helpers for Medium to Readwise automation."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.ingest_review.paths import repo_root
from src.medium_to_readwise.urls import filter_article_urls, normalize_article_url
from src.pipeline.atomic import atomic_write_json

ARTICLES_FILE = "articles.json"
PROCESSED_FILE = "processed.json"
RUN_LOG_FILE = "run.log"
SCREENSHOTS_DIR = "screenshots"


def utc_now_iso() -> str:
    """Return the current UTC timestamp in second-precision ISO format."""
    return datetime.now(tz=UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_state_dir() -> Path:
    """Return the default local progress directory."""
    return repo_root() / "state" / "medium_to_readwise"


def ensure_state_dir(state_dir: Path) -> None:
    """Create the state directory and screenshot subdirectory if needed."""
    (state_dir / SCREENSHOTS_DIR).mkdir(parents=True, exist_ok=True)


def load_json_object(path: Path, *, default: dict[str, Any]) -> dict[str, Any]:
    """Load a JSON object from ``path`` or return ``default`` when missing."""
    if not path.exists():
        return default
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return payload


def load_article_state(state_dir: Path) -> dict[str, Any]:
    """Load persisted article discovery state."""
    return load_json_object(
        state_dir / ARTICLES_FILE,
        default={"discovered_at": None, "reading_list_url": "", "urls": []},
    )


def save_article_state(state_dir: Path, *, reading_list_url: str, urls: list[str]) -> None:
    """Persist discovered article URLs atomically."""
    ensure_state_dir(state_dir)
    payload = {
        "discovered_at": utc_now_iso(),
        "reading_list_url": reading_list_url,
        "urls": filter_article_urls(urls),
    }
    atomic_write_json(state_dir / ARTICLES_FILE, payload)


def load_processed_state(state_dir: Path) -> dict[str, Any]:
    """Load processed URL state."""
    return load_json_object(state_dir / PROCESSED_FILE, default={"entries": []})


def processed_entries(state_dir: Path) -> list[dict[str, Any]]:
    """Return processed entries from local state."""
    state = load_processed_state(state_dir)
    entries = state.get("entries", [])
    if not isinstance(entries, list):
        raise ValueError(f"Expected list at entries in {state_dir / PROCESSED_FILE}")
    return [entry for entry in entries if isinstance(entry, dict)]


def save_processed_entries(state_dir: Path, entries: list[dict[str, Any]]) -> None:
    """Persist processed entries atomically."""
    ensure_state_dir(state_dir)
    atomic_write_json(state_dir / PROCESSED_FILE, {"entries": entries})


def append_run_log(state_dir: Path, message: str) -> None:
    """Append one timestamped line to the run log."""
    ensure_state_dir(state_dir)
    with (state_dir / RUN_LOG_FILE).open("a", encoding="utf-8") as log_file:
        log_file.write(f"{utc_now_iso()} {message}\n")


def merge_article_urls(previous_urls: list[str], discovered_urls: list[str]) -> list[str]:
    """Merge prior and newly discovered article URLs without losing old discoveries."""
    return filter_article_urls([*previous_urls, *discovered_urls])


def completed_url_keys(entries: list[dict[str, Any]]) -> set[str]:
    """Return normalized URL keys for entries marked as successfully processed."""
    keys: set[str] = set()
    for entry in entries:
        if entry.get("status") != "ok":
            continue
        url = str(entry.get("canonical_url") or entry.get("url") or "")
        if url:
            keys.add(normalize_article_url(url))
    return keys


def failed_url_keys(entries: list[dict[str, Any]]) -> set[str]:
    """Return normalized URL keys for entries whose last status is failed."""
    latest_by_url: dict[str, str] = {}
    for entry in entries:
        url = str(entry.get("canonical_url") or entry.get("url") or "")
        if url:
            latest_by_url[normalize_article_url(url)] = str(entry.get("status") or "")
    return {url for url, status in latest_by_url.items() if status == "failed"}


def pending_urls(
    urls: list[str],
    entries: list[dict[str, Any]],
    *,
    retry_failed: bool = True,
) -> list[str]:
    """Return URLs that should still be processed."""
    completed = completed_url_keys(entries)
    failed = failed_url_keys(entries)
    pending: list[str] = []
    for url in filter_article_urls(urls):
        key = normalize_article_url(url)
        if key in completed:
            continue
        if not retry_failed and key in failed:
            continue
        pending.append(url)
    return pending


def upsert_processed_entry(
    entries: list[dict[str, Any]], new_entry: dict[str, Any]
) -> list[dict[str, Any]]:
    """Return entries with the latest record for ``new_entry`` replacing prior rows."""
    url = str(new_entry.get("canonical_url") or new_entry.get("url") or "")
    if not url:
        return [*entries, new_entry]
    key = normalize_article_url(url)
    replaced = False
    updated: list[dict[str, Any]] = []
    for entry in entries:
        entry_url = str(entry.get("canonical_url") or entry.get("url") or "")
        if entry_url and normalize_article_url(entry_url) == key:
            if not replaced:
                updated.append(new_entry)
                replaced = True
            continue
        updated.append(entry)
    if not replaced:
        updated.append(new_entry)
    return updated


def screenshot_path(state_dir: Path, *, url: str, timestamp: str | None = None) -> Path:
    """Return a filesystem-safe screenshot path for ``url``."""
    stamp = timestamp or utc_now_iso().replace(":", "")
    safe = normalize_article_url(url).replace("https://", "").replace("http://", "")
    safe = "".join(char if char.isalnum() else "-" for char in safe).strip("-")
    while "--" in safe:
        safe = safe.replace("--", "-")
    safe = safe[:80] or "article"
    return state_dir / SCREENSHOTS_DIR / f"{safe}-{stamp}.png"
