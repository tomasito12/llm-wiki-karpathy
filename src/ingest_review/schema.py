"""Pydantic models for LLM classification output and JSON schema export."""

from __future__ import annotations

from typing import Any, Literal, cast

from pydantic import BaseModel, Field, field_validator, model_validator

from src.ingest_review.tags import MAX_PROPOSED_TAGS as _MAX_PROPOSED_TAGS
from src.ingest_review.tags import normalize_tag, normalize_tag_list

ARTIFACT_SCHEMA_VERSION = 15
PROMPT_VERSION = "29"
MAX_PROPOSED_TAGS = 5

SuggestedAction = Literal["create", "update", "ignore", "append_to_existing", "create_new_page"]
MatchKind = Literal["exact", "fuzzy", "none"]
ValueLevel = Literal["high", "medium", "low"]

EvidenceType = Literal[
    "vendor_claim",
    "independent_analysis",
    "benchmark",
    "user_report",
    "implementation_case",
    "research_result",
    "expert_opinion",
    "speculative_claim",
    "mixed",
    "unknown",
]


def normalize_glossary_term_capitalization(term: str) -> str:
    """Uppercase the first alphabetic character (e.g. ``frontmatter`` → ``Frontmatter``).

    Leaves terms that already start with an uppercase letter or non-letter unchanged.
    """
    s = term.strip()
    if not s:
        return s
    for i, ch in enumerate(s):
        if ch.isalpha():
            if ch.islower():
                return s[:i] + ch.upper() + s[i + 1 :]
            return s
    return s


EVIDENCE_TYPE_VALUES: tuple[str, ...] = (
    "vendor_claim",
    "independent_analysis",
    "benchmark",
    "user_report",
    "implementation_case",
    "research_result",
    "expert_opinion",
    "speculative_claim",
    "mixed",
    "unknown",
)

EVIDENCE_TYPE_SET: frozenset[str] = frozenset(EVIDENCE_TYPE_VALUES)


def normalize_evidence_type(raw: object) -> str:
    """Return *raw* if it is a valid evidence type label, else ``\"unknown\"``."""
    s = str(raw).strip() if raw is not None else ""
    return s if s in EVIDENCE_TYPE_SET else "unknown"


# String fields under ``source_summary`` that use ``{status, final_text, notes}`` review nodes.
SOURCE_SUMMARY_SCALAR_KEYS: tuple[str, ...] = (
    "summary",
    "accessible_overview",
    "why_it_matters",
    "limitations_and_open_questions",
    "contradictions_and_skepticism",
)

# Sections that support per-section LLM regeneration in the review dashboard.
REGENERATABLE_SOURCE_SECTION_KEYS: tuple[str, ...] = SOURCE_SUMMARY_SCALAR_KEYS + (
    "key_insights",
    "sources",
)


class MatchCandidate(BaseModel):
    """Possible existing wiki page match from the LLM."""

    title_or_slug: str = ""
    match_kind: MatchKind = "none"
    confidence: float = Field(0.0, ge=0.0, le=1.0)


class SourceSummaryBlock(BaseModel):
    """Structured source chapters for human review (JSON in review artifact)."""

    summary: str = ""
    accessible_overview: str = Field(
        "",
        description="Plain-language 'Easy read' for newcomers: 7–10 sentences, no abbreviations.",
    )
    key_insights: list[str] = Field(
        default_factory=list,
        description="Up to 5 concise bullets: actionable, non-obvious, non-generic.",
    )
    why_it_matters: str = Field(
        "",
        description="Unified significance: industry/engineering relevance, operational "
        "implications when substantiated, and time-bounded practical judgment.",
    )
    limitations_and_open_questions: str = ""
    contradictions_and_skepticism: str = ""
    assessed_as_of: str = Field(
        "",
        description="Source publication date; anchors all temporal judgments in this block.",
    )
    sources: list[str] = Field(default_factory=list)

    @field_validator("key_insights", mode="before")
    @classmethod
    def _coerce_key_insights(cls, v: object) -> list[str]:
        """Accept legacy string from JSON and split into bullets."""
        if isinstance(v, str):
            lines: list[str] = []
            for ln in v.splitlines():
                t = ln.strip().lstrip("-•* ").strip()
                if t:
                    lines.append(t)
            if not lines and v.strip():
                lines = [v.strip()]
            return lines[:5]
        if v is None:
            return []
        if isinstance(v, list):
            out = [str(x).strip() for x in v if str(x).strip()]
            return out[:5]
        return []

    @field_validator("key_insights")
    @classmethod
    def _cap_insights(cls, v: list[str]) -> list[str]:
        return v[:5]


