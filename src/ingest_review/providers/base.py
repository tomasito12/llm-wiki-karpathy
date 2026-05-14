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
        model: str,
        prompt_version: str,
        max_retries: int = 3,
    ) -> tuple[LlmClassificationOutput, dict[str, Any]]:
        """Run classification and return parsed output plus usage metadata.

        Returns:
            ``(parsed_output, meta)`` where ``meta`` may include ``request_id``,
            ``token_usage``, ``raw_message`` (for debugging).
        """

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
