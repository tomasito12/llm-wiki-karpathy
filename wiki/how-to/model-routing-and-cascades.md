---
title: Model Routing And Cascades
slug: model-routing-and-cascades
entity_id: how_to:model-routing-and-cascades
category: how-to
tags:
- agent-evals
- ai-economics
- inference-systems
- model-behavior
- orchestration
- support-automation
first_seen: '2026-04-17'
last_seen: '2026-05-08'
source_count: 2
evidence_count: 25
source_ids:
- 8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9
- agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv
value_level: high
confidence: 0.93
synthesis_state: stage1-placeholder
---

# Model Routing And Cascades

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Model routing sends each request to the cheapest model that can handle it well enough. It is useful when simple classification, extraction, or short answers are getting routed to expensive frontier models. The problem is overspending on easy requests while reserving high-cost models only for genuinely hard ones. Routing creates a tiered system instead of one expensive default model. That usually makes cost more proportional to task difficulty.

## Caveats

The article explicitly says to start conservative because wrong routing can produce visibly bad output. The suggested tier splits and savings are workload-dependent and should be treated as guidance, not universal rules, as of 2026-04-17.

## Implementation Steps

- Define request features that correlate with complexity.
- Build a simple classifier or rules layer.
- Map simple, medium, and complex requests to different model tiers.
- Start with conservative routing thresholds.
- Review misroutes and adjust the classifier over time.
- Estimate task difficulty or intent before selecting a model, or let a cheap model answer first.
- Add a lightweight checker that can judge confidence, uncertainty, or semantic alignment.
- Set escalation thresholds conservatively at first.
- Compare simple heuristics, embedding-based routing, and learned routers on your own traffic.
- Measure both quality and savings, not cost alone.
- Use the routing path that preserves acceptable answer quality for the lowest spend.

## Prerequisites

- Access to at least two model tiers
- A routing signal or classifier
- A quality evaluation loop
- A set of models with different cost or quality levels.
- Traffic that contains both easy and hard tasks.
- A way to evaluate answer quality after routing or escalation.

## Evidence / supporting sources

### 8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained) (2026-04-17)

- Classify incoming requests by difficulty before calling a model. Send simple tasks to a small or cheap model, medium tasks to a mid-tier model, and only the hardest tasks to a frontier model. Start conservatively so you do not misroute complex requests to weak models. Use signals such as request length, keywords, task type, and expected output length. Monitor quality carefully, because a bad routing decision is visible to users. (`cdbf9d092232` · neutral · answer_summary; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- Define request features that correlate with complexity. (`65b12546845f` · neutral · implementation_steps[0]; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- Build a simple classifier or rules layer. (`6316a5f6a1dd` · neutral · implementation_steps[1]; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- Map simple, medium, and complex requests to different model tiers. (`c1b800ba1a2d` · neutral · implementation_steps[2]; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- Start with conservative routing thresholds. (`fc7b3d8609fa` · neutral · implementation_steps[3]; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- Review misroutes and adjust the classifier over time. (`374ef020f788` · neutral · implementation_steps[4]; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- Access to at least two model tiers (`9d137418c22a` · neutral · prerequisites[0]; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- A routing signal or classifier (`c2d1ee1616e0` · neutral · prerequisites[1]; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- A quality evaluation loop (`efee670fe539` · neutral · prerequisites[2]; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- Model routing sends each request to the cheapest model that can handle it well enough. It is useful when simple classification, extraction, or short answers are getting routed to expensive frontier models. The problem is overspending on easy requests while reserving high-cost models only for genuinely hard ones. Routing creates a tiered system instead of one expensive default model. That usually makes cost more proportional to task difficulty. (`85df868d874b` · neutral · what_and_problem; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- "Model routing classifies each incoming request and sends it to the appropriate model tier. Simple requests go to cheap models. Complex requests go to capable ones." (`39e70e644952` · supporting · supporting_snippet; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- The article explicitly says to start conservative because wrong routing can produce visibly bad output. The suggested tier splits and savings are workload-dependent and should be treated as guidance, not universal rules, as of 2026-04-17. (`7b994434a0c9` · uncertainty · caveats; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])

### Agentic AI: How to Save on Tokens (2026-05-08)

- If you route up front, build a classifier or heuristic that estimates task difficulty and sends the request to the right model. If you cascade, let a cheaper model answer first, then check whether the answer looks strong enough before accepting it. Use conservative thresholds so weak answers are escalated rather than trusted too easily. Evaluate the system against your own tasks, because router quality and cost savings depend heavily on workload. Choose this approach when your traffic includes a mix of easy and hard requests and you can tolerate some added complexity. (`c50b8e6cb74b` · neutral · answer_summary; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- Estimate task difficulty or intent before selecting a model, or let a cheap model answer first. (`07b55f76b6d4` · neutral · implementation_steps[0]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- Add a lightweight checker that can judge confidence, uncertainty, or semantic alignment. (`2b9c419b14dc` · neutral · implementation_steps[1]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- Set escalation thresholds conservatively at first. (`80cda25cd983` · neutral · implementation_steps[2]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- Compare simple heuristics, embedding-based routing, and learned routers on your own traffic. (`9b988226ac8e` · neutral · implementation_steps[3]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- Measure both quality and savings, not cost alone. (`09af36a9a518` · neutral · implementation_steps[4]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- Use the routing path that preserves acceptable answer quality for the lowest spend. (`d878fa2ea61d` · neutral · implementation_steps[5]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- A set of models with different cost or quality levels. (`49e3bdea9cd0` · neutral · prerequisites[0]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- Traffic that contains both easy and hard tasks. (`984988ad4f3c` · neutral · prerequisites[1]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- A way to evaluate answer quality after routing or escalation. (`3a14f5d3ceff` · neutral · prerequisites[2]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- Model routing and cascades are ways to send easy work to cheaper models and reserve stronger models for harder work. They solve the problem of paying top-model prices for tasks that do not need them. Routing decides up front where a request should go, while cascades let a cheap model answer first and escalate only if needed. Both approaches try to reduce cost without giving up too much answer quality. (`3786891eaef8` · neutral · what_and_problem; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- "route to smaller models, or escalate to a larger model" ... "Start with cheap and cascade on low confidence" ... "Route to models based on task difficulty" (`85f2e888756f` · supporting · supporting_snippet; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- The article explicitly warns that routing can hurt quality if the wrong model is chosen. It also notes that learned routers may barely beat simple heuristics in some benchmarks, so fancy routing is not automatically better. Cascades require extra calls for escalated requests, so they only make sense when many requests can be handled cheaply. (`9173c2ec1289` · uncertainty · caveats; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])

## Contradictions / tensions

- The article explicitly says to start conservative because wrong routing can produce visibly bad output. The suggested tier splits and savings are workload-dependent and should be treated as guidance, not universal rules, as of 2026-04-17. (uncertainty; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- The article explicitly warns that routing can hurt quality if the wrong model is chosen. It also notes that learned routers may barely beat simple heuristics in some benchmarks, so fancy routing is not automatically better. Cascades require extra calls for escalated requests, so they only make sense when many requests can be handled cheaply. (uncertainty; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])

## Related pages

- [[how-to/semantic-caching|Semantic Caching]]
- [[how-to/prompt-caching|Prompt Caching]]

## Sources

- [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]]
- [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]]
