---
title: '🔬ESMFold2: The Bitter Lesson is Coming for Proteins - Alex Rives, BioHub'
slug: esmfold2-the-bitter-lesson-is-coming-for-proteins-alex-rives-biohub-01ksn8the62x1rdy5sz97gc2rj
category: source
source_id: esmfold2-the-bitter-lesson-is-coming-for-proteins-alex-rives-biohub-01ksn8the62x1rdy5sz97gc2rj
author: Latent.Space
publication: Substack
published_date: '2026-05-27'
assessed_as_of: '2026-05-27'
ingested_at: '2026-06-05T19:51:47.065778+00:00'
canonical_url: mailto:reader-forwarded-email/77ab5655d0a61b5a16d6d9f6a252a695
content_sha256: 2ddfd9de1eb8e3319d15180cafe53d841a5582b48826c45d424972b081f80924
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
---

# 🔬ESMFold2: The Bitter Lesson is Coming for Proteins - Alex Rives, BioHub

This piece is about a new protein AI system from BioHub called ESMFold2. The main idea is simple: instead of baking in a lot of hand-crafted biology assumptions, the team trains huge transformer models on protein sequences and lets the data teach the model structure and function patterns. The author argues this can work surprisingly well, even on tasks where specialized methods like AlphaFold3 are strong. The article also says the model can be used as a kind of protein world model, with separate heads for structure and other downstream tasks. A big part of the excitement is the scale of the release: billions of protein sequences, predicted structures, and tools meant to help with discovery and design.

## Key insights

- The article’s core claim is that enough data and scale can substitute for some protein-specific inductive bias, at least on selected tasks.
- ESMFold2 is presented as a downstream structure-prediction head on top of a broader sequence-trained ‘world model’ rather than as a standalone folding model.
- The author specifically contrasts this with AlphaFold2’s dependence on multiple-sequence alignments, noting that this can be weak for antibodies because such alignments are scarce.
- The release includes a very large protein atlas—6.8 billion proteins and 1.1 billion predicted structures—which makes the artifact potentially reusable beyond the single model.
- The article suggests sparse autoencoders could turn learned protein representations into interpretable semantic features, but that part is more of a research direction than a demonstrated workflow.

## Derived knowledge pages

No derived knowledge pages captured.

## Why it matters

The piece is useful because it compresses a real technical bet into one concrete release: large sequence models may be a more general substrate for protein biology than narrowly engineered structure predictors, at least for some problems BioHub chose to highlight. The article grounds that bet in specific claims: ESMFold2 is said to achieve state-of-the-art interaction performance, especially on antibodies, and to show inference-time scaling across five targets in cancer and immunology. It also gives a reusable mental model for bio-AI work: train a broad sequence model, then add task-specific heads for structure, property prediction, and design. That framing matters for engineering because it suggests the main asset may be a learned representation plus large-scale inference and retrieval infrastructure, not just a single predictor. The large atlas and open MIT-licensed release could make the work more durable than a paper-only claim if the structures and model are actually usable by others. The article’s strongest practical value is as a case study in when to favor scale over domain-specific heuristics, with the antibody/MSA example providing the clearest motivation. The closing implication for service automation is thin here; the article is about protein discovery, not customer workflows, so any automation relevance is indirect at best. Actionable as of 2026-05-27, but still worth treating as a model-and-benchmark claim until independent evaluation confirms the reported gains.

## Limitations / open questions

The evidence is mostly editorial and announcement-driven, not a full methods paper with enough detail to audit the claims. The article cites state-of-the-art interaction results and inference-time scaling, but it does not provide full benchmark tables, baselines, dataset splits, or failure modes in the text shown. It is unclear how much of the reported performance comes from distillation from AlphaFold2-derived data, which the article itself notes for ESMC, and that complicates the clean ‘MSAs-be-damned’ narrative. The practical utility of the 6.8 billion protein atlas depends on access, search quality, and downstream validation, none of which are demonstrated here. The sparse-autoencoder interpretability angle is intriguing, but the article presents it as an idea and a highlight from the episode rather than a validated production technique. Wet-lab validation is mentioned, but the scope, cost, and reproducibility of those experiments are not specified.

## Contradictions / unverified claims

The article’s rhetoric leans hard on the ‘Bitter Lesson’ and ‘world model’ framing, which is conceptually attractive but can overstate how general the approach is across protein subdomains. It also compares ESMFold2 to AlphaFold3 in a way that may hide important differences in task definitions, training data, and evaluation setup. The claim that vanilla BERT-like transformers can beat specialized models on some hard protein problems is plausible, but the text does not show enough detail to know whether the wins are narrow, benchmark-specific, or broadly transferable. The argument that MSAs hurt generalization is directionally reasonable in antibody settings, yet it is still an oversimplification to treat MSAs as uniformly bad rather than one useful inductive bias among others. The article is enthusiastic about programmable biology, but most of that remains aspirational in the text rather than demonstrated end-to-end.

## Source metadata

- Canonical URL: mailto:reader-forwarded-email/77ab5655d0a61b5a16d6d9f6a252a695
- Raw markdown: `raw/readwise/esmfold2-the-bitter-lesson-is-coming-for-proteins-alex-rives-biohub-01ksn8the62x1rdy5sz97gc2rj.md`
- Raw HTML: `raw/readwise/esmfold2-the-bitter-lesson-is-coming-for-proteins-alex-rives-biohub-01ksn8the62x1rdy5sz97gc2rj.html`

## Full source text

---
readwise_id: "01ksn8the62x1rdy5sz97gc2rj"
title: "🔬ESMFold2: The Bitter Lesson is Coming for Proteins - Alex Rives, BioHub"
author: "Latent.Space"
publication: "Substack"
source_url: "mailto:reader-forwarded-email/77ab5655d0a61b5a16d6d9f6a252a695"
category: "email"
location: "archive"
published_date: "2026-05-27"
saved_at: "2026-05-27T17:48:23.878000+00:00"
updated_at: "2026-05-31T11:36:02.973872+00:00"
tags: ["processed"]
---

ESMFold2 is a new AI model that predicts protein structures by learning from billions of protein sequences without relying on traditional methods. It works well for complex proteins like antibodies, where older models struggle. This approach helps scientists design new proteins and understand biology better, moving towards programmable biology.
