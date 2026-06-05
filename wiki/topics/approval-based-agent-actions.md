---
title: Approval-Based Agent Actions
slug: approval-based-agent-actions
entity_id: topic:approval-based-agent-actions
category: topic
tags:
- agent-systems
- auditability
- human-ai-workflows
- support-automation
- workflow-design
first_seen: '2026-05-15'
last_seen: '2026-05-15'
source_count: 1
evidence_count: 8
source_ids:
- operator-a-look-under-the-hood-01krmvv5hry22g6cxvat4xzge0
value_level: high
confidence: 0.93
synthesis_state: stage1-placeholder
---

# Approval-Based Agent Actions

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
When an agent can change live systems, the safest pattern is to route changes through a human review step before anything is applied. The agent should present a structured diff or proposal rather than silently executing write operations. This preserves human oversight while still letting the agent do the drafting and pre-work. The pattern is especially important when mistakes are costly, hard to detect, or difficult to roll back.

## Key Points

- Reviewable diffs provide a precise human checkpoint for high-stakes actions.
- Accept/reject/refine workflows preserve human authority without removing agent leverage.
- Safe write actions are more demanding than read-only analysis because they affect live systems.
- Auditable proposals support governance and incident review after changes are applied.

## Operational Insight

Treat write actions as proposals first and execution second. In production support systems, a reviewable diff is often the difference between useful automation and an unsafe autonomous system.

## Evidence / supporting sources

### Operator: A look under the hood (2026-05-15)

- When an agent can change live systems, the safest pattern is to route changes through a human review step before anything is applied. The agent should present a structured diff or proposal rather than silently executing write operations. This preserves human oversight while still letting the agent do the drafting and pre-work. The pattern is especially important when mistakes are costly, hard to detect, or difficult to roll back. (`2341fabafff4` · neutral · knowledge_summary; [[sources/operator-a-look-under-the-hood-01krmvv5hry22g6cxvat4xzge0|Operator: A look under the hood]])
- Treat write actions as proposals first and execution second. In production support systems, a reviewable diff is often the difference between useful automation and an unsafe autonomous system. (`260ba8dc4d71` · neutral · operational_insight; [[sources/operator-a-look-under-the-hood-01krmvv5hry22g6cxvat4xzge0|Operator: A look under the hood]])
- This is a durable control pattern for enterprise agents that act on knowledge bases, support workflows, or configuration. It reduces blast radius by turning automation into a supervised workflow, which is often easier to deploy than full autonomy. (`718d9bdd5e0c` · neutral · relevance_note; [[sources/operator-a-look-under-the-hood-01krmvv5hry22g6cxvat4xzge0|Operator: A look under the hood]])
- Reviewable diffs provide a precise human checkpoint for high-stakes actions. (`1555e8526965` · supporting · key_points[0]; [[sources/operator-a-look-under-the-hood-01krmvv5hry22g6cxvat4xzge0|Operator: A look under the hood]])
- Accept/reject/refine workflows preserve human authority without removing agent leverage. (`45f4afc7a8e8` · supporting · key_points[1]; [[sources/operator-a-look-under-the-hood-01krmvv5hry22g6cxvat4xzge0|Operator: A look under the hood]])
- Safe write actions are more demanding than read-only analysis because they affect live systems. (`828573f6dd72` · supporting · key_points[2]; [[sources/operator-a-look-under-the-hood-01krmvv5hry22g6cxvat4xzge0|Operator: A look under the hood]])
- Auditable proposals support governance and incident review after changes are applied. (`2e0688a7cb5b` · supporting · key_points[3]; [[sources/operator-a-look-under-the-hood-01krmvv5hry22g6cxvat4xzge0|Operator: A look under the hood]])
- "To prevent this, we built a robust proposal system, whereby every change Operator suggests is presented as a reviewable diff. You see exactly what will change before anything is applied, with the option to accept, reject, or refine." (`39ecb7bb24af` · supporting · supporting_snippet; [[sources/operator-a-look-under-the-hood-01krmvv5hry22g6cxvat4xzge0|Operator: A look under the hood]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

No related pages captured.

## Sources

- [[sources/operator-a-look-under-the-hood-01krmvv5hry22g6cxvat4xzge0|Operator: A look under the hood]]
