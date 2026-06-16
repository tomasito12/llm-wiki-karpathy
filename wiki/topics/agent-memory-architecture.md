---
title: Agent Memory Architecture
slug: agent-memory-architecture
entity_id: topic:agent-memory-architecture
category: topic
tags:
- agent-memory
- agent-systems
- context-engineering
- inference-systems
- knowledge-systems
- retrieval-systems
- runtime-architecture
first_seen: '2026-04-14'
last_seen: '2026-05-11'
source_count: 4
evidence_count: 32
source_ids:
- hermes-agent-the-open-source-ai-agent-that-actually-remembers-what-it-learned-yesterday-01kqkyhgefymbv50vnchz4b8w0
- rag-llm-wiki-or-gbrain-how-your-agent-remembers-changes-everything-01kqkvj2z9yv69c235tfg6b2gk
- the-agent-wars-why-i-m-trading-my-openclaw-setup-for-hermes-01krbnd5x8h4xphg9ga77n8hkw
- the-inference-shift-01krv8c6tf3rv57w8qyesagyzp
value_level: high
confidence: 0.9375
synthesis_state: stage1-placeholder
---

# Agent Memory Architecture

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Agent memory works best when different kinds of information are stored at different layers with different latency and recall tradeoffs. Short injected notes can hold the most important active facts, searchable session history can hold deep context, and optional external retrieval can extend beyond a single machine. This layered structure reduces prompt bloat while still preserving useful history. It also creates clear choices about what should be fast, what should be searchable, and what should be externalized.

## Key Points

- Different memory layers should serve different urgency and latency needs.
- Small injected files are useful for active operational facts.
- Searchable historical storage is a practical middle layer for deep recall.
- External retrieval is optional and should be justified by scale or multi-hop needs.
- Durable memory is only useful if it stays coherent across edits and repeated runs.
- Users need some way to inspect or compact memory when the stored context becomes fragmented.
- A system that saves successful workflows as reusable skills can shift effort from re-prompting to retrieval and execution.
- Memory quality is operational, not cosmetic; if the agent forgets identities or prior work, trust drops fast.
- Context windows are temporary; durable memory needs a separate architecture.
- Retrieval, synthesis, and action are distinct memory functions.
- A good memory layer should support compounding, not just recall.
- The best architecture depends on whether the agent answers, learns, or acts.
- KV cache is only one tier of agent memory, not the whole system.
- Host memory, SSDs, and databases can absorb context when latency is less critical.
- Design choices trade speed for capacity and persistence.
- State management matters more as human supervision decreases.

## Operational Insight

Use small injected memory for immediate context, searchable session history for durable recall, and external retrieval only when the local store is no longer enough. The more layers you add, the more important it becomes to define what gets promoted and what gets dropped.

## Related Topics

- agent-maintained-knowledge-bases
- knowledge-layer-architecture
- context-compaction
- agent-runtime-architecture-for-voice
- retrieval-augmented-generation
- llm-wiki
- agentic-workflows
- answer-inference-vs-agentic-inference

## Evidence / supporting sources

### Hermes Agent: The Open-Source AI Agent That Actually Remembers What It Learned Yesterday (2026-04-14)

