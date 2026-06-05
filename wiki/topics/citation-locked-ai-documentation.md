---
title: Citation-Locked AI Documentation
slug: citation-locked-ai-documentation
entity_id: topic:citation-locked-ai-documentation
category: topic
tags:
- knowledge-systems
first_seen: '2026-04-17'
last_seen: '2026-04-17'
source_count: 1
evidence_count: 8
source_ids:
- how-i-turned-andrej-karpathy-s-llm-wiki-into-a-tool-that-writes-wiki-s-from-code-01kqkv9ej7dxydcbtgnaj5bb1t
value_level: high
confidence: 0.95
synthesis_state: stage1-placeholder
---

# Citation-Locked AI Documentation

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
AI-generated documentation becomes more trustworthy when every non-trivial claim must be tied to a specific source location. Requiring citations forces the system to distinguish between what is directly supported by the code and what is only inferred. When the model cannot cite a claim, it should mark the uncertainty explicitly instead of pretending certainty. This reduces silent drift and makes review much faster.

## Examples

The source says the prompt rules include: "Cite or do not claim" and "Every non-trivial statement must be followed by (path:start-end)."

## Key Points

- Citation requirements narrow the model’s freedom to invent behavior that is not in the repository.
- `TODO-VERIFY` markers turn uncertainty into a review queue instead of hidden misinformation.
- The policy only works if the cited source is itself current and readable.

## Operational Insight

A strict citation policy is a practical guardrail for code-aware generation. It does not make the model correct by itself, but it changes failure modes from quiet hallucination to visible uncertainty.

## Related Topics

- commit-driven-documentation-generation
- provenance-tracking

## Evidence / supporting sources

### How I turned Andrej Karpathy’s LLM Wiki into a tool that writes wiki’s from code (2026-04-17)

- The source says the prompt rules include: "Cite or do not claim" and "Every non-trivial statement must be followed by (path:start-end)." (`ad081f525406` · neutral · examples; [[sources/how-i-turned-andrej-karpathy-s-llm-wiki-into-a-tool-that-writes-wiki-s-from-code-01kqkv9ej7dxydcbtgnaj5bb1t|How I turned Andrej Karpathy’s LLM Wiki into a tool that writes wiki’s from code]])
- AI-generated documentation becomes more trustworthy when every non-trivial claim must be tied to a specific source location. Requiring citations forces the system to distinguish between what is directly supported by the code and what is only inferred. When the model cannot cite a claim, it should mark the uncertainty explicitly instead of pretending certainty. This reduces silent drift and makes review much faster. (`0247c0191b61` · neutral · knowledge_summary; [[sources/how-i-turned-andrej-karpathy-s-llm-wiki-into-a-tool-that-writes-wiki-s-from-code-01kqkv9ej7dxydcbtgnaj5bb1t|How I turned Andrej Karpathy’s LLM Wiki into a tool that writes wiki’s from code]])
- A strict citation policy is a practical guardrail for code-aware generation. It does not make the model correct by itself, but it changes failure modes from quiet hallucination to visible uncertainty. (`bf0fa47f54e5` · neutral · operational_insight; [[sources/how-i-turned-andrej-karpathy-s-llm-wiki-into-a-tool-that-writes-wiki-s-from-code-01kqkv9ej7dxydcbtgnaj5bb1t|How I turned Andrej Karpathy’s LLM Wiki into a tool that writes wiki’s from code]])
- This matters in any AI system that explains code, policies, or internal operations from source material. The same discipline can support reviewable internal docs, runbooks, and support references when teams need traceable claims. (`cd08cf6719f5` · neutral · relevance_note; [[sources/how-i-turned-andrej-karpathy-s-llm-wiki-into-a-tool-that-writes-wiki-s-from-code-01kqkv9ej7dxydcbtgnaj5bb1t|How I turned Andrej Karpathy’s LLM Wiki into a tool that writes wiki’s from code]])
- Citation requirements narrow the model’s freedom to invent behavior that is not in the repository. (`38ab07c26399` · supporting · key_points[0]; [[sources/how-i-turned-andrej-karpathy-s-llm-wiki-into-a-tool-that-writes-wiki-s-from-code-01kqkv9ej7dxydcbtgnaj5bb1t|How I turned Andrej Karpathy’s LLM Wiki into a tool that writes wiki’s from code]])
- `TODO-VERIFY` markers turn uncertainty into a review queue instead of hidden misinformation. (`14915c214803` · supporting · key_points[1]; [[sources/how-i-turned-andrej-karpathy-s-llm-wiki-into-a-tool-that-writes-wiki-s-from-code-01kqkv9ej7dxydcbtgnaj5bb1t|How I turned Andrej Karpathy’s LLM Wiki into a tool that writes wiki’s from code]])
- The policy only works if the cited source is itself current and readable. (`67ad3222a615` · supporting · key_points[2]; [[sources/how-i-turned-andrej-karpathy-s-llm-wiki-into-a-tool-that-writes-wiki-s-from-code-01kqkv9ej7dxydcbtgnaj5bb1t|How I turned Andrej Karpathy’s LLM Wiki into a tool that writes wiki’s from code]])
- "Cite or do not claim. Every non-trivial statement must be followed by (path:start-end)." (`80c097904c29` · supporting · supporting_snippet; [[sources/how-i-turned-andrej-karpathy-s-llm-wiki-into-a-tool-that-writes-wiki-s-from-code-01kqkv9ej7dxydcbtgnaj5bb1t|How I turned Andrej Karpathy’s LLM Wiki into a tool that writes wiki’s from code]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- commit-driven-documentation-generation
- provenance-tracking

## Sources

- [[sources/how-i-turned-andrej-karpathy-s-llm-wiki-into-a-tool-that-writes-wiki-s-from-code-01kqkv9ej7dxydcbtgnaj5bb1t|How I turned Andrej Karpathy’s LLM Wiki into a tool that writes wiki’s from code]]
