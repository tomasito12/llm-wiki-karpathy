"""JSON-backed seen-state storage for discovered documents."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from src.pipeline.atomic import atomic_write_json


def canonicalize_url(url: str) -> str:
    """Return a normalized URL string for deterministic deduping."""
    trimmed = url.strip()
    no_fragment = trimmed.split("#", maxsplit=1)[0]
    no_utm = no_fragment.split("?", maxsplit=1)[0]
    return no_utm.rstrip("/")


def make_item_id(url: str) -> str:
    """Create a stable item ID from a canonical URL."""
    canonical_url = canonicalize_url(url)
    return hashlib.sha256(canonical_url.encode("utf-8")).hexdigest()[:16]


@dataclass
class SeenItemRecord:
    """Persistence model for one seen content item."""

    item_id: str
    title: str
    canonical_url: str
    published_at: str | None
    discovered_at: str
    local_path: str | None
    status: str


class SourceStateStore:
    """Read/write state for seen items keyed by source name."""

    def __init__(self, state_path: Path) -> None:
        """Initialize store with a path to the JSON file."""
        self._state_path = state_path

    def load(self) -> dict[str, dict[str, SeenItemRecord]]:
        """Load all state from JSON, returning typed records."""
        raw = self._read_raw()
        loaded: dict[str, dict[str, SeenItemRecord]] = {}
        for source_name, items in raw.get("sources", {}).items():
            loaded[source_name] = {
                item_id: SeenItemRecord(**record) for item_id, record in items.items()
            }
        return loaded

    def save(self, state: dict[str, dict[str, SeenItemRecord]]) -> None:
        """Save typed state back to JSON."""
        payload = {
            "sources": {
                source_name: {item_id: asdict(record) for item_id, record in items.items()}
                for source_name, items in state.items()
            }
        }
        atomic_write_json(self._state_path, payload)

    def is_seen(self, source_name: str, item_id: str) -> bool:
        """Check whether an item has already been seen for a source."""
        state = self.load()
        return item_id in state.get(source_name, {})

    def upsert_item(
        self,
        source_name: str,
        item_id: str,
        title: str,
        canonical_url: str,
        published_at: str | None,
        local_path: str | None,
        status: str,
    ) -> SeenItemRecord:
        """Insert or update one item record and persist immediately."""
        state = self.load()
        state.setdefault(source_name, {})
        previous = state[source_name].get(item_id)
        discovered_at = (
            previous.discovered_at
            if previous is not None
            else datetime.now(tz=UTC).replace(microsecond=0).isoformat()
        )
        record = SeenItemRecord(
            item_id=item_id,
            title=title,
            canonical_url=canonical_url,
            published_at=published_at,
            discovered_at=discovered_at,
            local_path=local_path,
            status=status,
        )
        state[source_name][item_id] = record
        self.save(state)
        return record

    def _read_raw(self) -> dict:
        """Read JSON payload from disk or return empty default."""
        if not self._state_path.exists():
            return {"sources": {}}
        content = self._state_path.read_text(encoding="utf-8").strip()
        if not content:
            return {"sources": {}}
        return json.loads(content)
