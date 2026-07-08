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
confidence: 0.927857142857143
synthesis_state: stage1-placeholder
---

# Context Engineering

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
When an AI system is constrained to a source set, the main performance lever becomes the structure of the context rather than prompt cleverness. Practitioners need to decide what enters the corpus, how documents are grouped, and where semantic boundaries should remain separate. The skill is closer to information architecture than to prompt writing. Good context design improves traceability, retrieval quality, and downstream synthesis.

## Key Points

- Corpus boundaries are part of the model design, not an afterthought.
- Merging documents can help bypass source limits, but it may blur useful distinctions.
- Separating documents can preserve semantic edges that improve retrieval and citation quality.
- Context quality depends on curation, not just token budget.
- Separate working, episodic, semantic, and procedural memory to control how information is compressed and reused.
- Use confidence and retention to decide what belongs in prompt context.
- Tie context loading to session start, query time, and lifecycle events rather than manual curation alone.
- Large agent system prompts can consume most of the usable context window.
- Quantizing the key-value cache can be the difference between fitting a model and crashing it.
- Context failures often look like model failures even when the root cause is the serving configuration.
- Raw context dumping leads to context rot and degraded reasoning.
- Progressive context disclosure keeps the signal-to-noise ratio sharp by loading only what is relevant.
- Context graphs and stateful compression are emerging ways to preserve institutional reasoning across longer workflows.
- Only request information when the workflow actually needs it.
- Structured summaries make human review easier during checkpoints.
- Context quality affects whether the agent can complete a workflow end to end.
- Repeated context can become a major cost driver in agentic systems.
- Long-running workflows need a deliberate strategy for what stays in the prompt and what gets retrieved.
- Caching and context reuse can materially change feasibility at scale.
- The model only reasons over what is inside the active context window.
- Poorly curated context can produce better results from a mediocre prompt than a carefully worded prompt surrounded by noise.
- Context window pressure forces explicit choices: summarize, truncate, or retrieve selectively.
- Context rot can appear before the hard window limit is reached.
- A strong prompt gives the model a job, context, success criteria, and a usable output shape.
- Ambiguity reduction is the central mechanism behind more reliable model behavior.
- Structured prompts are especially helpful when a task mixes instructions, changing inputs, and formatting needs.
- Long-context capability reduces some retrieval pressure but does not remove the need for good state management.
- Persistent memory and selective summarization are often more important than simply increasing token windows.
- Context should be treated as a managed resource because too much irrelevant state can degrade execution quality.
- AGENT.md/CLAUDE.md-style files make project context available at session start.
- JSON feature lists can act as both specification and progress tracker.
- Grounding in real file paths and state reduces hallucinated APIs and invented structure.
- The repo can become the single source of truth for agent behavior.
- The system context can carry time-sensitive facts such as the current date.
- Tool descriptions and schemas are part of the model’s usable context.
- Config-driven context makes task switching easier than hardcoding prompts.
- A scope file can outperform vague prompting by defining what counts as relevant.
- Filtering early reduces noise and contradictory over-extraction.
- Context should include both the immediate document and the existing knowledge base when compounding matters.
- Memory, retrieval, tools, history, state, and workflow position are all part of the context surface.
- Better context design can matter more than prompt wording for production reliability.
- This is especially relevant when a system must carry state across multi-step tasks.

## Operational Insight

Treat corpus design as an engineering task: curate source boundaries, reduce noise, and preserve separations that matter for retrieval and citations.

## Evidence / supporting sources

### 15 AI Engineering Terms — Beginners Get Wrong (And What It Costs You) (2026-04-21)

- Context engineering is the practice of designing what information a model can see at inference time so it has the right facts, instructions, and history to answer well. It includes selecting retrieved documents, trimming conversation history, ordering system context, and managing how much information is packed into the window. The key operational idea is that model performance often depends more on the quality and organization of context than on prompt wording alone. (`23396d359b37` · neutral · knowledge_summary; [[sources/15-ai-engineering-terms-beginners-get-wrong-and-what-it-costs-you-01kr434xn20g7q62nvzdvzgzx1|15 AI Engineering Terms — Beginners Get Wrong (And What It Costs You)]])
- Treat context as a managed resource. Before iterating on prompt wording, verify that the model has the right information, that irrelevant material is not crowding the window, and that long contexts are not silently degrading quality. (`0ea2ede081db` · neutral · operational_insight; [[sources/15-ai-engineering-terms-beginners-get-wrong-and-what-it-costs-you-01kr434xn20g7q62nvzdvzgzx1|15 AI Engineering Terms — Beginners Get Wrong (And What It Costs You)]])
- As of 2026-04-21, context engineering matters because many production AI failures come from missing, noisy, or poorly ordered information rather than from model incapability. It is especially relevant for chatbots, voicebots, and support automation systems that must combine user history, retrieved knowledge, and policy constraints under a limited context window. (`82e5af980403` · neutral · relevance_note; [[sources/15-ai-engineering-terms-beginners-get-wrong-and-what-it-costs-you-01kr434xn20g7q62nvzdvzgzx1|15 AI Engineering Terms — Beginners Get Wrong (And What It Costs You)]])
- The model only reasons over what is inside the active context window. (`44406771893b` · supporting · key_points[0]; [[sources/15-ai-engineering-terms-beginners-get-wrong-and-what-it-costs-you-01kr434xn20g7q62nvzdvzgzx1|15 AI Engineering Terms — Beginners Get Wrong (And What It Costs You)]])
- Poorly curated context can produce better results from a mediocre prompt than a carefully worded prompt surrounded by noise. (`36c8a5656fbe` · supporting · key_points[1]; [[sources/15-ai-engineering-terms-beginners-get-wrong-and-what-it-costs-you-01kr434xn20g7q62nvzdvzgzx1|15 AI Engineering Terms — Beginners Get Wrong (And What It Costs You)]])
- Context window pressure forces explicit choices: summarize, truncate, or retrieve selectively. (`b9fef7f9824f` · supporting · key_points[2]; [[sources/15-ai-engineering-terms-beginners-get-wrong-and-what-it-costs-you-01kr434xn20g7q62nvzdvzgzx1|15 AI Engineering Terms — Beginners Get Wrong (And What It Costs You)]])
- Context rot can appear before the hard window limit is reached. (`5f01b0ad061f` · supporting · key_points[3]; [[sources/15-ai-engineering-terms-beginners-get-wrong-and-what-it-costs-you-01kr434xn20g7q62nvzdvzgzx1|15 AI Engineering Terms — Beginners Get Wrong (And What It Costs You)]])
- Context engineering
is managing what information the model has access to at inference time: which documents are retrieved, how much conversation history is included, what system-level context to inject, and in what order. (`37d0ecb389f7` · supporting · supporting_snippet; [[sources/15-ai-engineering-terms-beginners-get-wrong-and-what-it-costs-you-01kr434xn20g7q62nvzdvzgzx1|15 AI Engineering Terms — Beginners Get Wrong (And What It Costs You)]])

