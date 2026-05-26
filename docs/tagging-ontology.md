# Tagging Ontology (Review Layer)

Tags classify **proposals** during ingest review for retrieval, clustering, and future synthesis.
They are **not** wiki frontmatter tags (`ai-engineering`, `tools`, `models`).

## Core principles

1. **Keep tags boring** — obvious, stable, reusable, retrieval-oriented, semantically narrow.
2. **Retrieval anchors, not article summaries** — durable conceptual neighborhoods, not title echoes.
3. **Stable abstractions** — prefer `visual-specifications` over `image-generation-for-ui-code`.
4. **Minimize ontology drift** — map to existing vocabulary before inventing new tags.
5. **Overlap is OK** — multiple tags per proposal when each improves retrieval.

## Global namespaces (coarse routing)

Use **1–3** per topic/trend proposal when genuinely applicable (subset of topic/trend allowlists):

`ai-engineering`, `ai-governance`, `ai-economics`, `ai-safety`, `enterprise-ai`, `multimodal-ai`,
`agent-systems`, `developer-tools`, `model-behavior`, `software-engineering`, `infrastructure`,
`enterprise-workflows`, `coding-agents`, `ai-policy`, `ai-evaluation`, `orchestration`,
`runtime-systems`, `organizational-design`, `ai-research`

## Artifact-specific vocabularies

| Artifact | Allowlist file | Field |
|----------|----------------|-------|
| Topics, insights | `config/review_tags_topics.yaml` | `proposed_tags` |
| Trends, signals | `config/review_tags_trends.yaml` | `proposed_tags` |
| Glossary | `config/review_tags_glossary.yaml` | `proposed_tags` |
| How-tos | same as topics | `proposed_tags` |
| Impl studies | `config/review_tags_impl_study.yaml` | `proposed_tags` |
| Tools (retrieval) | `config/review_tags_tools.yaml` | `proposed_tags` |
| Tools (archetype) | `config/review_tool_types.yaml` | `proposed_types` |
| Models (retrieval) | `config/review_tags_models.yaml` | `proposed_tags` |
| Models (archetype) | `config/review_model_types.yaml` | `proposed_types` |

**Never mix** trend tags on topics or tool retrieval tags on trends.

## Anti-patterns

- Article-specific slugs, launch names, vendor marketing, quality adjectives
- Clever abstractions: `execution-layer-transformation`, `orchestration-synergy`
- Tags that only make sense after reading one article

## Migration

Old slugs are mapped via `config/tag_migration.yaml`. Run `hatch run tag-migrate` after ontology updates.
