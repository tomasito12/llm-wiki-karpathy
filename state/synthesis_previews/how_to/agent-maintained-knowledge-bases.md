---
title: Agent-Maintained Knowledge Bases
slug: agent-maintained-knowledge-bases
entity_id: how_to:agent-maintained-knowledge-bases
category: how-to
tags:
- agent-memory
- agent-systems
- ai-engineering
- auditability
- context-engineering
- knowledge-systems
- workflow-automation
first_seen: '2026-04-21'
last_seen: '2026-05-07'
source_count: 3
evidence_count: 43
source_ids:
- building-a-complete-personal-harness-llm-wiki-developer-s-second-brain-in-obsidian-01krbnant10607tp88nmdzn55s
- give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k
- karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr
value_level: high
confidence: 0.963333
synthesis_state: synthesized
synthesis_stale: false
synthesis_input_hash: 2d3f036edb0ad439
current_input_hash: 2d3f036edb0ad439
synthesis_schema_version: 1
synthesis_prompt_version: 1
last_synthesized_at: '2026-07-08T19:50:45Z'
---

# Agent-Maintained Knowledge Bases

## Executive synthesis

The shared recommendation is a structured, agent-assisted knowledge base where raw sources stay immutable, synthesized wiki pages are generated and maintained separately, and a schema/root instruction file controls what the agent can read, write, and update. The system is meant to reduce repeated re-explanation, accumulate durable knowledge over time, and preserve provenance and contradictions instead of burying them in chat history. Across sources, the practical pattern is: ingest one source at a time, store provenance in metadata, review changes with Git or diffs, and run regular linting plus scheduled ingestion/compilation jobs. The main caveat is that the setup only stays safe if the raw/wiki boundary remains strict and humans actually review logs and lint reports; otherwise hallucinations and drift can become durable knowledge. The evidence is strong for the workflow itself, but thin on exact tool choices and on how well it scales beyond personal or small-team corpora.

## Context card

- **Use this page when:** Use this page when you want the core pattern for an agent-maintained knowledge base: immutable raw inputs, AI-written wiki outputs, explicit rules, provenance, and scheduled review.
- **Best for questions about:** How to structure an AI-maintained Obsidian or Markdown knowledge base, How to keep source material separate from generated synthesis, How to preserve provenance and auditability in a living wiki, How to set up ingestion, compilation, and linting workflows for agent-maintained notes
- **Not enough for:** A turnkey implementation with exact commands or plugin choices, Enterprise-scale knowledge management architecture, How to fine-tune prompts for a specific model or domain, A fully validated benchmark of accuracy or productivity gains
- **Strongest sources:** Building a Complete Personal Harness: LLM Wiki + Developer’s Second Brain in Obsidian, Give Your AI Unlimited Updated Context, Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over
- **Related tags:** agent-memory, agent-systems, ai-engineering, auditability, context-engineering, knowledge-systems, workflow-automation

## What to remember

- Raw is the source of truth; Wiki is the AI-maintained synthesis layer.
- Humans should read and review the wiki, but not directly write into the controlled wiki layer.
- A schema file/root instruction file is the control surface for rules, provenance, and update behavior.
- Version control, logs, and linting are not optional extras; they are part of the trust model.
- Scheduled jobs help: daily ingestion, weekly compilation, and monthly linting.
- If automation touches Raw, the whole source-of-truth guarantee breaks.

## Consensus

- Agent-maintained knowledge bases work by separating immutable raw sources from AI-generated wiki pages.
- A schema or root instruction file is needed to define folder structure, page rules, provenance, and update behavior.
- Provenance should be stored in page metadata so claims can be traced back to raw sources.
- Automation should be split into smaller jobs such as ingestion, compilation, and linting rather than asking one run to do everything.
- Logs, diffs, and lint reports are important because human review is part of keeping the system trustworthy.

## Tensions / open questions

- The sources agree on strict edit boundaries, but this creates an operational burden: the system depends on disciplined review and reliable automation, which may be hard to sustain.
- Karpathy’s source says the pattern is best for personal or team-scale corpora, so there is uncertainty about how far the approach generalizes to enterprise-scale knowledge stores.
- The workflow is described as append-only Raw plus generated Wiki, but the exact boundary and tooling are implementation choices rather than a single prescribed standard.
- Linting is emphasized, but the sources do not fully specify how to handle contradictions or stale claims beyond surfacing them for review.

## Evidence quality

- Strong convergence across 3 sources on the same workflow pattern and safety boundaries.
- Evidence is implementation-oriented and specific about folder structure, schemas, logs, and linting.
- Confidence is high for the basic pattern, but weaker on generalizing beyond personal or team-scale setups.
- The sources stress discipline and human review, so operational success depends on process quality, not just structure.

## Practical takeaway

Build it as a controlled pipeline, not a free-form chat workspace: keep Raw append-only, let the agent write only to Wiki, define rules in a root schema/instruction file, record provenance and run logs, and schedule ingestion, compilation, and linting with human review of diffs and drift.

## Evidence index

- Sources: 3
- Evidence items: 43
- Current input hash: `2d3f036edb0ad439`
- Cached input hash: `2d3f036edb0ad439`
- Last synthesized: 2026-07-08T19:50:45Z
- Synthesis status: `fresh`

## Related pages

- [[how-to/two-step-document-ingestion|Two-Step Document Ingestion]]
- [[how-to/claude-skills-setup|Claude Skills Setup]]
- [[how-to/knowledge-base-ingestion-pipeline|Knowledge Base Ingestion Pipeline]]
- [[how-to/commit-driven-documentation-sync|Commit-Driven Documentation Sync]]

## Sources

- [[sources/building-a-complete-personal-harness-llm-wiki-developer-s-second-brain-in-obsidian-01krbnant10607tp88nmdzn55s|Building a Complete Personal Harness: LLM Wiki + Developer’s Second Brain in Obsidian]]
- [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]]
- [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]]
