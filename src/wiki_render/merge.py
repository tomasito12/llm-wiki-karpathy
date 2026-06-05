"""Merge collected contributions into durable knowledge pages."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable
from pathlib import Path

from src.wiki_render import layout
from src.wiki_render.collect import CollectedItems
from src.wiki_render.evidence import EvidenceItem, evidence_set_hash
from src.wiki_render.models import Contribution, KnowledgeGraph, KnowledgePage

VALUE_RANK: dict[str, int] = {"high": 0, "medium": 1, "low": 2}
STANCE_ORDER: tuple[str, ...] = ("supporting", "counter", "uncertainty", "neutral")


def build_knowledge_graph(
    collected: CollectedItems,
    *,
    wiki_dir: Path,
    taxonomy_version: str,
) -> KnowledgeGraph:
    """Merge contributions and return the full in-memory graph."""
    pages = merge_contributions(collected.contributions, wiki_dir=wiki_dir)
    path_by_category_slug = {(page.category, page.slug): page.path for page in pages}
    for source in collected.sources:
        for key, slugs in source.derived.items():
            category = _category_for_derived_key(key)
            for slug in slugs:
                path = path_by_category_slug.get((category, slug))
                if path:
                    source.derived_paths.setdefault(f"{key}_paths", set()).add(path)
    alias_map = {page.entity_id: page.aliases for page in pages if page.aliases}
    return KnowledgeGraph(
        sources=collected.sources,
        knowledge_pages=pages,
        signals=collected.signals,
        insights=collected.insights,
        alias_map=alias_map,
        taxonomy_version=taxonomy_version,
    )


def merge_contributions(
    contributions: list[Contribution],
    *,
    wiki_dir: Path,
) -> list[KnowledgePage]:
    """Merge contributions by category + stable slug/title alias."""
    groups: dict[tuple[str, str], list[Contribution]] = defaultdict(list)
    canonical_by_title: dict[tuple[str, str], str] = {}
    for contribution in contributions:
        title_key = _title_key(contribution.title)
        canonical_slug = canonical_by_title.setdefault(
            (contribution.category, title_key),
            contribution.slug,
        )
        groups[(contribution.category, canonical_slug)].append(contribution)

    pages: list[KnowledgePage] = []
    for (category, slug), group in sorted(groups.items()):
        pages.append(_merge_group(category, slug, group, wiki_dir=wiki_dir))
    return pages


def _merge_group(
    category: str,
    slug: str,
    group: list[Contribution],
    *,
    wiki_dir: Path,
) -> KnowledgePage:
    """Merge one category/slug group."""
    ordered = sorted(
        group,
        key=lambda item: (_value_rank(item), item.source_date, item.source_id),
    )
    lead = ordered[0]
    evidence = _dedupe_evidence(
        [item for contribution in ordered for item in contribution.evidence]
    )
    source_ids = sorted({contribution.source_id for contribution in ordered})
    path = layout.page_path(wiki_dir, category, slug).relative
    aliases = _aliases(ordered, slug, lead.title)
    confidence_values = [item.confidence for item in ordered if item.confidence is not None]
    stance_counts = _stance_counts(evidence)
    page = KnowledgePage(
        category=category,
        slug=slug,
        title=lead.title,
        path=path,
        entity_id=f"{category}:{slug}",
        aliases=aliases,
        tags=_sorted_unique(tag for contribution in ordered for tag in contribution.tags),
        types=_sorted_unique(kind for contribution in ordered for kind in contribution.types),
        values=_merged_values(ordered, lead),
        evidence=evidence,
        source_ids=source_ids,
        source_titles={
            contribution.source_id: contribution.source_title for contribution in ordered
        },
        first_seen=_min_date(contribution.source_date for contribution in ordered),
        last_seen=_max_date(contribution.source_date for contribution in ordered),
        source_count=len(source_ids),
        evidence_count=len(evidence),
        evidence_set_hash=evidence_set_hash(evidence),
        stance_counts=stance_counts,
        confidence=(sum(confidence_values) / len(confidence_values)) if confidence_values else None,
        value_level=_best_value_level(ordered),
        maturity="unknown" if category == "trend" else "",
        duplicate_candidates=_duplicate_candidates(ordered),
    )
    return page


def _merged_values(group: list[Contribution], lead: Contribution) -> dict[str, object]:
    """Merge scalar and list values, using the lead contribution for prose scalars."""
    keys = sorted({key for contribution in group for key in contribution.values})
    values: dict[str, object] = {}
    for key in keys:
        lead_value = lead.values.get(key)
        if isinstance(lead_value, list):
            values[key] = _dedupe_lists(group, key)
        elif isinstance(lead_value, str) and lead_value.strip():
            values[key] = lead_value
        else:
            fallback = ""
            for contribution in group:
                raw = contribution.values.get(key)
                if isinstance(raw, str) and raw.strip():
                    fallback = raw
                    break
            values[key] = fallback
    return values


def _dedupe_lists(group: list[Contribution], key: str) -> list[str]:
    """Merge list values preserving contribution order."""
    seen: set[str] = set()
    output: list[str] = []
    for contribution in group:
        raw = contribution.values.get(key)
        if not isinstance(raw, list):
            continue
        for item in raw:
            clean = str(item).strip()
            if clean and clean not in seen:
                seen.add(clean)
                output.append(clean)
    return output


def _aliases(group: list[Contribution], slug: str, title: str) -> list[str]:
    """Return aliases from merged contribution alternates."""
    aliases: list[str] = []
    for contribution in group:
        if contribution.slug != slug:
            aliases.append(contribution.slug)
        if contribution.title != title:
            aliases.append(contribution.title)
        aliases.extend(contribution.aliases)
    return _sorted_unique(alias for alias in aliases if alias and alias not in {slug, title})


def _duplicate_candidates(group: list[Contribution]) -> list[str]:
    """Return unresolved duplicate candidate labels for diagnostics."""
    labels: list[str] = []
    for contribution in group:
        for candidate in contribution.match_candidates:
            title = candidate.get("title_or_slug")
            kind = candidate.get("match_kind")
            if title:
                labels.append(f"{title} ({kind or 'candidate'})")
    return _sorted_unique(labels)


def _stance_counts(evidence: list[EvidenceItem]) -> dict[str, int]:
    """Return deterministic stance-count breakdown."""
    counts = Counter(item.stance for item in evidence)
    return {stance: counts.get(stance, 0) for stance in STANCE_ORDER}


def _dedupe_evidence(values: list[EvidenceItem]) -> list[EvidenceItem]:
    """Deduplicate evidence by stable id and sort for deterministic rendering."""
    by_id: dict[str, EvidenceItem] = {}
    for item in values:
        by_id.setdefault(item.evidence_id, item)
    return sorted(
        by_id.values(),
        key=lambda item: (item.source_date, item.source_id, item.field, item.text),
    )


def _best_value_level(group: list[Contribution]) -> str:
    """Return highest value level in a contribution group."""
    return min((item.value_level for item in group), key=lambda value: VALUE_RANK.get(value, 1))


def _value_rank(contribution: Contribution) -> int:
    """Return sort rank for contribution value level."""
    return VALUE_RANK.get(contribution.value_level, 1)


def _min_date(values: Iterable[object]) -> str:
    """Return minimum non-empty date string."""
    dates = sorted(str(value) for value in values if str(value))
    return dates[0] if dates else ""


def _max_date(values: Iterable[object]) -> str:
    """Return maximum non-empty date string."""
    dates = sorted(str(value) for value in values if str(value))
    return dates[-1] if dates else ""


def _title_key(title: str) -> str:
    """Return normalized title key for cautious same-title merging."""
    return layout.safe_slug(title)


def _sorted_unique(values: Iterable[object]) -> list[str]:
    """Return sorted unique non-empty strings."""
    return sorted({str(value).strip() for value in values if str(value).strip()})


def _category_for_derived_key(key: str) -> str:
    """Map source derived frontmatter key back to page category."""
    return {
        "derived_topics": "topic",
        "derived_glossary": "glossary",
        "derived_trends": "trend",
        "derived_tools": "tool",
        "derived_models": "model",
        "derived_how_to": "how_to",
        "derived_implementation_studies": "impl_study",
    }[key]
