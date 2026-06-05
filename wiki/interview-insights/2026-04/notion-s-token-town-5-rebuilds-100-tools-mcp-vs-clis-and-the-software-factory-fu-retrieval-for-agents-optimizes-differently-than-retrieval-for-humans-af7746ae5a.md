---
title: Retrieval for agents optimizes differently than retrieval for humans
slug: retrieval-for-agents-optimizes-differently-than-retrieval-for-humans
category: insight
tags:
- retrieval-systems
- knowledge-systems
- enterprise-workflows
source_id: notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f
source_title: 'Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software
  Factory Future — Simon Last & Sarah Sachs of Notion'
source_date: '2026-04-15'
month: 2026-04
evidence_count: 7
evidence_set_hash: f6e01442470bc99e
insight_title: Retrieval for agents optimizes differently than retrieval for humans
insight_type: topic
confidence: high
durability_estimate: long_term
wiki_worthiness: strong_candidate
---

# Retrieval for agents optimizes differently than retrieval for humans

## Interview Insight

### Summary

Notion says agent search traffic is structurally different from human search traffic, so ranking, top-K retrieval, snippet selection, and query generation all need to be rethought. They emphasize that vector-embedding choices are less important than the broader retrieval and ranking loop for agentic queries. The implication is that agent workloads change the retrieval objective, not just the query volume.

### Why It Matters

Actionable as of 2026-04-15: products that let agents search company knowledge should not assume human search metrics will carry over. For agent-driven systems, retrieval quality must be judged by downstream task success, not just click-through or position bias.

### Operational Relevance

Rebuild retrieval pipelines around agent query generation, parallel exhaustive search, top-K relevance, and snippet quality. Treat ranking and query diversity as one system and optimize against task completion rather than human browsing behavior.

### Service Automation Relevance

Strong. Conversational service agents often need structured search over internal knowledge, and their success depends on the relevance of the retrieved context more than on traditional search UX metrics.

### Mentioned Entities

- Notion
- ElasticSearch

### Suggested Destinations

- topics/

### Evidence Snippets

- "the search load and the search traffic. Majority of it’s coming from agents, not humans."
- "top K retrieval mode matters more"
- "we don’t spend a lot of time trying to optimize what vector embedding we use anymore"

## Evidence / supporting sources

### Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion (2026-04-15)

- Rebuild retrieval pipelines around agent query generation, parallel exhaustive search, top-K relevance, and snippet quality. Treat ranking and query diversity as one system and optimize against task completion rather than human browsing behavior. (`b177935aae8c` · neutral · operational_relevance; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])
- Strong. Conversational service agents often need structured search over internal knowledge, and their success depends on the relevance of the retrieved context more than on traditional search UX metrics. (`62f4454cfcea` · neutral · service_automation_relevance; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])
- Notion says agent search traffic is structurally different from human search traffic, so ranking, top-K retrieval, snippet selection, and query generation all need to be rethought. They emphasize that vector-embedding choices are less important than the broader retrieval and ranking loop for agentic queries. The implication is that agent workloads change the retrieval objective, not just the query volume. (`4c71c0895a34` · neutral · summary; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])
- Actionable as of 2026-04-15: products that let agents search company knowledge should not assume human search metrics will carry over. For agent-driven systems, retrieval quality must be judged by downstream task success, not just click-through or position bias. (`b7551124c8cb` · neutral · why_it_matters; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])
- "the search load and the search traffic. Majority of it’s coming from agents, not humans." (`c4a250c56d3b` · supporting · evidence_snippets[0]; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])
- "top K retrieval mode matters more" (`f551d6c55f15` · supporting · evidence_snippets[1]; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])
- "we don’t spend a lot of time trying to optimize what vector embedding we use anymore" (`7118c9224ca3` · supporting · evidence_snippets[2]; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])

## Source

- [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]]