def normalize_source_summary(block: SourceSummaryBlock) -> SourceSummaryBlock:
    """Trim whitespace and cap key_insights length after parsing."""
    ki = [s.strip() for s in block.key_insights if s.strip()][:5]
    return block.model_copy(
        update={
            "summary": block.summary.strip(),
            "accessible_overview": block.accessible_overview.strip(),
            "key_insights": ki,
            "why_it_matters": block.why_it_matters.strip(),
            "limitations_and_open_questions": block.limitations_and_open_questions.strip(),
            "contradictions_and_skepticism": block.contradictions_and_skepticism.strip(),
            "assessed_as_of": block.assessed_as_of.strip(),
            "sources": [s.strip() for s in block.sources if isinstance(s, str) and s.strip()],
        }
    )


class SectionRegenerateOutput(BaseModel):
    """Minimal JSON returned by per-section regeneration."""

    section_key: str = ""
    content: str | list[str] = ""


class GlossaryTagSuggestOutput(BaseModel):
    """LLM suggestion for registry tag(s) not covered by the allowlist."""

    suggested_tag: str = Field(
        "",
        description="Single kebab-case tag slug, or empty if no new tag is warranted.",
    )
    suggested_tags: list[str] = Field(
        default_factory=list,
        description="Optional list form; merged with suggested_tag on validate.",
    )

    @model_validator(mode="after")
    def _merge_suggested_tags(self) -> GlossaryTagSuggestOutput:
        tags = normalize_tag_list(self.suggested_tags, cap=0)
        single = normalize_tag(self.suggested_tag)
        if single and single not in tags:
            tags.insert(0, single)
        object.__setattr__(self, "suggested_tags", tags)
        object.__setattr__(self, "suggested_tag", tags[0] if tags else "")
        return self


def _coerce_multitag_proposal_data(data: Any) -> Any:
    """Before-validator: build proposed_tags / suggested_new_tags from legacy scalars."""
    if not isinstance(data, dict):
        return data
    out = dict(data)
    proposed = out.get("proposed_tags")
    if not isinstance(proposed, list) or not proposed:
        legacy: list[str] = []
        for key in ("primary_tag", "secondary_tag"):
            t = normalize_tag(str(out.get(key) or ""))
            if t and t not in legacy:
                legacy.append(t)
        proposed = legacy
    out["proposed_tags"] = normalize_tag_list(proposed, cap=_MAX_PROPOSED_TAGS)

    snt = out.get("suggested_new_tags")
    if not isinstance(snt, list) or not snt:
        snt = []
        sn = normalize_tag(str(out.get("suggested_new_tag") or ""))
        if sn:
            snt = [sn]
    out["suggested_new_tags"] = normalize_tag_list(snt, cap=0)

    pts: list[str] = out["proposed_tags"]
    out["primary_tag"] = pts[0] if pts else normalize_tag(str(out.get("primary_tag") or ""))
    out["secondary_tag"] = (
        pts[1] if len(pts) > 1 else normalize_tag(str(out.get("secondary_tag") or ""))
    )
    sns: list[str] = out["suggested_new_tags"]
    if sns and not normalize_tag(str(out.get("suggested_new_tag") or "")):
        out["suggested_new_tag"] = sns[0]
    return out


class GlossaryProposal(BaseModel):
    """One glossary term proposal from the LLM."""

    term: str = ""
    proposed_definition: str = ""
    extended_explanation: str = ""
    supporting_snippet: str = ""
    relevance_note: str = Field(
        "",
        description="Durable industry/operational relevance — NOT article-specific context.",
    )
    related_terms: list[str] = Field(default_factory=list)
    proposed_tags: list[str] = Field(default_factory=list)
    suggested_new_tags: list[str] = Field(default_factory=list)
    primary_tag: str = ""
    secondary_tag: str = ""
    suggested_new_tag: str = ""
    match_candidates: list[MatchCandidate] = Field(default_factory=list)
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    suggested_action: SuggestedAction = "ignore"
    value_level: ValueLevel = "medium"
    evidence_type: EvidenceType | None = None

    @model_validator(mode="before")
    @classmethod
    def _coerce_tags(cls, data: Any) -> Any:
        return _coerce_multitag_proposal_data(data)

    @field_validator("term", mode="before")
    @classmethod
    def _normalize_glossary_term_capitalization(cls, v: object) -> str:
        if v is None:
            return ""
        return normalize_glossary_term_capitalization(str(v))


