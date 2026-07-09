"""Tests for the Stage 2 OpenAI synthesis provider."""

from __future__ import annotations

import json
from typing import Any

from src.wiki_synthesis.openai_provider import OpenAISynthesisProvider
from src.wiki_synthesis.prompts import PromptBundle


def test_openai_provider_requests_json_schema_response_format() -> None:
    """The provider should ask OpenAI for the synthesis JSON schema."""
    client = FakeClient([_completion(_payload())])
    provider = OpenAISynthesisProvider(client=client)

    payload, meta = provider.synthesize(_bundle(), model="test-model")

    kwargs = client.chat.completions.calls[0]
    assert kwargs["model"] == "test-model"
    assert kwargs["response_format"]["type"] == "json_schema"
    assert kwargs["response_format"]["json_schema"]["name"] == "wiki_synthesis_cache_entry"
    assert payload["executive_synthesis"] == "Local models make inference controllable."
    assert meta["request_id"] == "completion-1"


def test_openai_provider_repairs_incomplete_payload() -> None:
    """The provider should retry with a repair message when content validation fails."""
    client = FakeClient(
        [
            _completion({"what_to_remember": ["Missing other fields."]}),
            _completion(_payload(), completion_id="completion-2"),
        ]
    )
    provider = OpenAISynthesisProvider(client=client)

    payload, meta = provider.synthesize(_bundle(), model="test-model")

    assert payload["practical_takeaway"] == "Start small."
    assert meta["request_id"] == "completion-2"
    assert len(client.chat.completions.calls) == 2
    second_messages = client.chat.completions.calls[1]["messages"]
    assert "PREVIOUS OUTPUT FAILED VALIDATION" in second_messages[1]["content"]


class FakeClient:
    """Tiny fake OpenAI client with chat.completions.create."""

    def __init__(self, completions: list[FakeCompletion]) -> None:
        """Store completion responses."""
        self.chat = FakeChat(completions)
        self.closed = False

    def close(self) -> None:
        """Record close calls."""
        self.closed = True


class FakeChat:
    """Fake chat namespace."""

    def __init__(self, completions: list[FakeCompletion]) -> None:
        """Store completion responses."""
        self.completions = FakeCompletions(completions)


class FakeCompletions:
    """Fake completions endpoint."""

    def __init__(self, completions: list[FakeCompletion]) -> None:
        """Store completion responses and calls."""
        self._completions = completions
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> FakeCompletion:
        """Return the next fake completion."""
        self.calls.append(kwargs)
        return self._completions.pop(0)


class FakeCompletion:
    """Fake OpenAI completion object."""

    def __init__(self, payload: dict[str, Any], *, completion_id: str) -> None:
        """Store payload and id."""
        self.id = completion_id
        self.choices = [FakeChoice(json.dumps(payload))]
        self.usage = None


class FakeChoice:
    """Fake completion choice."""

    def __init__(self, content: str) -> None:
        """Store content."""
        self.message = FakeMessage(content)


class FakeMessage:
    """Fake completion message."""

    def __init__(self, content: str) -> None:
        """Store content."""
        self.content = content


def _completion(payload: dict[str, Any], *, completion_id: str = "completion-1") -> FakeCompletion:
    """Return a fake completion for payload."""
    return FakeCompletion(payload, completion_id=completion_id)


def _bundle() -> PromptBundle:
    """Return a minimal prompt bundle."""
    return PromptBundle(
        entity_id="topic:local-models",
        category="topic",
        slug="local-models",
        title="Local Models",
        prompt_version=1,
        synthesis_input_hash="hash",
        cached_input_hash="",
        system_prompt="system",
        user_prompt="user",
    )


def _payload() -> dict[str, Any]:
    """Return a complete provider payload."""
    return {
        "entity_id": "topic:local-models",
        "category": "topic",
        "slug": "local-models",
        "title": "Local Models",
        "synthesis_schema_version": 1,
        "synthesis_prompt_version": 1,
        "synthesis_input_hash": "hash",
        "last_synthesized_at": "2026-06-17T00:00:00Z",
        "executive_synthesis": "Local models make inference controllable.",
        "practical_example": {
            "title": "Private support draft",
            "example": (
                "A support team could run a local model to draft internal answers before "
                "sharing any sensitive customer details with a hosted model."
            ),
            "why_it_helps": "It makes the deployment tradeoff easy to picture.",
            "basis": "illustrative",
        },
        "what_to_remember": ["Use them when privacy or latency matters."],
        "consensus": ["They trade hosted convenience for control."],
        "tensions": ["They add operational work."],
        "evidence_quality": ["Two sources with consistent practitioner claims."],
        "practical_takeaway": "Start small.",
        "context_card": {
            "use_this_page_when": "Answering local deployment questions.",
            "best_for_questions_about": ["privacy", "latency"],
            "not_enough_for": ["benchmark selection"],
            "strongest_sources": ["Source A"],
            "related_tags": ["ai-engineering"],
        },
    }
