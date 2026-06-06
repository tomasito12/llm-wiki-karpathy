---
title: Speeding up agentic workflows with WebSockets in the Responses API
slug: speeding-up-agentic-workflows-with-websockets-in-the-responses-api-01kpv0wxjnsv9gk1qw36wa3z1x
category: source
tags:
- agent-systems
- ai-engineering
- ai-operationalization
- execution-oriented-agents
- runtime-architecture
source_id: speeding-up-agentic-workflows-with-websockets-in-the-responses-api-01kpv0wxjnsv9gk1qw36wa3z1x
author: OpenAI Blog
publication: OpenAI
published_date: '2026-04-22'
assessed_as_of: '2026-04-22'
ingested_at: '2026-05-19T16:45:24.997153+00:00'
canonical_url: https://openai.com/index/speeding-up-agentic-workflows-with-websockets
content_sha256: 22ff41f5494efcd56a88ce6aa193fc291f60d4f93b74bf150fa6f236caca1570
derived_topics:
- topics/agentic-workflow-latency-optimization.md
- topics/persistent-connection-response-state-reuse.md
derived_trends:
- industry-trends/transport-layer-optimization-becomes-critical-for-agent-latency.md
derived_pages:
- industry-trends/transport-layer-optimization-becomes-critical-for-agent-latency.md
- topics/agentic-workflow-latency-optimization.md
- topics/persistent-connection-response-state-reuse.md
---

# Speeding up agentic workflows with WebSockets in the Responses API

This post is about making AI agents faster by changing how they talk to the server. When an agent fixes code, it often has to ask the model for a step, run a tool, send the result back, and repeat many times. That back-and-forth can create a lot of waiting, even if the model itself is fast. The team reduced that waiting by keeping a connection open with WebSockets instead of starting a fresh request every time. They also reused state from earlier steps so the system did not have to rebuild the whole conversation again and again. The result was that users could feel the speed of a much faster model instead of being slowed down by the surrounding API work. The post says some partners saw large latency improvements, and that the fastest model hit very high token rates in production traffic. The main lesson is that as model output gets faster, the plumbing around it has to get faster too. As of 2026-04-22, this is a practical engineering change worth adopting when agent workflows are bottlenecked by request overhead.

## Key insights

- Persistent connections can matter more than raw model speed once agent loops involve many tool calls.
- Keeping reusable response state in memory lets follow-up turns skip repeated tokenization, validation, and routing work.
- A transport change can preserve the existing request shape while still cutting latency.
- The biggest latency win came from aligning the API protocol with the actual agent loop, not just from optimizing inference.
- Partners reported sizable workflow speedups, but the evidence is vendor-reported and the article does not provide independent measurement detail.

## Derived knowledge pages

- [[industry-trends/transport-layer-optimization-becomes-critical-for-agent-latency]]
- [[topics/agentic-workflow-latency-optimization]]
- [[topics/persistent-connection-response-state-reuse]]

## Why it matters

The article is useful because it isolates a problem that becomes easy to miss once model inference gets faster: the surrounding API choreography can dominate end-to-end latency. It shows a concrete way to reduce that overhead by keeping a connection open, caching prior response state, and only processing new input on follow-up turns. That is a durable architectural lesson for agent systems that do repeated tool calls, multi-step reasoning, or long-running workflows. The design also illustrates a useful product principle: you can change the transport and execution model without forcing developers to rewrite their integration around a totally new API shape. The strongest evidence here is operational rather than theoretical; OpenAI reports production traffic moving to WebSocket mode and partner latency gains, but the article does not expose full benchmark methodology. As of 2026-04-22, the claim is actionable for teams where request overhead is visibly eating into agent throughput, and it is less compelling if latency is still dominated by the model itself. For service automation workloads, the main implication is that chat or support flows with repeated tool use can benefit from lower round-trip overhead, but the post does not discuss contact centers or voice systems directly.

## Limitations / open questions

The post is vendor-authored and gives limited measurement detail beyond headline speedups, so the exact causal contribution of each optimization is not independently verifiable from the text. It does not describe failure modes, rollback criteria, or how state caching behaves under disconnects, retries, or partial failures. Security and privacy tradeoffs of connection-scoped in-memory caching are not explored. The article also does not say how broadly the results generalize beyond Codex-style agent loops or whether every workload benefits equally from WebSockets versus synchronous requests.

## Contradictions / unverified claims

The main claim is plausible, but the article leans on OpenAI-reported improvements and partner anecdotes rather than a fully transparent evaluation. The narrative implies that transport overhead became the bottleneck once inference got fast, but that will not be true for every workload. The post also frames WebSockets as developer-friendly, yet persistent connections can introduce more operational complexity than plain request/response APIs in real deployments.

## Source metadata

- Canonical URL: https://openai.com/index/speeding-up-agentic-workflows-with-websockets
- Raw markdown: `raw/readwise/speeding-up-agentic-workflows-with-websockets-in-the-responses-api-01kpv0wxjnsv9gk1qw36wa3z1x.md`
- Raw HTML: `raw/readwise/speeding-up-agentic-workflows-with-websockets-in-the-responses-api-01kpv0wxjnsv9gk1qw36wa3z1x.html`
