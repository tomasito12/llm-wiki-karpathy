---
title: Structured Specification for Agentic Development
slug: structured-specification-for-agentic-development
entity_id: topic:structured-specification-for-agentic-development
category: topic
tags:
- agent-systems
- ai-engineering
- coding-agents
- process-design
- software-engineering
- verification-systems
- workflow-design
first_seen: '2026-04-13'
last_seen: '2026-05-12'
source_count: 4
evidence_count: 34
source_ids:
- from-vibe-coding-to-spec-driven-development-01krkb186m11xe8rdxgc7wz89m
- sdd-writing-specifications-for-ai-bdd-as-the-missing-link-spec-driven-development-01kqz04y32hqhskkq6c3jh3esj
- spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w
- zeespec-how-to-write-a-complete-system-specification-for-ai-in-1-hour-01kqfz6p0jfhx9r1y4rd3x27sa
value_level: high
confidence: 0.945
synthesis_state: stage1-placeholder
---

# Structured Specification for Agentic Development

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Agentic systems benefit from explicit, structured specifications that enumerate constraints before implementation. A useful spec does more than describe features: it defines boundaries, permissions, timing, allowed states, and error behavior. This reduces ambiguity in systems where the model would otherwise fill gaps with guesses. The strongest specs treat omission as a defect because skipped decisions become implicit system behavior. This pattern is especially relevant when agents must behave predictably across teams, workflows, and failure cases.

## Key Points

- A spec should define what exists and what does not.
- Boundaries matter as much as features: where actions happen, where data can go, and where access is restricted.
- Timing questions expose triggers, retries, blocking conditions, and expiration rules.
- Role questions clarify who can create, update, delete, approve, or never act.
- Behavior questions should cover missing data, invalid input, errors, recovery, and consistency.
- Loose requirements documents leave too much implicit for an agent to infer safely.
- Over-detailed design documents collapse back into manual coding work.
- A behavior-level specification can sit between requirements and implementation without becoming code.
- The best spec artifact is one that humans can approve and machines can execute against.
- A spec should define WHAT and boundaries, not line-by-line HOW.
- Versioning the spec next to code matters because it preserves design intent in git history.
- Bidirectional updates matter because implementation reveals edge cases that should feed back into the spec.
- Machine-readable formats make the spec useful to both humans and agents.
- A spec can serve as contract, steering document, test oracle, and living document.
- Separate the specification from the implementation so the project can be steered without relying on chat history.
- Treat mission, tech stack, roadmap, feature specs, and validation as durable artifacts rather than one-off prompts.
- Use replanning explicitly when implementation uncovers mismatches between the initial plan and the real product need.
- Keep changes flowing through the agent so related documents stay consistent.

## Operational Insight

Use the specification process to surface hidden decisions early, especially around access control, data flow, retries, and irreversible actions. The value is not in longer documentation; it is in forcing the team to close every meaningful gap before the agent gets one.

## Evidence / supporting sources

### From Vibe Coding to Spec-Driven Development (2026-05-12)

