---
title: LLM-Maintained Knowledge Compilation
slug: llm-maintained-knowledge-compilation
entity_id: topic:llm-maintained-knowledge-compilation
category: topic
tags:
- agent-memory
- agent-systems
- context-engineering
- knowledge-systems
- workflow-automation
- workflow-design
first_seen: '2026-04-06'
last_seen: '2026-04-27'
source_count: 2
evidence_count: 18
source_ids:
- rag-llm-wiki-or-gbrain-how-your-agent-remembers-changes-everything-01kqkvj2z9yv69c235tfg6b2gk
- why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8
value_level: high
confidence: 0.935
synthesis_state: stage1-placeholder
---

# LLM-Maintained Knowledge Compilation

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
A durable knowledge system can be built by having an LLM compile raw documents into an interlinked artifact that is maintained over time. The key shift is from asking the model to answer from scratch on every query to letting it turn sources into summaries, concept pages, backlinks, and updates that accumulate. This approach works best when the model has explicit instructions, a stable file structure, and a review loop that keeps the compiled knowledge current. It treats the knowledge base as an output of the system, not just a record of conversations.

## Examples

The source gives a concrete workflow: raw documents go into a raw/ directory, the LLM writes summaries and concept pages, and the resulting wiki is stored as markdown files. It also describes the rule that "the LLM writes and maintains all of the data of the wiki, I rarely touch it directly."

## Key Points

- Raw sources are immutable inputs; the compiled wiki is the maintained artifact.
- Incremental updates matter more than reprocessing everything from scratch.
- The system benefits from explicit instructions for ingest, query, and lint operations.
- Knowledge compounds when queries can also write back into the wiki.
- The model compiles sources once and reuses the synthesis later.
- New ingest can update multiple linked pages, not just one summary.
- Query answers can be written back as new knowledge.
- Maintenance matters because orphaned or stale pages reduce value over time.
- Scale limits appear when the source corpus becomes too large for simple markdown navigation.

## Operational Insight

Design the agent to produce durable artifacts, not just answers. If every interaction can update the knowledge base, the system compounds instead of resetting.

## Evidence / supporting sources

### RAG, LLM Wiki, or Gbrain? How Your Agent Remembers Changes Everything (2026-04-27)

- LLM-maintained knowledge compilation is an architecture in which a model reads source material, synthesizes it into structured knowledge artifacts, and updates those artifacts as new information arrives. The compiled layer is persistent and interlinked, so later queries benefit from prior synthesis instead of starting over. This approach is strongest when the source set is bounded enough for human or model maintenance to stay manageable. It is weaker when the source base grows so large that navigation, rewrite cost, and governance become difficult. The operational value comes from compounding: each ingest can improve the knowledge base rather than merely add another retrievable chunk. (`a80f87fdd778` · neutral · knowledge_summary; [[sources/rag-llm-wiki-or-gbrain-how-your-agent-remembers-changes-everything-01kqkvj2z9yv69c235tfg6b2gk|RAG, LLM Wiki, or Gbrain? How Your Agent Remembers Changes Everything]])
- Use compilation when the value lies in cross-document synthesis and repeated queries over a smaller corpus. Keep the compiled layer maintained with link checking, contradiction handling, and write-back rules so it does not decay into a pile of summaries. (`b4c098b7a5f3` · neutral · operational_insight; [[sources/rag-llm-wiki-or-gbrain-how-your-agent-remembers-changes-everything-01kqkvj2z9yv69c235tfg6b2gk|RAG, LLM Wiki, or Gbrain? How Your Agent Remembers Changes Everything]])
- As of 2026-04-27, this pattern matters wherever teams maintain research notes, policy digests, product intelligence, or internal expertise bases. It is especially relevant when a conversational system should get better over time from the same source set instead of paying the retrieval cost on every question. (`be4eb0d51ac3` · neutral · relevance_note; [[sources/rag-llm-wiki-or-gbrain-how-your-agent-remembers-changes-everything-01kqkvj2z9yv69c235tfg6b2gk|RAG, LLM Wiki, or Gbrain? How Your Agent Remembers Changes Everything]])
- The model compiles sources once and reuses the synthesis later. (`22f8ed892316` · supporting · key_points[0]; [[sources/rag-llm-wiki-or-gbrain-how-your-agent-remembers-changes-everything-01kqkvj2z9yv69c235tfg6b2gk|RAG, LLM Wiki, or Gbrain? How Your Agent Remembers Changes Everything]])
- New ingest can update multiple linked pages, not just one summary. (`b40b6b33e2ce` · supporting · key_points[1]; [[sources/rag-llm-wiki-or-gbrain-how-your-agent-remembers-changes-everything-01kqkvj2z9yv69c235tfg6b2gk|RAG, LLM Wiki, or Gbrain? How Your Agent Remembers Changes Everything]])
- Query answers can be written back as new knowledge. (`9299315ce69d` · supporting · key_points[2]; [[sources/rag-llm-wiki-or-gbrain-how-your-agent-remembers-changes-everything-01kqkvj2z9yv69c235tfg6b2gk|RAG, LLM Wiki, or Gbrain? How Your Agent Remembers Changes Everything]])
- Maintenance matters because orphaned or stale pages reduce value over time. (`4a4dff04407b` · supporting · key_points[3]; [[sources/rag-llm-wiki-or-gbrain-how-your-agent-remembers-changes-everything-01kqkvj2z9yv69c235tfg6b2gk|RAG, LLM Wiki, or Gbrain? How Your Agent Remembers Changes Everything]])
- Scale limits appear when the source corpus becomes too large for simple markdown navigation. (`6fc26672e197` · supporting · key_points[4]; [[sources/rag-llm-wiki-or-gbrain-how-your-agent-remembers-changes-everything-01kqkvj2z9yv69c235tfg6b2gk|RAG, LLM Wiki, or Gbrain? How Your Agent Remembers Changes Everything]])
- "Karpathy wants your agent to build a persistent, interlinked wiki — knowledge that grows richer with every source you feed it." (`5c19b00c71ec` · supporting · supporting_snippet; [[sources/rag-llm-wiki-or-gbrain-how-your-agent-remembers-changes-everything-01kqkvj2z9yv69c235tfg6b2gk|RAG, LLM Wiki, or Gbrain? How Your Agent Remembers Changes Everything]])

### Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge (2026-04-06)

- The source gives a concrete workflow: raw documents go into a raw/ directory, the LLM writes summaries and concept pages, and the resulting wiki is stored as markdown files. It also describes the rule that "the LLM writes and maintains all of the data of the wiki, I rarely touch it directly." (`ccf755a9f572` · neutral · examples; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])
- A durable knowledge system can be built by having an LLM compile raw documents into an interlinked artifact that is maintained over time. The key shift is from asking the model to answer from scratch on every query to letting it turn sources into summaries, concept pages, backlinks, and updates that accumulate. This approach works best when the model has explicit instructions, a stable file structure, and a review loop that keeps the compiled knowledge current. It treats the knowledge base as an output of the system, not just a record of conversations. (`3cf6c5bf17c4` · neutral · knowledge_summary; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])
- Design the agent to produce durable artifacts, not just answers. If every interaction can update the knowledge base, the system compounds instead of resetting. (`20dd154b079c` · neutral · operational_insight; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])
- This pattern matters for AI engineering because many document and agent systems fail to accumulate structure. A maintained compilation layer can improve search, reuse, and consistency across personal knowledge bases, research workflows, and internal documentation systems. (`938b1aaeeb7d` · neutral · relevance_note; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])
- Raw sources are immutable inputs; the compiled wiki is the maintained artifact. (`cc14b31288f0` · supporting · key_points[0]; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])
- Incremental updates matter more than reprocessing everything from scratch. (`20c51471175f` · supporting · key_points[1]; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])
- The system benefits from explicit instructions for ingest, query, and lint operations. (`1afa1c6f49be` · supporting · key_points[2]; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])
- Knowledge compounds when queries can also write back into the wiki. (`4181b3d687d0` · supporting · key_points[3]; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])
- The LLM Wiki is a design pattern that inserts an LLM-maintained, compounding layer of markdown files between you and your raw source materials. (`25fc35c27731` · supporting · supporting_snippet; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- [[topics/agent-memory-architecture|Agent Memory Architecture]]

## Sources

- [[sources/rag-llm-wiki-or-gbrain-how-your-agent-remembers-changes-everything-01kqkvj2z9yv69c235tfg6b2gk|RAG, LLM Wiki, or Gbrain? How Your Agent Remembers Changes Everything]]
- [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]]
