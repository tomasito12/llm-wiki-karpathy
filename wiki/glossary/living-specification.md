---
title: Living Specification
slug: living-specification
entity_id: glossary:living-specification
category: glossary
tags:
- agent-systems
- context-engineering
first_seen: '2026-04-30'
last_seen: '2026-04-30'
source_count: 1
evidence_count: 4
source_ids:
- spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w
value_level: high
confidence: 0.9
synthesis_state: stage1-placeholder
---

# Living Specification

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
A living specification is a machine-readable project artifact that stays aligned with the codebase as the system evolves. It is updated bidirectionally from implementation and operational feedback rather than frozen before delivery.

## Relevance Note

This is operationally important wherever AI agents generate or modify code repeatedly, because the spec becomes the durable memory for design intent. It also supports auditability and coordinated multi-agent work when multiple systems need the same source of truth.

## Evidence / supporting sources

### Spec Driven Development — Three Maturity Levels Every AI Team Should Know (2026-04-30)

- A living specification is more than documentation. It acts as a contract, a planning aid, a test source, and a reference that can change when implementation reveals new edge cases. The key difference from static docs is that it remains in the repository and is revised as part of normal development. That makes it useful for teams that want AI tools to keep following the same architectural boundaries across sessions. (`3d0dfdfd9596` · neutral · extended_explanation; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])
- A living specification is a machine-readable project artifact that stays aligned with the codebase as the system evolves. It is updated bidirectionally from implementation and operational feedback rather than frozen before delivery. (`a7e6a08132e7` · neutral · proposed_definition; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])
- This is operationally important wherever AI agents generate or modify code repeatedly, because the spec becomes the durable memory for design intent. It also supports auditability and coordinated multi-agent work when multiple systems need the same source of truth. (`395d6d22fb8b` · neutral · relevance_note; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])
- “Versioned next to code in the repo … Bidirectional updates … Machine-readable format … Feedback loop from production” (`91cfcdd95d05` · supporting · supporting_snippet; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- [[glossary/specification-drift|Specification Drift]]
- [[glossary/behavior-driven-development|Behavior-Driven Development]]

## Sources

- [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]]
