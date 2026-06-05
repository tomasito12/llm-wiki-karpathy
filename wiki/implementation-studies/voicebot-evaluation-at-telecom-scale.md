---
title: Voicebot Evaluation at Telecom Scale
slug: voicebot-evaluation-at-telecom-scale
entity_id: impl_study:voicebot-evaluation-at-telecom-scale
category: implementation-study
tags:
- production-failure
- support-automation
first_seen: '2026-04-30'
last_seen: '2026-04-30'
source_count: 1
evidence_count: 23
source_ids:
- millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-01kqkyaqcyqgmyjjqs3r374v14
value_level: high
confidence: 0.95
synthesis_state: stage1-placeholder
---

# Voicebot Evaluation at Telecom Scale

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
A telecom voicebot deployed in production and handling millions of calls per year was evaluated with LLM-as-a-judge, automated scenarios, dashboards, and human review loops. The team redesigned evaluation around atomic binary checks and used a Golden Dataset to calibrate judges before shipping them to production.

## AI / model observations

LLM judges are useful only when their inputs are reliable. In this setup, the biggest source of evaluation error came from transcript quality, not prompt design.

## Business objective

Measure voicebot quality at production scale without listening to every call, while keeping business stakeholders confident that the bot was performing safely and usefully.

## Company / organization

Artefact and a major French telecom operator

## Deployment context

A conversational voicebot for a major telecom operator, already handling millions of calls per year in production. The evaluation system covered both offline calibration and online monitoring.

## Implications for service automation

This is directly relevant to support automation because it shows how to run quality control on a high-volume voicebot without relying on manual call listening. It also shows how to structure safety gates, live monitoring, and human review so automation can be corrected before failures spread.

## Industry / domain

telecom

## Key Lessons

- Break vague quality into atomic binary checks.
- Use a labeled Golden Dataset to calibrate judges before production.
- Keep an online safety net with kill switches, dashboards, and annotation queues.
- Benchmark transcription models early; transcript quality can dominate the error budget.
- Scenario tests should be paired with live monitoring because end-state validation misses messy intermediate paths.

## Open Questions

- How well does this evaluation design transfer to other languages, domains, or call mixes?
- How much human review capacity does the annotation queue require at scale?
- Can audio-native evaluation satisfy privacy and storage constraints for voice recordings?

## Operational constraints

Systematic human review was impossible at production call volumes. The bot also had to handle natural speech phenomena such as interruptions, hesitations, accents, and background noise, which complicate transcript-based evaluation. The article also notes GDPR and biometric-data constraints as a future constraint for audio-native evaluation.

## Outcome / current status

Ongoing production use with a human-in-the-loop monitoring system and continuous recalibration from real failures.

## Related Sources

- https://medium.com/artefact-engineering-and-data-science/millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-8c00f6ea6654

## Strategic signals

Production voice automation needs governance loops, not just model capability. Evaluation becomes part of the operating model when call volumes make manual review infeasible.

## Why it succeeded or struggled

The approach worked because it decomposed fuzzy quality into small checks, paired offline calibration with live safeguards, and treated transcription quality as a core dependency. The main failure mode was not the judge itself but degraded transcription upstream.

## Technical approach

The team moved from vague human-style scorecards to 29 binary metrics evaluated by LLM judges on transcripts. They calibrated those judges on 500 stratified conversations, ran scripted bot-vs-bot scenarios before release, and monitored live traffic with dashboards, kill switches, and a human annotation loop.

## Evidence / supporting sources

### Millions of Calls, One Judge: How We Evaluated Our Voicebot in Production (2026-04-30)

