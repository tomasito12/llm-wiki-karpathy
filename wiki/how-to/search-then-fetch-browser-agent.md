---
title: Search-Then-Fetch Browser Agent
slug: search-then-fetch-browser-agent
entity_id: how_to:search-then-fetch-browser-agent
category: how-to
tags:
- agent-orchestration
- retrieval-systems
- runtime-architecture
- workflow-design
first_seen: '2026-05-23'
last_seen: '2026-05-23'
source_count: 1
evidence_count: 13
source_ids:
- build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt
value_level: high
confidence: 0.96
synthesis_state: stage1-placeholder
---

# Search-Then-Fetch Browser Agent

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
This is a procedure for building an agent that can find a web page and then read the page itself instead of guessing from search snippets. It solves a common problem in web-assisted automation: search results often give enough hints to find a page, but not enough detail to answer a question accurately. The pattern is useful when a model needs evidence from live pages, not just recalled knowledge. It also helps when the task requires a browser rather than a plain HTTP fetch because the page is wrapped in JavaScript or protected by anti-bot defenses. The overall goal is to make the agent compose search and browsing as one flow.

## Caveats

This pattern depends on a model that can reliably follow tool instructions. The source shows smaller models can stop after search, return empty turns, or pick a bad URL, so the harness needs recursion and nudges. Search snippets can still be misleading, and long page snapshots may need truncation, which can hide relevant facts.

## Implementation Steps

- Run a local search service and a browser service, then expose each one through MCP.
- Register the tools with fully qualified names so the agent can distinguish them.
- Write a system prompt that requires search first for fresh questions and fetch immediately after search results.
- Implement recursive tool handling so the model can call another tool after a tool result.
- Return readable tool errors and truncate overly long results before sending them back to the model.

## Prerequisites

- A tool-capable language model
- An MCP-capable agent harness
- A search backend such as SearXNG
- A browser-fetch backend such as camofox-browser

## Evidence / supporting sources

### Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python (2026-05-23)

- Set up a search tool and a browser fetch tool as separate services, then force the agent to use search first when it needs fresh information. After search returns candidate URLs, make the next step a browser fetch on the most promising result. Do not let the agent answer from snippets alone; have it read the page snapshot and then answer from that content. Use recursive tool handling so the model can chain another fetch if the first page is not enough. Add strong system-prompt rules that say the model must call the tool rather than merely describing what it would do. (`ee061b4309af` · neutral · answer_summary; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])
- Run a local search service and a browser service, then expose each one through MCP. (`beea2f7a3446` · neutral · implementation_steps[0]; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])
- Register the tools with fully qualified names so the agent can distinguish them. (`0d7041aa3dbe` · neutral · implementation_steps[1]; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])
- Write a system prompt that requires search first for fresh questions and fetch immediately after search results. (`c2435c7695d2` · neutral · implementation_steps[2]; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])
- Implement recursive tool handling so the model can call another tool after a tool result. (`feb19ea0fe87` · neutral · implementation_steps[3]; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])
- Return readable tool errors and truncate overly long results before sending them back to the model. (`17bda7db668b` · neutral · implementation_steps[4]; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])
- A tool-capable language model (`589214aad721` · neutral · prerequisites[0]; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])
- An MCP-capable agent harness (`ff711567f6da` · neutral · prerequisites[1]; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])
- A search backend such as SearXNG (`8244b40a499f` · neutral · prerequisites[2]; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])
- A browser-fetch backend such as camofox-browser (`5ec343c6dd3f` · neutral · prerequisites[3]; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])
- This is a procedure for building an agent that can find a web page and then read the page itself instead of guessing from search snippets. It solves a common problem in web-assisted automation: search results often give enough hints to find a page, but not enough detail to answer a question accurately. The pattern is useful when a model needs evidence from live pages, not just recalled knowledge. It also helps when the task requires a browser rather than a plain HTTP fetch because the page is wrapped in JavaScript or protected by anti-bot defenses. The overall goal is to make the agent compose search and browsing as one flow. (`a079e0fe406b` · neutral · what_and_problem; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])
- "The two tools compose into this pipeline:
user question -> search -> pick best URL -> fetch -> answer." (`60623d42e5c7` · supporting · supporting_snippet; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])
- This pattern depends on a model that can reliably follow tool instructions. The source shows smaller models can stop after search, return empty turns, or pick a bad URL, so the harness needs recursion and nudges. Search snippets can still be misleading, and long page snapshots may need truncation, which can hide relevant facts. (`5cda60cfed48` · uncertainty · caveats; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])

## Contradictions / tensions

- This pattern depends on a model that can reliably follow tool instructions. The source shows smaller models can stop after search, return empty turns, or pick a bad URL, so the harness needs recursion and nudges. Search snippets can still be misleading, and long page snapshots may need truncation, which can hide relevant facts. (uncertainty; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])

## Related pages

- [[how-to/progressive-discovery-for-agent-tools|Progressive Discovery for Agent Tools]]
- [[how-to/lazy-loading-tools|Lazy-Loading Tools]]

## Sources

- [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]]
