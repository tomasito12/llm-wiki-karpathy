"""Shared artifact category definitions for render and lint."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from src.wiki_contract import layout

ArtifactClass = Literal["source", "merged", "evidence", "index"]


@dataclass(frozen=True)
class CategorySpec:
    """One generated artifact category."""

    graph_category: str
    frontmatter_category: str
    folder: str
    derived_key: str | None
    artifact_class: ArtifactClass
    uses_monthly_path: bool = False


_CATEGORY_SPECS: tuple[CategorySpec, ...] = (
    CategorySpec(
        graph_category="source",
        frontmatter_category="source",
        folder=layout.SOURCES,
        derived_key=None,
        artifact_class="source",
    ),
    CategorySpec(
        graph_category="topic",
        frontmatter_category="topic",
        folder=layout.TOPICS,
        derived_key="derived_topics",
        artifact_class="merged",
    ),
    CategorySpec(
        graph_category="glossary",
        frontmatter_category="glossary",
        folder=layout.GLOSSARY,
        derived_key="derived_glossary",
        artifact_class="merged",
    ),
    CategorySpec(
        graph_category="trend",
        frontmatter_category="industry-trend",
        folder=layout.INDUSTRY_TRENDS,
        derived_key="derived_trends",
        artifact_class="merged",
    ),
    CategorySpec(
        graph_category="tool",
        frontmatter_category="tool",
        folder=layout.TOOLS,
        derived_key="derived_tools",
        artifact_class="merged",
    ),
    CategorySpec(
        graph_category="model",
        frontmatter_category="foundation-model",
        folder=layout.FOUNDATION_MODELS,
        derived_key="derived_models",
        artifact_class="merged",
    ),
    CategorySpec(
        graph_category="how_to",
        frontmatter_category="how-to",
        folder=layout.HOW_TO,
        derived_key="derived_how_to",
        artifact_class="merged",
    ),
    CategorySpec(
        graph_category="signal",
        frontmatter_category="signal",
        folder=layout.SIGNALS,
        derived_key="derived_signals",
        artifact_class="evidence",
        uses_monthly_path=True,
    ),
    CategorySpec(
        graph_category="insight",
        frontmatter_category="insight",
        folder=layout.INTERVIEW_INSIGHTS,
        derived_key="derived_interview_insights",
        artifact_class="evidence",
        uses_monthly_path=True,
    ),
    CategorySpec(
        graph_category="impl_study",
        frontmatter_category="implementation-study",
        folder=layout.IMPLEMENTATION_STUDIES,
        derived_key="derived_implementation_studies",
        artifact_class="evidence",
        uses_monthly_path=True,
    ),
    CategorySpec(
        graph_category="index",
        frontmatter_category="index",
        folder=layout.INDEXES,
        derived_key=None,
        artifact_class="index",
    ),
    CategorySpec(
        graph_category="diagnostics",
        frontmatter_category="diagnostics",
        folder=layout.INDEXES,
        derived_key=None,
        artifact_class="index",
    ),
)

CATEGORY_BY_GRAPH: dict[str, CategorySpec] = {spec.graph_category: spec for spec in _CATEGORY_SPECS}
CATEGORY_BY_FRONTMATTER: dict[str, CategorySpec] = {
    spec.frontmatter_category: spec for spec in _CATEGORY_SPECS
}
FRONTMATTER_CATEGORY_BY_GRAPH: dict[str, str] = {
    spec.graph_category: spec.frontmatter_category for spec in _CATEGORY_SPECS
}
DERIVED_KEY_BY_GRAPH_CATEGORY: dict[str, str] = {
    spec.graph_category: spec.derived_key
    for spec in _CATEGORY_SPECS
    if spec.derived_key is not None
}
MERGED_GRAPH_CATEGORIES: frozenset[str] = frozenset(
    spec.graph_category for spec in _CATEGORY_SPECS if spec.artifact_class == "merged"
)
EVIDENCE_GRAPH_CATEGORIES: frozenset[str] = frozenset(
    spec.graph_category for spec in _CATEGORY_SPECS if spec.artifact_class == "evidence"
)


def all_category_specs() -> tuple[CategorySpec, ...]:
    """Return all category specifications."""
    return _CATEGORY_SPECS


def spec_for_graph(graph_category: str) -> CategorySpec:
    """Return the spec for a graph category slug."""
    return CATEGORY_BY_GRAPH[graph_category]


def spec_for_frontmatter(frontmatter_category: str) -> CategorySpec:
    """Return the spec for a rendered frontmatter category."""
    return CATEGORY_BY_FRONTMATTER[frontmatter_category]


def graph_category_for_frontmatter(frontmatter_category: str) -> str:
    """Map rendered frontmatter category to graph category."""
    return spec_for_frontmatter(frontmatter_category).graph_category


def derived_key_for_graph_category(graph_category: str) -> str | None:
    """Return derived frontmatter key for a graph category, if any."""
    return DERIVED_KEY_BY_GRAPH_CATEGORY.get(graph_category)
