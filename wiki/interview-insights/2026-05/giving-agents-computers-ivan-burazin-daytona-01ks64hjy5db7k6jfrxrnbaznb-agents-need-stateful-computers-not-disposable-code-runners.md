---
title: Agents need stateful computers, not disposable code runners
slug: agents-need-stateful-computers-not-disposable-code-runners
category: insight
tags:
- runtime-architecture
- long-running-agents
source_id: giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb
source_title: Giving Agents Computers — Ivan Burazin, Daytona
source_date: '2026-05-21'
month: 2026-05
evidence_count: 8
evidence_set_hash: 7de4dc9f708e003b
insight_title: Agents need stateful computers, not disposable code runners
insight_type: infrastructure
confidence: high
durability_estimate: long_term
wiki_worthiness: strong_candidate
---

# Agents need stateful computers, not disposable code runners

## Interview Insight

### Summary

Burazin argues that the useful primitive for agent workloads is a composable computer with persistent state, fast startup, and the ability to resize resources on demand. He contrasts this with narrow code-execution boxes that only run a snippet and return output. The design goal is to let an agent pause, resume, and continue a workflow without losing its working state.

### Why It Matters

As of 2026-05-21, this is a durable architectural frame for teams building agent runtimes and automation products. It suggests that product choices should be driven by workflow continuity and state recovery, not just container isolation or cheap execution. That is especially relevant when agents must survive long tasks, tool chains, and interrupted sessions.

### Operational Relevance

Prioritize stateful sandboxes, snapshot/resume semantics, and resource resizing when designing agent infrastructure. Treat the runtime as a computer abstraction rather than a one-off execution endpoint. This affects orchestration, failure recovery, and how you model work units for long-running agents.

### Service Automation Relevance

Service automation systems that need continuity across handoffs or multi-step investigations benefit from stateful runtime support. A chatbot or voicebot that launches tool-heavy back-office work may need the same pause/resume behavior to avoid losing context between steps.

### Mentioned Entities

- Daytona
- CodeAnywhere

### Suggested Destinations

- topics/

### Contrarian Or Speculative Claims

- Agents need composable computers rather than disposable code execution boxes.

### Evidence Snippets

- "what Daytona is today is essentially composable computers for AI agents"
- "they need a computer they can access through an API: something stateful enough to keep working, fast enough to spin up instantly, flexible enough to resize"
- "we need something insanely fast, how to make it fast, how to make it long-running, and stateful. And so those two things, it’s like combining a Lambda and an EC2"

## Evidence / supporting sources

### Giving Agents Computers — Ivan Burazin, Daytona (2026-05-21)

- Agents need composable computers rather than disposable code execution boxes. (`e3a146a94553` · counter · contrarian_or_speculative_claims[0]; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])
- Prioritize stateful sandboxes, snapshot/resume semantics, and resource resizing when designing agent infrastructure. Treat the runtime as a computer abstraction rather than a one-off execution endpoint. This affects orchestration, failure recovery, and how you model work units for long-running agents. (`aa385551d085` · neutral · operational_relevance; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])
- Service automation systems that need continuity across handoffs or multi-step investigations benefit from stateful runtime support. A chatbot or voicebot that launches tool-heavy back-office work may need the same pause/resume behavior to avoid losing context between steps. (`0d6494e17b60` · neutral · service_automation_relevance; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])
- Burazin argues that the useful primitive for agent workloads is a composable computer with persistent state, fast startup, and the ability to resize resources on demand. He contrasts this with narrow code-execution boxes that only run a snippet and return output. The design goal is to let an agent pause, resume, and continue a workflow without losing its working state. (`cba0d5e3f4bb` · neutral · summary; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])
- As of 2026-05-21, this is a durable architectural frame for teams building agent runtimes and automation products. It suggests that product choices should be driven by workflow continuity and state recovery, not just container isolation or cheap execution. That is especially relevant when agents must survive long tasks, tool chains, and interrupted sessions. (`8b00418aa50a` · neutral · why_it_matters; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])
- "what Daytona is today is essentially composable computers for AI agents" (`2781dbfb446f` · supporting · evidence_snippets[0]; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])
- "they need a computer they can access through an API: something stateful enough to keep working, fast enough to spin up instantly, flexible enough to resize" (`8c1a7091d261` · supporting · evidence_snippets[1]; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])
- "we need something insanely fast, how to make it fast, how to make it long-running, and stateful. And so those two things, it’s like combining a Lambda and an EC2" (`fc010e067844` · supporting · evidence_snippets[2]; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])

## Source

- [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]]
