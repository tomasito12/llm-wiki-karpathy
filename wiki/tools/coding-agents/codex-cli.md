---
title: Codex CLI
type: tool
created: 2026-05-08
updated: 2026-05-08
tags:
  - tools
---

## What problem does this tool solve?

**Agentic coding from the terminal**—orchestrating read/edit/test **tool calls** against a repo (the source treats reliable **function-calling** as the gating capability for local models).

## Properties

- Author uses **Codex CLI** `config.toml` with custom providers, `wire_api = "responses"`, and profiles (e.g. hybrid **cloud vs local** switching).
- **Compatibility footguns** in source: default **`web_search_preview`** tool type rejected by **llama.cpp** unless **`web_search = "disabled"`**; **`stream_idle_timeout_ms`** may need **≥ 1,800,000** ms for long tool-call cycles (author reports ~99 s on Mac).
- Workflow cited: `codex exec --full-auto`, `codex --oss -m …` for local model selection (per author).
- Version pinned in article: **Codex CLI v0.120.0** (2026-04-12 run).

## Author assessments

- Entire experiment is framed as whether **local** backends can substitute **cloud** for daily agentic coding (cost, privacy, resilience). [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr]]
- First-pass **tool reliability** and fewer retries mattered more than raw **tok/s** for wall-clock success on the scripted task. [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr]]
- Suggests **hybrid** usage: local profile for sensitive or iterative work, default cloud for harder tasks. [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr]]

## Sources

- [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr]]
