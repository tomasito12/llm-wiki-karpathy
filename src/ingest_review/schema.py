"""Pydantic models for LLM classification output and JSON schema export."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

ARTIFACT_SCHEMA_VERSION = 1
PROMPT_VERSION = "1"

SuggestedAction = Literal["create", "update", "ignore"]
MatchKind = Literal["exact", "fuzzy", "none"]
ReviewStatus = Literal["pending", "approved", "rejected", "modified"]


class MatchCandidate(BaseModel):
    """Possible existing wiki page match from LLM."""

    title_or_slug: str = ""
    match_kind: MatchKind = "none"
    confidence: float = Field(0.0, ge=0.0, le=1.0)


class SourceSummaryBlock(BaseModel):
    """Markdown-oriented sections for the source-level analysis."""

    why_it_matters: str = ""
    key_insights: str = ""
    implications_automation: str = Field(
        "",
        description="Implications for service automation, voicebots, chatbots.",
    )
    context_limitations: str = ""
    contradictions: str = ""
    sources: list[str] = Field(default_factory=list)


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
