---
title: Structured Page Extraction With LLMs
slug: structured-page-extraction-with-llms
entity_id: topic:structured-page-extraction-with-llms
category: topic
tags:
- context-engineering
- retrieval-systems
- runtime-architecture
- workflow-design
first_seen: '2026-05-23'
last_seen: '2026-05-23'
source_count: 1
evidence_count: 8
source_ids:
- build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt
value_level: high
confidence: 0.91
synthesis_state: stage1-placeholder
---

# Structured Page Extraction With LLMs

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
A browser or scraper can use a language model to turn page content into structured JSON instead of relying only on deterministic parsers. This is especially useful when the desired output is described in a schema and the information is spread across headings, infoboxes, or loosely structured page text. The technique trades determinism for flexibility: the model can populate arrays and fuzzy fields, but it is still limited by snapshot quality and prompt discipline. It works best when the page snapshot contains the relevant facts and the schema is specific enough to guide extraction. For long pages, snapshot budgeting becomes a first-order design constraint because truncation can remove the exact fields you wanted.

## Examples

The source shows an `extract` tool that fetches a page, then prompts Ollama with a JSON Schema and asks it to return only JSON. It also describes a failure case where middle truncation caused infobox fields such as a mayor and postal code to disappear from the snapshot.

## Key Points

- LLM extraction can handle array-shaped outputs that a rigid server-side extractor may reject.
- The schema should describe the fields clearly enough that the model can map page text to them.
- Snapshot truncation is a major failure mode for infobox-style or mid-page facts.

## Operational Insight

Use model-based extraction when the structure is too irregular for a simple parser, but treat the output as schema-guided reading rather than guaranteed parsing. Keep the snapshot large enough to preserve the region where the target data lives.

## Evidence / supporting sources

### Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python (2026-05-23)

- The source shows an `extract` tool that fetches a page, then prompts Ollama with a JSON Schema and asks it to return only JSON. It also describes a failure case where middle truncation caused infobox fields such as a mayor and postal code to disappear from the snapshot. (`97b228233fb8` · neutral · examples; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])
- A browser or scraper can use a language model to turn page content into structured JSON instead of relying only on deterministic parsers. This is especially useful when the desired output is described in a schema and the information is spread across headings, infoboxes, or loosely structured page text. The technique trades determinism for flexibility: the model can populate arrays and fuzzy fields, but it is still limited by snapshot quality and prompt discipline. It works best when the page snapshot contains the relevant facts and the schema is specific enough to guide extraction. For long pages, snapshot budgeting becomes a first-order design constraint because truncation can remove the exact fields you wanted. (`2029a5f4b00e` · neutral · knowledge_summary; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])
- Use model-based extraction when the structure is too irregular for a simple parser, but treat the output as schema-guided reading rather than guaranteed parsing. Keep the snapshot large enough to preserve the region where the target data lives. (`b36e10a93edd` · neutral · operational_insight; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])
- This is useful for automating page-to-record workflows in knowledge systems, cataloging, compliance review, and support tooling where the input is a web page but the output must be structured fields. It is also relevant when a conversation agent needs to extract specific facts from a page without asking the user to manually copy them. (`5de8c30bc03b` · neutral · relevance_note; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])
- LLM extraction can handle array-shaped outputs that a rigid server-side extractor may reject. (`eb0c37a947e8` · supporting · key_points[0]; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])
- The schema should describe the fields clearly enough that the model can map page text to them. (`b32f0946ce8a` · supporting · key_points[1]; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])
- Snapshot truncation is a major failure mode for infobox-style or mid-page facts. (`840bf7a78454` · supporting · key_points[2]; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])
- "The `extract` tool fetches the page snapshot, then makes its own Ollama call with a strict prompt: here is a schema, here is the page, fill in the schema and respond with only JSON." (`63fd5b9a1dc0` · supporting · supporting_snippet; [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- [[topics/agent-connectivity-layering|Agent Connectivity Layering]]

## Sources

- [[sources/build-your-own-local-web-browsing-llm-agent-in-250-lines-of-python-01kts19400x91hkkaam8ed7tvt|Build Your Own Local Web Browsing LLM Agent in 250 Lines of Python]]
