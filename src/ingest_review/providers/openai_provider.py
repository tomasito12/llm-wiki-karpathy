"""OpenAI chat completions provider for ingestion classification."""

from __future__ import annotations

import json
import logging
import time
from typing import Any

from openai import APIError, APITimeoutError, OpenAI, RateLimitError
from pydantic import ValidationError

from src.ingest_review.extract import SourceDocument
from src.ingest_review.providers.base import IngestionProvider
from src.ingest_review.schema import PROMPT_VERSION, LlmClassificationOutput, llm_output_json_schema
from src.ingest_review.wiki_snapshot import WikiSnapshot

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an analyst helping curate a personal AI-engineering Markdown wiki.
Return only valid JSON matching the provided schema. Ground every substantive claim in the \
source text via supporting_snippet (or section text for summaries). If unknown, use empty \
strings or empty arrays and low confidence. Do not invent facts.
For tools and how_to items, proposed_tags MUST be a subset of the allowlists provided in the \
user message; use [] if none apply.
Prefer reusing existing wiki pages (match_candidates, similar_existing_questions) when the \
article overlaps; suggest create only when justified.
Keep text concise (bullet phrases where possible)."""


def _build_user_prompt(
    doc: SourceDocument,
    wiki: WikiSnapshot,
    tool_tags: list[str],
    howto_tags: list[str],
    *,
    prompt_version: str,
) -> str:
    """Assemble the user message with metadata, lists, and article body."""
    meta_lines = [
        f"prompt_version: {prompt_version}",
        f"source_id: {doc.source_id}",
        f"title: {doc.title or ''}",
        f"author: {doc.author or ''}",
        f"published_date: {doc.published_date or ''}",
        f"canonical_url: {doc.canonical_url or ''}",
    ]
    schema_hint = json.dumps(llm_output_json_schema(), indent=2)[:24_000]
    blocks = [
        "## Metadata\n" + "\n".join(meta_lines),
        "## EXISTING_GLOSSARY_TERMS\n" + "\n".join(f"- {t}" for t in wiki.glossary_terms[:150]),
        "## EXISTING_QUESTION_HINTS\n" + "\n".join(f"- {q}" for q in wiki.question_hints[:150]),
        "## EXISTING_TOOL_NAMES\n" + "\n".join(f"- {t}" for t in wiki.tool_names[:200]),
        "## EXISTING_FOUNDATION_MODEL_NAMES\n"
        + "\n".join(f"- {m}" for m in wiki.foundation_model_names[:120]),
        "## TOOL_TAGS_ALLOWLIST\n" + "\n".join(f"- {t}" for t in tool_tags),
        "## HOWTO_TAGS_ALLOWLIST\n" + "\n".join(f"- {t}" for t in howto_tags),
        "## JSON_SCHEMA_HINT\n" + schema_hint,
        "## ARTICLE_PLAIN_TEXT\n" + doc.plain_text,
        "## Instructions\n"
        "Output one JSON object matching the schema keys: source_summary, glossary, tools, "
        "foundation_models, how_to, enterprise_studies, industry_trends, roundup. "
        "Use empty arrays when a category does not apply. For roundup: set is_roundup true only "
        "for digests/newsletters whose primary purpose is listing many external items.",
    ]
    return "\n\n".join(blocks)


def _parse_json_content(raw: str) -> dict[str, Any]:
    """Parse model string content as JSON object."""
    return json.loads(raw)


class OpenAIIngestionProvider(IngestionProvider):
    """OpenAI Chat Completions with structured JSON (schema validate locally)."""

    def __init__(self, client: OpenAI | None = None) -> None:
        """Initialize with optional shared client (for tests)."""
        self._client = client or OpenAI()

    @property
    def provider_name(self) -> str:
        """Return ``openai``."""
        return "openai"

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
        """Call OpenAI and validate against :class:`LlmClassificationOutput`."""
        user_prompt = _build_user_prompt(
            document,
            wiki,
            tool_tags_allowlist,
            howto_tags_allowlist,
            prompt_version=prompt_version or PROMPT_VERSION,
        )
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT + " Respond with one JSON object only."},
            {"role": "user", "content": user_prompt},
        ]
        # Prefer json_schema when the API accepts it; fall back to json_object.
        schema = llm_output_json_schema()
        response_formats: list[dict[str, Any] | None] = [
            {
                "type": "json_schema",
                "json_schema": {
                    "name": "ingest_classification",
                    "schema": schema,
                    "strict": False,
                },
            },
            {"type": "json_object"},
            None,
        ]

        last_error: str | None = None
        max_attempts = max(3, max_retries) * 2
        fmt_index = 0
        for attempt in range(max_attempts):
            response_format = response_formats[min(fmt_index, len(response_formats) - 1)]
            try:
                kwargs: dict[str, Any] = {
                    "model": model,
                    "messages": messages,
                    "timeout": 120.0,
                }
                if response_format is not None:
                    kwargs["response_format"] = response_format
                completion = self._client.chat.completions.create(**kwargs)
                choice = completion.choices[0]
                raw = choice.message.content or ""
                data = _parse_json_content(raw)
                parsed = LlmClassificationOutput.model_validate(data)
                meta: dict[str, Any] = {
                    "request_id": completion.id,
                    "token_usage": completion.usage.model_dump() if completion.usage else None,
                }
                return parsed, meta
            except json.JSONDecodeError as exc:
                last_error = f"json: {exc}"
                logger.warning("JSON decode failed: %s", last_error)
                time.sleep(0.5 * (attempt + 1))
            except ValidationError as exc:
                last_error = f"validate: {exc}"
                logger.warning("Schema validation failed: %s", last_error)
                repair = (
                    "\n\n## Previous output failed validation\n"
                    f"{str(exc)[:8000]}\n"
                    "Return corrected JSON only."
                )
                messages = [
                    messages[0],
                    {"role": "user", "content": user_prompt + repair},
                ]
                time.sleep(0.3 * (attempt + 1))
            except (RateLimitError, APITimeoutError, APIError) as exc:
                last_error = str(exc)
                logger.warning(
                    "OpenAI HTTP error (format=%s): %s",
                    fmt_index,
                    last_error,
                )
                if isinstance(exc, RateLimitError) or "429" in last_error:
                    time.sleep(2.0 * (attempt + 1))
                else:
                    fmt_index += 1
        raise RuntimeError(f"OpenAI classification failed: {last_error}")
