---
title: Money-denominated evals expose agent behavior that benchmark scores miss
slug: money-denominated-evals-expose-agent-behavior-that-benchmark-scores-miss
category: insight
tags:
- agent-evals
- ai-evaluation
source_id: reality-the-final-eval-lukas-petersson-and-axel-backlund-of-andon-labs-01kta5x2q1019991cgcmsykb83
source_title: 'Reality: The Final Eval — Lukas Petersson and Axel Backlund of Andon
  Labs'
source_date: '2026-06-04'
month: 2026-06
evidence_count: 8
evidence_set_hash: 78d63f0ed7ce9a68
insight_title: Money-denominated evals expose agent behavior that benchmark scores
  miss
insight_type: research_eval
confidence: high
durability_estimate: long_term
wiki_worthiness: strong_candidate
---

# Money-denominated evals expose agent behavior that benchmark scores miss

## Interview Insight

### Summary

Andon Labs argues that evaluating agents on dollars earned or lost is more durable than using bounded benchmark scores. Their claim is that revenue-style metrics do not saturate the way percentage or percentile benchmarks do, and they better capture long-horizon business behavior. The examples are vending machines and other real-world tasks where the agent must manage inventory, fees, and customer interactions over time.

### Why It Matters

As of 2026-06-04, this is a useful eval design pattern for teams building agents that touch commerce or operations. It shifts attention from abstract capability scores to outcome metrics that map to real deployment risk and value. The limitation is that the evidence here is still a lab-specific implementation case, not a general proof of predictive validity.

### Operational Relevance

Use dollar-based or other outcome-based scoring when the agent is meant to operate a business process. Preserve the full trace, because the path to the outcome contains failure modes that a final score hides. Keep the benchmark open-ended enough to avoid ceiling effects, but simple enough that harness quirks do not dominate.

### Service Automation Relevance

Useful for support and back-office automation when the goal is not just answer quality but measurable business outcomes like refunds avoided, issues resolved, or costs contained. The transcript suggests that final-answer metrics alone can miss harmful behavior in customer-facing workflows.

### Mentioned Entities

- Andon Labs
- VendingBench
- Project Vend

### Suggested Destinations

- topics/
- evaluation/

### Contrarian Or Speculative Claims

- Dollar-denominated evals are more durable because they do not saturate like percentage-style benchmarks.

### Evidence Snippets

- "One thing with Andon Labs, the way we kind of like decide what to do next and what projects to do, it’s what is like the heuristic we use is what is fun? Is What would be a fun project?"
- "The nice thing is that there’s no ceiling. You can just-- It never saturates because it could just make more and more money."
- "You don’t know what a model is capable of doing in the real world unless you actually give it inventory, a wallet, tools, customers, competitors, humans, & some time."

## Evidence / supporting sources

### Reality: The Final Eval — Lukas Petersson and Axel Backlund of Andon Labs (2026-06-04)

- Dollar-denominated evals are more durable because they do not saturate like percentage-style benchmarks. (`b324f4e68e4d` · counter · contrarian_or_speculative_claims[0]; [[sources/reality-the-final-eval-lukas-petersson-and-axel-backlund-of-andon-labs-01kta5x2q1019991cgcmsykb83|Reality: The Final Eval — Lukas Petersson and Axel Backlund of Andon Labs]])
- Use dollar-based or other outcome-based scoring when the agent is meant to operate a business process. Preserve the full trace, because the path to the outcome contains failure modes that a final score hides. Keep the benchmark open-ended enough to avoid ceiling effects, but simple enough that harness quirks do not dominate. (`b471d924d159` · neutral · operational_relevance; [[sources/reality-the-final-eval-lukas-petersson-and-axel-backlund-of-andon-labs-01kta5x2q1019991cgcmsykb83|Reality: The Final Eval — Lukas Petersson and Axel Backlund of Andon Labs]])
- Useful for support and back-office automation when the goal is not just answer quality but measurable business outcomes like refunds avoided, issues resolved, or costs contained. The transcript suggests that final-answer metrics alone can miss harmful behavior in customer-facing workflows. (`6e0579bfc644` · neutral · service_automation_relevance; [[sources/reality-the-final-eval-lukas-petersson-and-axel-backlund-of-andon-labs-01kta5x2q1019991cgcmsykb83|Reality: The Final Eval — Lukas Petersson and Axel Backlund of Andon Labs]])
- Andon Labs argues that evaluating agents on dollars earned or lost is more durable than using bounded benchmark scores. Their claim is that revenue-style metrics do not saturate the way percentage or percentile benchmarks do, and they better capture long-horizon business behavior. The examples are vending machines and other real-world tasks where the agent must manage inventory, fees, and customer interactions over time. (`8c80b0529382` · neutral · summary; [[sources/reality-the-final-eval-lukas-petersson-and-axel-backlund-of-andon-labs-01kta5x2q1019991cgcmsykb83|Reality: The Final Eval — Lukas Petersson and Axel Backlund of Andon Labs]])
- As of 2026-06-04, this is a useful eval design pattern for teams building agents that touch commerce or operations. It shifts attention from abstract capability scores to outcome metrics that map to real deployment risk and value. The limitation is that the evidence here is still a lab-specific implementation case, not a general proof of predictive validity. (`09a2bee852a3` · neutral · why_it_matters; [[sources/reality-the-final-eval-lukas-petersson-and-axel-backlund-of-andon-labs-01kta5x2q1019991cgcmsykb83|Reality: The Final Eval — Lukas Petersson and Axel Backlund of Andon Labs]])
- "One thing with Andon Labs, the way we kind of like decide what to do next and what projects to do, it’s what is like the heuristic we use is what is fun? Is What would be a fun project?" (`402ea00d91d9` · supporting · evidence_snippets[0]; [[sources/reality-the-final-eval-lukas-petersson-and-axel-backlund-of-andon-labs-01kta5x2q1019991cgcmsykb83|Reality: The Final Eval — Lukas Petersson and Axel Backlund of Andon Labs]])
- "The nice thing is that there’s no ceiling. You can just-- It never saturates because it could just make more and more money." (`f6d4a9f8c274` · supporting · evidence_snippets[1]; [[sources/reality-the-final-eval-lukas-petersson-and-axel-backlund-of-andon-labs-01kta5x2q1019991cgcmsykb83|Reality: The Final Eval — Lukas Petersson and Axel Backlund of Andon Labs]])
- "You don’t know what a model is capable of doing in the real world unless you actually give it inventory, a wallet, tools, customers, competitors, humans, & some time." (`280e4b81edaa` · supporting · evidence_snippets[2]; [[sources/reality-the-final-eval-lukas-petersson-and-axel-backlund-of-andon-labs-01kta5x2q1019991cgcmsykb83|Reality: The Final Eval — Lukas Petersson and Axel Backlund of Andon Labs]])

## Source

- [[sources/reality-the-final-eval-lukas-petersson-and-axel-backlund-of-andon-labs-01kta5x2q1019991cgcmsykb83|Reality: The Final Eval — Lukas Petersson and Axel Backlund of Andon Labs]]
