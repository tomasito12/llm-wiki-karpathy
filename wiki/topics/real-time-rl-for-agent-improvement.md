---
title: Real-Time RL for Agent Improvement
slug: real-time-rl-for-agent-improvement
entity_id: topic:real-time-rl-for-agent-improvement
category: topic
tags:
- agent-orchestration
- agent-systems
- coding-agents
- runtime-systems
first_seen: '2026-03-26'
last_seen: '2026-03-26'
source_count: 1
evidence_count: 8
source_ids:
- improving-composer-through-real-time-rl-01kr1qhv8tq25zjb3rkytptehd
value_level: high
confidence: 0.95
synthesis_state: stage1-placeholder
---

# Real-Time RL for Agent Improvement

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Real-world agent systems can be improved by converting live user interactions into training signal and using that signal to update the model on a short loop. The practical value is not just more data, but more realistic data: it comes from deployed workflows, actual users, and the exact product environment the agent must operate in. This makes the training signal more aligned with production behavior than simulated tasks alone, especially when the user’s guidance and approval are part of the task. The approach is operationally demanding because it requires instrumentation, signal distillation, reward construction, evaluation gates, and fast redeployment. It also creates a feedback loop where model failures and reward hacks become debugging inputs for the training system itself.

## Key Points

- Production inference tokens can be reused as training signal when the system can reliably translate user behavior into rewards.
- Short feedback loops reduce train-test mismatch because the model trains on the same or nearly the same policy that generated the data.
- The approach is only practical when evals and deployment are fast enough to keep updates close to on-policy.
- Reward hacking does not disappear in production; it shifts into the seams between data collection, signal conversion, and reward logic.

## Operational Insight

For agentic products, treat production interactions as a first-class training corpus only if you can measure, gate, and redeploy quickly enough to keep the data mostly on-policy.

## Related Topics

- verification-loops-in-ai-workflows

## Evidence / supporting sources

### Improving Composer through real-time RL (2026-03-26)

- Real-world agent systems can be improved by converting live user interactions into training signal and using that signal to update the model on a short loop. The practical value is not just more data, but more realistic data: it comes from deployed workflows, actual users, and the exact product environment the agent must operate in. This makes the training signal more aligned with production behavior than simulated tasks alone, especially when the user’s guidance and approval are part of the task. The approach is operationally demanding because it requires instrumentation, signal distillation, reward construction, evaluation gates, and fast redeployment. It also creates a feedback loop where model failures and reward hacks become debugging inputs for the training system itself. (`524083c4c940` · neutral · knowledge_summary; [[sources/improving-composer-through-real-time-rl-01kr1qhv8tq25zjb3rkytptehd|Improving Composer through real-time RL]])
- For agentic products, treat production interactions as a first-class training corpus only if you can measure, gate, and redeploy quickly enough to keep the data mostly on-policy. (`6013f7c4658d` · neutral · operational_insight; [[sources/improving-composer-through-real-time-rl-01kr1qhv8tq25zjb3rkytptehd|Improving Composer through real-time RL]])
- This pattern matters long-term because many deployed agents are judged in the same environment where they are used, so production feedback can be more valuable than synthetic benchmarks when the workflow is well instrumented. It is especially relevant for coding agents, support automation, and other systems where user actions directly expose whether the model helped. As of 2026-03-26, the main lesson is architectural: the training loop becomes part of the product stack. (`85e2d3eb31a4` · neutral · relevance_note; [[sources/improving-composer-through-real-time-rl-01kr1qhv8tq25zjb3rkytptehd|Improving Composer through real-time RL]])
- Production inference tokens can be reused as training signal when the system can reliably translate user behavior into rewards. (`61b2d9e60b8d` · supporting · key_points[0]; [[sources/improving-composer-through-real-time-rl-01kr1qhv8tq25zjb3rkytptehd|Improving Composer through real-time RL]])
- Short feedback loops reduce train-test mismatch because the model trains on the same or nearly the same policy that generated the data. (`3985417a9152` · supporting · key_points[1]; [[sources/improving-composer-through-real-time-rl-01kr1qhv8tq25zjb3rkytptehd|Improving Composer through real-time RL]])
- The approach is only practical when evals and deployment are fast enough to keep updates close to on-policy. (`d37de0c6e4a7` · supporting · key_points[2]; [[sources/improving-composer-through-real-time-rl-01kr1qhv8tq25zjb3rkytptehd|Improving Composer through real-time RL]])
- Reward hacking does not disappear in production; it shifts into the seams between data collection, signal conversion, and reward logic. (`33b2147cb9c0` · supporting · key_points[3]; [[sources/improving-composer-through-real-time-rl-01kr1qhv8tq25zjb3rkytptehd|Improving Composer through real-time RL]])
- "We call our approach of using real inference tokens for training \"real-time RL.\" ... We serve model checkpoints to production, observe user responses, and aggregate those responses as reward signals." (`5a808a311d31` · supporting · supporting_snippet; [[sources/improving-composer-through-real-time-rl-01kr1qhv8tq25zjb3rkytptehd|Improving Composer through real-time RL]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- verification-loops-in-ai-workflows

## Sources

- [[sources/improving-composer-through-real-time-rl-01kr1qhv8tq25zjb3rkytptehd|Improving Composer through real-time RL]]
