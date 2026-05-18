"""Tests for ai_tools_roundup tool → foundation_model routing."""

from __future__ import annotations

from src.ingest_review.schema import (
    FoundationModelProposal,
    LlmClassificationOutput,
    SourceTypeDetection,
    ToolProposal,
)
from src.ingest_review.tools_roundup_model_routing import (
    _compact_alnum,
    _proposed_types_are_model_only,
    _wiki_name_suggests_foundation_model,
    convert_tool_proposal_to_foundation_model,
    route_ai_tools_roundup_tools_to_foundation_models,
    tool_should_be_routed_to_foundation_model,
)
from src.ingest_review.wiki_snapshot import WikiSnapshot


def test_wiki_name_match_substring() -> None:
    """Normalized wiki entries match tool names via substring when long enough."""
    wiki = ["Claude 3.5 Sonnet"]
    assert _wiki_name_suggests_foundation_model("Claude 3.5 Sonnet (API)", wiki) is True


def test_wiki_name_no_false_short() -> None:
    """Very short tool names do not match via wiki."""
    assert _wiki_name_suggests_foundation_model("AB", ["Alpha Beta Model"]) is False


def test_proposed_types_model_only() -> None:
    """Model-only proposed types (no tool types) trigger routing."""
    assert (
        _proposed_types_are_model_only(
            ["frontier-model"],
            tool_types={"mcp-server"},
            model_types={"frontier-model"},
        )
        is True
    )


def test_proposed_types_mixed_registry_stays_in_tools_signal() -> None:
    """If any entry is a tool type, do not treat as model-only."""
    assert (
        _proposed_types_are_model_only(
            ["frontier-model", "mcp-server"],
            tool_types={"mcp-server"},
            model_types={"frontier-model"},
        )
        is False
    )


def test_convert_tool_to_foundation_model_maps_fields() -> None:
    """Conversion carries over shared operational fields."""
    t = ToolProposal(
        name="MegaLM",
        short_description="A big model.",
        operational_relevance="API access",
        strengths="Fast",
        weaknesses_limitations="Cost",
        maturity_signals="GA",
        supporting_snippet="snippet",
        core_capabilities=["reasoning"],
        integration_ecosystem=["vertex"],
        related_tools=["Other"],
        proposed_types=["frontier-model"],
        confidence=0.88,
        value_level="high",
    )
    m = convert_tool_proposal_to_foundation_model(t)
    assert m.model_name == "MegaLM"
    assert m.operational_profile == "A big model."
    assert m.service_automation_implications == "API access"
    assert m.core_capabilities == ["reasoning"]
    assert m.comparative_observations == ["vertex"]
    assert m.related_models == ["Other"]
    assert m.confidence == 0.88
    assert m.value_level == "high"


def test_route_roundup_moves_by_types() -> None:
    """Under ai_tools_roundup, model-only tool proposals become foundation_models."""
    parsed = LlmClassificationOutput(
        source_type_detection=SourceTypeDetection(detected_source_type="ai_tools_roundup"),
        tools=[
            ToolProposal(name="App", proposed_types=["mcp-server"]),
            ToolProposal(name="Mega", proposed_types=["frontier-model"]),
        ],
        foundation_models=[
            FoundationModelProposal(model_name="Existing", proposed_types=["frontier-model"]),
        ],
    )
    wiki = WikiSnapshot(
        glossary_terms=[],
        tool_names=[],
        foundation_model_names=[],
        implementation_study_titles=[],
        topic_titles=[],
        howto_titles=[],
        trend_titles=[],
    )
    out = route_ai_tools_roundup_tools_to_foundation_models(
        parsed,
        wiki,
        tool_types=["mcp-server"],
        model_types=["frontier-model"],
    )
    assert len(out.tools) == 1
    assert out.tools[0].name == "App"
    assert len(out.foundation_models) == 2
    assert out.foundation_models[0].model_name == "Existing"
    assert out.foundation_models[1].model_name == "Mega"


def test_route_roundup_moves_by_wiki_name() -> None:
    """Wiki foundation-model index match promotes tool row to foundation_models."""
    parsed = LlmClassificationOutput(
        source_type_detection=SourceTypeDetection(detected_source_type="ai_tools_roundup"),
        tools=[
            ToolProposal(
                name="GPT-4.1 preview",
                proposed_types=[],
            ),
        ],
    )
    wiki = WikiSnapshot(
        glossary_terms=[],
        tool_names=[],
        foundation_model_names=["GPT-4.1"],
        implementation_study_titles=[],
        topic_titles=[],
        howto_titles=[],
        trend_titles=[],
    )
    out = route_ai_tools_roundup_tools_to_foundation_models(
        parsed,
        wiki,
        tool_types=["mcp-server"],
        model_types=["frontier-model"],
    )
    assert out.tools == []
    assert len(out.foundation_models) == 1
    assert out.foundation_models[0].model_name == "GPT-4.1 preview"


def test_route_non_roundup_noop() -> None:
    """Standard articles keep tools unchanged."""
    parsed = LlmClassificationOutput(
        source_type_detection=SourceTypeDetection(detected_source_type="standard_article"),
        tools=[ToolProposal(name="Mega", proposed_types=["frontier-model"])],
    )
    wiki = WikiSnapshot(
        glossary_terms=[],
        tool_names=[],
        foundation_model_names=[],
        implementation_study_titles=[],
        topic_titles=[],
        howto_titles=[],
        trend_titles=[],
    )
    out = route_ai_tools_roundup_tools_to_foundation_models(
        parsed,
        wiki,
        tool_types=[],
        model_types=["frontier-model"],
    )
    assert len(out.tools) == 1


def test_tool_should_be_routed_prefers_wiki_over_mixed_types() -> None:
    """Wiki name match routes even when proposed_types include a tool class (ambiguous LLM)."""
    tool = ToolProposal(
        name="GPT-5 Turbo",
        proposed_types=["mcp-server", "frontier-model"],
    )
    assert (
        tool_should_be_routed_to_foundation_model(
            tool,
            wiki_names=["GPT-5 Turbo"],
            tool_types={"mcp-server"},
            model_types={"frontier-model"},
        )
        is True
    )


def test_compact_alnum_strips_noise() -> None:
    assert _compact_alnum("GPT-4.1-mini") == "gpt41mini"