GLOSSARY_SCALAR_KEYS: tuple[str, ...] = (
    "term",
    "proposed_definition",
    "extended_explanation",
    "supporting_snippet",
    "relevance_note",
)

GLOSSARY_LIST_KEYS: tuple[str, ...] = ("related_terms",)

GLOSSARY_REVIEWABLE_SCALAR_KEYS: tuple[str, ...] = (
    "term",
    "proposed_definition",
    "extended_explanation",
    "relevance_note",
)

GLOSSARY_REVIEWABLE_LIST_KEYS: tuple[str, ...] = ()


class TopicContribution(BaseModel):
    """Reusable operational knowledge contribution for a stable conceptual domain."""

    topic_slug: str = ""
    topic_title: str = ""
    knowledge_summary: str = ""
    examples: str = ""
    operational_insight: str = ""
    supporting_snippet: str = ""
    relevance_note: str = Field(
        "",
        description="Durable industry/operational relevance for the topic — NOT "
        "article-specific context or what the source emphasizes.",
    )
    key_points: list[str] = Field(default_factory=list)
    related_topics: list[str] = Field(
        default_factory=list,
        description="Kebab-case topic_slug cross-references to other topic pages — "
        "never TOPIC_TAGS_ALLOWLIST routing tags.",
    )
    proposed_tags: list[str] = Field(default_factory=list)
    suggested_new_tags: list[str] = Field(default_factory=list)
    primary_tag: str = ""
    secondary_tag: str = ""
    suggested_new_tag: str = ""
    match_candidates: list[MatchCandidate] = Field(default_factory=list)
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    suggested_action: SuggestedAction = "ignore"
    value_level: ValueLevel = "medium"
    evidence_type: EvidenceType | None = None

    @model_validator(mode="before")
    @classmethod
    def _coerce_tags(cls, data: Any) -> Any:
        return _coerce_multitag_proposal_data(data)


TOPIC_SCALAR_KEYS: tuple[str, ...] = (
    "topic_slug",
    "topic_title",
    "knowledge_summary",
    "examples",
    "operational_insight",
    "supporting_snippet",
    "relevance_note",
)

TOPIC_LIST_KEYS: tuple[str, ...] = (
    "key_points",
    "related_topics",
)

TOPIC_REVIEWABLE_SCALAR_KEYS: tuple[str, ...] = (
    "topic_slug",
    "topic_title",
    "knowledge_summary",
    "examples",
    "operational_insight",
    "relevance_note",
)

TOPIC_REVIEWABLE_LIST_KEYS: tuple[str, ...] = ("key_points", "related_topics")


class TopicRegenerateOutput(BaseModel):
    """JSON returned by per-topic regeneration under a reviewer-supplied title."""

    knowledge_summary: str = ""
    examples: str = ""
    operational_insight: str = ""
    relevance_note: str = ""
    key_points: list[str] = Field(default_factory=list)
    supporting_snippet: str = ""
    related_topics: list[str] = Field(default_factory=list)
    match_candidates: list[MatchCandidate] = Field(default_factory=list)
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    suggested_action: SuggestedAction = "ignore"
    value_level: ValueLevel = "medium"
    evidence_type: EvidenceType | None = None


class GlossaryRegenerateOutput(BaseModel):
    """JSON returned by per-glossary-term regeneration (no term field)."""

    proposed_definition: str = ""
    extended_explanation: str = ""
    relevance_note: str = ""
    supporting_snippet: str = ""
    match_candidates: list[MatchCandidate] = Field(default_factory=list)
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    suggested_action: SuggestedAction = "ignore"
    value_level: ValueLevel = "medium"
    evidence_type: EvidenceType | None = None


