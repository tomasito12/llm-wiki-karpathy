---
title: Intercom's AI-Approved Pull Request Pipeline
slug: intercom-s-ai-approved-pull-request-pipeline
category: implementation-study
tags:
- software-engineering
- enterprise-ai
- ai-operationalization
source_id: ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33
source_title: 'AI is approving our pull requests: Here’s how we made it safe'
source_date: '2026-04-21'
month: 2026-04
company: Intercom
industry: software / developer tools
evidence_count: 24
evidence_set_hash: 627c98a1f2234911
---

# Intercom's AI-Approved Pull Request Pipeline

## Implementation Study

### Overview

Intercom describes a production pull request review pipeline where AI agents review code changes and sometimes auto-approve them without a human reviewer. The system was rolled out after a controlled pilot and later scaled to hundreds of autonomous approvals in a broader rollout.

### What was implemented?

A multi-agent PR review system that decomposes review into specialist checks for problem description quality, intent alignment, safety, correctness, best practices, and anti-patterns, plus an auto-approval path for qualified changes.

### Business objective

Reduce the PR review bottleneck created by high volumes of AI-generated code while preserving or improving safety, compliance, and deployment quality.

### Technical approach

Intercom says the reviewer is split into independent sub-agents, grounded in Intercom-specific guidance, with continuous engineer feedback on review comments. The system logs labels, review comments, approval decisions, test results, and merge events for auditability.

### Deployment context

The article describes a controlled pilot of over 100 PRs, followed by a broader rollout in which 497 PRs went fully autonomous in the first four weeks. Intercom also says engineers can still request human review on any change.

### Outcome / current status

Ongoing production rollout as of 2026-04-21. Intercom reports zero reverts in the pilot, a 6–16x improvement in time-to-approval at the 75th percentile, and lower revert rates for AI-authored code than human-authored code in the reported sample.

### Why it succeeded or struggled

The system appears to work because it is strict, decomposed into specialist checks, grounded in local codebase guidance, and reinforced by feedback loops. The safety story also depends on shipping small batches and maintaining rollback discipline.

### Operational constraints

The system will not approve large, too-complex, or overly broad PRs. Intercom also notes that PR review cannot catch production-only issues such as infrastructure failures, unusual customer usage patterns, or third-party outages.

### AI / model observations

Intercom's account suggests that a structured agent reviewer can outperform ad hoc human review on some code-change quality dimensions when it is specialized, local-context-aware, and allowed to reject scope-heavy changes.

### Implications for service automation

Direct implications for service automation are limited because this is a software-engineering deployment, not a customer-facing chatbot or voicebot system. The transferable lesson is that high-trust automation needs explicit override paths, evidence logging, and scoped decision rights.

### Strategic signals

The case signals that agentic automation can be governed as an operational system rather than a convenience feature. It also suggests that organizations adopting AI-generated work may need AI reviewers to avoid human rubber-stamping under load.

### Key Lessons

- Break review into separate specialist checks instead of one generic judgment.
- Use scope limits to push engineers toward smaller changes.
- Keep human override available for exceptions and accountability.
- Log enough evidence that a later reviewer can reconstruct the decision.
- Do not expect PR review alone to catch production incidents.

### Open Questions

- How were false positives and false negatives measured over time?
- What confidence thresholds or rejection rules govern auto-approval?
- How much of the result comes from the reviewer versus the organization's small-batch shipping culture?
- How durable are the reported revert-rate differences across larger samples and longer periods?

### Related Sources

- https://www.intercom.com/blog/ai-is-approving-our-pull-requests-heres-how-we-made-it-safe/

### Evidence Snippets

- Intercom deployed an AI PR review system in production and allowed auto-approval for some pull requests. — "Today, over 93% of our pull requests (PRs) across our two main codebases are Agent-driven. And over 19% are auto-approved with no human reviewer in the loop." (stated)
- The system is decomposed into specialist sub-agents rather than one monolithic reviewer. — "Our PR review Agent doesn’t treat code review as a single task. It decomposes it into separate sub-jobs, each handled by an independent sub-Agent." (stated)
- Intercom logs the evidence needed for auditability. — "Every AI-approved PR is labelled, logged, and queryable. The review comments, the approval decision, the test results, the merge event: all recorded." (stated)
- The rollout produced measurable approval-speed and revert-rate outcomes. — "The results: zero reverts of AI-approved PRs, and a 6–16x improvement in time-to-approval at the 75th percentile." (stated)

## Evidence / supporting sources

### AI is approving our pull requests: Here’s how we made it safe (2026-04-21)

