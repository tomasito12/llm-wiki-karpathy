---
title: Cross-Harness Agent Memory
slug: cross-harness-agent-memory
entity_id: how_to:cross-harness-agent-memory
category: how-to
tags:
- agent-memory
- agent-systems
- knowledge-systems
first_seen: '2026-05-08'
last_seen: '2026-05-08'
source_count: 1
evidence_count: 13
source_ids:
- unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv
value_level: high
confidence: 0.96
synthesis_state: stage1-placeholder
---

# Cross-Harness Agent Memory

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
This is a way to keep one shared memory layer for coding agents that run inside different harnesses. It solves the problem of vendor lock-in, where each app keeps its own private history and switching tools means losing context. The goal is to make the memory live outside the harness so it can follow the user across clients. As of 2026-05-08, the pattern is aimed at coding assistants that need persistent context without depending on one vendor's memory store.

## Caveats

The article does not prove that rewritten notes remain correct over time, and it does not quantify latency, cost, or failure handling. It also does not address privacy controls, conflict resolution between memories, or what happens when sessions become noisy or long-running.

## Implementation Steps

- Install hook scripts for the harnesses you want to support.
- Write session events to a persistent store as they happen.
- Run a periodic batch job that reads new events since the last watermark.
- Ask a model to distill those events into short memory notes.
- Rewrite memory notes in place so they stay current instead of growing as an append-only log.
- Inject profile-level memory at session start and turn-level context on prompt submission.

## Prerequisites

- A harness that exposes lifecycle hooks such as session start, prompt submission, tool use, and session end.
- A persistent store for event history and memory notes.
- A batch process that can read accumulated events and write back rewritten memories.

## Related Howtos

- agentic-personal-knowledge-management

## Evidence / supporting sources

### Unified Agentic Memory Across Harnesses Using Hooks (2026-05-08)

- Set up hooks to capture session events automatically, store those events in a separate database, and then run a background job that turns the raw history into short durable notes. Load high-level memory at session start, and append session-relevant context when the user submits a prompt. Keep the hook path fast and deterministic by avoiding model calls inside the hook itself. Use a separate retrieval path, such as MCP tools, if the agent needs direct search or editing of memory on demand. (`8d71f7d43379` · neutral · answer_summary; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- Install hook scripts for the harnesses you want to support. (`ddfdc82f28d3` · neutral · implementation_steps[0]; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- Write session events to a persistent store as they happen. (`36ddc799c566` · neutral · implementation_steps[1]; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- Run a periodic batch job that reads new events since the last watermark. (`7ba3c1f0214a` · neutral · implementation_steps[2]; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- Ask a model to distill those events into short memory notes. (`91af4a42cc4b` · neutral · implementation_steps[3]; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- Rewrite memory notes in place so they stay current instead of growing as an append-only log. (`55a47029bf58` · neutral · implementation_steps[4]; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- Inject profile-level memory at session start and turn-level context on prompt submission. (`01c7a7cb8c96` · neutral · implementation_steps[5]; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- A harness that exposes lifecycle hooks such as session start, prompt submission, tool use, and session end. (`bc899a306d8d` · neutral · prerequisites[0]; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- A persistent store for event history and memory notes. (`9ee3796cd192` · neutral · prerequisites[1]; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- A batch process that can read accumulated events and write back rewritten memories. (`387651e6926b` · neutral · prerequisites[2]; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- This is a way to keep one shared memory layer for coding agents that run inside different harnesses. It solves the problem of vendor lock-in, where each app keeps its own private history and switching tools means losing context. The goal is to make the memory live outside the harness so it can follow the user across clients. As of 2026-05-08, the pattern is aimed at coding assistants that need persistent context without depending on one vendor's memory store. (`ac62371fb3ce` · neutral · what_and_problem; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- "keep the memory layer outside the harness, and let any harness plug into it" and "Hooks are deterministic and run at the start of every session to populate the system prompt." (`51aa0bd054b1` · supporting · supporting_snippet; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- The article does not prove that rewritten notes remain correct over time, and it does not quantify latency, cost, or failure handling. It also does not address privacy controls, conflict resolution between memories, or what happens when sessions become noisy or long-running. (`17512d25abd9` · uncertainty · caveats; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])

## Contradictions / tensions

- The article does not prove that rewritten notes remain correct over time, and it does not quantify latency, cost, or failure handling. It also does not address privacy controls, conflict resolution between memories, or what happens when sessions become noisy or long-running. (uncertainty; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])

## Related pages

- agentic-personal-knowledge-management

## Sources

- [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]]
