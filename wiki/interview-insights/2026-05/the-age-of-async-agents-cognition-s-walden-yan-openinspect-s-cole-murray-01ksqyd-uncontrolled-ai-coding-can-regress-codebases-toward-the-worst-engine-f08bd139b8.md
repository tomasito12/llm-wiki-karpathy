---
title: Uncontrolled AI coding can regress codebases toward the worst engineer's habits
slug: uncontrolled-ai-coding-can-regress-codebases-toward-the-worst-engineer-s-habits
category: insight
tags:
- behavioral-drift
- coding-agents
- ai-evaluation
- software-engineering
source_id: the-age-of-async-agents-cognition-s-walden-yan-openinspect-s-cole-murray-01ksqydx2j6fv1xvpkw7kf8ft0
source_title: The Age of Async Agents — Cognition's Walden Yan & OpenInspect's Cole
  Murray
source_date: '2026-05-28'
month: 2026-05
evidence_count: 4
evidence_set_hash: c7d3acdd5c4a10f2
insight_title: Uncontrolled AI coding can regress codebases toward the worst engineer's
  habits
insight_type: topic
confidence: high
durability_estimate: long_term
wiki_worthiness: strong_candidate
---

# Uncontrolled AI coding can regress codebases toward the worst engineer's habits

## Interview Insight

### Summary

The speakers warn that codebases can degrade when AI-generated changes are accepted without review. Cole’s formulation is that a codebase can regress toward the patterns of its least careful engineer, because the model starts learning from bad local examples and amplifying them. Their countermeasures are code review, scheduled cleanup, lint rules, and explicit boundaries between modules.

### Why It Matters

As of 2026-05-28, this is a practical anti-hype lesson for agentic development. The risk is not only bad one-off outputs; it is cumulative style and structure drift that makes future generations worse, so governance and cleanup become part of the engineering loop.

### Operational Relevance

Teams adopting coding agents should add guardrails such as linters, static checks, review stages, and periodic refactors. The insight also supports strict module contracts and human sign-off at boundary changes.

### Service Automation Relevance

Indirectly relevant: support and ops automations that can write or modify code can also accumulate bad patterns, so review and cleanup loops matter outside pure software engineering.

## Evidence / supporting sources

### The Age of Async Agents — Cognition's Walden Yan & OpenInspect's Cole Murray (2026-05-28)

- Teams adopting coding agents should add guardrails such as linters, static checks, review stages, and periodic refactors. The insight also supports strict module contracts and human sign-off at boundary changes. (`34575a868c81` · neutral · operational_relevance; [[sources/the-age-of-async-agents-cognition-s-walden-yan-openinspect-s-cole-murray-01ksqydx2j6fv1xvpkw7kf8ft0|The Age of Async Agents — Cognition's Walden Yan & OpenInspect's Cole Murray]])
- Indirectly relevant: support and ops automations that can write or modify code can also accumulate bad patterns, so review and cleanup loops matter outside pure software engineering. (`9633ed236689` · neutral · service_automation_relevance; [[sources/the-age-of-async-agents-cognition-s-walden-yan-openinspect-s-cole-murray-01ksqydx2j6fv1xvpkw7kf8ft0|The Age of Async Agents — Cognition's Walden Yan & OpenInspect's Cole Murray]])
- The speakers warn that codebases can degrade when AI-generated changes are accepted without review. Cole’s formulation is that a codebase can regress toward the patterns of its least careful engineer, because the model starts learning from bad local examples and amplifying them. Their countermeasures are code review, scheduled cleanup, lint rules, and explicit boundaries between modules. (`eba2a04c19a7` · neutral · summary; [[sources/the-age-of-async-agents-cognition-s-walden-yan-openinspect-s-cole-murray-01ksqydx2j6fv1xvpkw7kf8ft0|The Age of Async Agents — Cognition's Walden Yan & OpenInspect's Cole Murray]])
- As of 2026-05-28, this is a practical anti-hype lesson for agentic development. The risk is not only bad one-off outputs; it is cumulative style and structure drift that makes future generations worse, so governance and cleanup become part of the engineering loop. (`fa1f1ed417eb` · neutral · why_it_matters; [[sources/the-age-of-async-agents-cognition-s-walden-yan-openinspect-s-cole-murray-01ksqydx2j6fv1xvpkw7kf8ft0|The Age of Async Agents — Cognition's Walden Yan & OpenInspect's Cole Murray]])

## Source

- [[sources/the-age-of-async-agents-cognition-s-walden-yan-openinspect-s-cole-murray-01ksqydx2j6fv1xvpkw7kf8ft0|The Age of Async Agents — Cognition's Walden Yan & OpenInspect's Cole Murray]]