### 6 AI Concepts You Must Master to Build Production-Ready AI Systems (2026-04-29)

- Context engineering is the discipline of deciding what information an AI model should see, in what order, and with what level of compression so it can do the task reliably. It covers selection, pruning, ordering, and summarization of prompts, retrieved documents, and conversation state. The point is not to maximize input size, but to make the most relevant information salient inside a limited context window. In production systems, this often matters more than prompt wording because the model can only use what remains visible and prominent in context. (`9211d13991f1` · neutral · knowledge_summary; [[sources/6-ai-concepts-you-must-master-to-build-production-ready-ai-systems-01kqfz8qd4s3rz9n6sx9dma9a8|6 AI Concepts You Must Master to Build Production-Ready AI Systems]])
- Treat context as a scarce runtime resource. Keep the task goal, constraints, and freshest evidence prominent; compress older material and remove irrelevant noise before the model makes a decision. (`6d22cfcaf4f1` · neutral · operational_insight; [[sources/6-ai-concepts-you-must-master-to-build-production-ready-ai-systems-01kqfz8qd4s3rz9n6sx9dma9a8|6 AI Concepts You Must Master to Build Production-Ready AI Systems]])
- This is durable across chatbots, voicebots, support automation, and agent systems because every production LLM workflow has a bounded attention budget. Teams that manage context well get more stable outputs, fewer instruction-loss failures, and better cost control as of 2026-04-29. (`eeff33460895` · neutral · relevance_note; [[sources/6-ai-concepts-you-must-master-to-build-production-ready-ai-systems-01kqfz8qd4s3rz9n6sx9dma9a8|6 AI Concepts You Must Master to Build Production-Ready AI Systems]])
- "Context engineering is the discipline of deciding exactly what information goes into the model’s context window, how it is structured, and what gets left out." (`830f5d0cba83` · supporting · supporting_snippet; [[sources/6-ai-concepts-you-must-master-to-build-production-ready-ai-systems-01kqfz8qd4s3rz9n6sx9dma9a8|6 AI Concepts You Must Master to Build Production-Ready AI Systems]])

### 💠🌐 Everyone Is Wrong About NotebookLM (2025-11-17)

