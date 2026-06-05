---
title: Machine-Readable Testing Intent
slug: machine-readable-testing-intent
entity_id: trend:machine-readable-testing-intent
category: industry-trend
tags:
- ai-infrastructure
first_seen: '2026-04-28'
last_seen: '2026-04-28'
source_count: 1
evidence_count: 8
source_ids:
- the-next-frontier-of-ai-in-production-is-chaos-engineering-01krkb7np7mz3q1weya69wvnvv
value_level: medium
confidence: 0.88
synthesis_state: stage1-placeholder
maturity: unknown
---

# Machine-Readable Testing Intent

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Chaos engineering may evolve beyond blast-radius control toward machine-readable testing intent: a structured hypothesis layer that specifies what behavior is being validated, what counts as success, what budget and exclusion constraints apply, and what outcome data should be captured. The broader pattern is not the fault-injection script itself, but encoding experiment intent so tooling can validate, execute, and learn from tests in a computable way.

## Related Trends

- harness-design-becomes-more-important-for-agent-reliability

## Supporting Data Points

- Proposed schema fields include target_behavior, hypothesis, acceptance_criteria, budget_fraction, and exclusion_zones.
- The article says structured experiment outcomes are needed as training data.
- It proposes a hypothesis-quality score to measure whether a run changed the team's belief about the system.

## Time sensitivity

Actionable now as a proposed architecture and schema gap, but not yet shown as a widely adopted industry standard. The signal is about a tooling and data-model opportunity rather than an established market shift.

## Uncertainty / maturity

The source is a persuasive architecture argument, not adoption evidence. It is unclear whether teams will converge on one standard schema, whether intent records will stay up to date as systems change, and whether outcome data will be structured consistently enough to support reliable learning across organizations.

## Evidence / supporting sources

### The Next Frontier of AI in Production Is Chaos Engineering (2026-04-28)

- Chaos engineering may evolve beyond blast-radius control toward machine-readable testing intent: a structured hypothesis layer that specifies what behavior is being validated, what counts as success, what budget and exclusion constraints apply, and what outcome data should be captured. The broader pattern is not the fault-injection script itself, but encoding experiment intent so tooling can validate, execute, and learn from tests in a computable way. (`d91bbaa3d15a` · neutral · trend_description; [[sources/the-next-frontier-of-ai-in-production-is-chaos-engineering-01krkb7np7mz3q1weya69wvnvv|The Next Frontier of AI in Production Is Chaos Engineering]])
- The article argues that current chaos tools already handle safety constraints, but lack an intent layer. It proposes a standard intent specification schema with fields like target_behavior, hypothesis, acceptance_criteria, budget_fraction, and exclusion_zones; structured outcome records; and a hypothesis-quality score to make experiments machine-readable and improve learning over time. (`743184322c4a` · supporting · evidence_from_source; [[sources/the-next-frontier-of-ai-in-production-is-chaos-engineering-01krkb7np7mz3q1weya69wvnvv|The Next Frontier of AI in Production Is Chaos Engineering]])
- Proposed schema fields include target_behavior, hypothesis, acceptance_criteria, budget_fraction, and exclusion_zones. (`3a82b3430bd5` · supporting · supporting_data_points[0]; [[sources/the-next-frontier-of-ai-in-production-is-chaos-engineering-01krkb7np7mz3q1weya69wvnvv|The Next Frontier of AI in Production Is Chaos Engineering]])
- The article says structured experiment outcomes are needed as training data. (`105756dec648` · supporting · supporting_data_points[1]; [[sources/the-next-frontier-of-ai-in-production-is-chaos-engineering-01krkb7np7mz3q1weya69wvnvv|The Next Frontier of AI in Production Is Chaos Engineering]])
- It proposes a hypothesis-quality score to measure whether a run changed the team's belief about the system. (`915c59b05644` · supporting · supporting_data_points[2]; [[sources/the-next-frontier-of-ai-in-production-is-chaos-engineering-01krkb7np7mz3q1weya69wvnvv|The Next Frontier of AI in Production Is Chaos Engineering]])
- "Gap 1: A standard intent specification schema" (`ab98c233a28c` · supporting · supporting_snippet; [[sources/the-next-frontier-of-ai-in-production-is-chaos-engineering-01krkb7np7mz3q1weya69wvnvv|The Next Frontier of AI in Production Is Chaos Engineering]])
- Actionable now as a proposed architecture and schema gap, but not yet shown as a widely adopted industry standard. The signal is about a tooling and data-model opportunity rather than an established market shift. (`3a7bc622b87e` · uncertainty · time_sensitivity; [[sources/the-next-frontier-of-ai-in-production-is-chaos-engineering-01krkb7np7mz3q1weya69wvnvv|The Next Frontier of AI in Production Is Chaos Engineering]])
- The source is a persuasive architecture argument, not adoption evidence. It is unclear whether teams will converge on one standard schema, whether intent records will stay up to date as systems change, and whether outcome data will be structured consistently enough to support reliable learning across organizations. (`167e04539ef8` · uncertainty · uncertainty_note; [[sources/the-next-frontier-of-ai-in-production-is-chaos-engineering-01krkb7np7mz3q1weya69wvnvv|The Next Frontier of AI in Production Is Chaos Engineering]])

## Contradictions / tensions

- Actionable now as a proposed architecture and schema gap, but not yet shown as a widely adopted industry standard. The signal is about a tooling and data-model opportunity rather than an established market shift. (uncertainty; [[sources/the-next-frontier-of-ai-in-production-is-chaos-engineering-01krkb7np7mz3q1weya69wvnvv|The Next Frontier of AI in Production Is Chaos Engineering]])
- The source is a persuasive architecture argument, not adoption evidence. It is unclear whether teams will converge on one standard schema, whether intent records will stay up to date as systems change, and whether outcome data will be structured consistently enough to support reliable learning across organizations. (uncertainty; [[sources/the-next-frontier-of-ai-in-production-is-chaos-engineering-01krkb7np7mz3q1weya69wvnvv|The Next Frontier of AI in Production Is Chaos Engineering]])

## Related pages

- harness-design-becomes-more-important-for-agent-reliability

## Sources

- [[sources/the-next-frontier-of-ai-in-production-is-chaos-engineering-01krkb7np7mz3q1weya69wvnvv|The Next Frontier of AI in Production Is Chaos Engineering]]
