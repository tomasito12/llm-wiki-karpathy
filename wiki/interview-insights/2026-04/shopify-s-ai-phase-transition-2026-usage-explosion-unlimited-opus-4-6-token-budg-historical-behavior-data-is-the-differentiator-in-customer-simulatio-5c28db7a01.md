---
title: Historical behavior data is the differentiator in customer simulation
slug: historical-behavior-data-is-the-differentiator-in-customer-simulation
category: insight
tags:
- agent-systems
- workflow-automation
- multimodal-systems
source_id: shopify-s-ai-phase-transition-2026-usage-explosion-unlimited-opus-4-6-token-budget-tangle-tangent-simgym-with-mikhail-parakhin-shopify-cto-01kpvbfa6cdva1b08psggsea8q
source_title: 'Shopify’s AI Phase Transition: 2026 Usage Explosion, Unlimited Opus-4.6
  Token Budget, Tangle, Tangent, SimGym — with Mikhail Parakhin, Shopify CTO'
source_date: '2026-04-22'
month: 2026-04
evidence_count: 8
evidence_set_hash: 0e6b463e5929f132
insight_title: Historical behavior data is the differentiator in customer simulation
insight_type: service_automation
confidence: high
durability_estimate: long_term
wiki_worthiness: strong_candidate
---

# Historical behavior data is the differentiator in customer simulation

## Interview Insight

### Summary

SimGym is positioned as a customer-simulation system that only becomes meaningful because Shopify has decades of historical merchant and buyer behavior. Without that data, Parakhin says simulated agents would just repeat the prompt; with it, Shopify can denoise behavior, run counterfactuals, and predict the effect of storefront changes or interventions. He also says the system was later reframed from comparing two variants to recommending what a single merchant should change.

### Why It Matters

Actionable as of 2026-04-22 because it shows that simulation quality in commerce depends more on proprietary behavioral history than on generic prompt quality. That makes the idea highly relevant to companies with rich event histories and much less portable elsewhere. The article is careful that the claims are Shopify-specific and infrastructure-heavy, so the takeaway is architectural rather than universal.

### Operational Relevance

Use historical interaction logs to ground simulated agents, then evaluate counterfactual interventions on conversion-sensitive paths. Expect high infrastructure cost: multimodal models, browser farms, distillation, and many simulation runs are all part of the operating envelope.

### Service Automation Relevance

Strong relevance for conversational commerce and support automation: the same historical grounding principle can improve recommendation, intervention timing, and outcome prediction when agents act on behalf of users or merchants.

### Mentioned Entities

- SimGym
- Shopify
- HSTU
- CRP
- browser farms

### Suggested Destinations

- topics/

### Contrarian Or Speculative Claims

- The transcript suggests simulated customers are useful only when they are anchored by real historical behavior, which makes the approach far less general than prompt-only agents.

### Evidence Snippets

- "if you don’t have the historical data, all you can do is prompt agents in a vacuum, and they will do exactly what you prompt them to do."
- "we have decades of history of how people made changes and what there is, uh, there, what it resulted in terms of sales."
- "we have a huge HSTU-based system that models the whole companies, uh, and their possible paths."

## Evidence / supporting sources

### Shopify’s AI Phase Transition: 2026 Usage Explosion, Unlimited Opus-4.6 Token Budget, Tangle, Tangent, SimGym — with Mikhail Parakhin, Shopify CTO (2026-04-22)

