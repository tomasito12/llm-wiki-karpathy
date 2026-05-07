"""JSON index for exported Reader documents (dedupe without scanning ``raw/``)."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from src.pipeline.atomic import atomic_write_json

INDEX_VERSION = 1


@dataclass
class ExportedRecord:
    """One indexed Reader document after a successful export."""

    html_path: str
    md_path: str
    source_url: str | None
    updated_at: str | None
    content_sha256: str | None

    @staticmethod
    def from_dict(data: dict[str, Any]) -> ExportedRecord:
        """Parse a persisted ``ExportedRecord`` from a JSON object."""
        return ExportedRecord(
            html_path=str(data["html_path"]),
            md_path=str(data["md_path"]),
            source_url=data.get("source_url"),
            updated_at=data.get("updated_at"),
            content_sha256=data.get("content_sha256"),
        )


@dataclass
class LibraryIndex:
    """Full persisted index: document id → export metadata."""

    documents: dict[str, ExportedRecord]
    last_updated_after: str | None

    @staticmethod
    def empty() -> LibraryIndex:
        """Return a new empty index."""
        return LibraryIndex(documents={}, last_updated_after=None)

    @staticmethod
    def load(path: Path) -> LibraryIndex:
        """Load index from JSON file; missing file yields empty index."""
        if not path.exists():
            return LibraryIndex.empty()
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return LibraryIndex.empty()
        docs_raw = raw.get("documents")
        documents: dict[str, ExportedRecord] = {}
        if isinstance(docs_raw, dict):
            for doc_id, row in docs_raw.items():
                if isinstance(row, dict):
                    documents[str(doc_id)] = ExportedRecord.from_dict(row)
        last_after = raw.get("last_updated_after")
        last_after_str = str(last_after) if isinstance(last_after, str) else None
        return LibraryIndex(documents=documents, last_updated_after=last_after_str)

    def save(self, path: Path) -> None:
        """Write index to JSON with stable key ordering."""
        payload = {
            "version": INDEX_VERSION,
            "last_updated_after": self.last_updated_after,
            "documents": {
                doc_id: asdict(record) for doc_id, record in sorted(self.documents.items())
            },
        }
        atomic_write_json(path, payload)
