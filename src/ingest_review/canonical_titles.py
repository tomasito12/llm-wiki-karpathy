"""Canonical page titles from wiki indexes and approved review artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel

from src.ingest_review.schema import (
    FoundationModelProposal,
    GlossaryProposal,
    HowToProposal,
    ImplementationStudyProposal,
    IndustryTrendProposal,
    LlmClassificationOutput,
    ToolProposal,
    TopicContribution,
)
from src.ingest_review.tags import normalize_tag
from src.ingest_review.wiki_snapshot import WikiSnapshot
from src.pipeline.slug import slugify


@dataclass(frozen=True)
class CanonicalTitleEntry:
    """One canonical title (and optional slug) for deduplication."""

    title: str
    slug: str = ""


@dataclass(frozen=True)
class EntityCanonicalConfig:
    """How to read titles from review nodes for one entity type."""

    review_list_key: str
    title_field: str
    slug_field: str | None = None
    prompt_block_key: str = ""


ENTITY_CANONICAL_CONFIGS: dict[str, EntityCanonicalConfig] = {
    "topic": EntityCanonicalConfig(
        review_list_key="topics",
        title_field="topic_title",
        slug_field="topic_slug",
        prompt_block_key="CANONICAL_TOPIC_TITLES",
    ),
    "trend": EntityCanonicalConfig(
        review_list_key="industry_trends",
        title_field="trend_title",
        slug_field="trend_slug",
        prompt_block_key="CANONICAL_TREND_TITLES",
    ),
    "glossary": EntityCanonicalConfig(
        review_list_key="glossary",
        title_field="term",
        prompt_block_key="CANONICAL_GLOSSARY_TERMS",
    ),
    "how_to": EntityCanonicalConfig(
        review_list_key="how_to",
        title_field="question_title",
        prompt_block_key="CANONICAL_HOWTO_TITLES",
    ),
    "tool": EntityCanonicalConfig(
        review_list_key="tools",
        title_field="name",
        prompt_block_key="CANONICAL_TOOL_NAMES",
    ),
    "model": EntityCanonicalConfig(
        review_list_key="foundation_models",
        title_field="model_name",
        prompt_block_key="CANONICAL_FOUNDATION_MODEL_NAMES",
    ),
    "impl_study": EntityCanonicalConfig(
        review_list_key="implementation_studies",
        title_field="title",
        prompt_block_key="CANONICAL_IMPL_STUDY_TITLES",
    ),
}


def effective_title_from_node(node: dict[str, Any], title_field: str) -> str:
    """Prefer reviewer-final title text, else the LLM draft on ``llm_item``."""
    sections = node.get("sections")
    if isinstance(sections, dict):
        sec = sections.get(title_field)
        if isinstance(sec, dict):
            final = sec.get("final_text")
            if isinstance(final, str) and final.strip():
                return final.strip()
    llm_item = node.get("llm_item")
    if isinstance(llm_item, dict):
        raw = llm_item.get(title_field)
        if isinstance(raw, str) and raw.strip():
            return raw.strip()
    return ""


def effective_slug_from_node(
    node: dict[str, Any],
    slug_field: str,
    *,
    title: str,
) -> str:
    """Return slug from review node or derive from *title*."""
    llm_item = node.get("llm_item")
    if isinstance(llm_item, dict):
        raw = llm_item.get(slug_field)
        if isinstance(raw, str) and raw.strip():
            return normalize_tag(raw.strip())
    if title:
        return slugify(title)
    return ""


def review_node_is_canonical_source(node: dict[str, Any]) -> bool:
    """Return True when a review node may supply a canonical title (non-rejected)."""
    raw = str(node.get("proposal_status") or "approved")
    if raw == "pending":
        raw = "approved"
    return raw != "rejected"


def _include_review_node(node: dict[str, Any]) -> bool:
    """Alias for :func:`review_node_is_canonical_source`."""
    return review_node_is_canonical_source(node)


def collect_approved_titles_from_reviews(
    reviews_root: Path,
    cfg: EntityCanonicalConfig,
) -> list[CanonicalTitleEntry]:
    """Scan ``reviews_root/*/review.json`` for non-rejected proposal titles."""
    if not reviews_root.is_dir():
        return []
    out: list[CanonicalTitleEntry] = []
    seen_lower: set[str] = set()
    for path in sorted(reviews_root.glob("*/review.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        review = data.get("review")
        if not isinstance(review, dict):
            continue
        nodes = review.get(cfg.review_list_key)
        if not isinstance(nodes, list):
            continue
        for node in nodes:
            if not isinstance(node, dict) or not _include_review_node(node):
                continue
            title = effective_title_from_node(node, cfg.title_field)
            if not title:
                continue
            key = title.casefold()
            if key in seen_lower:
                continue
            seen_lower.add(key)
            slug = ""
            if cfg.slug_field:
                slug = effective_slug_from_node(node, cfg.slug_field, title=title)
            out.append(CanonicalTitleEntry(title=title, slug=slug))
    return out


