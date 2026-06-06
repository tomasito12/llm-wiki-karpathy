"""OpenAI per-proposal regeneration (rubrics + shared completion runner)."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from typing import Any

from openai import APIError, APITimeoutError, RateLimitError
from pydantic import BaseModel, ValidationError

from src.ingest_review.extract import SourceDocument
from src.ingest_review.schema import (
    PROMPT_VERSION,
    GlossaryRegenerateOutput,
    HowToRegenerateOutput,
    ImplStudyRegenerateOutput,
    ModelRegenerateOutput,
    ToolRegenerateOutput,
    TopicRegenerateOutput,
    TrendRegenerateOutput,
)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an analyst helping curate a personal AI-engineering Markdown wiki.
Respond with structured JSON only when asked. Ground claims in supplied source text."""


def _parse_json_content(raw: str) -> dict[str, Any]:
    return json.loads(raw)


def _truncate_plain_text(plain: str, max_chars: int | None) -> str:
    if max_chars is None or len(plain) <= max_chars:
        return plain
    return plain[:max_chars] + "\n[TRUNCATED]"


def resolve_effective_regen_title(
    reviewer_title: str,
    regen_dict: dict[str, Any],
) -> str:
    """Use reviewer title when set; otherwise fall back to LLM ``proposed_title``."""
    explicit = reviewer_title.strip()
    if explicit:
        return explicit
    return str(regen_dict.get("proposed_title") or "").strip()


def regen_payload_for_apply(regen_dict: dict[str, Any]) -> dict[str, Any]:
    """Drop title-only fields before merging regenerated content into artifacts."""
    payload = dict(regen_dict)
    payload.pop("proposed_title", None)
    return payload


TOPIC_REGEN_RUBRIC = """\
Regenerate ONE topic contribution under a reviewer-supplied NEW_TOPIC_TITLE.

Rules:
- Reframe all fields for the broader title NEW_TOPIC_TITLE — stable wiki page name, broad \
enough to accumulate knowledge across sources.
- Move narrower angles into knowledge_summary and examples — NOT into the title.
- Ground every claim in ARTICLE_PLAIN_TEXT via supporting_snippet; do not invent facts.
- Source-agnostic voice in relevance_note; no article-specific framing.
- related_topics: kebab-case slugs from EXISTING_TOPIC_SLUGS only.
- Follow REVIEWER_NOTE when provided. Do not output topic_title or topic_slug."""

GLOSSARY_REGEN_RUBRIC = """\
Regenerate ONE glossary term proposal under reviewer-supplied NEW_TERM.

Rules:
- Reframe definition and explanations for NEW_TERM as the stable wiki concept label.
- Ground in ARTICLE_PLAIN_TEXT; do not invent facts.
- Source-agnostic relevance_note; no "this article says…".
- Follow REVIEWER_NOTE when provided. Do not output term."""

HOWTO_REGEN_RUBRIC = """\
Regenerate ONE how-to proposal under reviewer-supplied NEW_PAGE_TITLE.

Rules:
- Reframe under the broader how-to page title NEW_PAGE_TITLE (noun phrase, not a question).
- what_and_problem and answer_summary: plain everyday language (easy read).
- Move situational qualifiers into what_and_problem / answer_summary, not the title.
- related_howtos: slugs/titles from context lists only.
- Follow REVIEWER_NOTE. Do not output question_title."""

TREND_REGEN_RUBRIC = """\
Regenerate ONE industry trend under reviewer-supplied NEW_TREND_TITLE.

Rules:
- Reframe for broader pattern NEW_TREND_TITLE; move narrower angles into trend_description.
- When REVIEWER_NOTE asks to simplify a title, apply trend-title decomposition: keep one \
outcome-level transition in the title and move mechanisms into body fields. Otherwise keep \
NEW_TREND_TITLE verbatim.
- When REVIEWER_NOTE asks to split a compound trend, regenerate only the one trend named by \
NEW_TREND_TITLE and keep independently varying transitions out of this proposal.
- uncertainty_note is REQUIRED (non-empty).
- related_trends: kebab-case trend_slug values from EXISTING_TREND_SLUGS only.
- Ground in ARTICLE_PLAIN_TEXT; measured, evidence-grounded voice.
- Follow REVIEWER_NOTE. Do not output trend_title or trend_slug."""

