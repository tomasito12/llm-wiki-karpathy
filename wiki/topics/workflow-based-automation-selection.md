---
title: Workflow-Based Automation Selection
slug: workflow-based-automation-selection
entity_id: topic:workflow-based-automation-selection
category: topic
tags:
- ai-engineering
- orchestration
- workflow-design
first_seen: '2026-05-20'
last_seen: '2026-05-20'
source_count: 1
evidence_count: 9
source_ids:
- forward-deployed-engineering-101-01kszj77y1z51yfaqzwmfknz7h
value_level: high
confidence: 0.91
synthesis_state: stage1-placeholder
---

# Workflow-Based Automation Selection

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Not every task should be automated with an agent. A durable design rule is to automate workflows that have clear rules, variable inputs, and enough volume to justify the overhead, while leaving low-volume or judgment-heavy work manual. This pushes teams to think about tool use, orchestration, and cost rather than treating every task as an AI candidate. The main benefit is better ROI and fewer cases where automation adds more complexity than value.

## Examples

The source gives explicit heuristics: if "the rules and inputs are both predictable, code is faster and cheaper," if a job "runs five times a month" it is probably not worth the ROI, and "most automation tasks can be done with a series of tool calls and just one call to an LLM as an orchestrating layer."

## Key Points

- Use agents when inputs vary but the workflow still follows rules and needs tool calls.
- Use code when both the rules and the inputs are predictable.
- Leave tasks manual when the work depends mainly on human judgment and domain expertise.
- Do not automate low-volume workflows unless the value per run is high enough to justify the effort.

## Operational Insight

Use task frequency, input variability, and decision type as the first filter before choosing agents, code, or manual handling.

## Evidence / supporting sources

### Forward Deployed Engineering 101 (2026-05-20)

- The source gives explicit heuristics: if "the rules and inputs are both predictable, code is faster and cheaper," if a job "runs five times a month" it is probably not worth the ROI, and "most automation tasks can be done with a series of tool calls and just one call to an LLM as an orchestrating layer." (`31cd3de55825` · neutral · examples; [[sources/forward-deployed-engineering-101-01kszj77y1z51yfaqzwmfknz7h|Forward Deployed Engineering 101]])
- Not every task should be automated with an agent. A durable design rule is to automate workflows that have clear rules, variable inputs, and enough volume to justify the overhead, while leaving low-volume or judgment-heavy work manual. This pushes teams to think about tool use, orchestration, and cost rather than treating every task as an AI candidate. The main benefit is better ROI and fewer cases where automation adds more complexity than value. (`3d53e915d944` · neutral · knowledge_summary; [[sources/forward-deployed-engineering-101-01kszj77y1z51yfaqzwmfknz7h|Forward Deployed Engineering 101]])
- Use task frequency, input variability, and decision type as the first filter before choosing agents, code, or manual handling. (`0b1ec6992016` · neutral · operational_insight; [[sources/forward-deployed-engineering-101-01kszj77y1z51yfaqzwmfknz7h|Forward Deployed Engineering 101]])
- This is useful for AI engineering and service automation because it reduces wasted build effort. Teams can reserve agents for workflows where orchestration actually helps, rather than forcing model calls into every process step. (`4013b3799ec0` · neutral · relevance_note; [[sources/forward-deployed-engineering-101-01kszj77y1z51yfaqzwmfknz7h|Forward Deployed Engineering 101]])
- Use agents when inputs vary but the workflow still follows rules and needs tool calls. (`8a0830dc8c6a` · supporting · key_points[0]; [[sources/forward-deployed-engineering-101-01kszj77y1z51yfaqzwmfknz7h|Forward Deployed Engineering 101]])
- Use code when both the rules and the inputs are predictable. (`a3c48f08ff7c` · supporting · key_points[1]; [[sources/forward-deployed-engineering-101-01kszj77y1z51yfaqzwmfknz7h|Forward Deployed Engineering 101]])
- Leave tasks manual when the work depends mainly on human judgment and domain expertise. (`abc47149addb` · supporting · key_points[2]; [[sources/forward-deployed-engineering-101-01kszj77y1z51yfaqzwmfknz7h|Forward Deployed Engineering 101]])
- Do not automate low-volume workflows unless the value per run is high enough to justify the effort. (`81140a1f56fc` · supporting · key_points[3]; [[sources/forward-deployed-engineering-101-01kszj77y1z51yfaqzwmfknz7h|Forward Deployed Engineering 101]])
- If a workflow can be distilled into rules but the inputs are different ... and the work involves calling tools, put an agent in. If the rules and inputs are both predictable, code is faster and cheaper. If the decision needs pattern recognition and domain expertise, leave it manual. (`1bbd616de0d2` · supporting · supporting_snippet; [[sources/forward-deployed-engineering-101-01kszj77y1z51yfaqzwmfknz7h|Forward Deployed Engineering 101]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

No related pages captured.

## Sources

- [[sources/forward-deployed-engineering-101-01kszj77y1z51yfaqzwmfknz7h|Forward Deployed Engineering 101]]
