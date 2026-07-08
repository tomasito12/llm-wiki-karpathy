---
title: Intent-Driven Chaos Engineering
slug: intent-driven-chaos-engineering
entity_id: topic:intent-driven-chaos-engineering
category: topic
tags:
- ai-engineering
- ai-evaluation
- intent-based-testing
- runtime-architecture
first_seen: '2026-04-28'
last_seen: '2026-04-28'
source_count: 1
evidence_count: 10
source_ids:
- the-next-frontier-of-ai-in-production-is-chaos-engineering-01krkb7np7mz3q1weya69wvnvv
value_level: high
confidence: 0.96
synthesis_state: stage1-placeholder
---

# Intent-Driven Chaos Engineering

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Chaos engineering is the practice of deliberately injecting failures into a system to test resilience under controlled conditions. Intent-driven chaos engineering extends that practice by specifying what an experiment is meant to teach: a falsifiable hypothesis about system behavior, behavioral acceptance criteria, exclusion zones, and a required steady-state window before injection. The article argues that current chaos tooling is strong on safety, but weak on intent: it can answer whether it is safe to run an experiment, but not whether the experiment was designed to validate a specific belief about failure propagation. The proposed model uses machine-readable intent to derive experiments, evaluate live resilience budgets, and record outcomes so the system’s dependency model improves over time.

## Key Points

- Safety and informativeness are different design problems: an experiment can be safe and still teach nothing.
- A useful chaos experiment should validate a specific belief about behavior, not only break a component.
- Intent specifications can include hypothesis, acceptance criteria, exclusion zones, and a steady-state window.
- Live topology and learned dependency weights can guide which fault to inject next.
- Outcome records should update the dependency model, including discovered dependencies and blast-radius prediction errors.
- Static scripts drift as systems and traffic patterns change; intent helps keep experiments meaningful.

## Operational Insight

Treat chaos runs as hypothesis tests, not just fault injections: encode target behavior, success criteria, and exclusions up front, then feed observed blast-radius and outcome data back into the model so future experiments become more informative.

## Evidence / supporting sources

### The Next Frontier of AI in Production Is Chaos Engineering (2026-04-28)

- Chaos engineering is the practice of deliberately injecting failures into a system to test resilience under controlled conditions. Intent-driven chaos engineering extends that practice by specifying what an experiment is meant to teach: a falsifiable hypothesis about system behavior, behavioral acceptance criteria, exclusion zones, and a required steady-state window before injection. The article argues that current chaos tooling is strong on safety, but weak on intent: it can answer whether it is safe to run an experiment, but not whether the experiment was designed to validate a specific belief about failure propagation. The proposed model uses machine-readable intent to derive experiments, evaluate live resilience budgets, and record outcomes so the system’s dependency model improves over time. (`1c217d51cd29` · neutral · knowledge_summary; [[sources/the-next-frontier-of-ai-in-production-is-chaos-engineering-01krkb7np7mz3q1weya69wvnvv|The Next Frontier of AI in Production Is Chaos Engineering]])
- Treat chaos runs as hypothesis tests, not just fault injections: encode target behavior, success criteria, and exclusions up front, then feed observed blast-radius and outcome data back into the model so future experiments become more informative. (`fa52ec12094b` · neutral · operational_insight; [[sources/the-next-frontier-of-ai-in-production-is-chaos-engineering-01krkb7np7mz3q1weya69wvnvv|The Next Frontier of AI in Production Is Chaos Engineering]])
- For production AI and agentic systems, reliability testing is most valuable when it validates a user-facing behavior or operational assumption, not merely whether a component survives. Intent-driven chaos engineering is relevant wherever resilience work needs machine-readable goals, adaptive experiment selection, and learning from outcomes rather than static failure scripts. (`0df4171fa913` · neutral · relevance_note; [[sources/the-next-frontier-of-ai-in-production-is-chaos-engineering-01krkb7np7mz3q1weya69wvnvv|The Next Frontier of AI in Production Is Chaos Engineering]])
- Safety and informativeness are different design problems: an experiment can be safe and still teach nothing. (`1602f55a3825` · supporting · key_points[0]; [[sources/the-next-frontier-of-ai-in-production-is-chaos-engineering-01krkb7np7mz3q1weya69wvnvv|The Next Frontier of AI in Production Is Chaos Engineering]])
- A useful chaos experiment should validate a specific belief about behavior, not only break a component. (`2d600ff15db7` · supporting · key_points[1]; [[sources/the-next-frontier-of-ai-in-production-is-chaos-engineering-01krkb7np7mz3q1weya69wvnvv|The Next Frontier of AI in Production Is Chaos Engineering]])
- Intent specifications can include hypothesis, acceptance criteria, exclusion zones, and a steady-state window. (`7cbfa7e397d2` · supporting · key_points[2]; [[sources/the-next-frontier-of-ai-in-production-is-chaos-engineering-01krkb7np7mz3q1weya69wvnvv|The Next Frontier of AI in Production Is Chaos Engineering]])
- Live topology and learned dependency weights can guide which fault to inject next. (`2e12aa6436d0` · supporting · key_points[3]; [[sources/the-next-frontier-of-ai-in-production-is-chaos-engineering-01krkb7np7mz3q1weya69wvnvv|The Next Frontier of AI in Production Is Chaos Engineering]])
- Outcome records should update the dependency model, including discovered dependencies and blast-radius prediction errors. (`5e916f861e2b` · supporting · key_points[4]; [[sources/the-next-frontier-of-ai-in-production-is-chaos-engineering-01krkb7np7mz3q1weya69wvnvv|The Next Frontier of AI in Production Is Chaos Engineering]])
- Static scripts drift as systems and traffic patterns change; intent helps keep experiments meaningful. (`1490132fa037` · supporting · key_points[5]; [[sources/the-next-frontier-of-ai-in-production-is-chaos-engineering-01krkb7np7mz3q1weya69wvnvv|The Next Frontier of AI in Production Is Chaos Engineering]])
- "The question is whether the experiment was designed to validate a specific belief about your system’s behavior, and whether its outcome changed what your team knows about failure propagation through your stack. ... Chaos engineering has a mature safety layer and an almost nonexistent intent layer. Safety tells you how much to break. Intent tells you what breaking it will teach. These are different design problems requiring different tooling." (`6991c6eb9762` · supporting · supporting_snippet; [[sources/the-next-frontier-of-ai-in-production-is-chaos-engineering-01krkb7np7mz3q1weya69wvnvv|The Next Frontier of AI in Production Is Chaos Engineering]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- [[topics/harness-decay|Harness Decay]]
- [[topics/provenance-tracking|Provenance Tracking]]
- [[topics/behavioral-blast-radius-evaluation|Behavioral Blast Radius Evaluation]]

## Sources

- [[sources/the-next-frontier-of-ai-in-production-is-chaos-engineering-01krkb7np7mz3q1weya69wvnvv|The Next Frontier of AI in Production Is Chaos Engineering]]
