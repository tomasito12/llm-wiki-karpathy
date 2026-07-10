---
title: I Built a Personal AI Operating System. It Now Knows More About My Week Than
  I Do.
slug: i-built-a-personal-ai-operating-system-it-now-knows-more-about-my-week-than-i-do-01kqm0pmnw3vtap5a84xh1r9h4
category: source
tags:
- agent-memory
- agent-orchestration
- agent-systems
- developer-focused
- human-ai-collaboration
- knowledge-systems
- local-first
- low-latency
- open-source
- open-weight-model
- reasoning-model
- runtime-systems
- workflow-design
source_id: i-built-a-personal-ai-operating-system-it-now-knows-more-about-my-week-than-i-do-01kqm0pmnw3vtap5a84xh1r9h4
author: Alex E
publication: Medium
published_date: '2026-04-12'
assessed_as_of: '2026-04-12'
ingested_at: '2026-07-10T11:51:13.914631+00:00'
canonical_url: https://medium.com/towards-artificial-intelligence/i-built-a-personal-ai-operating-system-it-now-knows-more-about-my-week-than-i-do-bddad36f8934
content_sha256: a703465d127ea5f0bdf67a9780245cf626a1c86fda58475c62d9edd028f7e85a
derived_models:
- foundation-models/qwen3-30b-a3b.md
derived_tools:
- tools/ollama.md
derived_topics:
- topics/agentic-personal-knowledge-management.md
- topics/scheduler-driven-assistant-runtime.md
derived_trends:
- industry-trends/agents-move-toward-persistent-memory-backed-workflows.md
derived_pages:
- foundation-models/qwen3-30b-a3b.md
- industry-trends/agents-move-toward-persistent-memory-backed-workflows.md
- tools/ollama.md
- topics/agentic-personal-knowledge-management.md
- topics/scheduler-driven-assistant-runtime.md
---

# I Built a Personal AI Operating System. It Now Knows More About My Week Than I Do.

This is a story about building a personal AI assistant that acts more like a second brain than a chatbot. The author combines notes, email, meetings, calendar events, and even health data into one system called Cerisa. Cerisa does not just answer questions; it keeps a running model of tasks, commitments, and context, then uses that to prepare briefings and reminders before they are needed. The interesting part is the loop: conversations become memory, memory becomes action, and action gets reviewed later. It is useful as a concrete example of how local models, a database, and a scheduler can be wired together into something proactive. As of 2026-04-12, it is a practical personal-system case study rather than evidence of a general product pattern.

## Key insights

- A personal AI becomes more useful when the same structured memory feeds both interpretation and action, instead of separating extraction from execution.
- A scheduler-driven assistant can create value without waiting for prompts by preparing briefings, surfacing stale commitments, and closing the day automatically.
- Persistent state matters more than chat quality for this use case because the system is designed to remember commitments, relationships, and follow-ups across weeks.
- Keeping outbound actions in a draft-first, approval-led flow is a practical guardrail when the assistant has access to sensitive personal context.
- The strongest claim is continuity of context, not autonomy: Cerisa helps the user operate better by organizing information, not by making decisions independently.

## Derived knowledge pages

- [[foundation-models/qwen3-30b-a3b]]
- [[industry-trends/agents-move-toward-persistent-memory-backed-workflows]]
- [[tools/ollama]]
- [[topics/agentic-personal-knowledge-management]]
- [[topics/scheduler-driven-assistant-runtime]]

## Why it matters

The article is useful because it shows a concrete architecture for turning a pile of personal data sources into an operational memory layer rather than a chat interface. Cerisa is built as one FastAPI service with PostgreSQL, pgvector, local models, and a background scheduler, which makes the core design easy to reason about and reuse as an internal pattern. The key engineering move is not the model choice but the dataflow: transcripts, email, calendar entries, health signals, location, bookmarks, and research are normalized into persistent state that downstream routines can query. That gives the system a durable loop for meeting prep, task tracking, relationship context, and recurring reviews. The article also surfaces a useful product boundary: the assistant is deliberately conservative, drafting actions for approval instead of acting autonomously. That is a pragmatic shape for a personal system that touches private context and high-trust actions. The evidence is still narrow, because everything comes from one builder’s account and there is no comparative evaluation against simpler tools or alternative stacks. As of 2026-04-12, this is actionable as a design reference for a personal knowledge-and-actions system, but its broader durability should be treated as promising rather than proven.

## Limitations / open questions

The evidence is a single-person implementation story, so there is no benchmark, cost breakdown, reliability study, or comparison against simpler combinations of existing tools. Several parts are underspecified: how extraction quality is measured, how often the knowledge graph is wrong, how permissions and privacy are enforced, and how much manual maintenance the system requires. The article says transcripts can be noisy and meeting timing inference is imperfect, which suggests the operational loop depends heavily on input quality. It is also unclear how scalable the design is beyond one user, since the author explicitly says it is built for a single person and not intended as a product. The use of sensitive personal data, ambient audio, and health information raises privacy and security questions that the article does not address in depth. The value proposition is strongest for someone who wants an always-on personal chief-of-staff style system; it is less clear whether the same architecture would justify itself for less obsessive users.

## Contradictions / unverified claims

The piece presents Cerisa as more useful than a collection of normal productivity tools, but that claim is asserted from personal experience rather than tested against a controlled baseline. The author emphasizes continuity and proactive memory, yet the system still depends on imperfect transcripts, manual approvals, and heuristic inference, so the boundary between assistant and elaborate workflow is thin. Some language is playful and anthropomorphic, which makes the system feel more capable than the described mechanics strictly prove. The article also suggests a lot of engineering effort was spent to solve a very personal problem, which is impressive but not evidence of general applicability. The main skeptical reading is that the system is a highly tailored demo of an attractive architecture, not proof that most users need this level of complexity.

## Source metadata

- Canonical URL: https://medium.com/towards-artificial-intelligence/i-built-a-personal-ai-operating-system-it-now-knows-more-about-my-week-than-i-do-bddad36f8934
- Raw markdown: `raw/readwise/i-built-a-personal-ai-operating-system-it-now-knows-more-about-my-week-than-i-do-01kqm0pmnw3vtap5a84xh1r9h4.md`
- Raw HTML: `raw/readwise/i-built-a-personal-ai-operating-system-it-now-knows-more-about-my-week-than-i-do-01kqm0pmnw3vtap5a84xh1r9h4.html`
