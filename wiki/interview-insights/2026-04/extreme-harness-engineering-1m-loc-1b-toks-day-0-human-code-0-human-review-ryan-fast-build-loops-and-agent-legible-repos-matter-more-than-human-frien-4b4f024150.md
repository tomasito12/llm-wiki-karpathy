---
title: Fast build loops and agent-legible repos matter more than human-friendly structure
slug: fast-build-loops-and-agent-legible-repos-matter-more-than-human-friendly-structure
category: insight
tags:
- agent-systems
- runtime-architecture
- developer-tooling
- test-and-verification
source_id: extreme-harness-engineering-1m-loc-1b-toks-day-0-human-code-0-human-review-ryan-lopopolo-openai-frontier-symphony-01knmf4r6yqgf92rpgng02z3wy
source_title: 'Extreme Harness Engineering: 1M LOC, 1B toks/day, 0% human code, 0%
  human review — Ryan Lopopolo, OpenAI Frontier & Symphony'
source_date: '2026-04-07'
month: 2026-04
evidence_count: 8
evidence_set_hash: 804c34d9da7cccdf
insight_title: Fast build loops and agent-legible repos matter more than human-friendly
  structure
insight_type: infrastructure
confidence: high
durability_estimate: long_term
wiki_worthiness: strong_candidate
---

# Fast build loops and agent-legible repos matter more than human-friendly structure

## Interview Insight

### Summary

The team repeatedly reworked the repository and build system so the agent could stay productive, including pushing builds under one minute and shifting toward background-shell-friendly workflows. Ryan’s view is that reasoning models work better when the harness is the box and the model chooses how to proceed, rather than being constrained by a rigid scaffold. The repo was also made highly decomposed so people and agents would not trample each other.

### Why It Matters

As of 2026-04-07, this is a reusable engineering lesson for agent-heavy repos: build latency, decomposition, and observability are product constraints, not just developer conveniences. The article grounds this in concrete changes like moving from bespoke makefiles to faster build systems and redesigning local dev around the model. It is valuable because it ties model behavior to software architecture choices in a way practitioners can act on.

### Operational Relevance

Use one-minute-or-better build loops where possible, favor explicit observability, and keep repo structure consistent enough that agents can navigate it without deep context switching. If a model is stalling, the fix may be to simplify the build graph or expose a better primitive, not to prompt harder. This is especially relevant for large multi-agent or multi-engineer repos where coordination cost compounds.

### Service Automation Relevance

For support automation, the analog is to keep tool chains quick, inspectable, and composable so the agent can resolve issues without waiting on humans. Fast feedback loops also matter for incident handling and ticket triage, where slow tool responses increase escalation and reduce automation reliability.

### Mentioned Entities

- Codex
- Turbo
- Nx
- Bazel

### Suggested Destinations

- topics/

### Contrarian Or Speculative Claims

- The claim that a one-minute build loop is the right operating constraint is specific to this repo and team; it is presented as a successful practice, not a universal rule.

### Evidence Snippets

- "we had to retool the entire build system to complete in under a minute"
- "the model, the harness be the whole box"
- "we have, I think, six skills. That’s it."

## Evidence / supporting sources

### Extreme Harness Engineering: 1M LOC, 1B toks/day, 0% human code, 0% human review — Ryan Lopopolo, OpenAI Frontier & Symphony (2026-04-07)

