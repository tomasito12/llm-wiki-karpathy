"""Deterministic ranking and selection for Stage 2 synthesis candidates."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from src.wiki_synthesis.models import PlanEntry
from src.wiki_synthesis.planner import plan_from_graph
from src.wiki_synthesis.prompts import find_knowledge_page

CHANGED_STATES = frozenset({"new", "stale"})
DEFAULT_SELECT_LIMIT = 20

CATEGORY_WEIGHTS: dict[str, int] = {
    "topic": 30,
    "how_to": 28,
    "tool": 24,
    "glossary": 22,
    "trend": 18,
    "model": 10,
}

DUPLICATE_STOPWORDS = frozenset(
    {"ai", "llm", "agentic", "agent", "workflow", "workflows"},
)
DUPLICATE_OVERLAP_THRESHOLD = 0.75
DUPLICATE_PENALTY = 5
MODEL_PENALTY = 15
STALE_BONUS = 10

ROLE_RELEVANCE_GROUPS: tuple[tuple[int, tuple[str, ...]], ...] = (
    (
        25,
        (
            "service automation",
            "conversational ai",
            "contact center",
            "contact-center",
            "voicebot",
            "voice bot",
            "chatbot",
            "chat bot",
        ),
    ),
    (
        20,
        (
            "agent",
            "workflow",
            "orchestration",
            "evaluation",
            "governance",
            "auditability",
        ),
    ),
    (
        15,
        (
            "knowledge management",
            "retrieval",
            "provenance",
            "context",
            "pii",
            "privacy",
        ),
    ),
    (
        10,
        (
            "ai engineering",
            "ai-engineering",
            "model routing",
            "local inference",
            "tool use",
        ),
    ),
)


@dataclass(frozen=True)
class SelectedEntry:
    """One ranked synthesis candidate."""

    rank: int
    score: int
    entity_id: str
    category: str
    slug: str
    title: str
    source_count: int
    evidence_count: int
    state: str
    notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable selected entry."""
        return asdict(self)


