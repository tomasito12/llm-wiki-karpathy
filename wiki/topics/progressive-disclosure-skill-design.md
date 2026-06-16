---
title: Progressive Disclosure in Skill Design
slug: progressive-disclosure-skill-design
entity_id: topic:progressive-disclosure-skill-design
category: topic
tags:
- agent-orchestration
- agent-systems
- context-engineering
- runtime-architecture
- workflow-design
first_seen: '2026-01-26'
last_seen: '2026-04-29'
source_count: 3
evidence_count: 24
source_ids:
- ai-agent-skills-explained-simply-01kr43s6p07ryvwqmstm9thx41
- how-we-built-an-ai-second-brain-for-60k-knowledge-workers-01kqz014gcexykw32fheswwzd3
- the-complete-guide-to-building-skills-for-claude-01krv8epdjta6664ek10fvp7tz
value_level: high
confidence: 0.9366666666666666
synthesis_state: stage1-placeholder
---

# Progressive Disclosure in Skill Design

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Progressive disclosure is a three-layer instruction pattern for keeping agent behavior efficient while still allowing specialized guidance. A minimal top layer decides when a capability should load, a fuller middle layer carries the main instructions, and deeper linked files hold details that are only fetched when needed. This structure reduces context cost and helps large instruction sets remain usable. It is especially valuable when the agent must juggle multiple skills or when the workflow has reference material that would be too expensive to load all at once.

## Examples

“Lean context up front, deeper detail on demand.”

## Key Points

- The trigger metadata is part of the runtime design, not a separate admin detail.
- Loaded-on-demand references keep specialized knowledge available without forcing it into every prompt.
- Multiple skills can coexist if each one is scoped cleanly.
- Token efficiency is a first-order design goal, not an afterthought.
- Load only skill name and description first to keep startup context small.
- Use the skill description as the trigger for deciding when to expand into full instructions.
- Delay scripts, references, and assets until the task actually needs them.
- The routing step depends on the model's own reasoning, so metadata quality matters.
- Start with a short root summary instead of loading all documents into every session.
- Open project-level detail only when the conversation or task actually needs it.
- The source explicitly links this pattern to better output quality and lower context waste.
- Skills can use the same idea by exposing a short description until the agent invokes them.

## Operational Insight

Treat the load trigger as part of the design, not just metadata. The skill should encode enough at the top level for routing, but defer everything else until the model has decided the task is relevant.

## Related Topics

- file-native-ai-workflows
- agent-workspace-layering

## Evidence / supporting sources

### AI Agent Skills Explained Simply (2026-04-24)

- Progressive disclosure in agent systems means loading only lightweight metadata first, then pulling in full instructions and optional resources only when a task matches. This reduces context waste and lets many skills coexist without overwhelming the model at startup. The pattern is especially useful when the agent must choose among many modular capabilities and needs a cheap first-pass index before expanding detail. Its practical value is in balancing scale, token efficiency, and relevance selection in agent runtimes. (`67b706493f70` · neutral · knowledge_summary; [[sources/ai-agent-skills-explained-simply-01kr43s6p07ryvwqmstm9thx41|AI Agent Skills Explained Simply]])
- Treat skill metadata as a routing layer and reserve full instructions for the point of need. The quality of the short description becomes a critical control surface because it determines whether the model expands the right skill at the right time. (`1cdb0ef3a350` · neutral · operational_insight; [[sources/ai-agent-skills-explained-simply-01kr43s6p07ryvwqmstm9thx41|AI Agent Skills Explained Simply]])
- This matters for agent runtimes because modular capabilities scale better when the system can route cheaply before expanding detail. In conversational AI and service automation, it supports many reusable task modules without forcing every request to carry full process instructions. (`f9477c367d84` · neutral · relevance_note; [[sources/ai-agent-skills-explained-simply-01kr43s6p07ryvwqmstm9thx41|AI Agent Skills Explained Simply]])
- Load only skill name and description first to keep startup context small. (`ff3cc4f2cb35` · supporting · key_points[0]; [[sources/ai-agent-skills-explained-simply-01kr43s6p07ryvwqmstm9thx41|AI Agent Skills Explained Simply]])
- Use the skill description as the trigger for deciding when to expand into full instructions. (`2ce692b5a1f1` · supporting · key_points[1]; [[sources/ai-agent-skills-explained-simply-01kr43s6p07ryvwqmstm9thx41|AI Agent Skills Explained Simply]])
- Delay scripts, references, and assets until the task actually needs them. (`559ed18b9cbb` · supporting · key_points[2]; [[sources/ai-agent-skills-explained-simply-01kr43s6p07ryvwqmstm9thx41|AI Agent Skills Explained Simply]])
- The routing step depends on the model's own reasoning, so metadata quality matters. (`0e21d86002de` · supporting · key_points[3]; [[sources/ai-agent-skills-explained-simply-01kr43s6p07ryvwqmstm9thx41|AI Agent Skills Explained Simply]])
- "How Progressive Disclosure Works
Here’s where it gets interesting. What if an agent has hundreds of skills? Loading all of them into memory would use up every token before anyone asks a question.
So skills use progressive disclosure in three tiers.
Tier One: Metadata Only
The agent loads just the name and description from each skill. That’s a few tokens per skill. Even with a hundred skills installed, the overhead won’t fill the context window.
This is essentially a table of contents." (`a2fdcc2e731c` · supporting · supporting_snippet; [[sources/ai-agent-skills-explained-simply-01kr43s6p07ryvwqmstm9thx41|AI Agent Skills Explained Simply]])

