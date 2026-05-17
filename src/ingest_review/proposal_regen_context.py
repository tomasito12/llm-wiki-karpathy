"""Build wiki/artifact context blocks for per-proposal OpenAI regeneration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.ingest_review.canonical_titles import (
    ENTITY_CANONICAL_CONFIGS,
    CanonicalTitleEntry,
    build_canonical_index,
    effective_slug_from_node,
    effective_title_from_node,
    format_canonical_block,
    merge_canonical_entries,
    review_node_is_canonical_source,
)
from src.ingest_review.proposal_regen import REGEN_SPECS
from src.ingest_review.wiki_snapshot import WikiSnapshot


def _lines(items: list[str], *, cap: int = 120) -> str:
    trimmed = [str(x).strip() for x in items if str(x).strip()][:cap]
    return "\n".join(f"- {t}" for t in trimmed) if trimmed else "(none)"


def _collect_slugs_from_artifact(
    artifact: dict[str, Any],
    review_list_key: str,
    slug_field: str,
) -> list[str]:
    out: list[str] = []
    for node in (artifact.get("review") or {}).get(review_list_key) or []:
        if not isinstance(node, dict):
            continue
        slug = (node.get("llm_item") or {}).get(slug_field)
        if isinstance(slug, str) and slug.strip():
            out.append(slug.strip())
    return out


def _canonical_entries_from_artifact(
    artifact: dict[str, Any],
    cfg: Any,
) -> list[CanonicalTitleEntry]:
    """Non-rejected titles from the current artifact's review list."""
    out: list[CanonicalTitleEntry] = []
    for node in (artifact.get("review") or {}).get(cfg.review_list_key) or []:
        if not isinstance(node, dict) or not review_node_is_canonical_source(node):
            continue
        title = effective_title_from_node(node, cfg.title_field)
        if not title:
            continue
        slug = ""
        if cfg.slug_field:
            slug = effective_slug_from_node(node, cfg.slug_field, title=title)
        out.append(CanonicalTitleEntry(title=title, slug=slug))
    return out


def build_regen_context_sections(
    entity_key: str,
    *,
    artifact: dict[str, Any],
    wiki: WikiSnapshot,
    topic_tags_allowlist: list[str] | None = None,
    trend_tags_allowlist: list[str] | None = None,
    howto_tags_allowlist: list[str] | None = None,
    glossary_tags_allowlist: list[str] | None = None,
    model_types_allowlist: list[str] | None = None,
    tool_types_allowlist: list[str] | None = None,
    impl_study_tags_allowlist: list[str] | None = None,
    reviews_root: Path | None = None,
) -> dict[str, str]:
    """Return ``## HEADING`` → body map for the regeneration user prompt."""
    spec = REGEN_SPECS.get(entity_key)
    if not spec:
        raise ValueError(f"Unknown entity_key: {entity_key}")

    sections: dict[str, str] = {}
    canon_cfg = ENTITY_CANONICAL_CONFIGS.get(entity_key)
    if canon_cfg is not None:
        index = build_canonical_index(wiki, reviews_root)
        merged = merge_canonical_entries(
            index.get(entity_key, []),
            _canonical_entries_from_artifact(artifact, canon_cfg),
        )
        sections[canon_cfg.prompt_block_key] = format_canonical_block(merged)

    if entity_key == "topic":
        slugs = list(wiki.topic_slugs)
        slugs.extend(_collect_slugs_from_artifact(artifact, spec.review_list_key, "topic_slug"))
        sections["EXISTING_TOPIC_SLUGS"] = _lines(slugs)
        sections["TOPIC_TAGS_ALLOWLIST"] = _lines(list(topic_tags_allowlist or []))

    elif entity_key == "glossary":
        sections["GLOSSARY_TAGS_ALLOWLIST"] = _lines(list(glossary_tags_allowlist or []))

    elif entity_key == "how_to":
        sections["HOWTO_TAGS_ALLOWLIST"] = _lines(list(howto_tags_allowlist or []))

    elif entity_key == "trend":
        slugs = list(wiki.trend_slugs)
        slugs.extend(_collect_slugs_from_artifact(artifact, spec.review_list_key, "trend_slug"))
        sections["EXISTING_TREND_SLUGS"] = _lines(slugs)
        sections["TREND_TAGS_ALLOWLIST"] = _lines(list(trend_tags_allowlist or []))

    elif entity_key == "tool":
        sections["TOOL_TYPES_ALLOWLIST"] = _lines(list(tool_types_allowlist or []))

    elif entity_key == "model":
        sections["MODEL_TYPES_ALLOWLIST"] = _lines(list(model_types_allowlist or []))

    elif entity_key == "impl_study":
        sections["IMPL_STUDY_TAGS_ALLOWLIST"] = _lines(list(impl_study_tags_allowlist or []))

    return sections
