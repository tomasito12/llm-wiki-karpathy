---
title: "I ran Gemma 4 as a local model in Codex CLI"
type: source
author: Daniel Vaughan
publication: Medium
created: 2026-05-08
updated: 2026-05-08
sources:
  - raw/readwise/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr.md
  - raw/readwise/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr.html
tags:
  - tools
---

Daniel Vaughan (Google Cloud on Medium) documents a **same-day practical test**: running **Gemma 4** locally as a custom provider for **Codex CLI**, comparing a **24 GB M4 Pro MacBook Pro** (26B MoE **Q4_K_M** via **llama.cpp**) with a **Dell Pro Max GB10** (128 GB, **31B dense** via **Ollama** 0.20.5), plus a **cloud GPT-5.4** baseline—focusing on **tool-calling reliability** and end-to-end task success, not just token speed.

## Apps and platforms covered

- [[tools/coding-agents/codex-cli]]
- [[tools/local-llm-runtimes/ollama]]
- [[tools/local-llm-runtimes/llama-cpp]]

## Foundation models covered

- [[foundation-models/gemma-4]]

## Why it matters

The piece is **one author’s controlled anecdote** (single task, dated stack versions), but it surfaces **real integration pitfalls** (Ollama streaming/tool-field bugs on Apple Silicon, llama.cpp **web_search** tool rejection, memory/KV-cache flags, `stream_idle_timeout_ms`) that anyone wiring **local models** into **agent harnesses** may hit.

## Implications for service-call automation

Any internal “local CODEX-like” CLI that relies on **OpenAI-compatible tool schemas** needs the same class of fixes: **disable unsupported tool types**, **tune idle timeouts** for long tool cycles, and **pin** server builds—relevant for regulated or insecure-environment automation prototypes.

## Context and Limitations

**N = 1** task (`parse_csv_summary` + tests via `codex exec --full-auto`); not a statistical benchmark. Medium export omits some tables (“Some content could not be imported”). Hardware and quant choices (**Q4_K_M** on 24 GB) heavily condition the Mac result; author explicitly avoids generalizing “Gemma 4 on Apple Silicon” from that run alone.

## Contradictions / Unverified Claims

- **tau2-bench** percentages for Gemma 3 vs Gemma 4 are **author-cited** in prose—trace to primary **Google/Gemma** eval materials before treating as settled.
- **Token-speed** ratios (**5.1×** Mac vs GB10) and **llama-bench** numbers come from the author’s machines on **2026-04-12**; different builds (author warns of **3.3×** regression between **llama.cpp** builds) can swamp comparisons.
- **GPT-5.4** cloud baseline (65 seconds, five tests) is a **single run** in one harness configuration.

## Sources

- [Medium (Google Cloud): I ran Gemma 4 as a local model in Codex CLI](https://medium.com/google-cloud/i-ran-gemma-4-as-a-local-model-in-codex-cli-7fda754dc0d4)
