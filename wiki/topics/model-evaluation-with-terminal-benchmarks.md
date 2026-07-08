---
title: Terminal-Centric Model Evaluation
slug: model-evaluation-with-terminal-benchmarks
entity_id: topic:model-evaluation-with-terminal-benchmarks
category: topic
tags:
- agent-evals
- ai-evaluation
- coding-agents
- test-and-verification
first_seen: '2026-03-19'
last_seen: '2026-03-19'
source_count: 1
evidence_count: 7
source_ids:
- introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1
value_level: medium
confidence: 0.86
synthesis_state: stage1-placeholder
---

# Terminal-Centric Model Evaluation

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Terminal-centric evaluation measures how well a model performs in interactive command-line or agent-like software tasks. These evaluations are useful when the target workload involves repeated actions, tool use, and stepwise correction rather than static generation. They can surface differences in persistence, planning, and execution quality that simpler benchmarks miss. The harness and scoring setup become part of the result, so methodology matters as much as the headline number.

## Key Points

- Harness choice changes what the benchmark number actually means.
- Repeated runs help reduce noise in agentic evaluations.
- Terminal tasks are a better fit than static prompts for workflows that need command-line execution.

## Operational Insight

For agentic coding systems, use terminal-oriented benchmarks alongside repo-level and task-level evals, because they better approximate iterative execution. Treat harness choice, number of iterations, and normalization assumptions as part of the model report, not as footnotes.

## Evidence / supporting sources

### Introducing Composer 2 (2026-03-19)

- Terminal-centric evaluation measures how well a model performs in interactive command-line or agent-like software tasks. These evaluations are useful when the target workload involves repeated actions, tool use, and stepwise correction rather than static generation. They can surface differences in persistence, planning, and execution quality that simpler benchmarks miss. The harness and scoring setup become part of the result, so methodology matters as much as the headline number. (`9cdfb123952d` · neutral · knowledge_summary; [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]])
- For agentic coding systems, use terminal-oriented benchmarks alongside repo-level and task-level evals, because they better approximate iterative execution. Treat harness choice, number of iterations, and normalization assumptions as part of the model report, not as footnotes. (`5c340a991b5b` · neutral · operational_insight; [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]])
- Terminal-style evals matter wherever agents must operate over shells, scripts, and command-line tools. As of 2026-03-19, they are a durable evaluation pattern for coding agents and other execution-oriented systems, especially when long action sequences are central to the product. (`98daeab2cf63` · neutral · relevance_note; [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]])
- Harness choice changes what the benchmark number actually means. (`197ac02b17a2` · supporting · key_points[0]; [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]])
- Repeated runs help reduce noise in agentic evaluations. (`d80369f51b5b` · supporting · key_points[1]; [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]])
- Terminal tasks are a better fit than static prompts for workflows that need command-line execution. (`df069d3afde0` · supporting · key_points[2]; [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]])
- "Our Cursor score was computed using the official Harbor evaluation framework (the designated harness for Terminal-Bench 2.0) with default benchmark settings. We ran 5 iterations per model-agent pair and report the average." (`7ff02840309f` · supporting · supporting_snippet; [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- [[topics/agentic-coding-workflows|Agentic Coding Workflows]]

## Sources

- [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]]
