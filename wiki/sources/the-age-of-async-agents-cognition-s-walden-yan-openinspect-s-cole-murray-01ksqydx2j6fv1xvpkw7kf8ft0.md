---
title: The Age of Async Agents — Cognition's Walden Yan & OpenInspect's Cole Murray
slug: the-age-of-async-agents-cognition-s-walden-yan-openinspect-s-cole-murray-01ksqydx2j6fv1xvpkw7kf8ft0
category: source
tags:
- agent-evals
- agent-memory
- agent-orchestration
- agent-systems
- ai-engineering
- ai-evaluation
- autonomous-workflows
- behavioral-drift
- coding-agents
- distribution
- enterprise-ai
- infrastructure
- knowledge-systems
- retrieval-systems
- software-engineering
- test-and-verification
- verification-systems
source_id: the-age-of-async-agents-cognition-s-walden-yan-openinspect-s-cole-murray-01ksqydx2j6fv1xvpkw7kf8ft0
author: Latent.Space
publication: Substack
published_date: '2026-05-28'
assessed_as_of: '2026-05-28'
ingested_at: '2026-06-08T16:05:24.247284+00:00'
canonical_url: mailto:reader-forwarded-email/d53a8f7261a10010333d3ba1b2a93b6c
content_sha256: 1eb1a0a6096e6ec832946467f729965bf10f9d33f7c0d2a0a197532e1dbea25d
derived_interview_insights:
- interview-insights/2026-05/the-age-of-async-agents-cognition-s-walden-yan-openinspect-s-cole-murray-01ksqyd-agent-products-sell-infrastructure-and-adoption-help-not-just-model-147dd19db2.md
- interview-insights/2026-05/the-age-of-async-agents-cognition-s-walden-yan-openinspect-s-cole-murray-01ksqyd-background-agents-are-becoming-practical-only-when-models-can-go-fro-b56a7c6dd7.md
- interview-insights/2026-05/the-age-of-async-agents-cognition-s-walden-yan-openinspect-s-cole-murray-01ksqyd-memory-is-still-an-unsolved-retrieval-problem-with-file-like-workaro-df717f81ed.md
- interview-insights/2026-05/the-age-of-async-agents-cognition-s-walden-yan-openinspect-s-cole-murray-01ksqyd-testing-real-applications-is-a-harder-problem-than-computer-use-d7390bd80e.md
- interview-insights/2026-05/the-age-of-async-agents-cognition-s-walden-yan-openinspect-s-cole-murray-01ksqyd-uncontrolled-ai-coding-can-regress-codebases-toward-the-worst-engine-f08bd139b8.md
derived_pages:
- interview-insights/2026-05/the-age-of-async-agents-cognition-s-walden-yan-openinspect-s-cole-murray-01ksqyd-agent-products-sell-infrastructure-and-adoption-help-not-just-model-147dd19db2.md
- interview-insights/2026-05/the-age-of-async-agents-cognition-s-walden-yan-openinspect-s-cole-murray-01ksqyd-background-agents-are-becoming-practical-only-when-models-can-go-fro-b56a7c6dd7.md
- interview-insights/2026-05/the-age-of-async-agents-cognition-s-walden-yan-openinspect-s-cole-murray-01ksqyd-memory-is-still-an-unsolved-retrieval-problem-with-file-like-workaro-df717f81ed.md
- interview-insights/2026-05/the-age-of-async-agents-cognition-s-walden-yan-openinspect-s-cole-murray-01ksqyd-testing-real-applications-is-a-harder-problem-than-computer-use-d7390bd80e.md
- interview-insights/2026-05/the-age-of-async-agents-cognition-s-walden-yan-openinspect-s-cole-murray-01ksqyd-uncontrolled-ai-coding-can-regress-codebases-toward-the-worst-engine-f08bd139b8.md
---

# The Age of Async Agents — Cognition's Walden Yan & OpenInspect's Cole Murray

This is a conversation about how coding agents are changing from chatty helpers into background workers that can take a task, run tests, and open a pull request. The main idea is that better models made “spec to PR” workflows realistic, but the real challenge is everything around the model: sandboxes, permissions, integrations, and evaluation. The guests explain why full virtual machines, snapshot restore, and strong separation between the agent’s brain and the machine matter for safety and reliability. They also talk about why memory is still messy, why code review is still needed, and why letting agents run wild can make a codebase degrade. In plain English: the hard part is building the factory around the agent, not just the agent itself.

## Key insights

- The most durable agent pattern described here is not local copilot-style assistance but background execution with a repo, machine, tests, and review loop attached.
- Separating the agent’s decision-making from the machine it operates on is presented as a security and permissions boundary, not just an architectural preference.
- Testing is treated as a harder problem than computer use because real validation requires orchestrating app state, feature flags, multiple services, and sometimes multiple frontier models.
- Memory remains unresolved; the article suggests practical stopgaps like skills, Claude.md, auto-generated memories, and file-system-like memory stores rather than a clean solved system.
- A codebase can regress toward the patterns of its least careful engineer if AI-generated changes are not reviewed and cleaned up, so linting and scheduled cleanup are operational safeguards, not optional polish.

