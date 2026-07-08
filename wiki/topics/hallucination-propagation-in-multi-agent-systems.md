---
title: Hallucination Propagation in Multi-Agent Systems
slug: hallucination-propagation-in-multi-agent-systems
entity_id: topic:hallucination-propagation-in-multi-agent-systems
category: topic
tags:
- agent-memory
- agent-systems
- alignment-failures
- auditability
first_seen: '2026-03-16'
last_seen: '2026-03-16'
source_count: 1
evidence_count: 8
source_ids:
- mirofish-swarm-intelligence-with-1m-agents-that-can-predict-everything-01kqg04cw3fx7h5w108h6vsq77
value_level: high
confidence: 0.98
synthesis_state: stage1-placeholder
---

# Hallucination Propagation in Multi-Agent Systems

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
When multiple agents can read and reuse each other’s outputs, an invented fact can spread through the system and become persistent shared memory. That makes falsehood propagation a structural problem, not just an individual model error. In simulation systems, this is especially dangerous because emergent consensus can look identical to contamination. The practical challenge is to preserve interaction effects while still tracking what entered the system from grounded sources versus generated noise.

## Key Points

- Shared memory turns one hallucination into a system-level contamination risk.
- Consensus and hallucination cascade can look the same from the outside.
- Memory provenance metadata is a practical mitigation because it helps distinguish grounded facts from absorbed model output.
- Simulation systems need evaluation methods that can separate emergence from error propagation.

## Operational Insight

Multi-agent systems that share memory or social channels need provenance on every memory write, not just generic moderation or post-processing. Without that, the system can reward self-reinforcing error cascades and misread them as convergence.

## Evidence / supporting sources

### MiroFish: Swarm-Intelligence with 1M Agents That Can Predict Everything (2026-03-16)

- When multiple agents can read and reuse each other’s outputs, an invented fact can spread through the system and become persistent shared memory. That makes falsehood propagation a structural problem, not just an individual model error. In simulation systems, this is especially dangerous because emergent consensus can look identical to contamination. The practical challenge is to preserve interaction effects while still tracking what entered the system from grounded sources versus generated noise. (`91482c455a2e` · neutral · knowledge_summary; [[sources/mirofish-swarm-intelligence-with-1m-agents-that-can-predict-everything-01kqg04cw3fx7h5w108h6vsq77|MiroFish: Swarm-Intelligence with 1M Agents That Can Predict Everything]])
- Multi-agent systems that share memory or social channels need provenance on every memory write, not just generic moderation or post-processing. Without that, the system can reward self-reinforcing error cascades and misread them as convergence. (`278d545ba725` · neutral · operational_insight; [[sources/mirofish-swarm-intelligence-with-1m-agents-that-can-predict-everything-01kqg04cw3fx7h5w108h6vsq77|MiroFish: Swarm-Intelligence with 1M Agents That Can Predict Everything]])
- This is durable because any agent system with shared memory, social feed effects, or conversational recursion can suffer the same failure mode. It directly affects evaluation, auditability, and whether outputs are safe to trust in service automation or decision support. (`575f1d24c63f` · neutral · relevance_note; [[sources/mirofish-swarm-intelligence-with-1m-agents-that-can-predict-everything-01kqg04cw3fx7h5w108h6vsq77|MiroFish: Swarm-Intelligence with 1M Agents That Can Predict Everything]])
- Shared memory turns one hallucination into a system-level contamination risk. (`92848960586f` · supporting · key_points[0]; [[sources/mirofish-swarm-intelligence-with-1m-agents-that-can-predict-everything-01kqg04cw3fx7h5w108h6vsq77|MiroFish: Swarm-Intelligence with 1M Agents That Can Predict Everything]])
- Consensus and hallucination cascade can look the same from the outside. (`a9ce74433b58` · supporting · key_points[1]; [[sources/mirofish-swarm-intelligence-with-1m-agents-that-can-predict-everything-01kqg04cw3fx7h5w108h6vsq77|MiroFish: Swarm-Intelligence with 1M Agents That Can Predict Everything]])
- Memory provenance metadata is a practical mitigation because it helps distinguish grounded facts from absorbed model output. (`60eb02d56c66` · supporting · key_points[2]; [[sources/mirofish-swarm-intelligence-with-1m-agents-that-can-predict-everything-01kqg04cw3fx7h5w108h6vsq77|MiroFish: Swarm-Intelligence with 1M Agents That Can Predict Everything]])
- Simulation systems need evaluation methods that can separate emergence from error propagation. (`b6f3086a582a` · supporting · key_points[3]; [[sources/mirofish-swarm-intelligence-with-1m-agents-that-can-predict-everything-01kqg04cw3fx7h5w108h6vsq77|MiroFish: Swarm-Intelligence with 1M Agents That Can Predict Everything]])
- "Agent A hallucinates a fact during generation Agent A posts this hallucinated fact to the simulated social platform Agents B, C, and D read the post and incorporate it into their memory They share it in their own posts and comments 50 simulation rounds later, the entire population is making decisions based on information that never existed" (`618d29d2bfaf` · supporting · supporting_snippet; [[sources/mirofish-swarm-intelligence-with-1m-agents-that-can-predict-everything-01kqg04cw3fx7h5w108h6vsq77|MiroFish: Swarm-Intelligence with 1M Agents That Can Predict Everything]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- [[topics/provenance-tracking|Provenance Tracking]]
- [[topics/agent-memory-architecture|Agent Memory Architecture]]

## Sources

- [[sources/mirofish-swarm-intelligence-with-1m-agents-that-can-predict-everything-01kqg04cw3fx7h5w108h6vsq77|MiroFish: Swarm-Intelligence with 1M Agents That Can Predict Everything]]
