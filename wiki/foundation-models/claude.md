---
title: Claude
slug: claude
entity_id: model:claude
category: foundation-model
tags:
- frontier-model
- proprietary-model
- tool-use-capable
source_count: 1
evidence_count: 17
source_ids:
- when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp
value_level: high
confidence: 0.95
synthesis_state: stage1-placeholder
types:
- frontier-model
- proprietary-model
---

# Claude

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Claude is presented as a frontier model that is increasingly strong at code generation, debugging, experiment execution, and open-ended research assistance. The source says it can be handed underspecified engineering work, run code, delegate tasks to other agents, and improve the quality of its own outputs over time. It is also used as a reviewer, which suggests the model is reaching the point where it can participate in both production coding and verification loops.

## Benchmark Observations

- The source says Claude’s success rate on the most open-ended tasks reached 76% in May 2026.
- The source says Claude went from about 3x speedup on a training-code optimization task in May 2025 to about 52x by April 2026.
- The source says Claude Opus 4.6 could handle 12-hour tasks, and METR found Claude Mythos Preview could work for at least 16 hours.

## Comparative Observations

- The source says Claude-written code was roughly at parity with human-written code at Anthropic by the time of publication, after being somewhat worse in late 2025.
- The source says an automated Claude reviewer would have caught roughly a third of the bugs behind past claude.ai incidents before production.
- The source says Claude Mythos Preview outperformed human next-step choices 64% of the time in a sampled open-ended research setting.

## Core Capabilities

- Claude can write code at a level that supports real production merges rather than only short snippets.
- Claude can run code and iterate on experiments when the goal and success metric are already defined.
- Claude can help debug open-ended incidents with limited human guidance.
- Claude can act as an automated reviewer that looks for bugs, security flaws, and other defects.

## Maturity signals

Anthropic describes Claude as already embedded in its own development process, with more than 80% of merged code attributed to it. The model is treated as good enough for internal review, debugging, and research loops rather than only as a demo system. That is a strong operational maturity signal as of the article’s publication date.

## Pricing / inference implications

The source does not provide pricing, but it does imply that high-volume use will be shaped by compute costs more than human labor costs once execution is automated. The practical inference is that cost control will depend on how much autonomous looping, code execution, and review you allow.

## Provider

Anthropic

## Service automation implications

The source has limited direct service-automation evidence, but it implies that stronger Claude-like models can reduce handoff volume in workflow-heavy support systems when tasks can be framed clearly. The main constraint would remain policy, validation, and review rather than raw task execution.

## Weaknesses / limitations

The source still describes a gap in judgment, especially in choosing goals and deciding which problems are worth working on. It also notes that quality parity is not settled and that lines-of-code metrics overstate true productivity gain. The model is strong at execution but not yet shown to reliably replace human direction-setting for frontier research.

## Evidence / supporting sources

### When AI builds itself (undated)

