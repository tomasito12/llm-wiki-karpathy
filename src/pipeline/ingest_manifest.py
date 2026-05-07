"""Durable manifest for wiki ingest decisions and generated artifacts."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from src.pipeline.atomic import atomic_write_json
from src.readwise.sync import _repo_root

INGEST_MANIFEST_VERSION = 1

Stage1Route = Literal["radar", "tools-overview", "questions", "unknown"]
ArtifactRoute = Literal["tool", "foundation-model", "mcp", "question", "glossary", "source"]
IngestStatus = Literal["pending", "rendered", "validated", "failed", "needs_review"]


def utc_now_iso() -> str:
    """Return a stable UTC timestamp string for manifest writes."""
    return datetime.now(tz=UTC).replace(microsecond=0).isoformat()


@dataclass
class Stage2RouteRecord:
    """One routed artifact decision from Stage 2."""

    name: str
    route: ArtifactRoute
    target_path: str | None = None
    notes: str | None = None

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Stage2RouteRecord:
        """Parse a Stage 2 route from JSON data."""
        return Stage2RouteRecord(
            name=str(data["name"]),
            route=data["route"],
            target_path=data.get("target_path"),
            notes=data.get("notes"),
        )


@dataclass
class IngestManifestRecord:
    """One source-level ingest manifest entry."""

    source_id: str
    raw_md_path: str
    raw_html_path: str
    canonical_url: str | None
    title: str
    author: str | None = None
    publication: str | None = None
    published_date: str | None = None
    content_sha256: str | None = None
    stage1_route: Stage1Route = "unknown"
    stage2_routes: list[Stage2RouteRecord] = field(default_factory=list)
    wiki_artifacts: list[str] = field(default_factory=list)
    status: IngestStatus = "pending"
    errors: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    ingest_version: int = INGEST_MANIFEST_VERSION

    @staticmethod
    def from_dict(data: dict[str, Any]) -> IngestManifestRecord:
        """Parse an ingest manifest record from JSON data."""
        return IngestManifestRecord(
            source_id=str(data["source_id"]),
            raw_md_path=str(data["raw_md_path"]),
            raw_html_path=str(data["raw_html_path"]),
            canonical_url=data.get("canonical_url"),
            title=str(data["title"]),
            author=data.get("author"),
            publication=data.get("publication"),
            published_date=data.get("published_date"),
            content_sha256=data.get("content_sha256"),
            stage1_route=data.get("stage1_route", "unknown"),
            stage2_routes=[
                Stage2RouteRecord.from_dict(row)
                for row in data.get("stage2_routes", [])
                if isinstance(row, dict)
            ],
            wiki_artifacts=[str(path) for path in data.get("wiki_artifacts", [])],
            status=data.get("status", "pending"),
            errors=[str(error) for error in data.get("errors", [])],
            created_at=str(data.get("created_at") or utc_now_iso()),
            updated_at=str(data.get("updated_at") or utc_now_iso()),
            ingest_version=int(data.get("ingest_version", INGEST_MANIFEST_VERSION)),
        )


@dataclass
class IngestManifest:
    """Top-level persisted ingest manifest."""

    records: dict[str, IngestManifestRecord]

    @staticmethod
    def empty() -> IngestManifest:
        """Return an empty ingest manifest."""
        return IngestManifest(records={})

    @staticmethod
    def load(path: Path) -> IngestManifest:
        """Load a manifest from JSON, treating missing/empty files as empty."""
        if not path.exists():
            return IngestManifest.empty()
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            return IngestManifest.empty()
        raw = json.loads(content)
        if not isinstance(raw, dict):
            return IngestManifest.empty()
        records_raw = raw.get("records")
        records: dict[str, IngestManifestRecord] = {}
        if isinstance(records_raw, dict):
            for source_id, record in records_raw.items():
                if isinstance(record, dict):
                    records[str(source_id)] = IngestManifestRecord.from_dict(record)
        return IngestManifest(records=records)

    def save(self, path: Path) -> None:
        """Persist the manifest to disk atomically."""
        payload = {
            "version": INGEST_MANIFEST_VERSION,
            "records": {
                source_id: asdict(record) for source_id, record in sorted(self.records.items())
            },
        }
        atomic_write_json(path, payload)


class IngestManifestStore:
    """Read/write helper for ingest manifest records."""

    def __init__(self, path: Path) -> None:
        """Initialize the store with a manifest path."""
        self.path = path

    def load(self) -> IngestManifest:
        """Load the current manifest."""
        return IngestManifest.load(self.path)

    def save(self, manifest: IngestManifest) -> None:
        """Save the current manifest."""
        manifest.save(self.path)

    def upsert_record(self, record: IngestManifestRecord) -> IngestManifestRecord:
        """Insert or replace a manifest record and refresh ``updated_at``."""
        manifest = self.load()
        existing = manifest.records.get(record.source_id)
        if existing is not None:
            record.created_at = existing.created_at
        record.updated_at = utc_now_iso()
        manifest.records[record.source_id] = record
        self.save(manifest)
        return record

    def update_status(
        self,
        source_id: str,
        status: IngestStatus,
        *,
        error: str | None = None,
    ) -> IngestManifestRecord:
        """Update status for one source and optionally append an error."""
        manifest = self.load()
        record = manifest.records[source_id]
        record.status = status
        record.updated_at = utc_now_iso()
        if error is not None:
            record.errors.append(error)
        manifest.records[source_id] = record
        self.save(manifest)
        return record


def default_manifest_path() -> Path:
    """Return the default ``state/ingest_manifest.json`` path."""
    return _repo_root() / "state" / "ingest_manifest.json"


def build_parser() -> argparse.ArgumentParser:
    """Build the ingest-manifest inspection CLI parser."""
    parser = argparse.ArgumentParser(
        prog="ingest-manifest",
        description="Inspect the local ingest manifest.",
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=default_manifest_path(),
        help="Manifest path (default: <repo>/state/ingest_manifest.json).",
    )
    parser.add_argument("--json", action="store_true", help="Print full JSON payload.")
    return parser


def main() -> int:
    """Run the ingest-manifest inspection CLI."""
    args = build_parser().parse_args()
    manifest = IngestManifest.load(args.path)
    if args.json:
        payload = {
            "version": INGEST_MANIFEST_VERSION,
            "records": {
                source_id: asdict(record) for source_id, record in sorted(manifest.records.items())
            },
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"ingest-manifest: records={len(manifest.records)} path={args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
