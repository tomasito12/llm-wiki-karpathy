---
title: AI Evaluation Shifts Toward Workflow-Based Tool Use
slug: agent-evaluation-shifts-toward-workflow-based-tool-use
entity_id: trend:agent-evaluation-shifts-toward-workflow-based-tool-use
category: industry-trend
tags:
- workflow-based-evaluation
first_seen: '2026-04-25'
last_seen: '2026-04-25'
source_count: 1
evidence_count: 10
source_ids:
- why-i-stopped-using-gemma-4-and-switched-to-qwen-3-6-01kqm05wc7wq68ypednrdcpa0b
value_level: high
confidence: 0.94
synthesis_state: stage1-placeholder
maturity: unknown
---

# AI Evaluation Shifts Toward Workflow-Based Tool Use

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Model evaluation is shifting from single-turn answer quality toward workflow-based tests that include tool calls, state tracking, and recovery from errors. The relevant benchmark is no longer just whether a model answers correctly, but whether it can complete a real task inside an execution loop. This favors evaluation suites that resemble agent work rather than chat completion.

## Supporting Data Points

- MCPMark: Qwen 37.0 vs Gemma 18.1
- SWE-bench Verified: Qwen 73.4 vs Gemma 52.0
- Terminal-Bench 2.0: Qwen 51.5 vs Gemma 42.9
- NL2Repo: Qwen 29.4 vs Gemma 15.5
- HumanEval note: Gemma still ranks first in community testing at 100 percent while Qwen sits at 93

## Time sensitivity

As of 2026-04-25, this is a live evaluation preference rather than a settled universal standard. The source presents it as especially relevant for agentic coding workflows, not all model use cases.

## Uncertainty / maturity

The source is persuasive but not definitive: some cited metrics are vendor-published, and a narrow benchmark can still miss important behavior. It is best read as a workflow-specific evaluation shift, not proof that every team should replace all existing evals.

## Evidence / supporting sources

### Why I Stopped Using Gemma 4 and Switched to Qwen 3.6 (2026-04-25)