### How We Built an AI Second Brain for 60K Knowledge Workers (2026-04-29)

- “Lean context up front, deeper detail on demand.” (`9d1ec02828dc` · neutral · examples; [[sources/how-we-built-an-ai-second-brain-for-60k-knowledge-workers-01kqz014gcexykw32fheswwzd3|How We Built an AI Second Brain for 60K Knowledge Workers]])
- Progressive disclosure is a workflow design pattern where an agent starts with a lean summary and only loads deeper detail when the task requires it. This is useful when context windows are finite and when indiscriminate loading hurts quality or wastes tokens. In practice, the agent sees a short description first, then opens specific workflows, folders, or instructions as needed. The pattern works both for workspace structure and for reusable skills. (`823432524945` · neutral · knowledge_summary; [[sources/how-we-built-an-ai-second-brain-for-60k-knowledge-workers-01kqz014gcexykw32fheswwzd3|How We Built an AI Second Brain for 60K Knowledge Workers]])
- Keep the first-pass context small and make deeper information discoverable on demand. This is a better default than feeding an agent every available file because it preserves budget and reduces distraction. (`80a7b4b838f3` · neutral · operational_insight; [[sources/how-we-built-an-ai-second-brain-for-60k-knowledge-workers-01kqz014gcexykw32fheswwzd3|How We Built an AI Second Brain for 60K Knowledge Workers]])
- This matters in agent orchestration, support automation, and coding workflows because too much context often makes systems slower, noisier, or harder to steer. Progressive disclosure gives a practical alternative to indiscriminate retrieval or prompt stuffing. It also fits service workflows where the first step should classify or route, and only the next step should open the full case history. (`2a67fe9cf2a4` · neutral · relevance_note; [[sources/how-we-built-an-ai-second-brain-for-60k-knowledge-workers-01kqz014gcexykw32fheswwzd3|How We Built an AI Second Brain for 60K Knowledge Workers]])
- Start with a short root summary instead of loading all documents into every session. (`c260c5a39df6` · supporting · key_points[0]; [[sources/how-we-built-an-ai-second-brain-for-60k-knowledge-workers-01kqz014gcexykw32fheswwzd3|How We Built an AI Second Brain for 60K Knowledge Workers]])
- Open project-level detail only when the conversation or task actually needs it. (`80c29b588a5f` · supporting · key_points[1]; [[sources/how-we-built-an-ai-second-brain-for-60k-knowledge-workers-01kqz014gcexykw32fheswwzd3|How We Built an AI Second Brain for 60K Knowledge Workers]])
- The source explicitly links this pattern to better output quality and lower context waste. (`b80a16879183` · supporting · key_points[2]; [[sources/how-we-built-an-ai-second-brain-for-60k-knowledge-workers-01kqz014gcexykw32fheswwzd3|How We Built an AI Second Brain for 60K Knowledge Workers]])
- Skills can use the same idea by exposing a short description until the agent invokes them. (`f336ae0ddb79` · supporting · key_points[3]; [[sources/how-we-built-an-ai-second-brain-for-60k-knowledge-workers-01kqz014gcexykw32fheswwzd3|How We Built an AI Second Brain for 60K Knowledge Workers]])