- When an AI system is constrained to a source set, the main performance lever becomes the structure of the context rather than prompt cleverness. Practitioners need to decide what enters the corpus, how documents are grouped, and where semantic boundaries should remain separate. The skill is closer to information architecture than to prompt writing. Good context design improves traceability, retrieval quality, and downstream synthesis. (`9ea13522b1b4` · neutral · knowledge_summary; [[sources/everyone-is-wrong-about-notebooklm-01kr433qg0ajtewhfmwa96q7a2|💠🌐 Everyone Is Wrong About NotebookLM]])
- Treat corpus design as an engineering task: curate source boundaries, reduce noise, and preserve separations that matter for retrieval and citations. (`fb0a903c7ac1` · neutral · operational_insight; [[sources/everyone-is-wrong-about-notebooklm-01kr433qg0ajtewhfmwa96q7a2|💠🌐 Everyone Is Wrong About NotebookLM]])
- This matters for any AI system whose behavior depends on document selection, chunking, and prompt context. In production assistants, context engineering often determines whether answers are grounded, concise, and maintainable. (`8fa89f68aae3` · neutral · relevance_note; [[sources/everyone-is-wrong-about-notebooklm-01kr433qg0ajtewhfmwa96q7a2|💠🌐 Everyone Is Wrong About NotebookLM]])
- Corpus boundaries are part of the model design, not an afterthought. (`379a5f027d89` · supporting · key_points[0]; [[sources/everyone-is-wrong-about-notebooklm-01kr433qg0ajtewhfmwa96q7a2|💠🌐 Everyone Is Wrong About NotebookLM]])
- Merging documents can help bypass source limits, but it may blur useful distinctions. (`5fd51d279f86` · supporting · key_points[1]; [[sources/everyone-is-wrong-about-notebooklm-01kr433qg0ajtewhfmwa96q7a2|💠🌐 Everyone Is Wrong About NotebookLM]])
- Separating documents can preserve semantic edges that improve retrieval and citation quality. (`d70a8a6ee0d8` · supporting · key_points[2]; [[sources/everyone-is-wrong-about-notebooklm-01kr433qg0ajtewhfmwa96q7a2|💠🌐 Everyone Is Wrong About NotebookLM]])
- Context quality depends on curation, not just token budget. (`6ebf216d2a00` · supporting · key_points[3]; [[sources/everyone-is-wrong-about-notebooklm-01kr433qg0ajtewhfmwa96q7a2|💠🌐 Everyone Is Wrong About NotebookLM]])
- A good NotebookLM session starts before the prompt:
What belongs in this corpus?
What does not?
What needs to be merged into one mega-document to bypass the 50-source limit?
What must stay separate to keep semantic edges sharp?
What is noise?
What is scaffolding? (`b1f17e58ad3d` · supporting · supporting_snippet; [[sources/everyone-is-wrong-about-notebooklm-01kr433qg0ajtewhfmwa96q7a2|💠🌐 Everyone Is Wrong About NotebookLM]])

### Harness Engineering: What Every AI Engineer Needs to Know in 2026 (2026-04-27)

- Reliable agent performance often depends more on the quality of the context supplied to the system than on the wording of a prompt. Context engineering includes repository structure, documentation, progress tracking, and task-scoped state that tell the agent what already exists and what it should do next. It reduces hallucinated paths, duplicate work, and inconsistent execution by grounding the agent in real artifacts rather than abstract instructions. The practice becomes more important as agents operate over long sessions or across large codebases. (`1b70e9fb7981` · neutral · knowledge_summary; [[sources/harness-engineering-what-every-ai-engineer-needs-to-know-in-2026-01kqfyrmc31stvazs0r8kbpbbx|Harness Engineering: What Every AI Engineer Needs to Know in 2026]])
- When an agent must modify software or operate a workflow, give it the current state of the world in machine-readable form: paths, progress, constraints, and verification criteria. That usually outperforms longer prompts. (`82f20772aae1` · neutral · operational_insight; [[sources/harness-engineering-what-every-ai-engineer-needs-to-know-in-2026-01kqfyrmc31stvazs0r8kbpbbx|Harness Engineering: What Every AI Engineer Needs to Know in 2026]])
- Context engineering is a durable operational pattern because agentic systems fail quickly when they lack grounding. It is central to coding agents, knowledge-grounded assistants, and any automation that needs to remember state across sessions or tasks. (`6c157bb559bc` · neutral · relevance_note; [[sources/harness-engineering-what-every-ai-engineer-needs-to-know-in-2026-01kqfyrmc31stvazs0r8kbpbbx|Harness Engineering: What Every AI Engineer Needs to Know in 2026]])
- AGENT.md/CLAUDE.md-style files make project context available at session start. (`78895aa76534` · supporting · key_points[0]; [[sources/harness-engineering-what-every-ai-engineer-needs-to-know-in-2026-01kqfyrmc31stvazs0r8kbpbbx|Harness Engineering: What Every AI Engineer Needs to Know in 2026]])
- JSON feature lists can act as both specification and progress tracker. (`fe305902ce32` · supporting · key_points[1]; [[sources/harness-engineering-what-every-ai-engineer-needs-to-know-in-2026-01kqfyrmc31stvazs0r8kbpbbx|Harness Engineering: What Every AI Engineer Needs to Know in 2026]])
- Grounding in real file paths and state reduces hallucinated APIs and invented structure. (`3e20088ecd27` · supporting · key_points[2]; [[sources/harness-engineering-what-every-ai-engineer-needs-to-know-in-2026-01kqfyrmc31stvazs0r8kbpbbx|Harness Engineering: What Every AI Engineer Needs to Know in 2026]])
- The repo can become the single source of truth for agent behavior. (`0420920e5a78` · supporting · key_points[3]; [[sources/harness-engineering-what-every-ai-engineer-needs-to-know-in-2026-01kqfyrmc31stvazs0r8kbpbbx|Harness Engineering: What Every AI Engineer Needs to Know in 2026]])
- “What does the agent need to know before it writes a single line of code?” (`0c059fe3cd0e` · supporting · supporting_snippet; [[sources/harness-engineering-what-every-ai-engineer-needs-to-know-in-2026-01kqfyrmc31stvazs0r8kbpbbx|Harness Engineering: What Every AI Engineer Needs to Know in 2026]])

### I ran Gemma 4 as a local model in Codex CLI (2026-04-13)

