---
title: Ollama
type: tool
created: 2026-05-08
updated: 2026-05-08
tags:
  - tools
---

## What problem does this tool solve?

**Run local LLMs** behind a simple pull/run API—used in the article as the successful path on **NVIDIA GB10** for **Gemma 4 31B dense**.

## Properties

- Author: **Ollama v0.20.5** on Dell **GB10** with `ollama pull gemma4:31b`, **SSH tunnel** on port **11434** when Codex runs on another machine (localhost check for `--oss` mode, per author).
- **Apple Silicon issues** (author, **v0.20.3** context): streaming bug routing **tool-call** payloads to the wrong field; **Flash Attention** freeze on prompts **> ~500 tokens** with Gemma 4—led author to abandon Ollama on **Mac** for this workload in favor of **llama.cpp**.

## Author assessments

- On **GB10**, Ollama was the **first reliable stack** vs failed **vLLM** ABI mismatch (PyTorch **2.10** extensions vs **2.11+cu128** for **sm_121**). [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr]]
- Streaming/tool bugs **did not reproduce** on **NVIDIA** the same way as on **Apple Silicon** for the author’s Gemma 4 test. [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr]]

## Sources

- [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr]]
