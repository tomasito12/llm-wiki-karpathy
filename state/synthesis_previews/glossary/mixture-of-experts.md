---
title: Mixture-of-Experts
slug: mixture-of-experts
entity_id: glossary:mixture-of-experts
category: glossary
tags:
- ai-engineering
- inference
- model-architecture
- orchestration
- runtime-architecture
first_seen: '2026-04-09'
last_seen: '2026-05-12'
source_count: 5
evidence_count: 20
source_ids:
- ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8
- choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj
- i-ran-gemma-4-locally-here-s-what-nobody-s-telling-you-01kqfzwx5z81csjrvzvv6xgq9x
- i-spent-3-days-researching-self-hosted-ai-here-s-why-you-should-and-shouldn-t-actually-do-it-01kqkvbh9k2p2m6eh234khs2kf
- kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6
value_level: high
confidence: 0.936
synthesis_state: synthesized
synthesis_stale: false
synthesis_input_hash: 634af74296cc4b9f
current_input_hash: 634af74296cc4b9f
synthesis_schema_version: 1
synthesis_prompt_version: 1
last_synthesized_at: '2026-07-10T12:03:25Z'
---

# Mixture-of-Experts

## Executive synthesis

Mixture-of-Experts (MoE) is a model architecture that keeps a large total parameter count but activates only a subset of expert sub-networks for each token or input. In practice, that means MoE can offer more capability per unit of compute than a dense model, which is why it comes up in serving, local deployment, and high-throughput systems. The key thing to remember is that benchmark or size comparisons can be misleading unless you look at active parameters and routing behavior, since those determine real inference cost and can also affect consistency. The main caveat is that MoE shifts complexity into the router and serving stack: if routing is weak or the runtime support is poor, the efficiency gains can be offset by uneven behavior or deployment friction.

## Example in practice

### Serving a high-volume assistant

A team choosing a model for a coding assistant or internal copilot may prefer an MoE model when it needs strong capability at high request volume without activating every parameter on every request. In the sources, this shows up in examples like models with very large total parameters but only a much smaller active slice per token, which can make them cheaper to serve than a dense model of similar nominal size. The practical decision is not just “which model is biggest,” but “which one fits the latency, cost, and runtime constraints of the deployment.”

- Why it helps: It makes the abstract idea concrete: MoE is mainly a deployment choice about how to trade capacity for compute, not just a model-size label.

- Basis: `source-grounded`

## Context card

- **Use this page when:** Use this page when deciding whether an MoE model is a good fit for deployment, when interpreting benchmark claims that may hide active-parameter costs, or when you need a quick definition of conditional compute in model architecture.
- **Best for questions about:** What Mixture-of-Experts means in practice, Why an MoE model can be large but still relatively cheap to run, How active parameters differ from total parameters, Why routing quality affects MoE behavior, When MoE is relevant for serving, local deployment, or high-throughput systems
- **Not enough for:** A full technical explanation of MoE training algorithms, Comparative benchmark rankings between specific MoE and dense models beyond the cited examples, Detailed runtime or quantization guidance for a specific hardware setup, Claims about universal superiority of MoE over dense models
- **Strongest sources:** Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks, I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You., Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better, [AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD
- **Related tags:** ai-engineering, inference, model-architecture, orchestration, runtime-architecture

## What to remember

- MoE = conditional compute: only part of the model is active per token or input.
- Total parameters can be very large even when active parameters are small.
- Routing quality matters as much as raw model size for real-world behavior.
- MoE is mainly a deployment/inference tradeoff: capability vs. compute, latency, and cost.
- Benchmark comparisons can be misleading if they ignore active parameters.
- MoE is most relevant for serving, local deployment, and high-throughput automation.

## Consensus

- Mixture-of-Experts (MoE) is an architecture that routes each input, token, or task through only a subset of specialized expert blocks instead of activating the full network every time.
- The main practical effect is conditional compute: a model can keep a very large total parameter count while using far fewer active parameters per inference step.
- Sources agree MoE is useful when teams want better capability or capacity without paying the full inference cost of a dense model of similar nominal size.
- Routing behavior is central to MoE performance; the router decides which experts handle each token or input.
- MoE matters most in deployment decisions where inference cost, latency, throughput, hardware fit, and benchmark interpretation all matter.

## Tensions / open questions

- MoE can look much stronger than a dense model if you compare only total parameters or headline benchmarks, but the real operating cost depends on active parameters and routing.
- MoE is attractive for efficiency and throughput, yet it adds routing complexity and can produce uneven or brittle behavior if the router or serving stack is weak.
- Sources frame MoE as broadly useful in production, but the evidence is mostly practical commentary rather than formal technical evaluation, so the page is best used as a working glossary entry rather than a definitive research summary.

## Evidence quality

- Evidence is fairly strong and consistent across five sources, with repeated definitions and deployment-focused explanations.
- Most claims are second-order synthesis from commentary, not primary technical documentation; useful for understanding practical meaning but not for formal specification.
- A few numeric examples are included in the sources, but this page should treat them as illustrative rather than normative.
- The evidence emphasizes production and inference concerns more than training or research details.

## Practical takeaway

Treat MoE as a compute-saving way to scale capacity, not as a free performance upgrade. When evaluating one, compare active parameters, routing quality, latency, and runtime compatibility—not just total parameter count.

## Evidence index

- Sources: 5
- Evidence items: 20
- Current input hash: `634af74296cc4b9f`
- Cached input hash: `634af74296cc4b9f`
- Last synthesized: 2026-07-10T12:03:25Z
- Synthesis status: `fresh`

## Related pages

- [[glossary/benchmark|Benchmark]]

## Sources

- [[sources/ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8|[AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD]]
- [[sources/choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj|Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks]]
- [[sources/i-ran-gemma-4-locally-here-s-what-nobody-s-telling-you-01kqfzwx5z81csjrvzvv6xgq9x|I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You.]]
- [[sources/i-spent-3-days-researching-self-hosted-ai-here-s-why-you-should-and-shouldn-t-actually-do-it-01kqkvbh9k2p2m6eh234khs2kf|I Spent 3 Days Researching Self-Hosted AI. Here’s Why You Should (And Shouldn’t) Actually Do It]]
- [[sources/kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6|Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better]]
