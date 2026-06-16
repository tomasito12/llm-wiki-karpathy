---
title: GBrain
slug: gbrain
entity_id: tool:gbrain
category: tool
tags:
- agentic
- memory
- open-source
- retrieval
source_count: 1
evidence_count: 14
source_ids:
- github-garrytan-gbrain-garry-s-opinionated-openclaw-brain-github-01kqh0a0ndw29gjtjmft53j486
value_level: high
confidence: 0.97
synthesis_state: stage1-placeholder
types:
- ai-infrastructure
- knowledge-management
---

# GBrain

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
GBrain is a knowledge backend for AI agents that indexes markdown repositories into searchable memory. It uses Postgres, pgvector, and hybrid search so agents can retrieve pages by exact terms and semantic meaning.

## Core Capabilities

- It indexes markdown repositories so agents can search a personal knowledge base by meaning and by exact terms.
- It supports hybrid retrieval, combining keyword search, vector search, and reranking so different query styles can succeed.
- It exposes CLI and MCP interfaces so agents can read, write, link, and traverse the brain programmatically.
- It keeps a compiled-truth-plus-timeline page model so current understanding can change without losing the evidence trail.

## Integration Ecosystem

- It works with OpenClaw agents through an install-and-skillpack workflow.
- It exposes MCP tools for clients such as Claude Code and Cursor.
- It connects to Postgres through Supabase and uses pgvector for embeddings and semantic search.
- It can ingest plain markdown repositories and Obsidian vaults via migration and import flows.

## Maturity signals

The repo presents GBrain as a production-oriented system rather than a prototype, with CLI commands, MCP tools, schema details, and installation paths. The source also describes a real deployment with thousands of pages and long-running maintenance, which is a meaningful operational signal, but it remains a single-vendor self-description rather than third-party validation. As of the source publication date, it looks like a niche but serious developer tool for agent memory workflows.

## Related Tools

- OpenClaw
- Obsidian
- Claude Code

## Strengths

- Uses a git-backed markdown repository as the source of truth, which keeps human editability while giving agents a structured memory layer.
- Combines keyword and vector retrieval with RRF fusion, which matters because exact-name lookup and semantic lookup fail in different ways.
- Supports incremental sync, so one file change can update the index without a full rescan of the corpus.
- Includes entity detection, enrichment, and backlinking in the agent workflow, which makes memory maintenance part of the operating loop rather than manual cleanup.

## Weaknesses / limitations

The source does not provide independent benchmarks, failure rates, or retrieval-quality metrics, so the real-world robustness of the search and sync stack is still mostly asserted by the author. It also depends on a fairly opinionated setup: Postgres, pgvector, embeddings, and skillpack-driven agent behavior. The operational surface is broad, so setup and maintenance will be heavier than a simple note index.

## Evidence / supporting sources

### GitHub - garrytan/gbrain: Garry's Opinionated OpenClaw Brain · GitHub (undated)

