---
title: OASIS
slug: oasis
entity_id: tool:oasis
category: tool
tags:
- agentic
- multi-step-execution
- open-source
- tool-use
first_seen: '2026-03-16'
last_seen: '2026-03-16'
source_count: 1
evidence_count: 13
source_ids:
- mirofish-swarm-intelligence-with-1m-agents-that-can-predict-everything-01kqg04cw3fx7h5w108h6vsq77
value_level: high
confidence: 0.82
synthesis_state: stage1-placeholder
types:
- ai-infrastructure
- ai-orchestration
---

# OASIS

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
An open-source framework for running large-scale agent social simulations. It handles the environment, scheduling, recommendation logic, and distributed inference needed to scale many LLM-backed agents.

## Core Capabilities

- It can scale agent social simulations to one million agents, which enables emergence studies at a size that small bespoke harnesses cannot handle.
- It provides social actions like following, commenting, reposting, liking, muting, and searching, which lets simulations mimic platform-like interaction patterns.
- It distributes LLM calls across GPUs, which is important because multi-agent simulations can become inference-bound very quickly.
- It manages simulation time and agent scheduling so that actions can be triggered by simulated chronology rather than manual turn-taking.

## Integration Ecosystem

- It is described as the framework underneath MiroFish, so it is already used as the runtime layer for a GraphRAG-driven simulation pipeline.
- It integrates with GPU-based distributed inference for large agent runs, which is central to keeping throughput viable.
- The article also shows it can sit alongside different knowledge-graph backends and local or remote model providers in the broader stack.

## Maturity signals

The source describes it as powering a project that can scale to one million agents, which suggests a technically ambitious and modular system. It also appears flexible enough to run with different knowledge-graph backends and local or remote inference setups. At the same time, the article emphasizes missing benchmarks and unresolved reliability issues, so maturity is best read as strong prototype maturity rather than proven production reliability as of 2026-03-16.

## Strengths

- Scales to very large agent counts, which matters when you need emergent behavior rather than a few scripted turns.
- Separates environment logic, time progression, recommendation systems, and inference distribution, which makes the stack easier to reason about and swap pieces independently.
- Supports multiple social actions such as following, commenting, reposting, liking, muting, and searching, so simulations can model richer interaction patterns than simple chat loops.

## Weaknesses / limitations

- The source does not provide published benchmarks against real-world outcomes, so the quality of simulation outputs remains unverified.
- Large-scale runs are expensive because each agent decision can require model inference, and the article warns that per-token hallucination detection would add prohibitive overhead at scale.
- The tool can make hallucination cascades look like consensus, so users need extra provenance and evaluation machinery before trusting outputs for high-stakes decisions.

## Evidence / supporting sources

### MiroFish: Swarm-Intelligence with 1M Agents That Can Predict Everything (2026-03-16)

