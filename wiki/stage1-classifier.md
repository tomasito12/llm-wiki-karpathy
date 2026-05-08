---
title: Stage 1 — Classifier (radar vs tools overview vs other non-radar)
type: style
created: 2026-05-05
updated: 2026-05-06
sources: []
tags: [ingest, classifier, stage-1]
---

Run this before editing any wiki content for a new Readwise item.

## Raw inputs (mandatory)

1. Read `raw/readwise/<basename>.md` **frontmatter only** for metadata.
2. Read paired `raw/readwise/<basename>.html` in full for content extraction.

If paired `.html` is missing, stop and request re-export.

## Decision (two questions)

Answer in order:

### Q1 — Industry radar digest?

Is this primarily a **daily / weekly / recent AI industry roundup** (same sense as Path B radar in broader wiki routing)?

- **Yes** → **Radar path** (defer details; follow radar ingest rules elsewhere).
- **No** → continue to Q2.

### Q2 — Is the **primary subject** one or more **named products** (apps, MCP servers, platforms, or **foundation models** treated as headline picks)?

Use **tools-overview path** when the **center of gravity** is **concrete named product(s)** the reader could install, adopt, API against, or compare—**including a deep dive on a single product** or **a listicle mixing apps and model releases**. Conceptual background (e.g. PKM tradeoffs, local-first vs cloud) is allowed **as long as it mainly frames** those named artifact(s), not a freestanding methodology article.

**Answer Yes when (non-exhaustive):**

- **Listicle / roundup:** “**N** MCP servers…”, “**N** Mac apps…”, “**N** AI tools…”, numbered or bulleted **distinct named products** with blurbs and links (models and apps may appear together).
- **Single-product focus:** Title or structure centers **one app/platform/model line** (review, launch post, “Meet X”, feature tour, “why X exists”). Example: a long essay that introduces **Tolaria** and compares incumbents only to position that product still counts as **tools path** if the reader’s job-to-be-done is “should I use this product / what does it do?”

**Answer No when:**

- The **thesis or method is primary** (production AI concepts, RAG methodology, guardrail patterns, org process) and **named products are incidental examples or illustrations**.
- The piece is **pure landscape** without a product recommendation or evaluable artifact (route separately if you add a non-ingest policy).

**Tie-breaker:** If unsure after reading the HTML, ask: “Would a busy practitioner file this under **‘tooling notes’**?” If **yes**, use **tools-overview** even when only **one** coverage wikilink appears under `## Apps and platforms covered`, `## Foundation models covered`, or `## MCP servers covered`.

- **Yes** → **Tools-overview path**: `wiki/sources/` page per `wiki/AGENTS.md` contract **6)**; create or update pages under `wiki/tools/` and/or `wiki/foundation-models/` per **Stage 2** (`wiki/stage2-artifact-router.md`); **no** new or updated `wiki/questions/q-*.md` for this ingest. Tag sources with `tools`.
- **No** → **Non-radar deep ingest**: questions + source + glossary per existing contracts (standard source page **5)**).

## Output location rule

Classifier notes are process metadata. Keep them in working notes or `wiki/log.md` if needed.

**Do not include classifier verdict blocks in final `wiki/sources/*.md` pages.**

Stage 1 **does not** assign each list item to `wiki/tools/` vs `wiki/foundation-models/`—that is **Stage 2** after you know the article is tools-overview.
