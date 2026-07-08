---
title: Token-Efficient Agent Instructions
slug: token-efficient-agent-instructions
entity_id: topic:token-efficient-agent-instructions
category: topic
tags:
- agent-systems
- ai-engineering
- context-engineering
- runtime-systems
first_seen: '2026-03-25'
last_seen: '2026-04-25'
source_count: 2
evidence_count: 15
source_ids:
- how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn
- i-spent-6-months-tuning-claude-code-here-s-the-exact-setup-that-finally-worked-01kr4358p7t4vfwjd4r6xqdmkj
value_level: high
confidence: 0.895
synthesis_state: stage1-placeholder
---

# Token-Efficient Agent Instructions

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Token-efficient agent instructions keep the always-loaded instruction set small and defer detail until the system knows it is relevant. This is a practical design pattern for agents that must support many workflows without wasting context on unused material. The pattern typically uses compact metadata or routing cues up front, then expands into deeper instructions only on demand. It is especially valuable when instruction sets accumulate over time and need to stay readable. The result is a more scalable way to encode behavior than repeatedly pasting long prompts into chat.

## Key Points

- Load only brief metadata at startup and expand instructions on demand.
- Keep the main instructions concise and move deep references into separate files.
- This pattern scales better than embedding every rule into every conversation.
- Short root instructions are more reusable than long prose because they behave like a high-signal cache.
- Scoped rules are cheaper than universal rules when the convention only matters in part of a repository.
- Behavioral rules are better than vague advice because the agent can follow them deterministically.
- Token overhead compounds across long sessions, so instruction size is an operational cost, not just a style choice.

## Operational Insight

Use short discovery metadata and load the detailed procedure only after a request matches. That preserves context for the conversation itself and makes larger skill libraries more workable.

## Evidence / supporting sources

### How to build Claude Skills 2.0 Better than 99% of People (2026-03-25)

- Token-efficient agent instructions keep the always-loaded instruction set small and defer detail until the system knows it is relevant. This is a practical design pattern for agents that must support many workflows without wasting context on unused material. The pattern typically uses compact metadata or routing cues up front, then expands into deeper instructions only on demand. It is especially valuable when instruction sets accumulate over time and need to stay readable. The result is a more scalable way to encode behavior than repeatedly pasting long prompts into chat. (`de8ed7dc7514` · neutral · knowledge_summary; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])
- Use short discovery metadata and load the detailed procedure only after a request matches. That preserves context for the conversation itself and makes larger skill libraries more workable. (`7e0128ad00ad` · neutral · operational_insight; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])
- This matters for AI systems that must juggle many reusable workflows, because context budget is a real operational constraint. The pattern helps teams keep instructions modular and reduces the chance that unused detail crowds out task-specific reasoning. (`855e7d912bc1` · neutral · relevance_note; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])
- Load only brief metadata at startup and expand instructions on demand. (`058f5db242f7` · supporting · key_points[0]; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])
- Keep the main instructions concise and move deep references into separate files. (`2e7aa3db1688` · supporting · key_points[1]; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])
- This pattern scales better than embedding every rule into every conversation. (`e9964ed0ac06` · supporting · key_points[2]; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])
- "The detailed instructions for a Skill are only displayed in the context window when it is triggered." (`a2369f658dc5` · supporting · supporting_snippet; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])

### I Spent 6 Months Tuning Claude Code. Here’s the Exact Setup That Finally Worked. (2026-04-25)