- Model evaluation is shifting from single-turn answer quality toward workflow-based tests that include tool calls, state tracking, and recovery from errors. The relevant benchmark is no longer just whether a model answers correctly, but whether it can complete a real task inside an execution loop. This favors evaluation suites that resemble agent work rather than chat completion. (`7280c63be81e` · neutral · trend_description; [[sources/why-i-stopped-using-gemma-4-and-switched-to-qwen-3-6-01kqm05wc7wq68ypednrdcpa0b|Why I Stopped Using Gemma 4 and Switched to Qwen 3.6]])
- The article argues that the benchmarks that mattered were MCPMark, SWE-bench Verified, Terminal-Bench 2.0, and NL2Repo because they measure tool use and agent loops better than one-shot tests. It explicitly contrasts this with Gemma 4's stronger performance on a single-question benchmark like HumanEval. (`442664239e24` · supporting · evidence_from_source; [[sources/why-i-stopped-using-gemma-4-and-switched-to-qwen-3-6-01kqm05wc7wq68ypednrdcpa0b|Why I Stopped Using Gemma 4 and Switched to Qwen 3.6]])
- MCPMark: Qwen 37.0 vs Gemma 18.1 (`7b5495ce6d37` · supporting · supporting_data_points[0]; [[sources/why-i-stopped-using-gemma-4-and-switched-to-qwen-3-6-01kqm05wc7wq68ypednrdcpa0b|Why I Stopped Using Gemma 4 and Switched to Qwen 3.6]])
- SWE-bench Verified: Qwen 73.4 vs Gemma 52.0 (`8557fccbf4c8` · supporting · supporting_data_points[1]; [[sources/why-i-stopped-using-gemma-4-and-switched-to-qwen-3-6-01kqm05wc7wq68ypednrdcpa0b|Why I Stopped Using Gemma 4 and Switched to Qwen 3.6]])
- Terminal-Bench 2.0: Qwen 51.5 vs Gemma 42.9 (`d7d38c764cf9` · supporting · supporting_data_points[2]; [[sources/why-i-stopped-using-gemma-4-and-switched-to-qwen-3-6-01kqm05wc7wq68ypednrdcpa0b|Why I Stopped Using Gemma 4 and Switched to Qwen 3.6]])
- NL2Repo: Qwen 29.4 vs Gemma 15.5 (`f81f3d82dad5` · supporting · supporting_data_points[3]; [[sources/why-i-stopped-using-gemma-4-and-switched-to-qwen-3-6-01kqm05wc7wq68ypednrdcpa0b|Why I Stopped Using Gemma 4 and Switched to Qwen 3.6]])
- HumanEval note: Gemma still ranks first in community testing at 100 percent while Qwen sits at 93 (`1be9f4abe359` · supporting · supporting_data_points[4]; [[sources/why-i-stopped-using-gemma-4-and-switched-to-qwen-3-6-01kqm05wc7wq68ypednrdcpa0b|Why I Stopped Using Gemma 4 and Switched to Qwen 3.6]])
- "Agent work is not that. Agent work is twenty turns of tool calls, state management, and recovery from errors. The benchmarks did not measure it. Real work did." (`4587a259a714` · supporting · supporting_snippet; [[sources/why-i-stopped-using-gemma-4-and-switched-to-qwen-3-6-01kqm05wc7wq68ypednrdcpa0b|Why I Stopped Using Gemma 4 and Switched to Qwen 3.6]])
- As of 2026-04-25, this is a live evaluation preference rather than a settled universal standard. The source presents it as especially relevant for agentic coding workflows, not all model use cases. (`06ed92509c4a` · uncertainty · time_sensitivity; [[sources/why-i-stopped-using-gemma-4-and-switched-to-qwen-3-6-01kqm05wc7wq68ypednrdcpa0b|Why I Stopped Using Gemma 4 and Switched to Qwen 3.6]])
- The source is persuasive but not definitive: some cited metrics are vendor-published, and a narrow benchmark can still miss important behavior. It is best read as a workflow-specific evaluation shift, not proof that every team should replace all existing evals. (`148689534c49` · uncertainty · uncertainty_note; [[sources/why-i-stopped-using-gemma-4-and-switched-to-qwen-3-6-01kqm05wc7wq68ypednrdcpa0b|Why I Stopped Using Gemma 4 and Switched to Qwen 3.6]])

## Contradictions / tensions

- As of 2026-04-25, this is a live evaluation preference rather than a settled universal standard. The source presents it as especially relevant for agentic coding workflows, not all model use cases. (uncertainty; [[sources/why-i-stopped-using-gemma-4-and-switched-to-qwen-3-6-01kqm05wc7wq68ypednrdcpa0b|Why I Stopped Using Gemma 4 and Switched to Qwen 3.6]])
- The source is persuasive but not definitive: some cited metrics are vendor-published, and a narrow benchmark can still miss important behavior. It is best read as a workflow-specific evaluation shift, not proof that every team should replace all existing evals. (uncertainty; [[sources/why-i-stopped-using-gemma-4-and-switched-to-qwen-3-6-01kqm05wc7wq68ypednrdcpa0b|Why I Stopped Using Gemma 4 and Switched to Qwen 3.6]])

## Related pages

- [[industry-trends/verification-loops-become-central-to-ai-workflows|AI workflows are shifting toward verification loops instead of prompt-only operation]]
- [[industry-trends/agentic-coding-shifts-toward-higher-supervision-costs|Agentic Coding Shifts Toward Higher Supervision Costs]]

## Sources

- [[sources/why-i-stopped-using-gemma-4-and-switched-to-qwen-3-6-01kqm05wc7wq68ypednrdcpa0b|Why I Stopped Using Gemma 4 and Switched to Qwen 3.6]]
