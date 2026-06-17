"""Review previews for Stage 2 synthesis cache entries."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from src.pipeline.atomic import atomic_write_text
from src.wiki_render.evidence import EvidenceItem
from src.wiki_render.models import KnowledgePage, RenderedFile
from src.wiki_render.render.knowledge import render_knowledge_page
from src.wiki_synthesis.cache import (
    CacheValidation,
    cache_file_path,
    load_cache_entry,
    validate_cache_entry,
)
from src.wiki_synthesis.input_hash import synthesis_input_hash
from src.wiki_synthesis.prompts import find_knowledge_page


@dataclass(frozen=True)
class SynthesisReviewPreview:
    """Review artifact for one synthesized wiki page preview."""

    entity_id: str
    category: str
    slug: str
    title: str
    target_path: str
    cache_path: str
    preview_path: str
    validation_state: str
    validation_reason: str
    current_input_hash: str
    cached_input_hash: str
    rendered_synthesis_state: str
    wrote_preview: bool

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable preview report."""
        return asdict(self)


def build_review_preview(
    graph: dict[str, Any],
    *,
    entity_id: str,
    cache_dir: Path,
    preview_dir: Path,
    dry_run: bool = False,
) -> tuple[SynthesisReviewPreview, RenderedFile]:
    """Render and optionally write a Stage 2 review preview for one entity."""
    page_payload = find_knowledge_page(graph, entity_id=entity_id)
    category = str(page_payload.get("category", ""))
    slug = str(page_payload.get("slug", ""))
    cache_path = cache_file_path(cache_dir, category=category, slug=slug)
    current_hash = synthesis_input_hash(page_payload)
    cache_entry = load_cache_entry(cache_dir, category=category, slug=slug)
    validation = validate_cache_entry(cache_entry, current_input_hash=current_hash)
    knowledge_page = knowledge_page_from_graph_payload(graph, page_payload)
    rendered = render_knowledge_page(knowledge_page, synthesis_cache_dir=cache_dir)
    preview_path = preview_dir / category / f"{slug}.md"
    if not dry_run:
        atomic_write_text(preview_path, rendered.text)
    report = SynthesisReviewPreview(
        entity_id=str(page_payload.get("entity_id", "")),
        category=category,
        slug=slug,
        title=str(page_payload.get("title", "")),
        target_path=str(page_payload.get("path", "")),
        cache_path=str(cache_path),
        preview_path=str(preview_path),
        validation_state=validation.state,
        validation_reason=validation.reason,
        current_input_hash=validation.current_input_hash,
        cached_input_hash=validation.cached_input_hash,
        rendered_synthesis_state=_rendered_state(validation),
        wrote_preview=not dry_run,
    )
    return report, rendered


def knowledge_page_from_graph_payload(
    graph: dict[str, Any],
    page: dict[str, Any],
) -> KnowledgePage:
    """Return an in-memory knowledge page from a graph-export page payload."""
    source_ids = _string_list(page.get("source_ids"))
    return KnowledgePage(
        category=str(page.get("category", "")),
        slug=str(page.get("slug", "")),
        title=str(page.get("title", "")),
        path=str(page.get("path", "")),
        entity_id=str(page.get("entity_id", "")),
        aliases=_string_list(page.get("aliases")),
        tags=_string_list(page.get("tags")),
        types=_string_list(page.get("types")),
        values={},
        evidence=[_evidence_item(item) for item in _dict_list(page.get("evidence"))],
        source_ids=source_ids,
        source_titles=_source_titles(graph, source_ids),
        first_seen=str(page.get("first_seen") or ""),
        last_seen=str(page.get("last_seen") or ""),
        source_count=_int_value(page.get("source_count")),
        evidence_count=_int_value(page.get("evidence_count")),
        evidence_set_hash=str(page.get("evidence_set_hash") or ""),
        stance_counts={
            "supporting": _int_value(page.get("supporting_count")),
            "counter": _int_value(page.get("counter_count")),
            "uncertainty": _int_value(page.get("uncertainty_count")),
            "neutral": _int_value(page.get("neutral_count")),
        },
        confidence=_float_or_none(page.get("confidence")),
        value_level=str(page.get("value_level") or "medium"),
        synthesis_state=str(page.get("synthesis_state") or "stage1-placeholder"),
        duplicate_candidates=_string_list(page.get("duplicate_candidates")),
    )


def _rendered_state(validation: CacheValidation) -> str:
    """Return the synthesis state expected in the rendered preview."""
    if validation.state == "fresh":
        return "synthesized"
    if validation.state == "stale":
        return "stale"
    return "stage1-placeholder"


def _evidence_item(item: dict[str, Any]) -> EvidenceItem:
    """Return an evidence item from graph-export data."""
    return EvidenceItem(
        evidence_id=str(item.get("evidence_id") or ""),
        text=str(item.get("text") or ""),
        source_id=str(item.get("source_id") or ""),
        source_title=str(item.get("source_title") or item.get("source_id") or ""),
        source_date=str(item.get("source_date") or ""),
        published_date=str(item.get("published_date") or ""),
        assessed_as_of=str(item.get("assessed_as_of") or ""),
        ingested_at=str(item.get("ingested_at") or ""),
        category=str(item.get("category") or ""),
        entity_slug=str(item.get("entity_slug") or ""),
        confidence=_float_or_none(item.get("confidence")),
        value_level=str(item.get("value_level") or "medium"),
        provenance=str(item.get("provenance") or ""),
        stance=str(item.get("stance") or "neutral"),
        evidence_type=str(item.get("evidence_type") or "unknown"),
        field=str(item.get("field") or ""),
    )


def _source_titles(graph: dict[str, Any], source_ids: list[str]) -> dict[str, str]:
    """Return source titles for source ids."""
    sources = graph.get("sources", [])
    if not isinstance(sources, list):
        return {}
    by_id = {
        str(source.get("source_id")): str(source.get("title") or source.get("source_id"))
        for source in sources
        if isinstance(source, dict) and source.get("source_id")
    }
    return {source_id: by_id.get(source_id, source_id) for source_id in source_ids}


def _string_list(value: Any) -> list[str]:
    """Return a list of strings."""
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _dict_list(value: Any) -> list[dict[str, Any]]:
    """Return a list of dictionaries."""
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _int_value(value: Any) -> int:
    """Return an integer for numeric values."""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int | float):
        return int(value)
    return 0


def _float_or_none(value: Any) -> float | None:
    """Return a float when the value is numeric."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    return None
