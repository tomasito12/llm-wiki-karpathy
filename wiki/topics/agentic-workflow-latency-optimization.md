---
title: Agentic Workflow Latency Optimization
slug: agentic-workflow-latency-optimization
entity_id: topic:agentic-workflow-latency-optimization
category: topic
tags:
- agent-systems
- runtime-architecture
first_seen: '2026-04-22'
last_seen: '2026-04-22'
source_count: 1
evidence_count: 7
source_ids:
- speeding-up-agentic-workflows-with-websockets-in-the-responses-api-01kpv0wxjnsv9gk1qw36wa3z1x
value_level: high
confidence: 0.96
synthesis_state: stage1-placeholder
---

# Agentic Workflow Latency Optimization

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Agentic systems often spend substantial time outside model inference, especially when each tool call, state rebuild, and validation step becomes a separate round trip. A useful design principle is to measure the full loop, not just token generation speed, because small per-request overheads compound across long workflows. Persistent connections, cached state, and reduced network hops can materially improve end-to-end responsiveness even when the model itself is already fast. The main engineering lesson is that the transport protocol and request lifecycle are part of the product architecture, not just plumbing.

## Key Points

- End-to-end latency can be dominated by API services and client-side work once inference gets faster.
- Connection-scoped caches let follow-up steps reuse response state instead of rebuilding context from scratch.
- Preserving the existing request body while changing transport lowers migration friction for builders.

## Operational Insight

Treat repeated agent turns as a throughput problem, not only an inference problem. If the model is fast enough, optimize connection reuse, state reuse, and post-inference overlap before chasing marginal model gains.

## Evidence / supporting sources

### Speeding up agentic workflows with WebSockets in the Responses API (2026-04-22)

- Agentic systems often spend substantial time outside model inference, especially when each tool call, state rebuild, and validation step becomes a separate round trip. A useful design principle is to measure the full loop, not just token generation speed, because small per-request overheads compound across long workflows. Persistent connections, cached state, and reduced network hops can materially improve end-to-end responsiveness even when the model itself is already fast. The main engineering lesson is that the transport protocol and request lifecycle are part of the product architecture, not just plumbing. (`6469da656f67` · neutral · knowledge_summary; [[sources/speeding-up-agentic-workflows-with-websockets-in-the-responses-api-01kpv0wxjnsv9gk1qw36wa3z1x|Speeding up agentic workflows with WebSockets in the Responses API]])
- Treat repeated agent turns as a throughput problem, not only an inference problem. If the model is fast enough, optimize connection reuse, state reuse, and post-inference overlap before chasing marginal model gains. (`c914eb96bfb0` · neutral · operational_insight; [[sources/speeding-up-agentic-workflows-with-websockets-in-the-responses-api-01kpv0wxjnsv9gk1qw36wa3z1x|Speeding up agentic workflows with WebSockets in the Responses API]])
- This pattern matters wherever agents do multi-step work with tools, memory, or approvals. In production conversational systems, reducing protocol overhead can improve perceived responsiveness without changing the underlying model. (`cc55e909f448` · neutral · relevance_note; [[sources/speeding-up-agentic-workflows-with-websockets-in-the-responses-api-01kpv0wxjnsv9gk1qw36wa3z1x|Speeding up agentic workflows with WebSockets in the Responses API]])
- End-to-end latency can be dominated by API services and client-side work once inference gets faster. (`93a537010f49` · supporting · key_points[0]; [[sources/speeding-up-agentic-workflows-with-websockets-in-the-responses-api-01kpv0wxjnsv9gk1qw36wa3z1x|Speeding up agentic workflows with WebSockets in the Responses API]])
- Connection-scoped caches let follow-up steps reuse response state instead of rebuilding context from scratch. (`eba6c850498a` · supporting · key_points[1]; [[sources/speeding-up-agentic-workflows-with-websockets-in-the-responses-api-01kpv0wxjnsv9gk1qw36wa3z1x|Speeding up agentic workflows with WebSockets in the Responses API]])
- Preserving the existing request body while changing transport lowers migration friction for builders. (`8ac9054a4743` · supporting · key_points[2]; [[sources/speeding-up-agentic-workflows-with-websockets-in-the-responses-api-01kpv0wxjnsv9gk1qw36wa3z1x|Speeding up agentic workflows with WebSockets in the Responses API]])
- "the Codex agent loop spends most of its time in three main stages: working in the API services (to validate and process requests), model inference, and client-side time (running tools and building model context)." (`399e50e7ed5e` · supporting · supporting_snippet; [[sources/speeding-up-agentic-workflows-with-websockets-in-the-responses-api-01kpv0wxjnsv9gk1qw36wa3z1x|Speeding up agentic workflows with WebSockets in the Responses API]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- [[topics/agentic-workflows|Agentic Workflows]]

## Sources

- [[sources/speeding-up-agentic-workflows-with-websockets-in-the-responses-api-01kpv0wxjnsv9gk1qw36wa3z1x|Speeding up agentic workflows with WebSockets in the Responses API]]