## Derived knowledge pages

- [[interview-insights/2026-05/the-age-of-async-agents-cognition-s-walden-yan-openinspect-s-cole-murray-01ksqyd-agent-products-sell-infrastructure-and-adoption-help-not-just-model-147dd19db2]]
- [[interview-insights/2026-05/the-age-of-async-agents-cognition-s-walden-yan-openinspect-s-cole-murray-01ksqyd-background-agents-are-becoming-practical-only-when-models-can-go-fro-b56a7c6dd7]]
- [[interview-insights/2026-05/the-age-of-async-agents-cognition-s-walden-yan-openinspect-s-cole-murray-01ksqyd-memory-is-still-an-unsolved-retrieval-problem-with-file-like-workaro-df717f81ed]]
- [[interview-insights/2026-05/the-age-of-async-agents-cognition-s-walden-yan-openinspect-s-cole-murray-01ksqyd-testing-real-applications-is-a-harder-problem-than-computer-use-d7390bd80e]]
- [[interview-insights/2026-05/the-age-of-async-agents-cognition-s-walden-yan-openinspect-s-cole-murray-01ksqyd-uncontrolled-ai-coding-can-regress-codebases-toward-the-worst-engine-f08bd139b8]]

## Why it matters

The piece is useful because it compresses a lot of practical background-agent design into one architecture discussion: where the agent runs, how it gets secrets, how it interacts with GitHub and Slack, how it tests real software, and how it avoids poisoning the codebase. That makes it more than a product interview; it is a field report on what is still hard after model quality improved enough to make spec-to-PR workflows plausible as of 2026-05-28. The strongest durable idea is that selling an agent product usually means selling agent infrastructure too: VMs, snapshots, integrations, onboarding, and environment setup. The guests repeatedly stress that sandbox choice, repo setup, and restore speed are production blockers, not implementation details. Their discussion of out-of-the-box control planes, scoped secrets, and full VMs gives concrete reasons why simple “tool calling” abstractions are insufficient for serious enterprise use. The memory section is also valuable because it resists hype and says the retrieval/generation problem is still open, with only partial workarounds. The code review and lint-rule discussion adds a practical warning: autonomous coding can amplify bad patterns unless teams add explicit guardrails. The most compelling operational takeaway is that agent adoption is constrained by systems engineering quality, not just model benchmarks, and that remains actionable as of 2026-05-28. The later use-case discussion matters because it shows where these systems are already being pointed in production: triage, pull requests from Slack, and code-aware support workflows.

## Limitations / open questions

Several claims are anecdotal or product-specific rather than benchmarked, including the 7x merged PR growth, the 16% to 80% commit share, and the claim that December 2025 model quality made spec-to-PR workflows practical. The discussion treats memory as unsolved, but does not provide a concrete retrieval design, pruning policy, or evaluation result that would let a reader judge which workaround is best. The architecture preference for out-of-the-box agents is plausible, but the transcript acknowledges that it is more complex and that state management remains hard. The economics are thinly specified: $20/seat is mentioned as hard to monetize, and $1k–$5k per engineer is cited as a common spend range, but there is no rigorous cost model or ROI analysis. The transcript also leaves open how to evaluate end-to-end testing quality across many heterogeneous apps, especially when no single frontier model can do the whole workflow alone. Support, PM, and SRE use cases are discussed, but implementation depth is uneven and mostly framed as product direction rather than proven deployment outcomes.

## Contradictions / unverified claims

The episode is enthusiastic about background agents, but it also undercuts some of its own optimism by admitting that multi-agent systems are still often just tool calls, not true collaboration, and that one strong agent can outperform a swarm in practice. The claim that agents can go from spec to PR with very little friction depends heavily on spec quality and on infrastructure that many teams do not have. The discussion of autonomous coding factory workflows is compelling, but the “don’t look at code” posture is explicitly rejected by both speakers, which is a useful check against pure hype. The memory discussion is especially skeptical: even the builders say it is not solved, and the suggested fixes are partial. Overall the transcript reads as production realism rather than marketing, but the strongest claims still need external validation beyond the examples cited here.

## Source metadata

- Canonical URL: mailto:reader-forwarded-email/d53a8f7261a10010333d3ba1b2a93b6c
- Raw markdown: `raw/readwise/the-age-of-async-agents-cognition-s-walden-yan-openinspect-s-cole-murray-01ksqydx2j6fv1xvpkw7kf8ft0.md`
- Raw HTML: `raw/readwise/the-age-of-async-agents-cognition-s-walden-yan-openinspect-s-cole-murray-01ksqydx2j6fv1xvpkw7kf8ft0.html`
