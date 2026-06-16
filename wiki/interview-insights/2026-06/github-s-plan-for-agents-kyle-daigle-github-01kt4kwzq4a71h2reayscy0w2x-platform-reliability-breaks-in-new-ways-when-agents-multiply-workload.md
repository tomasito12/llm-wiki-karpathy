---
title: Platform reliability breaks in new ways when agents multiply workload
slug: platform-reliability-breaks-in-new-ways-when-agents-multiply-workload
category: insight
tags:
- infrastructure
- runtime-systems
source_id: github-s-plan-for-agents-kyle-daigle-github-01kt4kwzq4a71h2reayscy0w2x
source_title: GitHub's plan for Agents — Kyle Daigle, GitHub
source_date: '2026-06-02'
month: 2026-06
evidence_count: 8
evidence_set_hash: d0f016119f688c29
insight_title: Platform reliability breaks in new ways when agents multiply workload
insight_type: infrastructure
confidence: high
durability_estimate: long_term
wiki_worthiness: strong_candidate
---

# Platform reliability breaks in new ways when agents multiply workload

## Interview Insight

### Summary

Daigle says GitHub’s reliability issues are not just old scaling problems returning at larger size. Agentic coding increases commits, PRs, builds, repository size, and permissioning complexity, which stresses Actions, databases, job queues, and on-prem deployments in new combinations.

### Why It Matters

As of 2026-06-02, this is a practical infrastructure lesson for any code platform or developer tool: agent adoption can create load patterns that invalidate older scaling assumptions. The implication is that platform teams need to model permissions, compute, and repository shape as part of reliability planning.

### Operational Relevance

Expect more CPU pressure from automation-heavy workflows and more database pressure from permissions and object growth. Reliability work may require both horizontal and vertical changes, plus rewrites of older subsystems that assumed human-scale traffic and smaller pushes.

### Service Automation Relevance

For support and conversational systems, the analog is that automation can create load spikes in routing, history storage, and permission checks, not just model inference. Operational planning should include back-end scaling and state management, not only response quality.

### Mentioned Entities

- GitHub Actions
- MySQL One
- Vitess
- Azure
- GitHub Enterprise Server
- npm

### Suggested Destinations

- topics/

### Contrarian Or Speculative Claims

- GitHub’s scaling path is becoming a diagonal problem where neither pure vertical nor pure horizontal scaling is enough.

### Evidence Snippets

- "more tools, more agents, more PRs mean more builds, more builds mean more CPUs"
- "the place that we continue to have pain is in, permissioning"
- "we’re sort of in a like diagonal, where like vertical doesn’t really work anymore. Horizontal isn’t work either"

## Evidence / supporting sources

### GitHub's plan for Agents — Kyle Daigle, GitHub (2026-06-02)

- GitHub’s scaling path is becoming a diagonal problem where neither pure vertical nor pure horizontal scaling is enough. (`3c8812b65742` · counter · contrarian_or_speculative_claims[0]; [[sources/github-s-plan-for-agents-kyle-daigle-github-01kt4kwzq4a71h2reayscy0w2x|GitHub's plan for Agents — Kyle Daigle, GitHub]])
- Expect more CPU pressure from automation-heavy workflows and more database pressure from permissions and object growth. Reliability work may require both horizontal and vertical changes, plus rewrites of older subsystems that assumed human-scale traffic and smaller pushes. (`c16ab27ed2f3` · neutral · operational_relevance; [[sources/github-s-plan-for-agents-kyle-daigle-github-01kt4kwzq4a71h2reayscy0w2x|GitHub's plan for Agents — Kyle Daigle, GitHub]])
- For support and conversational systems, the analog is that automation can create load spikes in routing, history storage, and permission checks, not just model inference. Operational planning should include back-end scaling and state management, not only response quality. (`d0360fdfa938` · neutral · service_automation_relevance; [[sources/github-s-plan-for-agents-kyle-daigle-github-01kt4kwzq4a71h2reayscy0w2x|GitHub's plan for Agents — Kyle Daigle, GitHub]])
- Daigle says GitHub’s reliability issues are not just old scaling problems returning at larger size. Agentic coding increases commits, PRs, builds, repository size, and permissioning complexity, which stresses Actions, databases, job queues, and on-prem deployments in new combinations. (`b3a53fc35bac` · neutral · summary; [[sources/github-s-plan-for-agents-kyle-daigle-github-01kt4kwzq4a71h2reayscy0w2x|GitHub's plan for Agents — Kyle Daigle, GitHub]])
- As of 2026-06-02, this is a practical infrastructure lesson for any code platform or developer tool: agent adoption can create load patterns that invalidate older scaling assumptions. The implication is that platform teams need to model permissions, compute, and repository shape as part of reliability planning. (`14eebe27f7da` · neutral · why_it_matters; [[sources/github-s-plan-for-agents-kyle-daigle-github-01kt4kwzq4a71h2reayscy0w2x|GitHub's plan for Agents — Kyle Daigle, GitHub]])
- "more tools, more agents, more PRs mean more builds, more builds mean more CPUs" (`f34766aa9984` · supporting · evidence_snippets[0]; [[sources/github-s-plan-for-agents-kyle-daigle-github-01kt4kwzq4a71h2reayscy0w2x|GitHub's plan for Agents — Kyle Daigle, GitHub]])
- "the place that we continue to have pain is in, permissioning" (`e5ded87885df` · supporting · evidence_snippets[1]; [[sources/github-s-plan-for-agents-kyle-daigle-github-01kt4kwzq4a71h2reayscy0w2x|GitHub's plan for Agents — Kyle Daigle, GitHub]])
- "we’re sort of in a like diagonal, where like vertical doesn’t really work anymore. Horizontal isn’t work either" (`13f6ab960867` · supporting · evidence_snippets[2]; [[sources/github-s-plan-for-agents-kyle-daigle-github-01kt4kwzq4a71h2reayscy0w2x|GitHub's plan for Agents — Kyle Daigle, GitHub]])

## Source

- [[sources/github-s-plan-for-agents-kyle-daigle-github-01kt4kwzq4a71h2reayscy0w2x|GitHub's plan for Agents — Kyle Daigle, GitHub]]