- A durable AI-assisted development workflow starts with a written specification that separates intent, constraints, and architecture from implementation. The specification becomes the source of truth across chat sessions and agents, which reduces drift, forgotten reasoning, and inconsistent conventions. This approach works best when humans make the architectural decisions first and agents execute against those decisions. Replanning is part of the workflow, because real usage often exposes gaps that require the specification to be revised before more code is added. (`5417ef484c19` · neutral · knowledge_summary; [[sources/from-vibe-coding-to-spec-driven-development-01krkb186m11xe8rdxgc7wz89m|From Vibe Coding to Spec-Driven Development]])
- Keep project intent in repository-backed Markdown rather than in transient chat history so agents can be steered, reviewed, and audited against stable requirements. (`2a1ae4bb68de` · neutral · operational_insight; [[sources/from-vibe-coding-to-spec-driven-development-01krkb186m11xe8rdxgc7wz89m|From Vibe Coding to Spec-Driven Development]])
- This pattern matters whenever AI agents are used for software delivery, especially on larger or multi-session work where context loss creates rework. Repository-backed specifications make agent output easier to review, safer to change, and more transferable across contributors and tools. (`bc435e50096c` · neutral · relevance_note; [[sources/from-vibe-coding-to-spec-driven-development-01krkb186m11xe8rdxgc7wz89m|From Vibe Coding to Spec-Driven Development]])
- Separate the specification from the implementation so the project can be steered without relying on chat history. (`db69818ef6ea` · supporting · key_points[0]; [[sources/from-vibe-coding-to-spec-driven-development-01krkb186m11xe8rdxgc7wz89m|From Vibe Coding to Spec-Driven Development]])
- Treat mission, tech stack, roadmap, feature specs, and validation as durable artifacts rather than one-off prompts. (`7c443147324b` · supporting · key_points[1]; [[sources/from-vibe-coding-to-spec-driven-development-01krkb186m11xe8rdxgc7wz89m|From Vibe Coding to Spec-Driven Development]])
- Use replanning explicitly when implementation uncovers mismatches between the initial plan and the real product need. (`b1431078d82b` · supporting · key_points[2]; [[sources/from-vibe-coding-to-spec-driven-development-01krkb186m11xe8rdxgc7wz89m|From Vibe Coding to Spec-Driven Development]])
- Keep changes flowing through the agent so related documents stay consistent. (`04691d3f04aa` · supporting · key_points[3]; [[sources/from-vibe-coding-to-spec-driven-development-01krkb186m11xe8rdxgc7wz89m|From Vibe Coding to Spec-Driven Development]])
- "Instead of jumping straight into implementation, we start by doing the hard thinking ourselves: making architectural decisions, defining requirements, and documenting them in a structured markdown specification stored in the repository and updated alongside the project." (`bcd3f6da4254` · supporting · supporting_snippet; [[sources/from-vibe-coding-to-spec-driven-development-01krkb186m11xe8rdxgc7wz89m|From Vibe Coding to Spec-Driven Development]])

### SDD Writing Specifications for AI: BDD as the Missing Link — Spec-Driven Development (2026-04-30)

- When code is produced by an AI agent, the specification needs to be concrete enough to guide implementation but not so detailed that it becomes the implementation itself. A good spec for agentic workflows encodes behavior, boundary conditions, and expected outcomes in a form that can be reviewed by humans and consumed by machines. This reduces ambiguity, shrinks translation loss between product and engineering, and makes validation easier. The most durable versions of this pattern use shared artifacts that can drive both implementation and tests. (`95604f6f9c32` · neutral · knowledge_summary; [[sources/sdd-writing-specifications-for-ai-bdd-as-the-missing-link-spec-driven-development-01kqz04y32hqhskkq6c3jh3esj|SDD Writing Specifications for AI: BDD as the Missing Link — Spec-Driven Development]])
- Use a spec format that is precise at the behavior level and avoid forcing the agent to infer hidden business rules from long prose. The practical test is whether the same artifact can guide implementation, review, and verification without becoming code in disguise. (`421582cc24f8` · neutral · operational_insight; [[sources/sdd-writing-specifications-for-ai-bdd-as-the-missing-link-spec-driven-development-01kqz04y32hqhskkq6c3jh3esj|SDD Writing Specifications for AI: BDD as the Missing Link — Spec-Driven Development]])
- This matters long term because AI-assisted development changes the role of specs from passive documentation to active input for code generation, review, and test creation. Teams that get the spec layer right can reduce rework, tighten feedback loops, and make agent behavior more predictable. (`4296beb7213a` · neutral · relevance_note; [[sources/sdd-writing-specifications-for-ai-bdd-as-the-missing-link-spec-driven-development-01kqz04y32hqhskkq6c3jh3esj|SDD Writing Specifications for AI: BDD as the Missing Link — Spec-Driven Development]])
- Loose requirements documents leave too much implicit for an agent to infer safely. (`1d6de0cde3d7` · supporting · key_points[0]; [[sources/sdd-writing-specifications-for-ai-bdd-as-the-missing-link-spec-driven-development-01kqz04y32hqhskkq6c3jh3esj|SDD Writing Specifications for AI: BDD as the Missing Link — Spec-Driven Development]])
- Over-detailed design documents collapse back into manual coding work. (`5e1a1f8e1df2` · supporting · key_points[1]; [[sources/sdd-writing-specifications-for-ai-bdd-as-the-missing-link-spec-driven-development-01kqz04y32hqhskkq6c3jh3esj|SDD Writing Specifications for AI: BDD as the Missing Link — Spec-Driven Development]])
- A behavior-level specification can sit between requirements and implementation without becoming code. (`8134c55b87cb` · supporting · key_points[2]; [[sources/sdd-writing-specifications-for-ai-bdd-as-the-missing-link-spec-driven-development-01kqz04y32hqhskkq6c3jh3esj|SDD Writing Specifications for AI: BDD as the Missing Link — Spec-Driven Development]])
- The best spec artifact is one that humans can approve and machines can execute against. (`fbf271c811ae` · supporting · key_points[3]; [[sources/sdd-writing-specifications-for-ai-bdd-as-the-missing-link-spec-driven-development-01kqz04y32hqhskkq6c3jh3esj|SDD Writing Specifications for AI: BDD as the Missing Link — Spec-Driven Development]])
- “A specification stopped being an archival document and became an execution contract.” (`0df4fb339f67` · supporting · supporting_snippet; [[sources/sdd-writing-specifications-for-ai-bdd-as-the-missing-link-spec-driven-development-01kqz04y32hqhskkq6c3jh3esj|SDD Writing Specifications for AI: BDD as the Missing Link — Spec-Driven Development]])