- Context engineering is the practice of shaping prompts, memory, and surrounding instructions so a model can complete the task without exceeding context limits or wasting attention on irrelevant text. In local agent setups, it includes practical decisions about context window size, prompt length, tool schema compatibility, and memory management. These choices are often as important as the model itself because they determine whether the agent can ingest the system prompt, preserve working state, and keep the tool loop stable. Good context engineering reduces failure modes like truncation, stalled requests, and malformed tool calls. (`9959fdf3ace4` · neutral · knowledge_summary; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- Treat context budget as an engineering constraint, not a background setting. If the agent's own system prompt is large, the serving stack must be tuned to fit it before any model-quality comparison is meaningful. (`9a64e1d417b2` · neutral · operational_insight; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- This matters because many production AI systems fail from context mismanagement long before they fail from model weakness. Conversational agents and coding agents both need careful prompt sizing, memory limits, and schema alignment to stay reliable. (`697dfc4adc39` · neutral · relevance_note; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- Large agent system prompts can consume most of the usable context window. (`b384e97f7c62` · supporting · key_points[0]; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- Quantizing the key-value cache can be the difference between fitting a model and crashing it. (`d8c33b657dee` · supporting · key_points[1]; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- Context failures often look like model failures even when the root cause is the serving configuration. (`1e8a9285ac6b` · supporting · key_points[2]; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])
- "Set context to 32,768 (Codex CLI's system prompt needs at least 27,000 tokens) and quantise the KV cache with -ctk q8_0 -ctv q8_0." (`6df3a9d46b68` · supporting · supporting_snippet; [[sources/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr|I ran Gemma 4 as a local model in Codex CLI]])

### Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better (2026-04-20)

- Context engineering is the practice of shaping what information a model sees, how it is structured, and how much of it is retained across a workflow. It becomes especially important in long-running agent systems where repeated queries, large codebases, or cached context can dominate cost and reliability. Good context design can reduce re-prompting, improve consistency, and make repeated interactions cheaper. Poor context design can waste tokens, confuse routing, or overwhelm the model with irrelevant detail. (`e69deeb5311f` · neutral · knowledge_summary; [[sources/kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6|Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better]])
- Treat cached or repeated context as a design object, because token cost and retrieval structure can decide whether an agent workflow is economically viable. (`7882a81c5596` · neutral · operational_insight; [[sources/kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6|Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better]])
- Context engineering is central to conversational AI and service automation because the wrong context can make assistants forget important state or repeat expensive retrieval. It is also a major cost lever in any system that reuses large documents, tickets, or codebases across multiple turns. (`0d068f2bf27c` · neutral · relevance_note; [[sources/kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6|Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better]])
- Repeated context can become a major cost driver in agentic systems. (`acdd07d38041` · supporting · key_points[0]; [[sources/kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6|Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better]])
- Long-running workflows need a deliberate strategy for what stays in the prompt and what gets retrieved. (`fd58217dbfe2` · supporting · key_points[1]; [[sources/kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6|Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better]])
- Caching and context reuse can materially change feasibility at scale. (`f668c779f4a6` · supporting · key_points[2]; [[sources/kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6|Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better]])
- This is the use case Moonshot is clearly targeting: long-running coding agents that hold a full codebase in context and repeatedly query against it. (`c16b4a85e365` · supporting · supporting_snippet; [[sources/kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6|Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better]])

### LLM Wiki v2 — extending Karpathy's LLM Wiki pattern with lessons from building agentmemory · GitHub (2026-04-07)

- Context engineering is the practice of assembling the right information, in the right form, for a model to use effectively. A useful system does not just collect raw text; it consolidates, scores, filters, and routes information so the model sees high-signal context instead of an undifferentiated dump. It also benefits from event-driven updates, because the best context depends on recent activity, contradictions, and task state. Schema and routing rules are part of the context layer because they determine what gets surfaced and when. (`82526d5a17b8` · neutral · knowledge_summary; [[sources/llm-wiki-v2-extending-karpathy-s-llm-wiki-pattern-with-lessons-from-building-agentmemory-github-01kqh03nmcmtye4ewv1fv7wcxp|LLM Wiki v2 — extending Karpathy's LLM Wiki pattern with lessons from building agentmemory · GitHub]])
- Design the context pipeline as a layered filter: raw observations, consolidated memories, confidence signals, and retrieval logic should each add structure before the model sees the result. (`c6382464c3e8` · neutral · operational_insight; [[sources/llm-wiki-v2-extending-karpathy-s-llm-wiki-pattern-with-lessons-from-building-agentmemory-github-01kqh03nmcmtye4ewv1fv7wcxp|LLM Wiki v2 — extending Karpathy's LLM Wiki pattern with lessons from building agentmemory · GitHub]])
- Context engineering is central to AI products because model behavior depends heavily on what is selected, compressed, and prioritized before generation. The pattern is especially relevant for assistants, agent systems, and support workflows where stale or overly broad context can degrade answers. (`d6ae0ca228d3` · neutral · relevance_note; [[sources/llm-wiki-v2-extending-karpathy-s-llm-wiki-pattern-with-lessons-from-building-agentmemory-github-01kqh03nmcmtye4ewv1fv7wcxp|LLM Wiki v2 — extending Karpathy's LLM Wiki pattern with lessons from building agentmemory · GitHub]])
- Separate working, episodic, semantic, and procedural memory to control how information is compressed and reused. (`ac3a8caaf9ce` · supporting · key_points[0]; [[sources/llm-wiki-v2-extending-karpathy-s-llm-wiki-pattern-with-lessons-from-building-agentmemory-github-01kqh03nmcmtye4ewv1fv7wcxp|LLM Wiki v2 — extending Karpathy's LLM Wiki pattern with lessons from building agentmemory · GitHub]])
- Use confidence and retention to decide what belongs in prompt context. (`58c8d2570b8d` · supporting · key_points[1]; [[sources/llm-wiki-v2-extending-karpathy-s-llm-wiki-pattern-with-lessons-from-building-agentmemory-github-01kqh03nmcmtye4ewv1fv7wcxp|LLM Wiki v2 — extending Karpathy's LLM Wiki pattern with lessons from building agentmemory · GitHub]])
- Tie context loading to session start, query time, and lifecycle events rather than manual curation alone. (`d8245bbd10a9` · supporting · key_points[2]; [[sources/llm-wiki-v2-extending-karpathy-s-llm-wiki-pattern-with-lessons-from-building-agentmemory-github-01kqh03nmcmtye4ewv1fv7wcxp|LLM Wiki v2 — extending Karpathy's LLM Wiki pattern with lessons from building agentmemory · GitHub]])
- The three-layer architecture (raw sources, wiki, schema) works. (`f60a0fe77119` · supporting · supporting_snippet; [[sources/llm-wiki-v2-extending-karpathy-s-llm-wiki-pattern-with-lessons-from-building-agentmemory-github-01kqh03nmcmtye4ewv1fv7wcxp|LLM Wiki v2 — extending Karpathy's LLM Wiki pattern with lessons from building agentmemory · GitHub]])

### LLMs, RAG, Agents, MCP: The AI Evolution You Must Know (A Visual Explanation) (2026-05-11)

- Context engineering is the practice of designing the information environment around a model so it can act reliably. It includes memory, retrieval, tool descriptions, conversation history, system state, and workflow position. The core idea is that model behavior depends heavily on what information is made available at each step and how that information is organized. This turns context from a passive input into an engineered control surface. (`73ab4db2e2aa` · neutral · knowledge_summary; [[sources/llms-rag-agents-mcp-the-ai-evolution-you-must-know-a-visual-explanation-01krn2cgwkpeykxeadbb3f2ntm|LLMs, RAG, Agents, MCP: The AI Evolution You Must Know (A Visual Explanation)]])
- For production systems, manage context as a first-class design problem. Control what the model remembers, what gets retrieved, how tools are described, and how task state is preserved across steps so the system can stay on task without relying on prompt cleverness alone. (`93ac5b619c55` · neutral · operational_insight; [[sources/llms-rag-agents-mcp-the-ai-evolution-you-must-know-a-visual-explanation-01krn2cgwkpeykxeadbb3f2ntm|LLMs, RAG, Agents, MCP: The AI Evolution You Must Know (A Visual Explanation)]])
- This is highly reusable for agents, support automation, and any workflow where the model must maintain task state across multiple turns. It gives practitioners a practical framework for reducing drift, confusion, and brittle behavior in long-running conversational systems. (`22ed8aee16c2` · neutral · relevance_note; [[sources/llms-rag-agents-mcp-the-ai-evolution-you-must-know-a-visual-explanation-01krn2cgwkpeykxeadbb3f2ntm|LLMs, RAG, Agents, MCP: The AI Evolution You Must Know (A Visual Explanation)]])
- Memory, retrieval, tools, history, state, and workflow position are all part of the context surface. (`31a2c3aecf8a` · supporting · key_points[0]; [[sources/llms-rag-agents-mcp-the-ai-evolution-you-must-know-a-visual-explanation-01krn2cgwkpeykxeadbb3f2ntm|LLMs, RAG, Agents, MCP: The AI Evolution You Must Know (A Visual Explanation)]])
- Better context design can matter more than prompt wording for production reliability. (`7c8d5d99d54b` · supporting · key_points[1]; [[sources/llms-rag-agents-mcp-the-ai-evolution-you-must-know-a-visual-explanation-01krn2cgwkpeykxeadbb3f2ntm|LLMs, RAG, Agents, MCP: The AI Evolution You Must Know (A Visual Explanation)]])
- This is especially relevant when a system must carry state across multi-step tasks. (`1fcaec9f0e65` · supporting · key_points[2]; [[sources/llms-rag-agents-mcp-the-ai-evolution-you-must-know-a-visual-explanation-01krn2cgwkpeykxeadbb3f2ntm|LLMs, RAG, Agents, MCP: The AI Evolution You Must Know (A Visual Explanation)]])
- "Context engineering is the discipline that makes everything above work reliably." (`e5f24e5f15fe` · supporting · supporting_snippet; [[sources/llms-rag-agents-mcp-the-ai-evolution-you-must-know-a-visual-explanation-01krn2cgwkpeykxeadbb3f2ntm|LLMs, RAG, Agents, MCP: The AI Evolution You Must Know (A Visual Explanation)]])

### Run Your Own AI Agent Locally: Ollama, MCP, and Skills Explained (2026-05-05)

- Context engineering is the practice of shaping what information the model sees so it can perform the task correctly. In agent systems that means deciding which instructions, tool descriptions, schemas, dates, and constraints belong in the prompt or system context. It is not just about stuffing more text into the prompt; it is about making the right information available at the right time. Good context design reduces ambiguity and limits unnecessary tool calls. (`be5911b7c27d` · neutral · knowledge_summary; [[sources/run-your-own-ai-agent-locally-ollama-mcp-and-skills-explained-01krbndqeaakn1z9vmar5vjf14|Run Your Own AI Agent Locally: Ollama, MCP, and Skills Explained]])
- Put the procedural rules, tool descriptions, and relevant runtime facts in a config-driven context block so the model can follow the task without extra back-and-forth. Keep the context tight enough that the model can reason over it and broad enough that it does not invent missing details. (`19dbe311a42c` · neutral · operational_insight; [[sources/run-your-own-ai-agent-locally-ollama-mcp-and-skills-explained-01krbndqeaakn1z9vmar5vjf14|Run Your Own AI Agent Locally: Ollama, MCP, and Skills Explained]])
- Context engineering is a durable skill for conversational AI and service automation because the quality of the task context often matters more than the raw model choice. The same pattern appears in chatbots, internal assistants, and tool-using agents that need current dates, policy rules, or domain-specific instructions to behave correctly. (`30a3137b51df` · neutral · relevance_note; [[sources/run-your-own-ai-agent-locally-ollama-mcp-and-skills-explained-01krbndqeaakn1z9vmar5vjf14|Run Your Own AI Agent Locally: Ollama, MCP, and Skills Explained]])
- The system context can carry time-sensitive facts such as the current date. (`fc75654ff14d` · supporting · key_points[0]; [[sources/run-your-own-ai-agent-locally-ollama-mcp-and-skills-explained-01krbndqeaakn1z9vmar5vjf14|Run Your Own AI Agent Locally: Ollama, MCP, and Skills Explained]])
- Tool descriptions and schemas are part of the model’s usable context. (`c954e141f057` · supporting · key_points[1]; [[sources/run-your-own-ai-agent-locally-ollama-mcp-and-skills-explained-01krbndqeaakn1z9vmar5vjf14|Run Your Own AI Agent Locally: Ollama, MCP, and Skills Explained]])
- Config-driven context makes task switching easier than hardcoding prompts. (`46f176448c9b` · supporting · key_points[2]; [[sources/run-your-own-ai-agent-locally-ollama-mcp-and-skills-explained-01krbndqeaakn1z9vmar5vjf14|Run Your Own AI Agent Locally: Ollama, MCP, and Skills Explained]])
- "Today's date is provided in the system context." (`671537ee38bb` · supporting · supporting_snippet; [[sources/run-your-own-ai-agent-locally-ollama-mcp-and-skills-explained-01krbndqeaakn1z9vmar5vjf14|Run Your Own AI Agent Locally: Ollama, MCP, and Skills Explained]])

### Technology Radar (2026-04-13)

- Context engineering is the practice of treating the model context window as an engineered system rather than a passive text bucket. It focuses on deciding what information the model sees, when it sees it, and how that information is loaded, compressed, retrieved, or refreshed over time. The goal is to preserve signal, reduce confusion, and keep reasoning stable as tasks become longer and more agentic. In production systems, this becomes a design problem that spans prompts, retrieval, tools, memory, and state management. (`ad838bdfb224` · neutral · knowledge_summary; [[sources/technology-radar-01krc5f8a8a6x35ke2kdjn5d9w|Technology Radar]])
- The durable lesson is to design context as a pipeline: start with discovery, load details only when needed, and prevent long prompts from accreting conflicting instructions and stale facts. (`0b85d3b3cba1` · neutral · operational_insight; [[sources/technology-radar-01krc5f8a8a6x35ke2kdjn5d9w|Technology Radar]])
- This matters because most production AI failures are often context failures: the model had the wrong inputs, too much noise, or stale instructions. For conversational AI and service automation, disciplined context design improves reliability, reduces hallucinations, and makes agent behavior easier to govern. (`25ff3f2fd80b` · neutral · relevance_note; [[sources/technology-radar-01krc5f8a8a6x35ke2kdjn5d9w|Technology Radar]])
- Raw context dumping leads to context rot and degraded reasoning. (`4c85e6545572` · supporting · key_points[0]; [[sources/technology-radar-01krc5f8a8a6x35ke2kdjn5d9w|Technology Radar]])
- Progressive context disclosure keeps the signal-to-noise ratio sharp by loading only what is relevant. (`b38624d02204` · supporting · key_points[1]; [[sources/technology-radar-01krc5f8a8a6x35ke2kdjn5d9w|Technology Radar]])
- Context graphs and stateful compression are emerging ways to preserve institutional reasoning across longer workflows. (`a1252e91b045` · supporting · key_points[2]; [[sources/technology-radar-01krc5f8a8a6x35ke2kdjn5d9w|Technology Radar]])
- Context engineering has evolved from an optimization tactic into a foundational architectural concern for modern AI systems. Unlike prompt engineering, which focuses on wording, context engineering treats the context window as a design surface and intentionally constructs the AI's information environment. (`87a519bcdc59` · supporting · supporting_snippet; [[sources/technology-radar-01krc5f8a8a6x35ke2kdjn5d9w|Technology Radar]])

### The 3 Claude Prompts Worth Stealing Today (2026-04-24)

- Context engineering is the practice of shaping a model’s input so it has enough role, background, constraints, examples, and output structure to do useful work reliably. The goal is not clever phrasing but reducing ambiguity so the model can behave more consistently across repeated tasks. Good context engineering often treats a prompt as a small system rather than a one-off request. (`d48327181ad9` · neutral · knowledge_summary; [[sources/the-3-claude-prompts-worth-stealing-today-01kqkybgz2w3786bcejsy8qacb|The 3 Claude Prompts Worth Stealing Today]])
- For practical AI work, the highest-leverage prompt improvement is usually adding the right context and output shape, not chasing shorter or more ornate wording. Role, goal, constraints, and formatting should be explicit when reliability matters. (`db95971934a4` · neutral · operational_insight; [[sources/the-3-claude-prompts-worth-stealing-today-01kqkybgz2w3786bcejsy8qacb|The 3 Claude Prompts Worth Stealing Today]])
- As of 2026-04-24, context engineering is a durable skill for conversational AI, agent workflows, and service automation because most failures come from underspecified inputs rather than model incapability. It matters whenever teams need repeatable outputs, easier review, or lower handholding across chatbots, voicebots, and internal assistants. (`1448377007ff` · neutral · relevance_note; [[sources/the-3-claude-prompts-worth-stealing-today-01kqkybgz2w3786bcejsy8qacb|The 3 Claude Prompts Worth Stealing Today]])
- A strong prompt gives the model a job, context, success criteria, and a usable output shape. (`44bcd526be8e` · supporting · key_points[0]; [[sources/the-3-claude-prompts-worth-stealing-today-01kqkybgz2w3786bcejsy8qacb|The 3 Claude Prompts Worth Stealing Today]])
- Ambiguity reduction is the central mechanism behind more reliable model behavior. (`7c4b72a2a460` · supporting · key_points[1]; [[sources/the-3-claude-prompts-worth-stealing-today-01kqkybgz2w3786bcejsy8qacb|The 3 Claude Prompts Worth Stealing Today]])
- Structured prompts are especially helpful when a task mixes instructions, changing inputs, and formatting needs. (`063deac77a8e` · supporting · key_points[2]; [[sources/the-3-claude-prompts-worth-stealing-today-01kqkybgz2w3786bcejsy8qacb|The 3 Claude Prompts Worth Stealing Today]])
- “Give Claude a real job. Give it context. Define what a good answer looks like.” (`9ff496067f12` · supporting · supporting_snippet; [[sources/the-3-claude-prompts-worth-stealing-today-01kqkybgz2w3786bcejsy8qacb|The 3 Claude Prompts Worth Stealing Today]])

### The hardest percentages (2026-04-14)

- Context engineering is the practice of supplying an AI system with the right inputs, state, and constraints so it can act correctly. In workflow settings, that includes routing rules, data connectors, policy context, and structured summaries for handoff. The goal is to reduce ambiguity and make the model's next step easier to verify. Good context design often matters as much as the base model. (`c63582abbbf8` · neutral · knowledge_summary; [[sources/the-hardest-percentages-01kp69pz8s9dp41q7ps3z6xftt|The hardest percentages]])
- Procedural systems fail less when context is structured, monitored, and only requested when needed. (`3539f59706b3` · neutral · operational_insight; [[sources/the-hardest-percentages-01kp69pz8s9dp41q7ps3z6xftt|The hardest percentages]])
- This is central to reliable conversational AI because support, chat, and voice flows depend on getting the right details at the right moment. Better context packaging lowers friction for users and reduces avoidable handoff loops. (`09dcd4cd2cf5` · neutral · relevance_note; [[sources/the-hardest-percentages-01kp69pz8s9dp41q7ps3z6xftt|The hardest percentages]])
- Only request information when the workflow actually needs it. (`4be69328f408` · supporting · key_points[0]; [[sources/the-hardest-percentages-01kp69pz8s9dp41q7ps3z6xftt|The hardest percentages]])
- Structured summaries make human review easier during checkpoints. (`f90ebbd43878` · supporting · key_points[1]; [[sources/the-hardest-percentages-01kp69pz8s9dp41q7ps3z6xftt|The hardest percentages]])
- Context quality affects whether the agent can complete a workflow end to end. (`f810a1d16f58` · supporting · key_points[2]; [[sources/the-hardest-percentages-01kp69pz8s9dp41q7ps3z6xftt|The hardest percentages]])
- Optional data connector parameters: Fin only asks customers for information when it’s actually needed, instead of prompting for every field. (`563c5dce3fbc` · supporting · supporting_snippet; [[sources/the-hardest-percentages-01kp69pz8s9dp41q7ps3z6xftt|The hardest percentages]])

### The Sequence Radar #849: Last Week in AI: OpenAI Ships Agents, xAI Eyes Cursor, DeepSeek and Kimi Advance (2026-04-26)

- Context engineering is the practice of shaping what information a model sees, in what order, and with what memory or retrieval support so it can perform well on a task. It includes summarization, long-context handling, retrieval, state management, and deciding what should persist across turns or sessions. The goal is to reduce confusion, missing facts, and unnecessary prompt rework while keeping the model focused on the task. In operational settings, context engineering often determines whether an assistant can sustain a long workflow or only answer isolated questions. (`8f6c1fc0d6d9` · neutral · knowledge_summary; [[sources/the-sequence-radar-849-last-week-in-ai-openai-ships-agents-xai-eyes-cursor-deepseek-and-kimi-advance-01kq4r8j0majmt8av52cng4zw0|The Sequence Radar #849: Last Week in AI: OpenAI Ships Agents, xAI Eyes Cursor, DeepSeek and Kimi Advance]])
- As models take on longer tasks, managing context becomes a primary engineering discipline rather than a prompt-writing detail. Long context helps, but only if the system also curates what gets preserved and what gets dropped. (`1065b6cde53b` · neutral · operational_insight; [[sources/the-sequence-radar-849-last-week-in-ai-openai-ships-agents-xai-eyes-cursor-deepseek-and-kimi-advance-01kq4r8j0majmt8av52cng4zw0|The Sequence Radar #849: Last Week in AI: OpenAI Ships Agents, xAI Eyes Cursor, DeepSeek and Kimi Advance]])
- Context engineering matters because AI systems increasingly operate across multi-step workflows, not just one-off prompts. It is a central lever for reliability in chatbots, coding agents, enterprise assistants, and any service workflow that must remember state without overwhelming the model. (`f6542d943aa3` · neutral · relevance_note; [[sources/the-sequence-radar-849-last-week-in-ai-openai-ships-agents-xai-eyes-cursor-deepseek-and-kimi-advance-01kq4r8j0majmt8av52cng4zw0|The Sequence Radar #849: Last Week in AI: OpenAI Ships Agents, xAI Eyes Cursor, DeepSeek and Kimi Advance]])
- Long-context capability reduces some retrieval pressure but does not remove the need for good state management. (`4c98eb43cdd8` · supporting · key_points[0]; [[sources/the-sequence-radar-849-last-week-in-ai-openai-ships-agents-xai-eyes-cursor-deepseek-and-kimi-advance-01kq4r8j0majmt8av52cng4zw0|The Sequence Radar #849: Last Week in AI: OpenAI Ships Agents, xAI Eyes Cursor, DeepSeek and Kimi Advance]])
- Persistent memory and selective summarization are often more important than simply increasing token windows. (`9385e793cc3b` · supporting · key_points[1]; [[sources/the-sequence-radar-849-last-week-in-ai-openai-ships-agents-xai-eyes-cursor-deepseek-and-kimi-advance-01kq4r8j0majmt8av52cng4zw0|The Sequence Radar #849: Last Week in AI: OpenAI Ships Agents, xAI Eyes Cursor, DeepSeek and Kimi Advance]])
- Context should be treated as a managed resource because too much irrelevant state can degrade execution quality. (`ba786a8bd83d` · supporting · key_points[2]; [[sources/the-sequence-radar-849-last-week-in-ai-openai-ships-agents-xai-eyes-cursor-deepseek-and-kimi-advance-01kq4r8j0majmt8av52cng4zw0|The Sequence Radar #849: Last Week in AI: OpenAI Ships Agents, xAI Eyes Cursor, DeepSeek and Kimi Advance]])
- A frontier model is no longer just a model. It is a runtime. It is the intelligence layer inside coding environments, research workflows, enterprise assistants, and autonomous systems. (`fdedfdb3d5c4` · supporting · supporting_snippet; [[sources/the-sequence-radar-849-last-week-in-ai-openai-ships-agents-xai-eyes-cursor-deepseek-and-kimi-advance-01kq4r8j0majmt8av52cng4zw0|The Sequence Radar #849: Last Week in AI: OpenAI Ships Agents, xAI Eyes Cursor, DeepSeek and Kimi Advance]])

### This Open-Source App Turns Your Documents Into a Self-Building Wiki (2026-05-08)

- Context engineering is the practice of shaping what information a model sees so it can do a task reliably. Good context design includes scope statements, explicit source boundaries, and the right supporting material for the job. In document workflows, this often matters more than prompt wording because the model's output quality depends on what it is allowed to inspect. Clear context reduces wasted inference on irrelevant material and helps keep the output aligned with the user's actual goal. (`54f990cce8d8` · neutral · knowledge_summary; [[sources/this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g|This Open-Source App Turns Your Documents Into a Self-Building Wiki]])
- Use a purpose file or equivalent scope document to filter aggressively before generation so the model spends its capacity on the right evidence. (`9f5f8866e127` · neutral · operational_insight; [[sources/this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g|This Open-Source App Turns Your Documents Into a Self-Building Wiki]])
- Context engineering is a durable operational skill for assistants that work over private documents, tools, or workflows. It directly affects answer quality, cost, and how much irrelevant material the model carries into a session. (`32cc36284987` · neutral · relevance_note; [[sources/this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g|This Open-Source App Turns Your Documents Into a Self-Building Wiki]])
- A scope file can outperform vague prompting by defining what counts as relevant. (`1da7837f60dd` · supporting · key_points[0]; [[sources/this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g|This Open-Source App Turns Your Documents Into a Self-Building Wiki]])
- Filtering early reduces noise and contradictory over-extraction. (`ae67adff50cc` · supporting · key_points[1]; [[sources/this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g|This Open-Source App Turns Your Documents Into a Self-Building Wiki]])
- Context should include both the immediate document and the existing knowledge base when compounding matters. (`56f7a6c67c3f` · supporting · key_points[2]; [[sources/this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g|This Open-Source App Turns Your Documents Into a Self-Building Wiki]])
- With a purpose file that says 'I'm specifically interested in regulatory frameworks for frontier model deployment in the EU,' the AI filters aggressively. It knows what to ignore. (`18705e687f9d` · supporting · supporting_snippet; [[sources/this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g|This Open-Source App Turns Your Documents Into a Self-Building Wiki]])

## Contradictions / tensions

No contradictions captured in current sources.

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
