---
title: Introducing Composer 2
slug: introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1
category: source
tags:
- agent-evals
- agent-orchestration
- agent-systems
- agentic
- ai-evaluation
- coding
- coding-agents
- coding-model
- developer-focused
- frontier-ai
- ide-integrated
- proprietary-model
- software-development
- software-engineering
- test-and-verification
- tool-use-capable
source_id: introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1
author: Cursor Blog
publication: Cursor
published_date: '2026-03-19'
assessed_as_of: '2026-03-19'
ingested_at: '2026-06-05T16:19:33.221079+00:00'
canonical_url: https://cursor.com/blog/composer-2
content_sha256: ddfa2acf0c1b63d7cd5141bdb821d8cfd2cc0ab0fd118c61042cdcd78dd61f53
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
derived_models:
- foundation-models/composer-2.md
derived_tools:
- tools/cursor.md
derived_topics:
- topics/agentic-coding-workflows.md
- topics/model-evaluation-with-terminal-benchmarks.md
derived_trends:
- industry-trends/coding-models-shift-toward-agentic-execution.md
derived_pages:
- foundation-models/composer-2.md
- industry-trends/coding-models-shift-toward-agentic-execution.md
- tools/cursor.md
- topics/agentic-coding-workflows.md
- topics/model-evaluation-with-terminal-benchmarks.md
---

# Introducing Composer 2

This article announces Composer 2, a coding model built into Cursor. Cursor says it is strong enough for frontier-level coding work and cheaper than many premium models. The main pitch is that the model is both capable and cost-efficient, not just one or the other. Cursor also says the model was improved through continued pretraining and then reinforcement learning on long coding tasks. The benchmarks suggest it can handle agent-like work that takes many steps. As of 2026-03-19, this is interesting mainly as a product and pricing update from the vendor, with the usual need to treat the benchmark claims cautiously.

## Key insights

- Composer 2 is framed as a cost-performance play: frontier-level coding quality at $0.50/M input and $2.50/M output tokens.
- Cursor attributes the gains to continued pretraining followed by reinforcement learning on long-horizon coding tasks.
- The benchmark table shows large jumps over Composer 1 and 1.5 across CursorBench, Terminal-Bench 2.0, and SWE-bench Multilingual.
- Cursor explicitly claims the model can handle tasks requiring hundreds of actions, which matters for agentic coding workflows.
- A faster variant keeps the same intelligence but changes the price tier, so deployment choices can trade speed for cost rather than capability.

## Derived knowledge pages

- [[foundation-models/composer-2]]
- [[industry-trends/coding-models-shift-toward-agentic-execution]]
- [[tools/cursor]]
- [[topics/agentic-coding-workflows]]
- [[topics/model-evaluation-with-terminal-benchmarks]]

## Why it matters

The article matters because it is a concrete vendor example of a coding model being optimized around both benchmark quality and serving price, not just one or the other. Cursor is not only publishing a headline score; it provides comparative results against its own earlier models across three benchmarks, which makes the product claim easier to inspect than a pure marketing announcement. The most durable takeaway is the combination of continued pretraining and reinforcement learning on long-horizon coding tasks as the stated path to better agentic performance. That is operationally relevant for teams evaluating models for multi-step coding agents, where long action sequences and terminal interaction matter more than short completions. The pricing split between the standard and fast variants also gives a practical procurement knob: teams can choose speed or lower cost without changing the underlying model family. The usage-pool note suggests Cursor is packaging the model into its product economics as much as into its model roadmap. The evidence is still vendor-controlled, so the significance is meaningful but bounded by the absence of independent replication. As of 2026-03-19, this is actionable as a product/data point to test, not a standalone proof that the broader model class has solved frontier coding.

## Limitations / open questions

All performance claims come from Cursor’s own benchmark reporting, so independent verification is missing. The post does not explain benchmark task composition, failure modes, or whether gains generalize beyond the listed evaluations. It says continued pretraining and reinforcement learning drove improvements, but gives no training-data details, compute scale, or safety constraints. The pricing discussion does not quantify end-to-end cost under real workloads, where retries, tool calls, and long context can dominate. The “hundreds of actions” claim is suggestive, but the article does not show example tasks or success rates on long trajectories. The faster variant is presented as equally intelligent, but the basis for that equivalence is only Cursor’s statement and benchmarks in the post.

## Contradictions / unverified claims

The piece is strong on benchmark-driven persuasion and light on independent validation, so skepticism is warranted. “Frontier-level” is a marketing label unless mapped to a broader, externally comparable eval suite, which this post does not provide. The claim that the fast variant has the same intelligence is plausible within Cursor’s framing, but the article does not show enough detail to rule out workload-dependent regressions. Benchmark gains may overstate real-world coding usefulness if the target tasks differ from users’ actual repos and tooling. The article does not substantiate any broader market or industry conclusion, only a product-specific release.

## Source metadata

- Canonical URL: https://cursor.com/blog/composer-2
- Raw markdown: `raw/readwise/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1.md`
- Raw HTML: `raw/readwise/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1.html`

## Full source text

---
readwise_id: 01kr1qhvfpdcttev7248ae0ba1
title: Introducing Composer 2
author: Cursor Blog
source_url: https://cursor.com/blog/composer-2
category: rss
location: archive
published_date: '2026-03-19'
saved_at: '2026-05-07T17:25:05.430000+00:00'
updated_at: '2026-05-08T09:54:22.374449+00:00'
tags:
- processed
publication: Cursor
---

Composer 2 is a new, powerful coding model available on Cursor with improved quality and efficiency. It costs $0.50 per million input tokens and $2.50 per million output tokens, with a faster, slightly more expensive option also offered. Composer 2 performs very well on coding benchmarks and can handle complex tasks requiring many steps.
