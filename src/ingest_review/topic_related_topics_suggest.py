"""Suggest related topic cross-links from wiki, reviews, and the current artifact."""

from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Literal

from src.ingest_review.canonical_titles import (
    ENTITY_CANONICAL_CONFIGS,
    CanonicalTitleEntry,
    build_canonical_index,
    collect_approved_titles_from_reviews,
    effective_slug_from_node,
    effective_title_from_node,
    review_node_is_canonical_source,
)
from src.ingest_review.schema import TopicContribution
from src.ingest_review.tags import normalize_tag
from src.ingest_review.wiki_snapshot import WikiSnapshot
from src.pipeline.slug import slugify

RelatedTopicSource = Literal["wiki", "review", "batch"]

_SOURCE_PRIORITY: dict[RelatedTopicSource, int] = {
    "wiki": 0,
    "review": 1,
    "batch": 2,
}

_SOURCE_LABELS: dict[RelatedTopicSource, str] = {
    "wiki": "wiki",
    "review": "other review",
    "batch": "this review",
}


@dataclass(frozen=True)
class RelatedTopicCandidate:
    """One linkable topic page."""

    slug: str
    title: str
    source: RelatedTopicSource


def _title_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    return SequenceMatcher(None, a, b).ratio()


def format_suggestion_line(candidate: RelatedTopicCandidate) -> str:
    """Human-readable line for readonly UI."""
    label = _SOURCE_LABELS.get(candidate.source, candidate.source)
    if candidate.title and candidate.title != candidate.slug.replace("-", " ").title():
        return f"{candidate.title} (`{candidate.slug}`) — {label}"
    return f"{candidate.slug} — {label}"


def _entry_to_candidate(
    entry: CanonicalTitleEntry, source: RelatedTopicSource
) -> RelatedTopicCandidate | None:
    slug = normalize_tag(entry.slug) if entry.slug else slugify(entry.title)
    if not slug:
        return None
    title = entry.title.strip() or slug.replace("-", " ").title()
    return RelatedTopicCandidate(slug=slug, title=title, source=source)


def _merge_candidates(*groups: list[RelatedTopicCandidate]) -> list[RelatedTopicCandidate]:
    """Dedupe by slug; higher-priority *source* wins (batch > review > wiki)."""
    by_slug: dict[str, RelatedTopicCandidate] = {}
    for group in groups:
        for cand in group:
            existing = by_slug.get(cand.slug)
            if existing is None:
                by_slug[cand.slug] = cand
                continue
            if _SOURCE_PRIORITY[cand.source] > _SOURCE_PRIORITY[existing.source]:
                by_slug[cand.slug] = cand
    return sorted(by_slug.values(), key=lambda c: (c.slug.lower(), c.title.lower()))


def _wiki_candidates(wiki: WikiSnapshot) -> list[RelatedTopicCandidate]:
    out: list[RelatedTopicCandidate] = []
    for entry in build_canonical_index(wiki, None).get("topic", []):
        cand = _entry_to_candidate(entry, "wiki")
        if cand:
            out.append(cand)
    return out


def _review_candidates(reviews_root: Path | None) -> list[RelatedTopicCandidate]:
    if reviews_root is None:
        return []
    cfg = ENTITY_CANONICAL_CONFIGS["topic"]
    out: list[RelatedTopicCandidate] = []
    for entry in collect_approved_titles_from_reviews(reviews_root, cfg):
        cand = _entry_to_candidate(entry, "review")
        if cand:
            out.append(cand)
    return out


def _batch_candidates_from_contributions(
    topics: list[TopicContribution],
) -> list[RelatedTopicCandidate]:
    out: list[RelatedTopicCandidate] = []
    seen: set[str] = set()
    for tc in topics:
        slug = normalize_tag(tc.topic_slug)
        title = (tc.topic_title or "").strip()
        if not slug and title:
            slug = slugify(title)
        if not slug or slug in seen:
            continue
        seen.add(slug)
        out.append(
            RelatedTopicCandidate(
                slug=slug,
                title=title or slug.replace("-", " ").title(),
                source="batch",
            )
        )
    return out


