---
title: Fin Platform Scaling and Reliability Architecture
slug: fin-platform-scaling-and-reliability-architecture
category: implementation-study
tags:
- enterprise-ai
- support-automation
source_id: ready-for-your-busiest-day-how-we-scale-01ks0e1b38y1emnqkewpcvbhzb
source_title: 'Ready for your busiest day: How we scale'
source_date: '2026-05-19'
month: 2026-05
company: Intercom
industry: customer support software
evidence_count: 21
evidence_set_hash: fcc8a94f8aa45683
---

# Fin Platform Scaling and Reliability Architecture

## Implementation Study

### Overview

Intercom describes how it scales its Fin and core platform across database, search, queues, and AI routing layers. The system is presented as already handling high-volume production traffic, with design choices intended to keep customer spikes isolated and routine maintenance non-disruptive.

### What was implemented?

Vitess managed by PlanetScale for sharded source-of-truth data, Elasticsearch index reshaping workflows, AWS SQS fair queues, application-level guardrails for multi-tenant isolation, and Fin LLM routing with multi-provider failover and capacity buffering.

### Business objective

Improve availability, reduce operational complexity, make migrations safer, simplify scaling, and eliminate customer downtime from routine database maintenance and failovers.

### Technical approach

Use commodity AWS primitives where appropriate, move source-of-truth data to Vitess/PlanetScale, spread critical database data across 128 shards, reshape Elasticsearch indexes online with dual writes and backfills, enforce tenant fairness in queues, and route Fin traffic across multiple model providers with failover and latency-based routing.

### Deployment context

Live production operations for a large multi-tenant customer support platform, including daily peak traffic, customer-specific spikes, search workloads, and AI support traffic.

### Outcome / current status

The article says the database migration completed in 2025 and the platform is operating day to day with the new architecture. It reports high-scale operation rather than a pilot or prototype.

### Why it succeeded or struggled

Success appears to come from building explicit scaling levers, keeping changes incremental, and enforcing isolation at multiple layers. The article also credits boring commodity primitives for reducing unnecessary engineering effort.

### Operational constraints

The source-of-truth database must remain correct, fast, resilient to failover, and safe for large migrations. Search indexes and multi-tenant queues must tolerate live traffic, and Fin cannot depend on a single model, provider, region, or capacity pool.

### AI / model observations

Fin is treated as production infrastructure rather than a single model call. Intercom says its LLM layer uses cross-vendor failover, cross-model failover, latency-based routing, capacity isolation, and load testing, which suggests AI systems at scale need routing and redundancy rather than model-only optimization.

### Implications for service automation

Support automation systems need the same reliability posture as core backend services when they absorb customer spikes. A voicebot or chatbot that sits on fragile upstream model capacity can fail during incidents or launches, so orchestration, routing, and headroom matter as much as model quality.

### Strategic signals

The case frames scale as an operating discipline built around limits, observability, and customer outcomes. It also shows that AI support products increasingly require infrastructure patterns normally associated with critical SaaS systems.

### Key Lessons

- Keep commodity infrastructure boring so engineering effort stays on differentiated problems.
- Design for shard-level or tenant-level isolation before a single customer's spike becomes everyone else's problem.
- Make database and search migrations incremental and reversible.
- Treat AI routing and failover as part of the product's reliability layer, not as an afterthought.

### Open Questions

- The article does not quantify the cost or operational overhead of the architecture.
- It does not provide external validation of the capacity numbers or headroom claims.
- It is unclear how much of this architecture would transfer to smaller systems with less operational maturity.

### Related Sources

- https://www.intercom.com/blog/ready-for-your-busiest-day-how-we-scale/

### Evidence Snippets

- Intercom says its platform handles very large daily peaks and workspace spikes in production. — "At daily peak, we see over 150,000 customer requests per second coming into the platform, with more than 70,000 asynchronous requests per second flowing through the background systems." (stated)
- The database migration completed and now supports shard-level isolation at large scale. — "We completed that migration in 2025... Today, our highest-scale source-of-truth data is spread across 128 shards." (stated)
- Fin uses multi-provider routing and buffer capacity to handle spikes. — "Our LLM routing layer supports cross-vendor failover, cross-model failover, latency-based routing, capacity isolation, and load testing. We also maintain buffer capacity with major providers, with headroom to handle 2x to 3x normal Fin traffic at any point." (stated)

