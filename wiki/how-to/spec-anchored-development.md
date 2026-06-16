---
title: Spec Anchored Development
slug: spec-anchored-development
entity_id: how_to:spec-anchored-development
category: how-to
tags:
- ai-engineering
- context-engineering
- workflow-design
first_seen: '2026-04-30'
last_seen: '2026-04-30'
source_count: 1
evidence_count: 12
source_ids:
- spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w
value_level: high
confidence: 0.91
synthesis_state: stage1-placeholder
---

# Spec Anchored Development

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
This is a workflow for teams that use AI coding tools and want the model to keep following the same architectural rules after the first feature ships. The problem is that chat instructions and one-time prompts decay, so later edits can drift away from the original design. A persistent specification gives the agent a stable contract to work from on each change. It also makes it easier for teams to revise the rules when real implementation details appear.

## Caveats

This approach still requires humans to maintain the specification, so it does not remove the work of keeping intent current. It also becomes brittle if the spec starts dictating implementation details instead of boundaries and goals.

## Implementation Steps

- Move the specification into a repository file that sits next to the code.
- Write the specification in a machine-readable format such as Markdown, YAML, or structured plain text.
- Update the specification whenever implementation reveals something the original version missed.
- Feed incidents, performance metrics, and user behavior back into the spec.
- Use the spec as the reference point for future modifications.

## Prerequisites

- An existing code repository.
- A team willing to edit the spec as part of normal development.
- AI coding tools that can read repository context.

## Related Howtos

- Commit-Driven Documentation Sync
- Agent-Maintained Knowledge Bases

## Evidence / supporting sources

### Spec Driven Development — Three Maturity Levels Every AI Team Should Know (2026-04-30)

- Start by moving the important rules into a file in the repository instead of leaving them in conversation history. Keep that file machine-readable and update it whenever implementation reveals a new edge case or architectural decision. Treat the spec as the source of truth for future changes, not as a one-time prompt. Add feedback from incidents, metrics, and user behavior so the document stays useful after the feature ships. (`822da4be7959` · neutral · answer_summary; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])
- Move the specification into a repository file that sits next to the code. (`91095b0d09c6` · neutral · implementation_steps[0]; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])
- Write the specification in a machine-readable format such as Markdown, YAML, or structured plain text. (`d2902ce9479d` · neutral · implementation_steps[1]; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])
- Update the specification whenever implementation reveals something the original version missed. (`8d9832ba2cd3` · neutral · implementation_steps[2]; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])
- Feed incidents, performance metrics, and user behavior back into the spec. (`f3bdcdb6829a` · neutral · implementation_steps[3]; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])
- Use the spec as the reference point for future modifications. (`0dd267bd12fd` · neutral · implementation_steps[4]; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])
- An existing code repository. (`b5df5b6cd2e1` · neutral · prerequisites[0]; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])
- A team willing to edit the spec as part of normal development. (`0e68423c5625` · neutral · prerequisites[1]; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])
- AI coding tools that can read repository context. (`c76758fcadcc` · neutral · prerequisites[2]; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])
- This is a workflow for teams that use AI coding tools and want the model to keep following the same architectural rules after the first feature ships. The problem is that chat instructions and one-time prompts decay, so later edits can drift away from the original design. A persistent specification gives the agent a stable contract to work from on each change. It also makes it easier for teams to revise the rules when real implementation details appear. (`02164b8d7ed2` · neutral · what_and_problem; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])
- “At the spec-anchored level, the specification isn’t abandoned after implementation — it lives alongside the code, evolves with it, and serves as the source of truth for every modification.” (`c572ab87f76b` · supporting · supporting_snippet; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])
- This approach still requires humans to maintain the specification, so it does not remove the work of keeping intent current. It also becomes brittle if the spec starts dictating implementation details instead of boundaries and goals. (`d96d5bf0ab25` · uncertainty · caveats; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])

## Contradictions / tensions

- This approach still requires humans to maintain the specification, so it does not remove the work of keeping intent current. It also becomes brittle if the spec starts dictating implementation details instead of boundaries and goals. (uncertainty; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])

## Related pages

- Agent-Maintained Knowledge Bases
- Commit-Driven Documentation Sync

## Sources

- [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]]
