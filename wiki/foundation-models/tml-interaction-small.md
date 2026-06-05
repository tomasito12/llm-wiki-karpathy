---
title: TML-Interaction-Small
slug: tml-interaction-small
entity_id: model:tml-interaction-small
category: foundation-model
first_seen: '2026-05-12'
last_seen: '2026-05-12'
source_count: 1
evidence_count: 17
source_ids:
- ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8
value_level: high
confidence: 0.91
synthesis_state: stage1-placeholder
types:
- multimodal-model
- proprietary-model
---

# TML-Interaction-Small

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
A large mixture-of-experts multimodal interaction model described as being trained from scratch for realtime human-AI collaboration. The source positions it as stronger for continuous interaction, interruption handling, and simultaneous multimodal response than standard turn-based systems.

- Designed for continuous interaction, which matters when the system must react mid-stream rather than wait for a full turn boundary.
- Uses encoder-free early fusion for images and audio, which suggests tighter cross-modal processing than a simple text-first pipeline.
- The article says it advances realtime voice performance and improves over several existing systems on the benchmarks mentioned in the roundup.
- The model is framed around time-aligned microturns of about 200 milliseconds, which is a concrete design target for low-latency conversational behavior.

## Benchmark Observations

- The source says it beats GPT-Realtime-2 and Gemini 3.1-Flash on BigBench Audio, IFEval, and FD-bench.
- The article also says the team created new internal benchmarks for time awareness, simultaneous translation, and visual proactivity.
- Benchmark evidence is meaningful here, but the article does not show the full score tables or independent reruns.

## Comparative Observations

- The source explicitly contrasts it with GPT-4o’s old “her” demo, implying a more detailed and practical realtime interaction target.
- It is also described as outperforming GPT-Realtime-2 and Gemini 3.1-Flash on the listed benchmarks.
- The article frames native interactivity as the deeper innovation than raw benchmark gains, so comparisons are not only about scores.

## Core Capabilities

- It handles multimodal realtime interaction with audio, images, and text in a continuous stream.
- It is described as supporting interruption handling and simultaneous speech rather than forcing clean turn-taking.
- It uses early fusion so multiple modalities are processed together rather than as separate staged inputs.
- It is framed around time-aligned microturns that can be as short as 200 milliseconds.

## Maturity signals

The source presents the model as a formal launch with technical demos and benchmark comparisons, which suggests a substantial internal effort rather than an experimental demo. Still, the evidence base is a product preview and commentary, not deployment data. The article also mentions a likely roadmap pairing with background agents, but that is only a hint.

## Pricing / inference implications

The source does not provide pricing, serving cost, or throughput data. Because the model is a 276B parameter MoE with 12B active, inference feasibility will likely depend heavily on serving stack efficiency and routing behavior, but that is an inference rather than a sourced claim.

## Provider

Thinking Machines

## Related Models

- GPT-Realtime-2
- Gemini 3.1-Flash
- GPT-4o
- Chameleon

## Service automation implications

Potentially useful for voice assistants and live conversational systems that need better interruption handling and timing, but the source does not provide evidence from support or contact-center deployments. As of 2026-05-12, the implication is promising but still early-stage.

## Weaknesses / limitations

- The source gives no production latency, cost, or stability data, so it is hard to judge how well the model behaves outside demos.
- The claims are benchmark- and demo-heavy, and the article does not show independent reproduction of the results.
- Continuous interaction raises unresolved questions about interruption safety, timing errors, and state management under noisy inputs.

## Evidence / supporting sources

### [AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD (2026-05-12)

