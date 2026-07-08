---
title: Context Compaction
slug: context-compaction
entity_id: how_to:context-compaction
category: how-to
tags:
- agent-memory
- ai-engineering
- context-engineering
- long-running-agents
first_seen: '2026-05-08'
last_seen: '2026-05-08'
source_count: 1
evidence_count: 13
source_ids:
- agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv
value_level: high
confidence: 0.93
synthesis_state: stage1-placeholder
---

# Context Compaction

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Context compaction is the practice of trimming an agent's working state so it carries only the information needed to keep going. It addresses a common problem in long-running agents: logs, tool output, repeated observations, old plans, and dead-end retries pile up and waste tokens. The goal is to preserve the important state while removing noise. This can improve both cost and performance without changing the model choice.

## Caveats

The hard part is deciding what to keep, and the article treats this as a real engineering burden. Compressing too aggressively can remove useful debugging or design state. It may be more expensive on very small cheap models if the compression step itself adds overhead.

## Implementation Steps

- Define what belongs in active context versus archive storage.
- Keep architectural decisions, unresolved bugs, and implementation details in the retained state.
- Drop raw logs, duplicate dumps, and repetitive outputs from the working prompt.
- Set lifecycle or expiry rules for context that does not need to live forever.
- Run compaction before the context becomes excessively bloated.
- Review compaction policies against long-horizon tasks and debugging needs.

## Prerequisites

- A long-running agent or a workflow with accumulating state.
- A way to store raw archives outside the active prompt.
- Rules for which facts must remain visible to the model.

## Evidence / supporting sources

### Agentic AI: How to Save on Tokens (2026-05-08)

- Keep raw outputs in an archive and move only the useful state into active context. Strip out duplicate file dumps, full logs, repeated observations, and dead-end retries. Preserve architectural decisions, unresolved bugs, and the current working set so the model still has enough continuity to act. Treat compaction as part of the state pipeline, not a cleanup step after the context is already bloated. Use it when agents accumulate long histories or noisy tool traces across many steps. (`2ccb6fa1036e` · neutral · answer_summary; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- Define what belongs in active context versus archive storage. (`c8820255252b` · neutral · implementation_steps[0]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- Keep architectural decisions, unresolved bugs, and implementation details in the retained state. (`ada82dd6f52f` · neutral · implementation_steps[1]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- Drop raw logs, duplicate dumps, and repetitive outputs from the working prompt. (`ebb08d164a07` · neutral · implementation_steps[2]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- Set lifecycle or expiry rules for context that does not need to live forever. (`7e428942400d` · neutral · implementation_steps[3]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- Run compaction before the context becomes excessively bloated. (`393d34d7e0f9` · neutral · implementation_steps[4]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- Review compaction policies against long-horizon tasks and debugging needs. (`01e4c73c3604` · neutral · implementation_steps[5]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- A long-running agent or a workflow with accumulating state. (`c13ac11d7264` · neutral · prerequisites[0]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- A way to store raw archives outside the active prompt. (`5ef838567df4` · neutral · prerequisites[1]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- Rules for which facts must remain visible to the model. (`439fc832c024` · neutral · prerequisites[2]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- Context compaction is the practice of trimming an agent's working state so it carries only the information needed to keep going. It addresses a common problem in long-running agents: logs, tool output, repeated observations, old plans, and dead-end retries pile up and waste tokens. The goal is to preserve the important state while removing noise. This can improve both cost and performance without changing the model choice. (`f06045f2d266` · neutral · what_and_problem; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- "agents keep accumulating junk: tool outputs, logs, repeated observations, old plans, stale attempts, and duplicated state." (`d329feebad1c` · supporting · supporting_snippet; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- The hard part is deciding what to keep, and the article treats this as a real engineering burden. Compressing too aggressively can remove useful debugging or design state. It may be more expensive on very small cheap models if the compression step itself adds overhead. (`8a66ab36495e` · uncertainty · caveats; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])

## Contradictions / tensions

- The hard part is deciding what to keep, and the article treats this as a real engineering burden. Compressing too aggressively can remove useful debugging or design state. It may be more expensive on very small cheap models if the compression step itself adds overhead. (uncertainty; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])

## Related pages

No related pages captured.

## Sources

- [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]]
