---
title: 'Building a Complete Personal Harness: LLM Wiki + Developer’s Second Brain
  in Obsidian'
slug: building-a-complete-personal-harness-llm-wiki-developer-s-second-brain-in-obsidian-01krbnant10607tp88nmdzn55s
category: source
tags:
- agent-systems
- agentic
- ai-engineering
- cli-tool
- coding
- infrastructure
- knowledge-systems
- local-first
- software-development
- workflow-automation
- workflow-design
- writing
source_id: building-a-complete-personal-harness-llm-wiki-developer-s-second-brain-in-obsidian-01krbnant10607tp88nmdzn55s
author: Roan Brasil Monteiro
publication: Medium
published_date: '2026-05-03'
assessed_as_of: '2026-05-03'
ingested_at: '2026-06-06T21:44:31+00:00'
canonical_url: https://medium.com/@roanmonteiro/building-a-complete-personal-harness-llm-wiki-developers-second-brain-in-obsidian-d7b61c7398ff
content_sha256: 47327d506449ee70f44e8ebc42fb8217068bb9bf9c4a0dccd411a6da3c4ab849
derived_how_to:
- how-to/agent-maintained-knowledge-bases.md
derived_tools:
- tools/claude-code.md
- tools/obsidian.md
derived_topics:
- topics/agent-workspace-layering.md
- topics/file-native-ai-workflows.md
derived_trends:
- industry-trends/ai-products-shift-from-models-to-systems.md
derived_pages:
- how-to/agent-maintained-knowledge-bases.md
- industry-trends/ai-products-shift-from-models-to-systems.md
- tools/claude-code.md
- tools/obsidian.md
- topics/agent-workspace-layering.md
- topics/file-native-ai-workflows.md
---

# Building a Complete Personal Harness: LLM Wiki + Developer’s Second Brain in Obsidian

This piece shows how to build a personal knowledge system in Obsidian that an AI agent can help maintain. The key idea is to separate raw source material from the wiki the agent writes and from your own working notes, so the system does not turn into a mess. A root instruction file tells the agent what it can edit and what it must leave alone. The article also adds skills and commands so the agent can ingest sources, write ADRs, and answer questions from the vault. The payoff is a searchable second brain that keeps growing instead of being trapped in one-off chats.

## Key insights

- Physical zone separation is the core design choice: raw is immutable, wiki is agent-owned, and dev is collaborative.
- A root CLAUDE.md file is treated as the vault’s operating policy, not just documentation.
- Starting with direct filesystem access plus official skills is presented as the most portable and debuggable path.
- Plan-before-execute gating is used to keep ingestion safe, especially when external content could carry prompt injection.
- Git is positioned as the practical rollback layer for agent-written changes, with explicit diffs before commits.

## Derived knowledge pages

- [[how-to/agent-maintained-knowledge-bases]]
- [[industry-trends/ai-products-shift-from-models-to-systems]]
- [[tools/claude-code]]
- [[tools/obsidian]]
- [[topics/agent-workspace-layering]]
- [[topics/file-native-ai-workflows]]

## Why it matters

The article is useful because it translates an abstract “AI second brain” idea into a concrete operating model with clear boundaries, file layouts, and permission rules. Its main engineering contribution is not a new model or retrieval method; it is a durable workflow for letting an agent synthesize notes without corrupting source material. The three-zone design is especially reusable because it separates immutable inputs, agent-authored synthesis, and human-led working documents in a way that supports cross-linking without losing trust in provenance. The CLAUDE.md contract is also practical: it turns vault behavior into rules the agent can read every session, which is more durable than relying on ad hoc prompts. The recommendation to start with direct filesystem access is grounded in the author’s portability and debugging preferences, and the article gives specific reasons to defer MCP until Obsidian-only features are truly needed. The custom ADR and debrief skills are a helpful pattern for teams that want decision records and incident writeups to live alongside research notes rather than in a separate system. The security discussion is thin but valuable: minimal allowed-tools, human approval before writes, and git diffs are simple controls with real operational value. As of 2026-05-03, the setup is actionable for practitioners who already want a file-based AI workflow; it looks durable as a pattern, but the broader benefits are asserted from the author’s experience rather than benchmarked.

## Limitations / open questions

The article is a tutorial from one author’s workflow, so its claims are mostly implementation experience rather than comparative evaluation. The recommended path 1 vs path 2 vs path 3 trade-offs are plausible, but the piece does not provide measured data on reliability, maintenance burden, or long-term task success across approaches. The security section identifies prompt injection and destructive actions, but it does not quantify residual risk or show formal safeguards beyond git and tool allowlists. The article assumes comfort with terminal, git, Claude Code, and Obsidian, which narrows the audience. It also leaves open how well the system scales when the vault becomes large, beyond general comments about token cost and session hooks.

## Contradictions / unverified claims

The article is confident that separation plus skills and commands yields a robust knowledge infrastructure, but that conclusion is mostly argued from design logic, not evidence of comparative outcomes. The claim that direct filesystem access is the best starting point may be true for portability, yet it also gives up richer Obsidian integrations until later, so the “recommended” path is a preference rather than a demonstrated universal best practice. The setup depends heavily on the quality of custom instructions and disciplined human review; if those drift, the system could still become messy despite the zone design. The piece’s durability claim is reasonable at the level of workflow design, but it remains an engineering pattern rather than a validated guarantee.

## Source metadata

- Canonical URL: https://medium.com/@roanmonteiro/building-a-complete-personal-harness-llm-wiki-developers-second-brain-in-obsidian-d7b61c7398ff
- Raw markdown: `raw/readwise/building-a-complete-personal-harness-llm-wiki-developer-s-second-brain-in-obsidian-01krbnant10607tp88nmdzn55s.md`
- Raw HTML: `raw/readwise/building-a-complete-personal-harness-llm-wiki-developer-s-second-brain-in-obsidian-01krbnant10607tp88nmdzn55s.html`
