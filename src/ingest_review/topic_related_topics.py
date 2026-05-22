"""Sanitize topic ``related_topics`` so tag allowlist slugs are not stored as cross-links."""

from __future__ import annotations

from src.ingest_review.schema import LlmClassificationOutput, TopicContribution
from src.ingest_review.tags import normalize_tag
from src.ingest_review.wiki_snapshot import WikiSnapshot

TOPIC_RELATED_TOPICS_MAX = 3


def cap_related_topic_slugs(
    slugs: list[str],
    *,
    max_count: int = TOPIC_RELATED_TOPICS_MAX,
) -> list[str]:
    """Keep the first *max_count* slugs in order (after normalization upstream)."""
    if max_count <= 0:
        return []
    return list(slugs)[:max_count]


def known_topic_slug_set(wiki: WikiSnapshot, batch_topics: list[TopicContribution]) -> set[str]:
    """Union of wiki topic slugs and ``topic_slug`` values from the current extraction batch."""
    known: set[str] = set()
    for s in wiki.topic_slugs:
        nt = normalize_tag(s)
        if nt:
            known.add(nt)
    for tc in batch_topics:
        nt = normalize_tag(tc.topic_slug)
        if nt:
            known.add(nt)
    return known


def sanitize_topic_related_topics(
    related_topics: list[str],
    *,
    topic_slug: str,
    tag_allowlist: set[str],
) -> list[str]:
    """Drop tag-allowlist entries, self-links, and duplicates.

    Unknown slugs are retained so reviewers can keep LLM proposals before the wiki index
    catches up.
    """
    tags_norm = {normalize_tag(t) for t in tag_allowlist if str(t).strip()}
    self_slug = normalize_tag(topic_slug)
    out: list[str] = []
    seen: set[str] = set()
    for raw in related_topics:
        slug = normalize_tag(str(raw))
        if not slug or slug in seen:
            continue
        if slug == self_slug:
            continue
        if slug in tags_norm:
            continue
        seen.add(slug)
        out.append(slug)
    return cap_related_topic_slugs(out)


def sanitize_topics_related_topics(
    parsed: LlmClassificationOutput,
    topic_tags: set[str],
    wiki: WikiSnapshot,
) -> LlmClassificationOutput:
    """Apply :func:`sanitize_topic_related_topics` to every topic contribution."""
    if not parsed.topics:
        return parsed
    new_topics: list[TopicContribution] = []
    for tc in parsed.topics:
        cleaned = sanitize_topic_related_topics(
            list(tc.related_topics),
            topic_slug=tc.topic_slug,
            tag_allowlist=topic_tags,
        )
        if cleaned == tc.related_topics:
            new_topics.append(tc)
        else:
            new_topics.append(tc.model_copy(update={"related_topics": cleaned}))
    return parsed.model_copy(update={"topics": new_topics})
