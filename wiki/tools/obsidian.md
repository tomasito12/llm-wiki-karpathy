---
title: Obsidian
slug: obsidian
entity_id: tool:obsidian
category: tool
tags:
- document-analysis
- ide-integrated
- local-first
- workflow-automation
- writing
first_seen: '2026-01-16'
last_seen: '2026-05-03'
source_count: 7
evidence_count: 80
source_ids:
- how-i-built-an-ai-second-brain-using-claude-code-and-obsidian-01kr434kyy8fyj0wpm1gyx443z
- i-rebuilt-my-obsidian-workflow-with-5-new-plugins-2026-setup-01kqkvcae2nsb4s8s0g9y4tq0h
- i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee
- i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769
- obsidian-claude-code-is-your-24-7-ai-agent-here-is-how-to-build-yours-01kqkvgnyhw96eaf0eb9fj5gft
- obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk
- why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8
value_level: high
confidence: 0.9400000000000001
synthesis_state: stage1-placeholder
types:
- app
- knowledge-management
- note-taking
- ui
---

# Obsidian

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Obsidian is a local note-taking application built around Markdown files and other open formats. In this context it is the target environment that AI is being taught to work with correctly.

## Core Capabilities

- It stores notes in local, human-readable files so users can keep content outside a vendor-owned database.
- It exposes file-oriented formats such as Markdown, Bases, and Canvas that an AI system can target directly.
- It supports a workflow where generated artifacts remain editable in the same environment that stores the notes.
- It provides a markdown-centered interface for reviewing raw documents, generated summaries, and derived pages in the same workspace.
- It supports plugins that can render alternate outputs such as slide decks, which makes the knowledge base usable beyond text review.
- It stores notes in markdown files, which makes the underlying content portable and easy to reorganize.
- It supports plugin-driven customization, allowing the app to be adapted into a personal knowledge workspace.
- It works as the central environment where search, capture, formatting, and calendar-based note habits can be combined.
- It renders markdown with backlinks so cross-references are visible and clickable.
- It shows a graph view that reveals how pages connect into clusters.
- It lets the user search and browse the wiki without directly editing the generated files.
- It stores notes as local markdown files, which allows external tools to read and write them through file access.
- It supports backlinks, tags, and folder structure so notes can be organized as a connected knowledge system.
- It can expose current note context through an Obsidian-specific MCP bridge when paired with compatible tools.
- It stores notes as plain-text markdown files, which makes them durable and easy for automation to manipulate.
- It supports a vault structure that can be organized into inbox, projects, areas, resources, archives, daily notes, and people.
- It functions as a local knowledge base that can be directly updated by an AI tool with filesystem access.
- It provides a markdown vault that can store the AI-generated wiki as plain files.
- It supports graph view so relationships between pages are visible during review.
- It can be pre-configured with hotkeys and default layout settings to speed navigation.

## Integration Ecosystem

- It works with Claude Code-compatible clients through a /.claude skill directory.
- It uses open file formats that can be generated or edited by external tools.
- It can accept AI-generated .md, .base, and .canvas files that the application understands.
- The source explicitly mentions the Marp plugin as a way to render slides inside the workflow.
- It is used alongside a markdown-based wiki structure rather than as a standalone note app.
- The article highlights compatibility with plugins such as Make.md, Omnisearch, Linter, QuickAdd, and Calendar.
- Its markdown foundation makes it compatible with file-based workflows and other tools that can read plain text notes.
- It works with plain markdown files stored in a local folder, which keeps the knowledge base portable.
- It is used together with Claude Code and a CLAUDE.md schema to keep the agent's edits structured.
- It fits a git-based review loop because the files can be inspected as plain text diffs.
- It works with filesystem access because the vault is just a folder of markdown files.
- It can be exposed to Claude Code through an Obsidian MCP plugin.
- It supports tags and links that the agent can use as structural context.
- It works with Claude Code because the tool can directly read and write the vault files.
- It pairs with PARA-style folder organization, which gives automated routing a clear destination scheme.
- It can hold daily notes and contact notes that are then enriched by external data pulled through MCP-enabled commands.
- It works with a file-based vault structure, so source documents and generated pages can live in the same local project folder.
- It is paired here with Cursor as the AI editing environment, which lets one app generate changes while the other app visualizes the result.

## Maturity signals

