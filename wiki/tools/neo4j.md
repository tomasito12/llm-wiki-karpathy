---
title: Neo4j
slug: neo4j
entity_id: tool:neo4j
category: tool
tags:
- local-first
- memory
- retrieval
first_seen: '2026-05-08'
last_seen: '2026-05-08'
source_count: 1
evidence_count: 12
source_ids:
- unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv
value_level: high
confidence: 0.89
synthesis_state: stage1-placeholder
types:
- database
---

# Neo4j

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
A graph database used here as the persistent store for session events and markdown-like memories.

## Core Capabilities

- It stores a session as a graph of ordered events, which supports complete audit trails of agent activity.
- It can hold the rewritten memory notes that the offline dream phase produces, so the same store supports capture and recall.
- It can back a memory layer that multiple harnesses share, reducing lock-in to any one client.

## Integration Ecosystem

- The article uses it with hook scripts that emit and read JSON around session lifecycle events.
- The source describes it as compatible with Claude Code, OpenAI Codex, and Cursor through the same hook contract.
- It is also described as compatible with Model Context Protocol tooling if direct graph access is needed on demand.

## Maturity signals

The source treats Neo4j as a production-capable store for agent memory, but that is an implementation choice rather than evidence of broad adoption in this pattern. The article explicitly notes the author works at Neo4j, so the discussion is partly vendor-adjacent and should be read as an applied example, not independent validation.

## Related Tools

- Claude Code

## Strengths

- Supports a session graph that can retain every event, which makes memory replay and auditing practical across multiple clients.
- Works well as a backing store for a separate summarization phase because raw events and distilled memories can live in the same durable system.
- Fits a markdown-wiki style memory organization, which makes stored notes easier to rewrite in place rather than append forever.

## Weaknesses / limitations

The article does not compare Neo4j against other storage options, so the tradeoffs are mostly implied rather than demonstrated. The design also inherits the usual operational burden of maintaining a graph-backed memory store, but the source does not quantify cost, scale, or complexity.

## Evidence / supporting sources

### Unified Agentic Memory Across Harnesses Using Hooks (2026-05-08)

- The article uses it with hook scripts that emit and read JSON around session lifecycle events. (`64ecdeadb545` · neutral · integration_ecosystem[0]; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- The source describes it as compatible with Claude Code, OpenAI Codex, and Cursor through the same hook contract. (`b39a90c85fe3` · neutral · integration_ecosystem[1]; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- It is also described as compatible with Model Context Protocol tooling if direct graph access is needed on demand. (`a5148833c715` · neutral · integration_ecosystem[2]; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- The source treats Neo4j as a production-capable store for agent memory, but that is an implementation choice rather than evidence of broad adoption in this pattern. The article explicitly notes the author works at Neo4j, so the discussion is partly vendor-adjacent and should be read as an applied example, not independent validation. (`2cbefefd3f58` · neutral · maturity_signals; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- This is the storage layer that makes the memory system durable across harnesses. It fits workflows where agent sessions need an auditable event timeline plus a separate, queryable memory store for later injection back into prompts. As of 2026-05-08, the article presents it as the backbone for cross-harness memory persistence rather than as a general-purpose database benchmark. (`cc8c276ba0ee` · neutral · operational_relevance; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- A graph database used here as the persistent store for session events and markdown-like memories. (`d13770b556d0` · neutral · short_description; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- - Supports a session graph that can retain every event, which makes memory replay and auditing practical across multiple clients.
- Works well as a backing store for a separate summarization phase because raw events and distilled memories can live in the same durable system.
- Fits a markdown-wiki style memory organization, which makes stored notes easier to rewrite in place rather than append forever. (`0613ca185cff` · neutral · strengths; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- It stores a session as a graph of ordered events, which supports complete audit trails of agent activity. (`3dff004a616a` · supporting · core_capabilities[0]; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- It can hold the rewritten memory notes that the offline dream phase produces, so the same store supports capture and recall. (`8763e5c533c6` · supporting · core_capabilities[1]; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- It can back a memory layer that multiple harnesses share, reducing lock-in to any one client. (`6878b2167361` · supporting · core_capabilities[2]; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- "we will be using it in this example" and "Each agent session is a node, connected to a linked list of event nodes, one per hook invocation." (`9b57ede9d2c6` · supporting · supporting_snippet; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- The article does not compare Neo4j against other storage options, so the tradeoffs are mostly implied rather than demonstrated. The design also inherits the usual operational burden of maintaining a graph-backed memory store, but the source does not quantify cost, scale, or complexity. (`dd46855962c8` · uncertainty · weaknesses_limitations; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])

## Contradictions / tensions

- The article does not compare Neo4j against other storage options, so the tradeoffs are mostly implied rather than demonstrated. The design also inherits the usual operational burden of maintaining a graph-backed memory store, but the source does not quantify cost, scale, or complexity. (uncertainty; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])

## Related pages

- Claude Code

## Sources

- [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]]
