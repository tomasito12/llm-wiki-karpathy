---
title: Mixture-of-Experts
slug: mixture-of-experts
entity_id: glossary:mixture-of-experts
category: glossary
tags:
- ai-engineering
- inference
- orchestration
- runtime-architecture
- tool-use
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
synthesis_state: stage1-placeholder
---

# Mixture-of-Experts

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
A mixture-of-experts model is a machine learning model that routes each input through only a subset of its internal parameters, rather than activating the full network every time. This lets the model scale up capacity without making every inference proportionally expensive.

## Relevance Note

Mixture-of-experts matters in production because it changes the compute-to-capability tradeoff for serving models. It is especially relevant for local deployment, latency-sensitive inference, and cost-constrained automation where full dense-model activation would be too expensive.

## Evidence / supporting sources

### [AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD (2026-05-12)

- In practice, mixture-of-experts systems try to get more model capability per unit of compute by turning on only the experts needed for a given input. That makes them attractive for large models that need to stay efficient at inference time. The tradeoff is that routing quality, expert balance, and serving complexity matter a lot, because a poorly tuned router can waste capacity or create brittle behavior. For product teams, the appeal is often better capability at a given latency or cost envelope, especially when the model must stay responsive in live workflows. (`f00294112aa0` · neutral · extended_explanation; [[sources/ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8|[AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD]])
- A model architecture that routes each input through only a subset of specialized submodels, rather than activating every parameter for every token. This can raise capacity without making every inference path proportionally expensive. (`448370ee2802` · neutral · proposed_definition; [[sources/ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8|[AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD]])
- Mixture-of-experts is a durable architecture pattern for building large-capacity systems that still need controllable inference cost. It shows up in model serving, routing, and capacity planning when teams care about quality without paying for all parameters on every request. (`195c610d516c` · neutral · relevance_note; [[sources/ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8|[AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD]])
- "TML-Interaction-Small is a 276B parameter MoE with 12B active." (`c036eeef34fe` · supporting · supporting_snippet; [[sources/ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8|[AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD]])

### Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks (2026-04-20)

- In practice, the key distinction is between total parameters and active parameters. A Mixture-of-Experts model may have a very large total capacity, but only a small slice of it is used for each token. That means benchmark numbers can look much better than a dense model of similar size if you do not account for how many parameters are actually active. The main operational consequence is that routing and active-parameter count matter when comparing speed, memory, and deployment fit. (`0618678f9ce7` · neutral · extended_explanation; [[sources/choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj|Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks]])
- A Mixture-of-Experts model routes each token or input to a subset of specialized submodels rather than activating the full parameter set every time. This can make the model cheaper or faster at inference while still retaining a large total parameter count. (`76d085c56fb3` · neutral · proposed_definition; [[sources/choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj|Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks]])
- Mixture-of-Experts affects inference cost, latency, and benchmark interpretation in production model selection. It matters for service automation because apparent speedups can be misleading if teams compare MoE and dense models without accounting for active parameters and routing behavior. (`51c4a45f4688` · neutral · relevance_note; [[sources/choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj|Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks]])
- "Qwen3.5–35B-A3B is a Mixture-of-Experts model (35B total parameters, 3B active per token, 256 experts, 8 routed plus 1 shared active)." (`f45a1c1e035c` · supporting · supporting_snippet; [[sources/choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj|Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks]])

### I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You. (2026-04-09)

- The core idea is conditional compute: a router decides which expert blocks should process a token or input. In practice, that can make a model feel much larger than the hardware cost would suggest, because only part of the model is active at each step. Practitioners care about this when they want stronger capability, longer context, or lower inference cost than a dense model of similar nominal size would require. The tradeoff is that quality depends heavily on routing behavior, serving stack support, and quantization/runtime compatibility. (`2ef34bd0320b` · neutral · extended_explanation; [[sources/i-ran-gemma-4-locally-here-s-what-nobody-s-telling-you-01kqfzwx5z81csjrvzvv6xgq9x|I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You.]])
- A mixture-of-experts model is a machine learning model that routes each input through only a subset of its internal parameters, rather than activating the full network every time. This lets the model scale up capacity without making every inference proportionally expensive. (`8f15fdaa3130` · neutral · proposed_definition; [[sources/i-ran-gemma-4-locally-here-s-what-nobody-s-telling-you-01kqfzwx5z81csjrvzvv6xgq9x|I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You.]])
- Mixture-of-experts matters in production because it changes the compute-to-capability tradeoff for serving models. It is especially relevant for local deployment, latency-sensitive inference, and cost-constrained automation where full dense-model activation would be too expensive. (`4dd153319396` · neutral · relevance_note; [[sources/i-ran-gemma-4-locally-here-s-what-nobody-s-telling-you-01kqfzwx5z81csjrvzvv6xgq9x|I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You.]])
- Gemma 4 is a
M
ixture-
O
f-
E
xperts model. That’s not marketing language, it’s the reason this thing fits on hardware you already own. (`cc9e71034e15` · supporting · supporting_snippet; [[sources/i-ran-gemma-4-locally-here-s-what-nobody-s-telling-you-01kqfzwx5z81csjrvzvv6xgq9x|I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You.]])

### I Spent 3 Days Researching Self-Hosted AI. Here’s Why You Should (And Shouldn’t) Actually Do It (2026-04-22)

- Mixture-of-experts models split a system into specialized parts and activate only the parts needed for a given input. In practice, that can make a model cheaper or faster to run than a dense model of similar total size. The tradeoff is that routing and specialization can introduce uneven behavior, especially if the activated portion is too small for complex tasks. Teams care about this because MoE models often sit at the intersection of performance, cost, and deployment complexity. (`9fb1853a0a0e` · neutral · extended_explanation; [[sources/i-spent-3-days-researching-self-hosted-ai-here-s-why-you-should-and-shouldn-t-actually-do-it-01kqkvbh9k2p2m6eh234khs2kf|I Spent 3 Days Researching Self-Hosted AI. Here’s Why You Should (And Shouldn’t) Actually Do It]])
- A model architecture that routes each input through only a subset of its parameters rather than activating the full model every time. This can reduce inference cost while keeping a large total parameter count. (`3003b75eca3f` · neutral · proposed_definition; [[sources/i-spent-3-days-researching-self-hosted-ai-here-s-why-you-should-and-shouldn-t-actually-do-it-01kqkvbh9k2p2m6eh234khs2kf|I Spent 3 Days Researching Self-Hosted AI. Here’s Why You Should (And Shouldn’t) Actually Do It]])
- Mixture-of-experts models matter in deployed AI systems because they can lower inference cost while preserving useful capability, which affects latency, hardware requirements, and agent throughput. They are especially relevant when teams need to balance cost against quality in coding assistants, internal copilots, and other high-volume workloads. (`d8ca602e8c45` · neutral · relevance_note; [[sources/i-spent-3-days-researching-self-hosted-ai-here-s-why-you-should-and-shouldn-t-actually-do-it-01kqkvbh9k2p2m6eh234khs2kf|I Spent 3 Days Researching Self-Hosted AI. Here’s Why You Should (And Shouldn’t) Actually Do It]])
- “GLM-4.7-Flash (MoE, 3B active params)” (`96bec9001e18` · supporting · supporting_snippet; [[sources/i-spent-3-days-researching-self-hosted-ai-here-s-why-you-should-and-shouldn-t-actually-do-it-01kqkvbh9k2p2m6eh234khs2kf|I Spent 3 Days Researching Self-Hosted AI. Here’s Why You Should (And Shouldn’t) Actually Do It]])

### Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better (2026-04-20)

- Mixture-of-Experts models are often used when teams want very large model capacity without paying the full inference cost of activating every parameter on every request. In practice, the router decides which expert sub-networks should handle a token or task. That can make the model more efficient, but it also adds routing complexity and can create uneven behavior if the routing policy is weak. For AI systems that need high throughput, the architecture can be a useful way to balance capability and cost. (`0a96870b91c6` · neutral · extended_explanation; [[sources/kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6|Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better]])
- A model architecture that routes each input through only a subset of its total parameters. This lets the system keep large capacity while limiting the compute used for each token. (`a53eab847b96` · neutral · proposed_definition; [[sources/kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6|Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better]])
- Mixture-of-Experts matters in production because it can make very large models cheaper to serve than dense models of similar total size. It is especially relevant when inference volume is high and routing quality is important to maintain consistency across tasks. (`6820ff1a6e60` · neutral · relevance_note; [[sources/kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6|Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better]])
- Kimi K2.5 is a
Mixture-of-Experts model with 1.04 trillion total parameters
, activating only
32 billion per token
at inference time. (`8825d4dfb9ab` · supporting · supporting_snippet; [[sources/kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6|Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- [[glossary/benchmark|Benchmark]]

## Sources

- [[sources/ainews-thinking-machines-native-interaction-models-tml-interaction-small-276b-a12b-advances-sota-realtime-voice-and-kills-standard-vad-01krd7h0s789k86g2yk4qr8zg8|[AINews] Thinking Machines' Native Interaction Models - TML-Interaction-Small 276B-A12B - advances SOTA Realtime Voice and kills standard VAD]]
- [[sources/choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj|Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks]]
- [[sources/i-ran-gemma-4-locally-here-s-what-nobody-s-telling-you-01kqfzwx5z81csjrvzvv6xgq9x|I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You.]]
- [[sources/i-spent-3-days-researching-self-hosted-ai-here-s-why-you-should-and-shouldn-t-actually-do-it-01kqkvbh9k2p2m6eh234khs2kf|I Spent 3 Days Researching Self-Hosted AI. Here’s Why You Should (And Shouldn’t) Actually Do It]]
- [[sources/kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6|Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better]]
