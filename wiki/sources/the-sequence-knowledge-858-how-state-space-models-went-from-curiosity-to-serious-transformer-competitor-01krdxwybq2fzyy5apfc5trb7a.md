---
title: 'The Sequence Knowledge #858: How State Space Models Went from Curiosity to
  Serious Transformer Competitor'
slug: the-sequence-knowledge-858-how-state-space-models-went-from-curiosity-to-serious-transformer-competitor-01krdxwybq2fzyy5apfc5trb7a
category: source
source_id: the-sequence-knowledge-858-how-state-space-models-went-from-curiosity-to-serious-transformer-competitor-01krdxwybq2fzyy5apfc5trb7a
author: Jesus Rodriguez
publication: substack.com
published_date: '2026-05-12'
assessed_as_of: '2026-05-12'
ingested_at: '2026-06-09T15:47:29.733849+00:00'
canonical_url: https://thesequence.substack.com/p/the-sequence-knowledge-858-how-state
content_sha256: be960849f02eb9bf7d6a63b902a27374e6da9f671d7bb2b82916af2c6d81d022
---

# The Sequence Knowledge #858: How State Space Models Went from Curiosity to Serious Transformer Competitor

This article is about a newer neural network family called state space models and why people are taking them seriously as transformer alternatives. The basic appeal is simple: transformers get expensive because attention grows with sequence length, while state space models are described as linear-time and constant-memory at inference. That makes them interesting for very long contexts and for large models where the cache uses a lot of memory. The piece says the big question has been whether they can match transformers on important language tasks. As of March 2026, it claims they are increasingly able to do that, but the excerpt does not yet show the data behind the claim.

## Key insights

- The core engineering tradeoff is sequence scaling: quadratic attention versus linear-time state space processing.
- The article emphasizes inference memory, not just training cost, as a practical limit for large transformer deployments.
- Eliminating the key-value cache is presented as a major operational advantage of state space models.
- The relevant benchmark bar is not abstract elegance but parity on perplexity, in-context learning, and reasoning.
- The excerpt is framing-level only; it asserts progress as of March 2026 without showing the underlying evidence.

## Derived knowledge pages

No derived knowledge pages captured.

## Why it matters

The piece is useful because it isolates a concrete bottleneck in transformer systems: self-attention scales as sequence length squared, and the author connects that directly to long-context workloads and VRAM pressure during inference. That makes the comparison operational rather than purely theoretical. It also usefully names the evaluation bar for any serious alternative: language modeling perplexity, in-context learning, and reasoning, not just speed claims. For practitioners, the durable takeaway is that architecture choice is increasingly tied to memory behavior and long-sequence economics, not only model quality. The article is still high-level, so its practical value as of 2026-05-12 is mainly as a framing note and a prompt to inspect benchmarks, not as a standalone adoption guide. There is no substantive discussion of customer support, voice, meetings, or back-office workflows in the provided text, so no direct service-automation implication can be drawn here.

## Limitations / open questions

The excerpt does not include the mathematical details, architectural variants, benchmark tables, or experimental setup needed to evaluate the claim that state space models increasingly match transformers. It also does not specify which tasks, datasets, model sizes, or latency/memory regimes were used. The statement about 70B models and 40GB of VRAM illustrates a bottleneck but is not accompanied by a methodology or measurement context in the provided text. Open questions include whether the stated advantages hold across all deployment settings, how state space models behave at scale, and what tradeoffs they introduce in accuracy, tooling, or training complexity.

## Contradictions / unverified claims

The text makes a strong performance-comparison claim — that state space models are increasingly matching transformers — but the excerpt provides no evidence beyond assertion. It also compresses a complicated architectural landscape into a simple transformer-versus-state-space contrast, which may hide important hybrids or task-specific exceptions. The quoted memory and sequence-scaling concerns are plausible, but the passage does not establish that they are the dominant constraints in every production setting. Skepticism is warranted until the promised mathematical foundation and empirical support are shown.

## Source metadata

- Canonical URL: https://thesequence.substack.com/p/the-sequence-knowledge-858-how-state
- Raw markdown: `raw/readwise/the-sequence-knowledge-858-how-state-space-models-went-from-curiosity-to-serious-transformer-competitor-01krdxwybq2fzyy5apfc5trb7a.md`
- Raw HTML: `raw/readwise/the-sequence-knowledge-858-how-state-space-models-went-from-curiosity-to-serious-transformer-competitor-01krdxwybq2fzyy5apfc5trb7a.html`