- Agent memory works best when different kinds of information are stored at different layers with different latency and recall tradeoffs. Short injected notes can hold the most important active facts, searchable session history can hold deep context, and optional external retrieval can extend beyond a single machine. This layered structure reduces prompt bloat while still preserving useful history. It also creates clear choices about what should be fast, what should be searchable, and what should be externalized. (`54c989dbd852` · neutral · knowledge_summary; [[sources/hermes-agent-the-open-source-ai-agent-that-actually-remembers-what-it-learned-yesterday-01kqkyhgefymbv50vnchz4b8w0|Hermes Agent: The Open-Source AI Agent That Actually Remembers What It Learned Yesterday]])
- Use small injected memory for immediate context, searchable session history for durable recall, and external retrieval only when the local store is no longer enough. The more layers you add, the more important it becomes to define what gets promoted and what gets dropped. (`da21f67554c5` · neutral · operational_insight; [[sources/hermes-agent-the-open-source-ai-agent-that-actually-remembers-what-it-learned-yesterday-01kqkyhgefymbv50vnchz4b8w0|Hermes Agent: The Open-Source AI Agent That Actually Remembers What It Learned Yesterday]])
- This is durable because production agents rarely need one undifferentiated memory bucket; they need tiers for active context, account or user profile data, historical recall, and long-horizon retrieval. The design maps well to assistants, chatbots, and service automation systems where latency, recall quality, and state management all matter. (`9f458b1e3a25` · neutral · relevance_note; [[sources/hermes-agent-the-open-source-ai-agent-that-actually-remembers-what-it-learned-yesterday-01kqkyhgefymbv50vnchz4b8w0|Hermes Agent: The Open-Source AI Agent That Actually Remembers What It Learned Yesterday]])
- Different memory layers should serve different urgency and latency needs. (`6d3523820a50` · supporting · key_points[0]; [[sources/hermes-agent-the-open-source-ai-agent-that-actually-remembers-what-it-learned-yesterday-01kqkyhgefymbv50vnchz4b8w0|Hermes Agent: The Open-Source AI Agent That Actually Remembers What It Learned Yesterday]])
- Small injected files are useful for active operational facts. (`3e954fecc4a1` · supporting · key_points[1]; [[sources/hermes-agent-the-open-source-ai-agent-that-actually-remembers-what-it-learned-yesterday-01kqkyhgefymbv50vnchz4b8w0|Hermes Agent: The Open-Source AI Agent That Actually Remembers What It Learned Yesterday]])
- Searchable historical storage is a practical middle layer for deep recall. (`5db93b723b1d` · supporting · key_points[2]; [[sources/hermes-agent-the-open-source-ai-agent-that-actually-remembers-what-it-learned-yesterday-01kqkyhgefymbv50vnchz4b8w0|Hermes Agent: The Open-Source AI Agent That Actually Remembers What It Learned Yesterday]])
- External retrieval is optional and should be justified by scale or multi-hop needs. (`e32037cca024` · supporting · key_points[3]; [[sources/hermes-agent-the-open-source-ai-agent-that-actually-remembers-what-it-learned-yesterday-01kqkyhgefymbv50vnchz4b8w0|Hermes Agent: The Open-Source AI Agent That Actually Remembers What It Learned Yesterday]])
- Hermes solves this with four tiers, stratified by how urgently the agent needs the information.
Tier 1: Agent’s Personal Notes (MEMORY.md)
stores environmental facts, project conventions, and operational lessons.
Tier 3: Session Search
archives everything across all historical sessions in a SQLite database.
Tier 4: External Memory Plugins
connect to graph-based retrieval systems like LightRAG, Supermemory, or custom vector stores. (`662d5a85088c` · supporting · supporting_snippet; [[sources/hermes-agent-the-open-source-ai-agent-that-actually-remembers-what-it-learned-yesterday-01kqkyhgefymbv50vnchz4b8w0|Hermes Agent: The Open-Source AI Agent That Actually Remembers What It Learned Yesterday]])

### RAG, LLM Wiki, or Gbrain? How Your Agent Remembers Changes Everything (2026-04-27)

- Agent memory architecture is the design of how an agent retains, compiles, and reuses information across sessions and tasks. A useful architecture separates ephemeral context from durable knowledge so the agent can avoid re-reading the same material from scratch every time. In practice, this can mean a retrieval layer for raw document access, a synthesis layer for persistent knowledge, and an action layer for triggers and workflows. The main design question is not whether memory exists, but what kind of work the memory is supposed to support. Systems that blur these roles tend to suffer from repeated computation, weak compounding, or poor automation hooks. (`7c8f14178393` · neutral · knowledge_summary; [[sources/rag-llm-wiki-or-gbrain-how-your-agent-remembers-changes-everything-01kqkvj2z9yv69c235tfg6b2gk|RAG, LLM Wiki, or Gbrain? How Your Agent Remembers Changes Everything]])
- Choose the memory layer around the job: retrieve answers, compound knowledge, or trigger actions. That separation helps avoid trying to make one mechanism solve scale, learning, and autonomy at once. (`eb2992a86c16` · neutral · operational_insight; [[sources/rag-llm-wiki-or-gbrain-how-your-agent-remembers-changes-everything-01kqkvj2z9yv69c235tfg6b2gk|RAG, LLM Wiki, or Gbrain? How Your Agent Remembers Changes Everything]])
- As of 2026-04-27, this abstraction is useful for designing chatbots, research agents, and service workflows because it separates what should be fetched, what should be written back, and what should be executed. That makes it easier to reason about latency, auditability, and long-running behavior in production agent systems. (`9bd2fff9984b` · neutral · relevance_note; [[sources/rag-llm-wiki-or-gbrain-how-your-agent-remembers-changes-everything-01kqkvj2z9yv69c235tfg6b2gk|RAG, LLM Wiki, or Gbrain? How Your Agent Remembers Changes Everything]])
- Context windows are temporary; durable memory needs a separate architecture. (`7f7f87295503` · supporting · key_points[0]; [[sources/rag-llm-wiki-or-gbrain-how-your-agent-remembers-changes-everything-01kqkvj2z9yv69c235tfg6b2gk|RAG, LLM Wiki, or Gbrain? How Your Agent Remembers Changes Everything]])
- Retrieval, synthesis, and action are distinct memory functions. (`d505722856f4` · supporting · key_points[1]; [[sources/rag-llm-wiki-or-gbrain-how-your-agent-remembers-changes-everything-01kqkvj2z9yv69c235tfg6b2gk|RAG, LLM Wiki, or Gbrain? How Your Agent Remembers Changes Everything]])
- A good memory layer should support compounding, not just recall. (`f5488c3dfcec` · supporting · key_points[2]; [[sources/rag-llm-wiki-or-gbrain-how-your-agent-remembers-changes-everything-01kqkvj2z9yv69c235tfg6b2gk|RAG, LLM Wiki, or Gbrain? How Your Agent Remembers Changes Everything]])
- The best architecture depends on whether the agent answers, learns, or acts. (`0a7d6ac1f8a7` · supporting · key_points[3]; [[sources/rag-llm-wiki-or-gbrain-how-your-agent-remembers-changes-everything-01kqkvj2z9yv69c235tfg6b2gk|RAG, LLM Wiki, or Gbrain? How Your Agent Remembers Changes Everything]])
- "Three patterns. Three trade-offs. One decision framework." (`6dff6086addf` · supporting · supporting_snippet; [[sources/rag-llm-wiki-or-gbrain-how-your-agent-remembers-changes-everything-01kqkvj2z9yv69c235tfg6b2gk|RAG, LLM Wiki, or Gbrain? How Your Agent Remembers Changes Everything]])