TOOL_REGEN_RUBRIC = """\
Regenerate ONE tool proposal under reviewer-supplied NEW_TOOL_NAME.

Rules:
- Reframe operational intelligence for NEW_TOOL_NAME as the product identity.
- strengths / weaknesses_limitations: explanatory prose or bullets — NOT keyword dumps.
- Ground in ARTICLE_PLAIN_TEXT; skeptical, operational voice.
- related_tools: names from EXISTING_TOOL_NAMES when applicable.
- Follow REVIEWER_NOTE. Do not output name."""

MODEL_REGEN_RUBRIC = """\
Regenerate ONE foundation model proposal under reviewer-supplied NEW_MODEL_NAME.

Rules:
- Reframe for NEW_MODEL_NAME; update provider if the source supports a different vendor.
- operational_profile / deployment_implications: non-overlapping explanatory prose or \
bullets — NOT keyword dumps; do not split the same substance across both fields.
- weaknesses_limitations: same depth rules.
- Ground in ARTICLE_PLAIN_TEXT; operational evaluation voice.
- related_models: names from EXISTING_FOUNDATION_MODEL_NAMES when applicable.
- Follow REVIEWER_NOTE. Do not output model_name."""

FORCED_EXTRACT_PREAMBLE = """\
## FORCED EXTRACTION (reviewer-initiated)

The automatic classifier skipped or missed this item. CURRENT_PROPOSAL_JSON is empty.
Extract a NEW proposal for the reviewer-supplied title from ARTICLE_PLAIN_TEXT only.
Ground every claim in the source; do not refuse because the piece is introductory or generic.
If the source only partially supports the title, extract the best defensible contribution and \
note limits in relevance_note / uncertainty_note / caveats as appropriate."""

IMPL_STUDY_REGEN_RUBRIC = """\
Regenerate ONE implementation study under reviewer-supplied NEW_STUDY_TITLE.

Rules:
- Reframe the case study narrative for NEW_STUDY_TITLE as the stable wiki page title.
- Preserve deployment-specific detail in body fields; title stays broad enough to accumulate \
studies.
- Ground claims in ARTICLE_PLAIN_TEXT; do not invent facts.
- Follow REVIEWER_NOTE. Do not output title. Do not output evidence_snippets."""


@dataclass(frozen=True)
class _ProposalRegenProviderConfig:
    rubric: str
    new_title_key: str
    output_model: type[BaseModel]
    schema_name: str
    output_type_name: str


