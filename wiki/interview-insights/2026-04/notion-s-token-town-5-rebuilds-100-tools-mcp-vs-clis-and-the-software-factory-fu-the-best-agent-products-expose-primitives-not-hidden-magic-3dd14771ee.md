---
title: The best agent products expose primitives, not hidden magic
slug: the-best-agent-products-expose-primitives-not-hidden-magic
category: insight
tags:
- agent-memory
- agent-orchestration
- knowledge-systems
- workflow-automation
source_id: notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f
source_title: 'Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software
  Factory Future — Simon Last & Sarah Sachs of Notion'
source_date: '2026-04-15'
month: 2026-04
evidence_count: 7
evidence_set_hash: b987ce1611e4b29e
insight_title: The best agent products expose primitives, not hidden magic
insight_type: orchestration
confidence: high
durability_estimate: long_term
wiki_worthiness: strong_candidate
---

# The best agent products expose primitives, not hidden magic

## Interview Insight

### Summary

Notion repeatedly frames its product as a set of primitives: pages, databases, triggers, permissions, and tools. Agents coordinate through those primitives, and memory is implemented as editable pages or databases rather than a bespoke memory subsystem. The broader design goal is to keep the system inspectable and composable for power users and operators.

### Why It Matters

This is a durable architectural pattern for enterprise AI: keep state in visible business objects instead of hiding it in opaque agent memory. That makes debugging, governance, and cross-agent coordination easier, and it fits products that already have strong data models.

### Operational Relevance

Design agent systems so agents can write to shared data structures, react to those data structures, and invoke each other through explicit interfaces. This reduces coupling and makes it easier to add manager agents, routing layers, and human inspection points.

### Service Automation Relevance

Strong. Service workflows often need shared state, handoffs, and auditability; using the same system-of-record objects for human and agent work makes escalation and review simpler.

### Mentioned Entities

- Notion

### Suggested Destinations

- topics/

### Evidence Snippets

- "memory is, is just pages and databases."
- "one agent, be writing to the database and there’s another agent that’s walked in the database"
- "we call it flippy... the main view... is the chat"

## Evidence / supporting sources

### Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion (2026-04-15)

- Design agent systems so agents can write to shared data structures, react to those data structures, and invoke each other through explicit interfaces. This reduces coupling and makes it easier to add manager agents, routing layers, and human inspection points. (`0a74b0d0d540` · neutral · operational_relevance; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])
- Strong. Service workflows often need shared state, handoffs, and auditability; using the same system-of-record objects for human and agent work makes escalation and review simpler. (`7320c1d99668` · neutral · service_automation_relevance; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])
- Notion repeatedly frames its product as a set of primitives: pages, databases, triggers, permissions, and tools. Agents coordinate through those primitives, and memory is implemented as editable pages or databases rather than a bespoke memory subsystem. The broader design goal is to keep the system inspectable and composable for power users and operators. (`8af2f1ff5efb` · neutral · summary; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])
- This is a durable architectural pattern for enterprise AI: keep state in visible business objects instead of hiding it in opaque agent memory. That makes debugging, governance, and cross-agent coordination easier, and it fits products that already have strong data models. (`d0d71fc212ca` · neutral · why_it_matters; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])
- "memory is, is just pages and databases." (`786ee17b5031` · supporting · evidence_snippets[0]; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])
- "one agent, be writing to the database and there’s another agent that’s walked in the database" (`85d4762af1e3` · supporting · evidence_snippets[1]; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])
- "we call it flippy... the main view... is the chat" (`afb3c3ab6967` · supporting · evidence_snippets[2]; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])

## Source

- [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]]
