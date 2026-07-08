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
last_seen: '2026-03-25'
source_count: 2
evidence_count: 24
source_ids:
- introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1
- run-cloud-agents-in-your-own-infrastructure-01kr1qhvaw58dz13633c041cmy
value_level: high
confidence: 0.795
synthesis_state: stage1-placeholder
types:
- coding-model
- frontier-model
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
- It can be selected as the model inside Cursor’s multi-model agent workflow.
- It is compatible with custom-built agent harnesses, which matters when coding tasks need tool execution and verification loops.

## Maturity signals

Cursor reports explicit benchmark tables, pricing, and a fast variant, which suggests a product that is being iterated as a commercial model offering rather than an experimental demo. The source does not show independent adoption signals, but it does show enough packaging detail to indicate operational maturity inside Cursor's product line. As of 2026-03-19, the model appears sufficiently productized to test in real coding workflows, but the validation remains vendor-led.

## Pricing / inference implications

The source sets pricing at $0.50/M input and $2.50/M output tokens for Composer 2, with a faster variant at $1.50/M input and $7.50/M output tokens. That creates a practical cost-control lever for coding-agent workloads where throughput and repeated tool calls can dominate spend. The article implies that teams should compare total workflow cost, not only raw token price, because long-horizon tasks can amplify retries and output-heavy loops.

## Provider

Cursor

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

### Run cloud agents in your own infrastructure (2026-03-25)

- If used in self-hosted agents, Composer 2 has to work inside a worker-based execution loop where tool calls, repo access, and test runs happen on customer machines. That shifts the real deployment question from raw chat quality to whether the model can support reliable multi-step coding workflows under enterprise security constraints. (`3113f0fa8043` · neutral · deployment_implications; [[sources/run-cloud-agents-in-your-own-infrastructure-01kr1qhvaw58dz13633c041cmy|Run cloud agents in your own infrastructure]])
- The source treats Composer 2 as an already-usable option in a generally available product, which suggests productization rather than a research preview. However, the article offers no independent evidence about adoption, benchmark standing, or ecosystem depth. (`8eed41e66f2a` · neutral · maturity_signals; [[sources/run-cloud-agents-in-your-own-infrastructure-01kr1qhvaw58dz13633c041cmy|Run cloud agents in your own infrastructure]])
- Composer 2 is presented as one of the models available to Cursor’s self-hosted cloud agents. In this source, its main operational significance is that it can be used inside an agent harness that runs in customer infrastructure, which means model choice is being exposed as part of the agent execution layer rather than as a standalone chat experience. (`47e323db6885` · neutral · operational_profile; [[sources/run-cloud-agents-in-your-own-infrastructure-01kr1qhvaw58dz13633c041cmy|Run cloud agents in your own infrastructure]])
- No pricing or inference-cost details are given. The only defensible inference is that model choice is being combined with self-hosted execution, so total cost would depend on both model usage and customer-run worker infrastructure. (`05b2bc4c1650` · neutral · pricing_inference_implications; [[sources/run-cloud-agents-in-your-own-infrastructure-01kr1qhvaw58dz13633c041cmy|Run cloud agents in your own infrastructure]])
- No direct service-automation implication is stated beyond its use in autonomous coding agents. (`2e60ec9f4763` · neutral · service_automation_implications; [[sources/run-cloud-agents-in-your-own-infrastructure-01kr1qhvaw58dz13633c041cmy|Run cloud agents in your own infrastructure]])
- It can be selected as the model inside Cursor’s multi-model agent workflow. (`e3266c802127` · supporting · core_capabilities[0]; [[sources/run-cloud-agents-in-your-own-infrastructure-01kr1qhvaw58dz13633c041cmy|Run cloud agents in your own infrastructure]])
- It is compatible with custom-built agent harnesses, which matters when coding tasks need tool execution and verification loops. (`c91b63c8bc97` · supporting · core_capabilities[1]; [[sources/run-cloud-agents-in-your-own-infrastructure-01kr1qhvaw58dz13633c041cmy|Run cloud agents in your own infrastructure]])
- "Multi-model: use Composer 2 or any model from frontier labs with custom-built agent harnesses." (`1c40dabee54e` · supporting · supporting_snippet; [[sources/run-cloud-agents-in-your-own-infrastructure-01kr1qhvaw58dz13633c041cmy|Run cloud agents in your own infrastructure]])
- The article does not provide benchmark data, pricing, or failure cases for Composer 2. Because it is only mentioned as an available option, the source gives no basis for judging its quality relative to the other frontier models Cursor supports. (`774848323072` · uncertainty · weaknesses_limitations; [[sources/run-cloud-agents-in-your-own-infrastructure-01kr1qhvaw58dz13633c041cmy|Run cloud agents in your own infrastructure]])

## Contradictions / tensions

- The evidence is vendor-controlled and benchmark-centric, so real-world reliability is not independently established in this source. The article does not provide failure modes, benchmark task composition, or workload-specific regressions, so the "frontier-level" framing should be treated cautiously as of 2026-03-19. (uncertainty; [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]])
- The article does not provide benchmark data, pricing, or failure cases for Composer 2. Because it is only mentioned as an available option, the source gives no basis for judging its quality relative to the other frontier models Cursor supports. (uncertainty; [[sources/run-cloud-agents-in-your-own-infrastructure-01kr1qhvaw58dz13633c041cmy|Run cloud agents in your own infrastructure]])

## Related pages

No related pages captured.

## Sources

- [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]]
- [[sources/run-cloud-agents-in-your-own-infrastructure-01kr1qhvaw58dz13633c041cmy|Run cloud agents in your own infrastructure]]