PROPOSAL_REGEN_PROVIDER_CONFIGS: dict[str, _ProposalRegenProviderConfig] = {
    "topic": _ProposalRegenProviderConfig(
        rubric=TOPIC_REGEN_RUBRIC,
        new_title_key="NEW_TOPIC_TITLE",
        output_model=TopicRegenerateOutput,
        schema_name="topic_proposal_regen",
        output_type_name="TopicRegenerateOutput",
    ),
    "glossary": _ProposalRegenProviderConfig(
        rubric=GLOSSARY_REGEN_RUBRIC,
        new_title_key="NEW_TERM",
        output_model=GlossaryRegenerateOutput,
        schema_name="glossary_proposal_regen",
        output_type_name="GlossaryRegenerateOutput",
    ),
    "how_to": _ProposalRegenProviderConfig(
        rubric=HOWTO_REGEN_RUBRIC,
        new_title_key="NEW_PAGE_TITLE",
        output_model=HowToRegenerateOutput,
        schema_name="howto_proposal_regen",
        output_type_name="HowToRegenerateOutput",
    ),
    "trend": _ProposalRegenProviderConfig(
        rubric=TREND_REGEN_RUBRIC,
        new_title_key="NEW_TREND_TITLE",
        output_model=TrendRegenerateOutput,
        schema_name="trend_proposal_regen",
        output_type_name="TrendRegenerateOutput",
    ),
    "tool": _ProposalRegenProviderConfig(
        rubric=TOOL_REGEN_RUBRIC,
        new_title_key="NEW_TOOL_NAME",
        output_model=ToolRegenerateOutput,
        schema_name="tool_proposal_regen",
        output_type_name="ToolRegenerateOutput",
    ),
    "model": _ProposalRegenProviderConfig(
        rubric=MODEL_REGEN_RUBRIC,
        new_title_key="NEW_MODEL_NAME",
        output_model=ModelRegenerateOutput,
        schema_name="model_proposal_regen",
        output_type_name="ModelRegenerateOutput",
    ),
    "impl_study": _ProposalRegenProviderConfig(
        rubric=IMPL_STUDY_REGEN_RUBRIC,
        new_title_key="NEW_STUDY_TITLE",
        output_model=ImplStudyRegenerateOutput,
        schema_name="impl_study_proposal_regen",
        output_type_name="ImplStudyRegenerateOutput",
    ),
}