- The source explicitly contrasts it with GPT-4o’s old “her” demo, implying a more detailed and practical realtime interaction target. (`880b12939bec` · neutral · comparative_observations[0]; [[sources/ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8|[AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD]])
- It is also described as outperforming GPT-Realtime-2 and Gemini 3.1-Flash on the listed benchmarks. (`b9de432388ba` · neutral · comparative_observations[1]; [[sources/ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8|[AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD]])
- The article frames native interactivity as the deeper innovation than raw benchmark gains, so comparisons are not only about scores. (`8303e9714e34` · neutral · comparative_observations[2]; [[sources/ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8|[AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD]])
- It suggests moving from prompt-response pipelines toward streaming interaction loops where timing, silence, and overlap are first-class concerns. Teams building realtime assistants may need evals and orchestration logic that treat the conversation as a live control problem rather than a sequence of independent turns. (`8aa3631b696d` · neutral · deployment_implications; [[sources/ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8|[AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD]])
- The source presents the model as a formal launch with technical demos and benchmark comparisons, which suggests a substantial internal effort rather than an experimental demo. Still, the evidence base is a product preview and commentary, not deployment data. The article also mentions a likely roadmap pairing with background agents, but that is only a hint. (`d6092bb8d0f3` · neutral · maturity_signals; [[sources/ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8|[AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD]])
- A large mixture-of-experts multimodal interaction model described as being trained from scratch for realtime human-AI collaboration. The source positions it as stronger for continuous interaction, interruption handling, and simultaneous multimodal response than standard turn-based systems.

- Designed for continuous interaction, which matters when the system must react mid-stream rather than wait for a full turn boundary.
- Uses encoder-free early fusion for images and audio, which suggests tighter cross-modal processing than a simple text-first pipeline.
- The article says it advances realtime voice performance and improves over several existing systems on the benchmarks mentioned in the roundup.
- The model is framed around time-aligned microturns of about 200 milliseconds, which is a concrete design target for low-latency conversational behavior. (`6cbead0aa0a5` · neutral · operational_profile; [[sources/ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8|[AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD]])
- The source does not provide pricing, serving cost, or throughput data. Because the model is a 276B parameter MoE with 12B active, inference feasibility will likely depend heavily on serving stack efficiency and routing behavior, but that is an inference rather than a sourced claim. (`ad36fdc3b17f` · neutral · pricing_inference_implications; [[sources/ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8|[AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD]])
- Potentially useful for voice assistants and live conversational systems that need better interruption handling and timing, but the source does not provide evidence from support or contact-center deployments. As of 2026-05-12, the implication is promising but still early-stage. (`9c832746f4f4` · neutral · service_automation_implications; [[sources/ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8|[AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD]])
- The source says it beats GPT-Realtime-2 and Gemini 3.1-Flash on BigBench Audio, IFEval, and FD-bench. (`ab94fbac4c1e` · supporting · benchmark_observations[0]; [[sources/ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8|[AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD]])
- The article also says the team created new internal benchmarks for time awareness, simultaneous translation, and visual proactivity. (`5c4fbd5acd31` · supporting · benchmark_observations[1]; [[sources/ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8|[AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD]])
- Benchmark evidence is meaningful here, but the article does not show the full score tables or independent reruns. (`6ceeadb13165` · supporting · benchmark_observations[2]; [[sources/ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8|[AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD]])
- It handles multimodal realtime interaction with audio, images, and text in a continuous stream. (`9750252da32e` · supporting · core_capabilities[0]; [[sources/ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8|[AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD]])
- It is described as supporting interruption handling and simultaneous speech rather than forcing clean turn-taking. (`00ddb1e8aaed` · supporting · core_capabilities[1]; [[sources/ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8|[AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD]])
- It uses early fusion so multiple modalities are processed together rather than as separate staged inputs. (`c0d9776812c8` · supporting · core_capabilities[2]; [[sources/ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8|[AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD]])
- It is framed around time-aligned microturns that can be as short as 200 milliseconds. (`2dc044404a77` · supporting · core_capabilities[3]; [[sources/ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8|[AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD]])
- "TML-Interaction-Small is a 276B parameter MoE with 12B active., which immediately advances the state of the art of realtime voice models" (`15f77fc5c73a` · supporting · supporting_snippet; [[sources/ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8|[AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD]])
- - The source gives no production latency, cost, or stability data, so it is hard to judge how well the model behaves outside demos.
- The claims are benchmark- and demo-heavy, and the article does not show independent reproduction of the results.
- Continuous interaction raises unresolved questions about interruption safety, timing errors, and state management under noisy inputs. (`e41f31033289` · uncertainty · weaknesses_limitations; [[sources/ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8|[AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD]])

## Contradictions / tensions

- - The source gives no production latency, cost, or stability data, so it is hard to judge how well the model behaves outside demos.
- The claims are benchmark- and demo-heavy, and the article does not show independent reproduction of the results.
- Continuous interaction raises unresolved questions about interruption safety, timing errors, and state management under noisy inputs. (uncertainty; [[sources/ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8|[AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD]])

## Related pages

- Chameleon
- GPT-4o
- GPT-Realtime-2
- Gemini 3.1-Flash

## Sources

- [[sources/ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8|[AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD]]