The article presents Obsidian as already established enough to have official skills for its file formats, but it does not provide adoption numbers or enterprise evidence. The strongest maturity signal in the source is ecosystem openness rather than scale. It reads as a mature notes platform with a technically engaged user base, not as a mass-market AI platform.

## Related Tools

- Claude Code
- OpenCode
- Goose
- Make.md
- Omnisearch
- Linter
- QuickAdd
- Calendar
- Granola
- Cursor

## Strengths

- Uses local Markdown and other open formats, which keeps the note system portable and easier to integrate with external tools.
- Supports file-based workflows such as Bases and Canvas, giving AI a concrete schema to target instead of an opaque database.
- Fits a toolchain approach where AI is an assistant to the existing workflow rather than the center of the product.

## Weaknesses / limitations

The article does not discuss performance, collaboration limits, or how well the app handles large-scale AI-assisted edits. Its value here also depends on whether the surrounding AI client can reliably follow the file conventions; Obsidian alone does not solve that. The source does not provide evidence that this approach is easier for non-technical users.

## Evidence / supporting sources

### How I Built an AI Second Brain Using Claude Code and Obsidian (2026-05-03)

- It works with Claude Code because the tool can directly read and write the vault files. (`66e54079d5ef` · neutral · integration_ecosystem[0]; [[sources/how-i-built-an-ai-second-brain-using-claude-code-and-obsidian-01kr434kyy8fyj0wpm1gyx443z|How I Built an AI Second Brain Using Claude Code and Obsidian]])
- It pairs with PARA-style folder organization, which gives automated routing a clear destination scheme. (`bf612546788b` · neutral · integration_ecosystem[1]; [[sources/how-i-built-an-ai-second-brain-using-claude-code-and-obsidian-01kr434kyy8fyj0wpm1gyx443z|How I Built an AI Second Brain Using Claude Code and Obsidian]])
- It can hold daily notes and contact notes that are then enriched by external data pulled through MCP-enabled commands. (`9b3a6ca65040` · neutral · integration_ecosystem[2]; [[sources/how-i-built-an-ai-second-brain-using-claude-code-and-obsidian-01kr434kyy8fyj0wpm1gyx443z|How I Built an AI Second Brain Using Claude Code and Obsidian]])
- The article treats Obsidian as established enough to be the base layer of a practical workflow. The source emphasizes its local-first file model rather than any experimental feature, which suggests a mature and stable role in personal knowledge systems. (`58431e7621f0` · neutral · maturity_signals; [[sources/how-i-built-an-ai-second-brain-using-claude-code-and-obsidian-01kr434kyy8fyj0wpm1gyx443z|How I Built an AI Second Brain Using Claude Code and Obsidian]])
- Obsidian matters in AI workflows because it gives an agent a stable, machine-readable file system to operate on. That makes it a good fit for knowledge bases, daily notes, and other artifact-driven systems where local control and portability matter. In service automation terms, it is less a chat surface and more the durable state layer behind an agent workflow. (`4b9970a4b72f` · neutral · operational_relevance; [[sources/how-i-built-an-ai-second-brain-using-claude-code-and-obsidian-01kr434kyy8fyj0wpm1gyx443z|How I Built an AI Second Brain Using Claude Code and Obsidian]])
- A free, local-first markdown editor used here as the storage layer for a personal AI knowledge system. Notes are plain text files on disk that an AI can read and write directly. (`00077170e535` · neutral · short_description; [[sources/how-i-built-an-ai-second-brain-using-claude-code-and-obsidian-01kr434kyy8fyj0wpm1gyx443z|How I Built an AI Second Brain Using Claude Code and Obsidian]])
- - Stores notes as local markdown files, which makes them easy for tools to read, write, search, and back up.
- Supports a folder-based structure that maps well to automation and routing logic.
- Works well as an artifact store for AI-generated daily notes, reference material, and contact notes. (`335fe78494a4` · neutral · strengths; [[sources/how-i-built-an-ai-second-brain-using-claude-code-and-obsidian-01kr434kyy8fyj0wpm1gyx443z|How I Built an AI Second Brain Using Claude Code and Obsidian]])
- It stores notes as plain-text markdown files, which makes them durable and easy for automation to manipulate. (`63e639fba053` · supporting · core_capabilities[0]; [[sources/how-i-built-an-ai-second-brain-using-claude-code-and-obsidian-01kr434kyy8fyj0wpm1gyx443z|How I Built an AI Second Brain Using Claude Code and Obsidian]])
- It supports a vault structure that can be organized into inbox, projects, areas, resources, archives, daily notes, and people. (`12e011979d4f` · supporting · core_capabilities[1]; [[sources/how-i-built-an-ai-second-brain-using-claude-code-and-obsidian-01kr434kyy8fyj0wpm1gyx443z|How I Built an AI Second Brain Using Claude Code and Obsidian]])
- It functions as a local knowledge base that can be directly updated by an AI tool with filesystem access. (`6d881843eff4` · supporting · core_capabilities[2]; [[sources/how-i-built-an-ai-second-brain-using-claude-code-and-obsidian-01kr434kyy8fyj0wpm1gyx443z|How I Built an AI Second Brain Using Claude Code and Obsidian]])
- "Obsidian is a free, local-first markdown editor. If you’ve never used it: imagine a note-taking app where every note is just a plain text file (.md) stored on your computer." (`97bb385dc19c` · supporting · supporting_snippet; [[sources/how-i-built-an-ai-second-brain-using-claude-code-and-obsidian-01kr434kyy8fyj0wpm1gyx443z|How I Built an AI Second Brain Using Claude Code and Obsidian]])
- The source does not discuss deep plugin behavior, sync strategy, or collaborative limits. It is strong as a local knowledge store, but the workflow still depends on external orchestration to become useful. (`9db34535ee3a` · uncertainty · weaknesses_limitations; [[sources/how-i-built-an-ai-second-brain-using-claude-code-and-obsidian-01kr434kyy8fyj0wpm1gyx443z|How I Built an AI Second Brain Using Claude Code and Obsidian]])

