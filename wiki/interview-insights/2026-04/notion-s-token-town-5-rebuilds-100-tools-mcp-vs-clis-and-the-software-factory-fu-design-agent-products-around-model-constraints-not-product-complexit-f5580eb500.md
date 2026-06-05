---
title: Design agent products around model constraints, not product complexity
slug: design-agent-products-around-model-constraints-not-product-complexity
category: insight
tags:
- agent-orchestration
- context-engineering
- agent-systems
- workflow-design
source_id: notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f
source_title: 'Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software
  Factory Future — Simon Last & Sarah Sachs of Notion'
source_date: '2026-04-15'
month: 2026-04
evidence_count: 7
evidence_set_hash: d4f7f2fc856fec52
insight_title: Design agent products around model constraints, not product complexity
insight_type: orchestration
confidence: high
durability_estimate: long_term
wiki_worthiness: strong_candidate
---

# Design agent products around model constraints, not product complexity

## Interview Insight

### Summary

Notion’s team describes a repeated pattern: early agent attempts failed because they exposed too much of Notion’s internal complexity to models, used representations the model did not handle well, or depended on capabilities that were not mature enough. Their fix was to simplify the tool surface, use representations the model already understands, and add progressive disclosure so the model only sees what it needs. The underlying lesson is that agent quality depends as much on harness design as on model capability.

### Why It Matters

Actionable as of 2026-04-15: agent builders should treat tool design, prompt size, and disclosure strategy as first-class product decisions, not implementation details. This is a durable pattern for shipping reliable enterprise agents because it reduces brittleness without waiting for frontier-model gains.

### Operational Relevance

Use simple, model-native abstractions; avoid forcing the model through lossy or overly rich internal formats; and introduce tools gradually with routing or disclosure layers. This also suggests that each new tool can degrade the overall harness if added without careful gating and eval coverage.

### Service Automation Relevance

Strong. Support and workflow automation systems benefit from narrow, legible tool sets and staged disclosure, especially when agents need to operate safely in shared enterprise environments.

### Mentioned Entities

- Notion
- OpenAI
- Anthropic
- Fireworks

### Suggested Destinations

- topics/

### Evidence Snippets

- "we created this whole XML format that can losslessly mapped in notion blocks... and then we’re like, okay, well it has to be marked down. the model’s no markdown"
- "we had to make our harness implement progressive disclosure in, in a nice way."
- "really try so hard not to expose it to any complexity about your system that, that’s unnecessary."

## Evidence / supporting sources

### Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion (2026-04-15)

- Use simple, model-native abstractions; avoid forcing the model through lossy or overly rich internal formats; and introduce tools gradually with routing or disclosure layers. This also suggests that each new tool can degrade the overall harness if added without careful gating and eval coverage. (`8f5b74e1413f` · neutral · operational_relevance; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])
- Strong. Support and workflow automation systems benefit from narrow, legible tool sets and staged disclosure, especially when agents need to operate safely in shared enterprise environments. (`8f7edde77578` · neutral · service_automation_relevance; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])
- Notion’s team describes a repeated pattern: early agent attempts failed because they exposed too much of Notion’s internal complexity to models, used representations the model did not handle well, or depended on capabilities that were not mature enough. Their fix was to simplify the tool surface, use representations the model already understands, and add progressive disclosure so the model only sees what it needs. The underlying lesson is that agent quality depends as much on harness design as on model capability. (`2907a7eaf540` · neutral · summary; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])
- Actionable as of 2026-04-15: agent builders should treat tool design, prompt size, and disclosure strategy as first-class product decisions, not implementation details. This is a durable pattern for shipping reliable enterprise agents because it reduces brittleness without waiting for frontier-model gains. (`8d7b16eb3218` · neutral · why_it_matters; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])
- "we created this whole XML format that can losslessly mapped in notion blocks... and then we’re like, okay, well it has to be marked down. the model’s no markdown" (`90e296bebb01` · supporting · evidence_snippets[0]; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])
- "we had to make our harness implement progressive disclosure in, in a nice way." (`f47520ead55f` · supporting · evidence_snippets[1]; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])
- "really try so hard not to expose it to any complexity about your system that, that’s unnecessary." (`fbd08b9e909d` · supporting · evidence_snippets[2]; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])

## Source

- [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]]
