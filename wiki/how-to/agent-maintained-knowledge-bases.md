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
confidence: 0.9633333333333333
synthesis_state: stage1-placeholder
---

# Agent-Maintained Knowledge Bases

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
This is a way to keep a growing pile of notes, papers, and source files from turning into disconnected chat transcripts. The problem is that ordinary question answering repeats the same synthesis work every time, so understanding never accumulates. A maintained knowledge base turns those repeated answers into structured pages that can be queried later. It also gives you a place to track provenance and contradictions instead of hiding them inside chat history.

## Caveats

This only works if provenance is maintained and linting is taken seriously. The source warns that hallucinations can become durable knowledge if they are written into the wiki and never checked. It also says the pattern is best for personal or team-scale corpora, not enterprise-scale knowledge stores.

## Implementation Steps

- Create a raw/ folder for immutable source documents and a wiki/ folder for generated pages.
- Write a schema file such as CLAUDE.md or AGENTS.md that defines page types, frontmatter, and update rules.
- Ingest one source at a time, letting the model update relevant wiki pages and create new ones as needed.
- Store provenance in page metadata so each claim can be traced back to raw sources.
- Run lint regularly to find broken links, orphan pages, missing concepts, contradictions, and stale claims.
- Use a save path for query answers that are worth promoting into the wiki as durable knowledge.
- Create a raw zone for immutable source files, a wiki zone for agent-maintained synthesis, and a dev zone for collaborative work.
- Write a root instruction file that tells the agent what it may read, write, or never touch.
- Use a planned ingest workflow that saves the original source first, then creates or updates wiki pages from it.
- Version the vault with Git and review diffs before committing changes.
- Add commands for ingesting sources and querying the vault so the workflow stays repeatable.
- Create a vault with separate Raw and Wiki folders.
- Make Raw append-only and forbid automation from editing it.
- Add a schema file at the vault root that defines folder structure, read order, and hard rules.
- Use a small hot cache file for the active threads and urgent items.
- Use a pending queue file to track new raw files before compilation.
- Use a log file to record every automated run and what it changed.
- Run daily ingestion to collect new material and refresh the hot cache.
- Run weekly compilation to synthesize raw files into structured wiki pages.
- Run monthly linting to check for stale pages, missing backlinks, contradictions, and orphaned files without auto-fixing them.

## Prerequisites

- A folder-based document store with raw source files.
- A schema file for page rules and provenance conventions.
- An agent capable of reading, editing, and linting Markdown files.
- A file-based note system such as Obsidian or another Markdown vault.
- A terminal-based agent that can read and write local files.
- Git for version control and rollback.
- A willingness to enforce edit boundaries between source material and synthesized notes.
- A file system or markdown workspace you can control.
- A scheduler or automation runner that can execute prompts on a cadence.
- A model that can read files and follow structured operating instructions.
- A discipline for keeping Raw immutable and reviewing logs or lint reports.

## Related Howtos

- two-step-document-ingestion
- agent-maintained-knowledge-bases
- claude-skills-setup
- knowledge-base-ingestion-pipeline
- commit-driven-documentation-sync
- Two-Step Document Ingestion
- Knowledge Base Ingestion Pipeline
- Wiki Schema Governance

## Evidence / supporting sources

### Building a Complete Personal Harness: LLM Wiki + Developer’s Second Brain in Obsidian (2026-05-03)

