---
title: '[AINews] New AI Infra unicorns: Exa, Modal, TurboPuffer'
slug: ainews-new-ai-infra-unicorns-exa-modal-turbopuffer-01ks73y0nn4rm1x8q4g5ek30y7
category: source
tags:
- continuous-evaluation
- execution-oriented-agents
- orchestration-layer-growth
- persistent-agents
- runtime-systems
- tool-centric-agents
- workflow-based-evaluation
source_id: ainews-new-ai-infra-unicorns-exa-modal-turbopuffer-01ks73y0nn4rm1x8q4g5ek30y7
author: AINews
publication: Substack
published_date: '2026-05-22'
assessed_as_of: '2026-05-22'
ingested_at: '2026-06-09T16:50:04.930969+00:00'
canonical_url: mailto:reader-forwarded-email/564e1345c8c55bc25641782459460c13
content_sha256: 93598e5ac5b8ee23a77ae504dc2791a4e78bd6143f8c4109ae68abb014f5aacf
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
derived_signals:
- signals/2026-05/ainews-new-ai-infra-unicorns-exa-modal-turbopuffer-01ks73y0nn4rm1x8q4g5ek30y7-agent-products-are-moving-from-chat-surfaces-to-persistent-cross-device-operators.md
- signals/2026-05/ainews-new-ai-infra-unicorns-exa-modal-turbopuffer-01ks73y0nn4rm1x8q4g5ek30y7-harness-design-remains-a-first-order-source-of-agent-gains.md
derived_trends:
- industry-trends/agent-tooling-shifts-from-prompting-to-workflow-architecture.md
derived_pages:
- industry-trends/agent-tooling-shifts-from-prompting-to-workflow-architecture.md
- signals/2026-05/ainews-new-ai-infra-unicorns-exa-modal-turbopuffer-01ks73y0nn4rm1x8q4g5ek30y7-agent-products-are-moving-from-chat-surfaces-to-persistent-cross-device-operators.md
- signals/2026-05/ainews-new-ai-infra-unicorns-exa-modal-turbopuffer-01ks73y0nn4rm1x8q4g5ek30y7-harness-design-remains-a-first-order-source-of-agent-gains.md
---

# [AINews] New AI Infra unicorns: Exa, Modal, TurboPuffer

This issue is a digest of AI news from May 20-21, 2026. The main theme is that practical AI progress is happening in infrastructure and agent tooling, not just in flashy model releases. It points to companies like Turbopuffer, Modal, and Exa raising or hitting major milestones, while also showing how harnesses, retrieval, and sandboxing can unlock more useful agent behavior. It also includes a few research results that matter because they change how people think about tokenization, data filtering, and interpretability. In plain English: the article says the stack around the model is getting more important, and some of the strongest signals are coming from products that make AI systems easier to run, control, and compose.

## Key insights

- Harnesses and scaffolding are still producing large capability gains, but the effect is model-specific rather than universal.
- The strongest infra stories in this roundup are search/retrieval and agent-serving layers, not base-model releases.
- Codex’s Mac app control and Appshots are evidence that agent products are extending beyond chat into persistent cross-device workflows.
- The roundup treats interpretability more cautiously: isolated sparse features may be less useful than grouped features with shared firing patterns.
- Several items suggest compute and data efficiency remain active bottlenecks, but the evidence is mixed and often benchmark-dependent.

## Derived knowledge pages

- [[industry-trends/agent-tooling-shifts-from-prompting-to-workflow-architecture]]
- [[signals/2026-05/ainews-new-ai-infra-unicorns-exa-modal-turbopuffer-01ks73y0nn4rm1x8q4g5ek30y7-agent-products-are-moving-from-chat-surfaces-to-persistent-cross-device-operators]]
- [[signals/2026-05/ainews-new-ai-infra-unicorns-exa-modal-turbopuffer-01ks73y0nn4rm1x8q4g5ek30y7-harness-design-remains-a-first-order-source-of-agent-gains]]

## Why it matters

