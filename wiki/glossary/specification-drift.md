---
title: Specification Drift
slug: specification-drift
entity_id: glossary:specification-drift
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
confidence: 0.93
synthesis_state: stage1-placeholder
---

# Specification Drift

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Specification drift is the gradual divergence between intended behavior and the system actually produced over time. It happens when the requirements or constraints guiding implementation are not kept current, so later changes follow local correctness while losing the original design intent.

## Related Terms

- Behavior-Driven Development
- Harness

## Relevance Note

This matters for AI-assisted development, agent workflows, and service automation because persistent systems need stable constraints across many edits and sessions. When the spec is not kept current, later changes tend to erode architecture, tests, and policy boundaries.

## Evidence / supporting sources

### Spec Driven Development — Three Maturity Levels Every AI Team Should Know (2026-04-30)

- In software and agent workflows, drift often shows up after repeated modifications, especially when the guiding instructions live only in chat or informal notes. The system may still work for the latest request, but older architectural choices stop being respected because they are no longer visible at generation time. Keeping the specification versioned and updated alongside the code helps reduce this problem. It is especially important in AI-assisted development because the agent does not retain durable project memory across sessions. (`fa45f42badd9` · neutral · extended_explanation; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])
- Specification drift is the gradual divergence between intended behavior and the system actually produced over time. It happens when the requirements or constraints guiding implementation are not kept current, so later changes follow local correctness while losing the original design intent. (`85e034905ecc` · neutral · proposed_definition; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])
- This matters for AI-assisted development, agent workflows, and service automation because persistent systems need stable constraints across many edits and sessions. When the spec is not kept current, later changes tend to erode architecture, tests, and policy boundaries. (`a1777fe4ead7` · neutral · relevance_note; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])
- “specification drift” — the phenomenon where an AI agent gradually diverges from the developer’s intent because that intent was never formalized in a file available at the moment of code generation. (`1dc47a7de18d` · supporting · supporting_snippet; [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- Behavior-Driven Development
- Harness

## Sources

- [[sources/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w|Spec Driven Development — Three Maturity Levels Every AI Team Should Know]]