- Start by separating what the agent may edit from what it may only read. Put source material in a raw zone, synthesized pages in a wiki zone, and work-in-progress material in a collaborative dev zone. Then define the rules in a root instruction file the agent reads every session. Use Git so you can review diffs and revert mistakes. Add small commands for ingesting sources and answering questions so the agent has a repeatable workflow instead of improvising each time. (`f37467d670f6` · neutral · answer_summary; [[sources/building-a-complete-personal-harness-llm-wiki-developer-s-second-brain-in-obsidian-01krbnant10607tp88nmdzn55s|Building a Complete Personal Harness: LLM Wiki + Developer’s Second Brain in Obsidian]])
- Create a raw zone for immutable source files, a wiki zone for agent-maintained synthesis, and a dev zone for collaborative work. (`1235b2bd02f2` · neutral · implementation_steps[0]; [[sources/building-a-complete-personal-harness-llm-wiki-developer-s-second-brain-in-obsidian-01krbnant10607tp88nmdzn55s|Building a Complete Personal Harness: LLM Wiki + Developer’s Second Brain in Obsidian]])
- Write a root instruction file that tells the agent what it may read, write, or never touch. (`68568f5f0d93` · neutral · implementation_steps[1]; [[sources/building-a-complete-personal-harness-llm-wiki-developer-s-second-brain-in-obsidian-01krbnant10607tp88nmdzn55s|Building a Complete Personal Harness: LLM Wiki + Developer’s Second Brain in Obsidian]])
- Use a planned ingest workflow that saves the original source first, then creates or updates wiki pages from it. (`d27af3aa304d` · neutral · implementation_steps[2]; [[sources/building-a-complete-personal-harness-llm-wiki-developer-s-second-brain-in-obsidian-01krbnant10607tp88nmdzn55s|Building a Complete Personal Harness: LLM Wiki + Developer’s Second Brain in Obsidian]])
- Version the vault with Git and review diffs before committing changes. (`adaec7729dbf` · neutral · implementation_steps[3]; [[sources/building-a-complete-personal-harness-llm-wiki-developer-s-second-brain-in-obsidian-01krbnant10607tp88nmdzn55s|Building a Complete Personal Harness: LLM Wiki + Developer’s Second Brain in Obsidian]])
- Add commands for ingesting sources and querying the vault so the workflow stays repeatable. (`b00ea6d5d76f` · neutral · implementation_steps[4]; [[sources/building-a-complete-personal-harness-llm-wiki-developer-s-second-brain-in-obsidian-01krbnant10607tp88nmdzn55s|Building a Complete Personal Harness: LLM Wiki + Developer’s Second Brain in Obsidian]])
- A file-based note system such as Obsidian or another Markdown vault. (`f258d4af0928` · neutral · prerequisites[0]; [[sources/building-a-complete-personal-harness-llm-wiki-developer-s-second-brain-in-obsidian-01krbnant10607tp88nmdzn55s|Building a Complete Personal Harness: LLM Wiki + Developer’s Second Brain in Obsidian]])
- A terminal-based agent that can read and write local files. (`52ad9b7ae144` · neutral · prerequisites[1]; [[sources/building-a-complete-personal-harness-llm-wiki-developer-s-second-brain-in-obsidian-01krbnant10607tp88nmdzn55s|Building a Complete Personal Harness: LLM Wiki + Developer’s Second Brain in Obsidian]])
- Git for version control and rollback. (`f473c1829113` · neutral · prerequisites[2]; [[sources/building-a-complete-personal-harness-llm-wiki-developer-s-second-brain-in-obsidian-01krbnant10607tp88nmdzn55s|Building a Complete Personal Harness: LLM Wiki + Developer’s Second Brain in Obsidian]])
- A willingness to enforce edit boundaries between source material and synthesized notes. (`5c4565ade755` · neutral · prerequisites[3]; [[sources/building-a-complete-personal-harness-llm-wiki-developer-s-second-brain-in-obsidian-01krbnant10607tp88nmdzn55s|Building a Complete Personal Harness: LLM Wiki + Developer’s Second Brain in Obsidian]])
- This is a way to keep a personal knowledge system where an AI agent helps maintain the structure, but humans still control the source material and important decisions. It solves the common problem where notes, articles, and work artifacts get mixed together until the whole vault becomes hard to trust. The pattern is useful when you want search, synthesis, and cross-linking without losing provenance. It also helps when one workspace needs to hold both research notes and work decisions without turning into a mess. (`c20c3bc96205` · neutral · what_and_problem; [[sources/building-a-complete-personal-harness-llm-wiki-developer-s-second-brain-in-obsidian-01krbnant10607tp88nmdzn55s|Building a Complete Personal Harness: LLM Wiki + Developer’s Second Brain in Obsidian]])
- "The vault has three zones with strictly different rules" (`6c6ee9a65d92` · supporting · supporting_snippet; [[sources/building-a-complete-personal-harness-llm-wiki-developer-s-second-brain-in-obsidian-01krbnant10607tp88nmdzn55s|Building a Complete Personal Harness: LLM Wiki + Developer’s Second Brain in Obsidian]])
- The setup depends on disciplined boundaries and human review. If those rules drift, the vault can still become cluttered or unsafe. The source also assumes comfort with terminal, Git, and Claude Code. (`7bc5625e79f0` · uncertainty · caveats; [[sources/building-a-complete-personal-harness-llm-wiki-developer-s-second-brain-in-obsidian-01krbnant10607tp88nmdzn55s|Building a Complete Personal Harness: LLM Wiki + Developer’s Second Brain in Obsidian]])