### The Complete Guide To Building Skills For Claude (2026-01-26)

- Progressive disclosure is a three-layer instruction pattern for keeping agent behavior efficient while still allowing specialized guidance. A minimal top layer decides when a capability should load, a fuller middle layer carries the main instructions, and deeper linked files hold details that are only fetched when needed. This structure reduces context cost and helps large instruction sets remain usable. It is especially valuable when the agent must juggle multiple skills or when the workflow has reference material that would be too expensive to load all at once. (`2e4a753f5ddb` · neutral · knowledge_summary; [[sources/the-complete-guide-to-building-skills-for-claude-01krv8epdjta6664ek10fvp7tz|The Complete Guide To Building Skills For Claude]])
- Treat the load trigger as part of the design, not just metadata. The skill should encode enough at the top level for routing, but defer everything else until the model has decided the task is relevant. (`56fceb710fab` · neutral · operational_insight; [[sources/the-complete-guide-to-building-skills-for-claude-01krv8epdjta6664ek10fvp7tz|The Complete Guide To Building Skills For Claude]])
- This is durable for AI systems that need to balance capability depth against context limits. It shows up in agent runtimes, tool routers, and workflow packs where routing accuracy and token efficiency both matter. The pattern is broadly useful for conversational agents that must carry specialized behaviors without bloating every request. (`2221c45aa1b5` · neutral · relevance_note; [[sources/the-complete-guide-to-building-skills-for-claude-01krv8epdjta6664ek10fvp7tz|The Complete Guide To Building Skills For Claude]])
- The trigger metadata is part of the runtime design, not a separate admin detail. (`541c5dfc6e8c` · supporting · key_points[0]; [[sources/the-complete-guide-to-building-skills-for-claude-01krv8epdjta6664ek10fvp7tz|The Complete Guide To Building Skills For Claude]])
- Loaded-on-demand references keep specialized knowledge available without forcing it into every prompt. (`3daad1512e9e` · supporting · key_points[1]; [[sources/the-complete-guide-to-building-skills-for-claude-01krv8epdjta6664ek10fvp7tz|The Complete Guide To Building Skills For Claude]])
- Multiple skills can coexist if each one is scoped cleanly. (`5cb7144715cc` · supporting · key_points[2]; [[sources/the-complete-guide-to-building-skills-for-claude-01krv8epdjta6664ek10fvp7tz|The Complete Guide To Building Skills For Claude]])
- Token efficiency is a first-order design goal, not an afterthought. (`be93db2f7af4` · supporting · key_points[3]; [[sources/the-complete-guide-to-building-skills-for-claude-01krv8epdjta6664ek10fvp7tz|The Complete Guide To Building Skills For Claude]])
- Skills use a three-level system: First level (YAML frontmatter): Always loaded in Claude's system prompt. Provides just enough information for Claude to know when each skill should be used without loading all of it into context. Second level (SKILL.md body): Loaded when Claude thinks the skill is relevant to the current task. Third level (Linked files): Additional files bundled within the skill directory that Claude can choose to navigate and discover only as needed. (`362fa4076eec` · supporting · supporting_snippet; [[sources/the-complete-guide-to-building-skills-for-claude-01krv8epdjta6664ek10fvp7tz|The Complete Guide To Building Skills For Claude]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- agent-workspace-layering
- file-native-ai-workflows

## Sources

- [[sources/ai-agent-skills-explained-simply-01kr43s6p07ryvwqmstm9thx41|AI Agent Skills Explained Simply]]
- [[sources/how-we-built-an-ai-second-brain-for-60k-knowledge-workers-01kqz014gcexykw32fheswwzd3|How We Built an AI Second Brain for 60K Knowledge Workers]]
- [[sources/the-complete-guide-to-building-skills-for-claude-01krv8epdjta6664ek10fvp7tz|The Complete Guide To Building Skills For Claude]]
