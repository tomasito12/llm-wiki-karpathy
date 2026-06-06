---
title: Andrej Karpathy Stopped Using AI to Write Code. He’s Using It to Build a Second
  Brain Instead
slug: andrej-karpathy-stopped-using-ai-to-write-code-he-s-using-it-to-build-a-second-brain-instead-01kr4392yb22p11v8q7pqc9npw
category: source
tags:
- ai-operationalization
- knowledge-systems
- memory-systems
- rag
- runtime-architecture
source_id: andrej-karpathy-stopped-using-ai-to-write-code-he-s-using-it-to-build-a-second-brain-instead-01kr4392yb22p11v8q7pqc9npw
author: Nikhil
publication: Medium
published_date: '2026-04-05'
assessed_as_of: '2026-04-05'
ingested_at: '2026-05-18T15:36:54.489985+00:00'
canonical_url: https://medium.com/neuralnotions/andrej-karpathy-stopped-using-ai-to-write-code-hes-using-it-to-build-a-second-brain-instead-cddceadc5df5
content_sha256: bf1c17bfe85df4cfcd1f23d4a8f15b9d2b2ca5eb603c0e1d5721cc42bd647085
derived_glossary:
- glossary/knowledge-management.md
- glossary/retrieval-augmented-generation.md
derived_topics:
- topics/ai-assisted-knowledge-compilation.md
derived_trends:
- industry-trends/models-becoming-execution-layers.md
derived_pages:
- glossary/knowledge-management.md
- glossary/retrieval-augmented-generation.md
- industry-trends/models-becoming-execution-layers.md
- topics/ai-assisted-knowledge-compilation.md
---

# Andrej Karpathy Stopped Using AI to Write Code. He’s Using It to Build a Second Brain Instead

This article is about a way to use artificial intelligence as a helper for building a personal knowledge base. Instead of asking the system only to write code, Andrej Karpathy describes using it to sort research notes into a linked wiki that keeps growing over time. You put your original articles, papers, and other files into one folder, and the system turns them into organized notes with links between related ideas. The important part is that the original files are left unchanged, so you always have the source material. The writer compares this approach with retrieval-augmented generation, which is a method where a system searches through documents each time you ask a question. In this workflow, the notes become a kind of second brain that can answer questions using your own collected sources. The article says you can start with simple tools like Obsidian and a browser extension, without needing a full software setup. It also makes a careful point that the system helps with organizing and connecting ideas, but it does not replace human thinking. As of 2026-04-05, the idea looks actionable for people who want a practical research workflow, though the bigger promise is still about knowledge organization rather than fully automated insight.

## Key insights

- A local markdown wiki can preserve accumulated structure better than one-off document retrieval because the knowledge is compiled once and then maintained.
- The source-of-truth/raw-folder split is a useful operational safeguard: original materials stay untouched while the wiki remains a regenerable layer.
- Periodic linting matters because the value of the system depends on backlinks, orphan cleanup, and stale-claim detection staying intact.
- The workflow compounds value when query answers are filed back into the wiki, turning usage into additional knowledge capture.
- The strongest claim is organizational, not epistemic: the system reduces research drudgery, but human synthesis still remains necessary.

## Derived knowledge pages

- [[glossary/knowledge-management]]
- [[glossary/retrieval-augmented-generation]]
- [[industry-trends/models-becoming-execution-layers]]
- [[topics/ai-assisted-knowledge-compilation]]

## Why it matters

The piece is useful because it reframes a common AI workflow problem: instead of treating an LLM as a question-answering layer over documents, it treats the model as a compiler that turns raw material into a maintained knowledge base. That is a durable idea for anyone building research tooling, internal knowledge systems, or agent workflows that need more structure than retrieval alone provides. The raw/source-of-truth split is especially practical because it separates immutable evidence from generated summaries, making the compiled layer easier to regenerate or audit. The article also makes clear that markdown, backlinks, indexes, and lint passes are not cosmetic details; they are the operational machinery that lets the knowledge base accumulate over time. The caveat is that the stakes are narrower than the viral framing suggests: the strongest evidence here is an expert-described workflow, not a measured comparison against alternative systems. Actionable as of 2026-04-05, with the core pattern likely durable because it is built around plain files, explicit structure, and local tooling rather than a single vendor feature. For service automation, the closing implication is indirect but real: the same pattern could organize internal documents, meeting transcripts, and support knowledge, but the article does not present a production customer-support deployment.

## Limitations / open questions

The article does not provide controlled evidence that the wiki approach outperforms retrieval-augmented generation on accuracy, speed, or maintenance cost. It also leaves open how well the system scales when the raw corpus becomes messy, contradictory, multilingual, or highly dynamic. The maintenance burden of linting, schema tuning, and prompt upkeep is described, but not quantified. The claim that the system can be used by non-developers depends on how comfortable they are with local files, LLM agents, and manual curation. The future idea of generating synthetic training data and fine-tuning a smaller model is mentioned only as a direction, not as a demonstrated outcome.

## Contradictions / unverified claims

The piece pushes back against retrieval-augmented generation, but the critique is framed from a workflow perspective rather than benchmark evidence. It is plausible that compiled markdown helps with organization, yet that does not prove it is always better than search-based retrieval for factual recall or freshness. The strongest speculative jump is the suggestion that a cleaned-up wiki could become training data for a model that internalizes the domain; that is an interesting extension, but it is not shown here. The viral framing may overstate novelty: the underlying ideas—structured notes, backlinks, and periodic cleanup—are familiar, even if the assembled workflow is unusually coherent.

## Source metadata

- Canonical URL: https://medium.com/neuralnotions/andrej-karpathy-stopped-using-ai-to-write-code-hes-using-it-to-build-a-second-brain-instead-cddceadc5df5
- Raw markdown: `raw/readwise/andrej-karpathy-stopped-using-ai-to-write-code-he-s-using-it-to-build-a-second-brain-instead-01kr4392yb22p11v8q7pqc9npw.md`
- Raw HTML: `raw/readwise/andrej-karpathy-stopped-using-ai-to-write-code-he-s-using-it-to-build-a-second-brain-instead-01kr4392yb22p11v8q7pqc9npw.html`
