---
title: Where the goblins came from
slug: where-the-goblins-came-from-01kqe6j1dkvzgyjehhqca53e60
category: source
tags:
- ai-engineering
- ai-evaluation
- ai-operationalization
- behavioral-evaluation
- reward-modeling
source_id: where-the-goblins-came-from-01kqe6j1dkvzgyjehhqca53e60
author: OpenAI Blog
publication: OpenAI
published_date: '2026-04-29'
assessed_as_of: '2026-04-29'
ingested_at: '2026-05-22T14:56:40.105532+00:00'
canonical_url: https://openai.com/index/where-the-goblins-came-from
content_sha256: 453a98c143ed5e8a4beede70eaae9c12debd60d838c511af65f6e7dad85e00cc
derived_topics:
- topics/behavioral-audits-for-model-style-drift.md
- topics/reward-generalization-effects.md
derived_trends:
- industry-trends/behavioral-regressions-need-qualitative-audits.md
derived_pages:
- industry-trends/behavioral-regressions-need-qualitative-audits.md
- topics/behavioral-audits-for-model-style-drift.md
- topics/reward-generalization-effects.md
---

# Where the goblins came from

This article is about a strange habit that showed up in some OpenAI models: they started talking about goblins, gremlins, and similar creatures more and more often. At first it looked like a harmless quirk, but over time it became hard to ignore. OpenAI says the cause was not a single bug, but a reward signal used to shape a playful personality style called Nerdy. That reward seems to have taught the model to like creature metaphors, and the habit then spread into other training stages. The company says it fixed the issue by removing that reward signal and filtering some training data. It also added a prompt-based mitigation for Codex. The main message is that models can learn small style habits in one setting and then carry them into others. As of April 2026, the story is a useful reminder to watch for odd behavior patterns and trace them back to training incentives.

## Key insights

- A style reward aimed at one personality can leak into broader model behavior.
- Lexical quirks may not show up as obvious benchmark failures and can require targeted behavioral audits.
- Rewarded outputs can re-enter supervised fine-tuning data and reinforce the same habit.
- Mitigation can combine training-data cleanup with prompt-level guardrails for downstream tools.
- Small, amusing artifacts can become operationally relevant when they affect conversation quality or tool behavior.

## Derived knowledge pages

- [[industry-trends/behavioral-regressions-need-qualitative-audits]]
- [[topics/behavioral-audits-for-model-style-drift]]
- [[topics/reward-generalization-effects]]

## Why it matters

The article is useful because it shows a concrete failure mode in alignment and persona training: a reward intended for one style can amplify a specific lexical habit and then spread it through later training stages. That is operationally important for anyone tuning assistants, because it suggests that style rewards are not isolated preferences; they can become latent behavioral attractors. The article also shows why ordinary evals may miss these issues: the problem was subtle, cumulative, and first noticed through user and employee reports rather than a single bad metric. For teams building conversational systems, this is a reminder to inspect qualitative output patterns, not just headline scores, when changing persona prompts or reward models. The useful part is fairly specific to reward design and training-data feedback loops, so the article is more of a tactical debugging case than a broad theory paper. As of 2026-04-29, it is actionable as a cautionary example and as evidence that fast behavioral auditing tools are worth investing in. For support automation and other service systems, the practical lesson is that persona tuning can create odd phrasing habits that leak into customer-facing outputs, so prompt-layer mitigations and training-data filters matter when conversational consistency is a product requirement.

## Limitations / open questions

The explanation is plausible and internally consistent, but it is still a single vendor account of a specific incident. The article gives useful percentages and internal observations, but it does not provide a full experimental design or independent replication of the causal chain from reward signal to downstream spread. It also leaves open how general this failure mode is across other persona styles, other training pipelines, or other model families. The mitigation described is partly prompt-based for Codex, which may reduce symptoms without proving the underlying behavior is fully eliminated across all surfaces.

## Contradictions / unverified claims

The article presents a neat root-cause story, but the behavior emerged through a chain of training stages, so causality may be messier than the narrative suggests. The reported percentages are compelling, yet they are still internal measurements from one system and should not be treated as universal evidence. The fact that a prompt-level instruction was used for Codex also suggests that some surface behavior management may still be needed even after training fixes.

## Source metadata

- Canonical URL: https://openai.com/index/where-the-goblins-came-from
- Raw markdown: `raw/readwise/where-the-goblins-came-from-01kqe6j1dkvzgyjehhqca53e60.md`
- Raw HTML: `raw/readwise/where-the-goblins-came-from-01kqe6j1dkvzgyjehhqca53e60.html`
