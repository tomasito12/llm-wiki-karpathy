---
title: How we develop pricing and packaging at Fin
slug: how-we-develop-pricing-and-packaging-at-fin-01ks2ns7k02qfhbcgkc41wqe3v
category: source
tags:
- ai-economics
- ai-engineering
- ai-operationalization
- enterprise-ai
- enterprise-workflows
- support-automation
source_id: how-we-develop-pricing-and-packaging-at-fin-01ks2ns7k02qfhbcgkc41wqe3v
author: Sophie Woods
publication: The Intercom Blog
published_date: '2026-05-20'
assessed_as_of: '2026-05-20'
ingested_at: '2026-06-06T21:54:12+00:00'
canonical_url: https://www.intercom.com/blog/how-we-develop-pricing-and-packaging-at-fin/
content_sha256: f30229317ec2e489f865b6a0f366e77142fddcb624705a89c1de6f5626159b42
derived_topics:
- topics/outcome-based-pricing-for-ai-agents.md
- topics/pricing-model-validation-for-ai-products.md
derived_trends:
- industry-trends/ai-product-pricing-shifts-toward-measured-outcomes.md
derived_pages:
- industry-trends/ai-product-pricing-shifts-toward-measured-outcomes.md
- topics/outcome-based-pricing-for-ai-agents.md
- topics/pricing-model-validation-for-ai-products.md
---

# How we develop pricing and packaging at Fin

This piece is about how Intercom thinks through pricing for Fin, its AI Agent. The main idea is that pricing is not just picking a number; it starts with research into how buyers think about value. Intercom first decides the pricing model and the unit it will measure, then tests how much people are willing to pay. After that, it models how discounts, usage, and margins affect the real business outcome. The article is useful because it shows pricing as a structured process, not guesswork. It also makes clear that pricing needs to keep evolving as the product grows.

## Key insights

- Buyer research comes first because the wrong pricing model makes later willingness-to-pay data meaningless.
- Intercom treats the pricing metric as a design choice, not just an accounting unit; for Fin, the metric is outcomes.
- Willingness-to-pay research is used to ground discussion, but not to finalize price, because intent is not the same as behavior.
- The modeling step matters because it converts survey intent into forecasts that include discounting, usage, adoption, ARR, and margins.
- As Fin expands, the harder question becomes system design across products, not optimizing one product’s price in isolation.

## Derived knowledge pages

- [[industry-trends/ai-product-pricing-shifts-toward-measured-outcomes]]
- [[topics/outcome-based-pricing-for-ai-agents]]
- [[topics/pricing-model-validation-for-ai-products]]

## Why it matters

The article is valuable because it shows a concrete internal workflow for pricing an AI product: qualitative buyer research, willingness-to-pay studies, then finance and data science modeling before executive approval. That sequence is operationally useful for teams building AI products with monetization uncertainty, because it separates the problem of choosing a pricing logic from the problem of estimating price points. The strongest reusable insight is that the pricing metric itself is strategic; small definition changes can materially alter how customers perceive value. The article also makes a useful distinction between survey intent and real commercial behavior, which is why the modeling step includes discounting, usage, attach rates, and margin constraints. It is less a general theory of AI pricing than a company-specific account of how Intercom tries to keep pricing aligned with product value and business goals. The piece is candid that the ideal process is only followed about half the time, which adds realism and limits overgeneralization. As of 2026-05-20, this is actionable as a process reference, but it should be treated as a durable workflow pattern rather than a universal pricing recipe. The service automation implication is direct: the article is about monetizing an AI Agent that resolves customer queries, so the outcome-based logic is especially relevant for customer support and similar automation products.

## Limitations / open questions

The article does not provide the actual pricing formula, the full model outputs, or the decision thresholds behind the final recommendation. It does not show how well the chosen model performed after launch, so there is no evidence here on forecast accuracy or realized margins. The discussion of Gabor-Granger and Van Westendorp is method-level, but the article gives only illustrative data, not a reproducible study design. It also leaves open how Intercom balances simplicity against increasing product breadth as Fin becomes more platform-like. The operational burden of rollout, sales enablement, customer education, and ROI tooling is acknowledged but not detailed.

## Contradictions / unverified claims

The article argues for a rigorous process, but also says the full process is followed only around half the time, which suggests the method is aspirational as much as operational. Outcome-based pricing sounds clean, but the piece admits that a single model becomes harder to apply as the product set expands. The claim that the chosen metric should track value is persuasive, but the article does not test whether customers actually experience the metric as fair over time. The narrative is internally coherent, but it is still one company’s self-reported process rather than comparative evidence.

## Source metadata

- Canonical URL: https://www.intercom.com/blog/how-we-develop-pricing-and-packaging-at-fin/
- Raw markdown: `raw/readwise/how-we-develop-pricing-and-packaging-at-fin-01ks2ns7k02qfhbcgkc41wqe3v.md`
- Raw HTML: `raw/readwise/how-we-develop-pricing-and-packaging-at-fin-01ks2ns7k02qfhbcgkc41wqe3v.html`
