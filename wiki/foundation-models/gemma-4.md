---
title: Gemma 4
slug: gemma-4
entity_id: model:gemma-4
category: foundation-model
tags:
- developer-focused
- inference-efficient
- long-context-model
- multimodal-model
- open-weight-model
- reasoning-model
- tool-use-capable
first_seen: '2026-04-03'
last_seen: '2026-04-25'
source_count: 4
evidence_count: 58
source_ids:
- i-finally-have-my-dream-local-ai-stack-and-it-runs-on-amd-01kqz00ky4865ndwsss3xegt6m
- i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr
- i-ran-gemma-4-locally-here-s-what-nobody-s-telling-you-01kqfzwx5z81csjrvzvv6xgq9x
- run-gemma-4-e2b-locally-with-ollama-no-cloud-no-limits-01kqz03kb05v3j801whhfw5twr
value_level: high
confidence: 0.9525
synthesis_state: stage1-placeholder
types:
- multimodal-model
- open-weight-model
- reasoning-model
---

# Gemma 4

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Gemma 4 is presented as a family of models with multiple sizes and capabilities, including OCR, speech-to-text, object detection, text-only use, multimodal function calling, reasoning, code completion, and correction. The source highlights the E2B variant as a small local model with a 128K context window and notes that the family includes both base and instruction-tuned versions.

## Benchmark Observations

- The source does not report formal benchmark scores or comparative measurements.
- The only operational quality signal is the author's qualitative observation that the model handled text reasoning, multilingual output, and a basic object-detection task in a local console workflow.
- The source claims 80–110 tokens per second on an RTX 3090 for the 26B A3B variant.
- The source claims up to 260K context for the model.
- The source says the smaller E4B vision variant has mixed reviews on visual tasks.
- The article cites a jump from 6.6 per cent to 86.4 per cent on the tau2-bench function-calling benchmark, which is the main reason the local test was worth running.
- In the article's spot check, Gemma 4 on the GB10 produced functional code with five tests passing after three tool calls.
- The Mac setup generated faster tokens but still needed ten tool calls and multiple failed test writes, showing that speed did not equal better task completion.

## Comparative Observations

- The source implies the smaller E2B variant is suitable for local use, while larger Gemma 4 variants may achieve better object-detection accuracy.
- Compared with cloud-only models, this setup emphasizes local control and zero per-call inference cost after installation.
- The article positions Gemma 4 as shifting local running from degraded quality or expensive workstations toward consumer-hardware feasibility.
- It implies the model offers a better local performance-to-hardware tradeoff than the older local-inference baseline, though no direct side-by-side benchmark is provided.
- The article contrasts Gemma 4 with previous Gemma generations that scored 6.6 per cent on tool calling, framing the improvement as the key threshold.
- The cloud baseline GPT-5.4 was faster and cleaner on the same coding task, so Gemma 4 was viable locally but not superior in this spot check.
- The GB10's dense 31B variant was slower than the Mac's 26B MoE variant, yet it produced better end-to-end coding results in this task.
- The source says it is the author's preferred local general-purpose model over Qwen 3.5 for most tasks.
- It is described as good enough that the author rarely needs to reach for a cloud model for coding-adjacent work in Claude Code or OpenCode.

## Core Capabilities

- It supports OCR, speech-to-text, and object detection in addition to text-only prompting.
- It supports multimodal function calling, reasoning, code completion, and correction.
- It includes both base and instruction-tuned versions across multiple sizes.
- The E2B variant is described as having a 128K context window, which makes it useful for longer prompts or larger working sets.
- The 26B A3B variant is described as running comfortably on an RTX 3090 with strong throughput and very large context windows.
- The model is presented as capable of local, on-device inference without an API call, which matters for privacy and offline operation.
- The source suggests the model can support agentic workflows, but only after careful configuration and backend validation.
- It can emit tool calls reliably enough to work inside a local coding-agent loop in the described setup.
- It can run in a sparse mixture-of-experts configuration that the author measures as materially faster on the Mac.
- It can support local inference on both Apple Silicon and NVIDIA Blackwell when paired with the right serving stack.
- It supports a dual-variant workflow, with a faster non-thinking version for quick tasks and a thinking coder variant for code and harder reasoning.
- Its MoE structure makes it practical to host a large total-parameter model on memory-rich local hardware without paying the full compute cost per token.
- It serves as a general-purpose local model for day-to-day work in a local AI stack.

