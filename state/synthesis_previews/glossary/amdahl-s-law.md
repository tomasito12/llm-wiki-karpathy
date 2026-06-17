---
title: Amdahl's law
slug: amdahl-s-law
entity_id: glossary:amdahl-s-law
category: glossary
tags:
- agent-systems
- inference
- orchestration
first_seen: '2026-05-28'
last_seen: '2026-05-28'
source_count: 2
evidence_count: 8
source_ids:
- the-orchestration-tax-01ktjzc8r76ht9hhzs4xpejf7y
- when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp
value_level: high
confidence: 0.935
synthesis_state: synthesized
synthesis_stale: false
synthesis_input_hash: 3895c322cb4594c0
current_input_hash: 3895c322cb4594c0
synthesis_schema_version: 1
synthesis_prompt_version: 1
last_synthesized_at: '2026-06-17T19:54:09Z'
---

# Amdahl's law

## Executive synthesis

Amdahl's law is the idea that overall speedup is capped by the part of a process that cannot be sped up. In the sources here, it is used as a practical lens for AI workflows: even if model generation or task execution becomes much faster, the end-to-end system may still be limited by human review, approval, data access, or verification. The main lesson is to identify the remaining serial bottleneck before assuming more parallel workers or better automation will improve total throughput.

## Context card

- **Use this page when:** Use this page when you need the practical meaning of Amdahl's law in AI engineering: checking whether a faster model, more agents, or more parallelism will actually improve end-to-end throughput.
- **Best for questions about:** How Amdahl's law applies to AI workflows and agent systems, Why speeding up one component may not improve total throughput much, How to size concurrency against the real bottleneck in human-AI workflows, When model automation does not translate into organizational speedups
- **Not enough for:** A full mathematical treatment of Amdahl's law, Quantitative estimates for a specific system without local measurements, Cases where the bottleneck shifts over time or where multiple bottlenecks interact
- **Strongest sources:** The Orchestration Tax, When AI builds itself
- **Related tags:** agent-systems, inference, orchestration

## What to remember

- The key idea: the serial part sets the ceiling on total speedup.
- More parallel work helps only until the serial bottleneck dominates.
- In AI systems, the slow step is often review, approval, or verification rather than generation.
- This is a useful sanity check when planning agent concurrency or automation gains.

## Consensus

- Amdahl's law says the speedup from parallelizing work is limited by the part of the workflow that must stay serial.
- If one step remains slow, adding more workers to other steps eventually gives diminishing returns.
- For AI and agent systems, faster model output does not automatically produce faster end-to-end delivery if review, approval, verification, or integration stay bottlenecks.

## Tensions / open questions

- There is no disagreement in the sources, but the page is an application-oriented interpretation rather than a formal mathematical discussion.
- The sources emphasize human and organizational bottlenecks; they do not show when the bottleneck moves or how to measure its size precisely.

## Evidence quality

- Evidence is strong for the basic definition and the workflow bottleneck interpretation; both sources agree closely.
- Evidence is context-specific rather than mathematical: it is about AI orchestration, human review, and organizational throughput, not a formal proof page.
- The sources are aligned and reinforce each other, but they do not add numerical bounds or system-specific measurements.

## Practical takeaway

Before adding more agents or parallelizing work, ask which step is still serial. If review, approval, or verification is the slowest part, improve that bottleneck first or expect diminishing returns.

## Evidence index

- Sources: 2
- Evidence items: 8
- Current input hash: `3895c322cb4594c0`
- Cached input hash: `3895c322cb4594c0`
- Last synthesized: 2026-06-17T19:54:09Z
- Synthesis status: `fresh`

## Related pages

No related pages captured.

## Sources

- [[sources/the-orchestration-tax-01ktjzc8r76ht9hhzs4xpejf7y|The Orchestration Tax]]
- [[sources/when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp|When AI builds itself]]
