---
title: Agent Specification Bidirectionality
slug: agent-specification-bidirectionality
entity_id: topic:agent-specification-bidirectionality
category: topic
tags:
- agent-orchestration
- agent-systems
- verification-systems
first_seen: '2026-04-30'
last_seen: '2026-04-30'
source_count: 1
evidence_count: 8
source_ids:
- spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w
value_level: high
confidence: 0.91
synthesis_state: stage1-placeholder
---

# Agent Specification Bidirectionality

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Bidirectional specification means implementation updates the spec as well as the spec guiding implementation. This closes the loop that otherwise causes requirements to rot after the first delivery. The pattern is useful for any AI-supported workflow where changes happen over multiple sessions and the original prompt will not be remembered. It also supports shared understanding across humans and multiple agents because the current contract is kept in one place.

## Key Points

- Unidirectional specs decay after delivery.
- Implementation feedback is part of the spec lifecycle, not an exception.
- Shared living specs help multiple agents avoid diverging from each other.
- This pattern is distinct from waterfall because it does not freeze requirements permanently.

## Operational Insight

If the spec never gets revised from implementation feedback, it is only a prompt with better formatting.

## Evidence / supporting sources

### Spec Driven Development — Three Maturity Levels Every AI Team Should Know (2026-04-30)

- Bidirectional specification means implementation updates the spec as well as the spec guiding implementation. This closes the loop that otherwise causes requirements to rot after the first delivery. The pattern is useful for any AI-supported workflow where changes happen over multiple sessions and the original prompt will not be remembered. It also supports shared understanding across humans and multiple agents because the current contract is kept in one place. (`beb31ab5e10f` · neutral · knowledge_summary; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])
- If the spec never gets revised from implementation feedback, it is only a prompt with better formatting. (`863148460a63` · neutral · operational_insight; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])
- This matters for recurring software work, agent orchestration, and service automation because systems fail when the current state and the intended state diverge. Bidirectional specs reduce that gap and make maintenance more predictable. (`e6e654825506` · neutral · relevance_note; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])
- Unidirectional specs decay after delivery. (`5bcebacb1b1c` · supporting · key_points[0]; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])
- Implementation feedback is part of the spec lifecycle, not an exception. (`b93ada9ea3c3` · supporting · key_points[1]; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])
- Shared living specs help multiple agents avoid diverging from each other. (`0014022c8405` · supporting · key_points[2]; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])
- This pattern is distinct from waterfall because it does not freeze requirements permanently. (`3ed9f86d65ea` · supporting · key_points[3]; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])
- “Bidirectional updates — when implementation reveals something the spec didn’t anticipate, the specification is updated.” (`f2a07b9fee30` · supporting · supporting_snippet; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- [[topics/structured-specification-for-agentic-development|Structured Specification for Agentic Development]]

## Sources

- [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]]
