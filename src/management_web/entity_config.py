"""Configuration for management-web entity groups and render alignment."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

EntitySection = Literal["wiki_entities", "source_specific_insights"]
RenderMode = Literal["merged", "individual"]

# Top-level ``llm_output`` keys that are not extractable entity proposal lists.
LLM_OUTPUT_NON_ENTITY_KEYS: frozenset[str] = frozenset(
    {
        "source_summary",
        "source_evidence_profile",
    }
)

# Pipeline list keys under ``llm_output`` that represent extractable entity groups.
PIPELINE_ENTITY_LIST_KEYS: frozenset[str] = frozenset(
    {
        "topics",
        "glossary",
        "industry_trends",
        "how_to",
        "tools",
        "foundation_models",
        "implementation_studies",
        "roundup_signals",
        "interview_insights",
    }
)


@dataclass(frozen=True)
class EditableEntityConfig:
    """Render-aligned configuration for one editable entity group."""

    group: str
    label: str
    section: EntitySection
    artifact_key: str
    review_key: str
    render_category: str
    render_mode: RenderMode
    title_key: str
    title_fallback_keys: tuple[str, ...]
    description_key: str
    description_fallback_keys: tuple[str, ...]
    tag_keys: tuple[str, ...] = (
        "proposed_tags",
        "primary_tag",
        "secondary_tag",
        "suggested_new_tags",
        "suggested_new_tag",
    )
    type_keys: tuple[str, ...] = ("proposed_types", "proposed_new_type")
    evidence_keys: tuple[str, ...] = (
        "evidence",
        "supporting_snippet",
        "evidence_from_source",
        "source_phrase",
        "source_quote",
        "supporting_evidence",
    )
    detail_list_fields: tuple[tuple[str, str], ...] = ()


ENTITY_CONFIGS: tuple[EditableEntityConfig, ...] = (
    EditableEntityConfig(
        group="topics",
        label="Topics",
        section="wiki_entities",
        artifact_key="topics",
        review_key="topics",
        render_category="topic",
        render_mode="merged",
        title_key="topic_title",
        title_fallback_keys=("topic", "title"),
        description_key="knowledge_summary",
        description_fallback_keys=(
            "topic_description",
            "operational_insight",
            "description",
            "summary",
        ),
        detail_list_fields=(("key_points", "Key points"),),
        tag_keys=(
            "topic_tags",
            "proposed_tags",
            "primary_tag",
            "secondary_tag",
            "suggested_new_tags",
            "suggested_new_tag",
        ),
    ),
    EditableEntityConfig(
        group="glossary",
        label="Glossary",
        section="wiki_entities",
        artifact_key="glossary",
        review_key="glossary",
        render_category="glossary",
        render_mode="merged",
        title_key="term",
        title_fallback_keys=("glossary_term", "title"),
        description_key="proposed_definition",
        description_fallback_keys=(
            "definition",
            "knowledge_summary",
            "description",
            "summary",
        ),
        tag_keys=(
            "tags",
            "glossary_tags",
            "proposed_tags",
            "primary_tag",
            "secondary_tag",
            "suggested_new_tags",
            "suggested_new_tag",
        ),
    ),
    EditableEntityConfig(
        group="trends",
        label="Trends",
        section="wiki_entities",
        artifact_key="industry_trends",
        review_key="industry_trends",
        render_category="trend",
        render_mode="merged",
        title_key="trend_title",
        title_fallback_keys=("trend", "title"),
        description_key="trend_description",
        description_fallback_keys=(
            "knowledge_summary",
            "operational_insight",
            "description",
            "summary",
        ),
        tag_keys=(
            "trend_tags",
            "proposed_tags",
            "primary_tag",
            "secondary_tag",
            "suggested_new_tags",
            "suggested_new_tag",
        ),
    ),
    EditableEntityConfig(
        group="how_to",
        label="How-tos",
        section="wiki_entities",
        artifact_key="how_to",
        review_key="how_to",
        render_category="how_to",
        render_mode="merged",
        title_key="question_title",
        title_fallback_keys=("title",),
        description_key="answer_summary",
        description_fallback_keys=("what_and_problem", "description", "summary"),
        detail_list_fields=(
            ("implementation_steps", "Implementation steps"),
            ("prerequisites", "Prerequisites"),
        ),
    ),
    EditableEntityConfig(
        group="tools",
        label="Tools",
        section="wiki_entities",
        artifact_key="tools",
        review_key="tools",
        render_category="tool",
        render_mode="merged",
        title_key="name",
        title_fallback_keys=("title",),
        description_key="short_description",
        description_fallback_keys=("operational_relevance", "description", "summary"),
        detail_list_fields=(
            ("core_capabilities", "Core capabilities"),
            ("integration_ecosystem", "Integration ecosystem"),
        ),
    ),
    EditableEntityConfig(
        group="models",
        label="Models",
        section="wiki_entities",
        artifact_key="foundation_models",
        review_key="foundation_models",
        render_category="model",
        render_mode="merged",
        title_key="model_name",
        title_fallback_keys=("title", "name"),
        description_key="operational_profile",
        description_fallback_keys=("deployment_implications", "description", "summary"),
        detail_list_fields=(
            ("core_capabilities", "Core capabilities"),
            ("benchmark_observations", "Benchmark observations"),
            ("comparative_observations", "Comparative observations"),
        ),
    ),
    EditableEntityConfig(
        group="implementation_studies",
        label="Implementation studies",
        section="source_specific_insights",
        artifact_key="implementation_studies",
        review_key="implementation_studies",
        render_category="impl_study",
        render_mode="individual",
        title_key="title",
        title_fallback_keys=(),
        description_key="overview",
        description_fallback_keys=("what_was_implemented", "description", "summary"),
        detail_list_fields=(
            ("key_lessons", "Key lessons"),
            ("open_questions", "Open questions"),
        ),
    ),
    EditableEntityConfig(
        group="signals",
        label="Signals",
        section="source_specific_insights",
        artifact_key="roundup_signals",
        review_key="roundup_signals",
        render_category="signal",
        render_mode="individual",
        title_key="signal_title",
        title_fallback_keys=("title",),
        description_key="summary",
        description_fallback_keys=("description",),
        detail_list_fields=(
            ("suggested_destinations", "Suggested destinations"),
            ("mentioned_entities", "Mentioned entities"),
            ("evidence_snippets", "Evidence snippets"),
        ),
    ),
    EditableEntityConfig(
        group="interview_insights",
        label="Interview insights",
        section="source_specific_insights",
        artifact_key="interview_insights",
        review_key="interview_insights",
        render_category="insight",
        render_mode="individual",
        title_key="insight_title",
        title_fallback_keys=("title",),
        description_key="summary",
        description_fallback_keys=("description",),
        detail_list_fields=(
            ("suggested_destinations", "Suggested destinations"),
            ("mentioned_entities", "Mentioned entities"),
            ("evidence_snippets", "Evidence snippets"),
        ),
    ),
)

ENTITY_CONFIG_BY_GROUP: dict[str, EditableEntityConfig] = {
    config.group: config for config in ENTITY_CONFIGS
}
SUPPORTED_ARTIFACT_KEYS: frozenset[str] = frozenset(
    config.artifact_key for config in ENTITY_CONFIGS
)
