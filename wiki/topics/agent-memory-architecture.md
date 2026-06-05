---
title: Agent Memory Architecture
slug: agent-memory-architecture
entity_id: topic:agent-memory-architecture
category: topic
tags:
- agent-memory
- agent-systems
- knowledge-systems
- runtime-architecture
first_seen: '2026-04-27'
last_seen: '2026-04-27'
source_count: 1
evidence_count: 8
source_ids:
- rag-llm-wiki-or-gbrain-how-your-agent-remembers-changes-everything-01kqkvj2z9yv69c235tfg6b2gk
value_level: high
confidence: 0.93
synthesis_state: stage1-placeholder
---

# Agent Memory Architecture

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Agent memory architecture is the design of how an agent retains, compiles, and reuses information across sessions and tasks. A useful architecture separates ephemeral context from durable knowledge so the agent can avoid re-reading the same material from scratch every time. In practice, this can mean a retrieval layer for raw document access, a synthesis layer for persistent knowledge, and an action layer for triggers and workflows. The main design question is not whether memory exists, but what kind of work the memory is supposed to support. Systems that blur these roles tend to suffer from repeated computation, weak compounding, or poor automation hooks.

## Key Points

- Context windows are temporary; durable memory needs a separate architecture.
- Retrieval, synthesis, and action are distinct memory functions.
- A good memory layer should support compounding, not just recall.
- The best architecture depends on whether the agent answers, learns, or acts.

## Operational Insight

Choose the memory layer around the job: retrieve answers, compound knowledge, or trigger actions. That separation helps avoid trying to make one mechanism solve scale, learning, and autonomy at once.

## Related Topics

- retrieval-augmented-generation
- llm-wiki
- agentic-workflows

## Evidence / supporting sources

### RAG, LLM Wiki, or Gbrain? How Your Agent Remembers Changes Everything (2026-04-27)

- Agent memory architecture is the design of how an agent retains, compiles, and reuses information across sessions and tasks. A useful architecture separates ephemeral context from durable knowledge so the agent can avoid re-reading the same material from scratch every time. In practice, this can mean a retrieval layer for raw document access, a synthesis layer for persistent knowledge, and an action layer for triggers and workflows. The main design question is not whether memory exists, but what kind of work the memory is supposed to support. Systems that blur these roles tend to suffer from repeated computation, weak compounding, or poor automation hooks. (`7c8f14178393` · neutral · knowledge_summary; [[sources/rag-llm-wiki-or-gbrain-how-your-agent-remembers-changes-everything-01kqkvj2z9yv69c235tfg6b2gk|RAG, LLM Wiki, or Gbrain? How Your Agent Remembers Changes Everything]])
- Choose the memory layer around the job: retrieve answers, compound knowledge, or trigger actions. That separation helps avoid trying to make one mechanism solve scale, learning, and autonomy at once. (`eb2992a86c16` · neutral · operational_insight; [[sources/rag-llm-wiki-or-gbrain-how-your-agent-remembers-changes-everything-01kqkvj2z9yv69c235tfg6b2gk|RAG, LLM Wiki, or Gbrain? How Your Agent Remembers Changes Everything]])
- As of 2026-04-27, this abstraction is useful for designing chatbots, research agents, and service workflows because it separates what should be fetched, what should be written back, and what should be executed. That makes it easier to reason about latency, auditability, and long-running behavior in production agent systems. (`9bd2fff9984b` · neutral · relevance_note; [[sources/rag-llm-wiki-or-gbrain-how-your-agent-remembers-changes-everything-01kqkvj2z9yv69c235tfg6b2gk|RAG, LLM Wiki, or Gbrain? How Your Agent Remembers Changes Everything]])
- Context windows are temporary; durable memory needs a separate architecture. (`7f7f87295503` · supporting · key_points[0]; [[sources/rag-llm-wiki-or-gbrain-how-your-agent-remembers-changes-everything-01kqkvj2z9yv69c235tfg6b2gk|RAG, LLM Wiki, or Gbrain? How Your Agent Remembers Changes Everything]])
- Retrieval, synthesis, and action are distinct memory functions. (`d505722856f4` · supporting · key_points[1]; [[sources/rag-llm-wiki-or-gbrain-how-your-agent-remembers-changes-everything-01kqkvj2z9yv69c235tfg6b2gk|RAG, LLM Wiki, or Gbrain? How Your Agent Remembers Changes Everything]])
- A good memory layer should support compounding, not just recall. (`f5488c3dfcec` · supporting · key_points[2]; [[sources/rag-llm-wiki-or-gbrain-how-your-agent-remembers-changes-everything-01kqkvj2z9yv69c235tfg6b2gk|RAG, LLM Wiki, or Gbrain? How Your Agent Remembers Changes Everything]])
- The best architecture depends on whether the agent answers, learns, or acts. (`0a7d6ac1f8a7` · supporting · key_points[3]; [[sources/rag-llm-wiki-or-gbrain-how-your-agent-remembers-changes-everything-01kqkvj2z9yv69c235tfg6b2gk|RAG, LLM Wiki, or Gbrain? How Your Agent Remembers Changes Everything]])
- "Three patterns. Three trade-offs. One decision framework." (`6dff6086addf` · supporting · supporting_snippet; [[sources/rag-llm-wiki-or-gbrain-how-your-agent-remembers-changes-everything-01kqkvj2z9yv69c235tfg6b2gk|RAG, LLM Wiki, or Gbrain? How Your Agent Remembers Changes Everything]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- agentic-workflows
- llm-wiki
- retrieval-augmented-generation

## Sources

- [[sources/rag-llm-wiki-or-gbrain-how-your-agent-remembers-changes-everything-01kqkvj2z9yv69c235tfg6b2gk|RAG, LLM Wiki, or Gbrain? How Your Agent Remembers Changes Everything]]