### I Rebuilt My Obsidian Workflow With 5 New Plugins (2026 Setup) (2026-04-18)

- The article highlights compatibility with plugins such as Make.md, Omnisearch, Linter, QuickAdd, and Calendar. (`f55728a716e7` · neutral · integration_ecosystem[0]; [[sources/i-rebuilt-my-obsidian-workflow-with-5-new-plugins-2026-setup-01kqkvcae2nsb4s8s0g9y4tq0h|I Rebuilt My Obsidian Workflow With 5 New Plugins (2026 Setup)]])
- Its markdown foundation makes it compatible with file-based workflows and other tools that can read plain text notes. (`4582cccd93c0` · neutral · integration_ecosystem[1]; [[sources/i-rebuilt-my-obsidian-workflow-with-5-new-plugins-2026-setup-01kqkvcae2nsb4s8s0g9y4tq0h|I Rebuilt My Obsidian Workflow With 5 New Plugins (2026 Setup)]])
- The piece treats Obsidian as established enough to build a long-lived personal workflow on top of it. At the same time, the need for five plugins suggests the core app alone may not cover advanced workflow needs for this user. The article does not provide adoption data or enterprise evidence. (`a617030bc8e4` · neutral · maturity_signals; [[sources/i-rebuilt-my-obsidian-workflow-with-5-new-plugins-2026-setup-01kqkvcae2nsb4s8s0g9y4tq0h|I Rebuilt My Obsidian Workflow With 5 New Plugins (2026 Setup)]])
- Obsidian matters as the container for the workflow, but the article is mostly about how plugins change that container into a more usable operating system for notes. For practitioners, the useful point is that the app can support structure, capture, retrieval, and daily logging when extended with the right plugins. It is relevant to knowledge-heavy work where reusable notes matter more than simple storage. (`0e8e4def7731` · neutral · operational_relevance; [[sources/i-rebuilt-my-obsidian-workflow-with-5-new-plugins-2026-setup-01kqkvcae2nsb4s8s0g9y4tq0h|I Rebuilt My Obsidian Workflow With 5 New Plugins (2026 Setup)]])
- A local markdown-based note-taking app used here as the base workspace for building a personal knowledge system. (`ec045e425ce2` · neutral · short_description; [[sources/i-rebuilt-my-obsidian-workflow-with-5-new-plugins-2026-setup-01kqkvcae2nsb4s8s0g9y4tq0h|I Rebuilt My Obsidian Workflow With 5 New Plugins (2026 Setup)]])
- - Local markdown storage makes notes durable and easy to reuse across workflows that depend on plain files.
- The plugin ecosystem lets users reshape the app around capture, search, cleanup, and daily review instead of treating it as a static editor.
- It can support a workspace-style knowledge system rather than just a folder of files when paired with organizing plugins. (`9a1ba31fd2dc` · neutral · strengths; [[sources/i-rebuilt-my-obsidian-workflow-with-5-new-plugins-2026-setup-01kqkvcae2nsb4s8s0g9y4tq0h|I Rebuilt My Obsidian Workflow With 5 New Plugins (2026 Setup)]])
- It stores notes in markdown files, which makes the underlying content portable and easy to reorganize. (`bf7b2d2f05f0` · supporting · core_capabilities[0]; [[sources/i-rebuilt-my-obsidian-workflow-with-5-new-plugins-2026-setup-01kqkvcae2nsb4s8s0g9y4tq0h|I Rebuilt My Obsidian Workflow With 5 New Plugins (2026 Setup)]])
- It supports plugin-driven customization, allowing the app to be adapted into a personal knowledge workspace. (`f3f3c9126e4e` · supporting · core_capabilities[1]; [[sources/i-rebuilt-my-obsidian-workflow-with-5-new-plugins-2026-setup-01kqkvcae2nsb4s8s0g9y4tq0h|I Rebuilt My Obsidian Workflow With 5 New Plugins (2026 Setup)]])
- It works as the central environment where search, capture, formatting, and calendar-based note habits can be combined. (`e6180325377c` · supporting · core_capabilities[2]; [[sources/i-rebuilt-my-obsidian-workflow-with-5-new-plugins-2026-setup-01kqkvcae2nsb4s8s0g9y4tq0h|I Rebuilt My Obsidian Workflow With 5 New Plugins (2026 Setup)]])
- "my old Obsidian vault looked like a crime scene. Notes everywhere, tags that made sense only at 2am, and a search function that somehow always found everything except what I needed" (`f5499f8834f1` · supporting · supporting_snippet; [[sources/i-rebuilt-my-obsidian-workflow-with-5-new-plugins-2026-setup-01kqkvcae2nsb4s8s0g9y4tq0h|I Rebuilt My Obsidian Workflow With 5 New Plugins (2026 Setup)]])
- The article implicitly shows that the base app can feel fragmented without additional structure, search help, and capture automation. A practical downside of this model is plugin dependency: the workflow can become harder to maintain if too many add-ons are required to keep it coherent. (`461432c8e395` · uncertainty · weaknesses_limitations; [[sources/i-rebuilt-my-obsidian-workflow-with-5-new-plugins-2026-setup-01kqkvcae2nsb4s8s0g9y4tq0h|I Rebuilt My Obsidian Workflow With 5 New Plugins (2026 Setup)]])

