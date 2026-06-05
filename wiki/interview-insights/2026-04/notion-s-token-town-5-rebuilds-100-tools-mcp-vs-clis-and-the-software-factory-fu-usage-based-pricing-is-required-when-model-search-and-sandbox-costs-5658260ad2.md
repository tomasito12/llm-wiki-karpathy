---
title: Usage-based pricing is required when model, search, and sandbox costs vary
  by task
slug: usage-based-pricing-is-required-when-model-search-and-sandbox-costs-vary-by-task
category: insight
tags:
- ai-economics
- infrastructure-economics
- enterprise-ai
source_id: notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f
source_title: 'Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software
  Factory Future — Simon Last & Sarah Sachs of Notion'
source_date: '2026-04-15'
month: 2026-04
evidence_count: 7
evidence_set_hash: 6f30f41d2de4ce05
insight_title: Usage-based pricing is required when model, search, and sandbox costs
  vary by task
insight_type: topic
confidence: high
durability_estimate: long_term
wiki_worthiness: strong_candidate
---

# Usage-based pricing is required when model, search, and sandbox costs vary by task

## Interview Insight

### Summary

Notion explains that credits are an abstraction above raw tokens because the real cost varies by model, serving tier, web search, and future sandboxing. They also argue that some tasks should use deterministic code paths instead of repeated language-model calls, both for cost control and for better predictability. Pricing therefore becomes a product design problem tied to capability choice.

### Why It Matters

Actionable as of 2026-04-15: agent products with heterogeneous runtime costs cannot safely price every action as if it were a uniform token stream. This insight is especially useful for enterprise AI products that mix search, tool execution, and asynchronous agents under one SKU.

### Operational Relevance

Separate low-cost deterministic tasks from expensive agentic tasks where possible, and surface cost-to-capability tradeoffs in the UI. Use pricing abstractions that can handle model choice, search, and execution environments without making the cheapest path the default for everything.

### Service Automation Relevance

Medium. Support automation products will usually need to expose when a route is expensive or slow, because the best model for a task is not always the cheapest or fastest one.

### Mentioned Entities

- Notion
- Anthropic
- OpenAI

### Suggested Destinations

- topics/

### Evidence Snippets

- "the credits and payment structures associated with the token usage"
- "if we were to host sandboxes, those are priced differently"
- "if every single autofill action was an agent running on Opus on every single database sell, it would be billions of dollars"

## Evidence / supporting sources

### Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion (2026-04-15)

- Separate low-cost deterministic tasks from expensive agentic tasks where possible, and surface cost-to-capability tradeoffs in the UI. Use pricing abstractions that can handle model choice, search, and execution environments without making the cheapest path the default for everything. (`82da73eb075a` · neutral · operational_relevance; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])
- Medium. Support automation products will usually need to expose when a route is expensive or slow, because the best model for a task is not always the cheapest or fastest one. (`abc33ca66e80` · neutral · service_automation_relevance; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])
- Notion explains that credits are an abstraction above raw tokens because the real cost varies by model, serving tier, web search, and future sandboxing. They also argue that some tasks should use deterministic code paths instead of repeated language-model calls, both for cost control and for better predictability. Pricing therefore becomes a product design problem tied to capability choice. (`610cebc696e2` · neutral · summary; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])
- Actionable as of 2026-04-15: agent products with heterogeneous runtime costs cannot safely price every action as if it were a uniform token stream. This insight is especially useful for enterprise AI products that mix search, tool execution, and asynchronous agents under one SKU. (`8c2ea4f1c8c2` · neutral · why_it_matters; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])
- "the credits and payment structures associated with the token usage" (`5c1bf7e199a2` · supporting · evidence_snippets[0]; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])
- "if we were to host sandboxes, those are priced differently" (`76f8415c3f71` · supporting · evidence_snippets[1]; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])
- "if every single autofill action was an agent running on Opus on every single database sell, it would be billions of dollars" (`0132620633ca` · supporting · evidence_snippets[2]; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])

## Source

- [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]]
