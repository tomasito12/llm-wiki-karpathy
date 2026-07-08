---
title: Wiki Schema Governance
slug: wiki-schema-governance
entity_id: topic:wiki-schema-governance
category: topic
tags:
- agent-systems
- ai-engineering
- auditability
- context-engineering
- knowledge-systems
- orchestration
- workflow-automation
first_seen: '2026-04-04'
last_seen: '2026-05-07'
source_count: 4
evidence_count: 32
source_ids:
- give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k
- i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee
- i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769
- llm-wiki-github-01kqh081eg75gw49db3mqd9cpq
value_level: high
confidence: 0.9299999999999999
synthesis_state: stage1-placeholder
---

# Wiki Schema Governance

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Wiki schema governance is the practice of using an explicit schema document to define how an LLM should organize, update, and maintain a knowledge base. The schema specifies conventions, workflows, and page structure so the model behaves consistently across ingests and queries. This turns an LLM from a generic assistant into a disciplined maintainer with constrained responsibilities. The value is highest when the system must preserve consistency across many pages, sources, and sessions. Schema governance also creates a shared operating contract between human editors and the model.

## Examples

The source says, “A single file called CLAUDE.md. This is the instruction manual for the AI. It defines what types of pages exist, what workflow to follow when processing a new source, how to format pages, and when to check the wiki for problems.”

## Key Points

- An explicit schema reduces drift across sessions by making conventions machine-readable and reviewable.
- The schema can encode ingest, query, and maintenance workflows rather than just file formats.
- Human and model responsibilities become easier to separate when the schema is the shared operating manual.
- A schema can define page types, ingest steps, query behavior, and lint checks.
- Editing the schema is the recommended way to adapt the system to a new domain.
- A governed schema helps the AI decide what to create versus what to update.
- Page types and naming conventions should be explicit, not implied.
- The schema should be refined after a few ingests when real failure modes appear.
- Lint rules are part of governance, not an optional cleanup step.
- The model will follow the schema, so unclear schemas produce inconsistent pages.
- Put operating rules in the workspace itself rather than only in a prompt.
- Define read order so active context is loaded before deeper indexes or archives.
- Use schema-level rules to prevent writes to source-of-truth folders.
- Encode prompting defaults so each new session starts from the same behavioral baseline.

## Operational Insight

Define the schema as a living control plane for ingestion, query answering, and linting. That makes the workflow repeatable and gives humans a place to steer behavior without rewriting prompts from scratch every session.

## Evidence / supporting sources

### Give Your AI Unlimited Updated Context (2026-05-07)

- Wiki schema governance is the practice of encoding operating rules, read order, folder structure, and update boundaries in a machine-readable or model-readable schema file. It turns a loose collection of markdown files into a system with explicit behavior. The schema can define what the model should read first, what it must never edit, and how it should behave at session start. This matters because the assistant needs governance before it needs more context. (`7a82ad228dc8` · neutral · knowledge_summary; [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]])
- If an AI is expected to maintain a knowledge workspace, policy should live beside the files it governs. The schema file becomes the contract that keeps read order, mutation rules, and session behavior consistent across runs. (`0e88a2491511` · neutral · operational_insight; [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]])
- This is useful anywhere an AI agent operates over files, notes, tickets, or support artifacts and needs predictable behavior. Clear schema governance reduces accidental writes, inconsistent prompts, and brittle setup instructions hidden in chat history. (`417c76c3f24c` · neutral · relevance_note; [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]])
- Put operating rules in the workspace itself rather than only in a prompt. (`3a0d84fcf090` · supporting · key_points[0]; [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]])
- Define read order so active context is loaded before deeper indexes or archives. (`1e95fa174909` · supporting · key_points[1]; [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]])
- Use schema-level rules to prevent writes to source-of-truth folders. (`5fa372ce5207` · supporting · key_points[2]; [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]])
- Encode prompting defaults so each new session starts from the same behavioral baseline. (`4ad35385de7c` · supporting · key_points[3]; [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]])
- The schema file sits at the root and tells any AI how the vault is organised, what to read first, and what the operating rules are. (`9651bb355845` · supporting · supporting_snippet; [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]])

### I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI (2026-04-07)

- The source says, “A single file called CLAUDE.md. This is the instruction manual for the AI. It defines what types of pages exist, what workflow to follow when processing a new source, how to format pages, and when to check the wiki for problems.” (`1ae793ec0979` · neutral · examples; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]])
- Wiki schema governance is the practice of using an explicit instruction file or schema to define how an AI should create, update, and verify a knowledge base. It makes page types, workflows, and validation steps first-class so the agent can behave consistently across ingests. The schema acts like a policy layer for the wiki: it constrains output format, determines what gets updated, and gives humans a place to change the rules for their domain. This is especially useful when the same agent is expected to create new pages, maintain cross-links, and check for inconsistencies over time. (`6ed2d247dcc3` · neutral · knowledge_summary; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]])
- When an AI is maintaining a living knowledge base, the schema is not a side detail; it is the operating manual. Explicit rules make the system easier to inspect, adapt, and debug. (`60b42b6ed695` · neutral · operational_insight; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]])
- Schema governance matters in agentic knowledge systems because the quality of the output depends on stable rules, not just model capability. In practice, it creates a reviewable control surface for page generation, terminology consistency, and maintenance workflows. (`149c9a10508c` · neutral · relevance_note; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]])
- A schema can define page types, ingest steps, query behavior, and lint checks. (`ec70ce3a8ce5` · supporting · key_points[0]; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]])
- Editing the schema is the recommended way to adapt the system to a new domain. (`6261c5570fa5` · supporting · key_points[1]; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]])
- A governed schema helps the AI decide what to create versus what to update. (`2a4ea83ef80f` · supporting · key_points[2]; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]])
- “The schema — A single file called CLAUDE.md. This is the instruction manual for the AI.” (`f62a5921c463` · supporting · supporting_snippet; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]])

