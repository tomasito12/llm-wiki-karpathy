---
title: Two-Pass Document Ingestion
slug: two-pass-document-ingestion
entity_id: how_to:two-pass-document-ingestion
category: how-to
tags:
- knowledge-systems
first_seen: '2026-05-08'
last_seen: '2026-05-08'
source_count: 1
evidence_count: 14
source_ids:
- this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g
value_level: high
confidence: 0.93
synthesis_state: stage1-placeholder
---

# Two-Pass Document Ingestion

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
This is a way to process documents so the model first thinks through the material and only later writes the final output. It helps when one step has to do two different jobs: understand the source and produce clean, structured text. That matters when the output needs stable formatting, links, and citations, because combining those tasks in one prompt often causes mistakes. The procedure is useful for document-heavy workflows where accuracy matters more than speed.

## Caveats

This pattern costs more tokens than a single-pass workflow, and the article warns that a 30-page PDF can take tens of thousands of tokens on a frontier model. It also depends on the model staying disciplined with format and links. Human review still matters because the model can generate wrong summaries or bad cross-references.

## Implementation Steps

- Load the source document together with the purpose file and existing index.
- Ask the model to produce a structured analysis instead of final prose.
- Check the analysis for missing entities, contradictions, and questionable updates.
- Use the analysis as the blueprint for the final markdown generation step.
- Store generated pages separately from immutable source files.
- Run periodic linting to catch orphan pages, dead links, and stale claims.

## Prerequisites

- A source document archive
- A purpose file that defines scope
- A schema or output format the model must follow
- A review loop for ambiguous updates

## Evidence / supporting sources

### This Open-Source App Turns Your Documents Into a Self-Building Wiki (2026-05-08)

- First ask the model to analyze the document with the purpose file and existing index in view. Have it identify the important entities, contradictions, and changes that should happen in the wiki. Then use that analysis as the blueprint for a second prompt that writes the final markdown files. Keep the raw source files unchanged so you can check the generated pages against them later. Review the analysis before generation when the update is ambiguous. (`032998698d34` · neutral · answer_summary; [[sources/this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g|This Open-Source App Turns Your Documents Into a Self-Building Wiki]])
- Load the source document together with the purpose file and existing index. (`15415219af03` · neutral · implementation_steps[0]; [[sources/this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g|This Open-Source App Turns Your Documents Into a Self-Building Wiki]])
- Ask the model to produce a structured analysis instead of final prose. (`c3351cc342dd` · neutral · implementation_steps[1]; [[sources/this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g|This Open-Source App Turns Your Documents Into a Self-Building Wiki]])
- Check the analysis for missing entities, contradictions, and questionable updates. (`bd4c06f85380` · neutral · implementation_steps[2]; [[sources/this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g|This Open-Source App Turns Your Documents Into a Self-Building Wiki]])
- Use the analysis as the blueprint for the final markdown generation step. (`d661df75e09f` · neutral · implementation_steps[3]; [[sources/this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g|This Open-Source App Turns Your Documents Into a Self-Building Wiki]])
- Store generated pages separately from immutable source files. (`e8f56acecd4a` · neutral · implementation_steps[4]; [[sources/this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g|This Open-Source App Turns Your Documents Into a Self-Building Wiki]])
- Run periodic linting to catch orphan pages, dead links, and stale claims. (`7d2b3ecc8843` · neutral · implementation_steps[5]; [[sources/this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g|This Open-Source App Turns Your Documents Into a Self-Building Wiki]])
- A source document archive (`26dcfe8bbfab` · neutral · prerequisites[0]; [[sources/this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g|This Open-Source App Turns Your Documents Into a Self-Building Wiki]])
- A purpose file that defines scope (`06bba7002a8c` · neutral · prerequisites[1]; [[sources/this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g|This Open-Source App Turns Your Documents Into a Self-Building Wiki]])
- A schema or output format the model must follow (`7fe9f872ec12` · neutral · prerequisites[2]; [[sources/this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g|This Open-Source App Turns Your Documents Into a Self-Building Wiki]])
- A review loop for ambiguous updates (`9a83b7a989e2` · neutral · prerequisites[3]; [[sources/this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g|This Open-Source App Turns Your Documents Into a Self-Building Wiki]])
- This is a way to process documents so the model first thinks through the material and only later writes the final output. It helps when one step has to do two different jobs: understand the source and produce clean, structured text. That matters when the output needs stable formatting, links, and citations, because combining those tasks in one prompt often causes mistakes. The procedure is useful for document-heavy workflows where accuracy matters more than speed. (`9dba9086f999` · neutral · what_and_problem; [[sources/this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g|This Open-Source App Turns Your Documents Into a Self-Building Wiki]])
- The first call is purely analytical. ... The second call takes that analysis as a blueprint and generates the actual markdown files. (`9e7af9aa9bea` · supporting · supporting_snippet; [[sources/this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g|This Open-Source App Turns Your Documents Into a Self-Building Wiki]])
- This pattern costs more tokens than a single-pass workflow, and the article warns that a 30-page PDF can take tens of thousands of tokens on a frontier model. It also depends on the model staying disciplined with format and links. Human review still matters because the model can generate wrong summaries or bad cross-references. (`8d2016a4a8c2` · uncertainty · caveats; [[sources/this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g|This Open-Source App Turns Your Documents Into a Self-Building Wiki]])

## Contradictions / tensions

- This pattern costs more tokens than a single-pass workflow, and the article warns that a 30-page PDF can take tens of thousands of tokens on a frontier model. It also depends on the model staying disciplined with format and links. Human review still matters because the model can generate wrong summaries or bad cross-references. (uncertainty; [[sources/this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g|This Open-Source App Turns Your Documents Into a Self-Building Wiki]])

## Related pages

- [[how-to/local-model-deployment|Local Model Deployment]]
- [[how-to/procedural-support-automation|Procedural Support Automation]]

## Sources

- [[sources/this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g|This Open-Source App Turns Your Documents Into a Self-Building Wiki]]