def _wiki_entries_for_entity(entity_key: str, wiki: WikiSnapshot) -> list[CanonicalTitleEntry]:
    """Build canonical entries from wiki index parsers."""
    if entity_key == "topic":
        titles = list(wiki.topic_titles)
        slugs = list(wiki.topic_slugs)
        entries: list[CanonicalTitleEntry] = []
        for i, title in enumerate(titles):
            slug = slugs[i] if i < len(slugs) else slugify(title)
            entries.append(CanonicalTitleEntry(title=title, slug=slug))
        for slug in slugs[len(titles) :]:
            if slug:
                entries.append(CanonicalTitleEntry(title=slug.replace("-", " ").title(), slug=slug))
        return entries
    if entity_key == "trend":
        entries = []
        for i, title in enumerate(wiki.trend_titles):
            slug = wiki.trend_slugs[i] if i < len(wiki.trend_slugs) else slugify(title)
            entries.append(CanonicalTitleEntry(title=title, slug=slug))
        return entries
    if entity_key == "glossary":
        return [CanonicalTitleEntry(title=t) for t in wiki.glossary_terms if t]
    if entity_key == "how_to":
        return [CanonicalTitleEntry(title=t) for t in wiki.howto_titles if t]
    if entity_key == "tool":
        return [CanonicalTitleEntry(title=t) for t in wiki.tool_names if t]
    if entity_key == "model":
        return [CanonicalTitleEntry(title=t) for t in wiki.foundation_model_names if t]
    if entity_key == "impl_study":
        return [CanonicalTitleEntry(title=t) for t in wiki.implementation_study_titles if t]
    return []


def merge_canonical_entries(
    *sources: list[CanonicalTitleEntry],
) -> list[CanonicalTitleEntry]:
    """Merge lists; first-seen spelling wins (case-insensitive dedupe)."""
    out: list[CanonicalTitleEntry] = []
    seen: set[str] = set()
    for source in sources:
        for entry in source:
            title = entry.title.strip()
            if not title:
                continue
            key = title.casefold()
            if key in seen:
                continue
            seen.add(key)
            slug = entry.slug.strip() if entry.slug else slugify(title)
            out.append(CanonicalTitleEntry(title=title, slug=slug if slug else ""))
    return out


def build_canonical_index(
    wiki: WikiSnapshot,
    reviews_root: Path | None,
) -> dict[str, list[CanonicalTitleEntry]]:
    """Per-entity canonical title lists (wiki first, then approved reviews)."""
    index: dict[str, list[CanonicalTitleEntry]] = {}
    for entity_key, cfg in ENTITY_CANONICAL_CONFIGS.items():
        wiki_entries = _wiki_entries_for_entity(entity_key, wiki)
        review_entries: list[CanonicalTitleEntry] = []
        if reviews_root is not None:
            review_entries = collect_approved_titles_from_reviews(reviews_root, cfg)
        index[entity_key] = merge_canonical_entries(wiki_entries, review_entries)
    return index


CANONICAL_FUZZY_ALIGN_MIN_SCORE = 0.95


