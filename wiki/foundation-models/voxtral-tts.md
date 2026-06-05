---
title: Voxtral TTS
slug: voxtral-tts
entity_id: model:voxtral-tts
category: foundation-model
first_seen: '2026-03-29'
last_seen: '2026-03-29'
source_count: 1
evidence_count: 14
source_ids:
- the-sequence-radar-832-last-week-in-ai-compression-voice-and-why-it-all-matters-01knem857g2mezerkwj34t8vnh
value_level: high
confidence: 0.89
synthesis_state: stage1-placeholder
types:
- multimodal-model
- open-weight-model
---

# Voxtral TTS

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
- An expressive multilingual text-to-speech model with a hybrid architecture that combines auto-regressive semantic-token generation and flow-matching acoustic-token generation.
- It clones voices from just 3 seconds of reference audio, which lowers the amount of enrollment audio needed for personalization.
- The source emphasizes low-latency streaming inference and deployment on smartphone hardware.
- Open weights and Creative Commons licensing make it operationally distinct from closed voice APIs.

## Benchmark Observations

- The source says it outperformed strong baselines like ElevenLabs Flash v2.5 in human preference evaluations for voice cloning.
- It reports a 90ms time-to-first-audio figure, which is operationally relevant for interactive use.

## Comparative Observations

- It is positioned against ElevenLabs Flash v2.5 in voice-cloning preference evaluations.
- Unlike closed cloud voice services, it is described as open-weight and runnable on a smartphone.

## Core Capabilities

- It generates expressive speech in multiple languages with a hybrid semantic-and-acoustic token architecture.
- It can clone a voice from a very short reference sample, which reduces enrollment friction.
- It is optimized for low-latency streaming inference, which matters for interactive voice products.

## Maturity signals

The model is described as Mistral’s first text-to-speech model, which suggests a new product line rather than a long-established ecosystem. The article cites human preference evaluations and low-latency streaming inference, which are useful maturity signals, but the evidence is still mostly vendor-provided. Open weights increase practical accessibility for evaluators and integrators.

## Pricing / inference implications

No explicit pricing is given. The smartphone and open-weight positioning imply a cost profile that may be attractive for self-hosted or edge deployments, but actual inference economics would depend on hardware and licensing choices.

## Provider

MistralAI

## Related Models

- Gemini 3.1 Flash Live

## Service automation implications

Potentially useful for voicebots and support systems where data residency and control matter more than generic cloud convenience. Its on-prem or on-device framing may suit regulated deployments that cannot send audio to third-party services. The source does not show real contact-center metrics or handoff behavior.

## Weaknesses / limitations

The source does not show broad production adoption or failure analysis, so the operational ceiling is uncertain. Voice cloning from a few seconds of audio can create governance and consent concerns that are not addressed here. The quality comparison is limited to human preference evaluation against one named baseline.

## Evidence / supporting sources

### The Sequence Radar #832: Last Week in AI: Compression, Voice, and Why It All Matters (2026-03-29)