## Maturity signals

The model is described as released one day before the article date, so this is early evidence rather than mature field reporting. Still, the source says the family already spans multiple sizes and supports both base and it versions, which suggests a serious product line rather than a one-off demo.

## Pricing / inference implications

The article claims zero inference cost after local setup, which is operationally meaningful for development and low-volume use. It does not establish total cost of ownership because hardware, installation, maintenance, and model download costs are not quantified.

## Provider

Google

## Related Models

- Gemma 4 E2B
- Gemma 4 E4B
- Gemma 4 26B
- Gemma 4 31B
- Llama 4
- Qwen 3.5
- GPT-5.4
- Qwen 3 Embedding:0.6B

## Service automation implications

Gemma 4 could support local prototypes for customer-facing assistants that need image understanding, multilingual replies, or structured extraction. The source does not show a production support deployment, so any service-automation use should be treated as experimental as of 2026-04-03.

## Weaknesses / limitations

The article does not provide quantitative accuracy, latency, memory, or throughput data. It also shows that object-detection boxes may not align perfectly with the original image, so outputs can require post-processing. The visible reasoning trace is not validated as a faithful explanation, only as surfaced intermediate text.

## Evidence / supporting sources

### I Finally Have My Dream Local AI Stack (and it runs on AMD) (2026-04-25)