### Spec Driven Development — Three Maturity Levels Every AI Team Should Know (2026-04-30)

- AI-assisted development works better when the system being built is governed by a structured specification rather than only by ad hoc prompts. The useful boundary is to specify what the system must do and which constraints it must respect, while leaving implementation details open to change. A strong spec can act as a contract, planning aid, test source, and living project memory. The practical difference is not whether a spec exists, but whether it stays versioned, readable, and tied to the codebase as the system evolves. (`759acc4e4db9` · neutral · knowledge_summary; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])
- For teams using coding agents, the highest leverage comes from making the spec durable and editable, not from making it longer. (`599559c2a55b` · neutral · operational_insight; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])
- This domain matters wherever AI tools are asked to generate, modify, or coordinate software repeatedly. The durable lesson is that structured specs reduce drift, improve reviewability, and make multi-session automation more reliable. (`8f141de86436` · neutral · relevance_note; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])
- A spec should define WHAT and boundaries, not line-by-line HOW. (`c5c75ef8d878` · supporting · key_points[0]; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])
- Versioning the spec next to code matters because it preserves design intent in git history. (`84eb87493554` · supporting · key_points[1]; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])
- Bidirectional updates matter because implementation reveals edge cases that should feed back into the spec. (`5f4ec0a1766b` · supporting · key_points[2]; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])
- Machine-readable formats make the spec useful to both humans and agents. (`b984c25656b1` · supporting · key_points[3]; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])
- A spec can serve as contract, steering document, test oracle, and living document. (`83e05661ee67` · supporting · key_points[4]; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])
- “Spec Driven Development is a maturity ladder — from CLAUDE.md (spec-first) through a living specification (spec-anchored) to code as a generated artifact (spec-as-source).” (`957322baddbe` · supporting · supporting_snippet; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])

### ZeeSpec: How to Write a Complete System Specification for AI in 1 Hour (2026-04-13)

