---
title: Qwen 3.5 9B
slug: qwen-3-5-9b
entity_id: model:qwen-3-5-9b
category: foundation-model
tags:
- developer-focused
- low-cost
- open-weight-model
- tool-use-capable
first_seen: '2026-05-05'
last_seen: '2026-05-23'
source_count: 2
evidence_count: 24
source_ids:
- build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt
- run-your-own-ai-agent-locally-ollama-mcp-and-skills-explained-01krbndqeaakn1z9vmar5vjf14
value_level: high
confidence: 0.89
synthesis_state: stage1-placeholder
types:
- coding-model
- open-weight-model
- reasoning-model
---

# Qwen 3.5 9B

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
This local 9B model is used as the agent runtime for a tool-using workflow. In the article it is positioned as capable enough for a small local orchestration task with tool traces and a relatively large context window.

- The article highlights a 256K context window, which matters for agent workflows that need to keep long procedures, tool traces, or multi-step context in memory.
- It is described as being trained with tool-use traces, which is operationally relevant for function-calling and MCP-style orchestration.
- The quantized model is small enough to fit on a 16 GB RAM machine in the example, which makes local experimentation more accessible.

## Comparative Observations

- The author says qwen3.5:4b is an easier swap if the machine has less RAM.
- The author says llama3.1:8b is a fine substitute if a different local model is preferred.
- The article implies this 9B local model is usable for the task, but only with stronger orchestration than a larger or more reliable model would likely need.
- It is contrasted indirectly with the limitations of smaller models in general, such as empty turns and missed tool chaining, rather than with a specific benchmark competitor.

## Core Capabilities

- It supports long-context agent workflows with a 256K context window.
- It is trained with tool-use traces, which is useful for orchestrated function calling.
- It can run locally in a quantized form on a laptop-class machine.
- It can drive a tool-using agent loop when the system prompt and recursion are explicit.
- It can participate in JSON-mode extraction when the browser server asks it to fill a schema from a page snapshot.
- It is small enough to fit a local-first stack, which makes it practical for self-hosted workflows.

## Maturity signals

The article frames this as a usable local model rather than a research preview, but the evidence is limited to a single laptop demo. The author’s ability to run it locally on 16 GB RAM is a practical maturity signal for development use. There is no evidence here of enterprise deployment or benchmark leadership.

## Pricing / inference implications

As a local model, it avoids per-call API pricing, but the source does not quantify electricity, hardware, or latency costs. The article implies that deployment feasibility depends on available RAM and model quantization more than on subscription pricing.

## Provider

Qwen

## Related Models

- Qwen 3.5 4B
- Llama 3.1 8B

## Service automation implications

The article’s example is an operations check, so the model could support simple triage-style service workflows, but the source does not demonstrate support-grade reliability or handoff behavior.

## Weaknesses / limitations

- The article does not provide any systematic evaluation of instruction-following quality, tool accuracy, or hallucination rate.
- A 9B local model can be memory-sensitive, and the author explicitly suggests a smaller variant if RAM is tight.
- No pricing or throughput comparison is given, so the inference economics for heavy use remain unclear.

## Evidence / supporting sources

### Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python (2026-05-23)

