---
title: Composer 2
slug: composer-2
entity_id: model:composer-2
category: foundation-model
tags:
- coding-model
- developer-focused
- proprietary-model
- tool-use-capable
first_seen: '2026-03-19'
last_seen: '2026-03-25'
source_count: 2
evidence_count: 24
source_ids:
- introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1
- run-cloud-agents-in-your-own-infrastructure-01kr1qhvaw58dz13633c041cmy
value_level: high
confidence: 0.795
synthesis_state: synthesized
synthesis_stale: false
synthesis_input_hash: f3a8e831d1f85d98
current_input_hash: f3a8e831d1f85d98
synthesis_schema_version: 1
synthesis_prompt_version: 1
last_synthesized_at: '2026-07-09T19:16:40Z'
types:
- coding-model
- frontier-model
- proprietary-model
---

# Composer 2

## Executive synthesis

Composer 2 is Cursor’s coding model for agentic software work, not a general-purpose chat model. The sources consistently frame it as useful for long-horizon coding tasks that may require many actions, especially when paired with tool use, terminal interaction, repo access, and verification loops. Cursor also offers a faster variant, so the practical choice is not just model quality but the balance between latency, token cost, and workflow throughput. The main caveat is evidence quality: the strongest claims come from Cursor’s own benchmark-oriented marketing, so the model looks productized and worth testing, but not independently validated here. It is most relevant when your question is whether a coding agent can sustain multi-step work inside an execution harness, including self-hosted infrastructure.

## Practical relevance

### Worth testing for long-running coding agents

Composer 2 appears relevant when you are building or evaluating a coding agent that must make many tool calls, run tests, and work inside a repo over a long task. Cursor positions it for this kind of multi-step software work and says it can be used in custom agent harnesses, including self-hosted execution. The evidence is thinner on how well it fails, how it compares outside Cursor’s own setup, and whether the fast variant is the right default. So this is a page to consult when deciding whether Composer 2 belongs in the shortlist for agentic coding, not when you need a trusted independent benchmark verdict.

- Why this matters: It turns the abstract claim of “frontier-level coding” into a concrete deployment question: can this model support a multi-step coding loop with tools, tests, and infrastructure constraints?

- Basis: `source-grounded`

## Context card

- **Use this page when:** Use this page when you need a quick read on whether Composer 2 is worth testing for coding agents, especially long-running tool-using workflows, and you want the main constraints, pricing tradeoff, and evidence caveats in one place.
- **Best for questions about:** What Composer 2 is used for in coding-agent workflows, Whether Composer 2 looks suitable for long multi-step software tasks, How Cursor positions Composer 2 relative to its earlier models, What the pricing/fast-variant tradeoff implies for agent workloads, Whether Composer 2 can fit into self-hosted or custom agent harnesses
- **Not enough for:** Independent quality claims beyond Cursor’s own evaluation, Failure modes or regressions in real-world coding work, Detailed pricing-inference or end-to-end deployment cost estimates, Comparisons against non-Cursor frontier models, Use in general chat, support bots, or other non-coding automation
- **Strongest sources:** Introducing Composer 2, Run cloud agents in your own infrastructure
- **Related tags:** coding-model, developer-focused, proprietary-model, tool-use-capable

## What to remember

- Composer 2 is a Cursor coding model aimed at long-horizon, multi-step software work.
- It is meant to work inside agent loops with tools, tests, repo access, and verification.
- Cursor offers a standard and a faster variant, so cost and latency are part of the decision.
- The sources say it outperforms Composer 1 and 1.5 on the benchmarks shown, but those claims are vendor-led.
- The self-hosted agent article shows Composer 2 can be one option in customer-run infrastructure, but it does not prove relative quality there.
- Evidence is good for understanding product positioning and deployment shape, weak for independent reliability or comparative performance beyond Cursor’s own framing.

## Consensus

- Composer 2 is Cursor’s coding-focused model, positioned for demanding software work and long-horizon agentic tasks.
- The sources present it as usable inside agent-style workflows, including self-hosted or custom-built agent harnesses with tool use and verification loops.
- Cursor provides a standard and a faster variant, making deployment partly a tradeoff between throughput/cost and the claimed intelligence level.
- The vendor source reports benchmark improvements over Composer 1 and 1.5, but the evidence is still vendor-led rather than independently established.

## Tensions / open questions

- Cursor reports strong benchmark gains and frontier-level positioning, but the evidence is vendor-controlled and not independently validated.
- The fast variant is described as retaining the same intelligence claim while changing cost, but the sources do not show workload-specific tradeoffs or failure cases.
- The self-hosted agent source implies operational flexibility, yet it provides no Composer 2-specific performance, pricing, or adoption evidence.
- The model is clearly positioned for coding agents, but the sources do not justify extending that confidence to customer-facing automation or general chat use.

## Evidence quality

- Evidence is narrow: only 2 sources and 24 reviewed evidence items, both vendor-authored Cursor articles.
- Benchmarks and quality claims are reported by the vendor; the sources do not establish independent real-world reliability.
- The self-hosted agent source is operationally useful, but it gives almost no performance or failure data for Composer 2 specifically.
- Pricing is explicit in one source, but total cost depends on the surrounding agent harness and customer-run infrastructure.

## Practical takeaway

Treat Composer 2 as a Cursor-native coding model that is most interesting for long-horizon agent workflows; test it for fit in a real agent harness, but do not rely on the vendor benchmarks alone to decide production use.

## Evidence index

- Sources: 2
- Evidence items: 24
- Current input hash: `f3a8e831d1f85d98`
- Cached input hash: `f3a8e831d1f85d98`
- Last synthesized: 2026-07-09T19:16:40Z
- Synthesis status: `fresh`

## Related pages

No related pages captured.

## Sources

- [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]]
- [[sources/run-cloud-agents-in-your-own-infrastructure-01kr1qhvaw58dz13633c041cmy|Run cloud agents in your own infrastructure]]
