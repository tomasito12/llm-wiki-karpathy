---
title: Ontology-Driven Extraction
slug: ontology-driven-extraction
entity_id: topic:ontology-driven-extraction
category: topic
tags:
- agent-memory
- auditability
- knowledge-systems
first_seen: '2025-12-03'
last_seen: '2026-04-29'
source_count: 3
evidence_count: 23
source_ids:
- ontology-driven-graphrag-a-framework-for-zero-noise-knowledge-extraction-01kqkvd7bwfhpbgqtw20czkk22
- why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8
- you-probably-don-t-need-a-graph-database-for-your-knowledge-graph-01kqz02qzddjehycrjafswxv5r
value_level: high
confidence: 0.916667
synthesis_state: stage1-placeholder
---

# Ontology-Driven Extraction

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Ontology-driven extraction uses a domain ontology to shape what an extractor looks for, how it formats output, and which values it should accept. Instead of asking a model for generic entity extraction, the system constrains the task with explicit entity types, properties, aliases, and validation expectations. This usually improves consistency, reduces hallucinated structure, and makes downstream validation easier. The approach is especially useful when documents vary in phrasing but must map into a stable schema.

## Examples

The source describes a pipeline that "identifies entities and concepts from the summaries, deduplicates them against the existing ontology" and uses explicit relation types like "is-a, part-of, related-to, contradicts."

## Key Points

- Explicit entity types and required properties can reduce ambiguity in extraction.
- Aliases let the extractor map variant surface forms to a canonical concept.
- Hybrid strategies can split work between language models and regex where structure is predictable.
- Concept deduplication is one of the hardest parts of maintaining a knowledge base.
- Explicit relation types outperform free-form linking for keeping the graph clean.
- Ontology quality directly affects contradiction detection and gap analysis.
- Typed extraction is a control mechanism for long-lived AI memory systems.
- ABoxes and TBoxes are different layers of a knowledge system and should not be conflated.
- Graph databases can store assertions without providing full ontology reasoning.
- Inference often requires external reasoners or logic engines.

## Operational Insight

Use the ontology as part of the prompt and extraction plan, not as a post-processing artifact. The more specific the schema, aliases, and property requirements, the less cleanup work you leave to later stages.

## Evidence / supporting sources

### Ontology-Driven GraphRAG: A Framework for Zero-Noise Knowledge Extraction (2025-12-03)

- Ontology-driven extraction uses a domain ontology to shape what an extractor looks for, how it formats output, and which values it should accept. Instead of asking a model for generic entity extraction, the system constrains the task with explicit entity types, properties, aliases, and validation expectations. This usually improves consistency, reduces hallucinated structure, and makes downstream validation easier. The approach is especially useful when documents vary in phrasing but must map into a stable schema. (`b8dae1e6a028` · neutral · knowledge_summary; [[sources/ontology-driven-graphrag-a-framework-for-zero-noise-knowledge-extraction-01kqkvd7bwfhpbgqtw20czkk22|Ontology-Driven GraphRAG: A Framework for Zero-Noise Knowledge Extraction]])
- Use the ontology as part of the prompt and extraction plan, not as a post-processing artifact. The more specific the schema, aliases, and property requirements, the less cleanup work you leave to later stages. (`dd482620edcb` · neutral · operational_insight; [[sources/ontology-driven-graphrag-a-framework-for-zero-noise-knowledge-extraction-01kqkvd7bwfhpbgqtw20czkk22|Ontology-Driven GraphRAG: A Framework for Zero-Noise Knowledge Extraction]])
- This pattern matters whenever teams need reliable structured extraction from unstructured text at scale. It is especially relevant for medical, legal, and support-document workflows where schema fidelity matters as much as recall. (`e4a7d96fa0ca` · neutral · relevance_note; [[sources/ontology-driven-graphrag-a-framework-for-zero-noise-knowledge-extraction-01kqkvd7bwfhpbgqtw20czkk22|Ontology-Driven GraphRAG: A Framework for Zero-Noise Knowledge Extraction]])
- Explicit entity types and required properties can reduce ambiguity in extraction. (`42b53738d8a3` · supporting · key_points[0]; [[sources/ontology-driven-graphrag-a-framework-for-zero-noise-knowledge-extraction-01kqkvd7bwfhpbgqtw20czkk22|Ontology-Driven GraphRAG: A Framework for Zero-Noise Knowledge Extraction]])
- Aliases let the extractor map variant surface forms to a canonical concept. (`7e9bbfd92cd1` · supporting · key_points[1]; [[sources/ontology-driven-graphrag-a-framework-for-zero-noise-knowledge-extraction-01kqkvd7bwfhpbgqtw20czkk22|Ontology-Driven GraphRAG: A Framework for Zero-Noise Knowledge Extraction]])
- Hybrid strategies can split work between language models and regex where structure is predictable. (`44ad6268ae4c` · supporting · key_points[2]; [[sources/ontology-driven-graphrag-a-framework-for-zero-noise-knowledge-extraction-01kqkvd7bwfhpbgqtw20czkk22|Ontology-Driven GraphRAG: A Framework for Zero-Noise Knowledge Extraction]])
- “we use the ontology to construct a precise, domain-specific prompt.” (`42baecb80c40` · supporting · supporting_snippet; [[sources/ontology-driven-graphrag-a-framework-for-zero-noise-knowledge-extraction-01kqkvd7bwfhpbgqtw20czkk22|Ontology-Driven GraphRAG: A Framework for Zero-Noise Knowledge Extraction]])

### Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge (2026-04-06)

