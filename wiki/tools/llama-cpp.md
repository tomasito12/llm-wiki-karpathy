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
synthesis_state: stage1-placeholder
types:
- ai-infrastructure
- model-serving
---

# llama.cpp

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
An open-source model serving and inference stack that can run local models through a lightweight server. In this piece it is used to host Gemma 4 on Apple Silicon and on a CUDA build for the GB10 machine.

## Core Capabilities

- It can host a local Gemma 4 model with direct control over server flags and memory usage.
- It can expose a tool-calling interface compatible with a coding agent when the right template and protocol settings are used.
- It can be configured to run through a direct GGUF path, which avoids unwanted downloads and memory surprises.
- It reads GGUF model files, which keeps it aligned with the broadest local model distribution channel described in the source.
- It supports layer offload between CPU and GPU through n_gpu_layers, which helps on devices with constrained unified memory.
- It can run either as a library or as an HTTP server, which lets teams choose between embedded and service-style integration.

## Integration Ecosystem

- The article says it can be configured as a custom model provider in Codex CLI through `config.toml`.
- It works with GGUF model files and a local server process, which makes it compatible with offline or self-hosted workflows.
- It was installed through Homebrew on macOS in the described setup.
- It uses GGUF files as its main model format.
- It supports Metal on Apple Silicon.
- It can be embedded as a library or exposed as an HTTP server.

## Maturity signals

The piece treats llama.cpp as a practical option rather than an experimental toy, because it became the working path after other servers failed. It also appears mature enough to be pinned, tuned, and integrated into Codex CLI profiles. At the same time, the article makes clear that it still demands hands-on debugging rather than one-click setup.

## Related Tools

- Ollama
- Codex CLI
- MLX
- LM Studio

## Strengths

- It can serve local models with enough control over context length, quantization, and GPU offload to make a 24 GB machine usable for an agentic coding workload.
- It supports the Gemma 4 tool-calling template through the `--jinja` flag, which matters because the agent is only useful if tool calls are emitted in the expected format.
- The article shows it can run as a custom provider inside Codex CLI, so it can plug into an existing coding-agent workflow rather than requiring a separate interface.

## Weaknesses / limitations

- The setup was fragile on Apple Silicon: the article reports a streaming bug in Ollama and a Flash Attention freeze, which is why llama.cpp became the fallback.
- The configuration was easy to break through hidden defaults, such as the `-hf` path downloading an unwanted vision projector and causing out-of-memory failure.
- The source notes that version changes can alter benchmark behavior, so operational results depend heavily on pinning builds and flags.

## Evidence / supporting sources

### Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks (2026-04-20)

- It uses GGUF files as its main model format. (`e932143a080f` · neutral · integration_ecosystem[0]; [[sources/choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj|Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks]])
- It supports Metal on Apple Silicon. (`b8a18eabf9e6` · neutral · integration_ecosystem[1]; [[sources/choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj|Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks]])
- It can be embedded as a library or exposed as an HTTP server. (`c8cdc5025b05` · neutral · integration_ecosystem[2]; [[sources/choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj|Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks]])
- The source describes llama.cpp as the broadest model ecosystem in local inference, which is a strong maturity signal. It is treated as an established engine rather than a niche or experimental product. Its continued relevance in the article comes from flexibility and ecosystem reach, not from a single benchmark peak. (`297dd68856a9` · neutral · maturity_signals; [[sources/choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj|Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks]])
- llama.cpp is the broad compatibility option when teams need maximum control over local inference on Apple Silicon. It is especially relevant when deployment constraints require CPU/GPU layer offload or when a model appears first in GGUF form. For service automation and internal tools, it is a practical fallback when MLX conversions are missing or memory constraints make partial offload necessary. (`527fc4fb3fa0` · neutral · operational_relevance; [[sources/choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj|Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks]])
- llama.cpp is a C/C++ inference engine with a Metal backend for Apple Silicon. It can read GGUF files, offload layers between CPU and GPU, and run either as a library or as an HTTP server. (`627defd263e0` · neutral · short_description; [[sources/choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj|Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks]])
- - Broad model ecosystem support makes it useful when model availability matters more than backend-specific performance.
- Layer offload via n_gpu_layers helps fit models onto customer hardware with limited unified memory.
- It can be used as either a library or an HTTP server, which gives teams flexibility in how deeply they integrate it into product code. (`070b83db4e85` · neutral · strengths; [[sources/choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj|Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks]])
- It reads GGUF model files, which keeps it aligned with the broadest local model distribution channel described in the source. (`b72bc9f3c552` · supporting · core_capabilities[0]; [[sources/choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj|Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks]])
- It supports layer offload between CPU and GPU through n_gpu_layers, which helps on devices with constrained unified memory. (`363fffc61719` · supporting · core_capabilities[1]; [[sources/choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj|Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks]])
- It can run either as a library or as an HTTP server, which lets teams choose between embedded and service-style integration. (`661fa0d704b6` · supporting · core_capabilities[2]; [[sources/choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj|Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks]])
- "llama.cpp is a C/C++ inference engine with a Metal backend for Apple Silicon. It reads GGUF files, supports layer offload between CPU and GPU via n_gpu_layers, and works as a library or as an HTTP server. It has the broadest model ecosystem in local inference." (`2d644bafa021` · supporting · supporting_snippet; [[sources/choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj|Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks]])
- - The source presents it as generally slower than MLX for smaller compute-bound models.
- It lacks the native on-device LoRA/QLoRA fine-tuning path that MLX provides.
- For very large dense models, the article says it converges with MLX because memory bandwidth dominates, so it does not provide a decisive speed advantage there. (`46f5b7c9f0cd` · uncertainty · weaknesses_limitations; [[sources/choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj|Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks]])