### The Agent Wars: Why I’m Trading my OpenClaw Setup for Hermes (2026-04-21)

- Agent memory architecture is the design of how an AI agent stores, retrieves, and updates information across sessions so repeated work becomes easier. A useful architecture distinguishes between short-lived working context and durable memory that survives across tasks. Strong implementations also make memory legible enough that users can inspect, compact, or correct it when it fragments. In practice, memory design shapes whether an agent feels like a persistent assistant or a brittle prompt loop. (`78d9de7b1492` · neutral · knowledge_summary; [[sources/the-agent-wars-why-i-m-trading-my-openclaw-setup-for-hermes-01krbnd5x8h4xphg9ga77n8hkw|The Agent Wars: Why I’m Trading my OpenClaw Setup for Hermes]])
- For reusable agents, memory should be treated as a first-class subsystem with persistence, visibility, and compaction controls. If memory cannot be inspected or corrected, it may accumulate fragmentation faster than it improves performance. (`f62ec4769eed` · neutral · operational_insight; [[sources/the-agent-wars-why-i-m-trading-my-openclaw-setup-for-hermes-01krbnd5x8h4xphg9ga77n8hkw|The Agent Wars: Why I’m Trading my OpenClaw Setup for Hermes]])
- Agent memory architecture matters whenever a system is expected to maintain continuity across sessions, users, or workflows. It is especially relevant for personal agents, internal copilots, and service automation systems that need durable preferences, task history, or reusable procedures. (`889eea242791` · neutral · relevance_note; [[sources/the-agent-wars-why-i-m-trading-my-openclaw-setup-for-hermes-01krbnd5x8h4xphg9ga77n8hkw|The Agent Wars: Why I’m Trading my OpenClaw Setup for Hermes]])
- Durable memory is only useful if it stays coherent across edits and repeated runs. (`dc9013f4ebbc` · supporting · key_points[0]; [[sources/the-agent-wars-why-i-m-trading-my-openclaw-setup-for-hermes-01krbnd5x8h4xphg9ga77n8hkw|The Agent Wars: Why I’m Trading my OpenClaw Setup for Hermes]])
- Users need some way to inspect or compact memory when the stored context becomes fragmented. (`795865196f32` · supporting · key_points[1]; [[sources/the-agent-wars-why-i-m-trading-my-openclaw-setup-for-hermes-01krbnd5x8h4xphg9ga77n8hkw|The Agent Wars: Why I’m Trading my OpenClaw Setup for Hermes]])
- A system that saves successful workflows as reusable skills can shift effort from re-prompting to retrieval and execution. (`8232bb750115` · supporting · key_points[2]; [[sources/the-agent-wars-why-i-m-trading-my-openclaw-setup-for-hermes-01krbnd5x8h4xphg9ga77n8hkw|The Agent Wars: Why I’m Trading my OpenClaw Setup for Hermes]])
- Memory quality is operational, not cosmetic; if the agent forgets identities or prior work, trust drops fast. (`41eed0b0aa62` · supporting · key_points[3]; [[sources/the-agent-wars-why-i-m-trading-my-openclaw-setup-for-hermes-01krbnd5x8h4xphg9ga77n8hkw|The Agent Wars: Why I’m Trading my OpenClaw Setup for Hermes]])
- "OpenClaw forgets. My endless hours customizing it just breaks other things. My custom “skills” would vanish, or the memory would get so fragmented that the agent forgot who I was by Tuesday." (`18a43206a90d` · supporting · supporting_snippet; [[sources/the-agent-wars-why-i-m-trading-my-openclaw-setup-for-hermes-01krbnd5x8h4xphg9ga77n8hkw|The Agent Wars: Why I’m Trading my OpenClaw Setup for Hermes]])

