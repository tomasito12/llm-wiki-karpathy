---
title: Windows support is strategically important because legacy work still lives
  there
slug: windows-support-is-strategically-important-because-legacy-work-still-lives-there
category: insight
tags:
- enterprise-workflows
- execution-environments
- agent-systems
source_id: giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb
source_title: Giving Agents Computers — Ivan Burazin, Daytona
source_date: '2026-05-21'
month: 2026-05
evidence_count: 10
evidence_set_hash: 842fb9c5b4343415
insight_title: Windows support is strategically important because legacy work still
  lives there
insight_type: infrastructure
confidence: high
durability_estimate: long_term
wiki_worthiness: strong_candidate
---

# Windows support is strategically important because legacy work still lives there

## Interview Insight

### Summary

Burazin argues that computer-use agents need access to Windows because much knowledge work remains trapped in legacy Windows applications. He describes Windows sandboxes as a new product opportunity because the current spin-up path on EC2 or Azure is measured in minutes, while agent workflows need sandbox-style snapshots and faster startup. He also notes that macOS support is constrained by Apple licensing and snapshot limitations.

### Why It Matters

As of 2026-05-21, this is a practical deployment insight for teams deciding which desktop environments to support first. Windows support is not a niche feature if the target workload is enterprise back-office automation, where legacy desktop apps remain common. The macOS constraints are also important because they make cross-platform parity harder than the product narrative might suggest.

### Operational Relevance

If the workflow touches desktop software, prioritize Windows runtime support early and model macOS as a constrained, higher-friction offering. Treat OS licensing, snapshot mobility, and concurrent VM limits as product constraints, not just infrastructure details. This affects packaging, pricing, and scheduling.

### Service Automation Relevance

Service automation for enterprise back-office work often needs to interact with desktop apps, not only APIs. A support or operations agent that can only use web APIs may miss the real system of record if the organization still runs on Windows tools.

### Mentioned Entities

- Windows
- macOS
- Azure
- EC2
- Apple
- Daytona

### Suggested Destinations

- topics/

### Contrarian Or Speculative Claims

- A large share of knowledge work still depends on legacy Windows applications.

### Evidence Snippets

- "most of them, most of that work is actually still locked into legacy apps inside of Windows"
- "we’ve created an actual sandbox, so it’s a second instead of milliseconds"
- "macOS has this problem"
- "you’re allowed to run only two parallel VMs per machine"
- "you can only license to a different user every 24 hours"

## Evidence / supporting sources

### Giving Agents Computers — Ivan Burazin, Daytona (2026-05-21)

- A large share of knowledge work still depends on legacy Windows applications. (`76d31ea4d0cf` · counter · contrarian_or_speculative_claims[0]; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])
- If the workflow touches desktop software, prioritize Windows runtime support early and model macOS as a constrained, higher-friction offering. Treat OS licensing, snapshot mobility, and concurrent VM limits as product constraints, not just infrastructure details. This affects packaging, pricing, and scheduling. (`f754d74d94bd` · neutral · operational_relevance; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])
- Service automation for enterprise back-office work often needs to interact with desktop apps, not only APIs. A support or operations agent that can only use web APIs may miss the real system of record if the organization still runs on Windows tools. (`4c10ed82eaaf` · neutral · service_automation_relevance; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])
- Burazin argues that computer-use agents need access to Windows because much knowledge work remains trapped in legacy Windows applications. He describes Windows sandboxes as a new product opportunity because the current spin-up path on EC2 or Azure is measured in minutes, while agent workflows need sandbox-style snapshots and faster startup. He also notes that macOS support is constrained by Apple licensing and snapshot limitations. (`b00d54aced42` · neutral · summary; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])
- As of 2026-05-21, this is a practical deployment insight for teams deciding which desktop environments to support first. Windows support is not a niche feature if the target workload is enterprise back-office automation, where legacy desktop apps remain common. The macOS constraints are also important because they make cross-platform parity harder than the product narrative might suggest. (`5b90e4265843` · neutral · why_it_matters; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])
- "most of them, most of that work is actually still locked into legacy apps inside of Windows" (`4f0daed58ad0` · supporting · evidence_snippets[0]; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])
- "we’ve created an actual sandbox, so it’s a second instead of milliseconds" (`bb1a7c4aeda5` · supporting · evidence_snippets[1]; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])
- "macOS has this problem" (`651cd7684d61` · supporting · evidence_snippets[2]; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])
- "you’re allowed to run only two parallel VMs per machine" (`69c8eca12857` · supporting · evidence_snippets[3]; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])
- "you can only license to a different user every 24 hours" (`947665d9c508` · supporting · evidence_snippets[4]; [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]])

## Source

- [[sources/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb|Giving Agents Computers — Ivan Burazin, Daytona]]