def run_proposal_regeneration(
    client: Any,
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
    """Call OpenAI to regenerate one proposal; return (output dict, meta)."""
    cfg = PROPOSAL_REGEN_PROVIDER_CONFIGS.get(entity_key)
    if not cfg:
        raise ValueError(f"Unknown proposal regen entity: {entity_key}")

    from src.ingest_review.proposal_regen import REGEN_SPECS
    from src.ingest_review.providers.openai_provider import (
        PAGE_MATCHING_RUBRIC,
        TITLE_CANONICALIZATION_RUBRIC,
        TITLE_GENERATION_RUBRIC,
    )

    reviewer_title = new_title.strip()
    auto_title = not reviewer_title
    regen_spec = REGEN_SPECS.get(entity_key)
    current_title = ""
    if regen_spec:
        current_title = str(current_item.get(regen_spec.title_field) or "").strip()

    body = _truncate_plain_text(document.plain_text, max_plain_text_chars)
    current_json = json.dumps(current_item, ensure_ascii=False)
    forced = not current_item
    user_blocks = [
        f"prompt_version: {prompt_version or PROMPT_VERSION}",
        f"source_id: {document.source_id}",
    ]
    if auto_title:
        user_blocks.append(
            f"REVIEWER_SET_{cfg.new_title_key}: (none — you must propose a new wiki page title "
            f"in proposed_title)"
        )
        user_blocks.append(f"CURRENT_{cfg.new_title_key}: {current_title or '(none)'}")
    else:
        user_blocks.append(f"{cfg.new_title_key}: {reviewer_title}")
    if forced:
        user_blocks.append(FORCED_EXTRACT_PREAMBLE)
    user_blocks.extend(
        [
            f"PROPOSAL_REGEN_RUBRIC:\n{cfg.rubric}",
            f"TITLE_GENERATION_RUBRIC:\n{TITLE_GENERATION_RUBRIC}",
            f"TITLE_CANONICALIZATION_RUBRIC:\n{TITLE_CANONICALIZATION_RUBRIC}",
            f"PAGE_MATCHING_RUBRIC:\n{PAGE_MATCHING_RUBRIC}",
            "## REVIEWER_NOTE\n"
            + (reviewer_instruction.strip() if reviewer_instruction else "(none)"),
            "## CURRENT_PROPOSAL_JSON\n" + current_json,
        ]
    )
    for heading, content in context_sections.items():
        user_blocks.append(f"## {heading}\n{content}")
    if source_entity_key and source_entity_key != entity_key:
        from src.ingest_review.proposal_transfer import transfer_target_label

        src_spec = REGEN_SPECS.get(source_entity_key)
        tgt_spec = REGEN_SPECS.get(entity_key)
        src_label = src_spec.entity_label if src_spec else source_entity_key
        tgt_label = tgt_spec.entity_label if tgt_spec else entity_key
        tgt_display = transfer_target_label(source_entity_key, entity_key)
        user_blocks.append(
            "## RECLASSIFICATION\n"
            f"This proposal was originally classified as a **{src_label}**. "
            f"Re-extract it as a **{tgt_display}** ({tgt_label}) contribution. "
            f"Use {tgt_label.lower()}-appropriate fields only; do not copy "
            f"{src_label.lower()}-specific framing into the output."
        )
    if auto_title:
        entity_title_field = regen_spec.title_field if regen_spec else "title"
        title_instruction = (
            f"Return one JSON object matching {cfg.output_type_name}. "
            "Include non-empty proposed_title with your chosen wiki page title. "
            "Follow REVIEWER_NOTE for how to change the title when provided; otherwise "
            f"propose a clearer, broader title distinct from CURRENT_{cfg.new_title_key} "
            "when possible. Regenerate all content fields for proposed_title. "
            f"Do not output the entity title field ({entity_title_field})."
        )
    else:
        title_instruction = (
            f"Return one JSON object matching {cfg.output_type_name} (content fields only; "
            f"do not output the reviewer-set title field). Leave proposed_title empty."
        )
    user_blocks.extend(
        [
            "## ARTICLE_PLAIN_TEXT\n" + body,
            "## Instructions\n" + title_instruction,
        ]
    )
    user_prompt = "\n\n".join(user_blocks)
    regen_schema = cfg.output_model.model_json_schema()
    system_suffix = f" Respond with one JSON object only; {cfg.output_type_name} fields only."
    if auto_title:
        system_suffix = (
            f" Respond with one JSON object only; {cfg.output_type_name} fields including "
            "proposed_title when the reviewer did not set a title."
        )
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT + system_suffix,
        },
        {"role": "user", "content": user_prompt},
    ]
    response_formats: list[dict[str, Any] | None] = [
        {
            "type": "json_schema",
            "json_schema": {
                "name": cfg.schema_name,
                "schema": regen_schema,
                "strict": False,
            },
        },
        {"type": "json_object"},
        None,
    ]
    last_error: str | None = None
    max_attempts = max(2, max_retries) * 2
    fmt_index = 0
    for attempt in range(max_attempts):
        response_format = response_formats[min(fmt_index, len(response_formats) - 1)]
        try:
            kwargs: dict[str, Any] = {
                "model": model,
                "messages": messages,
                "timeout": 90.0,
            }
            if response_format is not None:
                kwargs["response_format"] = response_format
            completion = client.chat.completions.create(**kwargs)
            raw = completion.choices[0].message.content or ""
            data = _parse_json_content(raw)
            out = cfg.output_model.model_validate(data)
            meta: dict[str, Any] = {
                "request_id": completion.id,
                "token_usage": completion.usage.model_dump() if completion.usage else None,
                "prompt_version": prompt_version or PROMPT_VERSION,
            }
            return out.model_dump(mode="json"), meta
        except (json.JSONDecodeError, ValidationError, TypeError, ValueError) as exc:
            last_error = str(exc)
            logger.warning("%s regen parse/validate failed: %s", entity_key, last_error)
            messages = [
                messages[0],
                {
                    "role": "user",
                    "content": user_prompt
                    + "\n\n## Previous output failed\n"
                    + str(exc)[:4000]
                    + f"\nReturn corrected {cfg.output_type_name} JSON only.",
                },
            ]
            time.sleep(0.3 * (attempt + 1))
        except (RateLimitError, APITimeoutError, APIError) as exc:
            last_error = str(exc)
            logger.warning("%s regen HTTP error: %s", entity_key, last_error)
            if isinstance(exc, RateLimitError) or "429" in last_error:
                time.sleep(2.0 * (attempt + 1))
            else:
                fmt_index += 1
    raise RuntimeError(f"OpenAI {entity_key} regeneration failed: {last_error}")