- Agentic systems benefit from explicit, structured specifications that enumerate constraints before implementation. A useful spec does more than describe features: it defines boundaries, permissions, timing, allowed states, and error behavior. This reduces ambiguity in systems where the model would otherwise fill gaps with guesses. The strongest specs treat omission as a defect because skipped decisions become implicit system behavior. This pattern is especially relevant when agents must behave predictably across teams, workflows, and failure cases. (`a74c67e2afb5` · neutral · knowledge_summary; [[sources/zeespec-how-to-write-a-complete-system-specification-for-ai-in-1-hour-01kqfz6p0jfhx9r1y4rd3x27sa|ZeeSpec: How to Write a Complete System Specification for AI in 1 Hour]])
- Use the specification process to surface hidden decisions early, especially around access control, data flow, retries, and irreversible actions. The value is not in longer documentation; it is in forcing the team to close every meaningful gap before the agent gets one. (`edf230e4d7e9` · neutral · operational_insight; [[sources/zeespec-how-to-write-a-complete-system-specification-for-ai-in-1-hour-01kqfz6p0jfhx9r1y4rd3x27sa|ZeeSpec: How to Write a Complete System Specification for AI in 1 Hour]])
- This pattern remains useful for AI engineering as teams move from loose prompts to governed agent workflows. It is especially relevant in service automation, where predictable behavior, explicit handoffs, and failure handling matter more than fluent text generation. (`69c706c77766` · neutral · relevance_note; [[sources/zeespec-how-to-write-a-complete-system-specification-for-ai-in-1-hour-01kqfz6p0jfhx9r1y4rd3x27sa|ZeeSpec: How to Write a Complete System Specification for AI in 1 Hour]])
- A spec should define what exists and what does not. (`43a53262cede` · supporting · key_points[0]; [[sources/zeespec-how-to-write-a-complete-system-specification-for-ai-in-1-hour-01kqfz6p0jfhx9r1y4rd3x27sa|ZeeSpec: How to Write a Complete System Specification for AI in 1 Hour]])
- Boundaries matter as much as features: where actions happen, where data can go, and where access is restricted. (`e6bbb85640a2` · supporting · key_points[1]; [[sources/zeespec-how-to-write-a-complete-system-specification-for-ai-in-1-hour-01kqfz6p0jfhx9r1y4rd3x27sa|ZeeSpec: How to Write a Complete System Specification for AI in 1 Hour]])
- Timing questions expose triggers, retries, blocking conditions, and expiration rules. (`fa48b43ef36c` · supporting · key_points[2]; [[sources/zeespec-how-to-write-a-complete-system-specification-for-ai-in-1-hour-01kqfz6p0jfhx9r1y4rd3x27sa|ZeeSpec: How to Write a Complete System Specification for AI in 1 Hour]])
- Role questions clarify who can create, update, delete, approve, or never act. (`b46785d4e08c` · supporting · key_points[3]; [[sources/zeespec-how-to-write-a-complete-system-specification-for-ai-in-1-hour-01kqfz6p0jfhx9r1y4rd3x27sa|ZeeSpec: How to Write a Complete System Specification for AI in 1 Hour]])
- Behavior questions should cover missing data, invalid input, errors, recovery, and consistency. (`11a12f7d4923` · supporting · key_points[4]; [[sources/zeespec-how-to-write-a-complete-system-specification-for-ai-in-1-hour-01kqfz6p0jfhx9r1y4rd3x27sa|ZeeSpec: How to Write a Complete System Specification for AI in 1 Hour]])
- "It’s not documentation. It’s a constraint system. You answer 60 questions — one per minute — and at the end, you don’t have notes. You have a system where: nothing important is undefined nothing critical is assumed and AI has no room to guess" (`6c41e546b5e5` · supporting · supporting_snippet; [[sources/zeespec-how-to-write-a-complete-system-specification-for-ai-in-1-hour-01kqfz6p0jfhx9r1y4rd3x27sa|ZeeSpec: How to Write a Complete System Specification for AI in 1 Hour]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- [[topics/verification-loops-in-ai-workflows|Verification Loops in AI Workflows]]
- [[topics/agentic-coding-workflows|Agentic Coding Workflows]]

## Sources

- [[sources/from-vibe-coding-to-spec-driven-development-01krkb186m11xe8rdxgc7wz89m|From Vibe Coding to Spec-Driven Development]]
- [[sources/sdd-writing-specifications-for-ai-bdd-as-the-missing-link-spec-driven-development-01kqz04y32hqhskkq6c3jh3esj|SDD Writing Specifications for AI: BDD as the Missing Link — Spec-Driven Development]]
- [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]]
- [[sources/zeespec-how-to-write-a-complete-system-specification-for-ai-in-1-hour-01kqfz6p0jfhx9r1y4rd3x27sa|ZeeSpec: How to Write a Complete System Specification for AI in 1 Hour]]
