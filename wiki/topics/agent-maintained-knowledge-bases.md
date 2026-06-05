---
title: Agent-Maintained Knowledge Bases
slug: agent-maintained-knowledge-bases
entity_id: topic:agent-maintained-knowledge-bases
category: topic
tags:
- agent-systems
- knowledge-systems
- workflow-design
first_seen: '2026-04-07'
last_seen: '2026-04-07'
source_count: 1
evidence_count: 9
source_ids:
- i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee
value_level: high
confidence: 0.97
synthesis_state: stage1-placeholder
---

# Agent-Maintained Knowledge Bases

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
An agent-maintained knowledge base is a file-based or document-based knowledge system where an AI is responsible for creating summaries, entity pages, cross-references, and maintenance updates. The key design choice is to separate immutable source material from AI-owned derived pages, so the agent can revise the knowledge base without mutating originals. This pattern works best when the system has explicit schema rules, logging, and periodic linting for contradictions or stale claims. The value comes from persistent bookkeeping: each new source updates a shared artifact instead of producing another isolated chat answer or one-off summary.

## Examples

The source describes a setup with a `raw/` folder for original documents and a `wiki/` folder that the AI owns, plus a `CLAUDE.md` file that defines the rules. It also says, “The AI creates and owns everything in this folder. It builds pages, maintains cross-references, keeps a glossary, and updates an index.”

## Key Points

- Keep raw sources immutable and put AI-generated outputs in a separate workspace.
- Use a schema file as the control plane for page types, workflows, and formatting rules.
- Add lint passes for contradictions, stale claims, orphan pages, and missing links.
- Index and glossary pages can work as navigation infrastructure without embedding-based search.

## Operational Insight

Treat the wiki as an artifact that compounds, not as a transcript of interactions. The AI should maintain structure, while humans supply sources and ask the right questions.

## Related Topics

- wiki-schema-governance
- knowledge-base-becomes-runtime-infrastructure

## Evidence / supporting sources

### I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI (2026-04-07)

- The source describes a setup with a `raw/` folder for original documents and a `wiki/` folder that the AI owns, plus a `CLAUDE.md` file that defines the rules. It also says, “The AI creates and owns everything in this folder. It builds pages, maintains cross-references, keeps a glossary, and updates an index.” (`ba2d3fd25dcf` · neutral · examples; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]])
- An agent-maintained knowledge base is a file-based or document-based knowledge system where an AI is responsible for creating summaries, entity pages, cross-references, and maintenance updates. The key design choice is to separate immutable source material from AI-owned derived pages, so the agent can revise the knowledge base without mutating originals. This pattern works best when the system has explicit schema rules, logging, and periodic linting for contradictions or stale claims. The value comes from persistent bookkeeping: each new source updates a shared artifact instead of producing another isolated chat answer or one-off summary. (`613f166733ca` · neutral · knowledge_summary; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]])
- Treat the wiki as an artifact that compounds, not as a transcript of interactions. The AI should maintain structure, while humans supply sources and ask the right questions. (`9b5d616a0604` · neutral · operational_insight; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]])
- This pattern matters wherever teams accumulate dense project knowledge across specs, transcripts, reports, and decisions. It reduces the odds that knowledge stays trapped in isolated files or chat history, and it gives practitioners a persistent artifact they can inspect, search, and repair. (`48830d341636` · neutral · relevance_note; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]])
- Keep raw sources immutable and put AI-generated outputs in a separate workspace. (`d62c9b1c2110` · supporting · key_points[0]; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]])
- Use a schema file as the control plane for page types, workflows, and formatting rules. (`f7471cbb152b` · supporting · key_points[1]; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]])
- Add lint passes for contradictions, stale claims, orphan pages, and missing links. (`3c16a71f15af` · supporting · key_points[2]; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]])
- Index and glossary pages can work as navigation infrastructure without embedding-based search. (`af319dd24c3f` · supporting · key_points[3]; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]])
- “LLM Wiki flips this around. Instead of searching your raw documents every time, the AI reads your documents once and builds a structured wiki from them.” (`70cf35c0d57b` · supporting · supporting_snippet; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- knowledge-base-becomes-runtime-infrastructure
- wiki-schema-governance

## Sources

- [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]]
