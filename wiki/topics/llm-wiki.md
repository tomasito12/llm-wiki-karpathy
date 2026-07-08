---
title: LLM Wiki
slug: llm-wiki
entity_id: topic:llm-wiki
category: topic
tags:
- agent-systems
- knowledge-systems
first_seen: '2026-04-29'
last_seen: '2026-04-29'
source_count: 1
evidence_count: 9
source_ids:
- i-found-a-full-llm-wiki-app-so-i-built-the-smaller-thing-i-actually-needed-01kqz036fj7zddpk9fppjf11va
value_level: high
confidence: 0.94
synthesis_state: stage1-placeholder
---

# LLM Wiki

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
An LLM wiki can be treated as a persistent Markdown knowledge base that an AI assistant helps maintain over time. The core pattern is to keep raw sources separate from synthesized wiki pages, use a small instruction file to guide upkeep, and let knowledge accumulate through repeated ingest and revision rather than one-off Q&A. More advanced implementations add document import, review queues, search, graph views, and compatibility with note-taking tools, but the durable lesson is that the system should fit the user’s real work and remain easy to keep using.

## Key Points

- Raw sources stay separate from the organized wiki layer.
- A purpose file gives the wiki direction and helps decide what knowledge to preserve.
- Two-step ingest improves quality by analyzing first and generating second.
- Review queues keep unresolved conflicts and draft assumptions out of automatic permanent guidance.
- A skill or instruction layer can be enough when the knowledge base already lives in Markdown.

## Operational Insight

Design the wiki as a maintained system: separate sources from synthesized pages, define purpose and operating rules, and make ingest a two-step process with review points for uncertain items. For smaller setups, a project-level skill or similar instruction layer can provide the maintenance behavior without requiring a full app.

## Evidence / supporting sources

### I Found a Full LLM Wiki App. So I Built the Smaller Thing I Actually Needed. (2026-04-29)

- An LLM wiki can be treated as a persistent Markdown knowledge base that an AI assistant helps maintain over time. The core pattern is to keep raw sources separate from synthesized wiki pages, use a small instruction file to guide upkeep, and let knowledge accumulate through repeated ingest and revision rather than one-off Q&A. More advanced implementations add document import, review queues, search, graph views, and compatibility with note-taking tools, but the durable lesson is that the system should fit the user’s real work and remain easy to keep using. (`62546e56609a` · neutral · knowledge_summary; [[sources/i-found-a-full-llm-wiki-app-so-i-built-the-smaller-thing-i-actually-needed-01kqz036fj7zddpk9fppjf11va|I Found a Full LLM Wiki App. So I Built the Smaller Thing I Actually Needed.]])
- Design the wiki as a maintained system: separate sources from synthesized pages, define purpose and operating rules, and make ingest a two-step process with review points for uncertain items. For smaller setups, a project-level skill or similar instruction layer can provide the maintenance behavior without requiring a full app. (`2a0e47acdc83` · neutral · operational_insight; [[sources/i-found-a-full-llm-wiki-app-so-i-built-the-smaller-thing-i-actually-needed-01kqz036fj7zddpk9fppjf11va|I Found a Full LLM Wiki App. So I Built the Smaller Thing I Actually Needed.]])
- This is useful anywhere people want AI-assisted note taking, living documentation, or internal knowledge bases that improve through ongoing maintenance. The main value is turning the assistant into a steward of the knowledge base while preserving provenance and human judgment. (`56d5d907d873` · neutral · relevance_note; [[sources/i-found-a-full-llm-wiki-app-so-i-built-the-smaller-thing-i-actually-needed-01kqz036fj7zddpk9fppjf11va|I Found a Full LLM Wiki App. So I Built the Smaller Thing I Actually Needed.]])
- Raw sources stay separate from the organized wiki layer. (`98430e9f6810` · supporting · key_points[0]; [[sources/i-found-a-full-llm-wiki-app-so-i-built-the-smaller-thing-i-actually-needed-01kqz036fj7zddpk9fppjf11va|I Found a Full LLM Wiki App. So I Built the Smaller Thing I Actually Needed.]])
- A purpose file gives the wiki direction and helps decide what knowledge to preserve. (`bad2fb53acfb` · supporting · key_points[1]; [[sources/i-found-a-full-llm-wiki-app-so-i-built-the-smaller-thing-i-actually-needed-01kqz036fj7zddpk9fppjf11va|I Found a Full LLM Wiki App. So I Built the Smaller Thing I Actually Needed.]])
- Two-step ingest improves quality by analyzing first and generating second. (`9fc8955511c5` · supporting · key_points[2]; [[sources/i-found-a-full-llm-wiki-app-so-i-built-the-smaller-thing-i-actually-needed-01kqz036fj7zddpk9fppjf11va|I Found a Full LLM Wiki App. So I Built the Smaller Thing I Actually Needed.]])
- Review queues keep unresolved conflicts and draft assumptions out of automatic permanent guidance. (`0d9d7c3c136b` · supporting · key_points[3]; [[sources/i-found-a-full-llm-wiki-app-so-i-built-the-smaller-thing-i-actually-needed-01kqz036fj7zddpk9fppjf11va|I Found a Full LLM Wiki App. So I Built the Smaller Thing I Actually Needed.]])
- A skill or instruction layer can be enough when the knowledge base already lives in Markdown. (`8382bf01b6e9` · supporting · key_points[4]; [[sources/i-found-a-full-llm-wiki-app-so-i-built-the-smaller-thing-i-actually-needed-01kqz036fj7zddpk9fppjf11va|I Found a Full LLM Wiki App. So I Built the Smaller Thing I Actually Needed.]])
- "Raw sources stay separate. The wiki becomes the organized layer. A small instruction file tells the AI how to keep everything tidy." (`ca8d3a6505ef` · supporting · supporting_snippet; [[sources/i-found-a-full-llm-wiki-app-so-i-built-the-smaller-thing-i-actually-needed-01kqz036fj7zddpk9fppjf11va|I Found a Full LLM Wiki App. So I Built the Smaller Thing I Actually Needed.]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- [[topics/knowledge-base-becomes-runtime-infrastructure|Knowledge Base Becomes Runtime Infrastructure]]
- [[topics/provenance-tracking|Provenance Tracking]]
- [[topics/two-step-document-ingest|Two-Step Document Ingest]]

## Sources

- [[sources/i-found-a-full-llm-wiki-app-so-i-built-the-smaller-thing-i-actually-needed-01kqz036fj7zddpk9fppjf11va|I Found a Full LLM Wiki App. So I Built the Smaller Thing I Actually Needed.]]
