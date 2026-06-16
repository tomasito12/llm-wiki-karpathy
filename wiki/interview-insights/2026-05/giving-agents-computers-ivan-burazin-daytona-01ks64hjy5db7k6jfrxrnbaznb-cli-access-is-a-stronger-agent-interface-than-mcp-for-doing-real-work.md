---
title: CLI access is a stronger agent interface than MCP for doing real work
slug: cli-access-is-a-stronger-agent-interface-than-mcp-for-doing-real-work
category: insight
tags:
- developer-tooling
- agent-systems
source_id: giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb
source_title: Giving Agents Computers — Ivan Burazin, Daytona
source_date: '2026-05-21'
month: 2026-05
evidence_count: 8
evidence_set_hash: 770beef70700fda7
insight_title: CLI access is a stronger agent interface than MCP for doing real work
insight_type: tool
confidence: medium
durability_estimate: medium_term
wiki_worthiness: review_candidate
---

# CLI access is a stronger agent interface than MCP for doing real work

## Interview Insight

### Summary

Burazin distinguishes MCP as an interface to an API from CLI access, which lets an agent actually execute scripts and operations. His claim is that sandboxes become more valuable when agents can run command-line workflows end to end rather than only read structured API responses. He frames this as a practical difference in how much action the agent can take, not just how much data it can inspect.

### Why It Matters

As of 2026-05-21, this is a useful implementation lens for agent tooling. Teams building agent runtimes should think in terms of executable interfaces, not only data-access interfaces, because the ability to run commands materially expands the set of tasks an agent can complete. The claim is opinionated, but it is operationally useful.

### Operational Relevance

Favor CLI-friendly runtimes, shell access, and script execution paths when the goal is autonomous completion rather than read-only integration. Reserve MCP-like interfaces for structured data access, but do not treat them as sufficient for end-to-end task execution. This is especially relevant for tool-heavy workflows and sandbox orchestration.

### Service Automation Relevance

Support automation agents often need to log in, export, transform, and validate data across systems. A CLI-capable agent runtime is more likely to complete those workflows than one limited to API-mediated access.

### Mentioned Entities

- MCP
- CLI
- Claude Code

### Suggested Destinations

- topics/

### Contrarian Or Speculative Claims

- CLI may matter more than MCP for agent capability.

### Evidence Snippets

- "the MCP is an interface against an API, whereas the CLI is like you can actually go do things"
- "being able to use a CLI very well enables the agent to do more things"
- "a lot of, let’s call them app layer agent companies"

## Evidence / supporting sources

### Giving Agents Computers — Ivan Burazin, Daytona (2026-05-21)

- CLI may matter more than MCP for agent capability. (`0fd1f45c888f` · counter · contrarian_or_speculative_claims[0]; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])
- Favor CLI-friendly runtimes, shell access, and script execution paths when the goal is autonomous completion rather than read-only integration. Reserve MCP-like interfaces for structured data access, but do not treat them as sufficient for end-to-end task execution. This is especially relevant for tool-heavy workflows and sandbox orchestration. (`4364166366fa` · neutral · operational_relevance; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])
- Support automation agents often need to log in, export, transform, and validate data across systems. A CLI-capable agent runtime is more likely to complete those workflows than one limited to API-mediated access. (`bdcb40729a14` · neutral · service_automation_relevance; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])
- Burazin distinguishes MCP as an interface to an API from CLI access, which lets an agent actually execute scripts and operations. His claim is that sandboxes become more valuable when agents can run command-line workflows end to end rather than only read structured API responses. He frames this as a practical difference in how much action the agent can take, not just how much data it can inspect. (`24d7bc1e5f0e` · neutral · summary; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])
- As of 2026-05-21, this is a useful implementation lens for agent tooling. Teams building agent runtimes should think in terms of executable interfaces, not only data-access interfaces, because the ability to run commands materially expands the set of tasks an agent can complete. The claim is opinionated, but it is operationally useful. (`9104789944b0` · neutral · why_it_matters; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])
- "the MCP is an interface against an API, whereas the CLI is like you can actually go do things" (`23f223a56c5d` · supporting · evidence_snippets[0]; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])
- "being able to use a CLI very well enables the agent to do more things" (`2cbc11eaeba0` · supporting · evidence_snippets[1]; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])
- "a lot of, let’s call them app layer agent companies" (`89dfbb37e705` · supporting · evidence_snippets[2]; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])

## Source

- [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]]
