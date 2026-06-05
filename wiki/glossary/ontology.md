---
title: Ontology
slug: ontology
entity_id: glossary:ontology
category: glossary
tags:
- agent-systems
- memory-systems
- orchestration
first_seen: '2025-12-03'
last_seen: '2026-04-29'
source_count: 3
evidence_count: 12
source_ids:
- ontology-driven-graphrag-a-framework-for-zero-noise-knowledge-extraction-01kqkvd7bwfhpbgqtw20czkk22
- why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8
- you-probably-don-t-need-a-graph-database-for-your-knowledge-graph-01kqz02qzddjehycrjafswxv5r
value_level: high
confidence: 0.9066666666666666
synthesis_state: stage1-placeholder
---

# Ontology

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
A formal representation of concepts, types, properties, and relationships in a domain. It defines the rules a system uses to interpret and structure data consistently.

## Related Terms

- Knowledge Management

## Relevance Note

Ontology is a core primitive for production knowledge systems because it keeps extraction, storage, and reasoning aligned as domains grow. It matters for AI workflows that need stable schema control, traceable facts, and consistent downstream automation.

## Evidence / supporting sources

### Ontology-Driven GraphRAG: A Framework for Zero-Noise Knowledge Extraction (2025-12-03)

- In practice, an ontology acts like a shared contract between documents, extraction logic, validation rules, and downstream queries. It helps systems know what kinds of entities exist, what properties they should have, and how those entities can relate to each other. In knowledge-graph systems, the ontology is often the difference between a pile of extracted records and a graph that can support reliable search, reasoning, and auditing. (`5ba5fe02b863` · neutral · extended_explanation; [[sources/ontology-driven-graphrag-a-framework-for-zero-noise-knowledge-extraction-01kqkvd7bwfhpbgqtw20czkk22|Ontology-Driven GraphRAG: A Framework for Zero-Noise Knowledge Extraction]])
- A formal representation of concepts, types, properties, and relationships in a domain. It defines the rules a system uses to interpret and structure data consistently. (`aefc4b867c13` · neutral · proposed_definition; [[sources/ontology-driven-graphrag-a-framework-for-zero-noise-knowledge-extraction-01kqkvd7bwfhpbgqtw20czkk22|Ontology-Driven GraphRAG: A Framework for Zero-Noise Knowledge Extraction]])
- Ontology is a core primitive for production knowledge systems because it keeps extraction, storage, and reasoning aligned as domains grow. It matters for AI workflows that need stable schema control, traceable facts, and consistent downstream automation. (`f646eeeceb18` · neutral · relevance_note; [[sources/ontology-driven-graphrag-a-framework-for-zero-noise-knowledge-extraction-01kqkvd7bwfhpbgqtw20czkk22|Ontology-Driven GraphRAG: A Framework for Zero-Noise Knowledge Extraction]])
- “we made it the central nervous system of the entire pipeline. Our system doesn’t just define what entities exist; it controls extraction, enforces validation, enables reasoning, tracks provenance, and evolves itself based on usage patterns.” (`629ee99a22d3` · supporting · supporting_snippet; [[sources/ontology-driven-graphrag-a-framework-for-zero-noise-knowledge-extraction-01kqkvd7bwfhpbgqtw20czkk22|Ontology-Driven GraphRAG: A Framework for Zero-Noise Knowledge Extraction]])

### Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge (2026-04-06)

- In AI systems, an ontology helps the system avoid treating near-synonyms as separate concepts and gives names to relations such as is-a, part-of, and contradicts. That makes it easier to deduplicate entities, track disagreements, and navigate complex knowledge bases. The value is practical rather than academic: it reduces ambiguity in how the system stores and updates knowledge. (`7e5aec33e896` · neutral · extended_explanation; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])
- A structured set of concepts and relations used to represent a domain in a consistent way. (`a574a75f9752` · neutral · proposed_definition; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])
- Ontologies matter in knowledge systems, agent memory, and structured extraction because they control whether the system can keep concepts stable over time. They are especially useful when AI outputs must support search, contradiction tracking, or multi-step reasoning over a growing corpus. (`3791b51a05f0` · neutral · relevance_note; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])
- The ontology is the hardest part. Concept deduplication — deciding whether “attention mechanism” and “self-attention” should be the same node or different nodes linked by a relation — is where the LLM struggles most. (`2399a5b99304` · supporting · supporting_snippet; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])

### You Probably Don’t Need a Graph Database for Your Knowledge Graph (2026-04-29)

- An ontology defines the important entities in a domain, the kinds of relationships they can have, and sometimes the rules that govern those relationships. In practice, it is used when systems need to share a common vocabulary and reason over that vocabulary consistently. Ontologies often show up in enterprise knowledge systems, semantic search, and rule-based automation. They are more about meaning and constraints than about simple data storage. (`0ee5dbca13b7` · neutral · extended_explanation; [[sources/you-probably-don-t-need-a-graph-database-for-your-knowledge-graph-01kqz02qzddjehycrjafswxv5r|You Probably Don’t Need a Graph Database for Your Knowledge Graph]])
- A formal representation of concepts in a domain and the relationships between them, often used to make meaning machine-readable and support reasoning. (`8fe082206aca` · neutral · proposed_definition; [[sources/you-probably-don-t-need-a-graph-database-for-your-knowledge-graph-01kqz02qzddjehycrjafswxv5r|You Probably Don’t Need a Graph Database for Your Knowledge Graph]])
- Ontologies matter because they give AI systems a structured way to represent domain concepts, constraints, and relationships. They are useful when a chatbot, agent, or knowledge system needs consistent interpretation rather than loose text matching. (`5a3793d96b07` · neutral · relevance_note; [[sources/you-probably-don-t-need-a-graph-database-for-your-knowledge-graph-01kqz02qzddjehycrjafswxv5r|You Probably Don’t Need a Graph Database for Your Knowledge Graph]])
- Practitioners often argue that there’s only one canonical way to represent ontologies — RDF — so a triple store or GraphDB is required. (`1384b102770a` · supporting · supporting_snippet; [[sources/you-probably-don-t-need-a-graph-database-for-your-knowledge-graph-01kqz02qzddjehycrjafswxv5r|You Probably Don’t Need a Graph Database for Your Knowledge Graph]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- Knowledge Management

## Sources

- [[sources/ontology-driven-graphrag-a-framework-for-zero-noise-knowledge-extraction-01kqkvd7bwfhpbgqtw20czkk22|Ontology-Driven GraphRAG: A Framework for Zero-Noise Knowledge Extraction]]
- [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]]
- [[sources/you-probably-don-t-need-a-graph-database-for-your-knowledge-graph-01kqz02qzddjehycrjafswxv5r|You Probably Don’t Need a Graph Database for Your Knowledge Graph]]