- The article implies this 9B local model is usable for the task, but only with stronger orchestration than a larger or more reliable model would likely need. (`786a2f09e830` · neutral · comparative_observations[0]; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])
- It is contrasted indirectly with the limitations of smaller models in general, such as empty turns and missed tool chaining, rather than with a specific benchmark competitor. (`b1afb33905f1` · neutral · comparative_observations[1]; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])
- Using a 9B model makes the stack feasible on local hardware, but it also raises the importance of prompt discipline, recursive tool handling, and readable tool errors. The article shows that a smaller model can chain search and fetch, but it may also produce empty turns, guess URLs, or stop after search unless the harness explicitly nudges it. For structured extraction, the model is called inside the browser server with JSON formatting enabled, so deployment depends on careful snapshot budgeting and output constraints. (`4910fbb89600` · neutral · deployment_implications; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])
- The source uses Qwen 3.5 9B as the working model across all stages, which is a practical signal that it is sufficiently usable for local agent prototyping as of 2026-05-23. The article does not provide formal benchmarks, but it does show successful end-to-end use on live web pages and structured extraction tasks. The evidence is hands-on and limited to one project, so maturity should be read as developer-ready rather than universally robust. (`337540a2f946` · neutral · maturity_signals; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])
- A small tool-capable local model used to run the agent loop in this tutorial. The source implies it is capable enough to search, fetch, and extract when the system prompt and tool loop are tightly constrained, but it also needs strong orchestration to stay on task. (`91909eda56e2` · neutral · operational_profile; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])
- The article does not provide pricing, but the local 9B setup implies a low marginal inference cost compared with hosted API calls. The tradeoff is not price alone; the source makes clear that lower-capability local models need more harness work, which can offset some of the cost advantage in engineering time. (`d36d7b015e21` · neutral · pricing_inference_implications; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])
- Useful for browser-backed service workflows when the task is simple enough to be broken into search, fetch, and extract steps. The source suggests it can power grounded support lookups, but only if the agent is tightly instructed to fetch actual pages rather than answer from snippets. It is not presented as a drop-in autonomous support model; the orchestration matters as much as the model. (`a2786f8a20a4` · neutral · service_automation_implications; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])
- It can drive a tool-using agent loop when the system prompt and recursion are explicit. (`0a8493352882` · supporting · core_capabilities[0]; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])
- It can participate in JSON-mode extraction when the browser server asks it to fill a schema from a page snapshot. (`7915283a6037` · supporting · core_capabilities[1]; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])
- It is small enough to fit a local-first stack, which makes it practical for self-hosted workflows. (`d5cce12b76a1` · supporting · core_capabilities[2]; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])
- "I am using the qwen3.5:9b model throughout. So, please make sure you have Ollama installed with that model pulled, or edit the config to point at another tool-capable model." (`8cfc8e4a91a1` · supporting · supporting_snippet; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])
- The article repeatedly shows that this class of model can be brittle in multi-step tool use. It may stop after search snippets, return an empty response after a tool result, or infer an incorrect URL pattern, so the surrounding harness has to compensate. The source also shows that extraction quality depends on how much of the page survives truncation, which limits reliability on long pages. (`583acc4c132f` · uncertainty · weaknesses_limitations; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])

### Run Your Own AI Agent Locally: Ollama, MCP, and Skills Explained (2026-05-05)

- The author says qwen3.5:4b is an easier swap if the machine has less RAM. (`2b79b901702c` · neutral · comparative_observations[0]; [[sources/run-your-own-ai-agent-locally-ollama-mcp-and-skills-explained-01krbndqeaakn1z9vmar5vjf14|Run Your Own AI Agent Locally: Ollama, MCP, and Skills Explained]])
- The author says llama3.1:8b is a fine substitute if a different local model is preferred. (`3ec9890dc223` · neutral · comparative_observations[1]; [[sources/run-your-own-ai-agent-locally-ollama-mcp-and-skills-explained-01krbndqeaakn1z9vmar5vjf14|Run Your Own AI Agent Locally: Ollama, MCP, and Skills Explained]])
- The model is used as a local tool-calling runtime, so the main workflow implication is that agent loops can be tested without a cloud LLM dependency. Its long context and tool-use training reduce the need for external prompt scaffolding in small procedural tasks. (`ff69c73ef8c7` · neutral · deployment_implications; [[sources/run-your-own-ai-agent-locally-ollama-mcp-and-skills-explained-01krbndqeaakn1z9vmar5vjf14|Run Your Own AI Agent Locally: Ollama, MCP, and Skills Explained]])
- The article frames this as a usable local model rather than a research preview, but the evidence is limited to a single laptop demo. The author’s ability to run it locally on 16 GB RAM is a practical maturity signal for development use. There is no evidence here of enterprise deployment or benchmark leadership. (`3393edd65eb6` · neutral · maturity_signals; [[sources/run-your-own-ai-agent-locally-ollama-mcp-and-skills-explained-01krbndqeaakn1z9vmar5vjf14|Run Your Own AI Agent Locally: Ollama, MCP, and Skills Explained]])
- This local 9B model is used as the agent runtime for a tool-using workflow. In the article it is positioned as capable enough for a small local orchestration task with tool traces and a relatively large context window.

