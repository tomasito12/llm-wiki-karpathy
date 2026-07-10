"""Execute Stage 2 synthesis calls and write validated cache entries."""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol, cast

from src.pipeline.atomic import atomic_write_json
from src.wiki_synthesis import SYNTHESIS_PROMPT_VERSION, SYNTHESIS_SCHEMA_VERSION
from src.wiki_synthesis.cache import cache_file_path, load_cache_entry, validate_cache_entry
from src.wiki_synthesis.models import PlanEntry
from src.wiki_synthesis.planner import plan_from_graph
from src.wiki_synthesis.prompts import PromptBundle, build_prompt_bundle

RUN_TARGET_STATES = {"new", "stale"}
SYNTHESIS_CONTENT_TEXT_FIELDS: tuple[str, ...] = (
    "executive_synthesis",
    "practical_takeaway",
)
SYNTHESIS_CONTENT_LIST_FIELDS: tuple[str, ...] = (
    "what_to_remember",
    "consensus",
    "tensions",
    "evidence_quality",
)


class SynthesisProvider(Protocol):
    """Provider interface for one synthesis completion."""

    def synthesize(
        self, bundle: PromptBundle, *, model: str
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Return a raw synthesis JSON object and provider metadata."""


@dataclass(frozen=True)
class SynthesisRunItem:
    """One executor decision or completed synthesis."""

    entity_id: str
    category: str
    slug: str
    title: str
    state: str
    action: str
    reason: str
    cache_path: str
    current_input_hash: str
    cached_input_hash: str
    model: str = ""
    provider_request_id: str = ""
    token_usage: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass(frozen=True)
class SynthesisRunReport:
    """Summary of one synthesis executor run."""

    planned: int
    called: int
    written: int
    dry_run: bool
    items: list[SynthesisRunItem]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return {
            "planned": self.planned,
            "called": self.called,
            "written": self.written,
            "dry_run": self.dry_run,
            "items": [item.to_dict() for item in self.items],
        }


def run_synthesis(
    graph: dict[str, Any],
    *,
    cache_dir: Path,
    provider: SynthesisProvider,
    model: str,
    category: str | None = None,
    entity: str | None = None,
    include_single_source: bool = False,
    limit: int = 1,
    dry_run: bool = True,
    now_fn: Callable[[], datetime] | None = None,
) -> SynthesisRunReport:
    """Run Stage 2 synthesis for planned new/stale entries."""
    plan = plan_from_graph(
        graph,
        cache_dir=cache_dir,
        category=category,
        entity=entity,
        include_single_source=include_single_source,
        changed_only=True,
    )
    targets = _target_entries(plan.entries, limit=limit)
    items: list[SynthesisRunItem] = []
    called = 0
    written = 0
    for entry in targets:
        cache_path = cache_file_path(cache_dir, category=entry.category, slug=entry.slug)
        if dry_run:
            items.append(
                _item_for_entry(entry, action="planned", cache_path=cache_path, model=model)
            )
            continue
        previous_cache = load_cache_entry(cache_dir, category=entry.category, slug=entry.slug)
        bundle = build_prompt_bundle(
            graph,
            entity_id=entry.entity_id,
            previous_cache=previous_cache,
        )
        raw_payload, meta = provider.synthesize(bundle, model=model)
        called += 1
        cache_payload = normalize_synthesis_payload(
            raw_payload,
            bundle=bundle,
            now=now_fn() if now_fn else datetime.now(UTC),
        )
        validation = validate_cache_entry(
            cache_payload,
            current_input_hash=bundle.synthesis_input_hash,
        )
        if not validation.is_usable or validation.state != "fresh":
            msg = f"Provider returned invalid synthesis cache: {validation.reason}"
            raise ValueError(msg)
        atomic_write_json(cache_path, cache_payload)
        written += 1
        items.append(
            _item_for_entry(
                entry,
                action="written",
                cache_path=cache_path,
                model=model,
                provider_request_id=str(meta.get("request_id") or ""),
                token_usage=_token_usage(meta),
            )
        )
    return SynthesisRunReport(
        planned=len(targets),
        called=called,
        written=written,
        dry_run=dry_run,
        items=items,
    )


def normalize_synthesis_payload(
    payload: dict[str, Any],
    *,
    bundle: PromptBundle,
    now: datetime,
) -> dict[str, Any]:
    """Return a trusted cache payload using provider prose plus local metadata."""
    normalized = {
        "entity_id": bundle.entity_id,
        "category": bundle.category,
        "slug": bundle.slug,
        "title": bundle.title,
        "synthesis_schema_version": SYNTHESIS_SCHEMA_VERSION,
        "synthesis_prompt_version": SYNTHESIS_PROMPT_VERSION,
        "synthesis_input_hash": bundle.synthesis_input_hash,
        "last_synthesized_at": _iso_utc(now),
        "executive_synthesis": _required_text(payload, "executive_synthesis"),
        "practical_example": _practical_example(payload.get("practical_example")),
        "workflow_variants": _workflow_variants(payload.get("workflow_variants")),
        "what_to_remember": _required_text_list(payload, "what_to_remember"),
        "consensus": _required_text_list(payload, "consensus"),
        "tensions": _required_text_list(payload, "tensions"),
        "evidence_quality": _required_text_list(payload, "evidence_quality"),
        "practical_takeaway": _required_text(payload, "practical_takeaway"),
        "context_card": _context_card(payload.get("context_card")),
    }
    return normalized


def validate_synthesis_content_payload(payload: dict[str, Any]) -> None:
    """Validate provider-generated synthesis content fields."""
    for key in SYNTHESIS_CONTENT_TEXT_FIELDS:
        _required_text(payload, key)
    for key in SYNTHESIS_CONTENT_LIST_FIELDS:
        _required_text_list(payload, key)
    _practical_example(payload.get("practical_example"))
    _workflow_variants(payload.get("workflow_variants"))


def synthesis_response_json_schema() -> dict[str, Any]:
    """Return the JSON schema requested from the synthesis provider."""
    string_array = {"type": "array", "items": {"type": "string"}}
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "entity_id": {"type": "string"},
            "category": {"type": "string"},
            "slug": {"type": "string"},
            "title": {"type": "string"},
            "synthesis_schema_version": {"type": "integer"},
            "synthesis_prompt_version": {"type": "integer"},
            "synthesis_input_hash": {"type": "string"},
            "last_synthesized_at": {"type": "string"},
            "executive_synthesis": {"type": "string"},
            "practical_example": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "title": {"type": "string"},
                    "example": {"type": "string"},
                    "why_it_helps": {"type": "string"},
                    "basis": {"type": "string", "enum": ["source-grounded", "illustrative"]},
                },
                "required": ["title", "example", "why_it_helps", "basis"],
            },
            "workflow_variants": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "title": {"type": "string"},
                        "use_when": {"type": "string"},
                        "steps": string_array,
                        "caveats": string_array,
                        "sources": string_array,
                    },
                    "required": ["title", "use_when", "steps", "caveats", "sources"],
                },
            },
            "what_to_remember": string_array,
            "consensus": string_array,
            "tensions": string_array,
            "evidence_quality": string_array,
            "practical_takeaway": {"type": "string"},
            "context_card": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "use_this_page_when": {"type": "string"},
                    "best_for_questions_about": string_array,
                    "not_enough_for": string_array,
                    "strongest_sources": string_array,
                    "related_tags": string_array,
                },
                "required": [
                    "use_this_page_when",
                    "best_for_questions_about",
                    "not_enough_for",
                    "strongest_sources",
                    "related_tags",
                ],
            },
        },
        "required": [
            "entity_id",
            "category",
            "slug",
            "title",
            "synthesis_schema_version",
            "synthesis_prompt_version",
            "synthesis_input_hash",
            "last_synthesized_at",
            "executive_synthesis",
            "practical_example",
            "workflow_variants",
            "what_to_remember",
            "consensus",
            "tensions",
            "evidence_quality",
            "practical_takeaway",
            "context_card",
        ],
    }


def parse_json_object(text: str) -> dict[str, Any]:
    """Parse a JSON object from provider text."""
    data = json.loads(text)
    if not isinstance(data, dict):
        msg = "Provider response must be a JSON object"
        raise ValueError(msg)
    return data


def _target_entries(entries: Iterable[PlanEntry], *, limit: int) -> list[PlanEntry]:
    """Return executable plan entries, capped by limit."""
    if limit < 1:
        return []
    return [entry for entry in entries if entry.state in RUN_TARGET_STATES][:limit]


def _item_for_entry(
    entry: PlanEntry,
    *,
    action: str,
    cache_path: Path,
    model: str = "",
    provider_request_id: str = "",
    token_usage: dict[str, Any] | None = None,
) -> SynthesisRunItem:
    """Return a run item for one plan entry."""
    return SynthesisRunItem(
        entity_id=entry.entity_id,
        category=entry.category,
        slug=entry.slug,
        title=entry.title,
        state=entry.state,
        action=action,
        reason=entry.reason,
        cache_path=str(cache_path),
        current_input_hash=entry.current_input_hash,
        cached_input_hash=entry.cached_input_hash,
        model=model,
        provider_request_id=provider_request_id,
        token_usage=token_usage,
    )


def _token_usage(meta: dict[str, Any]) -> dict[str, Any] | None:
    """Return token usage metadata when provided."""
    value = meta.get("token_usage")
    return value if isinstance(value, dict) else None


def _required_text(payload: dict[str, Any], key: str) -> str:
    """Return a required non-empty text field."""
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        msg = f"Missing required text field: {key}"
        raise ValueError(msg)
    return value.strip()


def _required_text_list(payload: dict[str, Any], key: str) -> list[str]:
    """Return a required list of non-empty strings."""
    value = payload.get(key)
    if not isinstance(value, list):
        msg = f"Missing required list field: {key}"
        raise ValueError(msg)
    items = [str(item).strip() for item in value if str(item).strip()]
    if not items:
        msg = f"Required list field is empty: {key}"
        raise ValueError(msg)
    return items


def _practical_example(value: Any) -> dict[str, str]:
    """Return a normalized practical example from provider output."""
    example = value if isinstance(value, dict) else {}
    basis = _optional_text(example.get("basis"))
    if basis not in {"source-grounded", "illustrative"}:
        basis = "illustrative"
    return {
        "title": _required_nested_text(example, "title", parent="practical_example"),
        "example": _required_nested_text(example, "example", parent="practical_example"),
        "why_it_helps": _required_nested_text(
            example,
            "why_it_helps",
            parent="practical_example",
        ),
        "basis": basis,
    }


def _workflow_variants(value: Any) -> list[dict[str, Any]]:
    """Return normalized workflow variants from provider output."""
    if not isinstance(value, list):
        msg = "Missing required list field: workflow_variants"
        raise ValueError(msg)
    variants: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            msg = f"workflow_variants[{index}] must be an object"
            raise ValueError(msg)
        variant = cast(dict[str, Any], item)
        parent = f"workflow_variants[{index}]"
        variants.append(
            {
                "title": _required_nested_text(variant, "title", parent=parent),
                "use_when": _required_nested_text(variant, "use_when", parent=parent),
                "steps": _required_nested_text_list(variant, "steps", parent=parent),
                "caveats": _optional_text_list(variant.get("caveats")),
                "sources": _optional_text_list(variant.get("sources")),
            }
        )
    return variants


def _context_card(value: Any) -> dict[str, Any]:
    """Return a normalized context card."""
    card = value if isinstance(value, dict) else {}
    return {
        "use_this_page_when": _optional_text(card.get("use_this_page_when")),
        "best_for_questions_about": _optional_text_list(card.get("best_for_questions_about")),
        "not_enough_for": _optional_text_list(card.get("not_enough_for")),
        "strongest_sources": _optional_text_list(card.get("strongest_sources")),
        "related_tags": _optional_text_list(card.get("related_tags")),
    }


def _optional_text(value: Any) -> str:
    """Return stripped optional text."""
    return str(value or "").strip()


def _required_nested_text(value: dict[str, Any], key: str, *, parent: str) -> str:
    """Return one required nested text field."""
    text = value.get(key)
    if not isinstance(text, str) or not text.strip():
        msg = f"Missing required text field: {parent}.{key}"
        raise ValueError(msg)
    return text.strip()


def _required_nested_text_list(value: dict[str, Any], key: str, *, parent: str) -> list[str]:
    """Return one required nested text-list field."""
    items = _optional_text_list(value.get(key))
    if not items:
        msg = f"Missing required list field: {parent}.{key}"
        raise ValueError(msg)
    return items


def _optional_text_list(value: Any) -> list[str]:
    """Return a stripped optional text list."""
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _iso_utc(value: datetime) -> str:
    """Return a second-precision UTC timestamp."""
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