def _batch_candidates_from_artifact_nodes(
    artifact: dict[str, Any],
) -> list[RelatedTopicCandidate]:
    review = artifact.get("review")
    if not isinstance(review, dict):
        return []
    nodes = review.get("topics")
    if not isinstance(nodes, list):
        return []
    cfg = ENTITY_CANONICAL_CONFIGS["topic"]
    out: list[RelatedTopicCandidate] = []
    seen: set[str] = set()
    for node in nodes:
        if not isinstance(node, dict) or not review_node_is_canonical_source(node):
            continue
        title = effective_title_from_node(node, cfg.title_field)
        slug = ""
        if cfg.slug_field:
            slug = effective_slug_from_node(node, cfg.slug_field, title=title)
        if not slug and title:
            slug = slugify(title)
        slug = normalize_tag(slug)
        if not slug or slug in seen:
            continue
        seen.add(slug)
        out.append(
            RelatedTopicCandidate(
                slug=slug,
                title=title or slug.replace("-", " ").title(),
                source="batch",
            )
        )
    return out


def build_topic_slug_catalog(
    wiki: WikiSnapshot,
    reviews_root: Path | None,
    artifact: dict[str, Any] | None,
    *,
    exclude_slug: str = "",
) -> list[RelatedTopicCandidate]:
    """Catalog of linkable topics from wiki, cross-artifact reviews, and this artifact."""
    batch_llm: list[TopicContribution] = []
    if artifact:
        llm = artifact.get("llm_output")
        if isinstance(llm, dict):
            raw = llm.get("topics")
            if isinstance(raw, list):
                for item in raw:
                    if isinstance(item, TopicContribution):
                        batch_llm.append(item)
                    elif isinstance(item, dict):
                        batch_llm.append(TopicContribution.model_validate(item))
    batch_nodes = _batch_candidates_from_artifact_nodes(artifact) if artifact else []
    batch_tc = _batch_candidates_from_contributions(batch_llm)
    merged_batch = _merge_candidates(batch_nodes, batch_tc)

    catalog = _merge_candidates(
        _wiki_candidates(wiki),
        _review_candidates(reviews_root),
        merged_batch,
    )
    excl = normalize_tag(exclude_slug)
    if excl:
        catalog = [c for c in catalog if c.slug != excl]
    return catalog


def build_topic_slug_catalog_from_topics(
    wiki: WikiSnapshot,
    reviews_root: Path | None,
    batch_topics: list[TopicContribution],
    *,
    exclude_slug: str = "",
) -> list[RelatedTopicCandidate]:
    """Catalog for analyze-time backfill (no full artifact yet)."""
    return build_topic_slug_catalog(
        wiki,
        reviews_root,
        {"llm_output": {"topics": [t.model_dump(mode="json") for t in batch_topics]}},
        exclude_slug=exclude_slug,
    )


def suggest_related_topics(
    topic_slug: str,
    topic_title: str,
    summary_text: str,
    catalog: list[RelatedTopicCandidate],
    *,
    cap: int = 3,
) -> list[RelatedTopicCandidate]:
    """Return up to *cap* related topic candidates ranked by title/summary similarity."""
    self_slug = normalize_tag(topic_slug)
    query_parts = [topic_title.strip(), summary_text.strip()]
    query = " ".join(p for p in query_parts if p).casefold()
    if not query:
        return []

    scored: list[tuple[float, RelatedTopicCandidate]] = []
    for cand in catalog:
        if cand.slug == self_slug:
            continue
        hay = f"{cand.title} {cand.slug}".casefold()
        score = _title_similarity(query, hay)
        if score <= 0.0:
            continue
        scored.append((score, cand))

    scored.sort(key=lambda x: (-x[0], x[1].slug.lower()))
    return [cand for _, cand in scored[: max(0, cap)]]


def catalog_by_slug(catalog: list[RelatedTopicCandidate]) -> dict[str, RelatedTopicCandidate]:
    """Index catalog entries by slug."""
    return {c.slug: c for c in catalog}