### I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI (2026-04-07)

- It works with a file-based vault structure, so source documents and generated pages can live in the same local project folder. (`ee1890c786cd` · neutral · integration_ecosystem[0]; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]])
- It is paired here with Cursor as the AI editing environment, which lets one app generate changes while the other app visualizes the result. (`fd5fd6def05a` · neutral · integration_ecosystem[1]; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]])
- The source treats Obsidian as a ready-to-use, pre-configured vault rather than an experimental dependency, which suggests mature enough tooling for personal and small-team workflows. The article does not claim enterprise adoption or quantify reliability, so maturity beyond that use case is not established here. (`8a188a1e0f68` · neutral · maturity_signals; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]])
- Obsidian is relevant when the knowledge system is stored as markdown files and needs a human-friendly way to inspect relationships, navigate pages, and review generated content. In this setup, it acts as the read/write surface for the wiki while the AI manages page generation and updates. That makes it useful for document-heavy workflows where a practitioner wants a visible artifact instead of chat-only answers. (`cc2d3673be4e` · neutral · operational_relevance; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]])
- A note-taking app used here as the front end for browsing and editing the wiki vault. It provides graph view, hotkeys, and a file-based workspace that fits a markdown knowledge base. (`49af5995467c` · neutral · short_description; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]])
- - File-native editing makes it easy to inspect and version-control the wiki alongside source files rather than trapping knowledge in a proprietary database.
- Graph view helps spot hubs, isolated pages, and missing links, which is useful when an AI is maintaining cross-references over time.
- Hotkeys and side-by-side browsing support a fast review loop between the AI editor and the knowledge base. (`e1823aebde5e` · neutral · strengths; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]])
- It provides a markdown vault that can store the AI-generated wiki as plain files. (`9f743f073308` · supporting · core_capabilities[0]; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]])
- It supports graph view so relationships between pages are visible during review. (`2cfbcc052758` · supporting · core_capabilities[1]; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]])
- It can be pre-configured with hotkeys and default layout settings to speed navigation. (`ce756f68c00a` · supporting · core_capabilities[2]; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]])
- “Cursor installed Obsidian via Homebrew and pre-configured the vault: New files land in wiki/ by default Graph view color-coded by page type Keyboard shortcuts for graph view, search, and quick switching Overview page opens on launch” (`29a975b24a19` · supporting · supporting_snippet; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]])
- The article does not provide evidence that Obsidian itself improves retrieval quality or scales beyond the author’s workflow. Its usefulness depends on disciplined schema design and AI maintenance; without those, it is just a note-taking app with a graph view. (`d30fe27ed6b1` · uncertainty · weaknesses_limitations; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]])

