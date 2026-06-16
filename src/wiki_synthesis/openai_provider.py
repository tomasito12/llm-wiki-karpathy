"""OpenAI provider for Stage 2 synthesis execution."""

from __future__ import annotations

import json
import logging
import time
from typing import Any, cast

from src.wiki_synthesis.executor import parse_json_object
from src.wiki_synthesis.prompts import PromptBundle

LOGGER = logging.getLogger(__name__)


class OpenAISynthesisProvider:
    """OpenAI Chat Completions provider for synthesis JSON."""

    def __init__(self) -> None:
        """Initialize the OpenAI client lazily so tests need no OpenAI dependency."""
        from openai import OpenAI

        self._client = OpenAI()

    def close(self) -> None:
        """Close the underlying OpenAI client."""
        self._client.close()

    def synthesize(
        self, bundle: PromptBundle, *, model: str
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Run one synthesis completion and return parsed JSON plus metadata."""
        messages = bundle.messages()
        last_error = ""
        for attempt in range(3):
            try:
                kwargs: dict[str, Any] = {
                    "model": model,
                    "messages": messages,
                    "response_format": {"type": "json_object"},
                    "timeout": 120.0,
                }
                completion = self._client.chat.completions.create(**cast(Any, kwargs))
                raw = completion.choices[0].message.content or ""
                return parse_json_object(raw), {
                    "request_id": completion.id,
                    "token_usage": completion.usage.model_dump() if completion.usage else None,
                }
            except json.JSONDecodeError as exc:
                last_error = f"json: {exc}"
                LOGGER.warning("Synthesis JSON decode failed: %s", last_error)
            except Exception as exc:
                last_error = str(exc)
                LOGGER.warning("Synthesis OpenAI call failed: %s", last_error)
            time.sleep(0.5 * (attempt + 1))
        msg = f"OpenAI synthesis failed for {bundle.entity_id}: {last_error}"
        raise RuntimeError(msg)