### I ran Gemma 4 as a local model in Codex CLI (2026-04-13)

- The article says it can be configured as a custom model provider in Codex CLI through `config.toml`. (`6958037ee38d` · neutral · integration_ecosystem[0]; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- It works with GGUF model files and a local server process, which makes it compatible with offline or self-hosted workflows. (`f0ce73077765` · neutral · integration_ecosystem[1]; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- It was installed through Homebrew on macOS in the described setup. (`a2729e3fa2a7` · neutral · integration_ecosystem[2]; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- The piece treats llama.cpp as a practical option rather than an experimental toy, because it became the working path after other servers failed. It also appears mature enough to be pinned, tuned, and integrated into Codex CLI profiles. At the same time, the article makes clear that it still demands hands-on debugging rather than one-click setup. (`166d79382b36` · neutral · maturity_signals; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- This is relevant wherever teams need local inference with tight control over memory use, quantization, and tool-calling templates. It fits agent workflows when the model must read files, write code, and call tools without sending prompts to a cloud API. The article shows it can be the workable path when other serving options fail on a given machine or tool protocol. (`154cfc699ae7` · neutral · operational_relevance; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- An open-source model serving and inference stack that can run local models through a lightweight server. In this piece it is used to host Gemma 4 on Apple Silicon and on a CUDA build for the GB10 machine. (`05b59da1dafe` · neutral · short_description; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- - It can serve local models with enough control over context length, quantization, and GPU offload to make a 24 GB machine usable for an agentic coding workload.
- It supports the Gemma 4 tool-calling template through the `--jinja` flag, which matters because the agent is only useful if tool calls are emitted in the expected format.
- The article shows it can run as a custom provider inside Codex CLI, so it can plug into an existing coding-agent workflow rather than requiring a separate interface. (`9cbdc65d622b` · neutral · strengths; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- It can host a local Gemma 4 model with direct control over server flags and memory usage. (`5fe0f6cfafdf` · supporting · core_capabilities[0]; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- It can expose a tool-calling interface compatible with a coding agent when the right template and protocol settings are used. (`6e87a4032dcb` · supporting · core_capabilities[1]; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- It can be configured to run through a direct GGUF path, which avoids unwanted downloads and memory surprises. (`1922941eb720` · supporting · core_capabilities[2]; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- "I switched to llama.cpp, installed via Homebrew. The working server command has six load-bearing flags:" (`e0228b4c3909` · supporting · supporting_snippet; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- - The setup was fragile on Apple Silicon: the article reports a streaming bug in Ollama and a Flash Attention freeze, which is why llama.cpp became the fallback.
- The configuration was easy to break through hidden defaults, such as the `-hf` path downloading an unwanted vision projector and causing out-of-memory failure.
- The source notes that version changes can alter benchmark behavior, so operational results depend heavily on pinning builds and flags. (`56c654eb29fb` · uncertainty · weaknesses_limitations; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])

## Contradictions / tensions

- - The setup was fragile on Apple Silicon: the article reports a streaming bug in Ollama and a Flash Attention freeze, which is why llama.cpp became the fallback.
- The configuration was easy to break through hidden defaults, such as the `-hf` path downloading an unwanted vision projector and causing out-of-memory failure.
- The source notes that version changes can alter benchmark behavior, so operational results depend heavily on pinning builds and flags. (uncertainty; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- - The source presents it as generally slower than MLX for smaller compute-bound models.
- It lacks the native on-device LoRA/QLoRA fine-tuning path that MLX provides.
- For very large dense models, the article says it converges with MLX because memory bandwidth dominates, so it does not provide a decisive speed advantage there. (uncertainty; [[sources/choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj|Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks]])

## Related pages

- Codex CLI
- LM Studio
- MLX
- Ollama

## Sources

- [[sources/choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj|Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks]]
- [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]]
