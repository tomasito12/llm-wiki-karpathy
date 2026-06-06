---
title: 'Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software
  Factory Future — Simon Last & Sarah Sachs of Notion'
slug: notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f
category: source
tags:
- agent-evals
- agent-memory
- agent-orchestration
- agent-systems
- ai-economics
- ai-evaluation
- context-engineering
- enterprise-ai
- enterprise-workflows
- infrastructure-economics
- knowledge-systems
- retrieval-systems
- test-and-verification
- verification-systems
- workflow-automation
- workflow-design
source_id: notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f
author: Latent Space
publication: Latent
published_date: '2026-04-15'
assessed_as_of: '2026-04-15'
ingested_at: '2026-06-05T15:28:32.680537+00:00'
canonical_url: https://www.latent.space/p/notion
content_sha256: 30cc50e4340c346681021eae57eb692c635318ec1733897fde5cb2f98eddd023
derived_interview_insights:
- interview-insights/2026-04/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-fu-design-agent-products-around-model-constraints-not-product-complexit-f5580eb500.md
- interview-insights/2026-04/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-fu-evals-should-be-treated-as-an-agent-harness-not-just-testing-4d8f7c7373.md
- interview-insights/2026-04/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-fu-retrieval-for-agents-optimizes-differently-than-retrieval-for-humans-af7746ae5a.md
- interview-insights/2026-04/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-fu-the-best-agent-products-expose-primitives-not-hidden-magic-3dd14771ee.md
- interview-insights/2026-04/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-fu-usage-based-pricing-is-required-when-model-search-and-sandbox-costs-5658260ad2.md
derived_pages:
- interview-insights/2026-04/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-fu-design-agent-products-around-model-constraints-not-product-complexit-f5580eb500.md
- interview-insights/2026-04/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-fu-evals-should-be-treated-as-an-agent-harness-not-just-testing-4d8f7c7373.md
- interview-insights/2026-04/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-fu-retrieval-for-agents-optimizes-differently-than-retrieval-for-humans-af7746ae5a.md
- interview-insights/2026-04/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-fu-the-best-agent-products-expose-primitives-not-hidden-magic-3dd14771ee.md
- interview-insights/2026-04/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-fu-usage-based-pricing-is-required-when-model-search-and-sandbox-costs-5658260ad2.md
---

# Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion

This conversation is about how Notion turned its productivity app into an agent platform. The interesting part is that they did not just wrap a model around existing features; they kept rebuilding the system until the tools, prompts, permissions, and evaluations fit how models actually behave. They also use Notion’s own data structures, like pages and databases, as the memory and coordination layer for agents. That makes the product feel less like a chatbot and more like a workspace where agents can act safely. The episode is especially useful if you care about building reliable agent products for real work, not just demos.

## Key insights

- Notion’s main lesson is to design around model constraints: use simpler tool representations, progressive disclosure, and a shorter system prompt instead of forcing the model to cope with the product’s internal complexity.
- They treat evals as a first-class platform layer, with regression tests, launch-quality evals, and deliberately hard headroom evals that should pass only about 30% of the time.
- The company separates model behavior work into its own career path, because failure analysis, rubric design, and judge building are not just ordinary software engineering tasks.
- Notion prefers primitives over bespoke agent features: pages, databases, triggers, and permissions are the substrate for memory, coordination, and agent-to-agent communication.
- Pricing is intentionally usage-based because the cost of model choice, search, sandboxing, and tiering varies too much to map cleanly to raw token throughput.

## Derived knowledge pages

- [[interview-insights/2026-04/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-fu-design-agent-products-around-model-constraints-not-product-complexit-f5580eb500]]
- [[interview-insights/2026-04/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-fu-evals-should-be-treated-as-an-agent-harness-not-just-testing-4d8f7c7373]]
- [[interview-insights/2026-04/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-fu-retrieval-for-agents-optimizes-differently-than-retrieval-for-humans-af7746ae5a]]
- [[interview-insights/2026-04/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-fu-the-best-agent-products-expose-primitives-not-hidden-magic-3dd14771ee]]
- [[interview-insights/2026-04/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-fu-usage-based-pricing-is-required-when-model-search-and-sandbox-costs-5658260ad2]]

## Why it matters

This piece is valuable because it gives a concrete, operator-level view of what it takes to ship agentic software inside an established product with real users and enterprise constraints. Notion’s team describes multiple rebuilds, and the important detail is not just that models improved; it is that they learned to stop fighting the model and instead reshape the harness, tool surface, and prompt architecture around what the model can use well. The interview also shows a durable pattern for agent products: keep the outer system simple and inspectable, make tools individually owned, and use evals to decide when to expose new capability. Their stance on MCP versus CLI is especially practical: CLI can be powerful because the agent can self-debug in the same environment, while MCP can be better for narrow, tightly permissioned tool access. The pricing discussion is also useful because it ties product economics to capability choice rather than pretending every action is equivalent. For builders, the most reusable idea is that “teaching the top of the class” means giving expert users enough visibility and control that the agent remains legible and debuggable. The closing, more domain-specific point is that meeting notes are treated as data capture, not just transcription, which is why they become a strong source of context for search and follow-up workflows; that is actionable as of 2026-04-15 and likely durable if your product also turns conversations into structured work.

## Limitations / open questions

Much of the discussion is self-reported product strategy and internal practice, so it is hard to verify which choices are broadly generalizable versus specific to Notion’s stack and culture. Several claims about reliability, model quality differences across providers, and the benefits of self-healing agents are anecdotal rather than benchmarked in the transcript. The interview gives very little hard detail on failure rates, user adoption breakdowns, cost curves, or how often each tool path is actually chosen in production. The “software factory” vision is compelling but still mostly aspirational here; the transcript does not show end-to-end metrics proving that human intervention can be minimized safely at scale. The retrieval and ranking section is concrete in direction but thin on implementation detail, especially around how they evaluate ranking quality for agentic search beyond general remarks about top-K and snippets. The meeting-notes section is convincing as a product narrative, but the transcript does not quantify retention lift or isolate causality beyond the speakers’ assertions.

## Contradictions / unverified claims

Some claims are ambitious and should be treated cautiously. For example, calling coding agents the kernel of AGI and implying a software factory of cooperating agents may be directionally interesting, but the transcript does not provide evidence that this abstraction is robust outside Notion’s environment. The idea that public system prompts are not secret sauce may be true for this product, but it could understate how much product quality still depends on hidden operational tuning. Their preference for custom, native integrations over MCP is plausible, yet the argument leans heavily on quality control and cost alignment rather than measured comparisons. The strongest skeptical note is that several conclusions are drawn from internal workflows and one live demo, so the piece is rich on implementation taste but light on external validation.

## Source metadata

- Canonical URL: https://www.latent.space/p/notion
- Raw markdown: `raw/readwise/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f.md`
- Raw HTML: `raw/readwise/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f.html`