- It works with OpenClaw agents through an install-and-skillpack workflow. (`7fd21943d3e4` · neutral · integration_ecosystem[0]; [[sources/github-garrytan-gbrain-garry-s-opinionated-openclaw-brain-github-01kqh0a0ndw29gjtjmft53j486|GitHub - garrytan/gbrain: Garry's Opinionated OpenClaw Brain · GitHub]])
- It exposes MCP tools for clients such as Claude Code and Cursor. (`255009bd3e0e` · neutral · integration_ecosystem[1]; [[sources/github-garrytan-gbrain-garry-s-opinionated-openclaw-brain-github-01kqh0a0ndw29gjtjmft53j486|GitHub - garrytan/gbrain: Garry's Opinionated OpenClaw Brain · GitHub]])
- It connects to Postgres through Supabase and uses pgvector for embeddings and semantic search. (`b632e61201f9` · neutral · integration_ecosystem[2]; [[sources/github-garrytan-gbrain-garry-s-opinionated-openclaw-brain-github-01kqh0a0ndw29gjtjmft53j486|GitHub - garrytan/gbrain: Garry's Opinionated OpenClaw Brain · GitHub]])
- It can ingest plain markdown repositories and Obsidian vaults via migration and import flows. (`9f5e71cf7138` · neutral · integration_ecosystem[3]; [[sources/github-garrytan-gbrain-garry-s-opinionated-openclaw-brain-github-01kqh0a0ndw29gjtjmft53j486|GitHub - garrytan/gbrain: Garry's Opinionated OpenClaw Brain · GitHub]])
- The repo presents GBrain as a production-oriented system rather than a prototype, with CLI commands, MCP tools, schema details, and installation paths. The source also describes a real deployment with thousands of pages and long-running maintenance, which is a meaningful operational signal, but it remains a single-vendor self-description rather than third-party validation. As of the source publication date, it looks like a niche but serious developer tool for agent memory workflows. (`3042c8e78e77` · neutral · maturity_signals; [[sources/github-garrytan-gbrain-garry-s-opinionated-openclaw-brain-github-01kqh0a0ndw29gjtjmft53j486|GitHub - garrytan/gbrain: Garry's Opinionated OpenClaw Brain · GitHub]])
- GBrain fits workflows where an agent needs durable memory over people, projects, notes, and meetings. It is especially relevant for service automation and agent operations because it supports read-before-write loops, incremental sync, entity propagation, and cross-linking rather than treating each interaction as isolated chat state. The source frames it as a practical layer for long-running agents that need to keep a markdown brain current. (`bda41b32c30e` · neutral · operational_relevance; [[sources/github-garrytan-gbrain-garry-s-opinionated-openclaw-brain-github-01kqh0a0ndw29gjtjmft53j486|GitHub - garrytan/gbrain: Garry's Opinionated OpenClaw Brain · GitHub]])
- GBrain is a knowledge backend for AI agents that indexes markdown repositories into searchable memory. It uses Postgres, pgvector, and hybrid search so agents can retrieve pages by exact terms and semantic meaning. (`796f9647da0a` · neutral · short_description; [[sources/github-garrytan-gbrain-garry-s-opinionated-openclaw-brain-github-01kqh0a0ndw29gjtjmft53j486|GitHub - garrytan/gbrain: Garry's Opinionated OpenClaw Brain · GitHub]])
- - Uses a git-backed markdown repository as the source of truth, which keeps human editability while giving agents a structured memory layer.
- Combines keyword and vector retrieval with RRF fusion, which matters because exact-name lookup and semantic lookup fail in different ways.
- Supports incremental sync, so one file change can update the index without a full rescan of the corpus.
- Includes entity detection, enrichment, and backlinking in the agent workflow, which makes memory maintenance part of the operating loop rather than manual cleanup. (`86931f308229` · neutral · strengths; [[sources/github-garrytan-gbrain-garry-s-opinionated-openclaw-brain-github-01kqh0a0ndw29gjtjmft53j486|GitHub - garrytan/gbrain: Garry's Opinionated OpenClaw Brain · GitHub]])
- It indexes markdown repositories so agents can search a personal knowledge base by meaning and by exact terms. (`71ecc6b92c64` · supporting · core_capabilities[0]; [[sources/github-garrytan-gbrain-garry-s-opinionated-openclaw-brain-github-01kqh0a0ndw29gjtjmft53j486|GitHub - garrytan/gbrain: Garry's Opinionated OpenClaw Brain · GitHub]])
- It supports hybrid retrieval, combining keyword search, vector search, and reranking so different query styles can succeed. (`62899433f5e0` · supporting · core_capabilities[1]; [[sources/github-garrytan-gbrain-garry-s-opinionated-openclaw-brain-github-01kqh0a0ndw29gjtjmft53j486|GitHub - garrytan/gbrain: Garry's Opinionated OpenClaw Brain · GitHub]])
- It exposes CLI and MCP interfaces so agents can read, write, link, and traverse the brain programmatically. (`7f13a7298f34` · supporting · core_capabilities[2]; [[sources/github-garrytan-gbrain-garry-s-opinionated-openclaw-brain-github-01kqh0a0ndw29gjtjmft53j486|GitHub - garrytan/gbrain: Garry's Opinionated OpenClaw Brain · GitHub]])
- It keeps a compiled-truth-plus-timeline page model so current understanding can change without losing the evidence trail. (`6248a4132f03` · supporting · core_capabilities[3]; [[sources/github-garrytan-gbrain-garry-s-opinionated-openclaw-brain-github-01kqh0a0ndw29gjtjmft53j486|GitHub - garrytan/gbrain: Garry's Opinionated OpenClaw Brain · GitHub]])
- "GBrain is a knowledge brain for OpenClaw agents. It gives your agent a searchable, indexed memory over your markdown repos using Postgres + pgvector + hybrid search." (`efa3275b14b7` · supporting · supporting_snippet; [[sources/github-garrytan-gbrain-garry-s-opinionated-openclaw-brain-github-01kqh0a0ndw29gjtjmft53j486|GitHub - garrytan/gbrain: Garry's Opinionated OpenClaw Brain · GitHub]])
- The source does not provide independent benchmarks, failure rates, or retrieval-quality metrics, so the real-world robustness of the search and sync stack is still mostly asserted by the author. It also depends on a fairly opinionated setup: Postgres, pgvector, embeddings, and skillpack-driven agent behavior. The operational surface is broad, so setup and maintenance will be heavier than a simple note index. (`c203a4ad87cc` · uncertainty · weaknesses_limitations; [[sources/github-garrytan-gbrain-garry-s-opinionated-openclaw-brain-github-01kqh0a0ndw29gjtjmft53j486|GitHub - garrytan/gbrain: Garry's Opinionated OpenClaw Brain · GitHub]])

## Contradictions / tensions

- The source does not provide independent benchmarks, failure rates, or retrieval-quality metrics, so the real-world robustness of the search and sync stack is still mostly asserted by the author. It also depends on a fairly opinionated setup: Postgres, pgvector, embeddings, and skillpack-driven agent behavior. The operational surface is broad, so setup and maintenance will be heavier than a simple note index. (uncertainty; [[sources/github-garrytan-gbrain-garry-s-opinionated-openclaw-brain-github-01kqh0a0ndw29gjtjmft53j486|GitHub - garrytan/gbrain: Garry's Opinionated OpenClaw Brain · GitHub]])

## Related pages

- Claude Code
- Obsidian
- OpenClaw

## Sources

- [[sources/github-garrytan-gbrain-garry-s-opinionated-openclaw-brain-github-01kqh0a0ndw29gjtjmft53j486|GitHub - garrytan/gbrain: Garry's Opinionated OpenClaw Brain · GitHub]]
