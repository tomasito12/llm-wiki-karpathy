---
title: Run cloud agents in your own infrastructure
slug: run-cloud-agents-in-your-own-infrastructure-01kr1qhvaw58dz13633c041cmy
category: source
tags:
- agent-systems
- agentic
- ai-operationalization
- cloud-hosted
- coding
- coding-agents
- developer-focused
- enterprise-ai
- execution-environments
- execution-oriented-agents
- infrastructure
- orchestration
- proprietary-model
- runtime-systems
- tool-use
- tool-use-capable
source_id: run-cloud-agents-in-your-own-infrastructure-01kr1qhvaw58dz13633c041cmy
author: Cursor Blog
publication: Cursor
published_date: '2026-03-25'
assessed_as_of: '2026-03-25'
ingested_at: '2026-06-06T20:34:06.597694+00:00'
canonical_url: https://cursor.com/blog/self-hosted-cloud-agents
content_sha256: dd53202c73a767622a2704117f3166faeee72fe49ac62126b38ebc71352d68d4
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
derived_models:
- foundation-models/composer-2.md
derived_tools:
- tools/cursor.md
derived_topics:
- topics/agent-infrastructure.md
- topics/self-hosted-agent-execution.md
derived_trends:
- industry-trends/enterprise-agents-move-into-customer-infrastructure.md
derived_pages:
- foundation-models/composer-2.md
- industry-trends/enterprise-agents-move-into-customer-infrastructure.md
- tools/cursor.md
- topics/agent-infrastructure.md
- topics/self-hosted-agent-execution.md
---

# Run cloud agents in your own infrastructure

Cursor is adding a self-hosted version of its cloud agents. That means the agent can run on machines inside your own network instead of in Cursor’s hosted environment. The appeal is simple: the agent still gets the tools it needs, but your code and build outputs stay in your control. Cursor says this helps teams with strict security rules or complicated internal systems. The basic setup is an outbound worker that Cursor’s cloud talks to, so the customer does not need inbound network access. The article is mainly a product announcement, but it shows how agent workflows can be made easier to adopt in locked-down environments as of 2026-03-25.

## Key insights

- The main product boundary is data and execution locality: Cursor says code, tool execution, and build artifacts never leave the customer environment.
- The agent model is not just chat; Cursor describes full remote machines with terminal, browser, and desktop for parallel autonomous work.
- Cursor is positioning self-hosting as a way to use existing caches, dependencies, and internal endpoints without redesigning the security model.
- Operationally, the deployment model is intentionally low-friction: outbound HTTPS only, no inbound ports, and a single worker start command.
- For larger fleets, Cursor provides Kubernetes-native scaling plus a fleet management API, which suggests the offering targets centralized platform teams rather than only individual developers.

## Derived knowledge pages

- [[foundation-models/composer-2]]
- [[industry-trends/enterprise-agents-move-into-customer-infrastructure]]
- [[tools/cursor]]
- [[topics/agent-infrastructure]]
- [[topics/self-hosted-agent-execution]]

## Why it matters

This article matters because it turns a hosted coding-agent product into something enterprises can place behind their own network boundary, which is often the gating issue for adoption. Cursor is explicit that the attraction is not new model behavior but the ability to keep code, secrets, build artifacts, caches, dependencies, and internal endpoints inside the customer environment. That is operationally relevant because many agent products are limited by where tool execution happens, not by the model itself. The article also reveals the deployment pattern: a per-session worker, outbound-only connectivity, and Kubernetes or fleet-management support for scale. That combination is useful for teams that want agent-driven code changes without building and maintaining their own agent orchestration stack. The strongest claim is still vendor-authored, so the practical value should be validated against real security review, latency, and reliability constraints. As of 2026-03-25, this looks actionable for teams already considering coding agents and blocked by environment isolation; it is more a deployable enterprise option than a proven universal pattern. If the same architecture later expands into reviewable demos, remote takeover, and automations, it could also matter for back-office workflows, but the article only states those features as forthcoming.

## Limitations / open questions

The evidence is a vendor announcement, not an independent deployment study, so security and performance claims are unverified. The article does not quantify latency, orchestration overhead, cost, or failure modes for long-lived workers, Kubernetes scaling, or fleet management. It also does not explain how secrets are handled in practice, what telemetry leaves the customer boundary, or how model access is audited. The phrase that code and artifacts never leave the environment is strong, but the exact data flow boundaries are not fully specified. It is unclear how well the system behaves across highly customized build systems or whether customers need significant internal platform work to operate it safely at scale.

## Contradictions / unverified claims

The piece frames self-hosting as simplifying enterprise adoption, but it still depends on customer-managed workers, infrastructure integration, and security review. The claim that Cursor handles orchestration and model access may reduce platform burden, yet it does not eliminate operational complexity. Several benefits are described in product language rather than evidenced outcomes, so the reader should treat them as plausible capabilities rather than demonstrated results. The announcement is strong on architecture and weak on benchmarks, incident handling, or comparative evaluation against in-house agent runners.

## Source metadata

- Canonical URL: https://cursor.com/blog/self-hosted-cloud-agents
- Raw markdown: `raw/readwise/run-cloud-agents-in-your-own-infrastructure-01kr1qhvaw58dz13633c041cmy.md`
- Raw HTML: `raw/readwise/run-cloud-agents-in-your-own-infrastructure-01kr1qhvaw58dz13633c041cmy.html`

## Full source text

---
readwise_id: 01kr1qhvaw58dz13633c041cmy
title: Run cloud agents in your own infrastructure
author: Cursor Blog
source_url: https://cursor.com/blog/self-hosted-cloud-agents
category: rss
location: archive
published_date: '2026-03-25'
saved_at: '2026-05-07T17:25:11.276000+00:00'
updated_at: '2026-05-07T17:28:53.727168+00:00'
tags:
- processed
publication: Cursor
---

Cursor now offers self-hosted cloud agents that run code and tools securely within your own network. These agents work in isolated environments and handle tasks like coding, testing, and building without exposing your data outside. This solution helps teams keep control over their security while using powerful cloud agent features.