- The source says it is the author's preferred local general-purpose model over Qwen 3.5 for most tasks. (`8c028f59aac0` · neutral · comparative_observations[0]; [[sources/i-finally-have-my-dream-local-ai-stack-and-it-runs-on-amd-01kqz00ky4865ndwsss3xegt6m|I Finally Have My Dream Local AI Stack (and it runs on AMD)]])
- It is described as good enough that the author rarely needs to reach for a cloud model for coding-adjacent work in Claude Code or OpenCode. (`7c7f9bcff174` · neutral · comparative_observations[1]; [[sources/i-finally-have-my-dream-local-ai-stack-and-it-runs-on-amd-01kqz00ky4865ndwsss3xegt6m|I Finally Have My Dream Local AI Stack (and it runs on AMD)]])
- Adopting this kind of model changes the local stack design because it encourages MoE selection for memory-rich, compute-limited hardware. It also supports a split between fast-answer and thinking/coder variants, which can reduce unnecessary cost or latency escalation for routine prompts. In a local-serving setup, it appears to be practical enough to anchor default local inference for many daily tasks. (`661a1fc2eea7` · neutral · deployment_implications; [[sources/i-finally-have-my-dream-local-ai-stack-and-it-runs-on-amd-01kqz00ky4865ndwsss3xegt6m|I Finally Have My Dream Local AI Stack (and it runs on AMD)]])
- The source says AMD shipped day-zero support for this model through Lemonade, which is a strong sign that it is operationally relevant in at least one current local-inference ecosystem. The model is treated as a stable daily driver rather than a novelty demo. Evidence quality is still a single-user deployment report, not a benchmark suite. (`2ffbaea21c51` · neutral · maturity_signals; [[sources/i-finally-have-my-dream-local-ai-stack-and-it-runs-on-amd-01kqz00ky4865ndwsss3xegt6m|I Finally Have My Dream Local AI Stack (and it runs on AMD)]])
- - The source identifies Gemma 4:26B-A4B as the primary local LLM.
- It is described as a mixture-of-experts model with 26 billion total parameters but only 4 billion active per token, which makes it attractive when memory is plentiful but compute is limited.
- The author uses two variants: a non-thinking version for quick tasks and a thinking coder-optimized variant for code and complex reasoning.
- The practical takeaway is that it can serve as a general-purpose local workhorse when the machine has enough unified memory to host a larger model while still keeping runtime costs manageable. (`5384e6973cb4` · neutral · operational_profile; [[sources/i-finally-have-my-dream-local-ai-stack-and-it-runs-on-amd-01kqz00ky4865ndwsss3xegt6m|I Finally Have My Dream Local AI Stack (and it runs on AMD)]])
- The article implies that a large MoE model can be economical locally if the hardware has enough unified memory, because the active compute load stays closer to a smaller model. The tradeoff is that hardware spend shifts upfront, while cloud token spend drops for routine use. No exact dollar figures or throughput numbers are given. (`3ec02916dff9` · neutral · pricing_inference_implications; [[sources/i-finally-have-my-dream-local-ai-stack-and-it-runs-on-amd-01kqz00ky4865ndwsss3xegt6m|I Finally Have My Dream Local AI Stack (and it runs on AMD)]])
- For service automation, a model like this can cover a large share of routine conversational and coding-adjacent work locally, reducing cloud calls for everyday tasks. The author suggests that a thinking variant is useful when complexity rises, which fits agent flows that need a cheap default path plus escalation for harder turns. (`c3762d6015cf` · neutral · service_automation_implications; [[sources/i-finally-have-my-dream-local-ai-stack-and-it-runs-on-amd-01kqz00ky4865ndwsss3xegt6m|I Finally Have My Dream Local AI Stack (and it runs on AMD)]])
- It supports a dual-variant workflow, with a faster non-thinking version for quick tasks and a thinking coder variant for code and harder reasoning. (`c2aa5c1f160e` · supporting · core_capabilities[0]; [[sources/i-finally-have-my-dream-local-ai-stack-and-it-runs-on-amd-01kqz00ky4865ndwsss3xegt6m|I Finally Have My Dream Local AI Stack (and it runs on AMD)]])
- Its MoE structure makes it practical to host a large total-parameter model on memory-rich local hardware without paying the full compute cost per token. (`54a1018f78b7` · supporting · core_capabilities[1]; [[sources/i-finally-have-my-dream-local-ai-stack-and-it-runs-on-amd-01kqz00ky4865ndwsss3xegt6m|I Finally Have My Dream Local AI Stack (and it runs on AMD)]])
- It serves as a general-purpose local model for day-to-day work in a local AI stack. (`a914c27b4a5e` · supporting · core_capabilities[2]; [[sources/i-finally-have-my-dream-local-ai-stack-and-it-runs-on-amd-01kqz00ky4865ndwsss3xegt6m|I Finally Have My Dream Local AI Stack (and it runs on AMD)]])
- "Gemma 4:26B-A4B is my primary LLM. This is a mixture-of-experts model with 26 billion total parameters but only 4 billion active per token." (`ceab15b1f1e9` · supporting · supporting_snippet; [[sources/i-finally-have-my-dream-local-ai-stack-and-it-runs-on-amd-01kqz00ky4865ndwsss3xegt6m|I Finally Have My Dream Local AI Stack (and it runs on AMD)]])
- The source implicitly shows the main limitation: MoE structure reduces active compute per token but does not make the model fast on weak hardware. It is not presented with benchmark data, so claims about quality and speed remain user-specific. The article also notes that some image tasks still favor cloud models, which suggests the local stack is not uniformly better across modalities. (`9542237253ae` · uncertainty · weaknesses_limitations; [[sources/i-finally-have-my-dream-local-ai-stack-and-it-runs-on-amd-01kqz00ky4865ndwsss3xegt6m|I Finally Have My Dream Local AI Stack (and it runs on AMD)]])

### I ran Gemma 4 as a local model in Codex CLI (2026-04-13)

