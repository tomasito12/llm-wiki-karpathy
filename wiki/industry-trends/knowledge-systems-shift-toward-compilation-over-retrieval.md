---
title: Knowledge Systems Shift Toward Compilation Over Retrieval
slug: knowledge-systems-shift-toward-compilation-over-retrieval
entity_id: trend:knowledge-systems-shift-toward-compilation-over-retrieval
category: industry-trend
tags:
- knowledge-systems
- workflow-restructuring
first_seen: '2026-04-04'
last_seen: '2026-04-21'
source_count: 2
evidence_count: 17
source_ids:
- karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr
- llm-wiki-github-01kqh081eg75gw49db3mqd9cpq
value_level: high
confidence: 0.94
synthesis_state: stage1-placeholder
maturity: unknown
---

# Knowledge Systems Shift Toward Compilation Over Retrieval

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Knowledge systems can move from answering questions by re-reading raw sources each time to compiling a maintained synthesis layer that accumulates over time. The workflow shifts work from repeated retrieval and reassembly toward incremental curation, contradiction tracking, and page maintenance. This can reduce repeated synthesis cost when the corpus is growing and questions require cross-source integration. The pattern is strongest where the real bottleneck is not reading once, but keeping the synthesized view current.

## Supporting Data Points

- The wiki is described as a 'persistent, compounding artifact.'
- Contradictions are flagged and synthesis is kept current rather than re-derived on every query.
- Answers from queries can be filed back into the wiki as new pages.
- The article says a single research paper might touch 10-15 wiki pages in one ingestion pass.
- It says queries run against pre-compiled wiki pages rather than raw chunks.
- It notes the pattern is designed for personal and team-scale knowledge, not enterprise-scale.
- It highlights provenance tracking and linting as required maintenance layers.

## Time sensitivity

Actionable as of 2026-04-04; the observation is architectural rather than time-sensitive, but its practical value depends on maintaining the corpus as it grows.

## Uncertainty / maturity

The source gives a coherent argument, but no measured comparison against retrieval-first systems, so the claimed advantage is plausible rather than proven.

## Evidence / supporting sources

### Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over (2026-04-21)

