---
title: Lippert's Cognigy Support Automation Rollout
slug: lippert-s-cognigy-support-automation-rollout
category: implementation-study
tags:
- support-automation
- customer-support
- enterprise-ai
source_id: lippert-s-ai-agent-cuts-costs-by-80-and-boosts-sales-01krxb2zvf0njv32xzz3djwk13
source_title: Lippert's AI Agent Cuts Costs by 80% and Boosts Sales
source_date: unknown
month: unknown
company: Lippert
industry: caravanning, marine, and rail components
evidence_count: 23
evidence_set_hash: bc037fa73f28d528
---

# Lippert's Cognigy Support Automation Rollout

## Implementation Study

### Overview

Lippert deployed Cognigy AI Agents to handle complex customer support requests that required detailed product knowledge. The reported rollout focused on chat-based self-service for part pricing, availability, and order status tracking, with business users managing the system internally.

### What was implemented?

Cognigy.AI chat agents, with planned expansion into Voice AI Agent, Knowledge AI search, and Agent Copilot.

### Business objective

Reduce support cost, streamline handling of complex inventory and customer questions, and improve customer experience while preserving answer quality.

### Technical approach

The source says Lippert used lexicons and metadata to train agents in industry-specific terminology and gave business users a simple UI to expand and adjust agents internally.

### Deployment context

Customer support operations for a manufacturer supplying components across caravanning, marine, and rail industries; the article describes live use on chat and a planned expansion roadmap.

### Outcome / current status

The source reports a 37% containment rate and an 80% reduction in costs for handled queries, plus an increase in online store conversion rates. The roadmap section says Lippert plans to extend the deployment into voice, search, and agent assistance.

### Why it succeeded or struggled

The reported success appears tied to narrow, high-volume intents and the use of domain terminology support. The source also suggests internal manageability mattered because business users were expected to maintain and scale the agents.

### Operational constraints

About 80% of customer contacts involved intricate queries requiring in-depth product knowledge, and interactions typically lasted 5–7 minutes because details such as specific parts had to be gathered.

### AI / model observations

The case suggests conversational systems are most valuable when they can reliably ground answers in structured product knowledge and terminology. It also shows that operational control and content maintenance may matter as much as model capability.

### Implications for service automation

This is directly relevant to service automation because it shows a support system being used for containment, cost reduction, and possibly conversion uplift. The source does not provide enough detail to judge handoff behavior, error handling, or governance, so those operational pieces remain open.

### Strategic signals

The deployment combines support automation with ecommerce impact, suggesting the support layer can influence revenue as well as cost. It also signals a platform expansion path from chat into voice, retrieval, and copilot-style assistance rather than a single use case.

### Key Lessons

- Start with information-heavy support intents that recur at high volume.
- Use domain terminology support when products or parts are highly specific.
- Give business users enough control to maintain and extend the system.
- Treat cost reduction and containment as separate metrics from conversion impact.

### Open Questions

- How was containment measured?
- What baseline and time period were used for the 80% cost reduction?
- How much of the conversion lift came from the AI Agents versus other site changes?
- What fallback and human handoff design was used?
- How were knowledge quality and answer accuracy monitored?

### Related Sources

- https://www.cognigy.com/en/case-study/lippert

### Evidence Snippets

- Lippert had a high proportion of complex support contacts requiring specialized knowledge. — Approximately 80% of customer contacts involved intricate queries necessitating in-depth product knowledge. (stated)
- The implementation used chat agents for specific support use cases. — With Cognigy, Lippert launched AI Agents on chat for key use cases: part pricing, availability, and order status tracking. (stated)
- Reported outcomes included containment, cost reduction, and conversion lift. — Using AI has allowed Lippert to achieve a 37% containment rate, resulting in an 80% cost reduction from handled queries. The efficiency and usability of the AI self-service has also increased the conversion rate for its online store purchases. (stated)

## Evidence / supporting sources

### Lippert's AI Agent Cuts Costs by 80% and Boosts Sales (undated)

