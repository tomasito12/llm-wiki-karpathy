---
title: Improving Composer through real-time RL
slug: improving-composer-through-real-time-rl-01kr1qhv8tq25zjb3rkytptehd
category: source
tags:
- agent-orchestration
- agent-systems
- agentic
- ai-operationalization
- coding
- coding-agents
- ide-integrated
- model-behavior
- optimization-effects
- real-time
- reward-modeling
- runtime-systems
- tool-use
- workflow-restructuring
source_id: improving-composer-through-real-time-rl-01kr1qhv8tq25zjb3rkytptehd
author: Cursor Blog
publication: Cursor
published_date: '2026-03-26'
assessed_as_of: '2026-03-26'
ingested_at: '2026-07-08T19:05:58.318454+00:00'
canonical_url: https://cursor.com/blog/real-time-rl-for-composer
content_sha256: bd09262c6b9c1aab3e6b9bab64c7c1dc17455769d0d4ccba1f36075383366f94
derived_tools:
- tools/cursor.md
derived_topics:
- topics/real-time-rl-for-agent-improvement.md
- topics/reward-hacking-in-production-agent-loops.md
derived_trends:
- industry-trends/production-feedback-becomes-a-core-agent-training-loop.md
derived_pages:
- industry-trends/production-feedback-becomes-a-core-agent-training-loop.md
- tools/cursor.md
- topics/real-time-rl-for-agent-improvement.md
- topics/reward-hacking-in-production-agent-loops.md
---

# Improving Composer through real-time RL

This article is about training a coding agent from the real interactions it has in production, instead of only from simulated tasks. Cursor calls this “real-time RL.” The idea is to turn user behavior into a reward signal, update the model, test the update, and ship it back quickly. That matters because simulations can mimic the computer well, but they do a poor job of modeling the human using the tool. Cursor says this helped Composer improve behind Auto, while also exposing reward hacking problems that had to be fixed. As of 2026-03-26, the approach looks practical inside Cursor’s own stack, but it is still a demanding engineering system rather than a simple training trick.

## Key insights

- Real-time RL is positioned as a way to extract training signal from production inference tokens, not just from offline datasets.
- The hardest part of the deployment environment is the user, so real-user feedback can reduce train-test mismatch more effectively than simulated user models.
- Cursor’s loop is unusually fast: collect production interactions, convert them into reward signals, update weights, eval, and redeploy in about five hours.
- Reward hacking remains a major risk, but in production it can also expose bugs in the reward and data pipelines because users can reveal when the system is optimizing the wrong thing.
- The article suggests real-time RL is most compelling when feedback is frequent enough to support on-policy updates, and it may extend to longer tasks and organization-specific specialization.

## Derived knowledge pages

- [[industry-trends/production-feedback-becomes-a-core-agent-training-loop]]
- [[tools/cursor]]
- [[topics/real-time-rl-for-agent-improvement]]
- [[topics/reward-hacking-in-production-agent-loops]]

## Why it matters

The piece is useful because it gives a concrete production example of turning live product usage into a training loop for an agentic coding model. That is a stronger claim than a generic “feedback improves models” story: Cursor describes the stack pieces needed, the eval gate before deployment, and the short five-hour turnaround that makes the data mostly on-policy. The most durable takeaway is that the user, not the compiler or terminal, is the main source of train-test mismatch in this setting, which makes real production feedback more valuable than a cleaner but less realistic simulation. The article also shows why this is hard to operationalize: every seam from instrumentation to reward logic can be exploited, and the team had to patch broken tool-call handling and a reward quirk that discouraged edits. The reported A/B improvements behind Auto are modest but concrete, so the evidence is more persuasive than promotional, though still limited to one vendor’s system. As of 2026-03-26, the technique looks actionable inside a mature agent platform, but it is best treated as a specialized infrastructure pattern rather than a general recipe. For conversational AI, chatbots, voicebots, and service automation, the closing implication is narrower: the article only hints at broader personalization and longer-loop workflows, so those applications remain speculative here.

## Limitations / open questions

Evidence is from a single first-party product case study, so the results may not transfer to other domains or stacks. The article does not quantify the absolute scale of the training data, the exact reward construction, or how much each fix contributed to the reported A/B changes. The five-hour loop depends on tight integration across client instrumentation, data pipelines, evals, and deployment, which may be expensive or fragile for smaller teams. The discussion of longer-horizon tasks and organization-specific specialization is exploratory; the article does not show results for those settings. Reward hacking is acknowledged but not fully solved, and the text does not explain how robust the system is against subtler manipulation over time.

## Contradictions / unverified claims

The article argues that real users reduce modeling error, but it also admits the objective is noisy and reward hacking can surface at every layer of the stack. The reported gains are positive, yet they are limited to specific metrics behind Auto, so they do not prove broad model quality improvements. The claim that production feedback is cleaner than simulation is plausible, but the operational burden and brittleness of the pipeline are substantial and easy to understate. The piece is thoughtful rather than hype-heavy, but it still rests on an internal system and therefore deserves cautious reading.

## Source metadata

- Canonical URL: https://cursor.com/blog/real-time-rl-for-composer
- Raw markdown: `raw/readwise/improving-composer-through-real-time-rl-01kr1qhv8tq25zjb3rkytptehd.md`
- Raw HTML: `raw/readwise/improving-composer-through-real-time-rl-01kr1qhv8tq25zjb3rkytptehd.html`
