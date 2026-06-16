---
title: Tax AI Self-Improvement Loop for Crete Accountants
slug: tax-ai-self-improvement-loop-for-crete-accountants
category: implementation-study
tags:
- agent-systems
- human-ai-workflows
- software-engineering
- enterprise-ai
- workflow-automation
source_id: building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md
source_title: Building self-improving tax agents with Codex
source_date: '2026-05-27'
month: 2026-05
company: OpenAI and Thrive Holdings
industry: accounting
evidence_count: 24
evidence_set_hash: 64208c0e219c1d4c
---

# Tax AI Self-Improvement Loop for Crete Accountants

## Implementation Study

### Overview

OpenAI and Thrive Holdings co-developed Tax AI with Crete accountants and used production corrections, traces, and Codex-scoped engineering tasks to improve the system during the tax season. The deployment handled real tax-return preparation work across participating firms and was iteratively improved after launch.

### What was implemented?

A tax-preparation workflow that extracts fields from source documents, maps them into a tax engine submission, records practitioner corrections, and routes repeated failures into Codex-assisted eval and engineering loops.

### Business objective

Reduce manual tax-preparation work, increase throughput, and make the product improve from real production feedback instead of relying on engineers to inspect every failure manually.

### Technical approach

Practitioners upload source files and notes; the system produces a tax-engine submission with cited fields and provenance; production traces capture source material, extracted fields, downstream mapping, and practitioner corrections; repeated errors become targeted evals; Codex inspects the trace, evals, repo, and skills, then proposes and validates fixes.

### Deployment context

Deployed with Crete's network of 30+ accounting firms during the 2026 tax season; the system processed 7,000 tax returns across participating firms and expanded from simpler documents to more complex returns involving K-1s and schedules.

### Outcome / current status

Pilot and active rollout showed measurable self-improvement over six weeks, with the system moving from simpler filings into more complex ones while improving field-completion accuracy and throughput.

### Why it succeeded or struggled

Success depended on close practitioner involvement, trace-rich product instrumentation, and turning repeated corrections into bounded evals. The article also says ambiguous cases were routed back to the product team instead of being forced into automation.

### Operational constraints

Tax judgment is ambiguous in places, and a changed value can reflect extraction miss, mapper issue, carry-forward behavior, or workflow noise. The system was bounded to extraction and tax-engine mapping, while architecture and product decisions remained with engineers.

### AI / model observations

Codex is positioned as an engineering assistant inside a structured improvement loop rather than as a fully autonomous fixer. The case suggests that agentic improvement works best when the model can inspect traces, code paths, skills, and targeted evals together.

### Implications for service automation

For service automation, the key lesson is that human corrections become operationally useful only when the workflow preserves provenance and routes recurring issues into eval-backed fixes. The article's strongest implication is for expert review loops in narrow support and back-office workflows, not for fully hands-off automation.

### Strategic signals

The system is framed as a reusable blueprint for other bounded workflows, including bookkeeping, audit, and IT help desk automation. The broader strategic signal is that workflow quality and instrumentation can matter as much as model quality for domain automation.

### Key Lessons

- Capture provenance and intermediate outputs, not just final answers.
- Group repeated practitioner corrections before deciding what to automate.
- Keep ambiguous cases with humans instead of forcing them through the loop.
- Use targeted and regression evals to validate fixes before shipping.
- Bound the writable surface so the agent only changes the right parts of the system.

### Open Questions

- How much of the improvement came from better models versus better instrumentation or human training?
- How well does this loop transfer to domains with weaker ground truth or fewer practitioner corrections?
- What are the cost, privacy, and auditability tradeoffs at larger scale?

### Related Sources

- https://openai.com/index/building-self-improving-tax-agents-with-codex

### Evidence Snippets

