---
title: Agent Contract Programming
slug: agent-contract-programming
entity_id: topic:agent-contract-programming
category: topic
tags:
- agent-orchestration
- agent-systems
- auditability
- workflow-design
first_seen: '2026-06-04'
last_seen: '2026-06-04'
source_count: 1
evidence_count: 8
source_ids:
- how-openprose-makes-ai-agent-behavior-repeatable-01ktb3ceq8be6weh8yt0k73z4f
value_level: high
confidence: 0.92
synthesis_state: stage1-placeholder
---

# Agent Contract Programming

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Agent workflows become more repeatable when the intended behavior is written as an explicit contract rather than left implicit in chat history. A contract separates what the workflow needs, what it must produce, and what evidence it must leave behind. This makes the work easier to review, version, and rerun across sessions and harnesses. The main operational idea is to constrain outputs and proof, not to rely on the model remembering a successful conversation. The approach is useful when the work is valuable enough to justify structure, but not so rigid that ordinary scripts alone are sufficient.

## Key Points

- `### Requires` and `### Ensures` are the central contract surfaces.
- The contract should include evidence requirements, not just output shape.
- Versioned text artifacts are easier to review than hidden chat state.
- A good contract can be reused across different coding-agent harnesses.

## Operational Insight

Write down the required inputs, required outputs, and proof of completion as durable artifacts, then let the agent execute inside that boundary.

## Evidence / supporting sources

### How OpenProse Makes AI Agent Behavior Repeatable (2026-06-04)

- Agent workflows become more repeatable when the intended behavior is written as an explicit contract rather than left implicit in chat history. A contract separates what the workflow needs, what it must produce, and what evidence it must leave behind. This makes the work easier to review, version, and rerun across sessions and harnesses. The main operational idea is to constrain outputs and proof, not to rely on the model remembering a successful conversation. The approach is useful when the work is valuable enough to justify structure, but not so rigid that ordinary scripts alone are sufficient. (`2d078a75a15d` · neutral · knowledge_summary; [[sources/how-openprose-makes-ai-agent-behavior-repeatable-01ktb3ceq8be6weh8yt0k73z4f|How OpenProse Makes AI Agent Behavior Repeatable]])
- Write down the required inputs, required outputs, and proof of completion as durable artifacts, then let the agent execute inside that boundary. (`bd930552c887` · neutral · operational_insight; [[sources/how-openprose-makes-ai-agent-behavior-repeatable-01ktb3ceq8be6weh8yt0k73z4f|How OpenProse Makes AI Agent Behavior Repeatable]])
- This pattern matters for any AI workflow where repeatability and reviewability are more important than one-off improvisation. It gives teams a way to preserve successful behavior as a versioned artifact instead of depending on a lucky session. That is especially useful in coding agents, document workflows, and service automation where failures need to be inspectable. (`9112d9e61dbc` · neutral · relevance_note; [[sources/how-openprose-makes-ai-agent-behavior-repeatable-01ktb3ceq8be6weh8yt0k73z4f|How OpenProse Makes AI Agent Behavior Repeatable]])
- `### Requires` and `### Ensures` are the central contract surfaces. (`345d48872e30` · supporting · key_points[0]; [[sources/how-openprose-makes-ai-agent-behavior-repeatable-01ktb3ceq8be6weh8yt0k73z4f|How OpenProse Makes AI Agent Behavior Repeatable]])
- The contract should include evidence requirements, not just output shape. (`1b2a7dd7f2c6` · supporting · key_points[1]; [[sources/how-openprose-makes-ai-agent-behavior-repeatable-01ktb3ceq8be6weh8yt0k73z4f|How OpenProse Makes AI Agent Behavior Repeatable]])
- Versioned text artifacts are easier to review than hidden chat state. (`b60c723576dc` · supporting · key_points[2]; [[sources/how-openprose-makes-ai-agent-behavior-repeatable-01ktb3ceq8be6weh8yt0k73z4f|How OpenProse Makes AI Agent Behavior Repeatable]])
- A good contract can be reused across different coding-agent harnesses. (`b1cfb4310de8` · supporting · key_points[3]; [[sources/how-openprose-makes-ai-agent-behavior-repeatable-01ktb3ceq8be6weh8yt0k73z4f|How OpenProse Makes AI Agent Behavior Repeatable]])
- A Prose program is a Markdown file (`*.prose.md`) that declares a service in logical English. The two sections that matter most are `### Requires` (the inputs the service needs before it can start) and `### Ensures` (what must be true when it’s done). (`d1aafc8ec66e` · supporting · supporting_snippet; [[sources/how-openprose-makes-ai-agent-behavior-repeatable-01ktb3ceq8be6weh8yt0k73z4f|How OpenProse Makes AI Agent Behavior Repeatable]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- [[topics/production-traceability-for-agent-improvement|Production Traceability for Agent Improvement]]
- [[topics/structured-specification-for-agentic-development|Structured Specification for Agentic Development]]

## Sources

- [[sources/how-openprose-makes-ai-agent-behavior-repeatable-01ktb3ceq8be6weh8yt0k73z4f|How OpenProse Makes AI Agent Behavior Repeatable]]