This roundup is useful because it compresses several durable signals about where AI engineering effort is concentrating as of 2026-05-22. The Turbopuffer, Modal, and Exa notes show that investor attention is still rewarding companies that sit in the retrieval, compute, and AI cloud layers rather than only at the frontier-model layer. The agent section is especially operational: physics-intern, mini-swe-agent, Codex’s cross-device Mac control, Gemini’s single-call workflows, and LangChain’s sandbox and streaming additions all describe concrete machinery for making agents more reliable and composable. Weaviate’s built-in MCP server and vLLM’s elastic expert parallelism are the kind of systems details that matter to teams building production stacks, because they reduce friction around retrieval, serving, and topology changes. The research items are mixed in strength, but they are still useful as directional evidence: RAEv2, Gated DeltaNet-2, and the data-filtering result all point to unresolved questions about representation, attention, and data curation. The interpretability discussion around feature groups is also a practical correction to oversimplified sparse-autoencoder narratives. The multimodal, biology, geospatial, and robotics items are more product-specific, but they show that applied model work is moving into narrower domains with clearer tooling and evaluation. As of 2026-05-22, the actionable reading is to monitor the infra and agent primitives closely and treat the more speculative research and benchmark claims as interesting but not yet universally settled.

## Limitations / open questions

Many of the most striking claims are compressed into social posts or product announcements, so the underlying methods, baselines, and failure modes are not fully visible here. The “no filter” data-curation result depends on scale assumptions and noisy downstream evaluations, so it is not a general license to stop filtering data. The harness results appear model-specific, which leaves open how transferable the gains are across models and tasks. The interpretability discussion about feature groups is plausible but still needs stronger empirical validation beyond thread-level argumentation. Several product items, including Codex remote app use and Hark’s long autonomous run, lack enough technical detail in this roundup to judge reliability, cost, security, or reproducibility. The article also mixes hard numbers, anecdotal reports, and promotional launches, so it should be read as a signal sampler rather than a settled benchmark report.

## Contradictions / unverified claims

The roundup repeatedly highlights impressive numbers, but some of them come from company claims or high-engagement posts rather than independent evaluations. The OpenAI math-result discussion shows how quickly benchmark-like claims invite skepticism about gameability and what counts as a legitimate AI contribution. The harness story is also a cautionary example: Gemini 3.1 Pro improved sharply in one setup, while GPT 5.5 Pro did not, which suggests these gains may depend on model-harness fit rather than general scaffold magic. The “best filter may be no filter” result is provocative, but the source itself notes noisy evaluations and an extreme compute crossover point, so it should not be overstated as a near-term default. In general, the roundup is strongest when describing concrete product capabilities and weakest when extrapolating from a single result into a broader principle.

## Source metadata

- Canonical URL: mailto:reader-forwarded-email/564e1345c8c55bc25641782459460c13
- Raw markdown: `raw/readwise/ainews-new-ai-infra-unicorns-exa-modal-turbopuffer-01ks73y0nn4rm1x8q4g5ek30y7.md`
- Raw HTML: `raw/readwise/ainews-new-ai-infra-unicorns-exa-modal-turbopuffer-01ks73y0nn4rm1x8q4g5ek30y7.html`

## Full source text

---
readwise_id: "01ks73y0nn4rm1x8q4g5ek30y7"
title: "[AINews] New AI Infra unicorns: Exa, Modal, TurboPuffer"
author: "AINews"
publication: "Substack"
source_url: "mailto:reader-forwarded-email/564e1345c8c55bc25641782459460c13"
category: "email"
location: "archive"
published_date: "2026-05-22"
saved_at: "2026-05-22T05:53:32.853000+00:00"
updated_at: "2026-05-25T09:55:45.436412+00:00"
tags: ["processed"]
---

Three AI infrastructure companies, Turbopuffer, Exa, and Modal, have raised large funds and reached high valuations. New research advances include faster AI training methods and better coding tools. The AI compute market is growing fast, with big investments in hardware and cloud services.