class HowToRegenerateOutput(BaseModel):
    """JSON returned by per-how-to regeneration (no question_title field)."""

    what_and_problem: str = ""
    answer_summary: str = ""
    caveats: str = ""
    implementation_steps: list[str] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)
    related_howtos: list[str] = Field(default_factory=list)
    match_candidates: list[MatchCandidate] = Field(default_factory=list)
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    suggested_action: SuggestedAction = "ignore"
    value_level: ValueLevel = "medium"
    evidence_type: EvidenceType | None = None


class TrendRegenerateOutput(BaseModel):
    """JSON returned by per-trend regeneration (no trend_title or trend_slug)."""

    trend_description: str = ""
    evidence_from_source: str = ""
    time_sensitivity: str = ""
    uncertainty_note: str = ""
    assessed_as_of: str = ""
    supporting_snippet: str = ""
    supporting_data_points: list[str] = Field(default_factory=list)
    related_trends: list[str] = Field(default_factory=list)
    match_candidates: list[MatchCandidate] = Field(default_factory=list)
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    suggested_action: SuggestedAction = "ignore"
    value_level: ValueLevel = "medium"
    evidence_type: EvidenceType | None = None


class ToolRegenerateOutput(BaseModel):
    """JSON returned by per-tool regeneration (no name field)."""

    short_description: str = ""
    operational_relevance: str = ""
    strengths: str = ""
    weaknesses_limitations: str = ""
    maturity_signals: str = ""
    supporting_snippet: str = ""
    core_capabilities: list[str] = Field(default_factory=list)
    integration_ecosystem: list[str] = Field(default_factory=list)
    related_tools: list[str] = Field(default_factory=list)
    match_candidates: list[MatchCandidate] = Field(default_factory=list)
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    suggested_action: SuggestedAction = "ignore"
    value_level: ValueLevel = "medium"
    evidence_type: EvidenceType | None = None


class ModelRegenerateOutput(BaseModel):
    """JSON returned by per-model regeneration (no model_name field)."""

    provider: str = ""
    operational_summary: str = ""
    strengths: str = ""
    weaknesses_limitations: str = ""
    workflow_implications: str = ""
    service_automation_implications: str = ""
    maturity_signals: str = ""
    pricing_inference_implications: str = ""
    supporting_snippet: str = ""
    core_capabilities: list[str] = Field(default_factory=list)
    benchmark_observations: list[str] = Field(default_factory=list)
    comparative_observations: list[str] = Field(default_factory=list)
    related_models: list[str] = Field(default_factory=list)
    match_candidates: list[MatchCandidate] = Field(default_factory=list)
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    suggested_action: SuggestedAction = "ignore"
    value_level: ValueLevel = "medium"
    evidence_type: EvidenceType | None = None


class ImplStudyRegenerateOutput(BaseModel):
    """JSON returned by per-implementation-study regeneration (no title field)."""

    company: str = ""
    industry: str = ""
    overview: str = ""
    what_was_implemented: str = ""
    business_objective: str = ""
    technical_approach: str = ""
    deployment_context: str = ""
    outcome_status: str = ""
    success_or_failure_factors: str = ""
    operational_constraints: str = ""
    ai_model_observations: str = ""
    implications_for_service_automation: str = ""
    strategic_signals: str = ""
    key_lessons: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    related_sources: list[str] = Field(default_factory=list)
    match_candidates: list[MatchCandidate] = Field(default_factory=list)
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    suggested_action: SuggestedAction = "ignore"
    value_level: ValueLevel = "medium"
    evidence_type: EvidenceType | None = None


class ToolProposal(BaseModel):
    """Operational intelligence about a tool extracted from a source."""

    name: str = ""
    short_description: str = ""
    operational_relevance: str = ""
    strengths: str = ""
    weaknesses_limitations: str = ""
    maturity_signals: str = ""
    supporting_snippet: str = ""
    core_capabilities: list[str] = Field(default_factory=list)
    integration_ecosystem: list[str] = Field(default_factory=list)
    related_tools: list[str] = Field(default_factory=list)
    proposed_types: list[str] = Field(default_factory=list)
    proposed_new_type: str | None = None
    match_candidates: list[MatchCandidate] = Field(default_factory=list)
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    suggested_action: SuggestedAction = "ignore"
    value_level: ValueLevel = "medium"
    evidence_type: EvidenceType | None = None


