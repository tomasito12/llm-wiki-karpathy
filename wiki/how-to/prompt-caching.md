---
title: Prompt Caching
slug: prompt-caching
entity_id: how_to:prompt-caching
category: how-to
tags:
- ai-economics
- inference-systems
- prompt-engineering
- runtime-systems
first_seen: '2026-05-08'
last_seen: '2026-05-08'
source_count: 1
evidence_count: 13
source_ids:
- agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv
value_level: high
confidence: 0.95
synthesis_state: stage1-placeholder
---

# Prompt Caching

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Prompt caching is a way to avoid paying to process the same long instructions every time an agent calls a model. It matters when an agent has a large stable prompt, such as a system prompt, examples, or tool definitions, that would otherwise be sent again and again. The goal is to reduce both latency and token cost without changing the task itself. It is most useful when the front of the prompt stays fixed across many calls.

## Caveats

Exact matching is required, so tiny prompt changes can eliminate the cache hit. Cached state takes memory on the serving side, and providers may evict it after a short time window. Savings depend on prompt stability and on the provider's pricing rules, so illustrative numbers in the article are not universal.

## Implementation Steps

- Identify the stable prefix of the prompt: system instructions, examples, and tools.
- Place that stable content before any user-specific or variable content.
- Keep the cached section byte-for-byte consistent across requests.
- If self-hosting, enable prefix caching in the serving framework and tune cache block size and memory limits.
- If using a provider API, follow the provider's cache parameters and prompt structure requirements.
- Audit prompt drift from timestamps, reordered tool blocks, and formatting changes.

## Prerequisites

- A long prompt that repeats across requests.
- A serving stack or API that supports prompt or prefix caching.
- A prompt design that cleanly separates stable and variable sections.

## Related Howtos

- context-engineering

## Evidence / supporting sources

### Agentic AI: How to Save on Tokens (2026-05-08)

- Put the stable part of the prompt first, keep it exactly the same, and let the variable user-specific content come later. If you are using a provider that supports it, make sure the request meets the provider's cache rules so the repeated prefix can be reused. For self-hosted inference, use a serving framework that supports prefix caching and keep the reusable content in the first part of the prompt. Treat cache hits as a systems problem: even small changes such as spacing, timestamps, or reordered tool definitions can break reuse. Use it first when you have long prompts that do not change much across calls. (`694ad8763207` · neutral · answer_summary; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- Identify the stable prefix of the prompt: system instructions, examples, and tools. (`511a64a6eb5a` · neutral · implementation_steps[0]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- Place that stable content before any user-specific or variable content. (`f68e70a28769` · neutral · implementation_steps[1]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- Keep the cached section byte-for-byte consistent across requests. (`058dca0486bb` · neutral · implementation_steps[2]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- If self-hosting, enable prefix caching in the serving framework and tune cache block size and memory limits. (`a9e1405f62df` · neutral · implementation_steps[3]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- If using a provider API, follow the provider's cache parameters and prompt structure requirements. (`e76594570413` · neutral · implementation_steps[4]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- Audit prompt drift from timestamps, reordered tool blocks, and formatting changes. (`5f8bb67615bf` · neutral · implementation_steps[5]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- A long prompt that repeats across requests. (`a8bca1653dda` · neutral · prerequisites[0]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- A serving stack or API that supports prompt or prefix caching. (`94c69f0d5baa` · neutral · prerequisites[1]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- A prompt design that cleanly separates stable and variable sections. (`5ff28557de49` · neutral · prerequisites[2]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- Prompt caching is a way to avoid paying to process the same long instructions every time an agent calls a model. It matters when an agent has a large stable prompt, such as a system prompt, examples, or tool definitions, that would otherwise be sent again and again. The goal is to reduce both latency and token cost without changing the task itself. It is most useful when the front of the prompt stays fixed across many calls. (`3d086ba2b311` · neutral · what_and_problem; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- "Prompt caching is a quick win for long system prompts" ... "you always put stable instructions, examples, and tools first, and variable content later." (`996359e5494f` · supporting · supporting_snippet; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- Exact matching is required, so tiny prompt changes can eliminate the cache hit. Cached state takes memory on the serving side, and providers may evict it after a short time window. Savings depend on prompt stability and on the provider's pricing rules, so illustrative numbers in the article are not universal. (`8c8b17c4313c` · uncertainty · caveats; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])

## Contradictions / tensions

- Exact matching is required, so tiny prompt changes can eliminate the cache hit. Cached state takes memory on the serving side, and providers may evict it after a short time window. Savings depend on prompt stability and on the provider's pricing rules, so illustrative numbers in the article are not universal. (uncertainty; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])

## Related pages

- context-engineering

## Sources

- [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]]
