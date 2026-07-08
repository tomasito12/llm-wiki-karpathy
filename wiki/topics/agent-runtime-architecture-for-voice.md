---
title: Agent Runtime Architecture for Voice
slug: agent-runtime-architecture-for-voice
entity_id: topic:agent-runtime-architecture-for-voice
category: topic
tags:
- agent-orchestration
- agent-systems
- infrastructure
- multimodal-ai
- runtime-architecture
- test-and-verification
- voice-ai
first_seen: '2026-05-07'
last_seen: '2026-06-04'
source_count: 4
evidence_count: 30
source_ids:
- announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn
- building-realtime-voice-agents-in-2026-01krbnc59jhd4hcxphw9zz42zp
- parloa-builds-service-agents-customers-want-to-talk-to-01kr11qtpam16gysk8yxpsbspy
- playing-a-different-game-01kt9zfvk8krrb2yv7mb50hywx
value_level: high
confidence: 0.9299999999999999
synthesis_state: stage1-placeholder
---

# Agent Runtime Architecture for Voice

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Realtime voice agents are better understood as distributed systems than as single models. The useful architecture splits telephony transport, audio streaming, runtime conversation, and deterministic backend actions into separate layers. This separation makes it easier to keep the conversational model flexible while preserving reliability for state, retries, and hand-offs. In practice, the model should decide conversational moves, while the system should own actions with definite outcomes.

## Examples

The source describes the stack as "a phone number, a SIP stack accepting the call, a media pipeline handling the audio, a runtime running the conversation, an integration layer holding the pieces together."

## Key Points

- The model is one box in the diagram, not the whole agent.
- Deterministic actions such as lookups and retries should live outside the model.
- The same runtime pattern can support support, scheduling, lead qualification, or screening by changing prompts and tools.
- Speech-to-text, reasoning, and text-to-speech should be evaluated separately.
- Latency compounds across the full voice pipeline, so model quality alone is not enough.
- Post-call summarization and intent classification are part of the runtime, not just analytics.
- Voice agents must preserve state across long conversations while still responding quickly.
- Transport issues such as packet loss are part of the runtime problem, not an edge case.
- Tool use is integral to voice-agent architecture when the job is completing service tasks.
- Different models can produce materially different call lengths, changing infrastructure cost.
- Real-time speech handling should be treated as a separate layer from answer generation.
- Phone support requires timing and turn-taking discipline, not just textual response quality.
- Handoff is part of the runtime, because many calls cannot be fully resolved by the agent.
- The architecture should support confirmation before action in high-stakes tasks.

## Operational Insight

When a voice agent needs to handle real calls, keep the model on the conversational side and move deterministic work into the surrounding runtime. That boundary reduces brittle behavior and makes the system easier to debug, scale, and hand off.

## Evidence / supporting sources

### Announcing agentic performance benchmarking for Speech to Speech models on... (2026-05-12)

