---
title: I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself
  with AI
slug: i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee
category: source
tags:
- agent-systems
- agentic
- ai-operationalization
- cli-tool
- enterprise-ai
- knowledge-systems
- local-first
- orchestration
- software-development
- workflow-automation
- workflow-design
- workflow-restructuring
source_id: i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee
author: Balu Kosuri
publication: Medium
published_date: '2026-04-07'
assessed_as_of: '2026-04-07'
ingested_at: '2026-06-05T16:14:58.183540+00:00'
canonical_url: https://medium.com/@k.balu124/i-used-karpathys-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-df968e4f5ea0
content_sha256: a1753308e8a9d5685e362ccc66c76732eecf30d770caf1eee5bc4dc4fffb902c
derived_tools:
- tools/cursor.md
- tools/obsidian.md
derived_topics:
- topics/agent-maintained-knowledge-bases.md
- topics/wiki-schema-governance.md
derived_trends:
- industry-trends/agent-maintained-documentation-pipelines.md
derived_pages:
- industry-trends/agent-maintained-documentation-pipelines.md
- tools/cursor.md
- tools/obsidian.md
- topics/agent-maintained-knowledge-bases.md
- topics/wiki-schema-governance.md
---

# I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI

This piece is about using AI to build a wiki that maintains itself. Instead of searching the same files over and over, the system reads each source once and turns it into structured pages that stay linked together. Raw documents stay untouched, while the AI owns the wiki and updates it as new material arrives. The author built the setup with Cursor and Obsidian, then packaged it into a repo others can clone. The interesting idea is simple: let AI do the boring wiki maintenance so humans can focus on finding good sources and asking better questions.

## Key insights

- The durable unit is not a chatbot answer but a persistent wiki that compounds across ingests.
- Separating raw sources from AI-owned wiki pages reduces mutation risk and makes maintenance rules explicit.
- A schema file such as CLAUDE.md can act as the control plane for page types, ingest workflow, and linting.
- The workflow relies on index and glossary pages as navigational infrastructure rather than embeddings or vector search.
- The article’s strongest claim is operational: AI is good at repetitive bookkeeping like cross-references, stale-claim cleanup, and terminology consistency.

## Derived knowledge pages

- [[industry-trends/agent-maintained-documentation-pipelines]]
- [[tools/cursor]]
- [[tools/obsidian]]
- [[topics/agent-maintained-knowledge-bases]]
- [[topics/wiki-schema-governance]]

## Why it matters

This article is useful because it shows a concrete pattern for turning scattered project documents into a maintained knowledge base instead of a pile of chat transcripts or one-off summaries. The proposed structure is operationally clear: keep originals immutable in raw/, let the AI own wiki/, and encode the rules in a schema file so the system can update itself consistently as new sources arrive. That separation is valuable for AI engineering because it makes maintenance an explicit workflow rather than an afterthought, and it gives you clear points to inspect: source summaries, glossary updates, index changes, and lint output. The idea is also durable because it is framed around workflow design, not a single model or editor feature. The repo details suggest this is meant to be copied and adapted, but the article does not provide benchmark evidence that the method outperforms alternatives. As of 2026-04-07, the piece is best read as a practical implementation pattern to try and review, not a proven standard. The closing implication is strongest for document-heavy work such as notes, transcripts, specs, and other back-office knowledge flows, where AI can handle repetitive filing and cross-linking if the human keeps supplying good sources and questions.

## Limitations / open questions

The article gives a compelling demo narrative but no quantitative evaluation of retrieval quality, maintenance cost, error rates, or time saved. It is unclear how well the approach scales beyond the author’s stated hundreds of pages, especially with conflicting sources, ambiguous terminology, or long-lived domains. Security, privacy, and permission handling are not addressed, even though the system is designed to ingest internal documents and transcripts. The article also does not explain how hallucinations are constrained when the agent generates new pages or updates existing ones. Obsidian and Cursor are treated as convenient implementation choices, but portability to other environments is not demonstrated. The suggestion to ask the AI to save good answers as analysis pages is useful, but the criteria for what should be persisted remain underspecified.

## Contradictions / unverified claims

The article presents AI as handling wiki maintenance nearly for free, but that is an intuition rather than evidence, and the risk of subtle errors may simply move from human upkeep into agent supervision. The claim that no vector database or embeddings are needed may hold for the described repository pattern, but it is not shown to generalize to larger or less structured corpora. The Memex comparison is rhetorically strong, though the article itself acknowledges that the missing piece was maintenance rather than linking; that makes the analogy useful but incomplete. The piece is promotional in tone at times, so the strongest claims should be treated as a worked example rather than a validated system design. As of 2026-04-07, it is worth experimenting with if you have document-heavy workflows, but it should be monitored and tested carefully before being trusted for high-stakes knowledge management.

## Source metadata

- Canonical URL: https://medium.com/@k.balu124/i-used-karpathys-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-df968e4f5ea0
- Raw markdown: `raw/readwise/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee.md`
- Raw HTML: `raw/readwise/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee.html`
