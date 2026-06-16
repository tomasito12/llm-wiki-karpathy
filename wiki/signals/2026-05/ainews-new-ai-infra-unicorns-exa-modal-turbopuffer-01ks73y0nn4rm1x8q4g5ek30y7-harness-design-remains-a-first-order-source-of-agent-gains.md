---
title: Harness design remains a first-order source of agent gains
slug: harness-design-remains-a-first-order-source-of-agent-gains
category: signal
tags:
- continuous-evaluation
- workflow-based-evaluation
- execution-oriented-agents
- tool-centric-agents
source_id: ainews-new-ai-infra-unicorns-exa-modal-turbopuffer-01ks73y0nn4rm1x8q4g5ek30y7
source_title: '[AINews] New AI Infra unicorns: Exa, Modal, TurboPuffer'
source_date: '2026-05-22'
month: 2026-05
evidence_count: 6
evidence_set_hash: 68a849be93bf9d0a
signal_title: Harness design remains a first-order source of agent gains
signal_type: research_eval
signal_strength: high
time_horizon: medium_term
wiki_worthiness: strong_candidate
---

# Harness design remains a first-order source of agent gains

## Signal

### Summary

The roundup repeatedly shows that scaffolding can materially change agent performance. One harness raised Gemini 3.1 Pro from 17.7 to 31.4 on a science-problem setup, while GPT 5.5 Pro did not benefit from the same harness. That makes the model-harness pairing an operational variable, not just a cosmetic wrapper.

### Why It Matters

As of 2026-05-22, teams building agents should treat harness design as part of the system budget. A good evaluation or control layer can produce large gains, but the source also shows those gains are not portable across all models.

### Operational Relevance

Invest in task-specific harnesses, evaluate model-harness fit, and do not assume prompt-only improvements will generalize across models or domains.

### Service Automation Relevance

This is relevant to support automation because workflow wrappers, validation steps, and tool gating can materially improve task completion quality. The same caution applies: one model may benefit more than another from the same scaffold.

### Mentioned Entities

- Gemini 3.1 Pro
- GPT 5.5 Pro
- physics-intern
- mini-swe-agent

### Suggested Destinations

- trends/

### Evidence Snippets

- Harnesses are still a major source of capability gains : @lvwerra released physics-intern, a science-problem harness that boosts models like Gemini 3.1 Pro from 17.7 to 31.4, surpassing GPT 5.5 Pro in that setup.
- The notable nuance is that GPT 5.5 Pro itself did not benefit from the harness, suggesting model-specific absorption of scaffolding tricks.

## Evidence / supporting sources

### [AINews] New AI Infra unicorns: Exa, Modal, TurboPuffer (2026-05-22)

- Invest in task-specific harnesses, evaluate model-harness fit, and do not assume prompt-only improvements will generalize across models or domains. (`99f91add4918` · neutral · operational_relevance; [[sources/ainews-new-ai-infra-unicorns-exa-modal-turbopuffer-01ks73y0nn4rm1x8q4g5ek30y7|[AINews] New AI Infra unicorns: Exa, Modal, TurboPuffer]])
- This is relevant to support automation because workflow wrappers, validation steps, and tool gating can materially improve task completion quality. The same caution applies: one model may benefit more than another from the same scaffold. (`e59c83a6d952` · neutral · service_automation_relevance; [[sources/ainews-new-ai-infra-unicorns-exa-modal-turbopuffer-01ks73y0nn4rm1x8q4g5ek30y7|[AINews] New AI Infra unicorns: Exa, Modal, TurboPuffer]])
- The roundup repeatedly shows that scaffolding can materially change agent performance. One harness raised Gemini 3.1 Pro from 17.7 to 31.4 on a science-problem setup, while GPT 5.5 Pro did not benefit from the same harness. That makes the model-harness pairing an operational variable, not just a cosmetic wrapper. (`d9d5cd32220e` · neutral · summary; [[sources/ainews-new-ai-infra-unicorns-exa-modal-turbopuffer-01ks73y0nn4rm1x8q4g5ek30y7|[AINews] New AI Infra unicorns: Exa, Modal, TurboPuffer]])
- As of 2026-05-22, teams building agents should treat harness design as part of the system budget. A good evaluation or control layer can produce large gains, but the source also shows those gains are not portable across all models. (`72c12909fb2d` · neutral · why_it_matters; [[sources/ainews-new-ai-infra-unicorns-exa-modal-turbopuffer-01ks73y0nn4rm1x8q4g5ek30y7|[AINews] New AI Infra unicorns: Exa, Modal, TurboPuffer]])
- Harnesses are still a major source of capability gains : @lvwerra released physics-intern, a science-problem harness that boosts models like Gemini 3.1 Pro from 17.7 to 31.4, surpassing GPT 5.5 Pro in that setup. (`2baf4a21aca1` · supporting · evidence_snippets[0]; [[sources/ainews-new-ai-infra-unicorns-exa-modal-turbopuffer-01ks73y0nn4rm1x8q4g5ek30y7|[AINews] New AI Infra unicorns: Exa, Modal, TurboPuffer]])
- The notable nuance is that GPT 5.5 Pro itself did not benefit from the harness, suggesting model-specific absorption of scaffolding tricks. (`c45a70d4601e` · supporting · evidence_snippets[1]; [[sources/ainews-new-ai-infra-unicorns-exa-modal-turbopuffer-01ks73y0nn4rm1x8q4g5ek30y7|[AINews] New AI Infra unicorns: Exa, Modal, TurboPuffer]])

## Source

- [[sources/ainews-new-ai-infra-unicorns-exa-modal-turbopuffer-01ks73y0nn4rm1x8q4g5ek30y7|[AINews] New AI Infra unicorns: Exa, Modal, TurboPuffer]]