- The case suggests conversational systems are most valuable when they can reliably ground answers in structured product knowledge and terminology. It also shows that operational control and content maintenance may matter as much as model capability. (`436cce83e178` · neutral · ai_model_observations; [[sources/lippert-s-ai-agent-cuts-costs-by-80-and-boosts-sales-01krxb2zvf0njv32xzz3djwk13|Lippert's AI Agent Cuts Costs by 80% and Boosts Sales]])
- Reduce support cost, streamline handling of complex inventory and customer questions, and improve customer experience while preserving answer quality. (`546fb146948c` · neutral · business_objective; [[sources/lippert-s-ai-agent-cuts-costs-by-80-and-boosts-sales-01krxb2zvf0njv32xzz3djwk13|Lippert's AI Agent Cuts Costs by 80% and Boosts Sales]])
- Customer support operations for a manufacturer supplying components across caravanning, marine, and rail industries; the article describes live use on chat and a planned expansion roadmap. (`10e230b54fcf` · neutral · deployment_context; [[sources/lippert-s-ai-agent-cuts-costs-by-80-and-boosts-sales-01krxb2zvf0njv32xzz3djwk13|Lippert's AI Agent Cuts Costs by 80% and Boosts Sales]])
- This is directly relevant to service automation because it shows a support system being used for containment, cost reduction, and possibly conversion uplift. The source does not provide enough detail to judge handoff behavior, error handling, or governance, so those operational pieces remain open. (`6f1f3f97c92e` · neutral · implications_for_service_automation; [[sources/lippert-s-ai-agent-cuts-costs-by-80-and-boosts-sales-01krxb2zvf0njv32xzz3djwk13|Lippert's AI Agent Cuts Costs by 80% and Boosts Sales]])
- How was containment measured? (`521d727bc1a5` · neutral · open_questions[0]; [[sources/lippert-s-ai-agent-cuts-costs-by-80-and-boosts-sales-01krxb2zvf0njv32xzz3djwk13|Lippert's AI Agent Cuts Costs by 80% and Boosts Sales]])
- What baseline and time period were used for the 80% cost reduction? (`97894fed413b` · neutral · open_questions[1]; [[sources/lippert-s-ai-agent-cuts-costs-by-80-and-boosts-sales-01krxb2zvf0njv32xzz3djwk13|Lippert's AI Agent Cuts Costs by 80% and Boosts Sales]])
- How much of the conversion lift came from the AI Agents versus other site changes? (`94ea0980a5f6` · neutral · open_questions[2]; [[sources/lippert-s-ai-agent-cuts-costs-by-80-and-boosts-sales-01krxb2zvf0njv32xzz3djwk13|Lippert's AI Agent Cuts Costs by 80% and Boosts Sales]])
- What fallback and human handoff design was used? (`d49ddff41f51` · neutral · open_questions[3]; [[sources/lippert-s-ai-agent-cuts-costs-by-80-and-boosts-sales-01krxb2zvf0njv32xzz3djwk13|Lippert's AI Agent Cuts Costs by 80% and Boosts Sales]])
- How were knowledge quality and answer accuracy monitored? (`165641175bef` · neutral · open_questions[4]; [[sources/lippert-s-ai-agent-cuts-costs-by-80-and-boosts-sales-01krxb2zvf0njv32xzz3djwk13|Lippert's AI Agent Cuts Costs by 80% and Boosts Sales]])
- About 80% of customer contacts involved intricate queries requiring in-depth product knowledge, and interactions typically lasted 5–7 minutes because details such as specific parts had to be gathered. (`1a47ce767760` · neutral · operational_constraints; [[sources/lippert-s-ai-agent-cuts-costs-by-80-and-boosts-sales-01krxb2zvf0njv32xzz3djwk13|Lippert's AI Agent Cuts Costs by 80% and Boosts Sales]])
- The source reports a 37% containment rate and an 80% reduction in costs for handled queries, plus an increase in online store conversion rates. The roadmap section says Lippert plans to extend the deployment into voice, search, and agent assistance. (`939eec9d75fa` · neutral · outcome_status; [[sources/lippert-s-ai-agent-cuts-costs-by-80-and-boosts-sales-01krxb2zvf0njv32xzz3djwk13|Lippert's AI Agent Cuts Costs by 80% and Boosts Sales]])
- Lippert deployed Cognigy AI Agents to handle complex customer support requests that required detailed product knowledge. The reported rollout focused on chat-based self-service for part pricing, availability, and order status tracking, with business users managing the system internally. (`76a07ea5e342` · neutral · overview; [[sources/lippert-s-ai-agent-cuts-costs-by-80-and-boosts-sales-01krxb2zvf0njv32xzz3djwk13|Lippert's AI Agent Cuts Costs by 80% and Boosts Sales]])
- The deployment combines support automation with ecommerce impact, suggesting the support layer can influence revenue as well as cost. It also signals a platform expansion path from chat into voice, retrieval, and copilot-style assistance rather than a single use case. (`5482a4c07192` · neutral · strategic_signals; [[sources/lippert-s-ai-agent-cuts-costs-by-80-and-boosts-sales-01krxb2zvf0njv32xzz3djwk13|Lippert's AI Agent Cuts Costs by 80% and Boosts Sales]])
- The reported success appears tied to narrow, high-volume intents and the use of domain terminology support. The source also suggests internal manageability mattered because business users were expected to maintain and scale the agents. (`06141d947a65` · neutral · success_or_failure_factors; [[sources/lippert-s-ai-agent-cuts-costs-by-80-and-boosts-sales-01krxb2zvf0njv32xzz3djwk13|Lippert's AI Agent Cuts Costs by 80% and Boosts Sales]])
- The source says Lippert used lexicons and metadata to train agents in industry-specific terminology and gave business users a simple UI to expand and adjust agents internally. (`e6e589da612b` · neutral · technical_approach; [[sources/lippert-s-ai-agent-cuts-costs-by-80-and-boosts-sales-01krxb2zvf0njv32xzz3djwk13|Lippert's AI Agent Cuts Costs by 80% and Boosts Sales]])
- Cognigy.AI chat agents, with planned expansion into Voice AI Agent, Knowledge AI search, and Agent Copilot. (`1ce17ffc30f1` · neutral · what_was_implemented; [[sources/lippert-s-ai-agent-cuts-costs-by-80-and-boosts-sales-01krxb2zvf0njv32xzz3djwk13|Lippert's AI Agent Cuts Costs by 80% and Boosts Sales]])
- Lippert had a high proportion of complex support contacts requiring specialized knowledge. — Approximately 80% of customer contacts involved intricate queries necessitating in-depth product knowledge. (`7c4674adf886` · supporting · evidence_snippets[0]; [[sources/lippert-s-ai-agent-cuts-costs-by-80-and-boosts-sales-01krxb2zvf0njv32xzz3djwk13|Lippert's AI Agent Cuts Costs by 80% and Boosts Sales]])
- The implementation used chat agents for specific support use cases. — With Cognigy, Lippert launched AI Agents on chat for key use cases: part pricing, availability, and order status tracking. (`c561558dcc40` · supporting · evidence_snippets[1]; [[sources/lippert-s-ai-agent-cuts-costs-by-80-and-boosts-sales-01krxb2zvf0njv32xzz3djwk13|Lippert's AI Agent Cuts Costs by 80% and Boosts Sales]])
- Reported outcomes included containment, cost reduction, and conversion lift. — Using AI has allowed Lippert to achieve a 37% containment rate, resulting in an 80% cost reduction from handled queries. The efficiency and usability of the AI self-service has also increased the conversion rate for its online store purchases. (`7d42105f5878` · supporting · evidence_snippets[2]; [[sources/lippert-s-ai-agent-cuts-costs-by-80-and-boosts-sales-01krxb2zvf0njv32xzz3djwk13|Lippert's AI Agent Cuts Costs by 80% and Boosts Sales]])
- Start with information-heavy support intents that recur at high volume. (`22f42be0397c` · supporting · key_lessons[0]; [[sources/lippert-s-ai-agent-cuts-costs-by-80-and-boosts-sales-01krxb2zvf0njv32xzz3djwk13|Lippert's AI Agent Cuts Costs by 80% and Boosts Sales]])
- Use domain terminology support when products or parts are highly specific. (`b680b53ee31c` · supporting · key_lessons[1]; [[sources/lippert-s-ai-agent-cuts-costs-by-80-and-boosts-sales-01krxb2zvf0njv32xzz3djwk13|Lippert's AI Agent Cuts Costs by 80% and Boosts Sales]])
- Give business users enough control to maintain and extend the system. (`09c26fae29a4` · supporting · key_lessons[2]; [[sources/lippert-s-ai-agent-cuts-costs-by-80-and-boosts-sales-01krxb2zvf0njv32xzz3djwk13|Lippert's AI Agent Cuts Costs by 80% and Boosts Sales]])
- Treat cost reduction and containment as separate metrics from conversion impact. (`eb8b38a4402f` · supporting · key_lessons[3]; [[sources/lippert-s-ai-agent-cuts-costs-by-80-and-boosts-sales-01krxb2zvf0njv32xzz3djwk13|Lippert's AI Agent Cuts Costs by 80% and Boosts Sales]])

## Source

- [[sources/lippert-s-ai-agent-cuts-costs-by-80-and-boosts-sales-01krxb2zvf0njv32xzz3djwk13|Lippert's AI Agent Cuts Costs by 80% and Boosts Sales]]