- LLM judges are useful only when their inputs are reliable. In this setup, the biggest source of evaluation error came from transcript quality, not prompt design. (`9fef5ae2c72d` · neutral · ai_model_observations; [[sources/millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-01kqkyaqcyqgmyjjqs3r374v14|Millions of Calls, One Judge: How We Evaluated Our Voicebot in Production]])
- Measure voicebot quality at production scale without listening to every call, while keeping business stakeholders confident that the bot was performing safely and usefully. (`2685684bfacd` · neutral · business_objective; [[sources/millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-01kqkyaqcyqgmyjjqs3r374v14|Millions of Calls, One Judge: How We Evaluated Our Voicebot in Production]])
- A conversational voicebot for a major telecom operator, already handling millions of calls per year in production. The evaluation system covered both offline calibration and online monitoring. (`d93b85bbec82` · neutral · deployment_context; [[sources/millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-01kqkyaqcyqgmyjjqs3r374v14|Millions of Calls, One Judge: How We Evaluated Our Voicebot in Production]])
- This is directly relevant to support automation because it shows how to run quality control on a high-volume voicebot without relying on manual call listening. It also shows how to structure safety gates, live monitoring, and human review so automation can be corrected before failures spread. (`9b586fbbd544` · neutral · implications_for_service_automation; [[sources/millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-01kqkyaqcyqgmyjjqs3r374v14|Millions of Calls, One Judge: How We Evaluated Our Voicebot in Production]])
- How well does this evaluation design transfer to other languages, domains, or call mixes? (`46ef510ab224` · neutral · open_questions[0]; [[sources/millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-01kqkyaqcyqgmyjjqs3r374v14|Millions of Calls, One Judge: How We Evaluated Our Voicebot in Production]])
- How much human review capacity does the annotation queue require at scale? (`f717e81e03cf` · neutral · open_questions[1]; [[sources/millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-01kqkyaqcyqgmyjjqs3r374v14|Millions of Calls, One Judge: How We Evaluated Our Voicebot in Production]])
- Can audio-native evaluation satisfy privacy and storage constraints for voice recordings? (`911c7ffb8dd3` · neutral · open_questions[2]; [[sources/millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-01kqkyaqcyqgmyjjqs3r374v14|Millions of Calls, One Judge: How We Evaluated Our Voicebot in Production]])
- Systematic human review was impossible at production call volumes. The bot also had to handle natural speech phenomena such as interruptions, hesitations, accents, and background noise, which complicate transcript-based evaluation. The article also notes GDPR and biometric-data constraints as a future constraint for audio-native evaluation. (`5599bf08e5d6` · neutral · operational_constraints; [[sources/millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-01kqkyaqcyqgmyjjqs3r374v14|Millions of Calls, One Judge: How We Evaluated Our Voicebot in Production]])
- Ongoing production use with a human-in-the-loop monitoring system and continuous recalibration from real failures. (`6be156d5f73b` · neutral · outcome_status; [[sources/millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-01kqkyaqcyqgmyjjqs3r374v14|Millions of Calls, One Judge: How We Evaluated Our Voicebot in Production]])
- A telecom voicebot deployed in production and handling millions of calls per year was evaluated with LLM-as-a-judge, automated scenarios, dashboards, and human review loops. The team redesigned evaluation around atomic binary checks and used a Golden Dataset to calibrate judges before shipping them to production. (`6a4ab19f4ee2` · neutral · overview; [[sources/millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-01kqkyaqcyqgmyjjqs3r374v14|Millions of Calls, One Judge: How We Evaluated Our Voicebot in Production]])
- Production voice automation needs governance loops, not just model capability. Evaluation becomes part of the operating model when call volumes make manual review infeasible. (`38b241197e4b` · neutral · strategic_signals; [[sources/millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-01kqkyaqcyqgmyjjqs3r374v14|Millions of Calls, One Judge: How We Evaluated Our Voicebot in Production]])
- The approach worked because it decomposed fuzzy quality into small checks, paired offline calibration with live safeguards, and treated transcription quality as a core dependency. The main failure mode was not the judge itself but degraded transcription upstream. (`812102f5eb0f` · neutral · success_or_failure_factors; [[sources/millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-01kqkyaqcyqgmyjjqs3r374v14|Millions of Calls, One Judge: How We Evaluated Our Voicebot in Production]])
- The team moved from vague human-style scorecards to 29 binary metrics evaluated by LLM judges on transcripts. They calibrated those judges on 500 stratified conversations, ran scripted bot-vs-bot scenarios before release, and monitored live traffic with dashboards, kill switches, and a human annotation loop. (`34f57185235c` · neutral · technical_approach; [[sources/millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-01kqkyaqcyqgmyjjqs3r374v14|Millions of Calls, One Judge: How We Evaluated Our Voicebot in Production]])
- An end-to-end production evaluation system for a speech-to-speech voicebot, including atomic binary judges, a stratified Golden Dataset, scripted bot-vs-bot scenarios, live dashboards, kill switches, and an annotation queue feeding failures back into training data. (`274e3523336f` · neutral · what_was_implemented; [[sources/millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-01kqkyaqcyqgmyjjqs3r374v14|Millions of Calls, One Judge: How We Evaluated Our Voicebot in Production]])
- The system was used on a live telecom voicebot handling production traffic at large scale. — "our voicebot does, it is a conversational voicebot deployed for a major telecom operator, currently handling millions of calls per year in production." (`0f6c86699f63` · supporting · evidence_snippets[0]; [[sources/millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-01kqkyaqcyqgmyjjqs3r374v14|Millions of Calls, One Judge: How We Evaluated Our Voicebot in Production]])
- The team used a two-loop evaluation structure with offline calibration and online monitoring. — "Our evaluation system rests on two pillars: an Offline lab and an Online safety net." (`b5b3117a6676` · supporting · evidence_snippets[1]; [[sources/millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-01kqkyaqcyqgmyjjqs3r374v14|Millions of Calls, One Judge: How We Evaluated Our Voicebot in Production]])
- The Golden Dataset calibrated judges before production shipment. — "Only once a metric reaches that alignment threshold on the Golden Dataset do we authorize it to ship to production." (`f85bff5e3f1e` · supporting · evidence_snippets[2]; [[sources/millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-01kqkyaqcyqgmyjjqs3r374v14|Millions of Calls, One Judge: How We Evaluated Our Voicebot in Production]])
- Transcription quality was a major operational constraint. — "The biggest source of evaluation error wasn’t the judge — it was the transcription." (`fd0e44b24c61` · supporting · evidence_snippets[3]; [[sources/millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-01kqkyaqcyqgmyjjqs3r374v14|Millions of Calls, One Judge: How We Evaluated Our Voicebot in Production]])
- Break vague quality into atomic binary checks. (`0b0ce8a0eb9c` · supporting · key_lessons[0]; [[sources/millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-01kqkyaqcyqgmyjjqs3r374v14|Millions of Calls, One Judge: How We Evaluated Our Voicebot in Production]])
- Use a labeled Golden Dataset to calibrate judges before production. (`ce877d8dbb1e` · supporting · key_lessons[1]; [[sources/millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-01kqkyaqcyqgmyjjqs3r374v14|Millions of Calls, One Judge: How We Evaluated Our Voicebot in Production]])
- Keep an online safety net with kill switches, dashboards, and annotation queues. (`b84d4e41e060` · supporting · key_lessons[2]; [[sources/millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-01kqkyaqcyqgmyjjqs3r374v14|Millions of Calls, One Judge: How We Evaluated Our Voicebot in Production]])
- Benchmark transcription models early; transcript quality can dominate the error budget. (`8a7ddbe907a8` · supporting · key_lessons[3]; [[sources/millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-01kqkyaqcyqgmyjjqs3r374v14|Millions of Calls, One Judge: How We Evaluated Our Voicebot in Production]])
- Scenario tests should be paired with live monitoring because end-state validation misses messy intermediate paths. (`6b78fac26881` · supporting · key_lessons[4]; [[sources/millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-01kqkyaqcyqgmyjjqs3r374v14|Millions of Calls, One Judge: How We Evaluated Our Voicebot in Production]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- https://medium.com/artefact-engineering-and-data-science/millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-8c00f6ea6654

## Sources

- [[sources/millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-01kqkyaqcyqgmyjjqs3r374v14|Millions of Calls, One Judge: How We Evaluated Our Voicebot in Production]]
