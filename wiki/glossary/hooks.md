---
title: Hooks
slug: hooks
entity_id: glossary:hooks
category: glossary
first_seen: '2026-05-08'
last_seen: '2026-05-08'
source_count: 1
evidence_count: 4
source_ids:
- unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv
value_level: high
confidence: 0.95
synthesis_state: stage1-placeholder
---

# Hooks

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
A hook is an automatic event-triggered command that runs outside the model’s decision loop to log, inject, or otherwise handle agent lifecycle events deterministically.

## Relevance Note

Useful as a stable concept for agent integrations where deterministic, event-driven behavior is needed across different harnesses.

## Evidence / supporting sources

### Unified Agentic Memory Across Harnesses Using Hooks (2026-05-08)

- In agent harnesses, hooks act as the integration layer that fires on predefined events such as session start, user prompt submission, tool use, and session end. Because they run automatically rather than being chosen by the model, they are suited to passive logging and prompt/context injection without relying on the agent to remember to call a tool. The source frames hooks as standardized across multiple coding agents and useful for building portable integrations that work across harnesses. (`47aa31097720` · neutral · extended_explanation; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- A hook is an automatic event-triggered command that runs outside the model’s decision loop to log, inject, or otherwise handle agent lifecycle events deterministically. (`5a990ff9cef9` · neutral · proposed_definition; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- Useful as a stable concept for agent integrations where deterministic, event-driven behavior is needed across different harnesses. (`e473e4b333eb` · neutral · relevance_note; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])
- Hooks are shell commands that fire automatically on lifecycle events: when a session starts, when the user submits a prompt, before and after every tool use, and when the session ends. The agent doesn’t decide to call them, they run programatically. (`d704cfe1aa5b` · supporting · supporting_snippet; [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

No related pages captured.

## Sources

- [[sources/unified-agentic-memory-across-harnesses-using-hooks-01kr7bk2d0hagq604nt14zrqcv|Unified Agentic Memory Across Harnesses Using Hooks]]