- Voice agents need an execution architecture that can handle speech input, tool calls, long multi-turn interactions, and noisy transport conditions at the same time. A voice runtime is not just a speech layer; it has to preserve conversational state, manage turn timing, and keep the agent moving through a workflow despite interruptions like packet loss or accent mismatch. Operationally, this means voice systems should be designed as interactive workflows with explicit success criteria and failure handling. Performance differences in conversation duration also show that runtime design affects both user experience and operating cost. (`5e11c4dd1cfe` · neutral · knowledge_summary; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- Treat voice as a runtime problem: the model, transport, tool layer, and evaluation harness all need to be designed together if you want reliable automation. (`ff718b4bdd57` · neutral · operational_insight; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- As of 2026-05-12, voice automation depends on more than model quality. Durable voice systems need runtime design that accounts for transport quality, conversational state, and tool execution, which is central to chatbots, voicebots, and contact-center automation. (`9d8e12301781` · neutral · relevance_note; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- Voice agents must preserve state across long conversations while still responding quickly. (`771ecb510522` · supporting · key_points[0]; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- Transport issues such as packet loss are part of the runtime problem, not an edge case. (`6c757f3f7a99` · supporting · key_points[1]; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- Tool use is integral to voice-agent architecture when the job is completing service tasks. (`2980caafc4d5` · supporting · key_points[2]; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- Different models can produce materially different call lengths, changing infrastructure cost. (`14f2c575b438` · supporting · key_points[3]; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])
- Voice channels introduce significant complexity: challenging accents, background noise, and packet loss, all while requiring fast responses, consistency across long multi-turn conversations, and reliable tool use. (`695c6082b622` · supporting · supporting_snippet; [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]])

### Building Realtime Voice Agents in 2026 (2026-05-07)

- The source describes the stack as "a phone number, a SIP stack accepting the call, a media pipeline handling the audio, a runtime running the conversation, an integration layer holding the pieces together." (`7beded7dc9b9` · neutral · examples; [[sources/building-realtime-voice-agents-in-2026-01krbnc59jhd4hcxphw9zz42zp|Building Realtime Voice Agents in 2026]])
- Realtime voice agents are better understood as distributed systems than as single models. The useful architecture splits telephony transport, audio streaming, runtime conversation, and deterministic backend actions into separate layers. This separation makes it easier to keep the conversational model flexible while preserving reliability for state, retries, and hand-offs. In practice, the model should decide conversational moves, while the system should own actions with definite outcomes. (`6bb55b6aa7c7` · neutral · knowledge_summary; [[sources/building-realtime-voice-agents-in-2026-01krbnc59jhd4hcxphw9zz42zp|Building Realtime Voice Agents in 2026]])
- When a voice agent needs to handle real calls, keep the model on the conversational side and move deterministic work into the surrounding runtime. That boundary reduces brittle behavior and makes the system easier to debug, scale, and hand off. (`5da05bca5279` · neutral · operational_insight; [[sources/building-realtime-voice-agents-in-2026-01krbnc59jhd4hcxphw9zz42zp|Building Realtime Voice Agents in 2026]])
- This architecture shows up in call automation, appointment scheduling, and support routing wherever a voice model needs to sit inside a production telephony system. The pattern remains useful because the hard problems are often in transport, state, and orchestration rather than in speech generation itself. (`f4c71e295b97` · neutral · relevance_note; [[sources/building-realtime-voice-agents-in-2026-01krbnc59jhd4hcxphw9zz42zp|Building Realtime Voice Agents in 2026]])
- The model is one box in the diagram, not the whole agent. (`2bd1e9cf4595` · supporting · key_points[0]; [[sources/building-realtime-voice-agents-in-2026-01krbnc59jhd4hcxphw9zz42zp|Building Realtime Voice Agents in 2026]])
- Deterministic actions such as lookups and retries should live outside the model. (`b87873f4b073` · supporting · key_points[1]; [[sources/building-realtime-voice-agents-in-2026-01krbnc59jhd4hcxphw9zz42zp|Building Realtime Voice Agents in 2026]])
- The same runtime pattern can support support, scheduling, lead qualification, or screening by changing prompts and tools. (`51fce5bbf913` · supporting · key_points[2]; [[sources/building-realtime-voice-agents-in-2026-01krbnc59jhd4hcxphw9zz42zp|Building Realtime Voice Agents in 2026]])

### Parloa builds service agents customers want to talk to (2026-05-07)

- Voice agents work best when the runtime is treated as a coordinated system rather than a single prompt. The stack usually separates speech-to-text, model reasoning, retrieval, tool execution, and text-to-speech, because each stage has different failure modes and latency constraints. Production systems also need orchestration rules for routing, handoff, and post-call analysis. The practical unit of design is the end-to-end voice workflow, not the model call alone. (`653ebf1910c5` · neutral · knowledge_summary; [[sources/parloa-builds-service-agents-customers-want-to-talk-to-01kr11qtpam16gysk8yxpsbspy|Parloa builds service agents customers want to talk to]])
- For voice automation, evaluate and control each runtime layer separately, then verify that the layers still work together under realistic traffic and latency pressure. (`3a0e2f3adc42` · neutral · operational_insight; [[sources/parloa-builds-service-agents-customers-want-to-talk-to-01kr11qtpam16gysk8yxpsbspy|Parloa builds service agents customers want to talk to]])
- This is durable because most real voice systems fail at the seams between transcription, reasoning, retrieval, and synthesis. Teams building voicebots and contact-center automation need a layered runtime view to manage latency, accuracy, and escalation risk as of 2026-05-07 and beyond. (`1af072533d21` · neutral · relevance_note; [[sources/parloa-builds-service-agents-customers-want-to-talk-to-01kr11qtpam16gysk8yxpsbspy|Parloa builds service agents customers want to talk to]])
- Speech-to-text, reasoning, and text-to-speech should be evaluated separately. (`d3cc193ec4fc` · supporting · key_points[0]; [[sources/parloa-builds-service-agents-customers-want-to-talk-to-01kr11qtpam16gysk8yxpsbspy|Parloa builds service agents customers want to talk to]])
- Latency compounds across the full voice pipeline, so model quality alone is not enough. (`633e79f22e0e` · supporting · key_points[1]; [[sources/parloa-builds-service-agents-customers-want-to-talk-to-01kr11qtpam16gysk8yxpsbspy|Parloa builds service agents customers want to talk to]])
- Post-call summarization and intent classification are part of the runtime, not just analytics. (`7611d6083658` · supporting · key_points[2]; [[sources/parloa-builds-service-agents-customers-want-to-talk-to-01kr11qtpam16gysk8yxpsbspy|Parloa builds service agents customers want to talk to]])
- Parloa evaluates each component of the voice stack independently: Speech-to-text systems are tested for word error rate, especially for sensitive inputs like policy numbers or account identifiers. Text-to-speech models are evaluated through blind listening tests to assess how natural the voice sounds to real users. (`31c34b18f599` · supporting · supporting_snippet; [[sources/parloa-builds-service-agents-customers-want-to-talk-to-01kr11qtpam16gysk8yxpsbspy|Parloa builds service agents customers want to talk to]])

### Playing a different game (2026-06-04)

- Voice agents benefit from a runtime that separates low-latency speech handling from slower response generation. That split lets the system preserve conversational timing while still allowing policy checks, external actions, and human handoff. In practice, voice quality depends on orchestration details as much as on model quality, because call flow, confirmations, escalation, and context transfer shape the user experience. This pattern becomes especially important when the agent must act in real time on phone calls rather than answer text prompts. (`07295ceea13d` · neutral · knowledge_summary; [[sources/playing-a-different-game-01kt9zfvk8krrb2yv7mb50hywx|Playing a different game]])
- Design voice agents as a layered runtime: keep speech processing on the critical path, isolate slower reasoning or response generation, and make handoff part of the core architecture. That is more durable than treating voice as a simple transcription-plus-chat wrapper. (`d8bf05771fd1` · neutral · operational_insight; [[sources/playing-a-different-game-01kt9zfvk8krrb2yv7mb50hywx|Playing a different game]])
- This pattern matters for any production voicebot because latency, turn-taking, and escalation are part of the core system, not just UI polish. It is especially relevant for customer support and service automation where a voice agent must hold a call, perform actions, and recover cleanly when uncertain. (`380a64674e06` · neutral · relevance_note; [[sources/playing-a-different-game-01kt9zfvk8krrb2yv7mb50hywx|Playing a different game]])
- Real-time speech handling should be treated as a separate layer from answer generation. (`fa05c17b2f86` · supporting · key_points[0]; [[sources/playing-a-different-game-01kt9zfvk8krrb2yv7mb50hywx|Playing a different game]])
- Phone support requires timing and turn-taking discipline, not just textual response quality. (`35bc9239713d` · supporting · key_points[1]; [[sources/playing-a-different-game-01kt9zfvk8krrb2yv7mb50hywx|Playing a different game]])
- Handoff is part of the runtime, because many calls cannot be fully resolved by the agent. (`2303731e079c` · supporting · key_points[2]; [[sources/playing-a-different-game-01kt9zfvk8krrb2yv7mb50hywx|Playing a different game]])
- The architecture should support confirmation before action in high-stakes tasks. (`6c324ea3b490` · supporting · key_points[3]; [[sources/playing-a-different-game-01kt9zfvk8krrb2yv7mb50hywx|Playing a different game]])
- "Most voice AI products are slow because they convert speech to text, send it to a general model, get a text answer, and then convert it back to speech. Fin Voice 2 was designed to work differently, separating the real time layer that handles speech processing, and the layer that generates answers." (`12e07544cdba` · supporting · supporting_snippet; [[sources/playing-a-different-game-01kt9zfvk8krrb2yv7mb50hywx|Playing a different game]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- [[topics/verification-loops-in-ai-workflows|Verification Loops in AI Workflows]]
- [[topics/layered-agent-architecture|Layered Agent Architecture]]
- [[topics/realtime-ai-evaluation|Realtime AI Evaluation]]
- [[topics/support-automation-as-operating-model|Support Automation as Operating Model]]
- [[topics/voice-agents-shift-toward-workflow-completion|Voice Agents Shift Toward Workflow Completion]]

## Sources

- [[sources/announcing-agentic-performance-benchmarking-for-speech-to-speech-models-on-01krgrx80q2dg5k4a2bcx1b5xn|Announcing agentic performance benchmarking for Speech to Speech models on...]]
- [[sources/building-realtime-voice-agents-in-2026-01krbnc59jhd4hcxphw9zz42zp|Building Realtime Voice Agents in 2026]]
- [[sources/parloa-builds-service-agents-customers-want-to-talk-to-01kr11qtpam16gysk8yxpsbspy|Parloa builds service agents customers want to talk to]]
- [[sources/playing-a-different-game-01kt9zfvk8krrb2yv7mb50hywx|Playing a different game]]
