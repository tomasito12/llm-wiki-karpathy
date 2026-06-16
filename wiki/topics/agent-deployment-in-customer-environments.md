---
title: Agent Deployment in Customer Environments
slug: agent-deployment-in-customer-environments
entity_id: topic:agent-deployment-in-customer-environments
category: topic
tags:
- ai-engineering
- enterprise-workflows
- execution-environments
first_seen: '2026-05-20'
last_seen: '2026-05-20'
source_count: 1
evidence_count: 9
source_ids:
- forward-deployed-engineering-101-01kszj77y1z51yfaqzwmfknz7h
value_level: high
confidence: 0.94
synthesis_state: stage1-placeholder
---

# Agent Deployment in Customer Environments

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Production AI systems often need to be designed inside the customer environment, not just for it. The practical pattern is to observe real workflows, understand existing systems and constraints, and then fit automation into that environment with minimal disruption. This approach favors domain immersion, API layering, and small reversible changes over big-bang replacement. It is most useful when the system must interact with legacy infrastructure, non-technical stakeholders, or business processes that differ sharply across customers.

## Examples

The source describes this as being "on-site with a customer" and says to "build APIs over an existing data layer (SharePoint or databases) and place a model on top as an orchestrator."

## Key Points

- Observe the workflow in the real operating environment before proposing automation.
- Prefer layering models over existing systems through APIs rather than replacing core infrastructure.
- Treat existing enterprise systems as integration surfaces, not obstacles to be removed.
- Move cautiously when the workflow affects production operations or customer-facing work.

## Operational Insight

Treat the customer site or customer system as part of the product spec; the workflow context is not optional metadata, it is the design surface.

## Evidence / supporting sources

### Forward Deployed Engineering 101 (2026-05-20)

- The source describes this as being "on-site with a customer" and says to "build APIs over an existing data layer (SharePoint or databases) and place a model on top as an orchestrator." (`c2ddf77afb20` · neutral · examples; [[sources/forward-deployed-engineering-101-01kszj77y1z51yfaqzwmfknz7h|Forward Deployed Engineering 101]])
- Production AI systems often need to be designed inside the customer environment, not just for it. The practical pattern is to observe real workflows, understand existing systems and constraints, and then fit automation into that environment with minimal disruption. This approach favors domain immersion, API layering, and small reversible changes over big-bang replacement. It is most useful when the system must interact with legacy infrastructure, non-technical stakeholders, or business processes that differ sharply across customers. (`dd76c1ea2dcf` · neutral · knowledge_summary; [[sources/forward-deployed-engineering-101-01kszj77y1z51yfaqzwmfknz7h|Forward Deployed Engineering 101]])
- Treat the customer site or customer system as part of the product spec; the workflow context is not optional metadata, it is the design surface. (`5dfad1aa8826` · neutral · operational_insight; [[sources/forward-deployed-engineering-101-01kszj77y1z51yfaqzwmfknz7h|Forward Deployed Engineering 101]])
- This pattern matters whenever AI has to fit into messy enterprise workflows, especially service automation and internal ops. It keeps the focus on constraints, data access, and handoff points instead of assuming a generic model can be dropped into any stack. (`be58cecb2c60` · neutral · relevance_note; [[sources/forward-deployed-engineering-101-01kszj77y1z51yfaqzwmfknz7h|Forward Deployed Engineering 101]])
- Observe the workflow in the real operating environment before proposing automation. (`32805bdca0c2` · supporting · key_points[0]; [[sources/forward-deployed-engineering-101-01kszj77y1z51yfaqzwmfknz7h|Forward Deployed Engineering 101]])
- Prefer layering models over existing systems through APIs rather than replacing core infrastructure. (`913c00c28a82` · supporting · key_points[1]; [[sources/forward-deployed-engineering-101-01kszj77y1z51yfaqzwmfknz7h|Forward Deployed Engineering 101]])
- Treat existing enterprise systems as integration surfaces, not obstacles to be removed. (`319e69d0c06f` · supporting · key_points[2]; [[sources/forward-deployed-engineering-101-01kszj77y1z51yfaqzwmfknz7h|Forward Deployed Engineering 101]])
- Move cautiously when the workflow affects production operations or customer-facing work. (`049ab79a7cba` · supporting · key_points[3]; [[sources/forward-deployed-engineering-101-01kszj77y1z51yfaqzwmfknz7h|Forward Deployed Engineering 101]])
- Being on-site with a customer. Palantir's CTO says that you cannot build products for an environment without actually being in the environment itself. We've seen the same thing internally. (`63e36e6bfac3` · supporting · supporting_snippet; [[sources/forward-deployed-engineering-101-01kszj77y1z51yfaqzwmfknz7h|Forward Deployed Engineering 101]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

No related pages captured.

## Sources

- [[sources/forward-deployed-engineering-101-01kszj77y1z51yfaqzwmfknz7h|Forward Deployed Engineering 101]]
