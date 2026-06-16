---
title: Simple shared harnesses reduce benchmark bias, even if they leave performance
  on the table
slug: simple-shared-harnesses-reduce-benchmark-bias-even-if-they-leave-performance-on-the-table
category: insight
tags:
- test-and-verification
- ai-evaluation
- ai-engineering
source_id: reality-the-final-eval-lukas-petersson-and-axel-backlund-of-andon-labs-01kta5x2q1019991cgcmsykb83
source_title: 'Reality: The Final Eval — Lukas Petersson and Axel Backlund of Andon
  Labs'
source_date: '2026-06-04'
month: 2026-06
evidence_count: 8
evidence_set_hash: 358b2788cddc3b3d
insight_title: Simple shared harnesses reduce benchmark bias, even if they leave performance
  on the table
insight_type: research_eval
confidence: high
durability_estimate: long_term
wiki_worthiness: review_candidate
---

# Simple shared harnesses reduce benchmark bias, even if they leave performance on the table

## Interview Insight

### Summary

Andon says it prefers a minimal, shared harness across models rather than model-specific prompt tuning. The rationale is that a complex or customized harness can accidentally favor one model family and make comparisons less trustworthy. They explicitly frame this as a trade-off between eliciting maximum performance and keeping the benchmark neutral.

### Why It Matters

As of 2026-06-04, this is a durable benchmark-design lesson for teams comparing frontier models. It is a reminder that benchmark engineering can distort conclusions as much as model differences can. The downside is that the transcript offers a principle and examples, but not a formal ablation study.

### Operational Relevance

When building evals, prefer simple, stable tool schemas and prompts that are shared across models. If model-specific tuning is used, keep it separate from the primary comparison benchmark and treat it as a secondary optimization layer.

### Service Automation Relevance

Indirect but useful: the same principle applies when measuring agent performance across different customer-service models or orchestration stacks. A neutral harness makes cross-vendor comparison more trustworthy.

### Mentioned Entities

- Andon Labs
- Cursor

### Suggested Destinations

- topics/

### Contrarian Or Speculative Claims

- Letting a model rewrite its own system prompt could be even less biased than a fixed prompt.

### Evidence Snippets

- "our philosophy around harnesses is like we try to make something that’s quite minimalistic, like quite simple."
- "we don’t wanna favor one model a lot over the other"
- "let the model write its own system prompt ... Maybe that’s even less bias."

## Evidence / supporting sources

### Reality: The Final Eval — Lukas Petersson and Axel Backlund of Andon Labs (2026-06-04)

- Letting a model rewrite its own system prompt could be even less biased than a fixed prompt. (`7996be64277b` · counter · contrarian_or_speculative_claims[0]; [[sources/reality-the-final-eval-lukas-petersson-and-axel-backlund-of-andon-labs-01kta5x2q1019991cgcmsykb83|Reality: The Final Eval — Lukas Petersson and Axel Backlund of Andon Labs]])
- When building evals, prefer simple, stable tool schemas and prompts that are shared across models. If model-specific tuning is used, keep it separate from the primary comparison benchmark and treat it as a secondary optimization layer. (`c73dfdaedba7` · neutral · operational_relevance; [[sources/reality-the-final-eval-lukas-petersson-and-axel-backlund-of-andon-labs-01kta5x2q1019991cgcmsykb83|Reality: The Final Eval — Lukas Petersson and Axel Backlund of Andon Labs]])
- Indirect but useful: the same principle applies when measuring agent performance across different customer-service models or orchestration stacks. A neutral harness makes cross-vendor comparison more trustworthy. (`fe874a06e418` · neutral · service_automation_relevance; [[sources/reality-the-final-eval-lukas-petersson-and-axel-backlund-of-andon-labs-01kta5x2q1019991cgcmsykb83|Reality: The Final Eval — Lukas Petersson and Axel Backlund of Andon Labs]])
- Andon says it prefers a minimal, shared harness across models rather than model-specific prompt tuning. The rationale is that a complex or customized harness can accidentally favor one model family and make comparisons less trustworthy. They explicitly frame this as a trade-off between eliciting maximum performance and keeping the benchmark neutral. (`be5b01382ccf` · neutral · summary; [[sources/reality-the-final-eval-lukas-petersson-and-axel-backlund-of-andon-labs-01kta5x2q1019991cgcmsykb83|Reality: The Final Eval — Lukas Petersson and Axel Backlund of Andon Labs]])
- As of 2026-06-04, this is a durable benchmark-design lesson for teams comparing frontier models. It is a reminder that benchmark engineering can distort conclusions as much as model differences can. The downside is that the transcript offers a principle and examples, but not a formal ablation study. (`c04fa09acfce` · neutral · why_it_matters; [[sources/reality-the-final-eval-lukas-petersson-and-axel-backlund-of-andon-labs-01kta5x2q1019991cgcmsykb83|Reality: The Final Eval — Lukas Petersson and Axel Backlund of Andon Labs]])
- "our philosophy around harnesses is like we try to make something that’s quite minimalistic, like quite simple." (`f513b549f85b` · supporting · evidence_snippets[0]; [[sources/reality-the-final-eval-lukas-petersson-and-axel-backlund-of-andon-labs-01kta5x2q1019991cgcmsykb83|Reality: The Final Eval — Lukas Petersson and Axel Backlund of Andon Labs]])
- "we don’t wanna favor one model a lot over the other" (`578267803a2e` · supporting · evidence_snippets[1]; [[sources/reality-the-final-eval-lukas-petersson-and-axel-backlund-of-andon-labs-01kta5x2q1019991cgcmsykb83|Reality: The Final Eval — Lukas Petersson and Axel Backlund of Andon Labs]])
- "let the model write its own system prompt ... Maybe that’s even less bias." (`4469a14ac689` · supporting · evidence_snippets[2]; [[sources/reality-the-final-eval-lukas-petersson-and-axel-backlund-of-andon-labs-01kta5x2q1019991cgcmsykb83|Reality: The Final Eval — Lukas Petersson and Axel Backlund of Andon Labs]])

## Source

- [[sources/reality-the-final-eval-lukas-petersson-and-axel-backlund-of-andon-labs-01kta5x2q1019991cgcmsykb83|Reality: The Final Eval — Lukas Petersson and Axel Backlund of Andon Labs]]
