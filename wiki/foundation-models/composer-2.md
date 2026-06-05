---
title: Composer 2
slug: composer-2
entity_id: model:composer-2
category: foundation-model
tags:
- coding-model
- developer-focused
- proprietary-model
- tool-use-capable
first_seen: '2026-03-19'
last_seen: '2026-03-19'
source_count: 1
evidence_count: 15
source_ids:
- introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1
value_level: high
confidence: 0.94
synthesis_state: stage1-placeholder
types:
- coding-model
- proprietary-model
---

# Composer 2

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Composer 2 is Cursor's coding model positioned for demanding software work. The source frames it as frontier-level on coding tasks and emphasizes that it can handle long-horizon work requiring many actions. Cursor attributes its quality jump to continued pretraining followed by reinforcement learning, which suggests the model is optimized for agentic coding rather than short completion quality alone. A faster variant is offered with the same intelligence claim, which makes deployment choice partly about throughput and cost.

## Benchmark Observations

- The source reports 61.3 on CursorBench, 61.7 on Terminal-Bench 2.0, and 73.7 on SWE-bench Multilingual for Composer 2.
- It reports large gains over Composer 1.5 and Composer 1 across all three benchmarks listed.
- The source says Cursor's Terminal-Bench 2.0 score used the official Harbor evaluation framework with default settings and five iterations per model-agent pair.

## Comparative Observations

- Composer 2 is reported to outperform Composer 1.5 and Composer 1 on every benchmark table shown in the source.
- The fast variant is presented as lower cost than other fast models, while keeping the same intelligence claim within Cursor's framing.

## Core Capabilities

- It is positioned as a coding-focused model for long-horizon tasks that may require hundreds of actions.
- It is trained from a continued-pretraining base and then reinforced on coding tasks, which the source presents as the reason for the quality jump.
- It has a faster variant that claims the same intelligence while changing the price point.

## Maturity signals

Cursor reports explicit benchmark tables, pricing, and a fast variant, which suggests a product that is being iterated as a commercial model offering rather than an experimental demo. The source does not show independent adoption signals, but it does show enough packaging detail to indicate operational maturity inside Cursor's product line. As of 2026-03-19, the model appears sufficiently productized to test in real coding workflows, but the validation remains vendor-led.

## Pricing / inference implications

The source sets pricing at $0.50/M input and $2.50/M output tokens for Composer 2, with a faster variant at $1.50/M input and $7.50/M output tokens. That creates a practical cost-control lever for coding-agent workloads where throughput and repeated tool calls can dominate spend. The article implies that teams should compare total workflow cost, not only raw token price, because long-horizon tasks can amplify retries and output-heavy loops.

## Provider

Cursor

## Related Models

- Composer 1.5
- Composer 1
- Claude Code

## Service automation implications

The main service-automation implication is indirect: stronger long-horizon coding models can improve internal automation for building and maintaining support tooling, but the source does not connect Composer 2 to customer-facing support automation directly. Any use in chatbots or voicebots would still need separate evidence.

## Weaknesses / limitations

The evidence is vendor-controlled and benchmark-centric, so real-world reliability is not independently established in this source. The article does not provide failure modes, benchmark task composition, or workload-specific regressions, so the "frontier-level" framing should be treated cautiously as of 2026-03-19.

## Evidence / supporting sources

### Introducing Composer 2 (2026-03-19)

