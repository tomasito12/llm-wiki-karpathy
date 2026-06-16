---
title: I Stopped Taking Notes and Built a Second Brain That Maintains Itself
slug: i-stopped-taking-notes-and-built-a-second-brain-that-maintains-itself-01krbncmhejhh6y608gm2pz2gb
category: source
tags:
- agent-systems
- agentic
- ai-engineering
- ai-operationalization
- cli-tool
- coding
- context-engineering
- developer-tools
- knowledge-systems
- local-first
- memory
- open-source
- persistent-agents
- runtime-architecture
- runtime-systems
- workflow-automation
- workflow-restructuring
source_id: i-stopped-taking-notes-and-built-a-second-brain-that-maintains-itself-01krbncmhejhh6y608gm2pz2gb
author: Deyves Senger
publication: Medium
published_date: '2026-04-14'
assessed_as_of: '2026-04-14'
ingested_at: '2026-06-06T15:39:17.347374+00:00'
canonical_url: https://medium.com/@deyves.senger/i-stopped-taking-notes-and-built-a-second-brain-that-maintains-itself-80075b7643fb
content_sha256: 1b24419ba22f795c8e88497bf1a782732916a8f307513ee0ae262ab9c12048d3
derived_tools:
- tools/claude-code.md
- tools/obsidian.md
derived_topics:
- topics/agent-maintained-knowledge-bases.md
- topics/file-native-ai-workflows.md
derived_trends:
- industry-trends/agents-are-shifting-from-stateless-chat-to-memory-backed-persistent-work-loops.md
derived_pages:
- industry-trends/agents-are-shifting-from-stateless-chat-to-memory-backed-persistent-work-loops.md
- tools/claude-code.md
- tools/obsidian.md
- topics/agent-maintained-knowledge-bases.md
- topics/file-native-ai-workflows.md
---

# I Stopped Taking Notes and Built a Second Brain That Maintains Itself

This piece is about turning a personal note system into something an AI agent helps maintain. Instead of just saving notes and hoping you revisit them, the author lets Claude Code read sources, write wiki pages, and keep links consistent. The core idea comes from Andrej Karpathy: the wiki is the durable knowledge layer, while raw documents stay untouched. Obsidian is used as the file workspace, and a configuration file tells the agent how to organize everything. The result is a small personal system that compounds over time instead of turning into a graveyard of notes.

## Key insights

- The article’s central distinction is maintenance versus capture: note-taking is easy, but keeping notes cross-linked and up to date is the hard part.
- Karpathy’s LLM Wiki pattern treats the wiki as a persistent artifact that accumulates structure over time instead of re-answering from raw documents on every query.
- A file-editing agent matters more than a chatbot here because the workflow depends on reading, writing, and revising files across sessions.
- The schema in CLAUDE.md is the control surface: it defines folder structure, naming rules, and ingest behavior so the system can operate consistently.
- The author’s reported gains come from compounding context, not from model novelty: new ingestions enrich existing pages and improve later syntheses.

## Derived knowledge pages

- [[industry-trends/agents-are-shifting-from-stateless-chat-to-memory-backed-persistent-work-loops]]
- [[tools/claude-code]]
- [[tools/obsidian]]
- [[topics/agent-maintained-knowledge-bases]]
- [[topics/file-native-ai-workflows]]

## Why it matters

The piece is useful because it turns “personal knowledge base” from a static note archive into an operational workflow with explicit maintenance loops. That is a concrete design pattern: immutable raw sources, AI-owned wiki pages, schema-driven updates, query filing, and linting for integrity. For AI engineers, the durable lesson is that file-system access plus a stable instruction file can be more important than a chat interface when the goal is long-lived state. The article also gives a plausible division of labor between human and model: humans curate sources and ask questions; the agent handles summarization, cross-linking, and consistency checks. The reported scale is modest—78 pages after about five days—and the evidence is a personal implementation account, so the main value is as a working pattern rather than a benchmarked system. The claims about reduced morning context switching and easier recall are practical, but they are self-reported and not independently evaluated. As of 2026-04-14, this is actionable as a workflow pattern for people already using Obsidian and file-editing agents; it is promising, but still early and best treated as a method to test rather than a proven standard.

## Limitations / open questions

The evidence is a single-person implementation over roughly five days, so there is no benchmark for accuracy, retrieval quality, or long-term maintenance cost. The article does not quantify how often the agent makes bad links, misses contradictions, or introduces drift in summaries. Privacy and security questions are important because the workflow depends on giving an agent access to local files, meeting notes, and clipped sources. It is also unclear how well the pattern scales beyond a personal vault, especially when source volume, schema complexity, or domain ambiguity grows. The author says the first ingestions are slow, but there is no estimate of the setup burden beyond anecdotal timing.

## Contradictions / unverified claims

The article frames the system as self-maintaining, but the first few ingestions still require schema tuning and course correction, so the maintenance burden is reduced rather than eliminated. The piece leans on Karpathy’s framing and the author’s satisfaction, but provides no objective comparison against simpler note systems or search-based workflows. The claim that the agent can keep everything consistent across dozens of files is plausible, but unproven in the article beyond a short usage window. The automation story is compelling, but the practical ceiling may depend on how disciplined the schema is and how reliable the model remains across edits and sessions.

## Source metadata

- Canonical URL: https://medium.com/@deyves.senger/i-stopped-taking-notes-and-built-a-second-brain-that-maintains-itself-80075b7643fb
- Raw markdown: `raw/readwise/i-stopped-taking-notes-and-built-a-second-brain-that-maintains-itself-01krbncmhejhh6y608gm2pz2gb.md`
- Raw HTML: `raw/readwise/i-stopped-taking-notes-and-built-a-second-brain-that-maintains-itself-01krbncmhejhh6y608gm2pz2gb.html`
