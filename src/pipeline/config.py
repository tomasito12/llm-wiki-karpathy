"""Pipeline configuration loading."""

from __future__ import annotations

import json
from pathlib import Path

from src.pipeline.models import SourceConfig


class PipelineConfigError(ValueError):
    """Raised when pipeline config is missing or invalid."""


def load_sources(config_path: Path) -> list[SourceConfig]:
    """Load configured sources from JSON config file."""
    if not config_path.exists():
        raise PipelineConfigError(
            f"Missing config file: {config_path}. Create it with a 'sources' list."
        )
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    sources_raw = payload.get("sources")
    if not isinstance(sources_raw, list):
        raise PipelineConfigError("Config must contain a 'sources' array.")
    sources: list[SourceConfig] = []
    for entry in sources_raw:
        if not isinstance(entry, dict):
            raise PipelineConfigError("Each source entry must be an object.")
        try:
            source = SourceConfig(
                name=str(entry["name"]),
                kind=str(entry["kind"]),
                url=str(entry["url"]),
            )
        except KeyError as exc:
            raise PipelineConfigError(f"Missing required source field: {exc}") from exc
        sources.append(source)
    return sources


def find_source_by_name(sources: list[SourceConfig], name: str) -> SourceConfig:
    """Return the configured source with matching name."""
    for source in sources:
        if source.name == name:
            return source
    raise PipelineConfigError(f"Unknown source '{name}'.")