## Evidence / supporting sources

### Ready for your busiest day: How we scale (2026-05-19)

- Fin is treated as production infrastructure rather than a single model call. Intercom says its LLM layer uses cross-vendor failover, cross-model failover, latency-based routing, capacity isolation, and load testing, which suggests AI systems at scale need routing and redundancy rather than model-only optimization. (`f5bde817ac43` · neutral · ai_model_observations; [[sources/ready-for-your-busiest-day-how-we-scale-01ks0e1b38y1emnqkewpcvbhzb|Ready for your busiest day: How we scale]])
- Improve availability, reduce operational complexity, make migrations safer, simplify scaling, and eliminate customer downtime from routine database maintenance and failovers. (`308a5384a308` · neutral · business_objective; [[sources/ready-for-your-busiest-day-how-we-scale-01ks0e1b38y1emnqkewpcvbhzb|Ready for your busiest day: How we scale]])
- Live production operations for a large multi-tenant customer support platform, including daily peak traffic, customer-specific spikes, search workloads, and AI support traffic. (`e755892a8ceb` · neutral · deployment_context; [[sources/ready-for-your-busiest-day-how-we-scale-01ks0e1b38y1emnqkewpcvbhzb|Ready for your busiest day: How we scale]])
- Support automation systems need the same reliability posture as core backend services when they absorb customer spikes. A voicebot or chatbot that sits on fragile upstream model capacity can fail during incidents or launches, so orchestration, routing, and headroom matter as much as model quality. (`799b805dde87` · neutral · implications_for_service_automation; [[sources/ready-for-your-busiest-day-how-we-scale-01ks0e1b38y1emnqkewpcvbhzb|Ready for your busiest day: How we scale]])
- The article does not quantify the cost or operational overhead of the architecture. (`c8cbfaf542d5` · neutral · open_questions[0]; [[sources/ready-for-your-busiest-day-how-we-scale-01ks0e1b38y1emnqkewpcvbhzb|Ready for your busiest day: How we scale]])
- It does not provide external validation of the capacity numbers or headroom claims. (`03dfdef62f94` · neutral · open_questions[1]; [[sources/ready-for-your-busiest-day-how-we-scale-01ks0e1b38y1emnqkewpcvbhzb|Ready for your busiest day: How we scale]])
- It is unclear how much of this architecture would transfer to smaller systems with less operational maturity. (`68512be8bbce` · neutral · open_questions[2]; [[sources/ready-for-your-busiest-day-how-we-scale-01ks0e1b38y1emnqkewpcvbhzb|Ready for your busiest day: How we scale]])
- The source-of-truth database must remain correct, fast, resilient to failover, and safe for large migrations. Search indexes and multi-tenant queues must tolerate live traffic, and Fin cannot depend on a single model, provider, region, or capacity pool. (`188e5648c3da` · neutral · operational_constraints; [[sources/ready-for-your-busiest-day-how-we-scale-01ks0e1b38y1emnqkewpcvbhzb|Ready for your busiest day: How we scale]])
- The article says the database migration completed in 2025 and the platform is operating day to day with the new architecture. It reports high-scale operation rather than a pilot or prototype. (`2b78c8a29169` · neutral · outcome_status; [[sources/ready-for-your-busiest-day-how-we-scale-01ks0e1b38y1emnqkewpcvbhzb|Ready for your busiest day: How we scale]])
- Intercom describes how it scales its Fin and core platform across database, search, queues, and AI routing layers. The system is presented as already handling high-volume production traffic, with design choices intended to keep customer spikes isolated and routine maintenance non-disruptive. (`c1a0c6ae6796` · neutral · overview; [[sources/ready-for-your-busiest-day-how-we-scale-01ks0e1b38y1emnqkewpcvbhzb|Ready for your busiest day: How we scale]])
- The case frames scale as an operating discipline built around limits, observability, and customer outcomes. It also shows that AI support products increasingly require infrastructure patterns normally associated with critical SaaS systems. (`ec0ff8cb156e` · neutral · strategic_signals; [[sources/ready-for-your-busiest-day-how-we-scale-01ks0e1b38y1emnqkewpcvbhzb|Ready for your busiest day: How we scale]])
- Success appears to come from building explicit scaling levers, keeping changes incremental, and enforcing isolation at multiple layers. The article also credits boring commodity primitives for reducing unnecessary engineering effort. (`60d15a176fe7` · neutral · success_or_failure_factors; [[sources/ready-for-your-busiest-day-how-we-scale-01ks0e1b38y1emnqkewpcvbhzb|Ready for your busiest day: How we scale]])
- Use commodity AWS primitives where appropriate, move source-of-truth data to Vitess/PlanetScale, spread critical database data across 128 shards, reshape Elasticsearch indexes online with dual writes and backfills, enforce tenant fairness in queues, and route Fin traffic across multiple model providers with failover and latency-based routing. (`83bc0066feea` · neutral · technical_approach; [[sources/ready-for-your-busiest-day-how-we-scale-01ks0e1b38y1emnqkewpcvbhzb|Ready for your busiest day: How we scale]])
- Vitess managed by PlanetScale for sharded source-of-truth data, Elasticsearch index reshaping workflows, AWS SQS fair queues, application-level guardrails for multi-tenant isolation, and Fin LLM routing with multi-provider failover and capacity buffering. (`603dd4bc223f` · neutral · what_was_implemented; [[sources/ready-for-your-busiest-day-how-we-scale-01ks0e1b38y1emnqkewpcvbhzb|Ready for your busiest day: How we scale]])
- Intercom says its platform handles very large daily peaks and workspace spikes in production. — "At daily peak, we see over 150,000 customer requests per second coming into the platform, with more than 70,000 asynchronous requests per second flowing through the background systems." (`0e8152016b8a` · supporting · evidence_snippets[0]; [[sources/ready-for-your-busiest-day-how-we-scale-01ks0e1b38y1emnqkewpcvbhzb|Ready for your busiest day: How we scale]])
- The database migration completed and now supports shard-level isolation at large scale. — "We completed that migration in 2025... Today, our highest-scale source-of-truth data is spread across 128 shards." (`67fc90918e4b` · supporting · evidence_snippets[1]; [[sources/ready-for-your-busiest-day-how-we-scale-01ks0e1b38y1emnqkewpcvbhzb|Ready for your busiest day: How we scale]])
- Fin uses multi-provider routing and buffer capacity to handle spikes. — "Our LLM routing layer supports cross-vendor failover, cross-model failover, latency-based routing, capacity isolation, and load testing. We also maintain buffer capacity with major providers, with headroom to handle 2x to 3x normal Fin traffic at any point." (`da9584f77e36` · supporting · evidence_snippets[2]; [[sources/ready-for-your-busiest-day-how-we-scale-01ks0e1b38y1emnqkewpcvbhzb|Ready for your busiest day: How we scale]])
- Keep commodity infrastructure boring so engineering effort stays on differentiated problems. (`197fc885759e` · supporting · key_lessons[0]; [[sources/ready-for-your-busiest-day-how-we-scale-01ks0e1b38y1emnqkewpcvbhzb|Ready for your busiest day: How we scale]])
- Design for shard-level or tenant-level isolation before a single customer's spike becomes everyone else's problem. (`f36b2785e8a3` · supporting · key_lessons[1]; [[sources/ready-for-your-busiest-day-how-we-scale-01ks0e1b38y1emnqkewpcvbhzb|Ready for your busiest day: How we scale]])
- Make database and search migrations incremental and reversible. (`67dcb31872f0` · supporting · key_lessons[2]; [[sources/ready-for-your-busiest-day-how-we-scale-01ks0e1b38y1emnqkewpcvbhzb|Ready for your busiest day: How we scale]])
- Treat AI routing and failover as part of the product's reliability layer, not as an afterthought. (`cc000793eb69` · supporting · key_lessons[3]; [[sources/ready-for-your-busiest-day-how-we-scale-01ks0e1b38y1emnqkewpcvbhzb|Ready for your busiest day: How we scale]])

## Source

- [[sources/ready-for-your-busiest-day-how-we-scale-01ks0e1b38y1emnqkewpcvbhzb|Ready for your busiest day: How we scale]]
