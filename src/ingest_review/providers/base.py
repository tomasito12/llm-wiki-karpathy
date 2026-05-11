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
        tool_tags_allowlist: list[str],
        howto_tags_allowlist: list[str],
        model: str,
        prompt_version: str,
        max_retries: int = 3,
    ) -> tuple[LlmClassificationOutput, dict[str, Any]]:
        """Run classification and return parsed output plus usage metadata.

        Returns:
            ``(parsed_output, meta)`` where ``meta`` may include ``request_id``,
            ``token_usage``, ``raw_message`` (for debugging).
        """
