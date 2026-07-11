---
title: How I Use Obsidian + Claude Cowork to Run My Life
slug: how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c
category: source
tags:
- ai-engineering
- frontier-model
- knowledge-systems
- orchestration
- proprietary-model
- runtime-architecture
- workflow-design
source_id: how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c
author: Linking Your Thinking with Nick Milo
publication: YouTube
published_date: '2026-06-05'
assessed_as_of: '2026-06-05'
ingested_at: '2026-06-16T16:25:09.060312+00:00'
canonical_url: https://youtube.com/watch/?v=rRa9td4oe7k
content_sha256: b11009e9d0c68900341b74b9f22c219810357d7d9186cf11581dcb57536b131b
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
derived_how_to:
- how-to/file-native-ai-workspace.md
derived_models:
- foundation-models/opus-4-6.md
- foundation-models/sonnet-4-6.md
derived_topics:
- topics/file-native-ai-workflows.md
- topics/translation-layer-ai-architecture.md
derived_pages:
- foundation-models/opus-4-6.md
- foundation-models/sonnet-4-6.md
- how-to/file-native-ai-workspace.md
- topics/file-native-ai-workflows.md
- topics/translation-layer-ai-architecture.md
---

# How I Use Obsidian + Claude Cowork to Run My Life

This video explains a way to connect personal notes to an AI tool without locking yourself into one app. The idea is to keep your thinking in plain markdown notes, then add a small set of map files that tell the AI who you are, how to move through your notes, and what skills it can use. Claude Co-work is used as the example tool, but the system is meant to be portable if you switch tools later. The setup is interesting because it treats AI as a layer on top of your own files, not as the place where your knowledge lives. It also shows how the same structure can power daily planning, note capture, reviews, and sharing with a team.

## Key insights

- Treat your note vault as the durable core and the AI tool as replaceable plumbing.
- Use a portable identity file plus a vault map and skill map to keep AI navigation explicit instead of relying on full-context scanning.
- Separate AI-generated material into its own folder so your personal note base stays clean and easy to manage.
- Recurring prompts can reduce session drift because the model may not reliably load all needed context at the start of a new chat.
- A maintenance skill matters because a real AI workflow needs cleanup, sanitization, and ongoing file hygiene, not just generation.

## Derived knowledge pages

- [[foundation-models/opus-4-6]]
- [[foundation-models/sonnet-4-6]]
- [[how-to/file-native-ai-workspace]]
- [[topics/file-native-ai-workflows]]
- [[topics/translation-layer-ai-architecture]]

## Why it matters

The piece is valuable because it offers a concrete pattern for making AI workflows less vendor-dependent and more maintainable: keep notes in markdown, keep identity and instruction files in your own vault, and let the tool sit on top as a swappable layer. That is a stronger operational idea than simply prompting a chatbot, because the video explicitly separates durable personal knowledge from AI-specific instructions and from the external model. The vault map and skill map are the most reusable concepts here: they compress a large note base into a navigable structure so the AI can find relevant context without pretending to have read everything. The article also makes a practical point that is easy to miss in AI demos: long-lived systems need routines for recurring work, context loading, capture, review, and cleanup, not just generation. The daily brief and daily log examples show how the same architecture can be used to pull together calendar, email, task, and note signals into structured daily workflows. The emphasis on storage in files you can open outside Obsidian is a useful durability claim, but it is still a single-person implementation rather than evidence of broader reliability. As of 2026-06-05, the approach looks actionable for practitioners who already manage a substantial note base and want a portable AI workflow; it is best treated as a solid implementation pattern to adapt, not as a proven universal standard.

## Limitations / open questions

The video is a personal workflow demo, not a benchmarked evaluation, so it does not show error rates, time saved, or comparative reliability against alternative systems. Several important details are deferred to linked guides, including the exact contents of the map files, the skill definitions, and the setup steps for recurring tasks. The claim that Claude does not train on user data is presented as a deciding factor, but the video does not analyze the full privacy model or retention implications beyond mentioning a rolling 30-day server window. It also assumes a fairly large, well-structured vault and a user willing to maintain maps and skill files; the maintenance burden for smaller or messier vaults is not quantified. The system depends on recurring prompts and careful folder selection, so failures in setup could produce misleading or incomplete AI behavior. It is unclear how robust the approach is across different AI tools beyond the speaker's own preference for Claude Co-work.

## Contradictions / unverified claims

The video argues for portability and anti-lock-in, but it still relies on a vendor-specific desktop app and its folder-permission model, so the independence is partial rather than absolute. The claim that an AI can safely interact with a 17,000-note vault only if given maps is plausible, but the video does not test that against simpler retrieval or search-based approaches. Several systems are described in promotional terms, and their effectiveness is asserted from personal use rather than independently verified. The future-oriented comments about local models and on-device silicon are speculative and are not supported with evidence in the source itself.

## Source metadata

- Canonical URL: https://youtube.com/watch/?v=rRa9td4oe7k
- Raw markdown: `raw/readwise/how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c.md`
- Raw HTML: `raw/readwise/how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c.html`

## Full source text

---
readwise_id: "01kv4tcedck5ftexd9hqeptc7c"
title: "How I Use Obsidian + Claude Cowork to Run My Life"
author: "Linking Your Thinking with Nick Milo"
publication: "YouTube"
source_url: "https://youtube.com/watch/?v=rRa9td4oe7k"
category: "video"
location: "archive"
published_date: "2026-06-05"
saved_at: "2026-06-15T04:59:34.700000+00:00"
updated_at: "2026-06-15T15:03:01.647081+00:00"
tags: ["processed"]
---

Nick Milo uses Obsidian to store and link his ideas in a simple folder system called the ideaverse. He connects this with Claude Co-work, an AI tool that reads his notes and helps manage tasks and daily briefs. This setup keeps his ideas safe and flexible, letting him switch AI tools without losing control.
