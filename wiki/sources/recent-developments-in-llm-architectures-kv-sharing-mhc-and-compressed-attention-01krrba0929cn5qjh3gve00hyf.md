---
title: 'Recent Developments in LLM Architectures: KV Sharing, mHC, and Compressed
  Attention'
slug: recent-developments-in-llm-architectures-kv-sharing-mhc-and-compressed-attention-01krrba0929cn5qjh3gve00hyf
category: source
tags:
- ai-engineering
- inference
- inference-efficiency
- inference-efficient
- inference-systems
- infrastructure
- long-context-adoption
- long-context-model
- memory-systems
- open-model-pressure
- open-weight-model
- reasoning-model
- runtime-systems
source_id: recent-developments-in-llm-architectures-kv-sharing-mhc-and-compressed-attention-01krrba0929cn5qjh3gve00hyf
author: Sebastian Raschka, PhD from Ahead of AI
publication: Substack
published_date: '2026-05-16'
assessed_as_of: '2026-05-16'
ingested_at: '2026-06-09T16:52:13+00:00'
canonical_url: mailto:reader-forwarded-email/a09d7102abdeca1fa212460c4d634316
content_sha256: b57264e580959de00b9013873628b37d85abac870916779158b804dc0ccb9c85
derived_glossary:
- glossary/grouped-query-attention.md
- glossary/kv-cache.md
derived_models:
- foundation-models/deepseek-v4.md
derived_topics:
- topics/kv-cache-compression.md
- topics/layer-wise-attention-budgeting.md
derived_trends:
- industry-trends/long-context-efficiency-becomes-an-architecture-priority.md
derived_pages:
- foundation-models/deepseek-v4.md
- glossary/grouped-query-attention.md
- glossary/kv-cache.md
- industry-trends/long-context-efficiency-becomes-an-architecture-priority.md
- topics/kv-cache-compression.md
- topics/layer-wise-attention-budgeting.md
---

# Recent Developments in LLM Architectures: KV Sharing, mHC, and Compressed Attention

This article is about how several new open-weight language models are changing the internals of the transformer block to make long contexts cheaper. Instead of only making models smaller, the designs try to save memory and attention cost in targeted ways. One model shares key-value tensors across layers, another gives different layers different attention budgets, and another moves attention into a compressed latent space. DeepSeek V4 goes further by compressing long-context attention along the sequence and by widening the residual path with constrained mixing. The core idea is simple: keep more context for less cost, but do it with extra architectural complexity.

## Key insights

- Gemma 4’s cross-layer KV sharing is a direct way to cut long-context KV-cache memory by reusing key-value states from earlier layers of the same attention type.
- Gemma 4’s per-layer embeddings add token-specific capacity in a cheaper path than widening the whole transformer stack, which is why the author treats them as an effective-size trick.
- Laguna XS.2 shows a practical pattern for layer-wise attention budgeting: fixed KV heads, but different query-head counts depending on whether a layer uses sliding-window or global attention.
- ZAYA1-8B’s Compressed Convolutional Attention matters because it compresses Q, K, and V and runs attention in the compressed space, so it can reduce both cache size and prefill/training FLOPs.
- DeepSeek V4’s CSA and HCA are sequence-length compression schemes, not just latent KV compression, which makes them a different tradeoff from MLA and explains why the author treats them as more aggressive and more complex.

## Derived knowledge pages

- [[foundation-models/deepseek-v4]]
- [[glossary/grouped-query-attention]]
- [[glossary/kv-cache]]
- [[industry-trends/long-context-efficiency-becomes-an-architecture-priority]]
- [[topics/kv-cache-compression]]
- [[topics/layer-wise-attention-budgeting]]

## Why it matters

The piece is valuable because it compresses several architecture ideas that matter for long-context LLMs into one comparison set, instead of treating each release as a one-off novelty. Gemma 4’s cross-layer KV sharing is a concrete mechanism for reducing cache growth, and the article gives a rough magnitude for the savings at 128K context. That is operationally useful for practitioners who care about memory-bound inference. The per-layer embedding design is also interesting because it separates effective transformer size from embedding capacity, which is a more durable concept than a single model label. Laguna XS.2 adds another reusable pattern: vary attention capacity by layer rather than giving every block identical compute. ZAYA1-8B and DeepSeek V4 are useful mainly as examples of where the design space is heading for long-context efficiency, but the article is careful to note that these are more complex systems with tradeoffs, not obviously universal upgrades. As of 2026-05-16, the practical takeaway is to monitor these mechanisms as specialized tools for long-context and efficiency-sensitive model design, not to assume they generalize cleanly across all model sizes or training regimes. The closing implication for service automation, support, voice, meetings, and back-office workflows is indirect: if long-context inference gets cheaper, those products can hold more conversation history and workflow state, but the article itself does not discuss those applications directly.

## Limitations / open questions

The article is mostly expert interpretation of released architectures, not original benchmarking. Several claims rely on model configs, architecture diagrams, or the author’s reading of papers rather than controlled ablations. For Gemma 4’s per-layer embeddings, the author explicitly notes the need for comparison studies against a regular smaller model and a regular larger model. For DeepSeek V4, the article says there is no ablation study in the paper for CSA/HCA, so the contribution of each component is hard to isolate. The reported efficiency numbers for DeepSeek V4 are tied to the full recipe, which also includes data, optimization, precision/storage, and system changes, so the architecture-only effect is not cleanly separated. The article also does not quantify implementation complexity, memory traffic costs, or inference latency in a standardized way across models.

## Contradictions / unverified claims

The article is optimistic about these techniques, but several of them are clearly approximate and may reduce model capacity or add implementation complexity. The author explicitly warns that KV sharing is an approximation and that its impact depends on scale and setting. The DeepSeek V4 comparison is especially hard to generalize because CSA/HCA are presented as more aggressive than MLA, but the paper does not isolate their effect with ablations. The “effective parameter” framing for Gemma 4 is useful, but it can also blur the distinction between transformer capacity and embedding-table capacity if read too literally. Overall the skeptical reading is that these are promising efficiency tricks, but the evidence here is stronger for architectural plausibility than for universal superiority.

## Source metadata

- Canonical URL: mailto:reader-forwarded-email/a09d7102abdeca1fa212460c4d634316
- Raw markdown: `raw/readwise/recent-developments-in-llm-architectures-kv-sharing-mhc-and-compressed-attention-01krrba0929cn5qjh3gve00hyf.md`
- Raw HTML: `raw/readwise/recent-developments-in-llm-architectures-kv-sharing-mhc-and-compressed-attention-01krrba0929cn5qjh3gve00hyf.html`