def format_canonical_block(entries: list[CanonicalTitleEntry]) -> str:
    """Format prompt block body for one entity."""
    if not entries:
        return "(none — invent a new broad, stable title when warranted)"
    lines: list[str] = [
        "Listed pages are **not** default append targets; apply PAGE_MATCHING_RUBRIC "
        "before reusing any title below.",
    ]
    for e in entries:
        if e.slug:
            lines.append(f"- {e.title} | {e.slug}")
        else:
            lines.append(f"- {e.title}")
    return "\n".join(lines)


def build_canonical_title_prompt_blocks(
    wiki: WikiSnapshot,
    reviews_root: Path | None,
) -> dict[str, str]:
    """Return ``CANONICAL_*`` heading → body for classification/regen prompts."""
    index = build_canonical_index(wiki, reviews_root)
    blocks: dict[str, str] = {}
    for entity_key, cfg in ENTITY_CANONICAL_CONFIGS.items():
        blocks[cfg.prompt_block_key] = format_canonical_block(index.get(entity_key, []))
    return blocks


def _similarity_score(a: str, b: str) -> float:
    """Lightweight title similarity (0–1)."""
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    from difflib import SequenceMatcher

    return SequenceMatcher(None, a, b).ratio()


def find_canonical_match(
    title: str,
    entries: list[CanonicalTitleEntry],
    *,
    min_score: float = CANONICAL_FUZZY_ALIGN_MIN_SCORE,
) -> CanonicalTitleEntry | None:
    """Return best canonical entry for *title*, or None."""
    norm = title.strip()
    if not norm:
        return None
    folded = norm.casefold()
    for entry in entries:
        if entry.title.casefold() == folded:
            return entry
    best: CanonicalTitleEntry | None = None
    best_score = 0.0
    candidate_folded = folded
    for entry in entries:
        score = _similarity_score(candidate_folded, entry.title.casefold())
        if score > best_score:
            best_score = score
            best = entry
    if best is not None and best_score >= min_score:
        return best
    return None


_TProposalModel = TypeVar("_TProposalModel", bound=BaseModel)


def align_parsed_classification_titles(
    parsed: LlmClassificationOutput,
    index: dict[str, list[CanonicalTitleEntry]],
) -> LlmClassificationOutput:
    """Align all entity proposal titles in a :class:`~LlmClassificationOutput`."""

    def _align_list(
        items: list[_TProposalModel],
        entity_key: str,
        model_cls: type[_TProposalModel],
    ) -> list[_TProposalModel]:
        cfg = ENTITY_CANONICAL_CONFIGS[entity_key]
        entries = index.get(entity_key, [])
        out: list[Any] = []
        for item in items:
            raw = item.model_dump(mode="json") if hasattr(item, "model_dump") else dict(item)
            aligned = align_title_on_proposal(
                raw,
                title_field=cfg.title_field,
                slug_field=cfg.slug_field,
                entries=entries,
            )
            out.append(model_cls.model_validate(aligned))
        return out

    return parsed.model_copy(
        update={
            "glossary": _align_list(parsed.glossary, "glossary", GlossaryProposal),
            "topics": _align_list(parsed.topics, "topic", TopicContribution),
            "how_to": _align_list(parsed.how_to, "how_to", HowToProposal),
            "industry_trends": _align_list(parsed.industry_trends, "trend", IndustryTrendProposal),
            "tools": _align_list(parsed.tools, "tool", ToolProposal),
            "foundation_models": _align_list(
                parsed.foundation_models, "model", FoundationModelProposal
            ),
            "implementation_studies": _align_list(
                parsed.implementation_studies, "impl_study", ImplementationStudyProposal
            ),
        }
    )


def align_title_on_proposal(
    proposal: dict[str, Any],
    *,
    title_field: str,
    slug_field: str | None,
    entries: list[CanonicalTitleEntry],
) -> dict[str, Any]:
    """Return proposal dict with title/slug aligned to canonical entry when matched."""
    raw_title = proposal.get(title_field)
    if not isinstance(raw_title, str) or not raw_title.strip():
        return proposal
    match = find_canonical_match(raw_title, entries)
    if match is None:
        return proposal
    out = dict(proposal)
    out[title_field] = match.title
    if slug_field and match.slug:
        out[slug_field] = match.slug
    return out
