---
title: Building self-improving tax agents with Codex
slug: building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md
category: source
tags:
- agent-systems
- ai-engineering
- ai-evaluation
- ai-operationalization
- auditability
- continuous-evaluation
- enterprise-ai
- human-ai-workflows
- software-engineering
- verification-over-principles
- verification-systems
- workflow-automation
- workflow-design
- workflow-restructuring
source_id: building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md
author: OpenAI Blog
publication: openai.com
published_date: '2026-05-27'
assessed_as_of: '2026-05-27'
ingested_at: '2026-06-06T21:44:59+00:00'
canonical_url: https://openai.com/index/building-self-improving-tax-agents-with-codex
content_sha256: ee8cc3323d4e535e9970fc4b11cab8ba553edff1eb2171426cd3a59efa1b3129
derived_implementation_studies:
- implementation-studies/2026-05/building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md-tax-ai-self-improvement-loop-for-crete-accountants.md
derived_topics:
- topics/practitioner-feedback-loops-for-agents.md
- topics/production-traceability-for-agent-improvement.md
derived_trends:
- industry-trends/ai-workflows-shift-toward-verification-loops.md
derived_pages:
- implementation-studies/2026-05/building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md-tax-ai-self-improvement-loop-for-crete-accountants.md
- industry-trends/ai-workflows-shift-toward-verification-loops.md
- topics/practitioner-feedback-loops-for-agents.md
- topics/production-traceability-for-agent-improvement.md
---

# Building self-improving tax agents with Codex

This piece is about making an AI agent improve from real work, not just from offline testing. OpenAI and Thrive Holdings used accounting work from Crete firms to build Tax AI, then fed practitioner corrections and production traces back into the system. Codex was used to turn repeated mistakes into focused engineering tasks and evals. The interesting part is the loop: people do the work, the product records the failure, and the model helps fix the right part of the pipeline. OpenAI says this improved speed, accuracy, and throughput over the tax season. The article is most useful as an example of how to build feedback-driven agent workflows in a narrow, well-instrumented domain.

## Key insights

- A self-improving agent needs production traces that preserve provenance, not just input/output pairs, or repeated mistakes remain ambiguous.
- Practitioner corrections are only useful once they are grouped into actionable failure patterns; single edits can reflect workflow noise, tax judgment, or product gaps.
- Codex is presented as an engineering assistant inside a bounded loop: inspect traces and repo code, propose a fix, and validate against targeted plus regression evals.
- The article’s strongest operational claim is measurable improvement over six weeks, including a rise from 25% to 86% at the 75% correct-field-completion threshold.
- The pattern is explicitly bounded to extraction and tax-engine mapping; architecture decisions and ambiguous cases stay with human engineers.

## Derived knowledge pages

- [[implementation-studies/2026-05/building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md-tax-ai-self-improvement-loop-for-crete-accountants]]
- [[industry-trends/ai-workflows-shift-toward-verification-loops]]
- [[topics/practitioner-feedback-loops-for-agents]]
- [[topics/production-traceability-for-agent-improvement]]

## Why it matters

This article matters because it gives a concrete, production-oriented pattern for building agents that improve from real work instead of from occasional prompt tuning. The main engineering lesson is not “use an LLM better,” but “instrument the workflow so failures become structured evidence.” OpenAI’s example shows a useful decomposition: capture source files, extracted fields, mapper behavior, and final practitioner edits; then convert repeated corrections into eval targets that an agent can work against. That is a more durable pattern than ad hoc debugging because it creates a repeatable path from production pain to testable code changes. The article also ties agent quality to human expertise in a way that is operational, not rhetorical: practitioners decide which errors matter and which corrections are just workflow noise. The rental-property walkthrough is especially valuable because it explains the mechanics of turning one correction into a scoped task with success criteria, rather than treating production feedback as a vague alert. The reported results are meaningful but still case-specific: a 7,000-return pilot, time savings, throughput gains, and improved field completion are useful evidence, but they come from a single vendor-run deployment in one accounting workflow. As of 2026-05-27, this is actionable as a design pattern for tightly bounded, heavily instrumented workflows; it is better treated as a strong implementation case than as proof that self-improving agents generalize broadly.

## Limitations / open questions

The evidence is a single OpenAI-led case study in one tax-preparation deployment, so the results may not transfer to less structured or less supervised domains. The article reports gains such as 97% draft accuracy, 50% higher throughput, and 25% to 86% movement at a 75% field-completion threshold, but it does not provide a full methodology, baseline definitions, or error bars. It is unclear how much of the improvement came from better models versus better workflow instrumentation, better practitioner training, or narrowing the task to bounded extraction and mapping. The article does not quantify cost, security, privacy, auditability, or failure severity when incorrect tax outputs slip through. It also leaves open how much human review is still required for ambiguous cases, and whether the same feedback loop would remain effective outside a domain with strong ground truth and dense practitioner corrections.

## Contradictions / unverified claims

The piece is persuasive about the loop design, but it is also promotional and written by the system builder, so the strongest claims deserve independent validation. The term "self-improving" can overstate what is described here: the system appears to improve through carefully engineered evaluation and routing infrastructure, with humans still deciding what counts as actionable evidence. The article implies portability to other domains such as bookkeeping, audit, and IT help desk automation, but it does not show comparable evidence for those settings. The fact that ambiguous cases are routed back to engineers is a useful safeguard, but it also means the loop is not fully autonomous in the strong sense the headline might suggest.

## Source metadata

- Canonical URL: https://openai.com/index/building-self-improving-tax-agents-with-codex
- Raw markdown: `raw/readwise/building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md.md`
- Raw HTML: `raw/readwise/building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md.html`