- The article contrasts Gemma 4 with previous Gemma generations that scored 6.6 per cent on tool calling, framing the improvement as the key threshold. (`b3e6b492a15c` · neutral · comparative_observations[0]; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- The cloud baseline GPT-5.4 was faster and cleaner on the same coding task, so Gemma 4 was viable locally but not superior in this spot check. (`9a11b5d71b40` · neutral · comparative_observations[1]; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- The GB10's dense 31B variant was slower than the Mac's 26B MoE variant, yet it produced better end-to-end coding results in this task. (`3d3466cf179f` · neutral · comparative_observations[2]; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- Gemma 4 makes local agentic coding more plausible because it can participate in a read-write-test loop instead of only generating text. That lowers the barrier to privacy-sensitive or cost-sensitive coding sessions, but it also raises the importance of provider compatibility, prompt size limits, and tool-call formatting. For teams building coding agents, the model choice is only one part of the stack; the serving layer can decide whether the workflow works at all. (`7fa5de115bc0` · neutral · deployment_implications; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- The article treats Gemma 4 as a meaningful step forward from prior Gemma generations because the tool-calling benchmark moved from failure to practical usability. It appears mature enough to be tried in real workflows, but still version- and stack-dependent. The source also notes that benchmark and setup details matter enough to pin versions and control quantization carefully. (`beebc90ccc7c` · neutral · maturity_signals; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- Gemma 4 is presented as a local model family that became viable for tool-using coding workflows once its function calling improved enough to work inside Codex CLI. The article frames it as a practical local alternative for agentic coding, though not a universal replacement for cloud models.

- Its tool calling crossed a usability threshold: the article contrasts earlier Gemma generations with Gemma 4's much stronger function-calling benchmark result.
- It can run locally on both a 24 GB MacBook Pro and a 128 GB NVIDIA Blackwell machine, which makes it relevant for self-hosted coding agents.
- It supports local agent workflows that read files, write patches, and run tests, so it is not just a chat model in this use case. (`28554484bc3f` · neutral · operational_profile; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- The local setup avoids per-token API charges, which matters for heavy Codex CLI use. The article does not quantify local hardware costs, so the economics are only directional: the model can reduce API spend, but it shifts cost into machine investment and setup time. For high-volume use, the practical question becomes whether the saved API spend outweighs the operational friction. (`3d0f60edef6d` · neutral · pricing_inference_implications; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- The source does not discuss customer support or voice automation directly. The durable implication is indirect: any service workflow that depends on reliable tool calling can benefit from a model that can execute structured actions locally, but this article only demonstrates that for coding tasks. (`9d32739a0c61` · neutral · service_automation_implications; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- The article cites a jump from 6.6 per cent to 86.4 per cent on the tau2-bench function-calling benchmark, which is the main reason the local test was worth running. (`2731c4629a57` · supporting · benchmark_observations[0]; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- In the article's spot check, Gemma 4 on the GB10 produced functional code with five tests passing after three tool calls. (`40f1d7aec1cf` · supporting · benchmark_observations[1]; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- The Mac setup generated faster tokens but still needed ten tool calls and multiple failed test writes, showing that speed did not equal better task completion. (`1c542403fb83` · supporting · benchmark_observations[2]; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- It can emit tool calls reliably enough to work inside a local coding-agent loop in the described setup. (`4cccf0210e62` · supporting · core_capabilities[0]; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- It can run in a sparse mixture-of-experts configuration that the author measures as materially faster on the Mac. (`51bb65c365af` · supporting · core_capabilities[1]; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- It can support local inference on both Apple Silicon and NVIDIA Blackwell when paired with the right serving stack. (`e5f17addecc9` · supporting · core_capabilities[2]; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- "Gemma 4 31B scores 86.4 per cent on the same benchmark. That is what made this test worth running." (`abdaccc87f20` · supporting · supporting_snippet; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- - The article shows that local deployment can be fragile: Apple Silicon required specific serving choices, and some combinations failed because of streaming bugs or prompt-length freezes.
- The Mac setup produced more retries, broken tool calls, and dead code than the GB10 setup, so local viability still depends on serving stack and quantization choices.
- The source does not show broader task coverage beyond one coding prompt, so generalization remains open. (`afad47eacfe3` · uncertainty · weaknesses_limitations; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])

### I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You. (2026-04-09)

- The article positions Gemma 4 as shifting local running from degraded quality or expensive workstations toward consumer-hardware feasibility. (`737edc11d991` · neutral · comparative_observations[0]; [[sources/i-ran-gemma-4-locally-here-s-what-nobody-s-telling-you-01kqfzwx5z81csjrvzvv6xgq9x|I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You.]])
- It implies the model offers a better local performance-to-hardware tradeoff than the older local-inference baseline, though no direct side-by-side benchmark is provided. (`380283ae4fbf` · neutral · comparative_observations[1]; [[sources/i-ran-gemma-4-locally-here-s-what-nobody-s-telling-you-01kqfzwx5z81csjrvzvv6xgq9x|I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You.]])
- Adopting this model changes the deployment conversation from API-only usage to on-device or self-hosted inference. It appears feasible on an RTX 3090 with the right quantization, and the source suggests 16GB VRAM setups may still work with CPU offload for MoE layers. For production planning, the relevant implication is that local deployment may be realistic for privacy-sensitive, latency-sensitive, or cost-constrained workflows, but only if the runtime backend and quantization are validated carefully. (`193542cfb697` · neutral · deployment_implications; [[sources/i-ran-gemma-4-locally-here-s-what-nobody-s-telling-you-01kqfzwx5z81csjrvzvv6xgq9x|I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You.]])
- The source frames Gemma 4 as a meaningful release in the local-model ecosystem, especially because of the size-to-hardware ratio and the speed of community experimentation. It also notes direct collaboration on llama.cpp integration, which is a positive ecosystem signal. Evidence quality is still practitioner-led and anecdotal rather than controlled benchmarking. (`d246869d7ad9` · neutral · maturity_signals; [[sources/i-ran-gemma-4-locally-here-s-what-nobody-s-telling-you-01kqfzwx5z81csjrvzvv6xgq9x|I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You.]])
- - An open-weight Mixture-of-Experts model that can deliver strong local-inference characteristics when paired with the right quantization and runtime settings.
- The 26B A3B variant is described as practical on consumer hardware, with enough throughput and context to be useful for real tasks rather than toy demos.
- The smaller E4B vision variant is treated more cautiously; text reasoning is the safer use case in this source.
- The main practical message is that the model’s perceived quality depends heavily on serving configuration, not just the base checkpoint. (`88378b10ca91` · neutral · operational_profile; [[sources/i-ran-gemma-4-locally-here-s-what-nobody-s-telling-you-01kqfzwx5z81csjrvzvv6xgq9x|I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You.]])
- The source argues that local inference may avoid API bills and cloud dependence, and it gives a concrete consumer-hardware example: an RTX 3090 bought secondhand for under $600. That makes the economics attractive for development and some deployment scenarios, but the article does not quantify total cost of ownership or energy costs. (`f661bdc892bf` · neutral · pricing_inference_implications; [[sources/i-ran-gemma-4-locally-here-s-what-nobody-s-telling-you-01kqfzwx5z81csjrvzvv6xgq9x|I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You.]])
- The model could support local assistants for privacy-sensitive service workflows, but the source gives no evidence that it is reliable enough for unattended customer support deployment. The strongest implication is for offline or on-device assistant prototypes where data locality matters more than guaranteed answer quality. (`4ccbbd47889e` · neutral · service_automation_implications; [[sources/i-ran-gemma-4-locally-here-s-what-nobody-s-telling-you-01kqfzwx5z81csjrvzvv6xgq9x|I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You.]])
- The source claims 80–110 tokens per second on an RTX 3090 for the 26B A3B variant. (`bcd496d806d3` · supporting · benchmark_observations[0]; [[sources/i-ran-gemma-4-locally-here-s-what-nobody-s-telling-you-01kqfzwx5z81csjrvzvv6xgq9x|I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You.]])
- The source claims up to 260K context for the model. (`c2271be85803` · supporting · benchmark_observations[1]; [[sources/i-ran-gemma-4-locally-here-s-what-nobody-s-telling-you-01kqfzwx5z81csjrvzvv6xgq9x|I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You.]])
- The source says the smaller E4B vision variant has mixed reviews on visual tasks. (`60e123054c1c` · supporting · benchmark_observations[2]; [[sources/i-ran-gemma-4-locally-here-s-what-nobody-s-telling-you-01kqfzwx5z81csjrvzvv6xgq9x|I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You.]])
- The 26B A3B variant is described as running comfortably on an RTX 3090 with strong throughput and very large context windows. (`593dd2927009` · supporting · core_capabilities[0]; [[sources/i-ran-gemma-4-locally-here-s-what-nobody-s-telling-you-01kqfzwx5z81csjrvzvv6xgq9x|I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You.]])
- The model is presented as capable of local, on-device inference without an API call, which matters for privacy and offline operation. (`ed77e0672b44` · supporting · core_capabilities[1]; [[sources/i-ran-gemma-4-locally-here-s-what-nobody-s-telling-you-01kqfzwx5z81csjrvzvv6xgq9x|I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You.]])
- The source suggests the model can support agentic workflows, but only after careful configuration and backend validation. (`9f3b0b3dc480` · supporting · core_capabilities[2]; [[sources/i-ran-gemma-4-locally-here-s-what-nobody-s-telling-you-01kqfzwx5z81csjrvzvv6xgq9x|I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You.]])
- Gemma 4 is a
M
ixture-
O
f-
E
xperts model. That’s not marketing language, it’s the reason this thing fits on hardware you already own.

In practice, that means Gemma 4’s 26B A3B variant runs comfortably on an RTX 3090 — a GPU you can buy secondhand for under $600. At 80–110 tokens per second. With up to 260K context. (`09edc26db8bd` · supporting · supporting_snippet; [[sources/i-ran-gemma-4-locally-here-s-what-nobody-s-telling-you-01kqfzwx5z81csjrvzvv6xgq9x|I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You.]])
- The source reports tool-calling loops, thinking-tag issues, and llama.cpp build-specific bugs that can distort generations. It also says the vision capabilities of the smaller E4B variant receive mixed reviews, and that Gemma 4 may over-rely on internal knowledge in RAG setups. These are meaningful limitations for agentic and retrieval-heavy use cases. (`9ca491fad1d3` · uncertainty · weaknesses_limitations; [[sources/i-ran-gemma-4-locally-here-s-what-nobody-s-telling-you-01kqfzwx5z81csjrvzvv6xgq9x|I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You.]])

### Run Gemma 4:E2B Locally with Ollama: No Cloud, No Limits (2026-04-03)

- The source implies the smaller E2B variant is suitable for local use, while larger Gemma 4 variants may achieve better object-detection accuracy. (`f9c7735d42ba` · neutral · comparative_observations[0]; [[sources/run-gemma-4-e2b-locally-with-ollama-no-cloud-no-limits-01kqz03kb05v3j801whhfw5twr|Run Gemma 4:E2B Locally with Ollama: No Cloud, No Limits]])
- Compared with cloud-only models, this setup emphasizes local control and zero per-call inference cost after installation. (`e25d4dfbf2b9` · neutral · comparative_observations[1]; [[sources/run-gemma-4-e2b-locally-with-ollama-no-cloud-no-limits-01kqz03kb05v3j801whhfw5twr|Run Gemma 4:E2B Locally with Ollama: No Cloud, No Limits]])
- The source supports using Gemma 4 locally through Ollama, which means teams can test multimodal and reasoning workflows on their own hardware before committing to cloud inference. The small E2B variant is specifically positioned as practical for local experimentation, but the article also implies that output alignment and preprocessing need attention when using it for object detection. (`f4f048caa483` · neutral · deployment_implications; [[sources/run-gemma-4-e2b-locally-with-ollama-no-cloud-no-limits-01kqz03kb05v3j801whhfw5twr|Run Gemma 4:E2B Locally with Ollama: No Cloud, No Limits]])
- The model is described as released one day before the article date, so this is early evidence rather than mature field reporting. Still, the source says the family already spans multiple sizes and supports both base and it versions, which suggests a serious product line rather than a one-off demo. (`2e01c776408e` · neutral · maturity_signals; [[sources/run-gemma-4-e2b-locally-with-ollama-no-cloud-no-limits-01kqz03kb05v3j801whhfw5twr|Run Gemma 4:E2B Locally with Ollama: No Cloud, No Limits]])
- Gemma 4 is presented as a family of models with multiple sizes and capabilities, including OCR, speech-to-text, object detection, text-only use, multimodal function calling, reasoning, code completion, and correction. The source highlights the E2B variant as a small local model with a 128K context window and notes that the family includes both base and instruction-tuned versions. (`943979213b3d` · neutral · operational_profile; [[sources/run-gemma-4-e2b-locally-with-ollama-no-cloud-no-limits-01kqz03kb05v3j801whhfw5twr|Run Gemma 4:E2B Locally with Ollama: No Cloud, No Limits]])
- The article claims zero inference cost after local setup, which is operationally meaningful for development and low-volume use. It does not establish total cost of ownership because hardware, installation, maintenance, and model download costs are not quantified. (`f26cf0efc8a5` · neutral · pricing_inference_implications; [[sources/run-gemma-4-e2b-locally-with-ollama-no-cloud-no-limits-01kqz03kb05v3j801whhfw5twr|Run Gemma 4:E2B Locally with Ollama: No Cloud, No Limits]])
- Gemma 4 could support local prototypes for customer-facing assistants that need image understanding, multilingual replies, or structured extraction. The source does not show a production support deployment, so any service-automation use should be treated as experimental as of 2026-04-03. (`a07fe308e0c2` · neutral · service_automation_implications; [[sources/run-gemma-4-e2b-locally-with-ollama-no-cloud-no-limits-01kqz03kb05v3j801whhfw5twr|Run Gemma 4:E2B Locally with Ollama: No Cloud, No Limits]])
- The source does not report formal benchmark scores or comparative measurements. (`36bf4be7e8fd` · supporting · benchmark_observations[0]; [[sources/run-gemma-4-e2b-locally-with-ollama-no-cloud-no-limits-01kqz03kb05v3j801whhfw5twr|Run Gemma 4:E2B Locally with Ollama: No Cloud, No Limits]])
- The only operational quality signal is the author's qualitative observation that the model handled text reasoning, multilingual output, and a basic object-detection task in a local console workflow. (`c5766bbcadba` · supporting · benchmark_observations[1]; [[sources/run-gemma-4-e2b-locally-with-ollama-no-cloud-no-limits-01kqz03kb05v3j801whhfw5twr|Run Gemma 4:E2B Locally with Ollama: No Cloud, No Limits]])
- It supports OCR, speech-to-text, and object detection in addition to text-only prompting. (`c37c5ed63922` · supporting · core_capabilities[0]; [[sources/run-gemma-4-e2b-locally-with-ollama-no-cloud-no-limits-01kqz03kb05v3j801whhfw5twr|Run Gemma 4:E2B Locally with Ollama: No Cloud, No Limits]])
- It supports multimodal function calling, reasoning, code completion, and correction. (`80a8b2431c5b` · supporting · core_capabilities[1]; [[sources/run-gemma-4-e2b-locally-with-ollama-no-cloud-no-limits-01kqz03kb05v3j801whhfw5twr|Run Gemma 4:E2B Locally with Ollama: No Cloud, No Limits]])
- It includes both base and instruction-tuned versions across multiple sizes. (`8ae71b84f101` · supporting · core_capabilities[2]; [[sources/run-gemma-4-e2b-locally-with-ollama-no-cloud-no-limits-01kqz03kb05v3j801whhfw5twr|Run Gemma 4:E2B Locally with Ollama: No Cloud, No Limits]])
- The E2B variant is described as having a 128K context window, which makes it useful for longer prompts or larger working sets. (`b059932f1bc5` · supporting · core_capabilities[3]; [[sources/run-gemma-4-e2b-locally-with-ollama-no-cloud-no-limits-01kqz03kb05v3j801whhfw5twr|Run Gemma 4:E2B Locally with Ollama: No Cloud, No Limits]])
- "Gemma 4 E2B — has a context window of 128K. Parameter size is 2.3B effective, 5.1B with embeddings." (`74179900065e` · supporting · supporting_snippet; [[sources/run-gemma-4-e2b-locally-with-ollama-no-cloud-no-limits-01kqz03kb05v3j801whhfw5twr|Run Gemma 4:E2B Locally with Ollama: No Cloud, No Limits]])
- The article does not provide quantitative accuracy, latency, memory, or throughput data. It also shows that object-detection boxes may not align perfectly with the original image, so outputs can require post-processing. The visible reasoning trace is not validated as a faithful explanation, only as surfaced intermediate text. (`33d8f87491e7` · uncertainty · weaknesses_limitations; [[sources/run-gemma-4-e2b-locally-with-ollama-no-cloud-no-limits-01kqz03kb05v3j801whhfw5twr|Run Gemma 4:E2B Locally with Ollama: No Cloud, No Limits]])

## Contradictions / tensions

- The article does not provide quantitative accuracy, latency, memory, or throughput data. It also shows that object-detection boxes may not align perfectly with the original image, so outputs can require post-processing. The visible reasoning trace is not validated as a faithful explanation, only as surfaced intermediate text. (uncertainty; [[sources/run-gemma-4-e2b-locally-with-ollama-no-cloud-no-limits-01kqz03kb05v3j801whhfw5twr|Run Gemma 4:E2B Locally with Ollama: No Cloud, No Limits]])
- The source reports tool-calling loops, thinking-tag issues, and llama.cpp build-specific bugs that can distort generations. It also says the vision capabilities of the smaller E4B variant receive mixed reviews, and that Gemma 4 may over-rely on internal knowledge in RAG setups. These are meaningful limitations for agentic and retrieval-heavy use cases. (uncertainty; [[sources/i-ran-gemma-4-locally-here-s-what-nobody-s-telling-you-01kqfzwx5z81csjrvzvv6xgq9x|I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You.]])
- - The article shows that local deployment can be fragile: Apple Silicon required specific serving choices, and some combinations failed because of streaming bugs or prompt-length freezes.
- The Mac setup produced more retries, broken tool calls, and dead code than the GB10 setup, so local viability still depends on serving stack and quantization choices.
- The source does not show broader task coverage beyond one coding prompt, so generalization remains open. (uncertainty; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- The source implicitly shows the main limitation: MoE structure reduces active compute per token but does not make the model fast on weak hardware. It is not presented with benchmark data, so claims about quality and speed remain user-specific. The article also notes that some image tasks still favor cloud models, which suggests the local stack is not uniformly better across modalities. (uncertainty; [[sources/i-finally-have-my-dream-local-ai-stack-and-it-runs-on-amd-01kqz00ky4865ndwsss3xegt6m|I Finally Have My Dream Local AI Stack (and it runs on AMD)]])

## Related pages

- GPT-5.4
- Gemma 4 26B
- Gemma 4 31B
- Gemma 4 E2B
- Gemma 4 E4B
- Llama 4
- Qwen 3 Embedding:0.6B
- Qwen 3.5

## Sources

- [[sources/i-finally-have-my-dream-local-ai-stack-and-it-runs-on-amd-01kqz00ky4865ndwsss3xegt6m|I Finally Have My Dream Local AI Stack (and it runs on AMD)]]
- [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]]
- [[sources/i-ran-gemma-4-locally-here-s-what-nobody-s-telling-you-01kqfzwx5z81csjrvzvv6xgq9x|I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You.]]
- [[sources/run-gemma-4-e2b-locally-with-ollama-no-cloud-no-limits-01kqz03kb05v3j801whhfw5twr|Run Gemma 4:E2B Locally with Ollama: No Cloud, No Limits]]
