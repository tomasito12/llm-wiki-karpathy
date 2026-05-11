"""High-level classification analysis orchestration."""

from __future__ import annotations

from pathlib import Path

from src.ingest_review.artifact import build_new_artifact, default_analysis_meta
from src.ingest_review.extract import SourceDocument
from src.ingest_review.providers.base import IngestionProvider
from src.ingest_review.schema import PROMPT_VERSION, LlmClassificationOutput
from src.ingest_review.wiki_snapshot import build_wiki_snapshot


def apply_tag_allowlists(
    parsed: LlmClassificationOutput,
    tool_tags: set[str],
    howto_tags: set[str],
) -> LlmClassificationOutput:
    """Drop LLM-proposed tags that are not on the allowlists."""
    new_tools = [
        tp.model_copy(update={"proposed_tags": [x for x in tp.proposed_tags if x in tool_tags]})
        for tp in parsed.tools
    ]
    new_how = [
        hp.model_copy(update={"proposed_tags": [x for x in hp.proposed_tags if x in howto_tags]})
        for hp in parsed.how_to
    ]
    return parsed.model_copy(update={"tools": new_tools, "how_to": new_how})


def run_classification(
    provider: IngestionProvider,
    document: SourceDocument,
    *,
    wiki_root: Path,
    tool_tags: list[str],
    howto_tags: list[str],
    model: str,
    prompt_version: str | None = None,
) -> tuple[dict[str, object], LlmClassificationOutput]:
    """Run provider analysis and return ``(artifact_dict, parsed_output)``."""
    pv = prompt_version or PROMPT_VERSION
    wiki = build_wiki_snapshot(wiki_root)
    parsed, meta = provider.analyze_classification(
        document=document,
        wiki=wiki,
        tool_tags_allowlist=tool_tags,
        howto_tags_allowlist=howto_tags,
        model=model,
        prompt_version=pv,
    )
    parsed = apply_tag_allowlists(parsed, set(tool_tags), set(howto_tags))
    analysis_meta = default_analysis_meta(
        provider=provider.provider_name,
        model=model,
        prompt_version=pv,
    )
    analysis_meta["request_id"] = meta.get("request_id")
    analysis_meta["token_usage"] = meta.get("token_usage")
    artifact = build_new_artifact(document, parsed, analysis_meta=analysis_meta)
    return artifact, parsed


def validate_llm_dict(data: dict[str, object]) -> LlmClassificationOutput:
    """Validate a dict against :class:`LlmClassificationOutput`; raise on failure."""
    return LlmClassificationOutput.model_validate(data)
