---
title: Spiky RL and eval workloads create a different capacity-planning problem than
  background agents
slug: spiky-rl-and-eval-workloads-create-a-different-capacity-planning-problem-than-background-agents
category: insight
tags:
- ai-evaluation
- infrastructure-economics
source_id: giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb
source_title: Giving Agents Computers — Ivan Burazin, Daytona
source_date: '2026-05-21'
month: 2026-05
evidence_count: 8
evidence_set_hash: 3e814ca36e7db9b6
insight_title: Spiky RL and eval workloads create a different capacity-planning problem
  than background agents
insight_type: research_eval
confidence: high
durability_estimate: long_term
wiki_worthiness: strong_candidate
---

# Spiky RL and eval workloads create a different capacity-planning problem than background agents

## Interview Insight

### Summary

The interview separates two workload shapes: steady background agents and highly bursty RL/eval jobs. Background agent traffic is described as follow-the-sun, while RL/eval usage is described as sudden spikes to very large CPU counts followed by drops back to near zero. That means the infrastructure problem is not just total demand, but demand shape.

### Why It Matters

As of 2026-05-21, this is a useful operational distinction for any provider serving agent workloads. Capacity planning, billing, and scheduler design may need to optimize for peak bursts and low average utilization, not just smooth growth curves.

### Operational Relevance

Providers should model separate queues, reservation policies, and autoscaling strategies for steady agent traffic versus batch-style RL/eval bursts. The source explicitly says mean utilization is low while peak utilization can be high, which implies overprovisioning or on-demand overflow is unavoidable.

### Service Automation Relevance

Service automation systems that trigger evaluation, testing, or retraining jobs can create sudden load spikes, so they need queueing and backpressure designs that do not destabilize customer-facing automation.

### Mentioned Entities

- Daytona
- Harbor
- TerminalBench
- GDPVal
- Cloudflare
- Neon
- Parallel

### Suggested Destinations

- topics/

### Contrarian Or Speculative Claims

- The source implies that spiky RL/eval workloads are a distinct infrastructure class with very high peak-to-average ratios, but that is based on vendor observation rather than independent market data.

### Evidence Snippets

- "RL/eval workloads went from 0% to roughly 50% of usage in just months"
- "mean utilization is 15%"
- "they’re gonna come in, it’s like, ‘We’re gonna use nothing, then can we have 100,000?’"

## Evidence / supporting sources

### Giving Agents Computers — Ivan Burazin, Daytona (2026-05-21)

- The source implies that spiky RL/eval workloads are a distinct infrastructure class with very high peak-to-average ratios, but that is based on vendor observation rather than independent market data. (`6da63d591482` · counter · contrarian_or_speculative_claims[0]; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb|Giving Agents Computers — Ivan Burazin, Daytona]])
- Providers should model separate queues, reservation policies, and autoscaling strategies for steady agent traffic versus batch-style RL/eval bursts. The source explicitly says mean utilization is low while peak utilization can be high, which implies overprovisioning or on-demand overflow is unavoidable. (`dd752518f451` · neutral · operational_relevance; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb|Giving Agents Computers — Ivan Burazin, Daytona]])
- Service automation systems that trigger evaluation, testing, or retraining jobs can create sudden load spikes, so they need queueing and backpressure designs that do not destabilize customer-facing automation. (`73ac58f7ecf9` · neutral · service_automation_relevance; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb|Giving Agents Computers — Ivan Burazin, Daytona]])
- The interview separates two workload shapes: steady background agents and highly bursty RL/eval jobs. Background agent traffic is described as follow-the-sun, while RL/eval usage is described as sudden spikes to very large CPU counts followed by drops back to near zero. That means the infrastructure problem is not just total demand, but demand shape. (`00e19e551860` · neutral · summary; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb|Giving Agents Computers — Ivan Burazin, Daytona]])
- As of 2026-05-21, this is a useful operational distinction for any provider serving agent workloads. Capacity planning, billing, and scheduler design may need to optimize for peak bursts and low average utilization, not just smooth growth curves. (`29e95e882f57` · neutral · why_it_matters; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb|Giving Agents Computers — Ivan Burazin, Daytona]])
- "RL/eval workloads went from 0% to roughly 50% of usage in just months" (`cb584b05dccb` · supporting · evidence_snippets[0]; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb|Giving Agents Computers — Ivan Burazin, Daytona]])
- "mean utilization is 15%" (`ed5c9528a313` · supporting · evidence_snippets[1]; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb|Giving Agents Computers — Ivan Burazin, Daytona]])
- "they’re gonna come in, it’s like, ‘We’re gonna use nothing, then can we have 100,000?’" (`aa4e6abb3429` · supporting · evidence_snippets[2]; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb|Giving Agents Computers — Ivan Burazin, Daytona]])

## Source

- [[sources/giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb|Giving Agents Computers — Ivan Burazin, Daytona]]