### I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me. (2026-04-19)

- It works with plain markdown files stored in a local folder, which keeps the knowledge base portable. (`2c9c279e6ca4` · neutral · integration_ecosystem[0]; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- It is used together with Claude Code and a CLAUDE.md schema to keep the agent's edits structured. (`8b6da9ad15ad` · neutral · integration_ecosystem[1]; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- It fits a git-based review loop because the files can be inspected as plain text diffs. (`9c042f40c4b1` · neutral · integration_ecosystem[2]; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- Obsidian is presented as a mature enough note-taking environment to function as the front end for an LLM-maintained wiki. The article does not discuss enterprise controls or collaborative governance, so the usage here is personal and local rather than enterprise-oriented. (`496aba7566a2` · neutral · maturity_signals; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- Obsidian is positioned as the viewing layer, not the intelligence layer. That matters because it shows a practical division of labor: the model writes and maintains the corpus, while the human inspects links, graphs, and search results in a file-based app. For knowledge-heavy teams, that makes Obsidian useful as a transparent front end for AI-maintained documentation and research notes. (`93d53d83780b` · neutral · operational_relevance; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- A note-taking app that renders markdown files, backlinks, graphs, and searches over a local folder of notes. Here it serves as the interface for reading and navigating the generated wiki. (`806e8e1015ff` · neutral · short_description; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- - It renders backlinks and graph connections, which helps users inspect how ideas cluster and bridge across a growing corpus.
- It updates in real time as markdown files change on disk, so the human can browse AI-generated pages without leaving the local file workflow.
- It supports search across all pages, which makes a compiled wiki easier to navigate than a pile of raw documents. (`77a598390098` · neutral · strengths; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- It renders markdown with backlinks so cross-references are visible and clickable. (`8b953e4d53f8` · supporting · core_capabilities[0]; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- It shows a graph view that reveals how pages connect into clusters. (`47555aff4268` · supporting · core_capabilities[1]; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- It lets the user search and browse the wiki without directly editing the generated files. (`de6c94633624` · supporting · core_capabilities[2]; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- "Obsidian is the window." (`e62b6960d5f4` · supporting · supporting_snippet; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- The article makes clear that Obsidian is only the window, not the brain, so it does not solve knowledge maintenance by itself. The value depends on the underlying agent and schema quality; without those, it would just be a note viewer with a graph. (`68464bdaccd0` · uncertainty · weaknesses_limitations; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])

### Obsidian + Claude Code is your 24×7 AI Agent: Here is how to build yours (2026-04-23)

- It works with filesystem access because the vault is just a folder of markdown files. (`405e6d2220a8` · neutral · integration_ecosystem[0]; [[sources/obsidian-claude-code-is-your-24-7-ai-agent-here-is-how-to-build-yours-01kqkvgnyhw96eaf0eb9fj5gft|Obsidian + Claude Code is your 24×7 AI Agent: Here is how to build yours]])
- It can be exposed to Claude Code through an Obsidian MCP plugin. (`cf01d6dc160f` · neutral · integration_ecosystem[1]; [[sources/obsidian-claude-code-is-your-24-7-ai-agent-here-is-how-to-build-yours-01kqkvgnyhw96eaf0eb9fj5gft|Obsidian + Claude Code is your 24×7 AI Agent: Here is how to build yours]])
- It supports tags and links that the agent can use as structural context. (`cb85d32c28fd` · neutral · integration_ecosystem[2]; [[sources/obsidian-claude-code-is-your-24-7-ai-agent-here-is-how-to-build-yours-01kqkvgnyhw96eaf0eb9fj5gft|Obsidian + Claude Code is your 24×7 AI Agent: Here is how to build yours]])
- The source treats Obsidian as a mature enough local notes app to serve as the base layer for automation. The fact that a bridge plugin exists for Claude Code suggests a small but practical ecosystem around agent access to vaults. The evidence remains narrow because the article is a personal setup guide rather than an independent review. (`c97b4c75908e` · neutral · maturity_signals; [[sources/obsidian-claude-code-is-your-24-7-ai-agent-here-is-how-to-build-yours-01kqkvgnyhw96eaf0eb9fj5gft|Obsidian + Claude Code is your 24×7 AI Agent: Here is how to build yours]])
- Obsidian is useful here because its notes are ordinary files, which makes them accessible to tools that can operate on the filesystem. That design supports agent-assisted retrieval, note creation, and folder-based organization without needing a separate database. For practitioners, the important operational pattern is that a well-structured vault can become a reusable context store for planning, drafting, and review tasks. The article frames this as more than storage: it becomes the system the agent works inside. (`1852f0fb9915` · neutral · operational_relevance; [[sources/obsidian-claude-code-is-your-24-7-ai-agent-here-is-how-to-build-yours-01kqkvgnyhw96eaf0eb9fj5gft|Obsidian + Claude Code is your 24×7 AI Agent: Here is how to build yours]])
- A local-first note-taking app that stores notes as markdown files in a folder called a vault. In this workflow, it serves as the user's structured knowledge base that Claude Code can read and write. (`8bf41fee72b5` · neutral · short_description; [[sources/obsidian-claude-code-is-your-24-7-ai-agent-here-is-how-to-build-yours-01kqkvgnyhw96eaf0eb9fj5gft|Obsidian + Claude Code is your 24×7 AI Agent: Here is how to build yours]])
- - Notes are stored as markdown files in a folder, which makes the vault portable and easier for tools to inspect and edit.
- Backlinks, tags, and folders support connected knowledge rather than isolated notes, which helps an agent trace ideas across time.
- A simple folder structure makes it easier to automate reviews and content extraction because the agent can find where different note types live. (`6d5537a8b751` · neutral · strengths; [[sources/obsidian-claude-code-is-your-24-7-ai-agent-here-is-how-to-build-yours-01kqkvgnyhw96eaf0eb9fj5gft|Obsidian + Claude Code is your 24×7 AI Agent: Here is how to build yours]])
- It stores notes as local markdown files, which allows external tools to read and write them through file access. (`7bd89b8ea9dd` · supporting · core_capabilities[0]; [[sources/obsidian-claude-code-is-your-24-7-ai-agent-here-is-how-to-build-yours-01kqkvgnyhw96eaf0eb9fj5gft|Obsidian + Claude Code is your 24×7 AI Agent: Here is how to build yours]])
- It supports backlinks, tags, and folder structure so notes can be organized as a connected knowledge system. (`34cf3d97db45` · supporting · core_capabilities[1]; [[sources/obsidian-claude-code-is-your-24-7-ai-agent-here-is-how-to-build-yours-01kqkvgnyhw96eaf0eb9fj5gft|Obsidian + Claude Code is your 24×7 AI Agent: Here is how to build yours]])
- It can expose current note context through an Obsidian-specific MCP bridge when paired with compatible tools. (`21b4a77815fc` · supporting · core_capabilities[2]; [[sources/obsidian-claude-code-is-your-24-7-ai-agent-here-is-how-to-build-yours-01kqkvgnyhw96eaf0eb9fj5gft|Obsidian + Claude Code is your 24×7 AI Agent: Here is how to build yours]])
- "Obsidian is just markdown files in a folder." (`23b66ef8a046` · supporting · supporting_snippet; [[sources/obsidian-claude-code-is-your-24-7-ai-agent-here-is-how-to-build-yours-01kqkvgnyhw96eaf0eb9fj5gft|Obsidian + Claude Code is your 24×7 AI Agent: Here is how to build yours]])
- The article does not address synchronization, collaboration, or governance concerns. It also assumes that the user maintains a disciplined vault structure; without that discipline, the agent has little to work with. The tool is presented as powerful for personal organization, but the source offers no evidence about team-scale reliability. (`9bb4014ab8e3` · uncertainty · weaknesses_limitations; [[sources/obsidian-claude-code-is-your-24-7-ai-agent-here-is-how-to-build-yours-01kqkvgnyhw96eaf0eb9fj5gft|Obsidian + Claude Code is your 24×7 AI Agent: Here is how to build yours]])

### Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault. (2026-01-16)

- It works with Claude Code-compatible clients through a /.claude skill directory. (`b1225bd2b906` · neutral · integration_ecosystem[0]; [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]])
- It uses open file formats that can be generated or edited by external tools. (`84a821e03d4d` · neutral · integration_ecosystem[1]; [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]])
- It can accept AI-generated .md, .base, and .canvas files that the application understands. (`01d338a34657` · neutral · integration_ecosystem[2]; [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]])
- The article presents Obsidian as already established enough to have official skills for its file formats, but it does not provide adoption numbers or enterprise evidence. The strongest maturity signal in the source is ecosystem openness rather than scale. It reads as a mature notes platform with a technically engaged user base, not as a mass-market AI platform. (`a7407fa63f2b` · neutral · maturity_signals; [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]])
- Obsidian matters here because its file formats are the boundary AI must respect. The article treats the app as a local knowledge workspace where generated output should remain readable, portable, and editable outside the AI system. That makes it relevant for practitioners who want AI assistance without surrendering file ownership or moving notes into a proprietary database. It is most interesting as a host environment for AI workflows, not as an AI product itself. (`640e965eba4c` · neutral · operational_relevance; [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]])
- Obsidian is a local note-taking application built around Markdown files and other open formats. In this context it is the target environment that AI is being taught to work with correctly. (`f74250f94a16` · neutral · short_description; [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]])
- - Uses local Markdown and other open formats, which keeps the note system portable and easier to integrate with external tools.
- Supports file-based workflows such as Bases and Canvas, giving AI a concrete schema to target instead of an opaque database.
- Fits a toolchain approach where AI is an assistant to the existing workflow rather than the center of the product. (`ef00c4c9a872` · neutral · strengths; [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]])
- It stores notes in local, human-readable files so users can keep content outside a vendor-owned database. (`e529ac120bc1` · supporting · core_capabilities[0]; [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]])
- It exposes file-oriented formats such as Markdown, Bases, and Canvas that an AI system can target directly. (`281dbcd95dac` · supporting · core_capabilities[1]; [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]])
- It supports a workflow where generated artifacts remain editable in the same environment that stores the notes. (`dd6018a71369` · supporting · core_capabilities[2]; [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]])
- "Obsidian has always walked this talk: starting with local Markdown and open formats so it could slot cleanly into a toolchain rather than own every step." (`b7821f11e9b5` · supporting · supporting_snippet; [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]])
- The article does not discuss performance, collaboration limits, or how well the app handles large-scale AI-assisted edits. Its value here also depends on whether the surrounding AI client can reliably follow the file conventions; Obsidian alone does not solve that. The source does not provide evidence that this approach is easier for non-technical users. (`dd37b6343fcb` · uncertainty · weaknesses_limitations; [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]])

### Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge (2026-04-06)

- The source explicitly mentions the Marp plugin as a way to render slides inside the workflow. (`2a6a798950cd` · neutral · integration_ecosystem[0]; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])
- It is used alongside a markdown-based wiki structure rather than as a standalone note app. (`12eefd225361` · neutral · integration_ecosystem[1]; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])
- Obsidian is treated as an established part of the workflow rather than an experimental add-on. The source assumes it can serve as the main IDE-like frontend for local knowledge work, which suggests enough maturity for everyday use. No broader market claims are made here. (`d0601c9521ac` · neutral · maturity_signals; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])
- The source describes Obsidian as the place where the user inspects raw data, the compiled wiki, and generated outputs. That makes it relevant as a practical interface layer for knowledge workflows where the model writes and maintains files while the human reviews the artifact. It fits especially well when the system is file-native and the user wants a markdown-centered review loop. (`a61db9dc0fc2` · neutral · operational_relevance; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])
- A local markdown workspace used here as the front end for viewing raw sources, compiled wiki pages, and derived visualizations. (`bdcaf4e50c75` · neutral · short_description; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])
- - Works as the visible workspace for raw sources, compiled markdown pages, and visual outputs, so the user can inspect the full knowledge pipeline in one place.
- Fits a file-native workflow because the wiki is stored as markdown files and the LLM maintains them directly.
- Supports plugin-based extensions, which the source uses for alternate views such as slides via Marp. (`b6bf778bd6df` · neutral · strengths; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])
- It provides a markdown-centered interface for reviewing raw documents, generated summaries, and derived pages in the same workspace. (`937b91c97dd8` · supporting · core_capabilities[0]; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])
- It supports plugins that can render alternate outputs such as slide decks, which makes the knowledge base usable beyond text review. (`c80de2864897` · supporting · core_capabilities[1]; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])
- IDE:
I use Obsidian as the IDE "frontend" where I can view the raw data, the the compiled wiki, and the derived visualizations. Important to note that the LLM writes and maintains all of the data of the wiki, I rarely touch it directly. I've played with a few Obsidian plugins to render and view data in other ways (e.g. Marp for slides). (`fd18f9328663` · supporting · supporting_snippet; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])
- The source does not present a deep product review of Obsidian itself, and it does not discuss collaboration, sync reliability, or enterprise controls. Its role here is mainly as a local interface, so the evidence is strong for workflow fit but thin for product-level evaluation. (`816b9fbb8caa` · uncertainty · weaknesses_limitations; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])

