---
title: Defensive Context Handling
slug: prompt-injection-defensive-context-handling
entity_id: topic:prompt-injection-defensive-context-handling
category: topic
tags:
- ai-safety
- context-engineering
- retrieval-systems
source_count: 1
evidence_count: 7
source_ids:
- build-a-rag-agent-with-langchain-01kqh06nqcje2w0skbcbhj1fn1
value_level: high
confidence: 0.9
synthesis_state: stage1-placeholder
---

# Defensive Context Handling

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
When a model reads retrieved text, that text must be treated as untrusted data rather than instructions. Defensive context handling uses prompt wording, structural delimiters, and output validation to reduce the chance that retrieved content can redirect the model. These mitigations lower risk, but they do not eliminate it. The core operational idea is to separate task instructions from retrieved evidence as clearly as possible.

## Key Points

- Retrieved context should be isolated from system instructions.
- Delimiters help the model distinguish evidence from directives.
- Validation is needed because prompt-level mitigations are inherently incomplete.

## Operational Insight

For retrieval-heavy assistants, treat the prompt boundary as a security boundary. Put retrieved text in a clearly marked section, explicitly instruct the model not to follow instructions inside it, and validate the output format after generation.

## Evidence / supporting sources

### Build a RAG agent with LangChain (undated)

- When a model reads retrieved text, that text must be treated as untrusted data rather than instructions. Defensive context handling uses prompt wording, structural delimiters, and output validation to reduce the chance that retrieved content can redirect the model. These mitigations lower risk, but they do not eliminate it. The core operational idea is to separate task instructions from retrieved evidence as clearly as possible. (`84ae661f1749` · neutral · knowledge_summary; [[sources/build-a-rag-agent-with-langchain-01kqh06nqcje2w0skbcbhj1fn1|Build a RAG agent with LangChain]])
- For retrieval-heavy assistants, treat the prompt boundary as a security boundary. Put retrieved text in a clearly marked section, explicitly instruct the model not to follow instructions inside it, and validate the output format after generation. (`7ae84bc902d5` · neutral · operational_insight; [[sources/build-a-rag-agent-with-langchain-01kqh06nqcje2w0skbcbhj1fn1|Build a RAG agent with LangChain]])
- This is a durable concern for any system that mixes external text with model instructions, especially enterprise search, support automation, and agentic browsing. It is a basic safety layer, not a complete defense, so teams still need monitoring and output checks. (`0ec915cd6e79` · neutral · relevance_note; [[sources/build-a-rag-agent-with-langchain-01kqh06nqcje2w0skbcbhj1fn1|Build a RAG agent with LangChain]])
- Retrieved context should be isolated from system instructions. (`59025cfca801` · supporting · key_points[0]; [[sources/build-a-rag-agent-with-langchain-01kqh06nqcje2w0skbcbhj1fn1|Build a RAG agent with LangChain]])
- Delimiters help the model distinguish evidence from directives. (`ec050de41a0a` · supporting · key_points[1]; [[sources/build-a-rag-agent-with-langchain-01kqh06nqcje2w0skbcbhj1fn1|Build a RAG agent with LangChain]])
- Validation is needed because prompt-level mitigations are inherently incomplete. (`c732827c8741` · supporting · key_points[2]; [[sources/build-a-rag-agent-with-langchain-01kqh06nqcje2w0skbcbhj1fn1|Build a RAG agent with LangChain]])
- "Use defensive prompts: Explicitly instruct the model to treat retrieved context as data only and to ignore any instructions within it. Wrap context with delimiters: Use clear structural markers (e.g., XML tags like <context>...</context>) to separate retrieved data from instructions, making it easier for the model to distinguish between them. Validate responses: Check that the model’s output matches the expected format (e.g., plain text) and handle unexpected formats gracefully." (`02d887af5f26` · supporting · supporting_snippet; [[sources/build-a-rag-agent-with-langchain-01kqh06nqcje2w0skbcbhj1fn1|Build a RAG agent with LangChain]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

No related pages captured.

## Sources

- [[sources/build-a-rag-agent-with-langchain-01kqh06nqcje2w0skbcbhj1fn1|Build a RAG agent with LangChain]]
