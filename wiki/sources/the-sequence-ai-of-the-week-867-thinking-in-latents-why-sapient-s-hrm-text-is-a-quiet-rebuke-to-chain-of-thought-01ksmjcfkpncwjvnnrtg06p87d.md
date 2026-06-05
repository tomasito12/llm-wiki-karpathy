---
title: 'The Sequence AI of the Week #867: Thinking in Latents: Why Sapient''s HRM-Text
  Is a Quiet Rebuke to Chain-of-Thought'
slug: the-sequence-ai-of-the-week-867-thinking-in-latents-why-sapient-s-hrm-text-is-a-quiet-rebuke-to-chain-of-thought-01ksmjcfkpncwjvnnrtg06p87d
category: source
tags:
- ai-engineering
- ai-research
- inference-systems
- model-behavior
- runtime-architecture
- runtime-systems
source_id: the-sequence-ai-of-the-week-867-thinking-in-latents-why-sapient-s-hrm-text-is-a-quiet-rebuke-to-chain-of-thought-01ksmjcfkpncwjvnnrtg06p87d
author: Jesus Rodriguez
publication: substack.com
published_date: '2026-05-27'
assessed_as_of: '2026-05-27'
ingested_at: '2026-06-05T19:36:07.115124+00:00'
canonical_url: https://thesequence.substack.com/p/the-sequence-ai-of-the-week-867-thinking
content_sha256: b0e6fed2589ee75913eaf52480e49888333dde90a53853a7542c81267b441fa8
derived_topics:
- chain-of-thought-as-externalized-depth
- latent-reasoning-architectures
derived_trends:
- latent-reasoning-replaces-token-chain-of-thought
---

# The Sequence AI of the Week #867: Thinking in Latents: Why Sapient's HRM-Text Is a Quiet Rebuke to Chain-of-Thought

This piece is about a simple but important question: should language models “think out loud” step by step, or should they do more of the reasoning inside their hidden activations? The author says chain-of-thought is a clumsy workaround because the model has to turn intermediate reasoning into words and then read those words back in. Sapient’s HRM-Text is presented as a model that tries a different path: internal, variable-depth computation in latent space. That makes the article interesting because it challenges a common habit in LLM design. But the excerpt is more of an argument than a proof. As of 2026-05-27, it is best read as a promising architectural critique worth monitoring, not a settled answer.

## Key insights

- Chain-of-thought is described as externalized depth, not true internal reasoning.
- The article’s core proposal is variable internal depth in latent space, not larger scale or more CoT data.
- The critique is architectural: sequential computation should happen inside the model, not through tokenized self-talk.
- HRM-Text is framed as extending an earlier Hierarchical Reasoning Model into language.
- The excerpt does not establish the claim with benchmarks, so the idea is conceptually interesting but evidentially thin.

## Derived knowledge pages

- [[industry-trends/latent-reasoning-replaces-token-chain-of-thought]]
- [[topics/chain-of-thought-as-externalized-depth]]
- [[topics/latent-reasoning-architectures]]

## Why it matters

The piece matters because it targets a common assumption in LLM engineering: that better reasoning is mainly a matter of prompting models to narrate more steps. The author argues that chain-of-thought is a workaround for a deeper architectural limitation, since intermediate steps must be emitted as tokens and then re-ingested, which is a fragile way to do internal computation. That makes HRM-Text interesting as a design direction: it tries to move reasoning back into latent space and give the model variable internal depth. If that mechanism works, it would be a more structural answer than simply collecting more reasoning traces or scaling the model. But the excerpt is careful enough to say this is not yet proven; it is a claim and a direction, not a demonstrated replacement. For practitioners, the useful takeaway is to separate “better verbalized reasoning” from “better internal reasoning” when evaluating model architectures. As of 2026-05-27, the idea is worth monitoring for architectural lessons, but the evidence in this excerpt is too thin to treat it as settled.

## Limitations / open questions

The excerpt gives no benchmark numbers, task suite, or failure analysis for HRM-Text, so it is unclear how much latent reasoning helps in practice. It also does not explain the compute cost, training complexity, or latency impact of variable internal depth. The article does not show whether latent reasoning generalizes beyond the specific model family discussed or whether it is easier to train than chain-of-thought supervision. It is also open whether the approach improves reliability, interpretability, or only changes where the computation is represented. Security, controllability, and debugging implications are not addressed.

## Contradictions / unverified claims

The argument strongly contrasts internal reasoning with chain-of-thought, but the excerpt itself does not show that token-based reasoning is ineffective in the tasks that matter. The “renting depth” framing is rhetorically sharp, but it risks overstating how much of current reasoning performance depends on explicit verbal traces. It is also possible that latent computation is harder to inspect or verify, which would trade one limitation for another. Without concrete results, the claim reads as a plausible architectural critique rather than evidence that CoT should be abandoned.

## Source metadata

- Canonical URL: https://thesequence.substack.com/p/the-sequence-ai-of-the-week-867-thinking
- Raw markdown: `raw/readwise/the-sequence-ai-of-the-week-867-thinking-in-latents-why-sapient-s-hrm-text-is-a-quiet-rebuke-to-chain-of-thought-01ksmjcfkpncwjvnnrtg06p87d.md`
- Raw HTML: `raw/readwise/the-sequence-ai-of-the-week-867-thinking-in-latents-why-sapient-s-hrm-text-is-a-quiet-rebuke-to-chain-of-thought-01ksmjcfkpncwjvnnrtg06p87d.html`