- OpenAI and Thrive Holdings co-developed Tax AI with Crete accountants over six months. — "Over the past six months, OpenAI forward deployed engineers and researchers along with Thrive Holdings’ engineers collaborated to build Tax AI alongside and for Crete’s network of 30+ accounting firms" (stated)
- The system processed 7,000 tax returns during the pilot season. — "Tax AI processed 7,000 tax returns across the Crete firms that participated in the pilot this tax season." (stated)
- Production traces and Codex were used to turn corrections into eval-driven engineering tasks. — "Production traces (a structured history from inputs through final output), and a Codex-driven iteration loop based on tailored evals to enable continuous, faster product development." (stated)
- The loop depends on preserving provenance and practitioner corrections. — "The product has to capture more than just inputs and outputs; it needs to capture the full path from source material, to extracted fields and provenance, to downstream submission and expert correction." (stated)
- Ambiguous cases are routed back to the product team instead of being forced through automation. — "If the evidence is ambiguous or not safely automatable, the case routes back to the product team instead of being forced through the loop." (stated)

## Evidence / supporting sources

### Building self-improving tax agents with Codex (2026-05-27)

- Codex is positioned as an engineering assistant inside a structured improvement loop rather than as a fully autonomous fixer. The case suggests that agentic improvement works best when the model can inspect traces, code paths, skills, and targeted evals together. (`5662e05a80dd` · neutral · ai_model_observations; [[sources/building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md|Building self-improving tax agents with Codex]])
- Reduce manual tax-preparation work, increase throughput, and make the product improve from real production feedback instead of relying on engineers to inspect every failure manually. (`c6ffa5a3ede7` · neutral · business_objective; [[sources/building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md|Building self-improving tax agents with Codex]])
- Deployed with Crete's network of 30+ accounting firms during the 2026 tax season; the system processed 7,000 tax returns across participating firms and expanded from simpler documents to more complex returns involving K-1s and schedules. (`b2c73af8f1a5` · neutral · deployment_context; [[sources/building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md|Building self-improving tax agents with Codex]])
- For service automation, the key lesson is that human corrections become operationally useful only when the workflow preserves provenance and routes recurring issues into eval-backed fixes. The article's strongest implication is for expert review loops in narrow support and back-office workflows, not for fully hands-off automation. (`caaba2b50161` · neutral · implications_for_service_automation; [[sources/building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md|Building self-improving tax agents with Codex]])
- How much of the improvement came from better models versus better instrumentation or human training? (`542ba8fcd0e7` · neutral · open_questions[0]; [[sources/building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md|Building self-improving tax agents with Codex]])
- How well does this loop transfer to domains with weaker ground truth or fewer practitioner corrections? (`61dd0d5c3e8f` · neutral · open_questions[1]; [[sources/building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md|Building self-improving tax agents with Codex]])
- What are the cost, privacy, and auditability tradeoffs at larger scale? (`881f7f2fe603` · neutral · open_questions[2]; [[sources/building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md|Building self-improving tax agents with Codex]])
- Tax judgment is ambiguous in places, and a changed value can reflect extraction miss, mapper issue, carry-forward behavior, or workflow noise. The system was bounded to extraction and tax-engine mapping, while architecture and product decisions remained with engineers. (`48f999939a81` · neutral · operational_constraints; [[sources/building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md|Building self-improving tax agents with Codex]])
- Pilot and active rollout showed measurable self-improvement over six weeks, with the system moving from simpler filings into more complex ones while improving field-completion accuracy and throughput. (`528f613dd092` · neutral · outcome_status; [[sources/building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md|Building self-improving tax agents with Codex]])
- OpenAI and Thrive Holdings co-developed Tax AI with Crete accountants and used production corrections, traces, and Codex-scoped engineering tasks to improve the system during the tax season. The deployment handled real tax-return preparation work across participating firms and was iteratively improved after launch. (`ceae0a98db45` · neutral · overview; [[sources/building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md|Building self-improving tax agents with Codex]])
- The system is framed as a reusable blueprint for other bounded workflows, including bookkeeping, audit, and IT help desk automation. The broader strategic signal is that workflow quality and instrumentation can matter as much as model quality for domain automation. (`88e390035ffa` · neutral · strategic_signals; [[sources/building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md|Building self-improving tax agents with Codex]])
- Success depended on close practitioner involvement, trace-rich product instrumentation, and turning repeated corrections into bounded evals. The article also says ambiguous cases were routed back to the product team instead of being forced into automation. (`72c60cc265e9` · neutral · success_or_failure_factors; [[sources/building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md|Building self-improving tax agents with Codex]])
- Practitioners upload source files and notes; the system produces a tax-engine submission with cited fields and provenance; production traces capture source material, extracted fields, downstream mapping, and practitioner corrections; repeated errors become targeted evals; Codex inspects the trace, evals, repo, and skills, then proposes and validates fixes. (`8e7ad452f936` · neutral · technical_approach; [[sources/building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md|Building self-improving tax agents with Codex]])
- A tax-preparation workflow that extracts fields from source documents, maps them into a tax engine submission, records practitioner corrections, and routes repeated failures into Codex-assisted eval and engineering loops. (`d8de38b9a73a` · neutral · what_was_implemented; [[sources/building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md|Building self-improving tax agents with Codex]])
- OpenAI and Thrive Holdings co-developed Tax AI with Crete accountants over six months. — "Over the past six months, OpenAI forward deployed engineers and researchers along with Thrive Holdings’ engineers collaborated to build Tax AI alongside and for Crete’s network of 30+ accounting firms" (`c57554d41b25` · supporting · evidence_snippets[0]; [[sources/building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md|Building self-improving tax agents with Codex]])
- The system processed 7,000 tax returns during the pilot season. — "Tax AI processed 7,000 tax returns across the Crete firms that participated in the pilot this tax season." (`17a42454196c` · supporting · evidence_snippets[1]; [[sources/building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md|Building self-improving tax agents with Codex]])
- Production traces and Codex were used to turn corrections into eval-driven engineering tasks. — "Production traces (a structured history from inputs through final output), and a Codex-driven iteration loop based on tailored evals to enable continuous, faster product development." (`ddc403ef59e5` · supporting · evidence_snippets[2]; [[sources/building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md|Building self-improving tax agents with Codex]])
- The loop depends on preserving provenance and practitioner corrections. — "The product has to capture more than just inputs and outputs; it needs to capture the full path from source material, to extracted fields and provenance, to downstream submission and expert correction." (`19af0a1a2b57` · supporting · evidence_snippets[3]; [[sources/building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md|Building self-improving tax agents with Codex]])
- Ambiguous cases are routed back to the product team instead of being forced through automation. — "If the evidence is ambiguous or not safely automatable, the case routes back to the product team instead of being forced through the loop." (`6619f2a86857` · supporting · evidence_snippets[4]; [[sources/building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md|Building self-improving tax agents with Codex]])
- Capture provenance and intermediate outputs, not just final answers. (`4bbfb3467fc4` · supporting · key_lessons[0]; [[sources/building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md|Building self-improving tax agents with Codex]])
- Group repeated practitioner corrections before deciding what to automate. (`ce1ab40a6331` · supporting · key_lessons[1]; [[sources/building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md|Building self-improving tax agents with Codex]])
- Keep ambiguous cases with humans instead of forcing them through the loop. (`625b3ef6dd6e` · supporting · key_lessons[2]; [[sources/building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md|Building self-improving tax agents with Codex]])
- Use targeted and regression evals to validate fixes before shipping. (`bfab4058bc94` · supporting · key_lessons[3]; [[sources/building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md|Building self-improving tax agents with Codex]])
- Bound the writable surface so the agent only changes the right parts of the system. (`3b0536349fe0` · supporting · key_lessons[4]; [[sources/building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md|Building self-improving tax agents with Codex]])

## Source

- [[sources/building-self-improving-tax-agents-with-codex-01ksmwb7m6qzb7ehpmfm5z83md|Building self-improving tax agents with Codex]]
