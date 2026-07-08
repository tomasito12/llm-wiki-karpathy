---
title: Behavior-Driven Development
slug: behavior-driven-development
entity_id: glossary:behavior-driven-development
category: glossary
tags:
- context-engineering
- tool-use
first_seen: '2026-04-30'
last_seen: '2026-04-30'
source_count: 1
evidence_count: 4
source_ids:
- sdd-writing-specifications-for-ai-bdd-as-the-missing-link-spec-driven-development-01kqz04y32hqhskkq6c3jh3esj
value_level: high
confidence: 0.95
synthesis_state: stage1-placeholder
---

# Behavior-Driven Development

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
A software development approach that describes system behavior in natural language examples and uses those examples as a shared basis for implementation and testing. It typically expresses behavior in Given/When/Then form so business stakeholders and technical systems can read the same intent.

## Relevance Note

BDD matters in AI engineering because it gives teams a compact, machine-readable way to specify behavior for agents, chatbots, and automated workflows. It is especially relevant when ambiguity in the request would otherwise lead to inconsistent outputs, brittle tests, or repeated human clarification.

## Evidence / supporting sources

### SDD Writing Specifications for AI: BDD as the Missing Link — Spec-Driven Development (2026-04-30)

- BDD is useful when teams need a specification that people can review without translation but that tools can also execute. The core idea is to define behavior in concrete scenarios rather than abstract requirements, which reduces ambiguity about what the system should do. In practice, BDD often sits between a high-level requirement document and code, making it easier to align product, development, and testing around the same example. It is especially valuable when an implementation agent or automation tool can turn those scenarios into executable tests or step definitions. (`68bb8da20698` · neutral · extended_explanation; [[sources/sdd-writing-specifications-for-ai-bdd-as-the-missing-link-spec-driven-development-01kqz04y32hqhskkq6c3jh3esj|SDD Writing Specifications for AI: BDD as the Missing Link — Spec-Driven Development]])
- A software development approach that describes system behavior in natural language examples and uses those examples as a shared basis for implementation and testing. It typically expresses behavior in Given/When/Then form so business stakeholders and technical systems can read the same intent. (`ccabd96b2290` · neutral · proposed_definition; [[sources/sdd-writing-specifications-for-ai-bdd-as-the-missing-link-spec-driven-development-01kqz04y32hqhskkq6c3jh3esj|SDD Writing Specifications for AI: BDD as the Missing Link — Spec-Driven Development]])
- BDD matters in AI engineering because it gives teams a compact, machine-readable way to specify behavior for agents, chatbots, and automated workflows. It is especially relevant when ambiguity in the request would otherwise lead to inconsistent outputs, brittle tests, or repeated human clarification. (`95bd40702bd9` · neutral · relevance_note; [[sources/sdd-writing-specifications-for-ai-bdd-as-the-missing-link-spec-driven-development-01kqz04y32hqhskkq6c3jh3esj|SDD Writing Specifications for AI: BDD as the Missing Link — Spec-Driven Development]])
- “BDD (Behavior-Driven Development) — a methodology for describing system behavior in natural language, readable by the business and executable by machines, using Given/When/Then scenarios.” (`e54ccef3963b` · supporting · supporting_snippet; [[sources/sdd-writing-specifications-for-ai-bdd-as-the-missing-link-spec-driven-development-01kqz04y32hqhskkq6c3jh3esj|SDD Writing Specifications for AI: BDD as the Missing Link — Spec-Driven Development]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- [[glossary/gherkin|Gherkin]]

## Sources

- [[sources/sdd-writing-specifications-for-ai-bdd-as-the-missing-link-spec-driven-development-01kqz04y32hqhskkq6c3jh3esj|SDD Writing Specifications for AI: BDD as the Missing Link — Spec-Driven Development]]
