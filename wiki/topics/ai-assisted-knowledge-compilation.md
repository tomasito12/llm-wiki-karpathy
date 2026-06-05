---
title: AI-Assisted Knowledge Compilation
slug: ai-assisted-knowledge-compilation
entity_id: topic:ai-assisted-knowledge-compilation
category: topic
tags:
- knowledge-systems
first_seen: '2026-04-05'
last_seen: '2026-04-05'
source_count: 1
evidence_count: 9
source_ids:
- andrej-karpathy-stopped-using-ai-to-write-code-he-s-using-it-to-build-a-second-brain-instead-01kr4392yb22p11v8q7pqc9npw
value_level: high
confidence: 0.96
synthesis_state: stage1-placeholder
---

# AI-Assisted Knowledge Compilation

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
AI-assisted knowledge compilation treats raw documents as immutable source material and uses an LLM to turn them into a structured, interlinked knowledge layer. The compiled layer can include summaries, concept pages, entity pages, comparisons, indexes, backlinks, and logs, and it can be regenerated incrementally as new material arrives. This approach is presented as an alternative to ad hoc chat histories or retrieval-only systems because the knowledge accumulates over time instead of being rediscovered on each query.

## Key Points

- Keep raw sources separate from compiled knowledge so outputs can be regenerated without losing evidence.
- Have the LLM maintain summaries, backlinks, indexes, and comparison pages as first-class artifacts.
- Recompile incrementally when new sources arrive rather than rebuilding the whole system from scratch.
- Run lint passes to find contradictions, orphan pages, missing concepts, and stale claims.
- Store outputs as plain markdown files so they remain editable, portable, and auditable.

## Operational Insight

Use the LLM as a compiler, librarian, and maintenance worker for a markdown knowledge base: ingest raw sources, generate structured pages, keep links and indexes updated, and run periodic lint passes to catch contradictions or stale claims. The practical advantage is a persistent, auditable knowledge system that improves with each new source and each new query.

## Related Topics

- knowledge-management
- local-file-based-ai-workflows

## Evidence / supporting sources

### Andrej Karpathy Stopped Using AI to Write Code. He’s Using It to Build a Second Brain Instead (2026-04-05)

- AI-assisted knowledge compilation treats raw documents as immutable source material and uses an LLM to turn them into a structured, interlinked knowledge layer. The compiled layer can include summaries, concept pages, entity pages, comparisons, indexes, backlinks, and logs, and it can be regenerated incrementally as new material arrives. This approach is presented as an alternative to ad hoc chat histories or retrieval-only systems because the knowledge accumulates over time instead of being rediscovered on each query. (`7bfece0c5af3` · neutral · knowledge_summary; [[sources/andrej-karpathy-stopped-using-ai-to-write-code-he-s-using-it-to-build-a-second-brain-instead-01kr4392yb22p11v8q7pqc9npw|Andrej Karpathy Stopped Using AI to Write Code. He’s Using It to Build a Second Brain Instead]])
- Use the LLM as a compiler, librarian, and maintenance worker for a markdown knowledge base: ingest raw sources, generate structured pages, keep links and indexes updated, and run periodic lint passes to catch contradictions or stale claims. The practical advantage is a persistent, auditable knowledge system that improves with each new source and each new query. (`e82bef1d8d4f` · neutral · operational_insight; [[sources/andrej-karpathy-stopped-using-ai-to-write-code-he-s-using-it-to-build-a-second-brain-instead-01kr4392yb22p11v8q7pqc9npw|Andrej Karpathy Stopped Using AI to Write Code. He’s Using It to Build a Second Brain Instead]])
- This pattern is broadly useful anywhere teams accumulate documents that need to become reusable knowledge, especially when structure, traceability, and incremental updates matter more than one-off answers. It fits workflows that need memory across sources without sacrificing the ability to inspect the underlying files. (`c4180b59c1f9` · neutral · relevance_note; [[sources/andrej-karpathy-stopped-using-ai-to-write-code-he-s-using-it-to-build-a-second-brain-instead-01kr4392yb22p11v8q7pqc9npw|Andrej Karpathy Stopped Using AI to Write Code. He’s Using It to Build a Second Brain Instead]])
- Keep raw sources separate from compiled knowledge so outputs can be regenerated without losing evidence. (`63b93a59b0cc` · supporting · key_points[0]; [[sources/andrej-karpathy-stopped-using-ai-to-write-code-he-s-using-it-to-build-a-second-brain-instead-01kr4392yb22p11v8q7pqc9npw|Andrej Karpathy Stopped Using AI to Write Code. He’s Using It to Build a Second Brain Instead]])
- Have the LLM maintain summaries, backlinks, indexes, and comparison pages as first-class artifacts. (`1f35b638bb6b` · supporting · key_points[1]; [[sources/andrej-karpathy-stopped-using-ai-to-write-code-he-s-using-it-to-build-a-second-brain-instead-01kr4392yb22p11v8q7pqc9npw|Andrej Karpathy Stopped Using AI to Write Code. He’s Using It to Build a Second Brain Instead]])
- Recompile incrementally when new sources arrive rather than rebuilding the whole system from scratch. (`e92fb8bebf72` · supporting · key_points[2]; [[sources/andrej-karpathy-stopped-using-ai-to-write-code-he-s-using-it-to-build-a-second-brain-instead-01kr4392yb22p11v8q7pqc9npw|Andrej Karpathy Stopped Using AI to Write Code. He’s Using It to Build a Second Brain Instead]])
- Run lint passes to find contradictions, orphan pages, missing concepts, and stale claims. (`21087d2527ed` · supporting · key_points[3]; [[sources/andrej-karpathy-stopped-using-ai-to-write-code-he-s-using-it-to-build-a-second-brain-instead-01kr4392yb22p11v8q7pqc9npw|Andrej Karpathy Stopped Using AI to Write Code. He’s Using It to Build a Second Brain Instead]])
- Store outputs as plain markdown files so they remain editable, portable, and auditable. (`cd732c9f64b3` · supporting · key_points[4]; [[sources/andrej-karpathy-stopped-using-ai-to-write-code-he-s-using-it-to-build-a-second-brain-instead-01kr4392yb22p11v8q7pqc9npw|Andrej Karpathy Stopped Using AI to Write Code. He’s Using It to Build a Second Brain Instead]])
- Instead of searching through raw documents on every query, the LLM reads the raw material once and compiles it into a structured, organized wiki. Summaries, concept articles, backlinks, comparisons, an index the whole thing. (`38aeb22fae1c` · supporting · supporting_snippet; [[sources/andrej-karpathy-stopped-using-ai-to-write-code-he-s-using-it-to-build-a-second-brain-instead-01kr4392yb22p11v8q7pqc9npw|Andrej Karpathy Stopped Using AI to Write Code. He’s Using It to Build a Second Brain Instead]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- knowledge-management
- local-file-based-ai-workflows

## Sources

- [[sources/andrej-karpathy-stopped-using-ai-to-write-code-he-s-using-it-to-build-a-second-brain-instead-01kr4392yb22p11v8q7pqc9npw|Andrej Karpathy Stopped Using AI to Write Code. He’s Using It to Build a Second Brain Instead]]
