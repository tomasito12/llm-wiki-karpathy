---
title: Context Engineering
slug: context-engineering
entity_id: topic:context-engineering
category: topic
tags:
- agent-systems
- ai-engineering
- context-engineering
- enterprise-workflows
- prompt-engineering
- runtime-architecture
- runtime-systems
first_seen: '2025-11-17'
last_seen: '2026-05-11'
source_count: 14
evidence_count: 98
source_ids:
- 15-ai-engineering-terms-beginners-get-wrong-and-what-it-costs-you-01kr434xn20g7q62nvzdvzgzx1
- 6-ai-concepts-you-must-master-to-build-production-ready-ai-systems-01kqfz8qd4s3rz9n6sx9dma9a8
- everyone-is-wrong-about-notebooklm-01kr433qg0ajtewhfmwa96q7a2
- harness-engineering-what-every-ai-engineer-needs-to-know-in-2026-01kqfyrmc31stvazs0r8kbpbbx
- i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr
- kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6
- llm-wiki-v2-extending-karpathy-s-llm-wiki-pattern-with-lessons-from-building-agentmemory-github-01kqh03nmcmtye4ewv1fv7wcxp
- llms-rag-agents-mcp-the-ai-evolution-you-must-know-a-visual-explanation-01krn2cgwkpeykxeadbb3f2ntm
- run-your-own-ai-agent-locally-ollama-mcp-and-skills-explained-01krbndqeaakn1z9vmar5vjf14
- technology-radar-01krc5f8a8a6x35ke2kdjn5d9w
- the-3-claude-prompts-worth-stealing-today-01kqkybgz2w3786bcejsy8qacb
- the-hardest-percentages-01kp69pz8s9dp41q7ps3z6xftt
- the-sequence-radar-849-last-week-in-ai-openai-ships-agents-xai-eyes-cursor-deepseek-and-kimi-advance-01kq4r8j0majmt8av52cng4zw0
- this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g
value_level: high
confidence: 0.927857
synthesis_state: synthesized
synthesis_stale: false
synthesis_input_hash: 50648d1ddf4d1c54
current_input_hash: 50648d1ddf4d1c54
synthesis_schema_version: 1
synthesis_prompt_version: 1
last_synthesized_at: '2026-07-09T15:57:24Z'
---

# Context Engineering

## Executive synthesis

Context engineering is the discipline of shaping the model’s information environment so it can act reliably: deciding what enters the context window, how it is structured, what stays out, and when information should be retrieved, summarized, or preserved. Across the sources, the strongest shared view is that model failures in production often come from bad context management—missing facts, stale instructions, noisy documents, or weak state handling—more than from the base model itself. This is especially important for agents and multi-step workflows, where context must carry task state, tool descriptions, source boundaries, and verification criteria over time. The evidence also points to a practical shift: context is no longer just prompt wording, but a runtime design problem that affects reliability, cost, and maintainability.

## Context card

- **Use this page when:** Use this page when you need a compact mental model for designing LLM/agent inputs, deciding what to include or exclude from context, or understanding why an assistant is failing despite a strong model.
- **Best for questions about:** What context engineering means in practice, Why context quality often matters more than prompt phrasing, How to structure prompts, retrieval, memory, and state for agents, When to use selective loading, summarization, or filtering instead of dumping everything into context, Why long-running or tool-using workflows need explicit context management
- **Not enough for:** A precise implementation guide for a specific stack, Benchmarked comparisons between context strategies, Hard rules for token budgets, caching, or memory architectures, A settled taxonomy of memory, retrieval, and prompt layers
- **Strongest sources:** Technology Radar, Harness Engineering: What Every AI Engineer Needs to Know in 2026, 15 AI Engineering Terms — Beginners Get Wrong (And What It Costs You), LLMs, RAG, Agents, MCP: The AI Evolution You Must Know (A Visual Explanation), LLM Wiki v2 — extending Karpathy's LLM Wiki pattern with lessons from building agentmemory · GitHub, This Open-Source App Turns Your Documents Into a Self-Building Wiki
- **Related tags:** agent-systems, ai-engineering, context-engineering, enterprise-workflows, prompt-engineering, runtime-architecture, runtime-systems

## What to remember

- The active context window is the practical boundary of what the model can reason over.
- Bad context can outperform a good prompt in the wrong environment; good context can rescue mediocre wording.
- Relevant context includes documents, history, tool schemas, system state, dates, progress, and workflow position.
- Filtering, ordering, and summarization are not optional clean-up steps; they are core design decisions.
- Context rot can happen before the window is full, especially when stale or contradictory material accumulates.
- For agents, the most useful context is often machine-readable state plus a small amount of high-signal guidance.
- This is especially important when the workflow spans multiple turns, sessions, or large codebases.

## Consensus

