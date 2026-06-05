---
title: GPT-Realtime-2 (High)
slug: gpt-realtime-2-high
entity_id: model:gpt-realtime-2-high
category: foundation-model
tags:
- frontier-model
- low-latency
- multimodal-model
- tool-use-capable
first_seen: '2026-05-12'
last_seen: '2026-05-12'
source_count: 1
evidence_count: 16
source_ids:
- announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn
value_level: medium
confidence: 0.85
synthesis_state: stage1-placeholder
types:
- realtime-voice-model
---

# GPT-Realtime-2 (High)

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
- Strong enough to place second on the reported speech-to-speech customer service benchmark, with 39.8% end-to-end success.
- The result indicates the model can participate in realistic voice-agent workflows, but not with the reliability of the benchmark leader.
- The source does not provide more detailed behavioral analysis, so the safest reading is that it is a competitive realtime voice model rather than a solved support agent.

## Benchmark Observations

- It scored 39.8% on the source benchmark.
- It averaged 3.0 minutes per conversation.
- The benchmark uses deterministic checks against expected actions and final database state, so success is measured by task completion rather than subjective listening quality.

## Comparative Observations

- It trailed Grok Voice Think Fast 1.0 at 52.1%.
- It was ahead of GPT-Realtime-1.5 at 38.8% and Gemini 3.1 Flash Live Preview - High at 37.7%.
- Its 3.0 minute average conversation length was longer than Gemini 2.5 Flash Native Audio Preview at 2.4 minutes and GPT-Realtime-2 (Minimal) at 2.6 minutes, but shorter than Grok Voice Think Fast 1.0 at 5.6 minutes.

## Core Capabilities

- It participates in realistic customer service voice-agent interactions with tool use and multi-turn flow.
- It achieves lower conversation duration than some higher-scoring models, which may matter for service throughput.
- It is benchmarked under accents, background noise, and packet loss rather than clean audio alone.

## Maturity signals

Being near the top of a realistic benchmark is a useful capability signal. The source provides no adoption or production-readiness evidence beyond the benchmark result.

## Pricing / inference implications

Its 3.0 minute average conversation length is shorter than the benchmark leader, which could reduce per-interaction cost relative to longer-running models. However, lower success than the leader may offset any cost advantage through more rework or escalation.

## Provider

OpenAI

## Related Models

- Grok Voice Think Fast 1.0
- GPT-Realtime-1.5
- Gemini 3.1 Flash Live Preview - High
- Gemini 2.5 Flash Native Audio Preview

## Service automation implications

Potentially useful for support automation where partial completion and fast turnaround are acceptable, but the reported success rate implies substantial handoff logic is still required as of 2026-05-12.

## Weaknesses / limitations

The source frames even strong speech-to-speech models as resolving only about half of realistic customer service scenarios end to end, so reliability remains the main limitation. Performance under noisy audio is a known challenge in the benchmark setting.

## Evidence / supporting sources

### Announcing agentic performance benchmarking for Speech to Speech models on... (2026-05-12)

- It trailed Grok Voice Think Fast 1.0 at 52.1%. (`013ef89a2f55` · neutral · comparative_observations[0]; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- It was ahead of GPT-Realtime-1.5 at 38.8% and Gemini 3.1 Flash Live Preview - High at 37.7%. (`c00b76d891c7` · neutral · comparative_observations[1]; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- Its 3.0 minute average conversation length was longer than Gemini 2.5 Flash Native Audio Preview at 2.4 minutes and GPT-Realtime-2 (Minimal) at 2.6 minutes, but shorter than Grok Voice Think Fast 1.0 at 5.6 minutes. (`b8c1b5fe8cf7` · neutral · comparative_observations[2]; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- As of 2026-05-12, this model should be evaluated against real customer-service task completion, not only speech quality. The reported 3.0 minute average conversation length suggests it may be operationally attractive where shorter calls matter, but success rate remains the more important constraint. No integration or production-deployment details are provided in the source. (`e29564626d6c` · neutral · deployment_implications; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- Being near the top of a realistic benchmark is a useful capability signal. The source provides no adoption or production-readiness evidence beyond the benchmark result. (`3a2f50e89895` · neutral · maturity_signals; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- - Strong enough to place second on the reported speech-to-speech customer service benchmark, with 39.8% end-to-end success.
- The result indicates the model can participate in realistic voice-agent workflows, but not with the reliability of the benchmark leader.
- The source does not provide more detailed behavioral analysis, so the safest reading is that it is a competitive realtime voice model rather than a solved support agent. (`ca535d15605a` · neutral · operational_profile; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- Its 3.0 minute average conversation length is shorter than the benchmark leader, which could reduce per-interaction cost relative to longer-running models. However, lower success than the leader may offset any cost advantage through more rework or escalation. (`fdda9013e0bd` · neutral · pricing_inference_implications; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- Potentially useful for support automation where partial completion and fast turnaround are acceptable, but the reported success rate implies substantial handoff logic is still required as of 2026-05-12. (`ead5ae0373ac` · neutral · service_automation_implications; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- It scored 39.8% on the source benchmark. (`e3f998e2f65d` · supporting · benchmark_observations[0]; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- It averaged 3.0 minutes per conversation. (`3a46b1bde578` · supporting · benchmark_observations[1]; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- The benchmark uses deterministic checks against expected actions and final database state, so success is measured by task completion rather than subjective listening quality. (`70891e1c894b` · supporting · benchmark_observations[2]; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- It participates in realistic customer service voice-agent interactions with tool use and multi-turn flow. (`d2af8cf88793` · supporting · core_capabilities[0]; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- It achieves lower conversation duration than some higher-scoring models, which may matter for service throughput. (`e7d557928105` · supporting · core_capabilities[1]; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- It is benchmarked under accents, background noise, and packet loss rather than clean audio alone. (`522b0c657387` · supporting · core_capabilities[2]; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- OpenAI's GPT-Realtime-2 (High) (39.8%, 3.0 min) ... follow (`cd4e1d09d81f` · supporting · supporting_snippet; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- The source frames even strong speech-to-speech models as resolving only about half of realistic customer service scenarios end to end, so reliability remains the main limitation. Performance under noisy audio is a known challenge in the benchmark setting. (`3ca7d2f7cf13` · uncertainty · weaknesses_limitations; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])

## Contradictions / tensions

- The source frames even strong speech-to-speech models as resolving only about half of realistic customer service scenarios end to end, so reliability remains the main limitation. Performance under noisy audio is a known challenge in the benchmark setting. (uncertainty; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])

## Related pages

- GPT-Realtime-1.5
- Gemini 2.5 Flash Native Audio Preview
- Gemini 3.1 Flash Live Preview - High
- Grok Voice Think Fast 1.0

## Sources

- [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]]