### I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me. (2026-04-19)

- The article says the CLAUDE.md file defines "what page types exist," "the naming conventions for [[wikilinks]]," and "what the lint checklist should check." (`1fb335352168` · neutral · examples; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- A schema can act as the control plane for an AI-maintained knowledge base by defining page types, naming rules, update behavior, and lint checks. When the model is allowed to write files, consistency depends on clear instructions about what pages exist and when new ones should be created. The schema itself evolves as the corpus grows, because early abstractions are often too loose. Good governance reduces drift by making the agent's editing behavior predictable and reviewable. (`b260c6b6962e` · neutral · knowledge_summary; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- The more autonomy you give the model in a file-based workflow, the more important the schema becomes. A concise but explicit schema can prevent page-style drift and make later linting far more effective. (`df6366d1c3ff` · neutral · operational_insight; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- This matters because file-writing agents need constraints if they are expected to maintain long-lived knowledge assets. Schema governance is useful anywhere an LLM edits markdown, documentation, or internal knowledge bases and the organization wants consistency over time rather than ad hoc outputs. (`b9a9233ad99d` · neutral · relevance_note; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- Page types and naming conventions should be explicit, not implied. (`c474fa05ea80` · supporting · key_points[0]; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- The schema should be refined after a few ingests when real failure modes appear. (`722751e993c4` · supporting · key_points[1]; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- Lint rules are part of governance, not an optional cleanup step. (`2009cf5f0da3` · supporting · key_points[2]; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- The model will follow the schema, so unclear schemas produce inconsistent pages. (`06a9e109b25f` · supporting · key_points[3]; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- "The schema document — CLAUDE.md — is the most important file in the system." (`3a01eb6d621a` · supporting · supporting_snippet; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])

### llm-wiki · GitHub (2026-04-04)

- Wiki schema governance is the practice of using an explicit schema document to define how an LLM should organize, update, and maintain a knowledge base. The schema specifies conventions, workflows, and page structure so the model behaves consistently across ingests and queries. This turns an LLM from a generic assistant into a disciplined maintainer with constrained responsibilities. The value is highest when the system must preserve consistency across many pages, sources, and sessions. Schema governance also creates a shared operating contract between human editors and the model. (`166e2ad8b2a4` · neutral · knowledge_summary; [[sources/llm-wiki-github-01kqh081eg75gw49db3mqd9cpq|llm-wiki · GitHub]])
- Define the schema as a living control plane for ingestion, query answering, and linting. That makes the workflow repeatable and gives humans a place to steer behavior without rewriting prompts from scratch every session. (`510d5e3fcea6` · neutral · operational_insight; [[sources/llm-wiki-github-01kqh081eg75gw49db3mqd9cpq|llm-wiki · GitHub]])
- As of 2026-04-04, schema governance is a durable design pattern for agentic knowledge work and other file-based AI systems. It is useful wherever an assistant must apply the same rules repeatedly across evolving artifacts, especially in team knowledge bases and support operations. (`a749e278eb3d` · neutral · relevance_note; [[sources/llm-wiki-github-01kqh081eg75gw49db3mqd9cpq|llm-wiki · GitHub]])
- An explicit schema reduces drift across sessions by making conventions machine-readable and reviewable. (`d9b2853f9265` · supporting · key_points[0]; [[sources/llm-wiki-github-01kqh081eg75gw49db3mqd9cpq|llm-wiki · GitHub]])
- The schema can encode ingest, query, and maintenance workflows rather than just file formats. (`6e8aeda18b40` · supporting · key_points[1]; [[sources/llm-wiki-github-01kqh081eg75gw49db3mqd9cpq|llm-wiki · GitHub]])
- Human and model responsibilities become easier to separate when the schema is the shared operating manual. (`597a1c2cffee` · supporting · key_points[2]; [[sources/llm-wiki-github-01kqh081eg75gw49db3mqd9cpq|llm-wiki · GitHub]])
- The schema — a document (e.g. CLAUDE.md for Claude Code or AGENTS.md for Codex) that tells the LLM how the wiki is structured, what the conventions are, and what workflows to follow when ingesting sources, answering questions, or maintaining the wiki. (`d0610ea5fffa` · supporting · supporting_snippet; [[sources/llm-wiki-github-01kqh081eg75gw49db3mqd9cpq|llm-wiki · GitHub]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- [[topics/agent-maintained-knowledge-bases|Agent-Maintained Knowledge Bases]]
- [[topics/procedural-knowledge-for-agents|Procedural Knowledge for Agents]]
- [[topics/llm-assisted-knowledge-compilation|LLM-Assisted Knowledge Compilation]]
- [[topics/file-native-ai-workflows|File-Native AI Workflows]]

## Sources

- [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]]
- [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]]
- [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]]
- [[sources/llm-wiki-github-01kqh081eg75gw49db3mqd9cpq|llm-wiki · GitHub]]
