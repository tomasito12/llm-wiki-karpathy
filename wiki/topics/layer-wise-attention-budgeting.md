---
title: Layer-Wise Attention Budgeting
slug: layer-wise-attention-budgeting
entity_id: topic:layer-wise-attention-budgeting
category: topic
tags:
- ai-engineering
- inference-systems
- infrastructure
- runtime-systems
first_seen: '2026-05-16'
last_seen: '2026-05-16'
source_count: 1
evidence_count: 7
source_ids:
- recent-developments-in-llm-architectures-kv-sharing-mhc-and-compressed-attention-01krrba0929cn5qjh3gve00hyf
value_level: high
confidence: 0.95
synthesis_state: stage1-placeholder
---

# Layer-Wise Attention Budgeting

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Layer-wise attention budgeting is the practice of assigning different attention capacity to different transformer layers instead of giving every layer the same budget. In one layer, that can mean using more query heads; in another, fewer heads or a cheaper attention pattern such as sliding-window attention. The reason is to spend compute where it is most useful instead of treating all layers as equal. This can preserve quality while reducing waste in expensive full-context layers.

## Key Points

- Laguna XS.2 uses different query-head counts per layer while keeping KV heads fixed.
- Sliding-window layers can be cheaper while global layers preserve full-context access.
- The same mixed local-plus-global pattern appears in other architectures, so the reusable idea is the per-layer budget, not the specific model.

## Operational Insight

A useful engineering pattern is to budget attention by layer type, not just by model size. That lets teams align compute with the role of the layer and avoid overpaying for uniformly wide attention everywhere.

## Evidence / supporting sources

### Recent Developments in LLM Architectures: KV Sharing, mHC, and Compressed Attention (2026-05-16)

- Layer-wise attention budgeting is the practice of assigning different attention capacity to different transformer layers instead of giving every layer the same budget. In one layer, that can mean using more query heads; in another, fewer heads or a cheaper attention pattern such as sliding-window attention. The reason is to spend compute where it is most useful instead of treating all layers as equal. This can preserve quality while reducing waste in expensive full-context layers. (`b37156804bdb` · neutral · knowledge_summary; [[sources/recent-developments-in-llm-architectures-kv-sharing-mhc-and-compressed-attention-01krrba0929cn5qjh3gve00hyf|Recent Developments in LLM Architectures: KV Sharing, mHC, and Compressed Attention]])
- A useful engineering pattern is to budget attention by layer type, not just by model size. That lets teams align compute with the role of the layer and avoid overpaying for uniformly wide attention everywhere. (`3d9abf0df2e9` · neutral · operational_insight; [[sources/recent-developments-in-llm-architectures-kv-sharing-mhc-and-compressed-attention-01krrba0929cn5qjh3gve00hyf|Recent Developments in LLM Architectures: KV Sharing, mHC, and Compressed Attention]])
- This matters wherever architecture teams need to balance context coverage and serving cost. It is especially relevant for long-context assistants and agent systems that mix local recency with occasional global access to the full conversation or task state. (`e9c806f57155` · neutral · relevance_note; [[sources/recent-developments-in-llm-architectures-kv-sharing-mhc-and-compressed-attention-01krrba0929cn5qjh3gve00hyf|Recent Developments in LLM Architectures: KV Sharing, mHC, and Compressed Attention]])
- Laguna XS.2 uses different query-head counts per layer while keeping KV heads fixed. (`f4eec9013214` · supporting · key_points[0]; [[sources/recent-developments-in-llm-architectures-kv-sharing-mhc-and-compressed-attention-01krrba0929cn5qjh3gve00hyf|Recent Developments in LLM Architectures: KV Sharing, mHC, and Compressed Attention]])
- Sliding-window layers can be cheaper while global layers preserve full-context access. (`5092200b880a` · supporting · key_points[1]; [[sources/recent-developments-in-llm-architectures-kv-sharing-mhc-and-compressed-attention-01krrba0929cn5qjh3gve00hyf|Recent Developments in LLM Architectures: KV Sharing, mHC, and Compressed Attention]])
- The same mixed local-plus-global pattern appears in other architectures, so the reusable idea is the per-layer budget, not the specific model. (`723ddb4294a6` · supporting · key_points[2]; [[sources/recent-developments-in-llm-architectures-kv-sharing-mhc-and-compressed-attention-01krrba0929cn5qjh3gve00hyf|Recent Developments in LLM Architectures: KV Sharing, mHC, and Compressed Attention]])
- instead of giving every transformer layer the same full attention budget, Laguna XS.2 varies the attention cost by layer (`d90a33e755cf` · supporting · supporting_snippet; [[sources/recent-developments-in-llm-architectures-kv-sharing-mhc-and-compressed-attention-01krrba0929cn5qjh3gve00hyf|Recent Developments in LLM Architectures: KV Sharing, mHC, and Compressed Attention]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

No related pages captured.

## Sources

- [[sources/recent-developments-in-llm-architectures-kv-sharing-mhc-and-compressed-attention-01krrba0929cn5qjh3gve00hyf|Recent Developments in LLM Architectures: KV Sharing, mHC, and Compressed Attention]]