- Some AI knowledge workflows are moving from query-time retrieval toward ingestion-time compilation. In this pattern, the system integrates sources into a maintained knowledge base first, then answers later questions from the compiled structure rather than reassembling context fragments each time. The operational consequence is more durable accumulated knowledge, but also higher ingestion cost and stronger dependence on provenance and linting. (`7bd5d1206269` · neutral · trend_description; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- The source explicitly argues that the useful pattern is to "stop making the model retrieve knowledge at query time, and start making it compile knowledge once into a structured wiki that compounds over time." (`d8fab449a89e` · supporting · evidence_from_source; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- The article says a single research paper might touch 10-15 wiki pages in one ingestion pass. (`93126850d2dd` · supporting · supporting_data_points[0]; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- It says queries run against pre-compiled wiki pages rather than raw chunks. (`8e9453db4c6b` · supporting · supporting_data_points[1]; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- It notes the pattern is designed for personal and team-scale knowledge, not enterprise-scale. (`8fc6845ef206` · supporting · supporting_data_points[2]; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- It highlights provenance tracking and linting as required maintenance layers. (`733960c180b0` · supporting · supporting_data_points[3]; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- "stop making the model retrieve knowledge at query time, and start making it compile knowledge once into a structured wiki that compounds over time." (`f3dcdba8c0aa` · supporting · supporting_snippet; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- Actionable as of 2026-04-21 for bounded personal or team-scale corpora; less compelling where freshness, scale, or immediate retrieval still dominate. (`80ddcc4612a6` · uncertainty · time_sensitivity; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- The evidence is architectural and anecdotal rather than benchmarked, so it is not yet clear how often this approach outperforms simpler retrieval workflows in practice. (`ffb892877e7d` · uncertainty · uncertainty_note; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])

### llm-wiki · GitHub (2026-04-04)

- Knowledge systems can move from answering questions by re-reading raw sources each time to compiling a maintained synthesis layer that accumulates over time. The workflow shifts work from repeated retrieval and reassembly toward incremental curation, contradiction tracking, and page maintenance. This can reduce repeated synthesis cost when the corpus is growing and questions require cross-source integration. The pattern is strongest where the real bottleneck is not reading once, but keeping the synthesized view current. (`152e8e7e1abe` · neutral · trend_description; [[sources/llm-wiki-github-01kqh081eg75gw49db3mqd9cpq|llm-wiki · GitHub]])
- The source contrasts pure RAG with a persistent wiki and explicitly frames the wiki as a compounding artifact that gets updated when new sources arrive. (`a2bbfe84a85c` · supporting · evidence_from_source; [[sources/llm-wiki-github-01kqh081eg75gw49db3mqd9cpq|llm-wiki · GitHub]])
- The wiki is described as a 'persistent, compounding artifact.' (`7d1cac0f3504` · supporting · supporting_data_points[0]; [[sources/llm-wiki-github-01kqh081eg75gw49db3mqd9cpq|llm-wiki · GitHub]])
- Contradictions are flagged and synthesis is kept current rather than re-derived on every query. (`69b17a598922` · supporting · supporting_data_points[1]; [[sources/llm-wiki-github-01kqh081eg75gw49db3mqd9cpq|llm-wiki · GitHub]])
- Answers from queries can be filed back into the wiki as new pages. (`2b439c754490` · supporting · supporting_data_points[2]; [[sources/llm-wiki-github-01kqh081eg75gw49db3mqd9cpq|llm-wiki · GitHub]])
- Instead of just retrieving from raw documents at query time, the LLM incrementally builds and maintains a persistent wiki — a structured, interlinked collection of markdown files that sits between you and the raw sources. (`2e2db2988cff` · supporting · supporting_snippet; [[sources/llm-wiki-github-01kqh081eg75gw49db3mqd9cpq|llm-wiki · GitHub]])
- Actionable as of 2026-04-04; the observation is architectural rather than time-sensitive, but its practical value depends on maintaining the corpus as it grows. (`fb8cd0fd63b9` · uncertainty · time_sensitivity; [[sources/llm-wiki-github-01kqh081eg75gw49db3mqd9cpq|llm-wiki · GitHub]])
- The source gives a coherent argument, but no measured comparison against retrieval-first systems, so the claimed advantage is plausible rather than proven. (`2e4b9a1cb806` · uncertainty · uncertainty_note; [[sources/llm-wiki-github-01kqh081eg75gw49db3mqd9cpq|llm-wiki · GitHub]])

## Contradictions / tensions

- Actionable as of 2026-04-04; the observation is architectural rather than time-sensitive, but its practical value depends on maintaining the corpus as it grows. (uncertainty; [[sources/llm-wiki-github-01kqh081eg75gw49db3mqd9cpq|llm-wiki · GitHub]])
- The source gives a coherent argument, but no measured comparison against retrieval-first systems, so the claimed advantage is plausible rather than proven. (uncertainty; [[sources/llm-wiki-github-01kqh081eg75gw49db3mqd9cpq|llm-wiki · GitHub]])
- Actionable as of 2026-04-21 for bounded personal or team-scale corpora; less compelling where freshness, scale, or immediate retrieval still dominate. (uncertainty; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- The evidence is architectural and anecdotal rather than benchmarked, so it is not yet clear how often this approach outperforms simpler retrieval workflows in practice. (uncertainty; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])

## Related pages

- [[industry-trends/knowledge-base-becomes-runtime-infrastructure|Knowledge Base Becomes Runtime Infrastructure]]
- [[industry-trends/agent-maintained-documentation-pipelines|AI Documentation Moves Toward Agent-Maintained Pipelines]]
- [[industry-trends/workflow-restructuring-around-ai-agents|Software workflows are restructuring around durable agents]]
- [[industry-trends/knowledge-systems-shift-toward-passive-capture|Knowledge Systems Shift Toward Passive Capture]]

## Sources

- [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]]
- [[sources/llm-wiki-github-01kqh081eg75gw49db3mqd9cpq|llm-wiki · GitHub]]
