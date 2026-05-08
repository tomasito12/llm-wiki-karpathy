---
title: Gemma 4 (Google)
type: foundation-model
created: 2026-05-08
updated: 2026-05-08
vendor: Google
homepage: https://ai.google.dev/gemma
open_weights: yes
tags:
  - models
---

## Summary

**Gemma 4** is a **Google** **open-weights** model line in the Gemma series that the source pairs with **agentic coding** workflows. The article contrasts earlier Gemma generations’ weak tool-calling with **Gemma 4**—and stress-tests **26B MoE** and **31B dense** variants under **Codex CLI** with local runtimes.

## Technical snapshot

- **Variants cited:** **26B MoE** (A4B-it) in **Q4_K_M** on Mac; **31B dense** **Q4_K_M** on GB10 via Ollama tag **`gemma4:31b`** (per author; verify exact artifact names on vendor / Ollama library).
- **Tool calling:** Source cites **tau2-bench**-style figures: prior generation **~6.6%** vs **Gemma 4 31B ~86.4%**—must be cross-checked against **official** evaluation docs.
- **Architecture note:** Author explains **MoE** reaches higher **tok/s** on memory-bandwidth-limited hardware by activating fewer parameters per token than **dense** at similar quant—tradeoffs for **agent** quality observed on their **N=1** task.

## Access and licensing

- **Open weights** (Gemma series framing); get exact license and download locations from **Google AI / Gemma** documentation.
- Local serving via **Ollama**, **llama.cpp**, or other runtimes (author-tested only on those two).

## Evaluation claims

- **Third-party (single author):** Same **Codex** task: cloud **GPT-5.4** baseline vs local Gemma configs—**one run each** in the article; not a benchmark suite.
- **Vendor-claimed / author-relayed:** **tau2-bench** percentages for Gemma 3 vs Gemma 4—label **unverified** here until linked to primary tables.

## Limitations and risks

Local **quant**, **VRAM/DRAM**, runtime bugs, and tool-schema compatibility dominate outcomes; article’s Mac result is explicitly **not** a universal verdict on **Gemma 4 on Apple Silicon**.

## Timeline

### 2026-04-12

- Author ran **Codex CLI v0.120.0** trials with **Gemma 4** on **llama.cpp** (Mac, **ggml 0.9.11** build **8680**) and **Ollama 0.20.5** (GB10); cloud baseline **GPT-5.4** “high reasoning effort”; task: `parse_csv_summary` + tests via `codex exec --full-auto`.

**Source:** [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr]]

## Commentary

- Author’s takeaway: moving from “broken tool-calling” to “works” (**Gemma 3 → 4** framing) is what unlocks **local agentic coding**; **first-pass reliability** beat **raw tok/s** on wall clock for their spot check. [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr]]

## Sources

- [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr]]