TOOL_SCALAR_KEYS: tuple[str, ...] = (
    "name",
    "short_description",
    "operational_relevance",
    "strengths",
    "weaknesses_limitations",
    "maturity_signals",
    "supporting_snippet",
)

TOOL_LIST_KEYS: tuple[str, ...] = (
    "core_capabilities",
    "integration_ecosystem",
    "related_tools",
)

TOOL_REVIEWABLE_SCALAR_KEYS: tuple[str, ...] = (
    "name",
    "short_description",
    "operational_relevance",
    "strengths",
    "weaknesses_limitations",
    "maturity_signals",
)

TOOL_REVIEWABLE_LIST_KEYS: tuple[str, ...] = (
    "core_capabilities",
    "integration_ecosystem",
)


class FoundationModelProposal(BaseModel):
    """Operational intelligence about a foundation model extracted from a source."""

    model_name: str = ""
    provider: str = ""
    operational_summary: str = ""
    strengths: str = ""
    weaknesses_limitations: str = ""
    workflow_implications: str = ""
    service_automation_implications: str = ""
    maturity_signals: str = ""
    pricing_inference_implications: str = ""
    supporting_snippet: str = ""
    core_capabilities: list[str] = Field(default_factory=list)
    benchmark_observations: list[str] = Field(default_factory=list)
    comparative_observations: list[str] = Field(default_factory=list)
    related_models: list[str] = Field(default_factory=list)
    proposed_types: list[str] = Field(default_factory=list)
    proposed_new_type: str | None = None
    match_candidates: list[MatchCandidate] = Field(default_factory=list)
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    suggested_action: SuggestedAction = "ignore"
    value_level: ValueLevel = "medium"
    evidence_type: EvidenceType | None = None


MODEL_SCALAR_KEYS: tuple[str, ...] = (
    "model_name",
    "provider",
    "operational_summary",
    "strengths",
    "weaknesses_limitations",
    "workflow_implications",
    "service_automation_implications",
    "maturity_signals",
    "pricing_inference_implications",
    "supporting_snippet",
)

MODEL_LIST_KEYS: tuple[str, ...] = (
    "core_capabilities",
    "benchmark_observations",
    "comparative_observations",
    "related_models",
)

MODEL_REVIEWABLE_SCALAR_KEYS: tuple[str, ...] = (
    "model_name",
    "provider",
    "operational_summary",
    "strengths",
    "weaknesses_limitations",
    "workflow_implications",
    "service_automation_implications",
    "maturity_signals",
    "pricing_inference_implications",
)

MODEL_REVIEWABLE_LIST_KEYS: tuple[str, ...] = (
    "core_capabilities",
    "benchmark_observations",
    "comparative_observations",
)


class HowToProposal(BaseModel):
    """Procedural/implementation knowledge extracted from a source."""

    question_title: str = ""
    what_and_problem: str = ""
    answer_summary: str = ""
    supporting_snippet: str = ""
    caveats: str = ""
    implementation_steps: list[str] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)
    related_howtos: list[str] = Field(default_factory=list)
    proposed_tags: list[str] = Field(default_factory=list)
    suggested_new_tags: list[str] = Field(default_factory=list)
    primary_tag: str = ""
    secondary_tag: str = ""
    suggested_new_tag: str = ""
    match_candidates: list[MatchCandidate] = Field(default_factory=list)
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    suggested_action: SuggestedAction = "ignore"
    value_level: ValueLevel = "medium"
    evidence_type: EvidenceType | None = None

    @model_validator(mode="before")
    @classmethod
    def _coerce_tags(cls, data: Any) -> Any:
        return _coerce_multitag_proposal_data(data)


HOWTO_SCALAR_KEYS: tuple[str, ...] = (
    "question_title",
    "what_and_problem",
    "answer_summary",
    "supporting_snippet",
    "caveats",
)

HOWTO_LIST_KEYS: tuple[str, ...] = (
    "implementation_steps",
    "prerequisites",
    "related_howtos",
)

HOWTO_REVIEWABLE_SCALAR_KEYS: tuple[str, ...] = (
    "question_title",
    "what_and_problem",
    "answer_summary",
    "caveats",
)

HOWTO_REVIEWABLE_LIST_KEYS: tuple[str, ...] = (
    "implementation_steps",
    "prerequisites",
)