- The transcript suggests simulated customers are useful only when they are anchored by real historical behavior, which makes the approach far less general than prompt-only agents. (`9503b2d979a8` · counter · contrarian_or_speculative_claims[0]; [[sources/shopify-s-ai-phase-transition-2026-usage-explosion-unlimited-opus-4-6-token-budget-tangle-tangent-simgym-with-mikhail-parakhin-shopify-cto-01kpvbfa6cdva1b08psggsea8q|Shopify’s AI Phase Transition: 2026 Usage Explosion, Unlimited Opus-4.6 Token Budget, Tangle, Tangent, SimGym — with Mikhail Parakhin, Shopify CTO]])
- Use historical interaction logs to ground simulated agents, then evaluate counterfactual interventions on conversion-sensitive paths. Expect high infrastructure cost: multimodal models, browser farms, distillation, and many simulation runs are all part of the operating envelope. (`ada11e4db3b8` · neutral · operational_relevance; [[sources/shopify-s-ai-phase-transition-2026-usage-explosion-unlimited-opus-4-6-token-budget-tangle-tangent-simgym-with-mikhail-parakhin-shopify-cto-01kpvbfa6cdva1b08psggsea8q|Shopify’s AI Phase Transition: 2026 Usage Explosion, Unlimited Opus-4.6 Token Budget, Tangle, Tangent, SimGym — with Mikhail Parakhin, Shopify CTO]])
- Strong relevance for conversational commerce and support automation: the same historical grounding principle can improve recommendation, intervention timing, and outcome prediction when agents act on behalf of users or merchants. (`47b4d98dcb07` · neutral · service_automation_relevance; [[sources/shopify-s-ai-phase-transition-2026-usage-explosion-unlimited-opus-4-6-token-budget-tangle-tangent-simgym-with-mikhail-parakhin-shopify-cto-01kpvbfa6cdva1b08psggsea8q|Shopify’s AI Phase Transition: 2026 Usage Explosion, Unlimited Opus-4.6 Token Budget, Tangle, Tangent, SimGym — with Mikhail Parakhin, Shopify CTO]])
- SimGym is positioned as a customer-simulation system that only becomes meaningful because Shopify has decades of historical merchant and buyer behavior. Without that data, Parakhin says simulated agents would just repeat the prompt; with it, Shopify can denoise behavior, run counterfactuals, and predict the effect of storefront changes or interventions. He also says the system was later reframed from comparing two variants to recommending what a single merchant should change. (`8d84386b8145` · neutral · summary; [[sources/shopify-s-ai-phase-transition-2026-usage-explosion-unlimited-opus-4-6-token-budget-tangle-tangent-simgym-with-mikhail-parakhin-shopify-cto-01kpvbfa6cdva1b08psggsea8q|Shopify’s AI Phase Transition: 2026 Usage Explosion, Unlimited Opus-4.6 Token Budget, Tangle, Tangent, SimGym — with Mikhail Parakhin, Shopify CTO]])
- Actionable as of 2026-04-22 because it shows that simulation quality in commerce depends more on proprietary behavioral history than on generic prompt quality. That makes the idea highly relevant to companies with rich event histories and much less portable elsewhere. The article is careful that the claims are Shopify-specific and infrastructure-heavy, so the takeaway is architectural rather than universal. (`e0c82fa1f876` · neutral · why_it_matters; [[sources/shopify-s-ai-phase-transition-2026-usage-explosion-unlimited-opus-4-6-token-budget-tangle-tangent-simgym-with-mikhail-parakhin-shopify-cto-01kpvbfa6cdva1b08psggsea8q|Shopify’s AI Phase Transition: 2026 Usage Explosion, Unlimited Opus-4.6 Token Budget, Tangle, Tangent, SimGym — with Mikhail Parakhin, Shopify CTO]])
- "if you don’t have the historical data, all you can do is prompt agents in a vacuum, and they will do exactly what you prompt them to do." (`5e00a17f02ee` · supporting · evidence_snippets[0]; [[sources/shopify-s-ai-phase-transition-2026-usage-explosion-unlimited-opus-4-6-token-budget-tangle-tangent-simgym-with-mikhail-parakhin-shopify-cto-01kpvbfa6cdva1b08psggsea8q|Shopify’s AI Phase Transition: 2026 Usage Explosion, Unlimited Opus-4.6 Token Budget, Tangle, Tangent, SimGym — with Mikhail Parakhin, Shopify CTO]])
- "we have decades of history of how people made changes and what there is, uh, there, what it resulted in terms of sales." (`b22bee132eb3` · supporting · evidence_snippets[1]; [[sources/shopify-s-ai-phase-transition-2026-usage-explosion-unlimited-opus-4-6-token-budget-tangle-tangent-simgym-with-mikhail-parakhin-shopify-cto-01kpvbfa6cdva1b08psggsea8q|Shopify’s AI Phase Transition: 2026 Usage Explosion, Unlimited Opus-4.6 Token Budget, Tangle, Tangent, SimGym — with Mikhail Parakhin, Shopify CTO]])
- "we have a huge HSTU-based system that models the whole companies, uh, and their possible paths." (`fc227ed4ae48` · supporting · evidence_snippets[2]; [[sources/shopify-s-ai-phase-transition-2026-usage-explosion-unlimited-opus-4-6-token-budget-tangle-tangent-simgym-with-mikhail-parakhin-shopify-cto-01kpvbfa6cdva1b08psggsea8q|Shopify’s AI Phase Transition: 2026 Usage Explosion, Unlimited Opus-4.6 Token Budget, Tangle, Tangent, SimGym — with Mikhail Parakhin, Shopify CTO]])

## Source

- [[sources/shopify-s-ai-phase-transition-2026-usage-explosion-unlimited-opus-4-6-token-budget-tangle-tangent-simgym-with-mikhail-parakhin-shopify-cto-01kpvbfa6cdva1b08psggsea8q|Shopify’s AI Phase Transition: 2026 Usage Explosion, Unlimited Opus-4.6 Token Budget, Tangle, Tangent, SimGym — with Mikhail Parakhin, Shopify CTO]]