- Intercom's account suggests that a structured agent reviewer can outperform ad hoc human review on some code-change quality dimensions when it is specialized, local-context-aware, and allowed to reject scope-heavy changes. (`1c425498bc2b` · neutral · ai_model_observations; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- Reduce the PR review bottleneck created by high volumes of AI-generated code while preserving or improving safety, compliance, and deployment quality. (`d19116472a40` · neutral · business_objective; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- The article describes a controlled pilot of over 100 PRs, followed by a broader rollout in which 497 PRs went fully autonomous in the first four weeks. Intercom also says engineers can still request human review on any change. (`36092415f691` · neutral · deployment_context; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- Direct implications for service automation are limited because this is a software-engineering deployment, not a customer-facing chatbot or voicebot system. The transferable lesson is that high-trust automation needs explicit override paths, evidence logging, and scoped decision rights. (`c8db02f39a46` · neutral · implications_for_service_automation; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- How were false positives and false negatives measured over time? (`ff60861bff4e` · neutral · open_questions[0]; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- What confidence thresholds or rejection rules govern auto-approval? (`15915dc4d1ff` · neutral · open_questions[1]; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- How much of the result comes from the reviewer versus the organization's small-batch shipping culture? (`78df02dc16ba` · neutral · open_questions[2]; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- How durable are the reported revert-rate differences across larger samples and longer periods? (`416bfcb33397` · neutral · open_questions[3]; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- The system will not approve large, too-complex, or overly broad PRs. Intercom also notes that PR review cannot catch production-only issues such as infrastructure failures, unusual customer usage patterns, or third-party outages. (`6851de2e1fe3` · neutral · operational_constraints; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- Ongoing production rollout as of 2026-04-21. Intercom reports zero reverts in the pilot, a 6–16x improvement in time-to-approval at the 75th percentile, and lower revert rates for AI-authored code than human-authored code in the reported sample. (`7e17aae29fd6` · neutral · outcome_status; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- Intercom describes a production pull request review pipeline where AI agents review code changes and sometimes auto-approve them without a human reviewer. The system was rolled out after a controlled pilot and later scaled to hundreds of autonomous approvals in a broader rollout. (`26b89dd17868` · neutral · overview; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- The case signals that agentic automation can be governed as an operational system rather than a convenience feature. It also suggests that organizations adopting AI-generated work may need AI reviewers to avoid human rubber-stamping under load. (`9348cf1b189a` · neutral · strategic_signals; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- The system appears to work because it is strict, decomposed into specialist checks, grounded in local codebase guidance, and reinforced by feedback loops. The safety story also depends on shipping small batches and maintaining rollback discipline. (`78531d1f7c2c` · neutral · success_or_failure_factors; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- Intercom says the reviewer is split into independent sub-agents, grounded in Intercom-specific guidance, with continuous engineer feedback on review comments. The system logs labels, review comments, approval decisions, test results, and merge events for auditability. (`5ceca10360a5` · neutral · technical_approach; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- A multi-agent PR review system that decomposes review into specialist checks for problem description quality, intent alignment, safety, correctness, best practices, and anti-patterns, plus an auto-approval path for qualified changes. (`9ef26c60037b` · neutral · what_was_implemented; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- Intercom deployed an AI PR review system in production and allowed auto-approval for some pull requests. — "Today, over 93% of our pull requests (PRs) across our two main codebases are Agent-driven. And over 19% are auto-approved with no human reviewer in the loop." (`6f54dfd0afcc` · supporting · evidence_snippets[0]; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- The system is decomposed into specialist sub-agents rather than one monolithic reviewer. — "Our PR review Agent doesn’t treat code review as a single task. It decomposes it into separate sub-jobs, each handled by an independent sub-Agent." (`41b06d983e9e` · supporting · evidence_snippets[1]; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- Intercom logs the evidence needed for auditability. — "Every AI-approved PR is labelled, logged, and queryable. The review comments, the approval decision, the test results, the merge event: all recorded." (`5f6031747780` · supporting · evidence_snippets[2]; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- The rollout produced measurable approval-speed and revert-rate outcomes. — "The results: zero reverts of AI-approved PRs, and a 6–16x improvement in time-to-approval at the 75th percentile." (`90d1a98533cd` · supporting · evidence_snippets[3]; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- Break review into separate specialist checks instead of one generic judgment. (`a5af4ef47e67` · supporting · key_lessons[0]; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- Use scope limits to push engineers toward smaller changes. (`c3a287913005` · supporting · key_lessons[1]; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- Keep human override available for exceptions and accountability. (`205c5744bbf3` · supporting · key_lessons[2]; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- Log enough evidence that a later reviewer can reconstruct the decision. (`ece59bfa669e` · supporting · key_lessons[3]; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- Do not expect PR review alone to catch production incidents. (`6302eb194f0e` · supporting · key_lessons[4]; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])

## Source

- [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]]