## Contradictions / tensions

- The article does not discuss performance, collaboration limits, or how well the app handles large-scale AI-assisted edits. Its value here also depends on whether the surrounding AI client can reliably follow the file conventions; Obsidian alone does not solve that. The source does not provide evidence that this approach is easier for non-technical users. (uncertainty; [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]])
- The source does not present a deep product review of Obsidian itself, and it does not discuss collaboration, sync reliability, or enterprise controls. Its role here is mainly as a local interface, so the evidence is strong for workflow fit but thin for product-level evaluation. (uncertainty; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])
- The article does not provide evidence that Obsidian itself improves retrieval quality or scales beyond the author’s workflow. Its usefulness depends on disciplined schema design and AI maintenance; without those, it is just a note-taking app with a graph view. (uncertainty; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]])
- The article implicitly shows that the base app can feel fragmented without additional structure, search help, and capture automation. A practical downside of this model is plugin dependency: the workflow can become harder to maintain if too many add-ons are required to keep it coherent. (uncertainty; [[sources/i-rebuilt-my-obsidian-workflow-with-5-new-plugins-2026-setup-01kqkvcae2nsb4s8s0g9y4tq0h|I Rebuilt My Obsidian Workflow With 5 New Plugins (2026 Setup)]])
- The article makes clear that Obsidian is only the window, not the brain, so it does not solve knowledge maintenance by itself. The value depends on the underlying agent and schema quality; without those, it would just be a note viewer with a graph. (uncertainty; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- The article does not address synchronization, collaboration, or governance concerns. It also assumes that the user maintains a disciplined vault structure; without that discipline, the agent has little to work with. The tool is presented as powerful for personal organization, but the source offers no evidence about team-scale reliability. (uncertainty; [[sources/obsidian-claude-code-is-your-24-7-ai-agent-here-is-how-to-build-yours-01kqkvgnyhw96eaf0eb9fj5gft|Obsidian + Claude Code is your 24×7 AI Agent: Here is how to build yours]])
- The source does not discuss deep plugin behavior, sync strategy, or collaborative limits. It is strong as a local knowledge store, but the workflow still depends on external orchestration to become useful. (uncertainty; [[sources/how-i-built-an-ai-second-brain-using-claude-code-and-obsidian-01kr434kyy8fyj0wpm1gyx443z|How I Built an AI Second Brain Using Claude Code and Obsidian]])

## Related pages

- Calendar
- Claude Code
- Cursor
- Goose
- Granola
- Linter
- Make.md
- Omnisearch
- OpenCode
- QuickAdd

## Sources

- [[sources/how-i-built-an-ai-second-brain-using-claude-code-and-obsidian-01kr434kyy8fyj0wpm1gyx443z|How I Built an AI Second Brain Using Claude Code and Obsidian]]
- [[sources/i-rebuilt-my-obsidian-workflow-with-5-new-plugins-2026-setup-01kqkvcae2nsb4s8s0g9y4tq0h|I Rebuilt My Obsidian Workflow With 5 New Plugins (2026 Setup)]]
- [[sources/i-used-karpathy-s-llm-wiki-to-build-a-knowledge-base-that-maintains-itself-with-ai-01kr439at95y3c5a5s41jwz1ee|I used Karpathy’s LLM Wiki to build a knowledge base that maintains itself with AI]]
- [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]]
- [[sources/obsidian-claude-code-is-your-24-7-ai-agent-here-is-how-to-build-yours-01kqkvgnyhw96eaf0eb9fj5gft|Obsidian + Claude Code is your 24×7 AI Agent: Here is how to build yours]]
- [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]]
- [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]]