- The claim that a one-minute build loop is the right operating constraint is specific to this repo and team; it is presented as a successful practice, not a universal rule. (`5f8a4001fc81` · counter · contrarian_or_speculative_claims[0]; [[sources/extreme-harness-engineering-1m-loc-1b-toks-day-0-human-code-0-human-review-ryan-lopopolo-openai-frontier-symphony-01knmf4r6yqgf92rpgng02z3wy|Extreme Harness Engineering: 1M LOC, 1B toks/day, 0% human code, 0% human review — Ryan Lopopolo, OpenAI Frontier & Symphony]])
- Use one-minute-or-better build loops where possible, favor explicit observability, and keep repo structure consistent enough that agents can navigate it without deep context switching. If a model is stalling, the fix may be to simplify the build graph or expose a better primitive, not to prompt harder. This is especially relevant for large multi-agent or multi-engineer repos where coordination cost compounds. (`fb1ca8cf8851` · neutral · operational_relevance; [[sources/extreme-harness-engineering-1m-loc-1b-toks-day-0-human-code-0-human-review-ryan-lopopolo-openai-frontier-symphony-01knmf4r6yqgf92rpgng02z3wy|Extreme Harness Engineering: 1M LOC, 1B toks/day, 0% human code, 0% human review — Ryan Lopopolo, OpenAI Frontier & Symphony]])
- For support automation, the analog is to keep tool chains quick, inspectable, and composable so the agent can resolve issues without waiting on humans. Fast feedback loops also matter for incident handling and ticket triage, where slow tool responses increase escalation and reduce automation reliability. (`8d66d16097de` · neutral · service_automation_relevance; [[sources/extreme-harness-engineering-1m-loc-1b-toks-day-0-human-code-0-human-review-ryan-lopopolo-openai-frontier-symphony-01knmf4r6yqgf92rpgng02z3wy|Extreme Harness Engineering: 1M LOC, 1B toks/day, 0% human code, 0% human review — Ryan Lopopolo, OpenAI Frontier & Symphony]])
- The team repeatedly reworked the repository and build system so the agent could stay productive, including pushing builds under one minute and shifting toward background-shell-friendly workflows. Ryan’s view is that reasoning models work better when the harness is the box and the model chooses how to proceed, rather than being constrained by a rigid scaffold. The repo was also made highly decomposed so people and agents would not trample each other. (`b39d98b1d488` · neutral · summary; [[sources/extreme-harness-engineering-1m-loc-1b-toks-day-0-human-code-0-human-review-ryan-lopopolo-openai-frontier-symphony-01knmf4r6yqgf92rpgng02z3wy|Extreme Harness Engineering: 1M LOC, 1B toks/day, 0% human code, 0% human review — Ryan Lopopolo, OpenAI Frontier & Symphony]])
- As of 2026-04-07, this is a reusable engineering lesson for agent-heavy repos: build latency, decomposition, and observability are product constraints, not just developer conveniences. The article grounds this in concrete changes like moving from bespoke makefiles to faster build systems and redesigning local dev around the model. It is valuable because it ties model behavior to software architecture choices in a way practitioners can act on. (`e534eaa631d1` · neutral · why_it_matters; [[sources/extreme-harness-engineering-1m-loc-1b-toks-day-0-human-code-0-human-review-ryan-lopopolo-openai-frontier-symphony-01knmf4r6yqgf92rpgng02z3wy|Extreme Harness Engineering: 1M LOC, 1B toks/day, 0% human code, 0% human review — Ryan Lopopolo, OpenAI Frontier & Symphony]])
- "we had to retool the entire build system to complete in under a minute" (`f4ed803f85ca` · supporting · evidence_snippets[0]; [[sources/extreme-harness-engineering-1m-loc-1b-toks-day-0-human-code-0-human-review-ryan-lopopolo-openai-frontier-symphony-01knmf4r6yqgf92rpgng02z3wy|Extreme Harness Engineering: 1M LOC, 1B toks/day, 0% human code, 0% human review — Ryan Lopopolo, OpenAI Frontier & Symphony]])
- "the model, the harness be the whole box" (`ce5938d9b5a8` · supporting · evidence_snippets[1]; [[sources/extreme-harness-engineering-1m-loc-1b-toks-day-0-human-code-0-human-review-ryan-lopopolo-openai-frontier-symphony-01knmf4r6yqgf92rpgng02z3wy|Extreme Harness Engineering: 1M LOC, 1B toks/day, 0% human code, 0% human review — Ryan Lopopolo, OpenAI Frontier & Symphony]])
- "we have, I think, six skills. That’s it." (`5975bb5bb502` · supporting · evidence_snippets[2]; [[sources/extreme-harness-engineering-1m-loc-1b-toks-day-0-human-code-0-human-review-ryan-lopopolo-openai-frontier-symphony-01knmf4r6yqgf92rpgng02z3wy|Extreme Harness Engineering: 1M LOC, 1B toks/day, 0% human code, 0% human review — Ryan Lopopolo, OpenAI Frontier & Symphony]])

## Source

- [[sources/extreme-harness-engineering-1m-loc-1b-toks-day-0-human-code-0-human-review-ryan-lopopolo-openai-frontier-symphony-01knmf4r6yqgf92rpgng02z3wy|Extreme Harness Engineering: 1M LOC, 1B toks/day, 0% human code, 0% human review — Ryan Lopopolo, OpenAI Frontier & Symphony]]
