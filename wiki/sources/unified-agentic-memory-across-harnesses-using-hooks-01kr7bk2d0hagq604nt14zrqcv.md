---
title: Unified Agentic Memory Across Harnesses Using Hooks
slug: unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv
category: source
tags:
- agent-memory
- agent-orchestration
- agent-systems
- coding-agents
- knowledge-systems
- local-first
- memory
- retrieval
- runtime-architecture
- runtime-systems
source_id: unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv
author: Tomaz Bratanic
publication: Medium
published_date: '2026-05-08'
assessed_as_of: '2026-05-08'
ingested_at: '2026-06-02T20:00:21.511258+00:00'
canonical_url: https://towardsdatascience.com/unified-agentic-memory-across-harnesses-using-hooks/
content_sha256: 72c3dd8cc1c6a1ab77ed620f44e5af271228212c373a2a98e770a0994bfc5720
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
derived_glossary:
- glossary/hooks.md
derived_how_to:
- how-to/cross-harness-agent-memory.md
derived_tools:
- tools/neo4j.md
derived_topics:
- topics/agent-memory.md
- topics/harness-engineering.md
derived_trends:
- industry-trends/harness-design-becomes-more-important-for-agent-reliability.md
derived_pages:
- glossary/hooks.md
- how-to/cross-harness-agent-memory.md
- industry-trends/harness-design-becomes-more-important-for-agent-reliability.md
- tools/neo4j.md
- topics/agent-memory.md
- topics/harness-engineering.md
---

# Unified Agentic Memory Across Harnesses Using Hooks

The article explains a way to give coding assistants a shared memory that works across different apps. Instead of letting each assistant keep its own private history, the author stores memory outside the app in a graph database called Neo4j. Small hook scripts watch what happens during a session, like when a chat starts, when the user sends a message, or when a tool is used. Those scripts record the events automatically, so the assistant does not have to decide what is important to remember. Later, a separate background job reads those events and turns them into short notes written like a personal wiki. Because the memory lives outside the app, the same information can be used in Claude Code, OpenAI Codex, and Cursor. The article says this makes it easier to switch between tools without losing context. It also explains that hooks are good for automatic context loading, while Model Context Protocol tools are still useful when the assistant needs to search or edit memory on demand. The main idea is practical: keep memory portable, deterministic, and owned by the user.

## Key insights

- Standardized session hooks can create a portable memory layer across multiple coding harnesses without relying on the model to remember to save state.
- Logging every lifecycle event to Neo4j gives a complete session audit trail, while a separate batch job turns that raw event log into durable markdown-style memories.
- Hooks are best for deterministic injection and logging; they are not a full replacement for MCP tools when the agent needs direct read/write access to memory.
- The article’s memory design treats each path as a living document that is merged and rewritten, not as an append-only log.
- The architecture is explicitly layered: online hooks for capture/injection, offline summarization for memory formation, and optional tools for direct retrieval/editing.

## Derived knowledge pages

- [[glossary/hooks]]
- [[how-to/cross-harness-agent-memory]]
- [[industry-trends/harness-design-becomes-more-important-for-agent-reliability]]
- [[tools/neo4j]]
- [[topics/agent-memory]]
- [[topics/harness-engineering]]

## Why it matters

The piece is useful because it turns an abstract "agent memory" idea into a concrete, portable architecture that does not depend on any single coding harness. Its main engineering contribution is the separation of concerns: hooks capture events deterministically, Neo4j stores them as a session timeline, and an offline job compresses those events into reusable notes. That pattern is durable because it is tied to stable lifecycle events like session start, prompt submission, tool use, and session end, rather than to one vendor’s private memory API. The article also makes a strong operational point: if memory is logged passively instead of chosen by the model, the system avoids inconsistency caused by the model deciding what is worth storing. The markdown-wiki framing is practical for incremental memory updates because it supports rewriting a topic page in place instead of growing an endless log. The discussion of MCP tools is a useful reminder that passive injection and active retrieval solve different problems and may both be needed. The evidence is implementation-level rather than benchmark-level, so the claims are best read as a working design pattern, not a validated performance result. Actionable as of 2026-05-08 for teams building agentic coding workflows that want cross-harness memory portability; its value is architectural and likely durable, but the article does not prove user, latency, or maintenance gains at scale. The service-automation implications are secondary here and are only relevant insofar as the same pattern could later support remembered preferences and workflow continuity.

## Limitations / open questions

The article does not provide comparative benchmarks, failure rates, or maintenance costs for the hook-based approach versus MCP-only memory. It is unclear how the system behaves under conflicting memories, noisy events, or large-scale long-running projects with many sessions. The dream phase depends on another model call and a batch schedule, but the article does not quantify latency, cost, or error handling for that offline step. Security and privacy questions are open: the hooks capture prompts and tool events, so any deployment would need clear controls around sensitive data, access, and retention. The piece also does not show how memory quality is evaluated or how reliably rewritten markdown notes stay correct over time.

## Contradictions / unverified claims

The article’s strongest claim is that hooks make memory deterministic and portable, but that depends on the surrounding harnesses exposing similar lifecycle events and stable payloads. The write-up also leans on the idea that a separate dream phase can safely distill durable memory from raw events, but the article does not show evidence that this summarization preserves important context without introducing drift. The statement that users can switch harnesses and "pick up exactly where you left off" is plausible within the demonstrated setup, but it is not validated beyond the example workflow. The argument is compelling as an architecture sketch, but the practical reliability of the full stack remains unproven in the article.

## Source metadata

- Canonical URL: https://towardsdatascience.com/unified-agentic-memory-across-harnesses-using-hooks/
- Raw markdown: `raw/readwise/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv.md`
- Raw HTML: `raw/readwise/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv.html`

## Full source text

---
readwise_id: "01kr7bk2d0hagq604nt14zrqcv"
title: "Unified Agentic Memory Across Harnesses Using Hooks"
author: "Tomaz Bratanic"
publication: "Medium"
source_url: "https://towardsdatascience.com/unified-agentic-memory-across-harnesses-using-hooks/"
category: "article"
location: "archive"
published_date: "2026-05-08"
saved_at: "2026-05-09T21:51:40.960000+00:00"
updated_at: "2026-05-11T09:40:30.930822+00:00"
tags: ["processed"]
---

Hooks enable different AI coding tools to share a single memory system by logging all session events outside the tools themselves. This memory is stored in Neo4j and updated in batches by summarizing past interactions into organized notes. As a result, users can switch between tools like Claude Code, Codex, and Cursor without losing their agent’s memory or context.
