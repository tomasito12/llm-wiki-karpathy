---
title: How LLMs Actually Work
slug: how-llms-actually-work-01kv4tanr9r0k17sysdm6cv45b
category: source
tags:
- ai-engineering
- developer-tools
- inference
- infrastructure
- memory-systems
- runtime-architecture
- runtime-systems
- software-engineering
source_id: how-llms-actually-work-01kv4tanr9r0k17sysdm6cv45b
author: 0xkato
publication: 0Xkato
published_date: '2026-06-01'
assessed_as_of: '2026-06-01'
ingested_at: '2026-06-15T23:09:44+00:00'
canonical_url: https://0xkato.xyz/how-llms-actually-work/
content_sha256: 46ba907bdd8d1e81067793887d0801beab0e2be96b161de34f551d49af5cb268
derived_glossary:
- glossary/grouped-query-attention.md
- glossary/kv-cache.md
derived_how_to:
- how-to/reading-transformer-model-cards.md
derived_topics:
- topics/transformer-llm-architecture.md
derived_trends:
- industry-trends/ai-products-shift-from-models-to-systems.md
derived_pages:
- glossary/grouped-query-attention.md
- glossary/kv-cache.md
- how-to/reading-transformer-model-cards.md
- industry-trends/ai-products-shift-from-models-to-systems.md
- topics/transformer-llm-architecture.md
---

# How LLMs Actually Work

This is a plain-English map of how an LLM works under the hood. It starts with text being broken into token IDs, turns those IDs into vectors, adds position information, and then lets tokens exchange information through attention. After that, each layer also does token-by-token processing in a feed-forward network, with residual connections and normalization keeping deep models trainable. The article also explains why modern models use RoPE, grouped-query attention, and sometimes mixture-of-experts. The key takeaway is that many famous model names differ more in weights and training choices than in the basic transformer skeleton.

## Key insights

- Tokenization is a real capability constraint: the model sees token IDs, not letters, so some obvious human tasks fail because the representation is subword-based.
- RoPE is presented as a better default than additive position schemes because it encodes relative distance directly in attention and adds no parameters.
- The feed-forward network is not just a minor helper; the article treats it as where much of a dense model’s stored factual and semantic structure lives.
- Grouped-query attention reduces KV-cache memory pressure by sharing key/value heads across query heads, which matters for inference at long context lengths.
- Mixture-of-experts shifts scaling by increasing total parameters without increasing per-token compute proportionally, but only a few experts run for any token.

## Derived knowledge pages

- [[glossary/grouped-query-attention]]
- [[glossary/kv-cache]]
- [[how-to/reading-transformer-model-cards]]
- [[industry-trends/ai-products-shift-from-models-to-systems]]
- [[topics/transformer-llm-architecture]]

## Why it matters

The article is useful because it compresses the transformer stack into the pieces an engineer actually needs to recognize when reading a model card, paper, or architecture diagram. It cleanly separates what is broadly shared across modern LLMs from what is mostly a training or configuration choice, which helps avoid overinterpreting brand-name differences between models. The explanation of tokenization, embeddings, positional encoding, and attention gives a practical mental model for why prompt length, ordering, and vocabulary choice affect model behavior. The sections on residual streams, layer normalization, and the feed-forward network are especially helpful because they explain why deep models train at all and where much of a model’s stored structure appears to live. The discussion of GQA, KV cache, and speculative decoding also points to concrete inference-cost tradeoffs that matter when deploying transformer systems. The article is less about product tactics than about durable architecture literacy, so its operational value is mainly in helping practitioners reason about what a given model can and cannot do from its design. Actionable as of 2026-06-01, and likely durable because the source argues these are the stable transformer mechanisms that still organize modern model design.

## Limitations / open questions

The piece is intentionally introductory, so it does not provide math, implementation details, or quantitative comparisons for most claims. Several statements rely on named research findings without reproducing the experimental evidence, so a reader would still need primary sources for rigorous validation. It notes that some modern models use mixture-of-experts and that alternatives like Mamba exist, but it does not compare these approaches on cost, quality, or deployment complexity. The discussion of facts living in feed-forward weights and of targeted edits such as ROME is informative, but it does not address reliability, side effects, or safety implications of such edits. It also does not discuss evaluation, robustness, or adversarial behavior in depth.

## Contradictions / unverified claims

The article simplifies several mechanisms for teaching purposes, especially attention, induction heads, and where semantic knowledge is stored, so readers should not treat the explanations as full mechanistic accounts. Some examples, like embedding arithmetic and single-neuron concept associations, are useful intuitions but can overstate how neatly meaning localizes in practice. The claim that RoPE or GQA are broadly adopted is consistent with the text, but the piece does not quantify how universal these choices are across all modern LLMs. The overall framing is solid, but it remains a synthesis article rather than a benchmarked technical report.

## Source metadata

- Canonical URL: https://0xkato.xyz/how-llms-actually-work/
- Raw markdown: `raw/readwise/how-llms-actually-work-01kv4tanr9r0k17sysdm6cv45b.md`
- Raw HTML: `raw/readwise/how-llms-actually-work-01kv4tanr9r0k17sysdm6cv45b.html`
