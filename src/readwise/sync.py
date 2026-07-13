"""Orchestrate Reader list → ``raw/readwise`` export with index updates."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx

from src.readwise.client import iter_archive_processed_documents, reader_client
from src.readwise.export import sha256_hex, write_document_export
from src.readwise.library_index import LibraryIndex
from src.readwise.models import ReaderDocument

INITIAL_LOOKBACK_DAYS = 100


def resolved_updated_after_for_list(
    index: LibraryIndex,
    *,
    now: datetime | None = None,
) -> str:
    """Return the ``updatedAfter`` query value for the Reader list API.

    When the index has no stored watermark yet (first runs), use a timestamp
    approximately ``INITIAL_LOOKBACK_DAYS`` in the past so the first sync still
    receives a bounded window of documents instead of omitting the filter.
    """
    if index.last_updated_after is not None:
        return index.last_updated_after
    base = now if now is not None else datetime.now(tz=UTC)
    return (base - timedelta(days=INITIAL_LOOKBACK_DAYS)).isoformat()


def max_iso_timestamps(values: list[str | None]) -> str | None:
    """Return the latest ISO-like timestamp string, or None if empty."""
    parsed: list[tuple[datetime, str]] = []
    for raw in values:
        if not raw:
            continue
        text = raw.strip()
        if not text:
            continue
        try:
            normalized = text.replace("Z", "+00:00")
            dt = datetime.fromisoformat(normalized)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=UTC)
            parsed.append((dt.astimezone(UTC), text))
        except ValueError:
            parsed.append((datetime.min.replace(tzinfo=UTC), text))
    if not parsed:
        return None
    return max(parsed, key=lambda item: item[0])[1]


@dataclass(frozen=True)
class SyncResult:
    """Summary counters after a sync run."""

    examined: int
    exported: int
    skipped: int
    dry_run: bool
    incremental_filter_active: bool
    incremental_watermark: str | None


def _repo_root() -> Path:
    """Resolve repository root (directory containing ``state`` and ``raw``)."""
    return Path(__file__).resolve().parents[2]


def _consume_reader_documents(
    stream: Iterator[ReaderDocument],
    *,
    index: LibraryIndex,
    out_dir: Path,
    dry_run: bool,
    prune_missing: bool,
) -> tuple[int, int, int, list[str | None], bool]:
    """Apply export decisions for each document in ``stream``.

    Returns ``(examined, exported, skipped, seen_updated, index_dirty)``.
    """
    examined = 0
    exported = 0
    skipped = 0
    seen_updated: list[str | None] = []
    index_dirty = False
    for doc in stream:
        examined += 1
        seen_updated.append(doc.updated_at)
        if not _needs_export(
            doc_id=doc.id,
            doc_updated_at=doc.updated_at,
            doc_html=doc.html_content,
            index=index,
            out_dir=out_dir,
            prune_missing=prune_missing,
        ):
            skipped += 1
            continue
        exported += 1
        if dry_run:
            continue
        record, _, _ = write_document_export(doc, out_dir)
        index.documents[doc.id] = record
        index_dirty = True
    return examined, exported, skipped, seen_updated, index_dirty


def _needs_export(
    *,
    doc_id: str,
    doc_updated_at: str | None,
    doc_html: str | None,
    index: LibraryIndex,
    out_dir: Path,
    prune_missing: bool,
) -> bool:
    """Return True if this document should be written to disk."""
    if doc_id in index.suppressed_ids:
        return False
    existing = index.documents.get(doc_id)
    if existing is None:
        return True
    if doc_updated_at != existing.updated_at:
        return True
    if doc_html and existing.content_sha256:
        if sha256_hex(doc_html) != existing.content_sha256:
            return True
    if prune_missing:
        html_path = out_dir / Path(existing.html_path).name
        md_path = out_dir / Path(existing.md_path).name
        if not html_path.is_file() or not md_path.is_file():
            return True
    return False


def run_sync(
    token: str,
    *,
    index_path: Path | None = None,
    output_dir: Path | None = None,
    repo_root: Path | None = None,
    dry_run: bool = False,
    prune_missing: bool = False,
    reset_watermark: bool = False,
    client: httpx.Client | None = None,
) -> SyncResult:
    """List archive+processed documents and export new or updated ones.

    When ``client`` is provided (for tests), it is used instead of building one
    from ``token``; the caller must still pass a valid token string (may be empty).
    """
    root = repo_root or _repo_root()
    idx_path = index_path or (root / "state" / "readwise_library.json")
    out_dir = output_dir or (root / "raw" / "readwise")

    index = LibraryIndex.load(idx_path)
    if reset_watermark:
        index.last_updated_after = None
    updated_after = resolved_updated_after_for_list(index)

    if client is not None:
        stream = iter_archive_processed_documents(client, updated_after=updated_after)
        examined, exported, skipped, seen_updated, index_dirty = _consume_reader_documents(
            stream,
            index=index,
            out_dir=out_dir,
            dry_run=dry_run,
            prune_missing=prune_missing,
        )
    else:
        with reader_client(token) as owned:
            stream = iter_archive_processed_documents(owned, updated_after=updated_after)
            examined, exported, skipped, seen_updated, index_dirty = _consume_reader_documents(
                stream,
                index=index,
                out_dir=out_dir,
                dry_run=dry_run,
                prune_missing=prune_missing,
            )

    max_seen = max_iso_timestamps(seen_updated)
    should_save = not dry_run and (
        index_dirty or max_seen is not None or (reset_watermark and examined == 0)
    )
    if should_save:
        if max_seen is not None:
            prior = index.last_updated_after
            if prior is None:
                index.last_updated_after = max_seen
            else:
                try:
                    p_dt = datetime.fromisoformat(prior.replace("Z", "+00:00"))
                    if p_dt.tzinfo is None:
                        p_dt = p_dt.replace(tzinfo=UTC)
                    m_dt = datetime.fromisoformat(max_seen.replace("Z", "+00:00"))
                    if m_dt.tzinfo is None:
                        m_dt = m_dt.replace(tzinfo=UTC)
                    index.last_updated_after = max(
                        m_dt.astimezone(UTC), p_dt.astimezone(UTC)
                    ).isoformat()
                except ValueError:
                    index.last_updated_after = max_seen
        index.save(idx_path)

    return SyncResult(
        examined=examined,
        exported=exported,
        skipped=skipped,
        dry_run=dry_run,
        incremental_filter_active=True,
        incremental_watermark=updated_after,
    )
