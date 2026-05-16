"""Abstract ingestion-analysis LLM provider."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.ingest_review.extract import SourceDocument
    from src.ingest_review.schema import LlmClassificationOutput
    from src.ingest_review.wiki_snapshot import WikiSnapshot


class IngestionProvider(ABC):
    """Pluggable backend for structured classification JSON."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Stable provider id (e.g. ``openai``)."""

    @abstractmethod
    def analyze_classification(
        self,
        *,
        document: SourceDocument,
        wiki: WikiSnapshot,
        tool_types_allowlist: list[str],
        howto_tags_allowlist: list[str],
        impl_study_tags_allowlist: list[str] | None = None,
        glossary_tags_allowlist: list[str] | None = None,
        topic_tags_allowlist: list[str] | None = None,
        trend_tags_allowlist: list[str] | None = None,
        model_types_allowlist: list[str] | None = None,
        source_type_override: str | None = None,
        extraction_budgets: dict[str, int] | None = None,
        model: str,
        prompt_version: str,
        max_retries: int = 3,
    ) -> tuple[LlmClassificationOutput, dict[str, Any]]:
        """Run classification and return parsed output plus usage metadata.

        Returns:
            ``(parsed_output, meta)`` where ``meta`` may include ``request_id``,
            ``token_usage``, ``raw_message`` (for debugging).
        """

    def regenerate_topic_proposal(
        self,
        *,
        document: SourceDocument,
        current_topic: dict[str, Any],
        new_title: str,
        reviewer_instruction: str | None,
        topic_tags_allowlist: list[str],
        existing_topic_slugs: list[str],
        model: str,
        prompt_version: str,
        max_plain_text_chars: int | None = None,
        max_retries: int = 2,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Regenerate one topic proposal under a reviewer-supplied title.

        Returns:
            ``(TopicRegenerateOutput dict, meta)`` with usage metadata.
        """
        raise NotImplementedError

    def regenerate_proposal(
        self,
        *,
        entity_key: str,
        document: SourceDocument,
        current_item: dict[str, Any],
        new_title: str,
        reviewer_instruction: str | None,
        context_sections: dict[str, str],
        model: str,
        prompt_version: str,
        max_plain_text_chars: int | None = None,
        max_retries: int = 2,
        source_entity_key: str | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Regenerate one proposal (any entity) under a reviewer-supplied title."""
        raise NotImplementedError

    @abstractmethod
    def regenerate_source_section(
        self,
        *,
        document: SourceDocument,
        section_key: str,
        current_value: str | list[str] | None,
        reviewer_instruction: str | None,
        model: str,
        prompt_version: str,
        max_plain_text_chars: int | None = None,
        max_retries: int = 2,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Regenerate one ``source_summary`` chapter.

        Returns:
            ``({"section_key": str, "content": str | list[str]}, meta)`` with validated content.
        """

    def suggest_domain_review_tag(
        self,
        *,
        entity_label: str,
        context_summary: str,
        allowlist: list[str],
        model: str,
        prompt_version: str,
        max_retries: int = 2,
    ) -> tuple[list[str], dict[str, Any]]:
        """Suggest kebab-case tag(s) not in *allowlist* (often zero or one entry)."""
        return [], {}

    def suggest_glossary_review_tag(
        self,
        *,
        term: str,
        proposed_definition: str,
        allowlist: list[str],
        model: str,
        prompt_version: str,
        max_retries: int = 2,
    ) -> tuple[list[str], dict[str, Any]]:
        """Backward-compatible alias for :meth:`suggest_domain_review_tag`."""
        return self.suggest_domain_review_tag(
            entity_label=term,
            context_summary=proposed_definition,
            allowlist=allowlist,
            model=model,
            prompt_version=prompt_version,
            max_retries=max_retries,
        )
