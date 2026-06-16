---
title: 'Ready for your busiest day: How we scale'
slug: ready-for-your-busiest-day-how-we-scale-01ks0e1b38y1emnqkewpcvbhzb
category: source
tags:
- agent-systems
- ai-operationalization
- enterprise-ai
- enterprise-workflows
- infrastructure
- runtime-systems
- software-engineering
- support-automation
source_id: ready-for-your-busiest-day-how-we-scale-01ks0e1b38y1emnqkewpcvbhzb
author: Ryan Sherlock
publication: The Intercom Blog
published_date: '2026-05-19'
assessed_as_of: '2026-05-19'
ingested_at: '2026-06-06T22:05:07+00:00'
canonical_url: https://www.intercom.com/blog/ready-for-your-busiest-day-how-we-scale/
content_sha256: c6470ba336339401880db68dbc794957bcaf2923502a07f57e052ff6ec0d773e
derived_implementation_studies:
- implementation-studies/2026-05/ready-for-your-busiest-day-how-we-scale-01ks0e1b38y1emnqkewpcvbhzb-fin-platform-scaling-and-reliability-architecture.md
derived_topics:
- topics/customer-isolation-and-tenant-fairness.md
- topics/incremental-and-reversible-infrastructure-changes.md
derived_trends:
- industry-trends/ai-products-shift-from-models-to-systems.md
derived_pages:
- implementation-studies/2026-05/ready-for-your-busiest-day-how-we-scale-01ks0e1b38y1emnqkewpcvbhzb-fin-platform-scaling-and-reliability-architecture.md
- industry-trends/ai-products-shift-from-models-to-systems.md
- topics/customer-isolation-and-tenant-fairness.md
- topics/incremental-and-reversible-infrastructure-changes.md
---

# Ready for your busiest day: How we scale

This is a behind-the-scenes look at how Intercom says it keeps its platform stable under heavy load. The main idea is simple: scale is not just about bigger numbers, but about knowing where the real pressure points are and designing systems so they can grow without risky rewrites. The article walks through the company’s database, search, queueing, and AI routing setup, and shows how it tries to make changes safer and more reversible. It also emphasizes that one customer’s spike should not slow everyone else down. For Fin, the AI agent, the team says it uses multiple model providers and failover paths so support traffic can keep flowing during bursts. The practical message is that boring infrastructure, careful isolation, and small changes can be more valuable than flashy scale claims.

## Key insights

- The article treats scale as a set of explicit levers and limits, not a marketing number; that framing is operationally reusable for any critical SaaS system.
- Moving the source-of-truth database to Vitess/PlanetScale is presented as a way to buy practical options: sharding, online schema changes, isolated customer capacity, and fewer customer-impacting maintenance windows.
- Search migrations are handled with a reversible playbook: partitioning, dual writes, backfills, validation, feature-flagged cutovers, and delayed deletion of the old index.
- Tenant fairness is enforced at multiple layers so one customer’s burst does not become shared latency for everyone else.
- Fin’s AI layer is operated like core infrastructure, with multi-provider routing, failover, and buffer capacity rather than a single upstream dependency.

## Derived knowledge pages

- [[implementation-studies/2026-05/ready-for-your-busiest-day-how-we-scale-01ks0e1b38y1emnqkewpcvbhzb-fin-platform-scaling-and-reliability-architecture]]
- [[industry-trends/ai-products-shift-from-models-to-systems]]
- [[topics/customer-isolation-and-tenant-fairness]]
- [[topics/incremental-and-reversible-infrastructure-changes]]

## Why it matters

The piece is useful because it turns vague “we can scale” claims into concrete operating patterns: use commodity primitives where they are strong, push complexity into the layers that actually need it, and make big infrastructure changes incremental and reversible. The database section is the most durable part of the article because it names a specific migration outcome—Vitess managed by PlanetScale completed in 2025—and ties it to concrete benefits such as shard-level isolation, online schema change, and reduced downtime risk. The search section adds a second reusable pattern: large Elasticsearch changes should be reshaped online rather than handled as high-risk manual migrations. The multi-tenant fairness discussion is also practical, because it shows that customer isolation has to be built into queues and application guardrails, not left to engineer memory. The Fin-specific section matters because it treats an AI agent as an availability-sensitive production system with routing, failover, and capacity management, not as a single model call. The article is strongest as an implementation case, not as an independent benchmark or third-party validation. As of 2026-05-19, the guidance is actionable for teams that already run serious multi-tenant SaaS or AI support workflows, but it should be read as a vendor’s own operating model rather than a universal proof.

## Limitations / open questions

The article gives detailed capacity numbers and architecture claims, but it does not provide external benchmarks, latency distributions, error rates, cost data, or before/after comparisons beyond a few point-in-time metrics. The database and search sections describe the mechanisms, but not the operational cost of running them, the failure modes encountered during migration, or how much engineering overhead the new patterns add. Claims about 2x to 3x headroom for Fin are framed by the vendor and are not independently verified here. It is also unclear how much of this architecture would transfer to smaller systems that do not have the same scale, organizational maturity, or multi-tenant complexity. The article emphasizes internal control and safety, but it does not discuss security, privacy, compliance, or data governance tradeoffs in depth. The production-learning examples are persuasive, yet they remain anecdotal rather than systematically evaluated.

## Contradictions / unverified claims

The article correctly notes that big throughput numbers age quickly, but it still uses them prominently, so the reader should treat them as context rather than proof of robustness. The “boring foundations” message is sensible, though it is also a vendor narrative that can understate how much hidden complexity remains in sharding, fair queues, routing, and online migrations. The piece presents fast shipping as a reliability enabler, which is plausible, but that claim depends on disciplined review, observability, and rollback execution; the article asserts these practices without independent evidence. The AI-routing discussion is promising, but multi-provider failover and capacity buffering can be expensive and operationally complex, and the article does not quantify those tradeoffs. Overall, the skepticism is moderate rather than severe: the mechanics are concrete, but the evidence base is still a first-party case study.

## Source metadata

- Canonical URL: https://www.intercom.com/blog/ready-for-your-busiest-day-how-we-scale/
- Raw markdown: `raw/readwise/ready-for-your-busiest-day-how-we-scale-01ks0e1b38y1emnqkewpcvbhzb.md`
- Raw HTML: `raw/readwise/ready-for-your-busiest-day-how-we-scale-01ks0e1b38y1emnqkewpcvbhzb.html`
