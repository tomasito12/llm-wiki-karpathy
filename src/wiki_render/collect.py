"""Collect source records, contributions, and chronological items from artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from src.ingest_review.evidence import (
    effective_proposal_evidence_type,
    source_primary_evidence_type,
)
from src.pipeline.slug import slugify
from src.wiki_render import layout
from src.wiki_render.evidence import EvidenceItem, evidence_set_hash, make_evidence_item
from src.wiki_render.models import Contribution, IndividualPage, SourceRecord
from src.wiki_render.resolve import (
    artifact_assessed_as_of,
    artifact_ingested_at,
    list_value,
    llm_item,
    proposal_is_included,
    reviewed_tags,
    reviewed_types,
    scalar_value,
    source_summary_list,
    source_summary_scalar,
)

DERIVED_KEY_BY_CATEGORY: dict[str, str] = {
    "topic": "derived_topics",
    "glossary": "derived_glossary",
    "trend": "derived_trends",
    "tool": "derived_tools",
    "model": "derived_models",
    "how_to": "derived_how_to",
    "impl_study": "derived_implementation_studies",
}


@dataclass(frozen=True)
class EntityConfig:
    """How to map one reviewed proposal category into contributions."""

    review_key: str
    category: str
    title_key: str
    slug_key: str | None
    scalar_keys: tuple[str, ...]
    list_keys: tuple[str, ...]
    evidence_scalar_keys: tuple[str, ...]
    evidence_list_keys: tuple[str, ...]
    related_keys: tuple[str, ...] = ()


ENTITY_CONFIGS: tuple[EntityConfig, ...] = (
    EntityConfig(
        review_key="topics",
        category="topic",
        title_key="topic_title",
        slug_key="topic_slug",
        scalar_keys=(
            "topic_slug",
            "topic_title",
            "knowledge_summary",
            "examples",
            "operational_insight",
            "relevance_note",
        ),
        list_keys=("key_points", "related_topics"),
        evidence_scalar_keys=(
            "knowledge_summary",
            "examples",
            "operational_insight",
            "relevance_note",
        ),
        evidence_list_keys=("key_points",),
        related_keys=("related_topics",),
    ),
    EntityConfig(
        review_key="glossary",
        category="glossary",
        title_key="term",
        slug_key=None,
        scalar_keys=("term", "proposed_definition", "extended_explanation", "relevance_note"),
        list_keys=("related_terms",),
        evidence_scalar_keys=("proposed_definition", "extended_explanation", "relevance_note"),
        evidence_list_keys=(),
        related_keys=("related_terms",),
    ),
    EntityConfig(
        review_key="industry_trends",
        category="trend",
        title_key="trend_title",
        slug_key="trend_slug",
        scalar_keys=(
            "trend_slug",
            "trend_title",
            "trend_description",
            "evidence_from_source",
            "time_sensitivity",
            "uncertainty_note",
        ),
        list_keys=("supporting_data_points", "related_trends"),
        evidence_scalar_keys=(
            "trend_description",
            "evidence_from_source",
            "time_sensitivity",
            "uncertainty_note",
        ),
        evidence_list_keys=("supporting_data_points",),
        related_keys=("related_trends",),
    ),
    EntityConfig(
        review_key="tools",
        category="tool",
        title_key="name",
        slug_key=None,
        scalar_keys=(
            "name",
            "short_description",
            "operational_relevance",
            "strengths",
            "weaknesses_limitations",
            "maturity_signals",
        ),
        list_keys=("core_capabilities", "integration_ecosystem", "related_tools"),
        evidence_scalar_keys=(
            "short_description",
            "operational_relevance",
            "strengths",
            "weaknesses_limitations",
            "maturity_signals",
        ),
        evidence_list_keys=("core_capabilities", "integration_ecosystem"),
        related_keys=("related_tools",),
    ),
    EntityConfig(
        review_key="foundation_models",
        category="model",
        title_key="model_name",
        slug_key=None,
        scalar_keys=(
            "model_name",
            "provider",
            "operational_profile",
            "deployment_implications",
            "weaknesses_limitations",
            "service_automation_implications",
            "maturity_signals",
            "pricing_inference_implications",
        ),
        list_keys=(
            "core_capabilities",
            "benchmark_observations",
            "comparative_observations",
            "related_models",
        ),
        evidence_scalar_keys=(
            "operational_profile",
            "deployment_implications",
            "weaknesses_limitations",
            "service_automation_implications",
            "maturity_signals",
            "pricing_inference_implications",
        ),
        evidence_list_keys=(
            "core_capabilities",
            "benchmark_observations",
            "comparative_observations",
        ),
        related_keys=("related_models",),
    ),
    EntityConfig(
        review_key="how_to",
        category="how_to",
        title_key="question_title",
        slug_key=None,
        scalar_keys=("question_title", "what_and_problem", "answer_summary", "caveats"),
        list_keys=("implementation_steps", "prerequisites", "related_howtos"),
        evidence_scalar_keys=("what_and_problem", "answer_summary", "caveats"),
        evidence_list_keys=("implementation_steps", "prerequisites"),
        related_keys=("related_howtos",),
    ),
    EntityConfig(
        review_key="implementation_studies",
        category="impl_study",
        title_key="title",
        slug_key=None,
        scalar_keys=(
            "title",
            "company",
            "industry",
            "overview",
            "what_was_implemented",
            "business_objective",
            "technical_approach",
            "deployment_context",
            "outcome_status",
            "success_or_failure_factors",
            "operational_constraints",
            "ai_model_observations",
            "implications_for_service_automation",
            "strategic_signals",
        ),
        list_keys=("key_lessons", "open_questions", "related_sources"),
        evidence_scalar_keys=(
            "overview",
            "what_was_implemented",
            "business_objective",
            "technical_approach",
            "deployment_context",
            "outcome_status",
            "success_or_failure_factors",
            "operational_constraints",
            "ai_model_observations",
            "implications_for_service_automation",
            "strategic_signals",
        ),
        evidence_list_keys=("key_lessons", "open_questions"),
        related_keys=("related_sources",),
    ),
)


@dataclass
class CollectedItems:
    """Raw collected graph parts before merge."""

    sources: list[SourceRecord]
    contributions: list[Contribution]
    signals: list[IndividualPage]
    insights: list[IndividualPage]


def collect_items(artifacts: list[dict[str, Any]], wiki_dir: Path) -> CollectedItems:
    """Collect renderable graph inputs from review artifacts."""
    sources: list[SourceRecord] = []
    contributions: list[Contribution] = []
    signals: list[IndividualPage] = []
    insights: list[IndividualPage] = []
    source_by_id: dict[str, SourceRecord] = {}
    for artifact in artifacts:
        source = _source_record(artifact)
        sources.append(source)
        source_by_id[source.source_id] = source
        contributions.extend(_source_contributions(artifact, source))
        signals.extend(_individual_pages(artifact, source, "roundup_signals", "signal", wiki_dir))
        insights.extend(
            _individual_pages(artifact, source, "interview_insights", "insight", wiki_dir)
        )

    for contribution in contributions:
        source = source_by_id[contribution.source_id]
        source.source_tags.update(contribution.tags)
        source.derived.setdefault(DERIVED_KEY_BY_CATEGORY[contribution.category], set()).add(
            contribution.slug
        )
    for item in [*signals, *insights]:
        source = source_by_id[item.source_id]
        source.source_tags.update(item.tags)
        key = "derived_signals" if item.category == "signal" else "derived_interview_insights"
        source.derived_paths.setdefault(key, set()).add(item.path)
    return CollectedItems(
        sources=sorted(sources, key=lambda item: item.source_id),
        contributions=sorted(
            contributions,
            key=lambda item: (item.category, item.slug, item.source_id),
        ),
        signals=sorted(signals, key=lambda item: item.path),
        insights=sorted(insights, key=lambda item: item.path),
    )


def _source_record(artifact: dict[str, Any]) -> SourceRecord:
    """Build a source record from an artifact."""
    raw = artifact.get("source") or {}
    source_id = str(raw.get("source_id") or "").strip()
    published = str(raw.get("published_date") or "").strip()
    assessed = artifact_assessed_as_of(artifact)
    return SourceRecord(
        source_id=source_id,
        title=str(raw.get("title") or source_id).strip(),
        author=str(raw.get("author") or "").strip(),
        publication=str(raw.get("publication") or "").strip(),
        canonical_url=str(raw.get("canonical_url") or "").strip(),
        published_date=published,
        assessed_as_of=assessed,
        ingested_at=artifact_ingested_at(artifact),
        content_sha256=str(raw.get("content_sha256") or "").strip(),
        raw_md_rel_path=str(raw.get("raw_md_rel_path") or "").strip(),
        raw_html_rel_path=str(raw.get("raw_html_rel_path") or "").strip(),
        summary=source_summary_scalar(artifact, "summary"),
        accessible_overview=source_summary_scalar(artifact, "accessible_overview"),
        key_insights=source_summary_list(artifact, "key_insights"),
        why_it_matters=source_summary_scalar(artifact, "why_it_matters"),
        limitations_and_open_questions=source_summary_scalar(
            artifact,
            "limitations_and_open_questions",
        ),
        contradictions_and_skepticism=source_summary_scalar(
            artifact,
            "contradictions_and_skepticism",
        ),
    )


def _source_contributions(artifact: dict[str, Any], source: SourceRecord) -> list[Contribution]:
    """Return all mergeable contributions from one source."""
    review = artifact.get("review") or {}
    source_primary = source_primary_evidence_type(artifact)
    contributions: list[Contribution] = []
    for config in ENTITY_CONFIGS:
        nodes = review.get(config.review_key) or []
        if not isinstance(nodes, list):
            continue
        for node in nodes:
            if not isinstance(node, dict) or not proposal_is_included(node):
                continue
            item = llm_item(node)
            title = scalar_value(node, config.title_key)
            if not title:
                continue
            slug = _node_slug(node, config, title)
            assessed = str(item.get("assessed_as_of") or source.assessed_as_of).strip()
            source_date = _source_date(source.published_date, assessed)
            values = _values_for_node(node, config)
            evidence_type = effective_proposal_evidence_type(source_primary, item)
            evidence = _evidence_for_node(
                node=node,
                config=config,
                source=source,
                slug=slug,
                source_date=source_date,
                assessed_as_of=assessed,
                evidence_type=evidence_type,
            )
            contributions.append(
                Contribution(
                    category=config.category,
                    slug=slug,
                    title=title,
                    source_id=source.source_id,
                    source_title=source.title,
                    source_date=source_date,
                    published_date=source.published_date,
                    assessed_as_of=assessed,
                    ingested_at=source.ingested_at,
                    tags=reviewed_tags(node),
                    types=reviewed_types(node),
                    values=values,
                    evidence=evidence,
                    aliases=_aliases_for_node(node, slug, title),
                    match_candidates=_match_candidates(item),
                    confidence=_confidence(item),
                    value_level=str(item.get("value_level") or "medium"),
                    evidence_type=evidence_type,
                )
            )
    return contributions


def _individual_pages(
    artifact: dict[str, Any],
    source: SourceRecord,
    review_key: str,
    category: str,
    wiki_dir: Path,
) -> list[IndividualPage]:
    """Build non-merged signal/insight pages."""
    review = artifact.get("review") or {}
    nodes = review.get(review_key) or []
    if not isinstance(nodes, list):
        return []
    title_key = "signal_title" if category == "signal" else "insight_title"
    output: list[IndividualPage] = []
    source_primary = source_primary_evidence_type(artifact)
    for node in nodes:
        if not isinstance(node, dict) or not proposal_is_included(node):
            continue
        item = llm_item(node)
        title = scalar_value(node, title_key)
        if not title:
            continue
        slug = slugify(title)
        assessed = str(item.get("assessed_as_of") or source.assessed_as_of).strip()
        source_date = _source_date(source.published_date, assessed)
        path = layout.monthly_item_path(
            wiki_dir,
            category,
            source_id=source.source_id,
            slug=slug,
            date_text=source_date,
        ).relative
        values = _individual_values(node, category)
        evidence_type = effective_proposal_evidence_type(source_primary, item)
        evidence = _individual_evidence(
            node=node,
            category=category,
            slug=slug,
            source=source,
            source_date=source_date,
            assessed_as_of=assessed,
            evidence_type=evidence_type,
        )
        output.append(
            IndividualPage(
                category=category,
                slug=slug,
                title=title,
                path=path,
                source_id=source.source_id,
                source_title=source.title,
                source_date=source_date,
                month=layout.month_bucket(source_date),
                tags=reviewed_tags(node),
                values=values,
                evidence=evidence,
                evidence_set_hash=evidence_set_hash(evidence),
                evidence_count=len(evidence),
            )
        )
    return output


def _values_for_node(node: dict[str, Any], config: EntityConfig) -> dict[str, object]:
    """Return all configured values for a mergeable proposal."""
    values: dict[str, object] = {}
    for key in config.scalar_keys:
        values[key] = scalar_value(node, key)
    for key in config.list_keys:
        values[key] = list_value(node, key)
    raw = llm_item(node)
    if raw.get("supporting_snippet"):
        values["supporting_snippet"] = str(raw["supporting_snippet"]).strip()
    if config.category == "impl_study":
        snippets = raw.get("evidence_snippets")
        if isinstance(snippets, list):
            values["evidence_snippets"] = snippets
    return values


def _individual_values(node: dict[str, Any], category: str) -> dict[str, object]:
    """Return values for a signal or insight."""
    scalar_keys = (
        (
            "signal_title",
            "signal_type",
            "summary",
            "why_it_matters",
            "operational_relevance",
            "service_automation_relevance",
            "signal_strength",
            "time_horizon",
            "wiki_worthiness",
        )
        if category == "signal"
        else (
            "insight_title",
            "insight_type",
            "summary",
            "why_it_matters",
            "operational_relevance",
            "service_automation_relevance",
            "confidence",
            "durability_estimate",
            "wiki_worthiness",
        )
    )
    list_keys = (
        ("suggested_destinations", "mentioned_entities", "evidence_snippets")
        if category == "signal"
        else (
            "suggested_destinations",
            "mentioned_entities",
            "contrarian_or_speculative_claims",
            "evidence_snippets",
        )
    )
    values: dict[str, object] = {}
    for key in scalar_keys:
        values[key] = scalar_value(node, key)
    for key in list_keys:
        values[key] = list_value(node, key)
    return values


def _evidence_for_node(
    *,
    node: dict[str, Any],
    config: EntityConfig,
    source: SourceRecord,
    slug: str,
    source_date: str,
    assessed_as_of: str,
    evidence_type: str,
) -> list[EvidenceItem]:
    """Create evidence items for one proposal."""
    item = llm_item(node)
    evidence: list[EvidenceItem] = []
    for key in config.evidence_scalar_keys:
        _append_evidence(
            evidence,
            text=scalar_value(node, key),
            field=key,
            source=source,
            category=config.category,
            slug=slug,
            source_date=source_date,
            assessed_as_of=assessed_as_of,
            confidence=item.get("confidence"),
            value_level=str(item.get("value_level") or "medium"),
            evidence_type=evidence_type,
        )
    for key in config.evidence_list_keys:
        for idx, text in enumerate(list_value(node, key)):
            _append_evidence(
                evidence,
                text=text,
                field=f"{key}[{idx}]",
                source=source,
                category=config.category,
                slug=slug,
                source_date=source_date,
                assessed_as_of=assessed_as_of,
                confidence=item.get("confidence"),
                value_level=str(item.get("value_level") or "medium"),
                evidence_type=evidence_type,
            )
    supporting = item.get("supporting_snippet")
    if isinstance(supporting, str):
        _append_evidence(
            evidence,
            text=supporting,
            field="supporting_snippet",
            source=source,
            category=config.category,
            slug=slug,
            source_date=source_date,
            assessed_as_of=assessed_as_of,
            confidence=item.get("confidence"),
            value_level=str(item.get("value_level") or "medium"),
            evidence_type=evidence_type,
            provenance="snippet",
        )
    if config.category == "impl_study":
        evidence.extend(
            _impl_study_evidence(
                item=item,
                source=source,
                slug=slug,
                source_date=source_date,
                assessed_as_of=assessed_as_of,
                evidence_type=evidence_type,
            )
        )
    return _dedupe_evidence(evidence)


def _individual_evidence(
    *,
    node: dict[str, Any],
    category: str,
    slug: str,
    source: SourceRecord,
    source_date: str,
    assessed_as_of: str,
    evidence_type: str,
) -> list[EvidenceItem]:
    """Create evidence items for a signal or interview insight."""
    item = llm_item(node)
    evidence: list[EvidenceItem] = []
    for key in (
        "summary",
        "why_it_matters",
        "operational_relevance",
        "service_automation_relevance",
    ):
        _append_evidence(
            evidence,
            text=scalar_value(node, key),
            field=key,
            source=source,
            category=category,
            slug=slug,
            source_date=source_date,
            assessed_as_of=assessed_as_of,
            confidence=item.get("confidence"),
            value_level=str(item.get("value_level") or "medium"),
            evidence_type=evidence_type,
        )
    for key in ("evidence_snippets", "contrarian_or_speculative_claims"):
        for idx, text in enumerate(list_value(node, key)):
            _append_evidence(
                evidence,
                text=text,
                field=f"{key}[{idx}]",
                source=source,
                category=category,
                slug=slug,
                source_date=source_date,
                assessed_as_of=assessed_as_of,
                confidence=item.get("confidence"),
                value_level=str(item.get("value_level") or "medium"),
                evidence_type=evidence_type,
                provenance=(
                    "contradiction" if key == "contrarian_or_speculative_claims" else "snippet"
                ),
            )
    return _dedupe_evidence(evidence)


def _append_evidence(
    evidence: list[EvidenceItem],
    *,
    text: str,
    field: str,
    source: SourceRecord,
    category: str,
    slug: str,
    source_date: str,
    assessed_as_of: str,
    confidence: object,
    value_level: str,
    evidence_type: str,
    provenance: str = "stated",
) -> None:
    """Append a non-empty evidence item."""
    item = make_evidence_item(
        text=text,
        source_id=source.source_id,
        source_title=source.title,
        source_date=source_date,
        published_date=source.published_date,
        assessed_as_of=assessed_as_of,
        ingested_at=source.ingested_at,
        category=category,
        entity_slug=slug,
        confidence=confidence,
        value_level=value_level,
        provenance=provenance,
        evidence_type=evidence_type,
        field=field,
    )
    if item is not None:
        evidence.append(item)


def _impl_study_evidence(
    *,
    item: dict[str, Any],
    source: SourceRecord,
    slug: str,
    source_date: str,
    assessed_as_of: str,
    evidence_type: str,
) -> list[EvidenceItem]:
    """Return structured implementation-study evidence snippets."""
    raw = item.get("evidence_snippets")
    if not isinstance(raw, list):
        return []
    output: list[EvidenceItem] = []
    for idx, snippet in enumerate(raw):
        if not isinstance(snippet, dict):
            continue
        snippet_dict = cast(dict[str, object], snippet)
        claim = str(snippet_dict.get("claim") or "").strip()
        text = str(snippet_dict.get("snippet") or "").strip()
        combined = f"{claim} — {text}" if claim and text else claim or text
        _append_evidence(
            output,
            text=combined,
            field=f"evidence_snippets[{idx}]",
            source=source,
            category="impl_study",
            slug=slug,
            source_date=source_date,
            assessed_as_of=assessed_as_of,
            confidence=item.get("confidence"),
            value_level=str(item.get("value_level") or "medium"),
            evidence_type=evidence_type,
            provenance=str(snippet_dict.get("provenance") or "stated"),
        )
    return output


def _node_slug(node: dict[str, Any], config: EntityConfig, title: str) -> str:
    """Return the effective slug for a proposal node."""
    if config.slug_key:
        raw = scalar_value(node, config.slug_key)
        if raw:
            return slugify(raw)
    return slugify(title)


def _aliases_for_node(node: dict[str, Any], slug: str, title: str) -> list[str]:
    """Return lightweight aliases from non-canonical slugs/titles."""
    aliases: list[str] = []
    raw_item = llm_item(node)
    for key in ("topic_slug", "trend_slug"):
        raw = raw_item.get(key)
        if isinstance(raw, str) and raw and slugify(raw) != slug:
            aliases.append(raw)
    for key in (
        "topic_title",
        "trend_title",
        "term",
        "name",
        "model_name",
        "question_title",
        "title",
    ):
        raw = raw_item.get(key)
        if isinstance(raw, str) and raw.strip() and raw.strip() != title:
            aliases.append(raw.strip())
    return _dedupe_text(aliases)


def _match_candidates(item: dict[str, Any]) -> list[dict[str, object]]:
    """Return normalized match candidates."""
    raw = item.get("match_candidates")
    if not isinstance(raw, list):
        return []
    return [candidate for candidate in raw if isinstance(candidate, dict)]


def _confidence(item: dict[str, Any]) -> float | None:
    """Return numeric confidence when stored as a float."""
    raw = item.get("confidence")
    if isinstance(raw, int | float):
        return float(raw)
    return None


def _source_date(published_date: str, assessed_as_of: str) -> str:
    """Return primary temporal anchor."""
    return published_date or assessed_as_of


def _dedupe_text(values: list[str]) -> list[str]:
    """Deduplicate non-empty strings preserving order."""
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        clean = value.strip()
        if clean and clean not in seen:
            seen.add(clean)
            output.append(clean)
    return output


def _dedupe_evidence(values: list[EvidenceItem]) -> list[EvidenceItem]:
    """Deduplicate evidence by stable id preserving order."""
    seen: set[str] = set()
    output: list[EvidenceItem] = []
    for item in values:
        if item.evidence_id not in seen:
            seen.add(item.evidence_id)
            output.append(item)
    return output
