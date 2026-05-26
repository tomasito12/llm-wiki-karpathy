"""Registry of ingestion-review tag/type allowlist YAML files."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from src.ingest_review.tags import (
    default_glossary_tags_path,
    default_howto_tags_path,
    default_impl_study_tags_path,
    default_model_tags_path,
    default_model_types_path,
    default_tool_tags_path,
    default_tool_types_path,
    default_topic_tags_path,
    default_trend_tags_path,
)

_PathFn = Callable[[Path | None], Path]


@dataclass(frozen=True, slots=True)
class TagTaxonomySpec:
    """One allowlist file: routing tags or tool/model types."""

    id: str
    label: str
    path_fn: _PathFn
    description: str
    baseline_tags: tuple[str, ...]


TAG_TAXONOMIES: tuple[TagTaxonomySpec, ...] = (
    TagTaxonomySpec(
        id="topics",
        label="Topics & insights",
        path_fn=default_topic_tags_path,
        description="Retrieval-oriented topic tags (durable conceptual neighborhoods).",
        baseline_tags=("agent-systems", "ai-engineering", "orchestration"),
    ),
    TagTaxonomySpec(
        id="glossary",
        label="Glossary",
        path_fn=default_glossary_tags_path,
        description="Stable conceptual neighborhood tags for glossary terms.",
        baseline_tags=("agent-systems", "alignment", "orchestration"),
    ),
    TagTaxonomySpec(
        id="howto",
        label="How-tos",
        path_fn=default_howto_tags_path,
        description="How-to tags (same vocabulary as topics; workflow-oriented selection).",
        baseline_tags=("agent-systems", "ai-engineering", "workflow-design"),
    ),
    TagTaxonomySpec(
        id="trends",
        label="Trends & signals",
        path_fn=default_trend_tags_path,
        description="Industry shift tags (directional forces, not broad domains).",
        baseline_tags=("ai-operationalization", "behavioral-evaluation", "runtime-centralization"),
    ),
    TagTaxonomySpec(
        id="impl_study",
        label="Implementation studies",
        path_fn=default_impl_study_tags_path,
        description=("Implementation-study tags (patterns/themes; industry is a separate field)."),
        baseline_tags=("enterprise-ai-adoption", "production-failure"),
    ),
    TagTaxonomySpec(
        id="tool_tags",
        label="Tool retrieval tags",
        path_fn=default_tool_tags_path,
        description="Retrieval tags for tool proposals (capability, deployment, workflow fit).",
        baseline_tags=("coding", "cli-tool", "workflow-automation"),
    ),
    TagTaxonomySpec(
        id="model_tags",
        label="Model retrieval tags",
        path_fn=default_model_tags_path,
        description="Retrieval tags for foundation-model proposals (capability, access, profile).",
        baseline_tags=("coding-model", "frontier-model", "open-weight-model"),
    ),
    TagTaxonomySpec(
        id="tool_types",
        label="Tool types",
        path_fn=default_tool_types_path,
        description="Product archetypes (what the tool IS). LLM proposes via proposed_types.",
        baseline_tags=("cloud-saas", "coding-agent", "mcp-server"),
    ),
    TagTaxonomySpec(
        id="model_types",
        label="Model types",
        path_fn=default_model_types_path,
        description=(
            "Model archetypes (deployment/capability class). LLM proposes via proposed_types."
        ),
        baseline_tags=("embedding-model", "frontier-model", "open-weight-model"),
    ),
)

_TAXONOMY_BY_ID: dict[str, TagTaxonomySpec] = {spec.id: spec for spec in TAG_TAXONOMIES}


def taxonomy_by_id(taxonomy_id: str) -> TagTaxonomySpec | None:
    """Return the spec for *taxonomy_id*, or None if unknown."""
    return _TAXONOMY_BY_ID.get(taxonomy_id)


def taxonomy_path(spec: TagTaxonomySpec, root: Path | None = None) -> Path:
    """Resolved filesystem path for one taxonomy allowlist."""
    return spec.path_fn(root)


def tag_taxonomy_paths(root: Path | None = None) -> list[Path]:
    """All YAML allowlist paths in registry order."""
    return [taxonomy_path(spec, root) for spec in TAG_TAXONOMIES]
