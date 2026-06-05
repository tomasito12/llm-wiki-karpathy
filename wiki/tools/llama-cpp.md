---
title: llama.cpp
slug: llama-cpp
entity_id: tool:llama-cpp
category: tool
first_seen: '2026-04-13'
last_seen: '2026-04-13'
source_count: 1
evidence_count: 12
source_ids:
- i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr
value_level: high
confidence: 0.91
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

## Integration Ecosystem

- The article says it can be configured as a custom model provider in Codex CLI through `config.toml`.
- It works with GGUF model files and a local server process, which makes it compatible with offline or self-hosted workflows.
- It was installed through Homebrew on macOS in the described setup.

## Maturity signals

The piece treats llama.cpp as a practical option rather than an experimental toy, because it became the working path after other servers failed. It also appears mature enough to be pinned, tuned, and integrated into Codex CLI profiles. At the same time, the article makes clear that it still demands hands-on debugging rather than one-click setup.

## Related Tools

- Ollama
- Codex CLI

## Strengths

- It can serve local models with enough control over context length, quantization, and GPU offload to make a 24 GB machine usable for an agentic coding workload.
- It supports the Gemma 4 tool-calling template through the `--jinja` flag, which matters because the agent is only useful if tool calls are emitted in the expected format.
- The article shows it can run as a custom provider inside Codex CLI, so it can plug into an existing coding-agent workflow rather than requiring a separate interface.

## Weaknesses / limitations

- The setup was fragile on Apple Silicon: the article reports a streaming bug in Ollama and a Flash Attention freeze, which is why llama.cpp became the fallback.
- The configuration was easy to break through hidden defaults, such as the `-hf` path downloading an unwanted vision projector and causing out-of-memory failure.
- The source notes that version changes can alter benchmark behavior, so operational results depend heavily on pinning builds and flags.

## Evidence / supporting sources

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

## Related pages

- Codex CLI
- Ollama

## Sources

- [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]]
