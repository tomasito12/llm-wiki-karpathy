---
title: Grouped Query Attention
slug: grouped-query-attention
entity_id: glossary:grouped-query-attention
category: glossary
tags:
- inference
- memory-systems
first_seen: '2026-05-16'
last_seen: '2026-06-01'
source_count: 2
evidence_count: 8
source_ids:
- how-llms-actually-work-01kv4tanr9r0k17sysdm6cv45b
- recent-developments-in-llm-architectures-kv-sharing-mhc-and-compressed-attention-01krrba0929cn5qjh3gve00hyf
value_level: high
confidence: 0.935
synthesis_state: synthesized
synthesis_stale: false
synthesis_input_hash: 5a8cc31641d8aa52
current_input_hash: 5a8cc31641d8aa52
synthesis_schema_version: 1
synthesis_prompt_version: 1
last_synthesized_at: '2026-06-17T19:54:23Z'
---

# Grouped Query Attention

## Executive synthesis

Grouped Query Attention (GQA) is a transformer attention variant where several query heads reuse the same key and value heads. That reduces KV-cache size and makes decoding cheaper, which is why it is used as a practical inference optimization in modern decoder-only LLMs. The sources frame it as a common compromise between full multi-head attention and more aggressive sharing schemes, especially useful when long contexts, large batches, or agent-style workloads make memory pressure a bottleneck.

## Context card

- **Use this page when:** Use this page when you need a quick definition of GQA and a practical sense of why it matters for inference memory and latency.
- **Best for questions about:** What GQA is in transformer attention, Why GQA reduces KV-cache and inference cost, When GQA matters in model serving, How GQA differs from full multi-head attention at a high level
- **Not enough for:** A full mathematical derivation of GQA, Exact implementation details across model families, Performance tradeoffs for a specific model or benchmark, Whether GQA is always better than alternative KV-sharing schemes
- **Strongest sources:** How LLMs Actually Work, Recent Developments in LLM Architectures: KV Sharing, mHC, and Compressed Attention
- **Related tags:** inference, memory-systems

## What to remember

- Multiple query heads share fewer key/value heads.
- Main payoff: smaller KV cache and cheaper inference.
- Useful when long context or many concurrent requests make memory a bottleneck.
- A common compromise between model quality and serving efficiency.
- Not the same as full multi-head attention, where each head has its own K/V projections.

## Consensus

- Grouped Query Attention (GQA) is an attention variant where multiple query heads share fewer key and value heads.
- Its main benefit is lower KV-cache memory use and cheaper inference/decoding than full multi-head attention.
- It is a practical efficiency compromise: it keeps multiple query heads while reducing memory pressure.
- It is especially relevant for long-context serving, large batch decoding, and conversational/agent systems with tight latency or memory budgets.
- Modern decoder-only LLMs commonly use GQA, according to both sources.

## Tensions / open questions

- The sources agree on the core mechanism, but one source emphasizes GQA as a standard practical pattern while the other places it among newer efficiency refinements.
- One source mentions Gemma 4 using GQA, but also notes additional KV sharing across layers, so that example should not be treated as a pure GQA-only case.
- The sources do not provide detailed tradeoff data, so quality-vs-efficiency boundaries remain qualitative here.

## Evidence quality

- Evidence is strong for the basic definition and serving relevance: two independent reviewed sources agree.
- Evidence is weaker for broader architectural claims, since the sources focus on practical framing rather than formal theory.
- The page is time-sensitive in the sense that it reflects current LLM serving practice, not a timeless taxonomy of attention variants.

## Practical takeaway

Remember GQA as a serving-friendly attention design: it keeps multiple query heads but shares key/value heads to cut memory and inference cost, so it is most useful when cache size and latency matter.

## Evidence index

- Sources: 2
- Evidence items: 8
- Current input hash: `5a8cc31641d8aa52`
- Cached input hash: `5a8cc31641d8aa52`
- Last synthesized: 2026-06-17T19:54:23Z
- Synthesis status: `fresh`

## Related pages

- [[glossary/kv-cache|KV cache]]

## Sources

- [[sources/how-llms-actually-work-01kv4tanr9r0k17sysdm6cv45b|How LLMs Actually Work]]
- [[sources/recent-developments-in-llm-architectures-kv-sharing-mhc-and-compressed-attention-01krrba0929cn5qjh3gve00hyf|Recent Developments in LLM Architectures: KV Sharing, mHC, and Compressed Attention]]
