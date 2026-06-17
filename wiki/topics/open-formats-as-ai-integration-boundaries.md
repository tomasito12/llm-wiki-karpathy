---
title: Open Formats as AI Integration Boundaries
slug: open-formats-as-ai-integration-boundaries
entity_id: topic:open-formats-as-ai-integration-boundaries
category: topic
tags:
- ai-engineering
- infrastructure
- runtime-systems
first_seen: '2026-01-16'
last_seen: '2026-05-23'
source_count: 2
evidence_count: 17
source_ids:
- obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk
- why-you-should-completely-avoid-ollama-in-2026-01ktpkravej1x72c85xxb312wd
value_level: high
confidence: 0.855
synthesis_state: stage1-placeholder
---

# Open Formats as AI Integration Boundaries

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Open file formats make it easier to add AI assistance without surrendering control of the underlying data. The application remains the system of record, while the AI becomes a tool that reads and writes in a documented format. That reduces lock-in and makes migrations or alternative clients more plausible. The design works best when the formats are human-readable and stable enough for repeated editing.

## Examples

The source explicitly points to local Markdown, Bases, and JSON Canvas as the formats Obsidian uses to stay portable. It contrasts this with proprietary app databases and vendors that try to absorb the whole workflow.

## Key Points

- The system of record should remain in open, inspectable files where possible.
- AI integration is more maintainable when it respects existing file boundaries.
- Portability is a product decision as much as a technical one.
- Model-file portability is part of system resilience.
- Opaque registries can create lock-in even when a product is branded as open source.
- Open formats make it easier to compare engines and recover from tool churn.
- Artifact portability matters for both local experimentation and production migration.

## Operational Insight

Design AI features around durable file boundaries rather than proprietary app state when portability matters. This makes it easier to swap clients, audit outputs, and keep a human-editable source of truth.

## Related Topics

- file-grammar-skills-for-ai
- local-model-deployment
- knowledge-base-becomes-runtime-infrastructure

## Evidence / supporting sources

### Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault. (2026-01-16)

- The source explicitly points to local Markdown, Bases, and JSON Canvas as the formats Obsidian uses to stay portable. It contrasts this with proprietary app databases and vendors that try to absorb the whole workflow. (`21a491fe5925` · neutral · examples; [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]])
- Open file formats make it easier to add AI assistance without surrendering control of the underlying data. The application remains the system of record, while the AI becomes a tool that reads and writes in a documented format. That reduces lock-in and makes migrations or alternative clients more plausible. The design works best when the formats are human-readable and stable enough for repeated editing. (`d6038c8a33a3` · neutral · knowledge_summary; [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]])
- Design AI features around durable file boundaries rather than proprietary app state when portability matters. This makes it easier to swap clients, audit outputs, and keep a human-editable source of truth. (`193ff42cc471` · neutral · operational_insight; [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]])
- This is durable for AI engineering because many knowledge and content workflows fail when the AI vendor owns the data model. Open formats let organizations build assistant-like systems while keeping exit options and toolchain flexibility. (`7d10975d9b7b` · neutral · relevance_note; [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]])
- The system of record should remain in open, inspectable files where possible. (`cb1ab61c1007` · supporting · key_points[0]; [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]])
- AI integration is more maintainable when it respects existing file boundaries. (`efc69518affa` · supporting · key_points[1]; [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]])
- Portability is a product decision as much as a technical one. (`174e1d8a5e9a` · supporting · key_points[2]; [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]])
- "The key point: Skills are not plugins. They don't require migrating your data into a proprietary app database." (`782c0e5d0dd7` · supporting · supporting_snippet; [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]])

### Why You Should Completely Avoid Ollama in 2026 (2026-05-23)

- The source says Ollama used a "proprietary model storage format" and that "You couldn’t just point llama.cpp, LM Studio, or any other inference framework at those files." (`a9c42d1a5f36` · neutral · examples; [[sources/why-you-should-completely-avoid-ollama-in-2026-01ktpkravej1x72c85xxb312wd|Why You Should Completely Avoid Ollama in 2026]])
- Open file and model formats make it easier to move workloads between runtimes, tools, and deployment environments. When model artifacts are stored in proprietary or opaque formats, the operational cost of switching rises and the system becomes harder to audit, test, and reuse. Open formats are especially important in model-serving stacks, where portability determines whether teams can migrate to faster engines or safer workflows without reprocessing artifacts. This is a design issue, not just a licensing issue. (`5877dd11425e` · neutral · knowledge_summary; [[sources/why-you-should-completely-avoid-ollama-in-2026-01ktpkravej1x72c85xxb312wd|Why You Should Completely Avoid Ollama in 2026]])
- Use open formats when the same artifacts may need to move across local runners, GUIs, and production servers. Portability is an operational safeguard: it lowers switching cost and reduces the chance that a tool choice traps the team inside one ecosystem. (`4842b3a7792d` · neutral · operational_insight; [[sources/why-you-should-completely-avoid-ollama-in-2026-01ktpkravej1x72c85xxb312wd|Why You Should Completely Avoid Ollama in 2026]])
- This is durable for AI systems because model and artifact portability affects model serving, evaluation, and recovery from vendor or tool changes. Teams building service automation benefit when model files, configs, and outputs are inspectable and transferable across runtimes. (`01eae205b09c` · neutral · relevance_note; [[sources/why-you-should-completely-avoid-ollama-in-2026-01ktpkravej1x72c85xxb312wd|Why You Should Completely Avoid Ollama in 2026]])
- Model-file portability is part of system resilience. (`88663b3ad1d2` · supporting · key_points[0]; [[sources/why-you-should-completely-avoid-ollama-in-2026-01ktpkravej1x72c85xxb312wd|Why You Should Completely Avoid Ollama in 2026]])
- Opaque registries can create lock-in even when a product is branded as open source. (`bf25f6777d90` · supporting · key_points[1]; [[sources/why-you-should-completely-avoid-ollama-in-2026-01ktpkravej1x72c85xxb312wd|Why You Should Completely Avoid Ollama in 2026]])
- Open formats make it easier to compare engines and recover from tool churn. (`87d873c0f6cf` · supporting · key_points[2]; [[sources/why-you-should-completely-avoid-ollama-in-2026-01ktpkravej1x72c85xxb312wd|Why You Should Completely Avoid Ollama in 2026]])
- Artifact portability matters for both local experimentation and production migration. (`58214ec51150` · supporting · key_points[3]; [[sources/why-you-should-completely-avoid-ollama-in-2026-01ktpkravej1x72c85xxb312wd|Why You Should Completely Avoid Ollama in 2026]])
- "You couldn’t just point llama.cpp, LM Studio, or any other inference framework at those files." (`9e15e670e5cd` · supporting · supporting_snippet; [[sources/why-you-should-completely-avoid-ollama-in-2026-01ktpkravej1x72c85xxb312wd|Why You Should Completely Avoid Ollama in 2026]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- file-grammar-skills-for-ai
- knowledge-base-becomes-runtime-infrastructure
- local-model-deployment

## Sources

- [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]]
- [[sources/why-you-should-completely-avoid-ollama-in-2026-01ktpkravej1x72c85xxb312wd|Why You Should Completely Avoid Ollama in 2026]]
