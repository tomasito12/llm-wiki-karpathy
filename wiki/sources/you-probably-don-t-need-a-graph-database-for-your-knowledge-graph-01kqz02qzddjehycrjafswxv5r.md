---
title: You Probably Don’t Need a Graph Database for Your Knowledge Graph
slug: you-probably-don-t-need-a-graph-database-for-your-knowledge-graph-01kqz02qzddjehycrjafswxv5r
category: source
tags:
- ai-operationalization
- knowledge-systems
- memory-systems
- runtime-architecture
- workflow-restructuring
source_id: you-probably-don-t-need-a-graph-database-for-your-knowledge-graph-01kqz02qzddjehycrjafswxv5r
author: Michael Sakhatsky
publication: Medium
published_date: '2026-04-29'
assessed_as_of: '2026-04-29'
ingested_at: '2026-05-18T15:49:13.762205+00:00'
canonical_url: https://medium.com/@msakhatsky/you-probably-dont-need-a-graph-database-for-your-knowledge-graph-7178054fe3d3
content_sha256: e3cdcfef2324d31f72ba98d96bb0622672bcc02067eaec6d59cfce4664bc7904
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
derived_glossary:
- glossary/datalog.md
- glossary/ontology.md
derived_topics:
- topics/knowledge-management.md
- topics/ontology-driven-extraction.md
derived_trends:
- industry-trends/knowledge-base-becomes-runtime-infrastructure.md
derived_pages:
- glossary/datalog.md
- glossary/ontology.md
- industry-trends/knowledge-base-becomes-runtime-infrastructure.md
- topics/knowledge-management.md
- topics/ontology-driven-extraction.md
---

# You Probably Don’t Need a Graph Database for Your Knowledge Graph

This article asks a simple question: if a company wants to help a language model use its internal knowledge, does it really need a graph database? The author says many teams jump too quickly from “we need shared concepts” to “we need Neo4j.” He argues that this jump skips several practical questions about what the system must do, such as follow relationships, apply rules, or check meanings. In his view, graph databases are good at some jobs, especially walking through chains of links, but they are not the best tool for every knowledge problem. He also points out that other tools, like rules engines and Datalog, can sometimes be faster and easier to use. A big theme is that storing knowledge is not the same as reasoning over it. He says the real challenge is picking a system that matches the task instead of choosing the most familiar “knowledge graph” stack. As of 2026-04-29, the article’s advice is to look carefully at simpler options before committing to a graph database.

## Key insights

- Graph databases are strongest when the task is recursive traversal over unknown depth, not general knowledge reasoning.
- A graph can store relationships, but semantics and inference are separate problems that often require logic systems or external reasoners.
- Many ontology workloads need validation and classification outside the database anyway, which adds pipeline complexity.
- Rules engines and Datalog can expose existing business logic to language models with less setup than a full RDF/OWL stack.
- Graph storage, graph analytics, and ontology engineering are different jobs and should not be collapsed into one architecture choice.

## Derived knowledge pages

- [[glossary/datalog]]
- [[glossary/ontology]]
- [[industry-trends/knowledge-base-becomes-runtime-infrastructure]]
- [[topics/knowledge-management]]
- [[topics/ontology-driven-extraction]]

## Why it matters

The core value of the piece is architectural: it pushes practitioners to separate knowledge storage from reasoning before choosing a stack. It argues that the popular “ontology implies graph database” chain is too coarse, because relationships, traversal, semantics, inference, and validation are different requirements with different tools. That matters for teams building retrieval and grounding layers for language models, because a graph database can look like a universal answer while still leaving inference, schema validation, and security unresolved. The article is especially useful in reminding teams that relational systems can store graph-shaped data, and that rules engines or Datalog may be enough when the real need is to expose business logic, not model an ontology from scratch. It also draws a useful distinction between graph databases and graph analytics, which are often conflated in product decisions. The practical conclusion is that graph databases have a real niche, but they should not be the default starting point for institutional knowledge systems. For service automation, the closing argument is that agents may work better when they query rules or knowledge bases directly instead of forcing every lookup through graph traversal; as of 2026-04-29, that is a plausible, low-hype design warning rather than a universal rule.

## Limitations / open questions

The article is strong on architectural critique but thin on comparative benchmarks, cost numbers, or side-by-side implementation evidence. Several claims depend on broad statements about how well graph databases support inference or validation, but the exact breakpoints will vary by vendor, ontology profile, and workload. The Datalog and rules-engine alternatives are presented as simpler, but the piece does not quantify migration effort, governance overhead, or team skill availability. It also leaves open how often a hybrid architecture is best: graph storage plus external reasoners, rules engines, or analytics systems. The security discussion is important but underspecified, especially for role-dependent visibility across inferred paths. More concrete examples of production grounding pipelines would strengthen the recommendation.

## Contradictions / unverified claims

The piece usefully challenges a common default, but it may overgeneralize from ontology-heavy and inference-heavy workloads to all knowledge graph use cases. Its argument that a graph database without an ontology is “just a less convenient relational database” is rhetorically sharp, but that will not hold equally for every retrieval or relationship-navigation problem. The claim that most teams should start with rules engines and Datalog is plausible, yet the article gives limited evidence about adoption friction, maintenance cost, or operational scalability. The strongest skepticism is that the right architecture is highly workload-specific, so the article should be read as a caution against premature graph adoption rather than a blanket rejection of graph databases.

## Source metadata

- Canonical URL: https://medium.com/@msakhatsky/you-probably-dont-need-a-graph-database-for-your-knowledge-graph-7178054fe3d3
- Raw markdown: `raw/readwise/you-probably-don-t-need-a-graph-database-for-your-knowledge-graph-01kqz02qzddjehycrjafswxv5r.md`
- Raw HTML: `raw/readwise/you-probably-don-t-need-a-graph-database-for-your-knowledge-graph-01kqz02qzddjehycrjafswxv5r.html`

## Full source text

---
readwise_id: 01kqz02qzddjehycrjafswxv5r
title: You Probably Don’t Need a Graph Database for Your Knowledge Graph
author: Michael Sakhatsky
source_url: https://medium.com/@msakhatsky/you-probably-dont-need-a-graph-database-for-your-knowledge-graph-7178054fe3d3
category: article
location: archive
published_date: '2026-04-29'
saved_at: '2026-05-06T15:56:36.205000+00:00'
updated_at: '2026-05-06T17:36:01.289820+00:00'
tags:
- processed
publication: Medium
---

Graph databases are good but often not the best choice for storing company knowledge. Many teams do better using rule engines and logic programming like Datalog, which are simpler and faster. Before choosing a graph database, consider other tools that fit your needs and skills better.
