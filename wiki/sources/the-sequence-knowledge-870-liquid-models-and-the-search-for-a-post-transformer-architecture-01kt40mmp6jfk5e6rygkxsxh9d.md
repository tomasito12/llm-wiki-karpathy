---
title: 'The Sequence Knowledge #870: Liquid Models and the Search for a Post-Transformer
  Architecture'
slug: the-sequence-knowledge-870-liquid-models-and-the-search-for-a-post-transformer-architecture-01kt40mmp6jfk5e6rygkxsxh9d
category: source
source_id: the-sequence-knowledge-870-liquid-models-and-the-search-for-a-post-transformer-architecture-01kt40mmp6jfk5e6rygkxsxh9d
author: Jesus Rodriguez
publication: substack.com
published_date: '2026-06-02'
assessed_as_of: '2026-06-02'
ingested_at: '2026-06-09T15:38:30.047511+00:00'
canonical_url: https://thesequence.substack.com/p/the-sequence-knowledge-870-liquid
content_sha256: 971787a74c5e395e8238db2c976b75019cb7859e2a75b1d9824a0a254681d32a
---

# The Sequence Knowledge #870: Liquid Models and the Search for a Post-Transformer Architecture

This piece is about why people are looking beyond transformers. Transformers are powerful because every token can look at every other token, but that makes memory and serving costs rise as context grows. The article says this is fine for cloud-scale models, but less attractive for always-on, low-latency, private, or on-device systems. It introduces liquid models as one possible post-transformer idea, without fully explaining how they work in the visible excerpt. The core message is simple: if a model has to run for a long time and remember a lot, attention may be too expensive. So the article asks whether sequence models based on dynamics instead of global attention could be a better fit.

## Key insights

- The article treats transformer cost as an inference-time memory problem, not just a training problem.
- It connects architecture choice to deployment setting: cloud-scale systems and always-on/on-device systems face different constraints.
- The visible excerpt makes liquid models a framing device for post-transformer research, not a demonstrated solution.
- The key practical pressure point is key-value cache growth as context length increases.
- The article’s strongest claim is conceptual: architectural physics can limit what is efficient to serve, even if the model is strong in principle.

## Derived knowledge pages

No derived knowledge pages captured.

## Why it matters

The piece is useful as a concise reminder that transformer dominance does not erase serving-time constraints. It highlights one of the most durable engineering tensions in sequence modeling: global attention is expressive, but explicit memory grows with context. That matters for practitioners who care about latency, memory footprint, and long-running interactions, because those constraints often decide whether a model is practical even when quality is acceptable. The article also helps separate architectural evaluation from benchmark hype: it is asking whether a different computation model may fit certain deployment regimes better, rather than claiming transformers are obsolete. At the same time, the excerpt is thin on evidence, so its significance is limited to framing rather than decision-making. As of 2026-06-02, this is best read as an early-stage architectural prompt to monitor rather than something to adopt based on the text alone.

## Limitations / open questions

The visible excerpt does not explain what liquid models are mechanically, how they are trained, or how they compare on benchmarks against transformers. It gives no empirical results, ablations, latency measurements, memory profiles, or deployment case studies. The argument assumes that growing key-value caches are a decisive limitation, but does not quantify where that becomes prohibitive in practice. It also leaves open whether dynamic sequence processing can match transformer quality, stability, or tooling ecosystem maturity.

## Contradictions / unverified claims

The piece is directionally plausible but mostly speculative in the excerpt shown. It presents transformer limitations in serving as a reason to seek alternatives, but does not show that the proposed alternative solves those constraints better. The claim that transformers are less suitable for always-on, low-latency, private, embodied, or on-device intelligence is plausible, yet unproven here because no measurements or comparative demonstrations are provided. The excerpt also risks over-weighting architectural elegance relative to optimization, compression, and systems-level fixes that can reduce transformer cost without changing the architecture.

## Source metadata

- Canonical URL: https://thesequence.substack.com/p/the-sequence-knowledge-870-liquid
- Raw markdown: `raw/readwise/the-sequence-knowledge-870-liquid-models-and-the-search-for-a-post-transformer-architecture-01kt40mmp6jfk5e6rygkxsxh9d.md`
- Raw HTML: `raw/readwise/the-sequence-knowledge-870-liquid-models-and-the-search-for-a-post-transformer-architecture-01kt40mmp6jfk5e6rygkxsxh9d.html`