### The Inference Shift (2026-05-11)

- Autonomous systems often depend on a layered memory hierarchy rather than a single model context window. Active working memory may live in the KV cache, but longer-lived context can spill into host memory, SSDs, databases, logs, embeddings, and object stores. The practical design problem is deciding which information stays close to the model and which is stored cheaply elsewhere without breaking task continuity. This becomes especially important when agents must resume work, use tools, or maintain state over long horizons. (`6cd9aa88ad8e` · neutral · knowledge_summary; [[sources/the-inference-shift-01krv8c6tf3rv57w8qyesagyzp|The Inference Shift]])
- For long-running agents, treat memory as infrastructure, not as a prompt-size problem. The main engineering question is how to preserve useful state across layers while accepting that not all context needs to be on the fastest memory tier. (`a3584de21d79` · neutral · operational_insight; [[sources/the-inference-shift-01krv8c6tf3rv57w8qyesagyzp|The Inference Shift]])
- This is directly relevant to conversational AI and service automation because practical agents need durable context across turns, sessions, and tool calls. Memory architecture determines whether an assistant can resume work, avoid repeating questions, and operate over long workflows without forcing everything into a single prompt. As of 2026-05-11, this is a useful abstraction for building production agents that need persistence without paying for maximal accelerator speed everywhere. (`47c21e06fff2` · neutral · relevance_note; [[sources/the-inference-shift-01krv8c6tf3rv57w8qyesagyzp|The Inference Shift]])
- KV cache is only one tier of agent memory, not the whole system. (`7e7712127fde` · supporting · key_points[0]; [[sources/the-inference-shift-01krv8c6tf3rv57w8qyesagyzp|The Inference Shift]])
- Host memory, SSDs, and databases can absorb context when latency is less critical. (`fbcee76fdc94` · supporting · key_points[1]; [[sources/the-inference-shift-01krv8c6tf3rv57w8qyesagyzp|The Inference Shift]])
- Design choices trade speed for capacity and persistence. (`b96aabb2f96a` · supporting · key_points[2]; [[sources/the-inference-shift-01krv8c6tf3rv57w8qyesagyzp|The Inference Shift]])
- State management matters more as human supervision decreases. (`63b5a1d294d0` · supporting · key_points[3]; [[sources/the-inference-shift-01krv8c6tf3rv57w8qyesagyzp|The Inference Shift]])
- Some of that will live as active KV cache; some will live in host memory or SSDs; much of it will live in databases, logs, embeddings, and object stores. The important point is that agentic inference will be less about GPUs answering a question and more about the memory hierarchy wrapped around a model. (`26869400b04a` · supporting · supporting_snippet; [[sources/the-inference-shift-01krv8c6tf3rv57w8qyesagyzp|The Inference Shift]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- agent-maintained-knowledge-bases
- agent-runtime-architecture-for-voice
- agentic-workflows
- answer-inference-vs-agentic-inference
- context-compaction
- knowledge-layer-architecture
- llm-wiki
- retrieval-augmented-generation

## Sources

- [[sources/hermes-agent-the-open-source-ai-agent-that-actually-remembers-what-it-learned-yesterday-01kqkyhgefymbv50vnchz4b8w0|Hermes Agent: The Open-Source AI Agent That Actually Remembers What It Learned Yesterday]]
- [[sources/rag-llm-wiki-or-gbrain-how-your-agent-remembers-changes-everything-01kqkvj2z9yv69c235tfg6b2gk|RAG, LLM Wiki, or Gbrain? How Your Agent Remembers Changes Everything]]
- [[sources/the-agent-wars-why-i-m-trading-my-openclaw-setup-for-hermes-01krbnd5x8h4xphg9ga77n8hkw|The Agent Wars: Why I’m Trading my OpenClaw Setup for Hermes]]
- [[sources/the-inference-shift-01krv8c6tf3rv57w8qyesagyzp|The Inference Shift]]