class EvidenceSnippet(BaseModel):
    """Source-grounded evidence for an implementation-study claim."""

    claim: str = ""
    snippet: str = ""
    provenance: Literal["stated", "inferred", "interpretation"] = "stated"


class ImplementationStudyProposal(BaseModel):
    """Rich implementation-study proposal extracted from a source."""

    title: str = ""
    company: str = ""
    industry: str = ""
    overview: str = ""
    what_was_implemented: str = ""
    business_objective: str = ""
    technical_approach: str = ""
    deployment_context: str = ""
    outcome_status: str = ""
    success_or_failure_factors: str = ""
    operational_constraints: str = ""
    ai_model_observations: str = ""
    implications_for_service_automation: str = ""
    strategic_signals: str = ""
    key_lessons: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    related_sources: list[str] = Field(default_factory=list)
    evidence_snippets: list[EvidenceSnippet] = Field(default_factory=list)
    proposed_tags: list[str] = Field(default_factory=list)
    suggested_new_tags: list[str] = Field(default_factory=list)
    primary_tag: str = ""
    secondary_tag: str = ""
    suggested_new_tag: str = ""
    match_candidates: list[MatchCandidate] = Field(default_factory=list)
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    suggested_action: SuggestedAction = "ignore"
    value_level: ValueLevel = "medium"
    evidence_type: EvidenceType | None = None

    @model_validator(mode="before")
    @classmethod
    def _coerce_tags(cls, data: Any) -> Any:
        return _coerce_multitag_proposal_data(data)


IMPL_STUDY_SCALAR_KEYS: tuple[str, ...] = (
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
)

IMPL_STUDY_LIST_KEYS: tuple[str, ...] = (
    "key_lessons",
    "open_questions",
    "related_sources",
)

IMPL_STUDY_REVIEWABLE_SCALAR_KEYS: tuple[str, ...] = IMPL_STUDY_SCALAR_KEYS

IMPL_STUDY_REVIEWABLE_LIST_KEYS: tuple[str, ...] = (
    "key_lessons",
    "open_questions",
)


class IndustryTrendProposal(BaseModel):
    """Time-sensitive industry trend or pattern supported by the article."""

    trend_slug: str = ""
    trend_title: str = ""
    trend_description: str = ""
    evidence_from_source: str = ""
    time_sensitivity: str = ""
    uncertainty_note: str = ""
    assessed_as_of: str = Field(
        "",
        description="Source publication date; anchors all temporal judgments in this block.",
    )
    supporting_snippet: str = ""
    supporting_data_points: list[str] = Field(default_factory=list)
    related_trends: list[str] = Field(
        default_factory=list,
        description="Kebab-case trend_slug cross-references to other trend pages.",
    )
    proposed_tags: list[str] = Field(default_factory=list)
    suggested_new_tags: list[str] = Field(default_factory=list)
    primary_tag: str = ""
    secondary_tag: str = ""
    suggested_new_tag: str = ""
    match_candidates: list[MatchCandidate] = Field(default_factory=list)
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    suggested_action: SuggestedAction = "ignore"
    value_level: ValueLevel = "medium"
    evidence_type: EvidenceType | None = None

    @model_validator(mode="before")
    @classmethod
    def _coerce_tags(cls, data: Any) -> Any:
        return _coerce_multitag_proposal_data(data)


TREND_SCALAR_KEYS: tuple[str, ...] = (
    "trend_slug",
    "trend_title",
    "trend_description",
    "evidence_from_source",
    "time_sensitivity",
    "uncertainty_note",
    "supporting_snippet",
)

TREND_LIST_KEYS: tuple[str, ...] = (
    "supporting_data_points",
    "related_trends",
)

TREND_REVIEWABLE_SCALAR_KEYS: tuple[str, ...] = (
    "trend_slug",
    "trend_title",
    "trend_description",
    "evidence_from_source",
    "time_sensitivity",
    "uncertainty_note",
)

TREND_REVIEWABLE_LIST_KEYS: tuple[str, ...] = ("supporting_data_points",)


SourceType = Literal[
    "standard_article",
    "ai_industry_roundup",
    "ai_tools_roundup",
    "interview_or_transcript",
    "technical_howto",
    "research_paper_or_report",
    "unknown",
]

SignalStrength = Literal["low", "medium", "high"]
TimeHorizon = Literal["transient", "short_term", "medium_term", "long_term"]
WikiWorthiness = Literal["ignore", "weak_candidate", "review_candidate", "strong_candidate"]