- Agent instructions are most durable when they are short, imperative, and scoped to behavior that actually changes outcomes. Large root files waste context and degrade responsiveness because every session must load them, while short path-scoped files load only when relevant. The useful unit is not explanatory prose but a rule that narrows action, such as a function length limit, a citation contract, or a test restriction. This keeps the agent’s ambient context stable and leaves more room for task-specific reasoning and tool output. (`be546647c813` · neutral · knowledge_summary; [[sources/i-spent-6-months-tuning-claude-code-here-s-the-exact-setup-that-finally-worked-01kr4358p7t4vfwjd4r6xqdmkj|I Spent 6 Months Tuning Claude Code. Here’s the Exact Setup That Finally Worked.]])
- Treat instructions as an operational cache, not a documentation dump. Put only behavior-changing rules in always-on memory, and move everything else into scoped files or triggered workflows. That makes long-running agent work less fragile and easier to keep consistent across sessions. (`2022cc80b5f4` · neutral · operational_insight; [[sources/i-spent-6-months-tuning-claude-code-here-s-the-exact-setup-that-finally-worked-01kr4358p7t4vfwjd4r6xqdmkj|I Spent 6 Months Tuning Claude Code. Here’s the Exact Setup That Finally Worked.]])
- This is durable because prompt budgets and context limits remain a core constraint in agentic systems. The same principle applies to support bots, code agents, and internal assistants: the less irrelevant instruction text they carry, the more reliable their behavior tends to be. (`883625fc9e4a` · neutral · relevance_note; [[sources/i-spent-6-months-tuning-claude-code-here-s-the-exact-setup-that-finally-worked-01kr4358p7t4vfwjd4r6xqdmkj|I Spent 6 Months Tuning Claude Code. Here’s the Exact Setup That Finally Worked.]])
- Short root instructions are more reusable than long prose because they behave like a high-signal cache. (`a6234cc4a381` · supporting · key_points[0]; [[sources/i-spent-6-months-tuning-claude-code-here-s-the-exact-setup-that-finally-worked-01kr4358p7t4vfwjd4r6xqdmkj|I Spent 6 Months Tuning Claude Code. Here’s the Exact Setup That Finally Worked.]])
- Scoped rules are cheaper than universal rules when the convention only matters in part of a repository. (`4950a39115d8` · supporting · key_points[1]; [[sources/i-spent-6-months-tuning-claude-code-here-s-the-exact-setup-that-finally-worked-01kr4358p7t4vfwjd4r6xqdmkj|I Spent 6 Months Tuning Claude Code. Here’s the Exact Setup That Finally Worked.]])
- Behavioral rules are better than vague advice because the agent can follow them deterministically. (`eb0f5bb0b49e` · supporting · key_points[2]; [[sources/i-spent-6-months-tuning-claude-code-here-s-the-exact-setup-that-finally-worked-01kr4358p7t4vfwjd4r6xqdmkj|I Spent 6 Months Tuning Claude Code. Here’s the Exact Setup That Finally Worked.]])
- Token overhead compounds across long sessions, so instruction size is an operational cost, not just a style choice. (`836b6ab01230` · supporting · key_points[3]; [[sources/i-spent-6-months-tuning-claude-code-here-s-the-exact-setup-that-finally-worked-01kr4358p7t4vfwjd4r6xqdmkj|I Spent 6 Months Tuning Claude Code. Here’s the Exact Setup That Finally Worked.]])
- "Keep the file under 200 lines. Keep it imperative. Do not write descriptive suggestions like ‘write clean code’. Write literal rules like ‘all functions must have TypeScript type annotations’. Every line must actually change behavior." (`51bfcad8c786` · supporting · supporting_snippet; [[sources/i-spent-6-months-tuning-claude-code-here-s-the-exact-setup-that-finally-worked-01kr4358p7t4vfwjd4r6xqdmkj|I Spent 6 Months Tuning Claude Code. Here’s the Exact Setup That Finally Worked.]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- [[topics/file-grammar-skills-for-ai|File Grammar Skills for AI]]
- [[topics/agent-workspace-layering|Agent Workspace Layering]]
- [[topics/harness-engineering|Harness Engineering]]

## Sources

- [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]]
- [[sources/i-spent-6-months-tuning-claude-code-here-s-the-exact-setup-that-finally-worked-01kr4358p7t4vfwjd4r6xqdmkj|I Spent 6 Months Tuning Claude Code. Here’s the Exact Setup That Finally Worked.]]
