---
title: llm-wiki · GitHub
slug: llm-wiki-github-01kqh081eg75gw49db3mqd9cpq
category: source
tags:
- agent-systems
- knowledge-systems
- orchestration
- workflow-design
- workflow-restructuring
source_id: llm-wiki-github-01kqh081eg75gw49db3mqd9cpq
author: '262588213843476'
publication: Github
published_date: '2026-04-04'
assessed_as_of: '2026-04-04'
ingested_at: '2026-06-06T21:59:40+00:00'
canonical_url: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
content_sha256: 7d48dfb5f3743090e986bc2fb81342aa6c63bfa5bc3a9d8cb0725ea587adf2a1
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
derived_topics:
- topics/llm-maintained-knowledge-bases.md
- topics/wiki-schema-governance.md
derived_trends:
- industry-trends/knowledge-systems-shift-toward-compilation-over-retrieval.md
derived_pages:
- industry-trends/knowledge-systems-shift-toward-compilation-over-retrieval.md
- topics/llm-maintained-knowledge-bases.md
- topics/wiki-schema-governance.md
---

# llm-wiki · GitHub

This is an idea for using an LLM to build and maintain a personal wiki, instead of just answering questions from a pile of files. The important twist is that the model does not only retrieve text; it also writes and updates the wiki as new sources arrive. That means summaries, links, contradictions, and related concepts can accumulate over time. The result is meant to feel more like a living knowledge base than a search box. The author presents it as a flexible pattern, not a finished product, so you can adapt the workflow to your own tools and domain.

## Key insights

- The durable unit is a persistent wiki, not a one-off answer, so each new source compounds prior work instead of forcing re-analysis.
- A schema file is treated as the control plane for the LLM, which is a useful design pattern for making agent behavior repeatable across sessions.
- Index and log files are singled out as lightweight infrastructure that can replace heavier RAG machinery at moderate scale.
- The workflow explicitly includes contradiction tracking and linting, which makes maintenance an ongoing first-class task rather than an afterthought.
- Answers generated during exploration should be written back into the wiki when they are worth keeping, so analysis does not disappear into chat history.

## Derived knowledge pages

- [[industry-trends/knowledge-systems-shift-toward-compilation-over-retrieval]]
- [[topics/llm-maintained-knowledge-bases]]
- [[topics/wiki-schema-governance]]

## Why it matters

The article is useful because it reframes LLM-assisted knowledge work as maintenance of a structured artifact rather than repeated question answering over raw documents. That is a durable operational idea for anyone building personal or team knowledge bases: the model reads sources once, updates linked markdown pages, and preserves synthesis, contradictions, and cross-references for later reuse. The proposed architecture is simple enough to be implemented with existing note-taking and file-based workflows, which makes it more actionable than a vague “use an LLM for RAG” slogan. Its practical value is strongest where information accumulates over time and where keeping pages synchronized is the real bottleneck. The emphasis on index.md, log.md, and a schema file is a concrete reminder that agent systems need an explicit operating model, not just model calls. The piece is also honest that the pattern is abstract and modular, so the value is in the workflow design rather than any single tool recommendation. As of 2026-04-04, the idea looks actionable as a personal or team knowledge-management pattern, but it remains a conceptual proposal rather than a benchmarked system.

## Limitations / open questions

The document is intentionally abstract, so it does not specify concrete page schemas, conflict-resolution rules, evaluation methods, or failure handling. It does not show measured gains over conventional RAG, nor does it compare maintenance cost, latency, or quality across scales. The suggestion that the LLM can keep a wiki consistent depends on the quality of the schema and human oversight, but the article does not define how much review is needed. Security, privacy, and provenance concerns are only implied, not addressed: an LLM updating a knowledge base could easily propagate errors if source boundaries are unclear. The search and lint tooling are described as optional, which leaves open how far the pattern can scale before the index/log approach becomes insufficient. The document also does not say how to handle ambiguous sources, conflicting evidence, or changing source hierarchies in a formal way.

## Contradictions / unverified claims

The central claim—that LLMs can make wiki maintenance cheap enough to solve the real bottleneck—is plausible, but the article offers no empirical evidence beyond the author’s reasoning. The comparison with RAG is directionally persuasive, yet simplified: retrieval systems can also be layered with summaries, memory, and indexes, so the distinction is not as absolute as the text suggests. The idea depends heavily on disciplined schemas and human guidance, which means it is less like fully autonomous maintenance and more like supervised synthesis. The “touch 10–15 pages in one pass” claim is a capability claim, not a quality guarantee; large edit breadth can also increase the chance of subtle inconsistencies. Overall, the skepticism is mild: the pattern is coherent and practical, but its effectiveness is asserted rather than demonstrated.

## Source metadata

- Canonical URL: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- Raw markdown: `raw/readwise/llm-wiki-github-01kqh081eg75gw49db3mqd9cpq.md`
- Raw HTML: `raw/readwise/llm-wiki-github-01kqh081eg75gw49db3mqd9cpq.html`

## Full source text

---
readwise_id: 01kqh081eg75gw49db3mqd9cpq
title: llm-wiki · GitHub
author: '262588213843476'
source_url: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
category: article
location: archive
published_date: '2026-04-04'
saved_at: '2026-05-01T05:30:07.696000+00:00'
updated_at: '2026-05-02T14:22:00.264220+00:00'
tags:
- processed
publication: Github
---

The llm-wiki is a personal knowledge base where an AI reads and summarizes new sources into a growing, linked wiki. This wiki updates itself with new information and keeps everything consistent over time. You guide the AI by adding sources and asking questions, while it does the hard work of organizing and synthesizing knowledge.