SignalType = Literal[
    "trend",
    "topic",
    "tool",
    "model",
    "howto",
    "research_eval",
    "infrastructure",
    "pricing_economics",
    "ignore",
]

InsightConfidence = Literal["low", "medium", "high"]
DurabilityEstimate = Literal["transient", "medium_term", "long_term"]

InsightType = Literal[
    "topic",
    "trend",
    "model",
    "tool",
    "infrastructure",
    "orchestration",
    "service_automation",
    "privacy_security",
    "research_eval",
    "ignore",
]


class SourceTypeDetection(BaseModel):
    """Automatic detection of the source content type."""

    detected_source_type: SourceType = "unknown"
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    reasoning: list[str] = Field(default_factory=list)


class SourceEvidenceProfile(BaseModel):
    """Dominant evidence basis for the source as a whole."""

    primary_evidence_type: EvidenceType = "unknown"
    reasoning: list[str] = Field(
        default_factory=list,
        description="1–3 bullets: why this source's claims are mainly this evidence type.",
    )


class RoundupSignal(BaseModel):
    """One durable operational signal extracted from an AI industry roundup."""

    signal_title: str = ""
    signal_type: SignalType = "ignore"
    summary: str = ""
    why_it_matters: str = ""
    operational_relevance: str = ""
    service_automation_relevance: str = ""
    signal_strength: SignalStrength = "low"
    time_horizon: TimeHorizon = "transient"
    wiki_worthiness: WikiWorthiness = "ignore"
    assessed_as_of: str = Field(
        "",
        description="Source publication date; anchors all temporal judgments in this block.",
    )

    proposed_tags: list[str] = Field(default_factory=list)
    suggested_new_tags: list[str] = Field(default_factory=list)
    primary_tag: str = ""
    secondary_tag: str = ""
    suggested_new_tag: str = ""
    suggested_destinations: list[str] = Field(default_factory=list)
    mentioned_entities: list[str] = Field(default_factory=list)
    evidence_snippets: list[str] = Field(default_factory=list)
    value_level: ValueLevel = "medium"
    evidence_type: EvidenceType | None = None

    @model_validator(mode="before")
    @classmethod
    def _coerce_tags(cls, data: Any) -> Any:
        return _coerce_multitag_proposal_data(data)


