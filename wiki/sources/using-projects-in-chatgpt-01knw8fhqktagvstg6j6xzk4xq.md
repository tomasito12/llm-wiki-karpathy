---
title: Using projects in ChatGPT
slug: using-projects-in-chatgpt-01knw8fhqktagvstg6j6xzk4xq
category: source
tags:
- context-engineering
- enterprise-ai
- enterprise-workflows
- human-ai-collaboration
- workflow-automation
- workflow-restructuring
source_id: using-projects-in-chatgpt-01knw8fhqktagvstg6j6xzk4xq
author: OpenAI Blog
publication: OpenAI
published_date: '2026-04-10'
assessed_as_of: '2026-04-10'
ingested_at: '2026-06-08T19:49:12.418645+00:00'
canonical_url: https://openai.com/academy/projects
content_sha256: 7dbffc8f29e2486fb7277bb67a90d1a6b477985fb2307eb2ae6cd328a1c3d769
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
derived_how_to:
- how-to/chatgpt-projects-setup.md
derived_topics:
- topics/agent-workspace-layering.md
- topics/project-scoped-memory-boundaries.md
derived_trends:
- industry-trends/chat-products-move-toward-persistent-workspaces.md
derived_pages:
- how-to/chatgpt-projects-setup.md
- industry-trends/chat-products-move-toward-persistent-workspaces.md
- topics/agent-workspace-layering.md
- topics/project-scoped-memory-boundaries.md
---

# Using projects in ChatGPT

This article explains a ChatGPT feature for organizing work. A project is like a container for chats, files, instructions, and context tied to one task or theme. The main benefit is that you do not have to repeat the same background every time you start a new chat. It is useful for work that lasts over time, such as research, writing, planning, or shared tasks. The article also describes a project-only memory option that keeps conversations inside that project boundary. In plain terms, it is about making ChatGPT easier to reuse for longer-running work.

## Key insights

- Projects are most useful when the same context must survive across multiple chats, rather than for one-off questions.
- The practical payoff is reduced repetition: fewer re-uploads of files, fewer repeated instructions, and less searching through past chats.
- Project-only memory creates a bounded workspace by preventing chats in that project from pulling context from outside it.
- Shared projects are designed around common files, instructions, and conversation history, which reduces duplicate copies of the same work.
- Enterprise admins get workspace-level control over shared projects, so access management is part of the feature, not an afterthought.

## Derived knowledge pages

- [[how-to/chatgpt-projects-setup]]
- [[industry-trends/chat-products-move-toward-persistent-workspaces]]
- [[topics/agent-workspace-layering]]
- [[topics/project-scoped-memory-boundaries]]

## Why it matters

The article matters because it frames ChatGPT projects as a lightweight state-management layer for work that cannot fit into a single conversation. For AI practitioners building with chat systems, the useful idea is not model behavior but context persistence: chats, files, and instructions are bundled so later turns can reuse the same working memory. That makes projects relevant for workflows where continuity is more important than raw generation quality, such as iterative drafting, research notebooks, or multi-step planning. The piece also clarifies a practical boundary: project-only memory can isolate one body of work from the rest of a user’s chat history, which may matter for organization, privacy, or avoiding accidental context bleed. Shared projects add a collaboration layer by letting multiple people see the same materials and history, reducing copy/version drift. The article is less about novel AI capability than about product ergonomics around context reuse. As of 2026-04-10, the feature looks operationally useful and easy to adopt for teams that repeatedly revisit the same materials, but the source gives no evidence on performance, reliability, or governance beyond basic admin controls.

## Limitations / open questions

The article is product guidance from the vendor, so it does not provide independent evaluation, usage data, or failure cases. It does not explain limits on file types, project size, retention, versioning, or how project context interacts with other ChatGPT memory features. Security and privacy questions are only lightly addressed through the project-only memory and Enterprise access-control mentions; there is no deeper policy detail. The practical impact of shared projects depends on plan availability, but the article does not specify the full plan matrix here. No benchmark or comparison is offered to show whether projects improve output quality versus just convenience.

## Contradictions / unverified claims

The piece presents projects as a clean answer to scattered context, but that claim is mostly intuitive rather than demonstrated with evidence. It assumes that keeping chats, files, and instructions together is enough to produce more consistent results, yet the article does not show measurable outcomes. The feature may also add another layer of workspace management that some users do not need for short, self-contained tasks. The value is plausible, but the source stays at the level of product rationale rather than proof.

## Source metadata

- Canonical URL: https://openai.com/academy/projects
- Raw markdown: `raw/readwise/using-projects-in-chatgpt-01knw8fhqktagvstg6j6xzk4xq.md`
- Raw HTML: `raw/readwise/using-projects-in-chatgpt-01knw8fhqktagvstg6j6xzk4xq.html`

## Full source text

---
readwise_id: 01knw8fhqktagvstg6j6xzk4xq
title: Using projects in ChatGPT
author: OpenAI Blog
source_url: https://openai.com/academy/projects
category: rss
location: archive
published_date: '2026-04-10'
saved_at: '2026-04-10T17:53:23.459000+00:00'
updated_at: '2026-05-08T11:40:01.075927+00:00'
tags:
- processed
publication: OpenAI
---

Projects in ChatGPT help you keep related chats, files, and instructions together in one place. They are useful for ongoing work or shared collaboration, so you don’t have to repeat context. Some plans let you share projects and control access for teamwork and better organization.
