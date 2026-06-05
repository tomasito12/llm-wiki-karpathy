---
title: Progressive Disclosure in Skill Design
slug: progressive-disclosure-skill-design
entity_id: topic:progressive-disclosure-skill-design
category: topic
tags:
- agent-systems
- context-engineering
- runtime-architecture
first_seen: '2026-01-26'
last_seen: '2026-01-26'
source_count: 1
evidence_count: 8
source_ids:
- the-complete-guide-to-building-skills-for-claude-01krv8epdjta6664ek10fvp7tz
value_level: high
confidence: 0.95
synthesis_state: stage1-placeholder
---

# Progressive Disclosure in Skill Design

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Progressive disclosure is a three-layer instruction pattern for keeping agent behavior efficient while still allowing specialized guidance. A minimal top layer decides when a capability should load, a fuller middle layer carries the main instructions, and deeper linked files hold details that are only fetched when needed. This structure reduces context cost and helps large instruction sets remain usable. It is especially valuable when the agent must juggle multiple skills or when the workflow has reference material that would be too expensive to load all at once.

## Key Points

- The trigger metadata is part of the runtime design, not a separate admin detail.
- Loaded-on-demand references keep specialized knowledge available without forcing it into every prompt.
- Multiple skills can coexist if each one is scoped cleanly.
- Token efficiency is a first-order design goal, not an afterthought.

## Operational Insight

Treat the load trigger as part of the design, not just metadata. The skill should encode enough at the top level for routing, but defer everything else until the model has decided the task is relevant.

## Evidence / supporting sources

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

No related pages captured.

## Sources

- [[sources/the-complete-guide-to-building-skills-for-claude-01krv8epdjta6664ek10fvp7tz|The Complete Guide To Building Skills For Claude]]
