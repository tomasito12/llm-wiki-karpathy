---
title: llama.cpp
type: tool
created: 2026-05-08
updated: 2026-05-08
tags:
  - tools
---

## What problem does this tool solve?

**Local inference server** for GGUF models—used on the author’s **24 GB M4 Pro MacBook Pro** to run **Gemma 4 26B MoE** when **Ollama** was unusable for Codex-scale prompts.

## Properties

- Author command sketch (abbreviated in prose): `llama-server` with **direct `-m` GGUF path** (avoid **`-hf`** path that pulled an extra **vision projector** and OOM’d on 24 GB), **`--jinja`** for Gemma 4 tool templates, **`-c 32768`** context (**Codex** system prompt **~27k** tokens per author), **`-np 1`**, **KV cache** quant **`-ctk q8_0 -ctv q8_0`**, **`-ngl 99`**, model **Q4_K_M** variant.
- **llama-bench** cited for **tok/s** comparisons between Mac (MoE) vs GB10 (dense); author warns **version pinning** after reported large **speed regressions** across builds.
- **CUDA** build attempted on GB10; **Codex** `responses` wire sent **non-function tool types** that **llama.cpp** rejected—author pivoted to Ollama on that machine.

## Author assessments

- Treats **llama.cpp** as the **workable** Gemma 4 path on **Apple Silicon** for this test after Ollama failures. [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr]]
- Emphasizes **memory math** (MoE activates fewer params per token → higher **tok/s** but, in this run, worse **agent** reliability under **Q4** on 24 GB). [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr]]

## Sources

- [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr]]
