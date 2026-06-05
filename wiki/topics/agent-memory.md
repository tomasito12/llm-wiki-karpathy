---
title: Agent Memory
slug: agent-memory
entity_id: topic:agent-memory
category: topic
tags:
- agent-memory
- knowledge-systems
- runtime-architecture
first_seen: '2026-05-08'
last_seen: '2026-05-08'
source_count: 1
evidence_count: 9
source_ids:
- unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv
value_level: high
confidence: 0.98
synthesis_state: stage1-placeholder
---

# Agent Memory

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Agent memory is durable state that survives beyond a single turn or session and can be reused later to improve continuity. In practical systems, memory is often split between passive capture, offline distillation, and online injection. A strong memory design avoids relying on the model to decide what matters and instead stores events or facts deterministically before compressing them into reusable notes. The important operational question is not just where memory lives, but how it is written, rewritten, and reintroduced into context.

## Examples

The source describes memories as small markdown files such as "profile/role.md" and "tools/bash/common-flags.md" that are merged rather than appended.

## Key Points

- Passive logging is more reliable than asking the model to remember what to store.
- Offline summarization can compress sessions into durable facts.
- Rewrite-in-place memory keeps knowledge current better than endless append-only logs.
- Online injection and direct retrieval are complementary rather than interchangeable.

## Operational Insight

Use memory as a living document, not a transcript. Deterministic capture plus periodic rewriting is a cleaner pattern than asking the agent to self-manage every fact it should remember.

## Related Topics

- harness-engineering

## Evidence / supporting sources

### Unified Agentic Memory Across Harnesses Using Hooks (2026-05-08)

- The source describes memories as small markdown files such as "profile/role.md" and "tools/bash/common-flags.md" that are merged rather than appended. (`507882b5e762` · neutral · examples; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- Agent memory is durable state that survives beyond a single turn or session and can be reused later to improve continuity. In practical systems, memory is often split between passive capture, offline distillation, and online injection. A strong memory design avoids relying on the model to decide what matters and instead stores events or facts deterministically before compressing them into reusable notes. The important operational question is not just where memory lives, but how it is written, rewritten, and reintroduced into context. (`48494294a6cd` · neutral · knowledge_summary; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- Use memory as a living document, not a transcript. Deterministic capture plus periodic rewriting is a cleaner pattern than asking the agent to self-manage every fact it should remember. (`b4d31442fe63` · neutral · operational_insight; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- Agent memory is central to conversational systems that need continuity across sessions, especially coding assistants and support automation flows. The reusable lesson is that memory quality depends on capture policy and retrieval timing, not just on the presence of a vector store or database. (`27bd67566826` · neutral · relevance_note; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- Passive logging is more reliable than asking the model to remember what to store. (`8949f6a6ea5e` · supporting · key_points[0]; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- Offline summarization can compress sessions into durable facts. (`3da01631b5fe` · supporting · key_points[1]; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- Rewrite-in-place memory keeps knowledge current better than endless append-only logs. (`577553c963b8` · supporting · key_points[2]; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- Online injection and direct retrieval are complementary rather than interchangeable. (`3c4836f2c573` · supporting · key_points[3]; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- "The idea is for this blog post is simple: keep the memory layer outside the harness, and let any harness plug into it." (`bed9c706d83f` · supporting · supporting_snippet; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- harness-engineering

## Sources

- [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]]