- The article highlights a 256K context window, which matters for agent workflows that need to keep long procedures, tool traces, or multi-step context in memory.
- It is described as being trained with tool-use traces, which is operationally relevant for function-calling and MCP-style orchestration.
- The quantized model is small enough to fit on a 16 GB RAM machine in the example, which makes local experimentation more accessible. (`e4dd6b20c886` · neutral · operational_profile; [[sources/run-your-own-ai-agent-locally-ollama-mcp-and-skills-explained-01krbndqeaakn1z9vmar5vjf14|Run Your Own AI Agent Locally: Ollama, MCP, and Skills Explained]])
- As a local model, it avoids per-call API pricing, but the source does not quantify electricity, hardware, or latency costs. The article implies that deployment feasibility depends on available RAM and model quantization more than on subscription pricing. (`30ba2baa4f5d` · neutral · pricing_inference_implications; [[sources/run-your-own-ai-agent-locally-ollama-mcp-and-skills-explained-01krbndqeaakn1z9vmar5vjf14|Run Your Own AI Agent Locally: Ollama, MCP, and Skills Explained]])
- The article’s example is an operations check, so the model could support simple triage-style service workflows, but the source does not demonstrate support-grade reliability or handoff behavior. (`596980a9912b` · neutral · service_automation_implications; [[sources/run-your-own-ai-agent-locally-ollama-mcp-and-skills-explained-01krbndqeaakn1z9vmar5vjf14|Run Your Own AI Agent Locally: Ollama, MCP, and Skills Explained]])
- It supports long-context agent workflows with a 256K context window. (`074384b15f31` · supporting · core_capabilities[0]; [[sources/run-your-own-ai-agent-locally-ollama-mcp-and-skills-explained-01krbndqeaakn1z9vmar5vjf14|Run Your Own AI Agent Locally: Ollama, MCP, and Skills Explained]])
- It is trained with tool-use traces, which is useful for orchestrated function calling. (`7af420961c61` · supporting · core_capabilities[1]; [[sources/run-your-own-ai-agent-locally-ollama-mcp-and-skills-explained-01krbndqeaakn1z9vmar5vjf14|Run Your Own AI Agent Locally: Ollama, MCP, and Skills Explained]])
- It can run locally in a quantized form on a laptop-class machine. (`21a3c78741c1` · supporting · core_capabilities[2]; [[sources/run-your-own-ai-agent-locally-ollama-mcp-and-skills-explained-01krbndqeaakn1z9vmar5vjf14|Run Your Own AI Agent Locally: Ollama, MCP, and Skills Explained]])
- "Qwen 3.5 9B is a recent model with a 256K context window, trained with tool-use traces, and quantized to 6.6 GB." (`215054e37c4a` · supporting · supporting_snippet; [[sources/run-your-own-ai-agent-locally-ollama-mcp-and-skills-explained-01krbndqeaakn1z9vmar5vjf14|Run Your Own AI Agent Locally: Ollama, MCP, and Skills Explained]])
- - The article does not provide any systematic evaluation of instruction-following quality, tool accuracy, or hallucination rate.
- A 9B local model can be memory-sensitive, and the author explicitly suggests a smaller variant if RAM is tight.
- No pricing or throughput comparison is given, so the inference economics for heavy use remain unclear. (`3fe6134cb6a3` · uncertainty · weaknesses_limitations; [[sources/run-your-own-ai-agent-locally-ollama-mcp-and-skills-explained-01krbndqeaakn1z9vmar5vjf14|Run Your Own AI Agent Locally: Ollama, MCP, and Skills Explained]])

## Contradictions / tensions

- - The article does not provide any systematic evaluation of instruction-following quality, tool accuracy, or hallucination rate.
- A 9B local model can be memory-sensitive, and the author explicitly suggests a smaller variant if RAM is tight.
- No pricing or throughput comparison is given, so the inference economics for heavy use remain unclear. (uncertainty; [[sources/run-your-own-ai-agent-locally-ollama-mcp-and-skills-explained-01krbndqeaakn1z9vmar5vjf14|Run Your Own AI Agent Locally: Ollama, MCP, and Skills Explained]])
- The article repeatedly shows that this class of model can be brittle in multi-step tool use. It may stop after search snippets, return an empty response after a tool result, or infer an incorrect URL pattern, so the surrounding harness has to compensate. The source also shows that extraction quality depends on how much of the page survives truncation, which limits reliability on long pages. (uncertainty; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])

## Related pages

- Llama 3.1 8B
- Qwen 3.5 4B

## Sources

- [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]]
- [[sources/run-your-own-ai-agent-locally-ollama-mcp-and-skills-explained-01krbndqeaakn1z9vmar5vjf14|Run Your Own AI Agent Locally: Ollama, MCP, and Skills Explained]]
