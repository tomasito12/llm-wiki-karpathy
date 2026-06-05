"""In-memory graph objects for the wiki renderer."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.wiki_render.evidence import EvidenceItem


@dataclass
class SourceRecord:
    """One reviewed source artifact and its generated relationships."""

    source_id: str
    title: str
    author: str
    publication: str
    canonical_url: str
    published_date: str
    assessed_as_of: str
    ingested_at: str
    content_sha256: str
    raw_md_rel_path: str
    raw_html_rel_path: str
    summary: str
    accessible_overview: str
    key_insights: list[str]
    why_it_matters: str
    limitations_and_open_questions: str
    contradictions_and_skepticism: str
    source_tags: set[str] = field(default_factory=set)
    derived: dict[str, set[str]] = field(default_factory=dict)
    derived_paths: dict[str, set[str]] = field(default_factory=dict)


@dataclass
class Contribution:
    """One source's contribution to a mergeable knowledge page."""

    category: str
    slug: str
    title: str
    source_id: str
    source_title: str
    source_date: str
    published_date: str
    assessed_as_of: str
    ingested_at: str
    tags: list[str]
    types: list[str]
    values: dict[str, object]
    evidence: list[EvidenceItem]
    aliases: list[str] = field(default_factory=list)
    match_candidates: list[dict[str, object]] = field(default_factory=list)
    confidence: float | None = None
    value_level: str = "medium"
    evidence_type: str = "unknown"


@dataclass
class KnowledgePage:
    """A merged page generated from one or more contributions."""

    category: str
    slug: str
    title: str
    path: str
    entity_id: str
    aliases: list[str]
    tags: list[str]
    types: list[str]
    values: dict[str, object]
    evidence: list[EvidenceItem]
    source_ids: list[str]
    source_titles: dict[str, str]
    first_seen: str
    last_seen: str
    source_count: int
    evidence_count: int
    evidence_set_hash: str
    stance_counts: dict[str, int]
    confidence: float | None
    value_level: str
    synthesis_state: str = "stage1-placeholder"
    maturity: str = ""
    duplicate_candidates: list[str] = field(default_factory=list)


@dataclass
class IndividualPage:
    """A non-merged generated item such as a signal or interview insight."""

    category: str
    slug: str
    title: str
    path: str
    source_id: str
    source_title: str
    source_date: str
    month: str
    tags: list[str]
    values: dict[str, object]
    evidence: list[EvidenceItem]
    evidence_set_hash: str
    evidence_count: int


@dataclass
class RenderedFile:
    """One generated markdown or JSON file."""

    relative_path: str
    text: str


@dataclass
class KnowledgeGraph:
    """Complete full-regeneration graph built from current reviews."""

    sources: list[SourceRecord]
    knowledge_pages: list[KnowledgePage]
    signals: list[IndividualPage]
    insights: list[IndividualPage]
    alias_map: dict[str, list[str]]
    taxonomy_version: str