- The source says Claude-written code was roughly at parity with human-written code at Anthropic by the time of publication, after being somewhat worse in late 2025. (`d0c0ea2468c4` · neutral · comparative_observations[0]; [[sources/when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp|When AI builds itself]])
- The source says an automated Claude reviewer would have caught roughly a third of the bugs behind past claude.ai incidents before production. (`d7daf10730f8` · neutral · comparative_observations[1]; [[sources/when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp|When AI builds itself]])
- The source says Claude Mythos Preview outperformed human next-step choices 64% of the time in a sampled open-ended research setting. (`d3ae2ae4afa7` · neutral · comparative_observations[2]; [[sources/when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp|When AI builds itself]])
- Adopting Claude in an engineering org can shift a meaningful share of implementation work from humans to model-directed workflows, which changes review load and supervision design. The source suggests teams should expect human review to become the new bottleneck as model-generated code volume rises, so deployment needs stronger validation, code review, and incident-response loops. It also implies that research and experimentation workflows can be accelerated when the model is allowed to run iterative loops rather than only suggest snippets. (`69625c8d37ca` · neutral · deployment_implications; [[sources/when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp|When AI builds itself]])
- Anthropic describes Claude as already embedded in its own development process, with more than 80% of merged code attributed to it. The model is treated as good enough for internal review, debugging, and research loops rather than only as a demo system. That is a strong operational maturity signal as of the article’s publication date. (`1979291c3fe6` · neutral · maturity_signals; [[sources/when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp|When AI builds itself]])
- Claude is presented as a frontier model that is increasingly strong at code generation, debugging, experiment execution, and open-ended research assistance. The source says it can be handed underspecified engineering work, run code, delegate tasks to other agents, and improve the quality of its own outputs over time. It is also used as a reviewer, which suggests the model is reaching the point where it can participate in both production coding and verification loops. (`57d15664ebe2` · neutral · operational_profile; [[sources/when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp|When AI builds itself]])
- The source does not provide pricing, but it does imply that high-volume use will be shaped by compute costs more than human labor costs once execution is automated. The practical inference is that cost control will depend on how much autonomous looping, code execution, and review you allow. (`d7482d9f7893` · neutral · pricing_inference_implications; [[sources/when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp|When AI builds itself]])
- The source has limited direct service-automation evidence, but it implies that stronger Claude-like models can reduce handoff volume in workflow-heavy support systems when tasks can be framed clearly. The main constraint would remain policy, validation, and review rather than raw task execution. (`720894e46830` · neutral · service_automation_implications; [[sources/when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp|When AI builds itself]])
- The source says Claude’s success rate on the most open-ended tasks reached 76% in May 2026. (`f68f87493e1a` · supporting · benchmark_observations[0]; [[sources/when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp|When AI builds itself]])
- The source says Claude went from about 3x speedup on a training-code optimization task in May 2025 to about 52x by April 2026. (`f9897b1c1ca1` · supporting · benchmark_observations[1]; [[sources/when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp|When AI builds itself]])
- The source says Claude Opus 4.6 could handle 12-hour tasks, and METR found Claude Mythos Preview could work for at least 16 hours. (`50919e68eeeb` · supporting · benchmark_observations[2]; [[sources/when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp|When AI builds itself]])
- Claude can write code at a level that supports real production merges rather than only short snippets. (`d4ce90e5bfae` · supporting · core_capabilities[0]; [[sources/when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp|When AI builds itself]])
- Claude can run code and iterate on experiments when the goal and success metric are already defined. (`4d356563e715` · supporting · core_capabilities[1]; [[sources/when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp|When AI builds itself]])
- Claude can help debug open-ended incidents with limited human guidance. (`5d4cac5298c3` · supporting · core_capabilities[2]; [[sources/when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp|When AI builds itself]])
- Claude can act as an automated reviewer that looks for bugs, security flaws, and other defects. (`d6ff0076e227` · supporting · core_capabilities[3]; [[sources/when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp|When AI builds itself]])
- As of May 2026, more than 80% of the code we merge into Anthropic’s codebase was authored by Claude. (`7e07a4184038` · supporting · supporting_snippet; [[sources/when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp|When AI builds itself]])
- The source still describes a gap in judgment, especially in choosing goals and deciding which problems are worth working on. It also notes that quality parity is not settled and that lines-of-code metrics overstate true productivity gain. The model is strong at execution but not yet shown to reliably replace human direction-setting for frontier research. (`d6eea8fb83cb` · uncertainty · weaknesses_limitations; [[sources/when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp|When AI builds itself]])

## Contradictions / tensions

- The source still describes a gap in judgment, especially in choosing goals and deciding which problems are worth working on. It also notes that quality parity is not settled and that lines-of-code metrics overstate true productivity gain. The model is strong at execution but not yet shown to reliably replace human direction-setting for frontier research. (uncertainty; [[sources/when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp|When AI builds itself]])

## Related pages

No related pages captured.

## Sources

- [[sources/when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp|When AI builds itself]]
