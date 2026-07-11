---
title: 'The Sequence Knowledge #866: Three Text Diffusion Models You Need To Know
  About'
slug: the-sequence-knowledge-866-three-text-diffusion-models-you-need-to-know-about-01kshz8jb3nx8m3gw4r97f2brs
category: source
tags:
- ai-engineering
- ai-research
- frontier-model
- inference-systems
- model-behavior
- proprietary-model
- runtime-systems
source_id: the-sequence-knowledge-866-three-text-diffusion-models-you-need-to-know-about-01kshz8jb3nx8m3gw4r97f2brs
author: Jesus Rodriguez
publication: substack.com
published_date: '2026-05-26'
assessed_as_of: '2026-05-26'
ingested_at: '2026-06-09T15:46:31.400209+00:00'
canonical_url: https://thesequence.substack.com/p/the-sequence-knowledge-866-three
content_sha256: 72df246855da38768c3531ff231c9a61d28d11be609a99efd4ae90da6da4320d
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
derived_models:
- foundation-models/mercury.md
derived_topics:
- topics/diffusion-as-sequence-generation.md
- topics/text-diffusion-models.md
derived_trends:
- industry-trends/text-generation-moves-beyond-left-to-right-decoding.md
derived_pages:
- foundation-models/mercury.md
- industry-trends/text-generation-moves-beyond-left-to-right-decoding.md
- topics/diffusion-as-sequence-generation.md
- topics/text-diffusion-models.md
---

# The Sequence Knowledge #866: Three Text Diffusion Models You Need To Know About

This article is about text diffusion models, which generate language by refining noisy text instead of writing one token after another. The basic idea is closer to editing than typing: the model looks at the whole sequence, fixes many spots at once, and can revisit earlier choices. The piece says this matters because it offers a different way to build language models, not just a small tweak to existing ones. It uses three examples to anchor the idea: LLaDA, Mercury, and Gemini Diffusion. The point is that these models show the approach can be studied, used in products, and taken seriously by frontier labs. As of 2026-05-26, the article treats the space as early but credible, not fully settled.

## Key insights

- Text diffusion treats generation as iterative denoising over a whole sequence, not left-to-right token completion.
- Because the model revises many positions at once, it can use bidirectional context during generation.
- The article positions LLaDA as the strongest evidence that diffusion scales into a real large language model.
- Mercury is presented as the example that turns diffusion into a commercial speed advantage, though the excerpt gives no benchmark details.
- Gemini Diffusion is used as signaling evidence that frontier labs view the paradigm as strategically important.

## Derived knowledge pages

- [[foundation-models/mercury]]
- [[industry-trends/text-generation-moves-beyond-left-to-right-decoding]]
- [[topics/diffusion-as-sequence-generation]]
- [[topics/text-diffusion-models]]

## Why it matters

The article is useful because it compresses a new model family into one mental frame: diffusion for text is not just a decoding trick, but a different training and generation setup that may change how sequence models are built. For AI engineers, the main takeaway is that the relevant comparison is no longer only quality on next-token prediction; the source argues that diffusion can support whole-sequence revision, bidirectional context, and multi-position updates during generation. That makes the architecture worth tracking as a separate design path rather than as a minor variant of standard autoregressive LLMs. The three examples also map the field onto three practical questions: can it scale, can it be monetized, and do frontier labs care enough to invest in it. The article does not provide enough evidence here to conclude how broadly applicable these claims are, but it does establish why the category deserves attention. As of 2026-05-26, the sensible posture is to monitor diffusion-language systems as an emerging alternative and not to assume they have displaced token-by-token generation. The service-automation, support, voice, and meeting implications are not discussed in this excerpt, so they should not be read into the piece.

## Limitations / open questions

The excerpt gives no benchmark table, task breakdown, latency numbers, or cost comparisons, so claims about speed and commercial advantage are not verifiable here. It also does not explain training data, inference procedure, sequence length limits, or failure modes for the named systems. The article asserts that LLaDA, Mercury, and Gemini Diffusion define the conversation, but that is a framing choice rather than demonstrated field consensus in the text. Open questions include whether iterative denoising preserves quality on long-form generation, how well it handles controllability, and what the compute tradeoffs are versus autoregressive models.

## Contradictions / unverified claims

The piece makes a strong architectural contrast between diffusion and next-token generation, but the excerpt does not show evidence that the difference is always operationally decisive. Calling Mercury a commercial speed advantage and Gemini Diffusion strategic validation is plausible framing, yet the article supplies no hard numbers or deployment detail in the excerpt. The ‘scientific proof, industrial deployment, frontier validation’ storyline is elegant, but it is still an interpretation layered on top of three named systems rather than a demonstrated industry taxonomy.

## Source metadata

- Canonical URL: https://thesequence.substack.com/p/the-sequence-knowledge-866-three
- Raw markdown: `raw/readwise/the-sequence-knowledge-866-three-text-diffusion-models-you-need-to-know-about-01kshz8jb3nx8m3gw4r97f2brs.md`
- Raw HTML: `raw/readwise/the-sequence-knowledge-866-three-text-diffusion-models-you-need-to-know-about-01kshz8jb3nx8m3gw4r97f2brs.html`

## Full source text

---
readwise_id: "01kshz8jb3nx8m3gw4r97f2brs"
title: "The Sequence Knowledge #866: Three Text Diffusion Models You Need To Know About"
author: "Jesus Rodriguez"
publication: "substack.com"
source_url: "https://thesequence.substack.com/p/the-sequence-knowledge-866-three"
category: "rss"
location: "archive"
published_date: "2026-05-26"
saved_at: "2026-05-26T11:03:31.500000+00:00"
updated_at: "2026-05-27T10:12:17.051106+00:00"
tags: ["processed"]
---

LlaDa, Gemini Diffusion and Mercury rule the space.
