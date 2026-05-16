"""Build wiki/artifact context blocks for per-proposal OpenAI regeneration."""

from __future__ import annotations

from typing import Any

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


def _collect_titles_from_artifact(
    artifact: dict[str, Any],
    review_list_key: str,
    title_field: str,
) -> list[str]:
    out: list[str] = []
    for node in (artifact.get("review") or {}).get(review_list_key) or []:
        if not isinstance(node, dict):
            continue
        title = (node.get("llm_item") or {}).get(title_field)
        if isinstance(title, str) and title.strip():
            out.append(title.strip())
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
) -> dict[str, str]:
    """Return ``## HEADING`` → body map for the regeneration user prompt."""
    spec = REGEN_SPECS.get(entity_key)
    if not spec:
        raise ValueError(f"Unknown entity_key: {entity_key}")

    sections: dict[str, str] = {}

    if entity_key == "topic":
        slugs = list(wiki.topic_slugs)
        slugs.extend(_collect_slugs_from_artifact(artifact, spec.review_list_key, "topic_slug"))
        sections["EXISTING_TOPIC_SLUGS"] = _lines(slugs)
        sections["TOPIC_TAGS_ALLOWLIST"] = _lines(list(topic_tags_allowlist or []))

    elif entity_key == "glossary":
        terms = list(wiki.glossary_terms)
        terms.extend(_collect_titles_from_artifact(artifact, spec.review_list_key, "term"))
        sections["EXISTING_GLOSSARY_TERMS"] = _lines(terms)
        sections["GLOSSARY_TAGS_ALLOWLIST"] = _lines(list(glossary_tags_allowlist or []))

    elif entity_key == "how_to":
        titles = list(wiki.howto_titles)
        titles.extend(
            _collect_titles_from_artifact(artifact, spec.review_list_key, "question_title")
        )
        sections["EXISTING_HOWTO_TITLES"] = _lines(titles)
        sections["HOWTO_TAGS_ALLOWLIST"] = _lines(list(howto_tags_allowlist or []))

    elif entity_key == "trend":
        slugs = list(wiki.trend_slugs)
        slugs.extend(_collect_slugs_from_artifact(artifact, spec.review_list_key, "trend_slug"))
        sections["EXISTING_TREND_SLUGS"] = _lines(slugs)
        titles = _collect_titles_from_artifact(artifact, spec.review_list_key, "trend_title")
        if titles:
            sections["EXISTING_TREND_TITLES"] = _lines(titles)
        sections["TREND_TAGS_ALLOWLIST"] = _lines(list(trend_tags_allowlist or []))

    elif entity_key == "tool":
        names = list(wiki.tool_names)
        names.extend(_collect_titles_from_artifact(artifact, spec.review_list_key, "name"))
        sections["EXISTING_TOOL_NAMES"] = _lines(names)
        sections["TOOL_TYPES_ALLOWLIST"] = _lines(list(tool_types_allowlist or []))

    elif entity_key == "model":
        names = list(wiki.foundation_model_names)
        names.extend(_collect_titles_from_artifact(artifact, spec.review_list_key, "model_name"))
        sections["EXISTING_FOUNDATION_MODEL_NAMES"] = _lines(names)
        sections["MODEL_TYPES_ALLOWLIST"] = _lines(list(model_types_allowlist or []))

    elif entity_key == "impl_study":
        titles = _collect_titles_from_artifact(artifact, spec.review_list_key, "title")
        sections["EXISTING_IMPL_STUDY_TITLES"] = _lines(titles)
        sections["IMPL_STUDY_TAGS_ALLOWLIST"] = _lines(list(impl_study_tags_allowlist or []))

    return sections
