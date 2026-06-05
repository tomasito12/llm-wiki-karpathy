---
title: Grok Voice Think Fast 1.0
slug: grok-voice-think-fast-1-0
entity_id: model:grok-voice-think-fast-1-0
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
value_level: high
confidence: 0.92
synthesis_state: stage1-placeholder
types:
- realtime-voice-model
---

# Grok Voice Think Fast 1.0

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
- Strongest reported performer in this benchmark, leading the field on realistic customer service voice tasks at 52.1% end-to-end success.
- The result suggests it can keep multi-turn voice interactions moving while also handling tool use under noisy, real-call-like conditions.
- Its longer average conversation time indicates it may be more thorough or more verbose than some alternatives, which can matter in voice support flows where completeness trades off against speed.

## Benchmark Observations

- It scored 52.1% on the source’s agentic performance benchmark for speech-to-speech models.
- It averaged 5.6 minutes per conversation, the second-longest among the models listed in the source.
- The benchmark evaluates realistic customer service tasks across airline, retail, and telecom scenarios under accents, background noise, and packet loss.

## Comparative Observations

- It outperformed OpenAI's GPT-Realtime-2 (High) at 39.8% and GPT-Realtime-1.5 at 38.8% in the source leaderboard.
- It also exceeded Gemini 3.1 Flash Live Preview - High at 37.7%.
- Its conversation time was longer than Gemini 2.5 Flash Native Audio Preview at 2.4 minutes, GPT-Realtime-2 (Minimal) at 2.6 minutes, and GPT-Realtime-2 (Medium) at 2.9 minutes.

## Core Capabilities

- It completes a higher share of realistic customer service voice scenarios end to end than the other models reported here.
- It appears able to combine multi-turn voice interaction with tool use under noisy audio conditions.
- Its longer average conversations suggest it can sustain interaction across more turns, which may help with complex support flows.

## Maturity signals

The model is positioned as a benchmark leader in a named evaluation, which is a meaningful signal of capability. The source does not provide deployment adoption data, so maturity beyond benchmark performance is unknown.

## Pricing / inference implications

A 5.6 minute mean conversation length implies non-trivial inference and orchestration cost for high-volume support use. Even with strong performance, economics will depend on how often the model resolves an issue without escalating.

## Provider

xAI

## Related Models

- GPT-Realtime-2 (High)
- GPT-Realtime-1.5
- Gemini 3.1 Flash Live Preview - High
- Gemini 2.5 Flash Native Audio Preview

## Service automation implications

Promising for voice support automation, but as of 2026-05-12 it still looks like a partial containment tool rather than a full replacement for human handling. The benchmark suggests it may handle some full interactions, yet the failure rate leaves substantial handoff risk.

## Weaknesses / limitations

The source still says the strongest Speech to Speech models resolve only about half of realistic customer service scenarios end-to-end, so the model is not close to fully reliable on this task class. Longer conversations can increase operating cost and create more opportunities for failure in live service flows.

## Evidence / supporting sources

### Announcing agentic performance benchmarking for Speech to Speech models on... (2026-05-12)

- It outperformed OpenAI's GPT-Realtime-2 (High) at 39.8% and GPT-Realtime-1.5 at 38.8% in the source leaderboard. (`a3b12d5f950c` · neutral · comparative_observations[0]; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- It also exceeded Gemini 3.1 Flash Live Preview - High at 37.7%. (`d0f8f99c369b` · neutral · comparative_observations[1]; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- Its conversation time was longer than Gemini 2.5 Flash Native Audio Preview at 2.4 minutes, GPT-Realtime-2 (Minimal) at 2.6 minutes, and GPT-Realtime-2 (Medium) at 2.9 minutes. (`c0c7a5c63528` · neutral · comparative_observations[2]; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- As of 2026-05-12, teams evaluating voice agents should treat this as a candidate for end-to-end task completion rather than just speech naturalness. The reported 5.6 minute average conversation length suggests latency and cost planning should include time-to-resolution, not only accuracy. The benchmark’s noisy-audio setup also implies that clean-audio tests alone would overestimate production readiness. (`9aeddb14ecc3` · neutral · deployment_implications; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- The model is positioned as a benchmark leader in a named evaluation, which is a meaningful signal of capability. The source does not provide deployment adoption data, so maturity beyond benchmark performance is unknown. (`b34aa62258d5` · neutral · maturity_signals; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- - Strongest reported performer in this benchmark, leading the field on realistic customer service voice tasks at 52.1% end-to-end success.
- The result suggests it can keep multi-turn voice interactions moving while also handling tool use under noisy, real-call-like conditions.
- Its longer average conversation time indicates it may be more thorough or more verbose than some alternatives, which can matter in voice support flows where completeness trades off against speed. (`5bc795d66812` · neutral · operational_profile; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- A 5.6 minute mean conversation length implies non-trivial inference and orchestration cost for high-volume support use. Even with strong performance, economics will depend on how often the model resolves an issue without escalating. (`e634f746b8de` · neutral · pricing_inference_implications; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- Promising for voice support automation, but as of 2026-05-12 it still looks like a partial containment tool rather than a full replacement for human handling. The benchmark suggests it may handle some full interactions, yet the failure rate leaves substantial handoff risk. (`e682d619ed81` · neutral · service_automation_implications; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- It scored 52.1% on the source’s agentic performance benchmark for speech-to-speech models. (`02b9e7455448` · supporting · benchmark_observations[0]; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- It averaged 5.6 minutes per conversation, the second-longest among the models listed in the source. (`534aae1d3c9c` · supporting · benchmark_observations[1]; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- The benchmark evaluates realistic customer service tasks across airline, retail, and telecom scenarios under accents, background noise, and packet loss. (`46d5b68a0a9e` · supporting · benchmark_observations[2]; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- It completes a higher share of realistic customer service voice scenarios end to end than the other models reported here. (`cc922f594b52` · supporting · core_capabilities[0]; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- It appears able to combine multi-turn voice interaction with tool use under noisy audio conditions. (`15ea21972642` · supporting · core_capabilities[1]; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- Its longer average conversations suggest it can sustain interaction across more turns, which may help with complex support flows. (`ad1ab84294f7` · supporting · core_capabilities[2]; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- xAI's Grok Voice Think Fast 1.0 is the clear leader at 52.1%, averaging 5.6 minutes per conversation, the second-longest overall. (`6d0fe8350af7` · supporting · supporting_snippet; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- The source still says the strongest Speech to Speech models resolve only about half of realistic customer service scenarios end-to-end, so the model is not close to fully reliable on this task class. Longer conversations can increase operating cost and create more opportunities for failure in live service flows. (`8aeabaddade7` · uncertainty · weaknesses_limitations; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])

## Contradictions / tensions

- The source still says the strongest Speech to Speech models resolve only about half of realistic customer service scenarios end-to-end, so the model is not close to fully reliable on this task class. Longer conversations can increase operating cost and create more opportunities for failure in live service flows. (uncertainty; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])

## Related pages

- GPT-Realtime-1.5
- GPT-Realtime-2 (High)
- Gemini 2.5 Flash Native Audio Preview
- Gemini 3.1 Flash Live Preview - High

## Sources

- [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]]
