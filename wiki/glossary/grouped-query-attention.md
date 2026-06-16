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
synthesis_state: stage1-placeholder
---

# Grouped Query Attention

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Grouped Query Attention is an attention variant where multiple query heads share fewer key and value heads. It reduces memory and inference cost compared with full multi-head attention while preserving much of the model’s behavior.

## Related Terms

- KV cache

## Relevance Note

A practical inference optimization for transformer serving. Teams running assistants, support bots, or agent loops care because GQA can reduce memory pressure without requiring a different product architecture.

## Evidence / supporting sources

### How LLMs Actually Work (2026-06-01)

- In standard multi-head attention, each head has its own Key and Value projections. GQA cuts that down by letting groups of query heads share the same Key and Value heads. That lowers KV-cache memory and makes decoding cheaper, which matters a lot at large batch sizes or long context lengths. It is one of the architectural refinements that made modern decoder-only LLMs more practical to run. (`638eb2b7e1be` · neutral · extended_explanation; [[sources/how-llms-actually-work-01kv4tanr9r0k17sysdm6cv45b|How LLMs Actually Work]])
- Grouped Query Attention is an attention variant where multiple query heads share fewer key and value heads. It reduces memory and inference cost compared with full multi-head attention while preserving much of the model’s behavior. (`5992a0bc1258` · neutral · proposed_definition; [[sources/how-llms-actually-work-01kv4tanr9r0k17sysdm6cv45b|How LLMs Actually Work]])
- A practical inference optimization for transformer serving. Teams running assistants, support bots, or agent loops care because GQA can reduce memory pressure without requiring a different product architecture. (`304436077339` · neutral · relevance_note; [[sources/how-llms-actually-work-01kv4tanr9r0k17sysdm6cv45b|How LLMs Actually Work]])
- "Modern decoder-only LLMs mostly use a variant called Grouped-Query Attention (GQA). Instead of every head having its own keys and values, groups of heads share the same key and value heads." (`594faba00dd1` · supporting · supporting_snippet; [[sources/how-llms-actually-work-01kv4tanr9r0k17sysdm6cv45b|How LLMs Actually Work]])

### Recent Developments in LLM Architectures: KV Sharing, mHC, and Compressed Attention (2026-05-16)

- GQA sits between full multi-head attention and more aggressive sharing schemes. Instead of giving every query head its own key and value projections, several query heads reuse the same KV heads. That lowers memory use and can make long-context inference cheaper. It is widely relevant because many modern LLMs use it as a practical compromise between quality and efficiency. (`a4e016b639ea` · neutral · extended_explanation; [[sources/recent-developments-in-llm-architectures-kv-sharing-mhc-and-compressed-attention-01krrba0929cn5qjh3gve00hyf|Recent Developments in LLM Architectures: KV Sharing, mHC, and Compressed Attention]])
- Grouped Query Attention is an attention variant where multiple query heads share the same key and value heads. It reduces the size of the KV cache and can lower attention memory costs while keeping multiple query heads. (`02971d7a5640` · neutral · proposed_definition; [[sources/recent-developments-in-llm-architectures-kv-sharing-mhc-and-compressed-attention-01krrba0929cn5qjh3gve00hyf|Recent Developments in LLM Architectures: KV Sharing, mHC, and Compressed Attention]])
- GQA is a standard efficiency pattern in transformer design and shows up wherever teams need lower cache cost without fully changing the attention mechanism. It matters for conversational systems and agents that must hold longer histories while staying within tight latency and memory budgets. (`ee05509db8d5` · neutral · relevance_note; [[sources/recent-developments-in-llm-architectures-kv-sharing-mhc-and-compressed-attention-01krrba0929cn5qjh3gve00hyf|Recent Developments in LLM Architectures: KV Sharing, mHC, and Compressed Attention]])
- Gemma 4 uses GQA. However, in addition to the KV sharing among queries as part of GQA, Gemma 4 also shares KV projections across different layers (`e77a8a5df707` · supporting · supporting_snippet; [[sources/recent-developments-in-llm-architectures-kv-sharing-mhc-and-compressed-attention-01krrba0929cn5qjh3gve00hyf|Recent Developments in LLM Architectures: KV Sharing, mHC, and Compressed Attention]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- KV cache

## Sources

- [[sources/how-llms-actually-work-01kv4tanr9r0k17sysdm6cv45b|How LLMs Actually Work]]
- [[sources/recent-developments-in-llm-architectures-kv-sharing-mhc-and-compressed-attention-01krrba0929cn5qjh3gve00hyf|Recent Developments in LLM Architectures: KV Sharing, mHC, and Compressed Attention]]