- It is positioned against ElevenLabs Flash v2.5 in voice-cloning preference evaluations. (`43eff0b5ec46` · neutral · comparative_observations[0]; [[sources/the-sequence-radar-832-last-week-in-ai-compression-voice-and-why-it-all-matters-01knem857g2mezerkwj34t8vnh|The Sequence Radar #832: Last Week in AI: Compression, Voice, and Why It All Matters]])
- Unlike closed cloud voice services, it is described as open-weight and runnable on a smartphone. (`9c8d1316e350` · neutral · comparative_observations[1]; [[sources/the-sequence-radar-832-last-week-in-ai-compression-voice-and-why-it-all-matters-01knem857g2mezerkwj34t8vnh|The Sequence Radar #832: Last Week in AI: Compression, Voice, and Why It All Matters]])
- This model is relevant for teams that need voice generation with stronger data control, because the article frames it as suitable for running on a smartphone and never leaving a datacenter. Open weights can make it easier to self-host, adapt, and keep audio in regulated environments. The low time-to-first-audio number suggests it could fit interactive systems that need quick turn-taking, but the source does not provide a full production cost model. For service automation, the sovereignty angle is the main deployment implication. (`960a6d210f5d` · neutral · deployment_implications; [[sources/the-sequence-radar-832-last-week-in-ai-compression-voice-and-why-it-all-matters-01knem857g2mezerkwj34t8vnh|The Sequence Radar #832: Last Week in AI: Compression, Voice, and Why It All Matters]])
- The model is described as Mistral’s first text-to-speech model, which suggests a new product line rather than a long-established ecosystem. The article cites human preference evaluations and low-latency streaming inference, which are useful maturity signals, but the evidence is still mostly vendor-provided. Open weights increase practical accessibility for evaluators and integrators. (`a03453d3deb7` · neutral · maturity_signals; [[sources/the-sequence-radar-832-last-week-in-ai-compression-voice-and-why-it-all-matters-01knem857g2mezerkwj34t8vnh|The Sequence Radar #832: Last Week in AI: Compression, Voice, and Why It All Matters]])
- - An expressive multilingual text-to-speech model with a hybrid architecture that combines auto-regressive semantic-token generation and flow-matching acoustic-token generation.
- It clones voices from just 3 seconds of reference audio, which lowers the amount of enrollment audio needed for personalization.
- The source emphasizes low-latency streaming inference and deployment on smartphone hardware.
- Open weights and Creative Commons licensing make it operationally distinct from closed voice APIs. (`d17b78f067c5` · neutral · operational_profile; [[sources/the-sequence-radar-832-last-week-in-ai-compression-voice-and-why-it-all-matters-01knem857g2mezerkwj34t8vnh|The Sequence Radar #832: Last Week in AI: Compression, Voice, and Why It All Matters]])
- No explicit pricing is given. The smartphone and open-weight positioning imply a cost profile that may be attractive for self-hosted or edge deployments, but actual inference economics would depend on hardware and licensing choices. (`196fa8009ea8` · neutral · pricing_inference_implications; [[sources/the-sequence-radar-832-last-week-in-ai-compression-voice-and-why-it-all-matters-01knem857g2mezerkwj34t8vnh|The Sequence Radar #832: Last Week in AI: Compression, Voice, and Why It All Matters]])
- Potentially useful for voicebots and support systems where data residency and control matter more than generic cloud convenience. Its on-prem or on-device framing may suit regulated deployments that cannot send audio to third-party services. The source does not show real contact-center metrics or handoff behavior. (`741915d1e86c` · neutral · service_automation_implications; [[sources/the-sequence-radar-832-last-week-in-ai-compression-voice-and-why-it-all-matters-01knem857g2mezerkwj34t8vnh|The Sequence Radar #832: Last Week in AI: Compression, Voice, and Why It All Matters]])
- The source says it outperformed strong baselines like ElevenLabs Flash v2.5 in human preference evaluations for voice cloning. (`ca184d668925` · supporting · benchmark_observations[0]; [[sources/the-sequence-radar-832-last-week-in-ai-compression-voice-and-why-it-all-matters-01knem857g2mezerkwj34t8vnh|The Sequence Radar #832: Last Week in AI: Compression, Voice, and Why It All Matters]])
- It reports a 90ms time-to-first-audio figure, which is operationally relevant for interactive use. (`560eb6485c56` · supporting · benchmark_observations[1]; [[sources/the-sequence-radar-832-last-week-in-ai-compression-voice-and-why-it-all-matters-01knem857g2mezerkwj34t8vnh|The Sequence Radar #832: Last Week in AI: Compression, Voice, and Why It All Matters]])
- It generates expressive speech in multiple languages with a hybrid semantic-and-acoustic token architecture. (`4d7c3dd49d9d` · supporting · core_capabilities[0]; [[sources/the-sequence-radar-832-last-week-in-ai-compression-voice-and-why-it-all-matters-01knem857g2mezerkwj34t8vnh|The Sequence Radar #832: Last Week in AI: Compression, Voice, and Why It All Matters]])
- It can clone a voice from a very short reference sample, which reduces enrollment friction. (`ae4b9a8f4955` · supporting · core_capabilities[1]; [[sources/the-sequence-radar-832-last-week-in-ai-compression-voice-and-why-it-all-matters-01knem857g2mezerkwj34t8vnh|The Sequence Radar #832: Last Week in AI: Compression, Voice, and Why It All Matters]])
- It is optimized for low-latency streaming inference, which matters for interactive voice products. (`2fdab010329c` · supporting · core_capabilities[2]; [[sources/the-sequence-radar-832-last-week-in-ai-compression-voice-and-why-it-all-matters-01knem857g2mezerkwj34t8vnh|The Sequence Radar #832: Last Week in AI: Compression, Voice, and Why It All Matters]])
- "Voxtral TTS is 4B parameters, built on Ministral 3B, runs on a smartphone, voice-clones from under five seconds of audio, and ships with open weights under Creative Commons." (`a518e0eae1b5` · supporting · supporting_snippet; [[sources/the-sequence-radar-832-last-week-in-ai-compression-voice-and-why-it-all-matters-01knem857g2mezerkwj34t8vnh|The Sequence Radar #832: Last Week in AI: Compression, Voice, and Why It All Matters]])
- The source does not show broad production adoption or failure analysis, so the operational ceiling is uncertain. Voice cloning from a few seconds of audio can create governance and consent concerns that are not addressed here. The quality comparison is limited to human preference evaluation against one named baseline. (`c0f8e159fb66` · uncertainty · weaknesses_limitations; [[sources/the-sequence-radar-832-last-week-in-ai-compression-voice-and-why-it-all-matters-01knem857g2mezerkwj34t8vnh|The Sequence Radar #832: Last Week in AI: Compression, Voice, and Why It All Matters]])

## Contradictions / tensions

- The source does not show broad production adoption or failure analysis, so the operational ceiling is uncertain. Voice cloning from a few seconds of audio can create governance and consent concerns that are not addressed here. The quality comparison is limited to human preference evaluation against one named baseline. (uncertainty; [[sources/the-sequence-radar-832-last-week-in-ai-compression-voice-and-why-it-all-matters-01knem857g2mezerkwj34t8vnh|The Sequence Radar #832: Last Week in AI: Compression, Voice, and Why It All Matters]])

## Related pages

- Gemini 3.1 Flash Live

## Sources

- [[sources/the-sequence-radar-832-last-week-in-ai-compression-voice-and-why-it-all-matters-01knem857g2mezerkwj34t8vnh|The Sequence Radar #832: Last Week in AI: Compression, Voice, and Why It All Matters]]
