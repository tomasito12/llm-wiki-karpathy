---
title: 'The Sequence AI of the Week #863: The Model is the Interface: Inside Thinking
  Machines'' Interactive Models'
slug: the-sequence-ai-of-the-week-863-the-model-is-the-interface-inside-thinking-machines-interactive-models-01ks2hmn3zsq6emgx6m9pxtyfv
category: source
source_id: the-sequence-ai-of-the-week-863-the-model-is-the-interface-inside-thinking-machines-interactive-models-01ks2hmn3zsq6emgx6m9pxtyfv
author: Jesus Rodriguez
publication: substack.com
published_date: '2026-05-20'
assessed_as_of: '2026-05-20'
ingested_at: '2026-06-09T18:32:43+00:00'
canonical_url: https://thesequence.substack.com/p/the-sequence-ai-of-the-week-863-the
content_sha256: 0a1138920907be3965c5d864bf01bd8af2af548cc3b58cd0decc22b0058cd186
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
---

# The Sequence AI of the Week #863: The Model is the Interface: Inside Thinking Machines' Interactive Models

This piece is about a different way to interact with large language models. Instead of treating the model like a chatbot that only processes text turn by turn, it argues for interfaces that handle interaction as something happening over time. The basic idea is that collaboration is not always best represented as a neat text stream. Thinking Machines’ work is presented as an early attempt to make that richer interaction feel natural. The article is mostly a framing piece, but the framing itself is the main point.

## Key insights

- The article’s central abstraction is that collaboration is temporal, not just textual.
- It treats plain chat as a narrow serialization of interaction, not the natural shape of all model use.
- The model is presented as the interface, which suggests the interaction layer should be native rather than bolted on.
- Multimodality is framed as part of the interaction model, not just an input/output feature.
- The source is only a preview excerpt, so the concrete implementation and evaluation claims are not available here.

## Derived knowledge pages

No derived knowledge pages captured.

## Why it matters

The piece is useful as a framing exercise for AI engineers who design model-facing product surfaces. Its main contribution is the insistence that a text-only turn structure may be too simple for workflows where the user and model coordinate over time, especially when edits, partial outputs, and multiple modalities matter. That is a durable design question even though the excerpt does not show the full implementation. The article also suggests a different product boundary: instead of wrapping a model in a chat UI, the interaction primitive itself can be the model. As of 2026-05-20, this is best treated as an early concept to watch rather than an operational pattern to adopt on the strength of this excerpt alone. The practical value is limited by the absence of details on latency, state handling, evaluation, or how the interactive model behaves under real tasks. The source does not substantiate broader claims about the market or deployment outcomes. For service automation, support, voice, or meeting-style workflows, the implication is only indirect here: richer temporal interaction could matter, but this article does not show a concrete automation use case.

## Limitations / open questions

The imported text is incomplete, so the article’s actual mechanism, architecture, and evaluation are missing. There are no benchmarks, user studies, latency numbers, or deployment examples. It is unclear how these interactive models manage state, revision, multimodal synchronization, or failure recovery. The excerpt also does not show whether the ideas are a research prototype, a product direction, or a polished system. Without concrete evidence, it is hard to judge whether the framing yields measurable gains over standard chat interfaces.

## Contradictions / unverified claims

The piece leans on a strong conceptual claim—collaboration is temporal—without evidence in the excerpt that this yields practical superiority. Calling the work impressive while providing no specifics makes the assessment feel more promotional than validated. The “model is the interface” idea is compelling, but it remains abstract here and could collapse into familiar interface redesign language if not backed by concrete interaction mechanisms.

## Source metadata

- Canonical URL: https://thesequence.substack.com/p/the-sequence-ai-of-the-week-863-the
- Raw markdown: `raw/readwise/the-sequence-ai-of-the-week-863-the-model-is-the-interface-inside-thinking-machines-interactive-models-01ks2hmn3zsq6emgx6m9pxtyfv.md`
- Raw HTML: `raw/readwise/the-sequence-ai-of-the-week-863-the-model-is-the-interface-inside-thinking-machines-interactive-models-01ks2hmn3zsq6emgx6m9pxtyfv.html`

## Full source text

---
readwise_id: "01ks2hmn3zsq6emgx6m9pxtyfv"
title: "The Sequence AI of the Week #863: The Model is the Interface: Inside Thinking Machines' Interactive Models"
author: "Jesus Rodriguez"
publication: "substack.com"
source_url: "https://thesequence.substack.com/p/the-sequence-ai-of-the-week-863-the"
category: "rss"
location: "archive"
published_date: "2026-05-20"
saved_at: "2026-05-20T11:16:51.016000+00:00"
updated_at: "2026-05-20T20:49:28.296599+00:00"
tags: ["processed"]
---

Thinking Machines’ interactive models turn real-time conversation, vision, audio, and tool use into one continuous learned system.