- Context engineering is about deciding what information a model sees at inference time, in what order, and with what compression or structure.
- It matters because many production failures come from missing, noisy, stale, or poorly ordered context rather than model incapability.
- It applies across chatbots, voicebots, support automation, coding agents, enterprise assistants, and other multi-step workflows that must preserve state.
- Good context design usually beats prompt wording alone when reliability, traceability, or repeatability matter.
- The main operational moves are selection, pruning, ordering, summarization, retrieval, and state/memory management.
- Context should be treated as a scarce runtime resource and an engineered control surface, not a passive text bucket.

## Tensions / open questions

- Sources agree that context quality matters more than prompt cleverness, but they do not fully agree on the best organizing pattern: some emphasize source boundaries and corpus design, others layered memory and retrieval, and others config-driven context blocks.
- Long-context models reduce some retrieval pressure, but sources caution that longer windows do not remove the need for curation, state management, or selective summarization.
- Some guidance implies context can be made precise with structured files and schemas, but the evidence here is mostly qualitative and does not establish a universal architecture.
- A few sources note that context failures can masquerade as model failures or serving/configuration failures, which makes diagnosis harder than the concept alone suggests.

## Evidence quality

- Evidence is broad and convergent across 14 sources, with 98 reviewed evidence items and repeated agreement on the core definition.
- Most claims are reinforced by multiple sources, especially around context as a managed resource, the importance of filtering and ordering, and the limits of long context.
- The evidence is mostly practitioner synthesis and operational commentary, not controlled experiments or formal benchmarks.
- Several sources are recent (2026), so the framing is somewhat time-sensitive and tied to current agent and workflow systems.
- There is little disagreement on the importance of context engineering, but less clarity on the best implementation patterns for different architectures.

## Practical takeaway

Before tuning prompts, check whether the model has the right facts, the right boundaries, and the right state. Filter aggressively, load information progressively, keep task-scoped state machine-readable where possible, and treat long or repeated context as something to curate, compress, and measure.

## Evidence index

- Sources: 14
- Evidence items: 98
- Current input hash: `50648d1ddf4d1c54`
- Cached input hash: `50648d1ddf4d1c54`
- Last synthesized: 2026-07-09T15:57:24Z
- Synthesis status: `fresh`

## Related pages

- [[topics/prompt-engineering|Prompt Engineering]]
- [[topics/knowledge-management|Knowledge Management]]
- [[topics/agentic-workflows|Agentic Workflows]]
- [[topics/progressive-disclosure-skill-design|Progressive Disclosure in Skill Design]]
- [[topics/layered-ai-architecture|Layered AI Architecture]]

## Sources

- [[sources/15-ai-engineering-terms-beginners-get-wrong-and-what-it-costs-you-01kr434xn20g7q62nvzdvzgzx1|15 AI Engineering Terms — Beginners Get Wrong (And What It Costs You)]]
- [[sources/6-ai-concepts-you-must-master-to-build-production-ready-ai-systems-01kqfz8qd4s3rz9n6sx9dma9a8|6 AI Concepts You Must Master to Build Production-Ready AI Systems]]
- [[sources/everyone-is-wrong-about-notebooklm-01kr433qg0ajtewhfmwa96q7a2|💠🌐 Everyone Is Wrong About NotebookLM]]
- [[sources/harness-engineering-what-every-ai-engineer-needs-to-know-in-2026-01kqfyrmc31stvazs0r8kbpbbx|Harness Engineering: What Every AI Engineer Needs to Know in 2026]]
- [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]]
- [[sources/kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6|Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better]]
- [[sources/llm-wiki-v2-extending-karpathy-s-llm-wiki-pattern-with-lessons-from-building-agentmemory-github-01kqh03nmcmtye4ewv1fv7wcxp|LLM Wiki v2 — extending Karpathy's LLM Wiki pattern with lessons from building agentmemory · GitHub]]
- [[sources/llms-rag-agents-mcp-the-ai-evolution-you-must-know-a-visual-explanation-01krn2cgwkpeykxeadbb3f2ntm|LLMs, RAG, Agents, MCP: The AI Evolution You Must Know (A Visual Explanation)]]
- [[sources/run-your-own-ai-agent-locally-ollama-mcp-and-skills-explained-01krbndqeaakn1z9vmar5vjf14|Run Your Own AI Agent Locally: Ollama, MCP, and Skills Explained]]
- [[sources/technology-radar-01krc5f8a8a6x35ke2kdjn5d9w|Technology Radar]]
- [[sources/the-3-claude-prompts-worth-stealing-today-01kqkybgz2w3786bcejsy8qacb|The 3 Claude Prompts Worth Stealing Today]]
- [[sources/the-hardest-percentages-01kp69pz8s9dp41q7ps3z6xftt|The hardest percentages]]
- [[sources/the-sequence-radar-849-last-week-in-ai-openai-ships-agents-xai-eyes-cursor-deepseek-and-kimi-advance-01kq4r8j0majmt8av52cng4zw0|The Sequence Radar #849: Last Week in AI: OpenAI Ships Agents, xAI Eyes Cursor, DeepSeek and Kimi Advance]]
- [[sources/this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g|This Open-Source App Turns Your Documents Into a Self-Building Wiki]]
