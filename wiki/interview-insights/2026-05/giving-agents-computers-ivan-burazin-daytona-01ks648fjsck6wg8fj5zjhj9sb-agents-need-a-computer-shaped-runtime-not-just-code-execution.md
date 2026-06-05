---
title: Agents need a computer-shaped runtime, not just code execution
slug: agents-need-a-computer-shaped-runtime-not-just-code-execution
category: insight
tags:
- agent-systems
- runtime-architecture
- infrastructure
- execution-environments
source_id: giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb
source_title: Giving Agents Computers — Ivan Burazin, Daytona
source_date: '2026-05-21'
month: 2026-05
evidence_count: 7
evidence_set_hash: 69e74dccbf190378
insight_title: Agents need a computer-shaped runtime, not just code execution
insight_type: infrastructure
confidence: high
durability_estimate: long_term
wiki_worthiness: strong_candidate
---

# Agents need a computer-shaped runtime, not just code execution

## Interview Insight

### Summary

The core argument is that AI agents need a composable computer exposed through an API, not a narrow sandbox that only runs code. The required primitive includes state, fast startup, resizing, isolation, and support for different operating systems and workflows. This reframes the infrastructure problem from "run code" to "provide a usable machine for agent work."

### Why It Matters

As of 2026-05-21, this is a durable design constraint for agent infrastructure: if the workload includes long-running tasks, GUI interaction, or tool-rich workflows, a simple container is often the wrong abstraction. The interview suggests that runtime choice is a product decision, not just an ops detail, because it shapes what agents can do and how reliably they can recover from interruptions.

### Operational Relevance

Teams building agent runtimes should evaluate whether their primitive supports pause/resume, state retention, dynamic resizing, and multiple OS targets. The source argues that these features matter more than a disposable execution box when agents need to continue work across sessions or handle heterogeneous tasks.

### Service Automation Relevance

Service automation systems that only rely on API access may miss important workflows hidden behind legacy or GUI-only tools. A computer-shaped runtime can help support automation extend into systems that chatbots or voicebots cannot reach through APIs alone.

### Mentioned Entities

- Daytona
- CodeAnywhere

### Suggested Destinations

- topics/

### Contrarian Or Speculative Claims

- The market calls these sandboxes, but the source argues that term is misleading because agents need composable computers rather than disposable boxes.

### Evidence Snippets

- "what Daytona is today is essentially composable computers for AI agents"
- "They need a computer they can access through an API: something stateful enough to keep working, fast enough to spin up instantly, flexible enough to resize, isolated enough to be safe"

## Evidence / supporting sources

### Giving Agents Computers — Ivan Burazin, Daytona (2026-05-21)

- The market calls these sandboxes, but the source argues that term is misleading because agents need composable computers rather than disposable boxes. (`513e58e664c2` · counter · contrarian_or_speculative_claims[0]; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb|Giving Agents Computers — Ivan Burazin, Daytona]])
- Teams building agent runtimes should evaluate whether their primitive supports pause/resume, state retention, dynamic resizing, and multiple OS targets. The source argues that these features matter more than a disposable execution box when agents need to continue work across sessions or handle heterogeneous tasks. (`8c632a2e0400` · neutral · operational_relevance; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb|Giving Agents Computers — Ivan Burazin, Daytona]])
- Service automation systems that only rely on API access may miss important workflows hidden behind legacy or GUI-only tools. A computer-shaped runtime can help support automation extend into systems that chatbots or voicebots cannot reach through APIs alone. (`99ea50fb1b08` · neutral · service_automation_relevance; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb|Giving Agents Computers — Ivan Burazin, Daytona]])
- The core argument is that AI agents need a composable computer exposed through an API, not a narrow sandbox that only runs code. The required primitive includes state, fast startup, resizing, isolation, and support for different operating systems and workflows. This reframes the infrastructure problem from "run code" to "provide a usable machine for agent work." (`76e1643c820c` · neutral · summary; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb|Giving Agents Computers — Ivan Burazin, Daytona]])
- As of 2026-05-21, this is a durable design constraint for agent infrastructure: if the workload includes long-running tasks, GUI interaction, or tool-rich workflows, a simple container is often the wrong abstraction. The interview suggests that runtime choice is a product decision, not just an ops detail, because it shapes what agents can do and how reliably they can recover from interruptions. (`094b8fcb9915` · neutral · why_it_matters; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb|Giving Agents Computers — Ivan Burazin, Daytona]])
- "what Daytona is today is essentially composable computers for AI agents" (`c3deb307169b` · supporting · evidence_snippets[0]; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb|Giving Agents Computers — Ivan Burazin, Daytona]])
- "They need a computer they can access through an API: something stateful enough to keep working, fast enough to spin up instantly, flexible enough to resize, isolated enough to be safe" (`065b63678d69` · supporting · evidence_snippets[1]; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb|Giving Agents Computers — Ivan Burazin, Daytona]])

## Source

- [[sources/giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb|Giving Agents Computers — Ivan Burazin, Daytona]]