@dataclass(frozen=True)
class SelectionResult:
    """Ranked synthesis candidate selection."""

    total_changed: int
    shown: int
    entries: list[SelectedEntry]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable selection result."""
        return {
            "total_changed": self.total_changed,
            "shown": self.shown,
            "entries": [entry.to_dict() for entry in self.entries],
        }


def select_synthesis_candidates(
    graph: dict[str, Any],
    *,
    cache_dir: Path,
    category: str | None = None,
    entity: str | None = None,
    include_single_source: bool = False,
    limit: int = DEFAULT_SELECT_LIMIT,
    finished_source_ids: set[str] | None = None,
) -> SelectionResult:
    """Return ranked changed synthesis candidates without side effects."""
    plan = plan_from_graph(
        graph,
        cache_dir=cache_dir,
        category=category,
        entity=entity,
        include_single_source=include_single_source,
        changed_only=True,
        finished_source_ids=finished_source_ids,
    )
    changed_entries = [entry for entry in plan.entries if entry.state in CHANGED_STATES]
    total_changed = len(changed_entries)
    if entity and not changed_entries:
        return SelectionResult(total_changed=0, shown=0, entries=[])
    scored = _score_entries(graph, changed_entries)
    duplicate_notes = _duplicate_notes(scored)
    ranked = sorted(
        scored,
        key=lambda item: (-item["score"], item["entry"].entity_id),
    )
    shown = ranked[: max(0, limit)]
    entries = [
        SelectedEntry(
            rank=index,
            score=item["score"],
            entity_id=item["entry"].entity_id,
            category=item["entry"].category,
            slug=item["entry"].slug,
            title=item["entry"].title,
            source_count=item["entry"].source_count,
            evidence_count=item["entry"].evidence_count,
            state=item["entry"].state,
            notes=_entry_notes(
                graph,
                item,
                duplicate_notes.get(item["entry"].entity_id, []),
            ),
        )
        for index, item in enumerate(shown, start=1)
    ]
    return SelectionResult(total_changed=total_changed, shown=len(entries), entries=entries)


def count_changed_candidates(
    graph: dict[str, Any],
    *,
    cache_dir: Path,
    category: str | None = None,
    entity: str | None = None,
    include_single_source: bool = False,
    finished_source_ids: set[str] | None = None,
) -> int:
    """Return the number of changed synthesis candidates matching filters."""
    plan = plan_from_graph(
        graph,
        cache_dir=cache_dir,
        category=category,
        entity=entity,
        include_single_source=include_single_source,
        changed_only=True,
        finished_source_ids=finished_source_ids,
    )
    return sum(1 for entry in plan.entries if entry.state in CHANGED_STATES)


def format_selection_text(result: SelectionResult) -> str:
    """Render a human-readable selection report."""
    lines = [
        f"wiki-synthesis-select total={result.total_changed} shown={result.shown}",
        f"{'score':<7} {'entity_id':<46} {'sources':<7} {'evidence':<8} title",
    ]
    for entry in result.entries:
        lines.append(
            f"{entry.score:<7} {entry.entity_id:<46} "
            f"{entry.source_count:<7} {entry.evidence_count:<8} {entry.title}"
        )
    return "\n".join(lines)


def format_workflow_commands(entries: list[SelectedEntry]) -> str:
    """Return copy-pasteable wiki-synthesis-workflow commands."""
    return "\n".join(
        f"hatch run wiki-synthesis-workflow --entity {entry.entity_id} --yes" for entry in entries
    )


def score_candidate(
    graph: dict[str, Any],
    entry: PlanEntry,
    *,
    duplicate_penalty: int = 0,
) -> tuple[int, list[str]]:
    """Return a deterministic score and scoring notes for one candidate."""
    page = _page_for_entry(graph, entry)
    score = _category_weight(entry.category)
    score += min(entry.source_count, 5) * 5
    score += min(entry.evidence_count, 30)
    score += _role_relevance_weight(page, entry)
    score += STALE_BONUS if entry.state == "stale" else 0
    if entry.category == "model":
        score -= MODEL_PENALTY
    score -= duplicate_penalty
    notes = _score_notes(entry, page, duplicate_penalty)
    return score, notes


def _score_entries(
    graph: dict[str, Any],
    entries: list[PlanEntry],
) -> list[dict[str, Any]]:
    """Return scored candidate payloads before duplicate penalties."""
    return [
        {
            "entry": entry,
            "score": score_candidate(graph, entry)[0],
            "tokens": _normalized_tokens(entry.title, entry.slug),
        }
        for entry in entries
    ]


def _duplicate_notes(scored: list[dict[str, Any]]) -> dict[str, list[str]]:
    """Return possible-duplicate notes keyed by entity id."""
    notes: dict[str, list[str]] = {}
    for index, left in enumerate(scored):
        for right in scored[index + 1 :]:
            overlap = _token_overlap(left["tokens"], right["tokens"])
            if overlap < DUPLICATE_OVERLAP_THRESHOLD:
                continue
            left_id = left["entry"].entity_id
            right_id = right["entry"].entity_id
            notes.setdefault(left_id, []).append("possible_duplicate")
            notes.setdefault(right_id, []).append("possible_duplicate")
            left["score"] = max(0, left["score"] - DUPLICATE_PENALTY)
            right["score"] = max(0, right["score"] - DUPLICATE_PENALTY)
    return notes


def _entry_notes(
    graph: dict[str, Any],
    item: dict[str, Any],
    duplicate_notes: list[str],
) -> list[str]:
    """Return stable note labels for one selected entry."""
    page = _page_for_entry(graph, item["entry"])
    notes = _score_notes(
        item["entry"],
        page,
        DUPLICATE_PENALTY if duplicate_notes else 0,
    )
    for note in duplicate_notes:
        if note not in notes:
            notes.append(note)
    category_note = item["entry"].category
    if category_note and category_note not in notes:
        notes.append(category_note)
    return notes


def _score_notes(entry: PlanEntry, page: dict[str, Any], duplicate_penalty: int) -> list[str]:
    """Return explainability notes derived from scoring inputs."""
    notes: list[str] = []
    if _role_relevance_weight(page, entry) > 0:
        notes.append("role_relevant")
    if entry.state == "stale":
        notes.append("stale")
    if duplicate_penalty:
        notes.append("possible_duplicate")
    return notes


def _category_weight(category: str) -> int:
    """Return the base category weight for scoring."""
    return CATEGORY_WEIGHTS.get(category, 0)


def _role_relevance_weight(page: dict[str, Any], entry: PlanEntry) -> int:
    """Return role-relevance bonus points from page text and tags."""
    haystack = _searchable_text(page, entry)
    total = 0
    for weight, terms in ROLE_RELEVANCE_GROUPS:
        if any(term in haystack for term in terms):
            total += weight
    return total


def _searchable_text(page: dict[str, Any], entry: PlanEntry) -> str:
    """Return lowercase searchable text for role relevance matching."""
    parts = [entry.title, entry.slug.replace("-", " ")]
    tags = page.get("tags")
    if isinstance(tags, list):
        parts.extend(str(tag).replace("-", " ") for tag in tags)
    evidence = page.get("evidence")
    if isinstance(evidence, list):
        for item in evidence:
            if isinstance(item, dict):
                tag_value = item.get("tags")
                if isinstance(tag_value, list):
                    parts.extend(str(tag).replace("-", " ") for tag in tag_value)
    return " ".join(parts).lower()


def _page_for_entry(graph: dict[str, Any], entry: PlanEntry) -> dict[str, Any]:
    """Return graph page metadata for one plan entry when available."""
    try:
        page = find_knowledge_page(graph, entity_id=entry.entity_id)
    except (KeyError, ValueError):
        return {}
    return page if isinstance(page, dict) else {}


def _normalized_tokens(title: str, slug: str) -> set[str]:
    """Return normalized comparison tokens for duplicate heuristics."""
    raw = f"{title} {slug.replace('-', ' ')}".lower()
    tokens = {token for token in re.split(r"[^a-z0-9]+", raw) if token}
    return {token for token in tokens if token not in DUPLICATE_STOPWORDS}


def _token_overlap(left: set[str], right: set[str]) -> float:
    """Return conservative token overlap between two normalized token sets."""
    if not left or not right:
        return 0.0
    intersection = left & right
    if not intersection:
        return 0.0
    return len(intersection) / min(len(left), len(right))
