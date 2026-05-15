# glossary-worthiness.md

## Purpose

This document defines the philosophy and extraction criteria for glossary entries in the LLM wiki ingestion system.

The glossary is a durable conceptual reference layer.

It is not:

* a list of article keywords
* a terminology dump
* a summary of all mentioned concepts
* a collection of supporting vocabulary

The glossary should contain only concepts that deserve long-term conceptual preservation.

Glossary extraction should therefore remain highly conservative.

---

# Core Principle

The central glossary question is:

> Would this concept deserve a glossary entry even if this article had never existed?

If the answer is no, the concept should probably not become a glossary proposal.

This is the most important glossary filter.

---

# Purpose Of The Glossary

The glossary exists to help understand:

* recurring industry concepts
* durable architectural ideas
* operational AI terminology
* reusable mental models
* important system-design patterns
* persistent workflow concepts

Glossary entries should support:

* long-term understanding
* conceptual consistency
* reusable operational reasoning
* onboarding into recurring AI concepts

---

# What The Glossary Is NOT

The glossary is NOT intended to capture:

* every term appearing in an article
* supporting vocabulary
* obvious terminology
* temporary buzzwords
* weakly differentiated concepts
* article-specific framing
* marketing language
* repetitive AI jargon

The ingestion system should aggressively suppress low-value glossary extraction.

---

# High-Level Extraction Philosophy

Glossary extraction should optimize for:

* precision over recall
* durability over completeness
* operational relevance over semantic possibility
* conceptual reuse over extraction volume

The system should strongly prefer:

> a few durable glossary entries

over:

> many weak terminology entries

---

# The Five Worthiness Questions

Before proposing a glossary entry, the system should internally evaluate the following questions.

A concept should usually satisfy most or all of them.

---

# 1. Is The Concept Durable?

Question:

> Will this concept likely still matter in 6–12 months?

Durable concepts include:

* orchestration concepts
* retrieval architectures
* evaluation methodologies
* agent patterns
* infrastructure abstractions
* operational AI workflows

Weak glossary candidates include:

* temporary product slogans
* short-lived memes
* transient benchmark discourse
* hype terminology

---

# 2. Is The Concept Reusable Across Sources?

Question:

> Is this concept likely to appear repeatedly across many future sources?

The glossary should prioritize recurring conceptual structures.

One-off terminology should rank low.

---

# 3. Is The Concept Operationally Useful?

Question:

> Does understanding this concept improve AI engineering, orchestration, evaluation, automation, or service automation understanding?

Operationally useful concepts deserve glossary space.

Purely decorative or descriptive terminology does not.

---

# 4. Is The Concept Semantically Distinct?

Question:

> Does this concept represent a genuinely distinct idea?

The system should avoid creating separate glossary entries for concepts that are merely:

* wording variants
* subphrases
* overlapping abstractions
* semantically compressed into stronger parent concepts

Example:

Separate glossary entries for:

* provenance
* auditability
* traceability

may not always be necessary if the operational distinction is weak.

---

# 5. Is The Concept Important Beyond This Source?

Question:

> Does the concept matter independently of the current article?

This is critical.

A concept should not receive glossary status merely because:

* the article emphasizes it heavily
* the source repeats it often
* the author frames it as central

Glossary relevance must be:

* industry-level
* operational-level
* architectural-level

NOT:
source-level.

---

# Glossary Relevance Philosophy

The glossary relevance section should explain:

* why the concept matters in the AI industry
* where it appears in real-world systems
* why practitioners should understand it
* how it affects AI workflows
* how it relates to orchestration, evaluation, automation, or service systems

The glossary relevance section should NOT explain:

* why the concept matters for the article
* how the article discusses it
* what the source author believes about it

Avoid phrasing such as:

* "This article argues..."
* "The source focuses on..."
* "This is the main idea of the article..."

The glossary is a durable conceptual layer, not a source commentary layer.

---

# Glossary Definitions

Definitions should prioritize:

* conceptual clarity
* operational usefulness
* understandable language
* durable meaning

Definitions should avoid:

* excessive jargon
* benchmark-heavy framing
* hype-heavy language
* source-specific wording
* marketing terminology

The intended reader is:

* technically informed
* operationally interested
* not necessarily deeply academic

---

# Service Automation Relevance

Where applicable, glossary entries should explain implications for:

* chatbots
* voicebots
* AI agents
* support automation
* orchestration systems
* enterprise assistants
* conversational reliability
* workflow automation

If no meaningful connection exists, this should be stated explicitly.

Not every glossary concept requires forced service-automation relevance.

---

# Examples Of Strong Glossary Candidates

Examples:

* Retrieval-Augmented Generation (RAG)
* Context Engineering
* Agent Orchestration
* Tool Calling
* Knowledge Graphs
* Model Context Protocol (MCP)
* Synthetic Data
* Evaluation Harness
* Memory Architecture
* Multi-Agent Systems

Characteristics:

* reusable
* durable
* operationally meaningful
* recurring across sources
* strategically important

---

# Examples Of Weak Glossary Candidates

Examples:

* article-specific coined phrases
* weak marketing abstractions
* shallow trend labels
* repetitive AI buzzwords
* narrow feature terminology
* low-reuse sub-concepts

Weak candidates should be suppressed aggressively.

---

# Glossary Extraction Budgets

Glossary extraction should remain highly constrained.

Recommended philosophy:

* most articles should generate 0–2 glossary proposals
* dense concept articles may occasionally generate 3
* generating many glossary proposals is usually a failure mode

Large glossary proposal counts typically indicate:

* weak filtering
* semantic redundancy
* extraction-recall optimization
* ontology instability

---

# Relationship To Topics

Not every important concept deserves a glossary page.

Some concepts are better represented as:

* topics
* trends
* how-tos
* architecture pages

The glossary should prioritize:

* conceptual primitives
* reusable abstractions
* stable terminology

Topics should handle broader operational synthesis.

---

# Relationship To Tags

Tags are not glossary concepts.

A tag should not automatically imply glossary-worthiness.

Glossary entries require substantially higher conceptual value than tags.

---

# Relationship To Related Terms

Related terms should not dominate glossary review.

Semantic graph enrichment can happen later.

The glossary review workflow should remain lightweight and focused on:

* worthiness
* definition quality
* operational relevance

NOT:
manual concept graph management.

---

# Anti-Goals

The glossary should avoid becoming:

* a terminology archive
* an AI buzzword collection
* a synonym database
* a marketing language repository
* an exhaustive ontology
* a source-keyword index

The glossary is intentionally selective.

---

# Long-Term Philosophy

A small, durable, high-quality glossary is more valuable than a large noisy one.

The glossary should evolve slowly and conservatively.

Ontology stability is more important than rapid conceptual expansion.

The system should optimize for:

* conceptual clarity
* operational usefulness
* long-term maintainability
* reviewer sustainability
* reusable understanding

over extraction volume.
