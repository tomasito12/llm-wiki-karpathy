---
title: I Found a Full LLM Wiki App. So I Built the Smaller Thing I Actually Needed.
slug: i-found-a-full-llm-wiki-app-so-i-built-the-smaller-thing-i-actually-needed-01kqz036fj7zddpk9fppjf11va
category: source
tags:
- agent-systems
- knowledge-systems
source_id: i-found-a-full-llm-wiki-app-so-i-built-the-smaller-thing-i-actually-needed-01kqz036fj7zddpk9fppjf11va
author: Mark Chen
publication: Medium
published_date: '2026-04-29'
assessed_as_of: '2026-04-29'
ingested_at: '2026-05-22T16:38:44.812110+00:00'
canonical_url: https://medium.com/@markchen69/i-found-a-full-llm-wiki-app-so-i-built-the-smaller-thing-i-actually-needed-62c629b3c8d2
content_sha256: 243ebbdfcd5bdcb9f33524fe4621338bd0a9496383f11641af48e05111cb5a6d
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
derived_topics:
- topics/llm-wiki.md
- topics/two-step-document-ingest.md
derived_pages:
- topics/llm-wiki.md
- topics/two-step-document-ingest.md
---

# I Found a Full LLM Wiki App. So I Built the Smaller Thing I Actually Needed.

This piece is about building a personal knowledge system that an artificial intelligence assistant can help maintain. The author started with a simple folder of Markdown files and then found a much larger project that showed how the same idea could become a full desktop app. Instead of copying everything, the author focused on the parts that would make the small setup smarter and easier to keep clean. One important idea was adding a file that explains the purpose of the wiki, so the assistant knows what kind of knowledge matters. Another was splitting work into two steps: first analyze the source, then write the wiki entry. The author also liked the idea of putting some items into a human review queue when the assistant is unsure. Because the wiki already lived in Markdown, the author chose to build a skill for the coding assistant rather than a whole new app. The result was a lighter system that still gets better over time. The piece is most useful as of 2026-04-29 for people who want a practical way to organize notes and sources without overbuilding.

## Key insights

- A purpose file can act as a stable policy layer for a personal wiki, steering what gets preserved and why.
- Two-step ingest is safer than direct write-through because it separates source analysis from permanent knowledge updates.
- A human review queue is useful when metric definitions, architecture choices, or source conflicts are still unsettled.
- For a Markdown-native knowledge base, a project-level skill may deliver most of the value of a full app with less complexity.
- The durable lesson is to improve maintenance behavior before adding more interface features.

## Derived knowledge pages

- [[topics/llm-wiki]]
- [[topics/two-step-document-ingest]]

## Why it matters

The article is useful because it reframes an LLM Wiki as an operating system for knowledge maintenance rather than just a document store. The most durable idea is the separation of raw sources, generated wiki pages, and agent instructions, because that boundary makes it easier to preserve provenance and prevent permanent overcommitment to a bad source. The described two-step ingest pattern is especially practical: analyze first, then generate, so the model can identify claims, contradictions, and review items before it starts rewriting the knowledge base. The purpose file adds another durable control point by telling the agent what the wiki is for, which is more useful than generic summarization when the source mix includes business documents, KPI notes, and changing architecture decisions. The review queue also matters because it keeps judgment with the human when definitions are draft or sources conflict. For service automation, the closing implication is narrow but real: the same maintenance pattern can help keep support or operations knowledge bases less stale, but the article is not about customer support systems specifically. Actionable as of 2026-04-29, especially for Markdown-based personal or team knowledge workflows; the broader value is in disciplined maintenance habits, not a flashy new interface.

## Limitations / open questions

The article is a personal account, so it does not provide measured outcomes, error rates, or comparative evaluations of the app versus the skill-based approach. The strongest claims are about usefulness and workflow fit rather than quantified performance. It is also unclear how well the described maintenance pattern scales when many users edit the same knowledge base or when ingestion volume is high. The piece does not explain the exact review heuristics, failure modes for provenance tracking, or how duplicate concept detection is implemented. The “skill now, app later” choice is plausible for a Markdown-native setup, but the article does not test whether that remains sufficient once the wiki becomes much larger or more collaborative.

## Contradictions / unverified claims

The piece is honest that the full app is impressive, but it also makes a gentle tradeoff argument that may not hold for everyone: a skill is enough if you already live in Markdown, yet that is a workflow preference rather than a universal rule. The article sometimes treats richer structure as obviously better, but it does not show a case where the extra layers materially improved outcomes beyond perceived organization. The claims about better judgment, cleaner maintenance, and less forgetfulness are sensible, but they remain qualitative.

## Source metadata

- Canonical URL: https://medium.com/@markchen69/i-found-a-full-llm-wiki-app-so-i-built-the-smaller-thing-i-actually-needed-62c629b3c8d2
- Raw markdown: `raw/readwise/i-found-a-full-llm-wiki-app-so-i-built-the-smaller-thing-i-actually-needed-01kqz036fj7zddpk9fppjf11va.md`
- Raw HTML: `raw/readwise/i-found-a-full-llm-wiki-app-so-i-built-the-smaller-thing-i-actually-needed-01kqz036fj7zddpk9fppjf11va.html`

## Full source text

---
readwise_id: 01kqz036fj7zddpk9fppjf11va
title: I Found a Full LLM Wiki App. So I Built the Smaller Thing I Actually Needed.
author: Mark Chen
source_url: https://medium.com/@markchen69/i-found-a-full-llm-wiki-app-so-i-built-the-smaller-thing-i-actually-needed-62c629b3c8d2
category: article
location: archive
published_date: '2026-04-29'
saved_at: '2026-05-06T15:56:51.058000+00:00'
updated_at: '2026-05-06T17:35:43.071596+00:00'
tags:
- processed
publication: Medium
---

Mark Chen built a simple tool to keep his personal knowledge base organized using ideas from a bigger LLM Wiki app. He focused on clear purpose, careful two-step processing, and human review to improve the wiki. The key lesson is to start small and build a system that fits your real needs and grows over time.