- Composer 2 is reported to outperform Composer 1.5 and Composer 1 on every benchmark table shown in the source. (`9920cc1e2d4f` · neutral · comparative_observations[0]; [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]])
- The fast variant is presented as lower cost than other fast models, while keeping the same intelligence claim within Cursor's framing. (`1f58fc85ff90` · neutral · comparative_observations[1]; [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]])
- Adopting Composer 2 appears to favor agent-style coding loops that can run for many steps, not just single-shot code generation. Teams evaluating it would want harnesses that capture terminal interaction, tool use, and long task trajectories rather than relying only on brief prompt-response tests. The pricing split between standard and fast variants creates a concrete deployment tradeoff between latency and inference cost. (`8ec0abc86dec` · neutral · deployment_implications; [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]])
- Cursor reports explicit benchmark tables, pricing, and a fast variant, which suggests a product that is being iterated as a commercial model offering rather than an experimental demo. The source does not show independent adoption signals, but it does show enough packaging detail to indicate operational maturity inside Cursor's product line. As of 2026-03-19, the model appears sufficiently productized to test in real coding workflows, but the validation remains vendor-led. (`ec737dcde498` · neutral · maturity_signals; [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]])
- Composer 2 is Cursor's coding model positioned for demanding software work. The source frames it as frontier-level on coding tasks and emphasizes that it can handle long-horizon work requiring many actions. Cursor attributes its quality jump to continued pretraining followed by reinforcement learning, which suggests the model is optimized for agentic coding rather than short completion quality alone. A faster variant is offered with the same intelligence claim, which makes deployment choice partly about throughput and cost. (`44adfa2f9fe4` · neutral · operational_profile; [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]])
- The source sets pricing at $0.50/M input and $2.50/M output tokens for Composer 2, with a faster variant at $1.50/M input and $7.50/M output tokens. That creates a practical cost-control lever for coding-agent workloads where throughput and repeated tool calls can dominate spend. The article implies that teams should compare total workflow cost, not only raw token price, because long-horizon tasks can amplify retries and output-heavy loops. (`cfab601c79ef` · neutral · pricing_inference_implications; [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]])
- The main service-automation implication is indirect: stronger long-horizon coding models can improve internal automation for building and maintaining support tooling, but the source does not connect Composer 2 to customer-facing support automation directly. Any use in chatbots or voicebots would still need separate evidence. (`c602feb91a10` · neutral · service_automation_implications; [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]])
- The source reports 61.3 on CursorBench, 61.7 on Terminal-Bench 2.0, and 73.7 on SWE-bench Multilingual for Composer 2. (`d464781e4d7d` · supporting · benchmark_observations[0]; [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]])
- It reports large gains over Composer 1.5 and Composer 1 across all three benchmarks listed. (`0180de1fe827` · supporting · benchmark_observations[1]; [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]])
- The source says Cursor's Terminal-Bench 2.0 score used the official Harbor evaluation framework with default settings and five iterations per model-agent pair. (`1cf715cf3d08` · supporting · benchmark_observations[2]; [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]])
- It is positioned as a coding-focused model for long-horizon tasks that may require hundreds of actions. (`f0e0c60db430` · supporting · core_capabilities[0]; [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]])
- It is trained from a continued-pretraining base and then reinforced on coding tasks, which the source presents as the reason for the quality jump. (`55abe2729e8c` · supporting · core_capabilities[1]; [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]])
- It has a faster variant that claims the same intelligence while changing the price point. (`1fce8d0b619e` · supporting · core_capabilities[2]; [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]])
- "Composer 2 is now available in Cursor. It's frontier-level at coding and priced at $0.50/M input and $2.50/M output tokens" (`c22bf9a46c78` · supporting · supporting_snippet; [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]])
- The evidence is vendor-controlled and benchmark-centric, so real-world reliability is not independently established in this source. The article does not provide failure modes, benchmark task composition, or workload-specific regressions, so the "frontier-level" framing should be treated cautiously as of 2026-03-19. (`846b0d66987f` · uncertainty · weaknesses_limitations; [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]])

## Contradictions / tensions

- The evidence is vendor-controlled and benchmark-centric, so real-world reliability is not independently established in this source. The article does not provide failure modes, benchmark task composition, or workload-specific regressions, so the "frontier-level" framing should be treated cautiously as of 2026-03-19. (uncertainty; [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]])

## Related pages

- Claude Code
- Composer 1
- Composer 1.5

## Sources

- [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]]
