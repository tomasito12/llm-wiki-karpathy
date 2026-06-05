---
title: Wiki Schema Governance
slug: wiki-schema-governance
entity_id: topic:wiki-schema-governance
category: topic
tags:
- agent-systems
- ai-engineering
- knowledge-systems
- orchestration
first_seen: '2026-04-07'
last_seen: '2026-04-19'
source_count: 2
evidence_count: 17
source_ids:
- i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee
- i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769
value_level: high
confidence: 0.9299999999999999
synthesis_state: stage1-placeholder
---

# Wiki Schema Governance

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Wiki schema governance is the practice of using an explicit instruction file or schema to define how an AI should create, update, and verify a knowledge base. It makes page types, workflows, and validation steps first-class so the agent can behave consistently across ingests. The schema acts like a policy layer for the wiki: it constrains output format, determines what gets updated, and gives humans a place to change the rules for their domain. This is especially useful when the same agent is expected to create new pages, maintain cross-links, and check for inconsistencies over time.

## Examples

The source says, “A single file called CLAUDE.md. This is the instruction manual for the AI. It defines what types of pages exist, what workflow to follow when processing a new source, how to format pages, and when to check the wiki for problems.”

## Key Points

- A schema can define page types, ingest steps, query behavior, and lint checks.
- Editing the schema is the recommended way to adapt the system to a new domain.
- A governed schema helps the AI decide what to create versus what to update.
- Page types and naming conventions should be explicit, not implied.
- The schema should be refined after a few ingests when real failure modes appear.
- Lint rules are part of governance, not an optional cleanup step.
- The model will follow the schema, so unclear schemas produce inconsistent pages.

## Operational Insight

When an AI is maintaining a living knowledge base, the schema is not a side detail; it is the operating manual. Explicit rules make the system easier to inspect, adapt, and debug.

## Related Topics

- agent-maintained-knowledge-bases
- llm-assisted-knowledge-compilation

## Evidence / supporting sources

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

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- agent-maintained-knowledge-bases
- llm-assisted-knowledge-compilation

## Sources

- [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]]
- [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]]