### Give Your AI Unlimited Updated Context (2026-05-07)

- Start by separating your source material from the AI-generated layer. Put raw notes, transcripts, and documents in one folder, and make those files append-only so the source of truth stays intact. Then create a schema file that tells the model how the vault is organized, what to read first, and which rules it must follow. Use a small hot cache for active items, a queue for new raw files, and a log for every automated run. Split automation into daily ingestion, weekly compilation, and monthly linting so one job does not have to both interpret and mutate the whole system. (`1f81ead2eed9` · neutral · answer_summary; [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]])
- Create a vault with separate Raw and Wiki folders. (`18f75af3ffcf` · neutral · implementation_steps[0]; [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]])
- Make Raw append-only and forbid automation from editing it. (`728c7ea83dc1` · neutral · implementation_steps[1]; [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]])
- Add a schema file at the vault root that defines folder structure, read order, and hard rules. (`1237f9e057ed` · neutral · implementation_steps[2]; [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]])
- Use a small hot cache file for the active threads and urgent items. (`83cef68b9d13` · neutral · implementation_steps[3]; [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]])
- Use a pending queue file to track new raw files before compilation. (`512610286d17` · neutral · implementation_steps[4]; [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]])
- Use a log file to record every automated run and what it changed. (`23d799210b73` · neutral · implementation_steps[5]; [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]])
- Run daily ingestion to collect new material and refresh the hot cache. (`08002eb41675` · neutral · implementation_steps[6]; [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]])
- Run weekly compilation to synthesize raw files into structured wiki pages. (`72a376d2840c` · neutral · implementation_steps[7]; [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]])
- Run monthly linting to check for stale pages, missing backlinks, contradictions, and orphaned files without auto-fixing them. (`fdcf0d660303` · neutral · implementation_steps[8]; [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]])
- A file system or markdown workspace you can control. (`8ace46a2cc5b` · neutral · prerequisites[0]; [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]])
- A scheduler or automation runner that can execute prompts on a cadence. (`8d395c6ce0e2` · neutral · prerequisites[1]; [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]])
- A model that can read files and follow structured operating instructions. (`aaa9f6e83948` · neutral · prerequisites[2]; [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]])
- A discipline for keeping Raw immutable and reviewing logs or lint reports. (`47ce04366a3e` · neutral · prerequisites[3]; [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]])
- This is a way to keep an AI working from a living knowledge base instead of starting every chat from scratch. It solves the problem of repeated re-explanation, scattered project notes, and context that disappears when a conversation ends. The core idea is to store raw source material separately from AI-written summaries, then let the model keep the summaries updated over time. That gives the AI a persistent context layer that can be refreshed, audited, and rebuilt if needed. (`a9079a2d2a0c` · neutral · what_and_problem; [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]])
- Raw is your source of truth.
Meeting transcripts, exported Slack threads, documents pulled from wherever your work actually happens. The rule is absolute: the AI reads Raw, never edits it.
Append-only.
Wiki is what the AI builds and maintains. (`8b893d55f7d3` · supporting · supporting_snippet; [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]])
- This only works if the boundary between raw source files and generated wiki files stays strict. If automation edits Raw, the source-of-truth guarantee is broken. The workflow also depends on reliable scheduling, disciplined prompts, and someone reading the audit trail and lint reports; otherwise drift can accumulate. (`2260065694c0` · uncertainty · caveats; [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]])

### Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over (2026-04-21)

- Start by separating raw sources from generated wiki pages. Put the original material in an immutable raw folder, then let the model compile that material into Markdown pages in a wiki folder. Keep a schema file that defines page types, frontmatter, and update rules, because that is the control surface for the system. After each ingestion, review the pages the model created or changed, and run lint checks for broken links, orphan pages, missing concepts, and contradictions. If a question produces genuinely new insight, save it back into the wiki so the system compounds over time. (`5779221b43c4` · neutral · answer_summary; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- Create a raw/ folder for immutable source documents and a wiki/ folder for generated pages. (`384d70fe8bfc` · neutral · implementation_steps[0]; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- Write a schema file such as CLAUDE.md or AGENTS.md that defines page types, frontmatter, and update rules. (`44795d2f84bf` · neutral · implementation_steps[1]; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- Ingest one source at a time, letting the model update relevant wiki pages and create new ones as needed. (`e881126af6b8` · neutral · implementation_steps[2]; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- Store provenance in page metadata so each claim can be traced back to raw sources. (`32d70191e25d` · neutral · implementation_steps[3]; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- Run lint regularly to find broken links, orphan pages, missing concepts, contradictions, and stale claims. (`b0e236198be8` · neutral · implementation_steps[4]; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- Use a save path for query answers that are worth promoting into the wiki as durable knowledge. (`666f08c23cfd` · neutral · implementation_steps[5]; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- A folder-based document store with raw source files. (`1bb35ee99b96` · neutral · prerequisites[0]; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- A schema file for page rules and provenance conventions. (`278b305250aa` · neutral · prerequisites[1]; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- An agent capable of reading, editing, and linting Markdown files. (`d6def0fd1971` · neutral · prerequisites[2]; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- This is a way to keep a growing pile of notes, papers, and source files from turning into disconnected chat transcripts. The problem is that ordinary question answering repeats the same synthesis work every time, so understanding never accumulates. A maintained knowledge base turns those repeated answers into structured pages that can be queried later. It also gives you a place to track provenance and contradictions instead of hiding them inside chat history. (`153fd3904579` · neutral · what_and_problem; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- "The hard rule: humans read the wiki, humans don't write to the wiki." (`34504a6ba04e` · supporting · supporting_snippet; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- This only works if provenance is maintained and linting is taken seriously. The source warns that hallucinations can become durable knowledge if they are written into the wiki and never checked. It also says the pattern is best for personal or team-scale corpora, not enterprise-scale knowledge stores. (`a6c1494aa824` · uncertainty · caveats; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])

## Contradictions / tensions

- This only works if provenance is maintained and linting is taken seriously. The source warns that hallucinations can become durable knowledge if they are written into the wiki and never checked. It also says the pattern is best for personal or team-scale corpora, not enterprise-scale knowledge stores. (uncertainty; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- The setup depends on disciplined boundaries and human review. If those rules drift, the vault can still become cluttered or unsafe. The source also assumes comfort with terminal, Git, and Claude Code. (uncertainty; [[sources/building-a-complete-personal-harness-llm-wiki-developer-s-second-brain-in-obsidian-01krbnant10607tp88nmdzn55s|Building a Complete Personal Harness: LLM Wiki + Developer’s Second Brain in Obsidian]])
- This only works if the boundary between raw source files and generated wiki files stays strict. If automation edits Raw, the source-of-truth guarantee is broken. The workflow also depends on reliable scheduling, disciplined prompts, and someone reading the audit trail and lint reports; otherwise drift can accumulate. (uncertainty; [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]])

## Related pages

- Knowledge Base Ingestion Pipeline
- Two-Step Document Ingestion
- Wiki Schema Governance
- agent-maintained-knowledge-bases
- claude-skills-setup
- commit-driven-documentation-sync
- knowledge-base-ingestion-pipeline
- two-step-document-ingestion

## Sources

- [[sources/building-a-complete-personal-harness-llm-wiki-developer-s-second-brain-in-obsidian-01krbnant10607tp88nmdzn55s|Building a Complete Personal Harness: LLM Wiki + Developer’s Second Brain in Obsidian]]
- [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]]
- [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]]