SIGNAL_SCALAR_KEYS: tuple[str, ...] = (
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

SIGNAL_LIST_KEYS: tuple[str, ...] = (
    "suggested_destinations",
    "mentioned_entities",
    "evidence_snippets",
)

SIGNAL_REVIEWABLE_SCALAR_KEYS: tuple[str, ...] = SIGNAL_SCALAR_KEYS

SIGNAL_REVIEWABLE_LIST_KEYS: tuple[str, ...] = SIGNAL_LIST_KEYS


class InterviewInsight(BaseModel):
    """One durable operational insight extracted from an interview or transcript."""

    insight_title: str = ""
    insight_type: InsightType = "ignore"
    summary: str = ""
    why_it_matters: str = ""
    operational_relevance: str = ""
    service_automation_relevance: str = ""
    confidence: InsightConfidence = "low"
    durability_estimate: DurabilityEstimate = "transient"
    wiki_worthiness: WikiWorthiness = "ignore"
    assessed_as_of: str = Field(
        "",
        description="Source publication date; anchors all temporal judgments in this block.",
    )

    proposed_tags: list[str] = Field(default_factory=list)
    suggested_new_tags: list[str] = Field(default_factory=list)
    primary_tag: str = ""
    secondary_tag: str = ""
    suggested_new_tag: str = ""
    suggested_destinations: list[str] = Field(default_factory=list)
    mentioned_entities: list[str] = Field(default_factory=list)
    contrarian_or_speculative_claims: list[str] = Field(default_factory=list)
    evidence_snippets: list[str] = Field(default_factory=list)
    value_level: ValueLevel = "medium"
    evidence_type: EvidenceType | None = None

    @model_validator(mode="before")
    @classmethod
    def _coerce_tags(cls, data: Any) -> Any:
        return _coerce_multitag_proposal_data(data)


INSIGHT_SCALAR_KEYS: tuple[str, ...] = (
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

INSIGHT_LIST_KEYS: tuple[str, ...] = (
    "suggested_destinations",
    "mentioned_entities",
    "contrarian_or_speculative_claims",
    "evidence_snippets",
)

INSIGHT_REVIEWABLE_SCALAR_KEYS: tuple[str, ...] = INSIGHT_SCALAR_KEYS

INSIGHT_REVIEWABLE_LIST_KEYS: tuple[str, ...] = INSIGHT_LIST_KEYS


class ExtractionMeta(BaseModel):
    """LLM self-assessment of the extraction pass."""

    skip_recommended: bool = False
    skip_reason: str = ""
    total_candidates_considered: int = 0
    review_burden_estimate: Literal["light", "moderate", "heavy"] = "moderate"


class LlmClassificationOutput(BaseModel):
    """Root object returned by the ingestion analysis LLM."""

    @model_validator(mode="before")
    @classmethod
    def _coerce_proposal_evidence_types(cls, data: Any) -> Any:
        """Drop invalid per-proposal evidence_type overrides before nested validation."""
        if not isinstance(data, dict):
            return data
        profile = data.get("source_evidence_profile")
        if isinstance(profile, dict):
            et = profile.get("primary_evidence_type")
            s = str(et).strip() if et is not None else ""
            profile["primary_evidence_type"] = s if s in EVIDENCE_TYPE_SET else "unknown"
        for key in (
            "glossary",
            "tools",
            "foundation_models",
            "how_to",
            "topics",
            "implementation_studies",
            "industry_trends",
            "roundup_signals",
            "interview_insights",
        ):
            items = data.get(key)
            if not isinstance(items, list):
                continue
            for item in items:
                if not isinstance(item, dict):
                    continue
                if "evidence_type" not in item:
                    continue
                et = item.get("evidence_type")
                if et is None:
                    item.pop("evidence_type", None)
                    continue
                s = str(et).strip()
                if s in EVIDENCE_TYPE_SET:
                    item["evidence_type"] = s
                else:
                    item.pop("evidence_type", None)
        return data

    extraction_meta: ExtractionMeta = Field(default_factory=ExtractionMeta)
    source_summary: SourceSummaryBlock = Field(default_factory=SourceSummaryBlock)
    source_type_detection: SourceTypeDetection = Field(default_factory=SourceTypeDetection)
    source_evidence_profile: SourceEvidenceProfile = Field(default_factory=SourceEvidenceProfile)
    glossary: list[GlossaryProposal] = Field(default_factory=list)
    tools: list[ToolProposal] = Field(default_factory=list)
    foundation_models: list[FoundationModelProposal] = Field(default_factory=list)
    how_to: list[HowToProposal] = Field(default_factory=list)
    topics: list[TopicContribution] = Field(default_factory=list)
    implementation_studies: list[ImplementationStudyProposal] = Field(default_factory=list)
    industry_trends: list[IndustryTrendProposal] = Field(default_factory=list)
    roundup_signals: list[RoundupSignal] = Field(default_factory=list)
    interview_insights: list[InterviewInsight] = Field(default_factory=list)


_CLASSIFICATION_SCHEMA_OMIT: frozenset[str] = frozenset({"suggested_action", "match_candidates"})


def _strip_properties_from_json_schema(node: object, omit: frozenset[str]) -> None:
    """Remove *omit* keys from ``properties`` / ``required`` recursively."""
    if isinstance(node, dict):
        obj = cast(dict[str, Any], node)
        props = obj.get("properties")
        if isinstance(props, dict):
            for key in omit:
                props.pop(key, None)
            required = obj.get("required")
            if isinstance(required, list):
                obj["required"] = [r for r in required if r not in omit]
        for value in obj.values():
            _strip_properties_from_json_schema(value, omit)
    elif isinstance(node, list):
        for item in node:
            _strip_properties_from_json_schema(item, omit)


def llm_output_json_schema() -> dict:
    """JSON schema dict for OpenAI structured outputs (full model)."""
    return LlmClassificationOutput.model_json_schema()


def llm_output_json_schema_for_classification() -> dict:
    """Classification prompt schema — omits deferred routing fields."""
    import copy

    schema = copy.deepcopy(LlmClassificationOutput.model_json_schema())
    _strip_properties_from_json_schema(schema, _CLASSIFICATION_SCHEMA_OMIT)
    return schema