- It is described as the framework underneath MiroFish, so it is already used as the runtime layer for a GraphRAG-driven simulation pipeline. (`e4eb1eaad5b4` · neutral · integration_ecosystem[0]; [[sources/mirofish-swarm-intelligence-with-1m-agents-that-can-predict-everything-01kqg04cw3fx7h5w108h6vsq77|MiroFish: Swarm-Intelligence with 1M Agents That Can Predict Everything]])
- It integrates with GPU-based distributed inference for large agent runs, which is central to keeping throughput viable. (`8f7ba1defb4e` · neutral · integration_ecosystem[1]; [[sources/mirofish-swarm-intelligence-with-1m-agents-that-can-predict-everything-01kqg04cw3fx7h5w108h6vsq77|MiroFish: Swarm-Intelligence with 1M Agents That Can Predict Everything]])
- The article also shows it can sit alongside different knowledge-graph backends and local or remote model providers in the broader stack. (`70ef14a55ddf` · neutral · integration_ecosystem[2]; [[sources/mirofish-swarm-intelligence-with-1m-agents-that-can-predict-everything-01kqg04cw3fx7h5w108h6vsq77|MiroFish: Swarm-Intelligence with 1M Agents That Can Predict Everything]])
- The source describes it as powering a project that can scale to one million agents, which suggests a technically ambitious and modular system. It also appears flexible enough to run with different knowledge-graph backends and local or remote inference setups. At the same time, the article emphasizes missing benchmarks and unresolved reliability issues, so maturity is best read as strong prototype maturity rather than proven production reliability as of 2026-03-16. (`a5590473009d` · neutral · maturity_signals; [[sources/mirofish-swarm-intelligence-with-1m-agents-that-can-predict-everything-01kqg04cw3fx7h5w108h6vsq77|MiroFish: Swarm-Intelligence with 1M Agents That Can Predict Everything]])
- This is useful when the core problem is not just orchestrating agents, but running them inside a simulated social world with feeds, posts, and timed actions. It fits agent-system builders who need a reusable simulation runtime rather than a task executor. For service automation teams, it is more of an experimentation substrate than a customer-facing automation product. (`aef6fba1b75f` · neutral · operational_relevance; [[sources/mirofish-swarm-intelligence-with-1m-agents-that-can-predict-everything-01kqg04cw3fx7h5w108h6vsq77|MiroFish: Swarm-Intelligence with 1M Agents That Can Predict Everything]])
- An open-source framework for running large-scale agent social simulations. It handles the environment, scheduling, recommendation logic, and distributed inference needed to scale many LLM-backed agents. (`923eca409856` · neutral · short_description; [[sources/mirofish-swarm-intelligence-with-1m-agents-that-can-predict-everything-01kqg04cw3fx7h5w108h6vsq77|MiroFish: Swarm-Intelligence with 1M Agents That Can Predict Everything]])
- - Scales to very large agent counts, which matters when you need emergent behavior rather than a few scripted turns.
- Separates environment logic, time progression, recommendation systems, and inference distribution, which makes the stack easier to reason about and swap pieces independently.
- Supports multiple social actions such as following, commenting, reposting, liking, muting, and searching, so simulations can model richer interaction patterns than simple chat loops. (`eac8638eca00` · neutral · strengths; [[sources/mirofish-swarm-intelligence-with-1m-agents-that-can-predict-everything-01kqg04cw3fx7h5w108h6vsq77|MiroFish: Swarm-Intelligence with 1M Agents That Can Predict Everything]])
- It can scale agent social simulations to one million agents, which enables emergence studies at a size that small bespoke harnesses cannot handle. (`52bff53787cc` · supporting · core_capabilities[0]; [[sources/mirofish-swarm-intelligence-with-1m-agents-that-can-predict-everything-01kqg04cw3fx7h5w108h6vsq77|MiroFish: Swarm-Intelligence with 1M Agents That Can Predict Everything]])
- It provides social actions like following, commenting, reposting, liking, muting, and searching, which lets simulations mimic platform-like interaction patterns. (`7cac5b11694f` · supporting · core_capabilities[1]; [[sources/mirofish-swarm-intelligence-with-1m-agents-that-can-predict-everything-01kqg04cw3fx7h5w108h6vsq77|MiroFish: Swarm-Intelligence with 1M Agents That Can Predict Everything]])
- It distributes LLM calls across GPUs, which is important because multi-agent simulations can become inference-bound very quickly. (`52fcd69de56e` · supporting · core_capabilities[2]; [[sources/mirofish-swarm-intelligence-with-1m-agents-that-can-predict-everything-01kqg04cw3fx7h5w108h6vsq77|MiroFish: Swarm-Intelligence with 1M Agents That Can Predict Everything]])
- It manages simulation time and agent scheduling so that actions can be triggered by simulated chronology rather than manual turn-taking. (`24e06c2c1e6b` · supporting · core_capabilities[3]; [[sources/mirofish-swarm-intelligence-with-1m-agents-that-can-predict-everything-01kqg04cw3fx7h5w108h6vsq77|MiroFish: Swarm-Intelligence with 1M Agents That Can Predict Everything]])
- "MiroFish is powered by OASIS (Open Agent Social Interaction Simulations) framework by CAMEL-AI, it can scale to one million agents with 23 different social actions such as following, commenting, reposting, liking, muting, searching. It handles the environment logic, the recommendation systems, the time engine that activates agents on schedules, and the scalable inference layer that distributes LLM calls across GPUs." (`e6a2dfd50c73` · supporting · supporting_snippet; [[sources/mirofish-swarm-intelligence-with-1m-agents-that-can-predict-everything-01kqg04cw3fx7h5w108h6vsq77|MiroFish: Swarm-Intelligence with 1M Agents That Can Predict Everything]])
- - The source does not provide published benchmarks against real-world outcomes, so the quality of simulation outputs remains unverified.
- Large-scale runs are expensive because each agent decision can require model inference, and the article warns that per-token hallucination detection would add prohibitive overhead at scale.
- The tool can make hallucination cascades look like consensus, so users need extra provenance and evaluation machinery before trusting outputs for high-stakes decisions. (`ac98e5d6ae75` · uncertainty · weaknesses_limitations; [[sources/mirofish-swarm-intelligence-with-1m-agents-that-can-predict-everything-01kqg04cw3fx7h5w108h6vsq77|MiroFish: Swarm-Intelligence with 1M Agents That Can Predict Everything]])

## Contradictions / tensions

- - The source does not provide published benchmarks against real-world outcomes, so the quality of simulation outputs remains unverified.
- Large-scale runs are expensive because each agent decision can require model inference, and the article warns that per-token hallucination detection would add prohibitive overhead at scale.
- The tool can make hallucination cascades look like consensus, so users need extra provenance and evaluation machinery before trusting outputs for high-stakes decisions. (uncertainty; [[sources/mirofish-swarm-intelligence-with-1m-agents-that-can-predict-everything-01kqg04cw3fx7h5w108h6vsq77|MiroFish: Swarm-Intelligence with 1M Agents That Can Predict Everything]])

## Related pages

- [[tools/neo4j|Neo4j]]

## Sources

- [[sources/mirofish-swarm-intelligence-with-1m-agents-that-can-predict-everything-01kqg04cw3fx7h5w108h6vsq77|MiroFish: Swarm-Intelligence with 1M Agents That Can Predict Everything]]
