---
title: llama.cpp
slug: llama-cpp
entity_id: tool:llama-cpp
category: tool
tags:
- api-first
- local-first
- open-source
first_seen: '2026-04-13'
last_seen: '2026-04-20'
source_count: 2
evidence_count: 24
source_ids:
- choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj
- i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr
value_level: high
confidence: 0.935
synthesis_state: synthesized
synthesis_stale: false
synthesis_input_hash: 7672c8ab765c35ed
current_input_hash: 7672c8ab765c35ed
synthesis_schema_version: 1
synthesis_prompt_version: 1
last_synthesized_at: '2026-07-09T16:46:24Z'
types:
- ai-infrastructure
- model-serving
---

# llama.cpp

## Executive synthesis

llama.cpp is a mature open-source runtime for local inference when you need control more than convenience. The sources describe it as a C/C++ engine with a Metal backend on Apple Silicon, GGUF support, and the ability to offload layers between CPU and GPU through `n_gpu_layers`. It can be used either as a library or as an HTTP server, which makes it fit both embedded product code and service-style deployment. In practice, it shows up as the workable option when teams need local model serving, offline or self-hosted workflows, or a coding-agent setup that must read files, write code, and emit tool calls without sending prompts to a cloud API. The main caution is that it is not presented as the best choice for pure speed or low-friction setup: the sources say it can be slower than MLX on smaller compute-bound models, lacks MLX’s native on-device LoRA/QLoRA path, and may require careful pinning and debugging because defaults and build choices can change behavior.

## Example in practice

### Local coding-agent runtime with controlled memory use

A team wants a local coding assistant that can work inside Codex CLI without sending prompts to a cloud API. They configure llama.cpp as a custom provider, point it at a GGUF model, and tune the template plus offload settings so the model emits tool calls in the expected format. On a 24 GB machine, they keep memory use under control by adjusting context length, quantization, and GPU offload. In the described setup, this became the fallback when other serving options had streaming or attention issues, and the direct GGUF path avoided surprise downloads and memory blowups.

- Why it helps: It shows why llama.cpp matters in practice: it can turn a local model into a usable agent backend when compatibility, memory control, and tool-call formatting are the real constraints.

- Basis: `source-grounded`

## Context card

- **Use this page when:** Use this page when you need a local LLM runtime that prioritizes compatibility, control, and offline integration over peak benchmark performance.
- **Best for questions about:** Running local models with tight control over memory and offload, Using GGUF models in an on-device or self-hosted workflow, Integrating a local runtime as either a library or an HTTP server, Making coding-agent or tool-calling setups work offline, Choosing a broad-compatibility fallback runtime on Apple Silicon
- **Not enough for:** Choosing the fastest runtime in every case, Native on-device fine-tuning workflows such as LoRA/QLoRA, Deep comparative performance claims across all model sizes and hardware, One-click setup or low-friction operationalization without debugging
- **Strongest sources:** Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks, I ran Gemma 4 as a local model in Codex CLI
- **Related tags:** api-first, local-first, open-source

## What to remember

- Open-source local inference runtime with GGUF support and a broad model ecosystem.
- Can run as either a library or an HTTP server, so it fits embedded and service-style deployments.
- Supports CPU/GPU layer offload with `n_gpu_layers`, which is useful on memory-limited hardware.
- Useful for local agents and offline workflows when tool calls and file/code access must stay on-device.
- Often chosen as a practical fallback when other runtimes or servers are less compatible.
- Strong on flexibility and control; weaker as a default choice if your main goal is simplest setup or peak small-model speed.

## Consensus

- llama.cpp is an open-source local inference stack for running models through a lightweight server or as an embeddable library.
- It reads GGUF model files and supports layer offload between CPU and GPU with `n_gpu_layers`, which helps when memory is tight.
- On Apple Silicon it supports a Metal backend and is positioned as a broad-compatibility option rather than a niche runtime.
- It is useful for agentic or offline workflows where teams need local control over memory use, quantization, and tool-calling templates.
- The sources treat it as a practical, mature tool that is often used as a fallback when other serving options fail or are less compatible.

## Tensions / open questions

- The sources frame llama.cpp as broadly compatible and practical, but not as the fastest option for smaller compute-bound models.
- It lacks the native on-device LoRA/QLoRA fine-tuning path that MLX provides, so it is not the whole answer for local model adaptation.
- The hands-on article shows it can be the working fallback after other servers fail, but also highlights that it still requires debugging and careful configuration.
- Operational behavior depends on flags, templates, and version pinning, so a setup that works in one environment may not transfer cleanly.

## Evidence quality

- Evidence is fairly strong for core capabilities and integration patterns: two reviewed sources agree on GGUF support, offload, library/server modes, and local deployment use.
- Evidence is strong for practical usefulness in agent workflows, but that comes mainly from one hands-on setup report rather than broad comparative testing.
- Evidence is weaker for performance judgments, because the sources explicitly frame tradeoffs as context-dependent and note cases where speed converges or varies with version/build choices.
- Operational details appear time-sensitive: build flags, templates, and hidden defaults can materially change behavior, so results may not transfer cleanly across setups.

## Practical takeaway

Choose llama.cpp when your priority is broad model compatibility, local control, and flexible integration on constrained hardware. Do not choose it expecting the simplest setup or the fastest small-model runtime; expect to tune flags, templates, and build choices.

## Evidence index

- Sources: 2
- Evidence items: 24
- Current input hash: `7672c8ab765c35ed`
- Cached input hash: `7672c8ab765c35ed`
- Last synthesized: 2026-07-09T16:46:24Z
- Synthesis status: `fresh`

## Related pages

- [[tools/ollama|Ollama]]
- [[tools/mlx|MLX]]

## Sources

- [[sources/choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj|Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks]]
- [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]]
