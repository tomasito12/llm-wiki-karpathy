---
title: Evals should be treated as an agent harness, not just testing
slug: evals-should-be-treated-as-an-agent-harness-not-just-testing
category: insight
tags:
- agent-evals
- ai-evaluation
- test-and-verification
- verification-systems
source_id: notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f
source_title: 'Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software
  Factory Future — Simon Last & Sarah Sachs of Notion'
source_date: '2026-04-15'
month: 2026-04
evidence_count: 8
evidence_set_hash: ded6812fe0976bd2
insight_title: Evals should be treated as an agent harness, not just testing
insight_type: research_eval
confidence: high
durability_estimate: long_term
wiki_worthiness: strong_candidate
---

# Evals should be treated as an agent harness, not just testing

## Interview Insight

### Summary

Notion separates regression tests, launch-quality evals, and deliberately hard headroom evals that are expected to pass only about 30% of the time. They also describe an internal workflow where agents can help write evals, debug failures, and iterate on fixes. This makes evals part of the production system rather than a side activity.

### Why It Matters

Actionable as of 2026-04-15: teams shipping agentic systems need evaluation layers that can distinguish product readiness from frontier capability exploration. The distinction between launch-quality and headroom evals is especially reusable because it lets teams measure both safety and future model headroom without collapsing them into one metric.

### Operational Relevance

Build separate eval classes for regression, launch readiness, and frontier probing. Integrate eval writing and failure triage into the same outer loop as development so that model changes, tool changes, and prompt changes can all be validated against the right target.

### Service Automation Relevance

High. Reliable chatbots and service agents need launch-quality checks for customer-facing journeys plus harder evals for future capability planning, especially when routing, permissions, and escalation behavior can fail silently.

### Mentioned Entities

- Notion
- OpenAI

### Suggested Destinations

- topics/

### Contrarian Or Speculative Claims

- The team’s "frontier" evals are intentionally designed to pass only about 30% of the time, which is an internal headroom strategy rather than a general benchmark rule.

### Evidence Snippets

- "we have the equivalent of unit test. Regression test... Then we have... launch quality... And then what we have what we call frontier or headroom evals, where we actively wanna be at 30% pass rate."
- "our evals were saturated and we weren’t able to really give insightful feedback other than it wasn’t worse."
- "if a new model release comes out and we... maintain their own evals"

## Evidence / supporting sources

### Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion (2026-04-15)

- The team’s "frontier" evals are intentionally designed to pass only about 30% of the time, which is an internal headroom strategy rather than a general benchmark rule. (`8551d07afb48` · counter · contrarian_or_speculative_claims[0]; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])
- Build separate eval classes for regression, launch readiness, and frontier probing. Integrate eval writing and failure triage into the same outer loop as development so that model changes, tool changes, and prompt changes can all be validated against the right target. (`f3535c6592c9` · neutral · operational_relevance; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])
- High. Reliable chatbots and service agents need launch-quality checks for customer-facing journeys plus harder evals for future capability planning, especially when routing, permissions, and escalation behavior can fail silently. (`341315228a43` · neutral · service_automation_relevance; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])
- Notion separates regression tests, launch-quality evals, and deliberately hard headroom evals that are expected to pass only about 30% of the time. They also describe an internal workflow where agents can help write evals, debug failures, and iterate on fixes. This makes evals part of the production system rather than a side activity. (`4742c68bcbaf` · neutral · summary; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])
- Actionable as of 2026-04-15: teams shipping agentic systems need evaluation layers that can distinguish product readiness from frontier capability exploration. The distinction between launch-quality and headroom evals is especially reusable because it lets teams measure both safety and future model headroom without collapsing them into one metric. (`0ddc80d7be76` · neutral · why_it_matters; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])
- "we have the equivalent of unit test. Regression test... Then we have... launch quality... And then what we have what we call frontier or headroom evals, where we actively wanna be at 30% pass rate." (`8fe3bf4e3745` · supporting · evidence_snippets[0]; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])
- "our evals were saturated and we weren’t able to really give insightful feedback other than it wasn’t worse." (`2ddb417f5aae` · supporting · evidence_snippets[1]; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])
- "if a new model release comes out and we... maintain their own evals" (`5df3f9002efd` · supporting · evidence_snippets[2]; [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]])

## Source

- [[sources/notion-s-token-town-5-rebuilds-100-tools-mcp-vs-clis-and-the-software-factory-future-simon-last-sarah-sachs-of-notion-01kp78z75pbkx3sh0k25xes45f|Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion]]