- The source describes a pipeline that "identifies entities and concepts from the summaries, deduplicates them against the existing ontology" and uses explicit relation types like "is-a, part-of, related-to, contradicts." (`0a509ca790ea` · neutral · examples; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])
- Structured extraction improves knowledge systems when the model must identify concepts, deduplicate near-synonyms, and attach typed relations instead of producing loose text links. A typed ontology gives the system stable nodes and edges for concepts such as is-a, part-of, related-to, and contradicts. This makes it easier to detect duplicates, surface contradictions, and keep a large wiki internally consistent. The approach is especially useful when the corpus grows enough that free-form linking becomes unreliable. (`a273a5c75bae` · neutral · knowledge_summary; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])
- If a knowledge system will grow, invest in a typed concept graph early. The more the system must reconcile overlapping terms and conflicting claims, the more the ontology becomes the real control surface. (`4d80080a5bc0` · neutral · operational_insight; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])
- Ontology-driven extraction matters in AI systems that need stable memory, search, or provenance over time. It reduces the chance that the model fragments the same concept into multiple pages or loses track of contradictions as the corpus expands. (`6f2720238ffd` · neutral · relevance_note; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])
- Concept deduplication is one of the hardest parts of maintaining a knowledge base. (`755578396ff6` · supporting · key_points[0]; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])
- Explicit relation types outperform free-form linking for keeping the graph clean. (`5459c2583a30` · supporting · key_points[1]; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])
- Ontology quality directly affects contradiction detection and gap analysis. (`b55e58ac260c` · supporting · key_points[2]; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])
- Typed extraction is a control mechanism for long-lived AI memory systems. (`3520868dbd29` · supporting · key_points[3]; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])
- I have found that maintaining a typed entity system with explicit relation types (is-a, part-of, related-to, contradicts) produces much cleaner wikis than letting the LLM free-form link things. (`e86d08a7926b` · supporting · supporting_snippet; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])

### You Probably Don’t Need a Graph Database for Your Knowledge Graph (2026-04-29)

- Ontology-driven extraction uses a domain ontology to structure information extraction and constrain how entities and relations are interpreted. It can improve consistency and downstream reasoning, but it also adds modeling work and often depends on external reasoning systems. Inference, validation, and schema management are separate concerns from storing graph-shaped data. (`d81a13c6461c` · neutral · knowledge_summary; [[sources/you-probably-don-t-need-a-graph-database-for-your-knowledge-graph-01kqz02qzddjehycrjafswxv5r|You Probably Don’t Need a Graph Database for Your Knowledge Graph]])
- Do not treat ontology modeling as equivalent to graph storage. If the workflow needs classification, validation, or inference, plan for the reasoning layer explicitly rather than assuming the database will handle it. (`0d4ce37eaf9e` · neutral · operational_insight; [[sources/you-probably-don-t-need-a-graph-database-for-your-knowledge-graph-01kqz02qzddjehycrjafswxv5r|You Probably Don’t Need a Graph Database for Your Knowledge Graph]])
- Ontology-driven extraction matters in enterprise AI because it can turn unstructured text into structured knowledge that agents can use. The main operational challenge is that the ontology is only useful if reasoning and validation are supported cleanly in the pipeline. (`973bf1f449ed` · neutral · relevance_note; [[sources/you-probably-don-t-need-a-graph-database-for-your-knowledge-graph-01kqz02qzddjehycrjafswxv5r|You Probably Don’t Need a Graph Database for Your Knowledge Graph]])
- ABoxes and TBoxes are different layers of a knowledge system and should not be conflated. (`c5c873b3ca17` · supporting · key_points[0]; [[sources/you-probably-don-t-need-a-graph-database-for-your-knowledge-graph-01kqz02qzddjehycrjafswxv5r|You Probably Don’t Need a Graph Database for Your Knowledge Graph]])
- Graph databases can store assertions without providing full ontology reasoning. (`b9879061baa0` · supporting · key_points[1]; [[sources/you-probably-don-t-need-a-graph-database-for-your-knowledge-graph-01kqz02qzddjehycrjafswxv5r|You Probably Don’t Need a Graph Database for Your Knowledge Graph]])
- Inference often requires external reasoners or logic engines. (`d636447aad8c` · supporting · key_points[2]; [[sources/you-probably-don-t-need-a-graph-database-for-your-knowledge-graph-01kqz02qzddjehycrjafswxv5r|You Probably Don’t Need a Graph Database for Your Knowledge Graph]])
- They handle facts but not rules.

In description logic terms, GraphDB stores A-Boxes (assertions) but not T-Boxes (terminology and rules). (`4a2c2a85152c` · supporting · supporting_snippet; [[sources/you-probably-don-t-need-a-graph-database-for-your-knowledge-graph-01kqz02qzddjehycrjafswxv5r|You Probably Don’t Need a Graph Database for Your Knowledge Graph]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- [[topics/privacy-controls-for-ai-products|Privacy Controls for AI Products]]
- [[topics/ai-assisted-knowledge-compilation|AI-Assisted Knowledge Compilation]]
- [[topics/provenance-tracking|Provenance Tracking]]
- [[topics/llm-maintained-knowledge-compilation|LLM-Maintained Knowledge Compilation]]
- [[topics/realtime-ai-evaluation|Realtime AI Evaluation]]
- [[topics/local-model-deployment|Local Model Deployment]]

## Sources

- [[sources/ontology-driven-graphrag-a-framework-for-zero-noise-knowledge-extraction-01kqkvd7bwfhpbgqtw20czkk22|Ontology-Driven GraphRAG: A Framework for Zero-Noise Knowledge Extraction]]
- [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]]
- [[sources/you-probably-don-t-need-a-graph-database-for-your-knowledge-graph-01kqz02qzddjehycrjafswxv5r|You Probably Don’t Need a Graph Database for Your Knowledge Graph]]
