"""OpenAI provider for Stage 2 synthesis execution."""

from __future__ import annotations

import json
import logging
import time
from typing import Any, cast

from src.wiki_synthesis.executor import (
    parse_json_object,
    synthesis_response_json_schema,
    validate_synthesis_content_payload,
)
from src.wiki_synthesis.prompts import PromptBundle

LOGGER = logging.getLogger(__name__)


class OpenAISynthesisProvider:
    """OpenAI Chat Completions provider for synthesis JSON."""

    def __init__(self, client: Any | None = None) -> None:
        """Initialize with an optional client for tests."""
        if client is None:
            from openai import OpenAI

            client = OpenAI()
        self._client = client

    def close(self) -> None:
        """Close the underlying OpenAI client."""
        self._client.close()

    def synthesize(
        self, bundle: PromptBundle, *, model: str
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Run one synthesis completion and return parsed JSON plus metadata."""
        messages = bundle.messages()
        response_formats: list[dict[str, Any] | None] = [
            {
                "type": "json_schema",
                "json_schema": {
                    "name": "wiki_synthesis_cache_entry",
                    "schema": synthesis_response_json_schema(),
                    "strict": False,
                },
            },
            {"type": "json_object"},
            None,
        ]
        last_error = ""
        fmt_index = 0
        for attempt in range(3):
            try:
                response_format = response_formats[min(fmt_index, len(response_formats) - 1)]
                kwargs: dict[str, Any] = {
                    "model": model,
                    "messages": messages,
                    "timeout": 120.0,
                }
                if response_format is not None:
                    kwargs["response_format"] = response_format
                completion = self._client.chat.completions.create(**cast(Any, kwargs))
                raw = completion.choices[0].message.content or ""
                payload = parse_json_object(raw)
                validate_synthesis_content_payload(payload)
                return payload, {
                    "request_id": completion.id,
                    "token_usage": completion.usage.model_dump() if completion.usage else None,
                }
            except json.JSONDecodeError as exc:
                last_error = f"json: {exc}"
                LOGGER.warning("Synthesis JSON decode failed: %s", last_error)
                messages = _repair_messages(bundle, last_error)
            except ValueError as exc:
                last_error = f"validate: {exc}"
                LOGGER.warning("Synthesis payload validation failed: %s", last_error)
                messages = _repair_messages(bundle, last_error)
            except Exception as exc:
                last_error = str(exc)
                LOGGER.warning("Synthesis OpenAI call failed: %s", last_error)
                fmt_index += 1
            time.sleep(0.5 * (attempt + 1))
        msg = f"OpenAI synthesis failed for {bundle.entity_id}: {last_error}"
        raise RuntimeError(msg)


def _repair_messages(bundle: PromptBundle, error: str) -> list[dict[str, str]]:
    """Return messages asking the provider to repair invalid JSON."""
    repair = (
        "\n\nPREVIOUS OUTPUT FAILED VALIDATION\n"
        f"{error[:4000]}\n"
        "Return corrected JSON only. Preserve the requested schema."
    )
    return [
        {"role": "system", "content": bundle.system_prompt},
        {"role": "user", "content": bundle.user_prompt + repair},
    ]
