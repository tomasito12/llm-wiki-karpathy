"""Pydantic models for LLM classification output and JSON schema export."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

ARTIFACT_SCHEMA_VERSION = 2
PROMPT_VERSION = "2"

SuggestedAction = Literal["create", "update", "ignore"]
MatchKind = Literal["exact", "fuzzy", "none"]

# String fields under ``source_summary`` that use ``{status, final_text, notes}`` review nodes.
SOURCE_SUMMARY_SCALAR_KEYS: tuple[str, ...] = (
    "summary",
    "why_it_matters",
    "implications_automation",
    "practical_relevance",
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
    key_insights: list[str] = Field(
        default_factory=list,
        description="Up to 5 concise bullets: actionable, non-obvious, non-generic.",
    )
    why_it_matters: str = ""
    implications_automation: str = Field(
        "",
        description="Concrete implications for chatbots, voicebots, support automation; "
        "state explicitly if none.",
    )
    practical_relevance: str = Field(
        "",
        description="Short honest judgment (e.g. immediately useful, hype, incremental).",
    )
    limitations_and_open_questions: str = ""
    contradictions_and_skepticism: str = ""
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
            "key_insights": ki,
            "why_it_matters": block.why_it_matters.strip(),
            "implications_automation": block.implications_automation.strip(),
            "practical_relevance": block.practical_relevance.strip(),
            "limitations_and_open_questions": block.limitations_and_open_questions.strip(),
            "contradictions_and_skepticism": block.contradictions_and_skepticism.strip(),
            "sources": [s.strip() for s in block.sources if isinstance(s, str) and s.strip()],
        }
    )


class SectionRegenerateOutput(BaseModel):
    """Minimal JSON returned by per-section regeneration."""

    section_key: str = ""
    content: str | list[str] = ""


class GlossaryProposal(BaseModel):
    """One glossary term proposal from the LLM."""

    term: str = ""
    proposed_definition: str = ""
    supporting_snippet: str = ""
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    suggested_action: SuggestedAction = "ignore"
    match_candidates: list[MatchCandidate] = Field(default_factory=list)
    tag_gap_notes: str | None = None


class ToolProposal(BaseModel):
    """One tool proposal."""

    name: str = ""
    short_description: str = ""
    tool_type: str = ""
    supporting_snippet: str = ""
    match_candidates: list[MatchCandidate] = Field(default_factory=list)
    proposed_tags: list[str] = Field(default_factory=list)
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    suggested_action: SuggestedAction = "ignore"
    tag_gap_notes: str | None = None


class FoundationModelProposal(BaseModel):
    """One foundation model the article substantially discusses."""

    model_name: str = ""
    provider: str | None = None
    article_summary: str = ""
    newsworthy_attributes: str = ""
    supporting_snippet: str = ""
    match_candidates: list[MatchCandidate] = Field(default_factory=list)
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    suggested_action: SuggestedAction = "ignore"


class HowToProposal(BaseModel):
    """One practical how-to the article addresses."""

    question_title: str = ""
    answer_summary: str = ""
    supporting_snippet: str = ""
    match_candidates: list[MatchCandidate] = Field(default_factory=list)
    similar_existing_questions: list[str] = Field(default_factory=list)
    proposed_tags: list[str] = Field(default_factory=list)
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    suggested_action: SuggestedAction = "ignore"
    tag_gap_notes: str | None = None


class EnterpriseStudyProposal(BaseModel):
    """Enterprise implementation pattern."""

    company_name: str = ""
    implemented_technology: str = ""
    business_context: str = ""
    implementation_pattern: str = ""
    lessons_learned: str = ""
    supporting_snippet: str = ""
    proposed_tags: list[str] = Field(default_factory=list)
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    suggested_action: SuggestedAction = "ignore"


class IndustryTrendProposal(BaseModel):
    """Industry trend / pattern supported by the article."""

    trend_name: str = ""
    short_explanation: str = ""
    why_article_supports: str = ""
    supporting_snippets: list[str] = Field(default_factory=list)
    proposed_tags: list[str] = Field(default_factory=list)
    evidence_as_of: str | None = None
    claim_type: Literal["source_observation"] = "source_observation"
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    suggested_action: SuggestedAction = "ignore"


class RoundupDetection(BaseModel):
    """Newsletter / radar / roundup classification."""

    is_roundup: bool = False
    reasoning: str = ""
    confidence: float = Field(0.0, ge=0.0, le=1.0)


class LlmClassificationOutput(BaseModel):
    """Root object returned by the ingestion analysis LLM."""

    source_summary: SourceSummaryBlock = Field(default_factory=SourceSummaryBlock)
    glossary: list[GlossaryProposal] = Field(default_factory=list)
    tools: list[ToolProposal] = Field(default_factory=list)
    foundation_models: list[FoundationModelProposal] = Field(default_factory=list)
    how_to: list[HowToProposal] = Field(default_factory=list)
    enterprise_studies: list[EnterpriseStudyProposal] = Field(default_factory=list)
    industry_trends: list[IndustryTrendProposal] = Field(default_factory=list)
    roundup: RoundupDetection = Field(default_factory=RoundupDetection)


def llm_output_json_schema() -> dict:
    """JSON schema dict for OpenAI structured outputs."""
    return LlmClassificationOutput.model_json_schema()
