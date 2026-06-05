---
title: Continuous-time interaction
slug: continuous-time-interaction
entity_id: glossary:continuous-time-interaction
category: glossary
tags:
- interactive-ai
first_seen: '2026-05-12'
last_seen: '2026-05-12'
source_count: 1
evidence_count: 4
source_ids:
- ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8
value_level: high
confidence: 0.93
synthesis_state: stage1-placeholder
---

# Continuous-time interaction

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
A model interaction style where perception, reasoning, and response are handled as an ongoing stream instead of as discrete user turns. The system can listen, speak, and react while a conversation or task is still unfolding.

## Relevance Note

Continuous-time interaction is an important operational concept for voice assistants, live copilots, and multimodal agents that must respond fluidly under timing pressure. It affects evaluation, UI design, and orchestration because the system must reason about when to speak as much as what to say.

## Evidence / supporting sources

### [AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD (2026-05-12)

- This idea matters when the assistant needs to react at the right moment rather than wait for a clean prompt-response boundary. It is especially useful for voice, video, and live collaborative settings where timing is part of the task itself. The engineering challenge is that the model must manage silence, interruption, overlap, and partial evidence without breaking the user experience. That typically requires tighter coupling between streaming input, policy decisions, and output timing than standard chat systems use. (`2b1f449fc0f2` · neutral · extended_explanation; [[sources/ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8|[AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD]])
- A model interaction style where perception, reasoning, and response are handled as an ongoing stream instead of as discrete user turns. The system can listen, speak, and react while a conversation or task is still unfolding. (`72bc57fedcba` · neutral · proposed_definition; [[sources/ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8|[AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD]])
- Continuous-time interaction is an important operational concept for voice assistants, live copilots, and multimodal agents that must respond fluidly under timing pressure. It affects evaluation, UI design, and orchestration because the system must reason about when to speak as much as what to say. (`f69bce8758f1` · neutral · relevance_note; [[sources/ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8|[AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD]])
- "models trained from scratch for real-time interaction rather than layering speech, turn-taking, and tool use onto a turn-based LLM" (`247c6cf62db4` · supporting · supporting_snippet; [[sources/ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8|[AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

No related pages captured.

## Sources

- [[sources/ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8|[AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD]]
