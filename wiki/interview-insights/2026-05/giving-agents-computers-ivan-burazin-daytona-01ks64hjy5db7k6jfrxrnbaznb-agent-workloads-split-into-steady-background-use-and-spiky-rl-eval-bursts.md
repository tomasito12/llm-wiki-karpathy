---
title: Agent workloads split into steady background use and spiky RL/eval bursts
slug: agent-workloads-split-into-steady-background-use-and-spiky-rl-eval-bursts
category: insight
tags:
- agent-evals
- infrastructure-economics
- runtime-systems
source_id: giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb
source_title: Giving Agents Computers — Ivan Burazin, Daytona
source_date: '2026-05-21'
month: 2026-05
evidence_count: 10
evidence_set_hash: 5156b60f55586895
insight_title: Agent workloads split into steady background use and spiky RL/eval
  bursts
insight_type: research_eval
confidence: high
durability_estimate: long_term
wiki_worthiness: strong_candidate
---

# Agent workloads split into steady background use and spiky RL/eval bursts

## Interview Insight

### Summary

Burazin separates Daytona usage into two distinct shapes: long-running background agents and RL/eval workloads. Background agents resemble human usage patterns, while RL/eval jobs can jump from no demand to very large CPU bursts and then drop back to zero. He says this makes average utilization a weak planning metric because peak capacity matters more than mean load.

### Why It Matters

As of 2026-05-21, this is a useful mental model for capacity planning in agent infrastructure. It explains why general cloud heuristics can fail when workloads are highly bursty and why providers may need different pricing, reservation, and scheduling strategies for different agent categories. The insight is operationally durable because it ties economics directly to workload shape.

### Operational Relevance

Design capacity management around peak concurrency and burst handling, not just average usage. Separate long-running interactive agents from eval/training-style workloads in scheduling, reservation, and billing logic. Expect provisioning pressure to come from sudden CPU spikes rather than smooth growth curves.

### Service Automation Relevance

Support automation and agentic operations may inherit the same burst patterns when teams batch-run evaluations, regression suites, or large ticket-processing jobs. Systems that assume human-like traffic shapes may underprovision or queue too aggressively.

### Mentioned Entities

- Daytona
- RL
- TerminalBench
- GDPVal
- Harbor

### Suggested Destinations

- topics/

### Contrarian Or Speculative Claims

- RL/eval workloads require infrastructure planning that is unlike human usage patterns.

### Evidence Snippets

- "background agents or long-running agents"
- "the other is, basically RLs and evals"
- "their usage patterns are similar to human, which is like follow the sun"
- "When you have companies doing sort of like evals and RL, they’re super spiky"
- "Daytona’s mean utilization is 15%"

## Evidence / supporting sources

### Giving Agents Computers — Ivan Burazin, Daytona (2026-05-21)

- RL/eval workloads require infrastructure planning that is unlike human usage patterns. (`0b40c4924abc` · counter · contrarian_or_speculative_claims[0]; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])
- Design capacity management around peak concurrency and burst handling, not just average usage. Separate long-running interactive agents from eval/training-style workloads in scheduling, reservation, and billing logic. Expect provisioning pressure to come from sudden CPU spikes rather than smooth growth curves. (`2ece2bbce499` · neutral · operational_relevance; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])
- Support automation and agentic operations may inherit the same burst patterns when teams batch-run evaluations, regression suites, or large ticket-processing jobs. Systems that assume human-like traffic shapes may underprovision or queue too aggressively. (`ba5f59a4a958` · neutral · service_automation_relevance; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])
- Burazin separates Daytona usage into two distinct shapes: long-running background agents and RL/eval workloads. Background agents resemble human usage patterns, while RL/eval jobs can jump from no demand to very large CPU bursts and then drop back to zero. He says this makes average utilization a weak planning metric because peak capacity matters more than mean load. (`325396fef0a0` · neutral · summary; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])
- As of 2026-05-21, this is a useful mental model for capacity planning in agent infrastructure. It explains why general cloud heuristics can fail when workloads are highly bursty and why providers may need different pricing, reservation, and scheduling strategies for different agent categories. The insight is operationally durable because it ties economics directly to workload shape. (`4aad7f1ab6f4` · neutral · why_it_matters; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])
- "background agents or long-running agents" (`48e5f6c48a4e` · supporting · evidence_snippets[0]; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])
- "the other is, basically RLs and evals" (`ad4319d7e3c8` · supporting · evidence_snippets[1]; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])
- "their usage patterns are similar to human, which is like follow the sun" (`1ea1c0a040a2` · supporting · evidence_snippets[2]; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])
- "When you have companies doing sort of like evals and RL, they’re super spiky" (`ff0a7e50ec3c` · supporting · evidence_snippets[3]; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])
- "Daytona’s mean utilization is 15%" (`d4dbaf5715b0` · supporting · evidence_snippets[4]; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])

## Source

- [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]]
