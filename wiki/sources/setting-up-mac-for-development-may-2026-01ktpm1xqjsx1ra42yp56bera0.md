---
title: Setting Up Mac for Development [May 2026]
slug: setting-up-mac-for-development-may-2026-01ktpm1xqjsx1ra42yp56bera0
category: source
tags:
- agent-systems
- agentic
- ai-assisted-development
- cli-tool
- coding
- coding-agents
- developer-tools
- orchestration
- software-engineering
- tool-use
- workflow-design
- workflow-restructuring
source_id: setting-up-mac-for-development-may-2026-01ktpm1xqjsx1ra42yp56bera0
author: Aman Kumar
publication: Medium
published_date: '2026-05-20'
assessed_as_of: '2026-05-20'
ingested_at: '2026-06-16T00:43:12+00:00'
canonical_url: https://medium.com/macoclock/setting-up-mac-for-development-may-2026-b6b456efd823
content_sha256: af2c802ed20d079f294942e9c09a19fa861e3d038bd8e0e5bc4ed620947532a6
derived_tools:
- tools/claude-code.md
derived_topics:
- topics/agent-workspace-layering.md
- topics/agentic-coding-workflows.md
derived_trends:
- industry-trends/coding-agents-diverge-into-workflow-specific-products.md
derived_pages:
- industry-trends/coding-agents-diverge-into-workflow-specific-products.md
- tools/claude-code.md
- topics/agent-workspace-layering.md
- topics/agentic-coding-workflows.md
---

# Setting Up Mac for Development [May 2026]

This piece is a personal checklist for setting up a Mac for software development in May 2026. The interesting part is the author’s shift toward terminal-based AI coding agents instead of staying inside a full IDE. Claude Code is the main recommendation, while Codex is used for larger delegated tasks and Antigravity is kept for inspecting agent output. The rest of the setup is a mix of standard developer tools, productivity apps, and shell shortcuts that make everyday work faster. It is useful mainly as a practical example of one experienced developer’s stack, not as a benchmark or universal best practice.

## Key insights

- The author treats terminal-native AI agents as the center of the 2026 development workflow, not a plugin inside a traditional editor.
- Claude Code is positioned as the default choice because it stays inside the project and works with MCP servers.
- Codex is framed for parallel, delegated work across multiple branches, which makes worktrees a core workflow primitive.
- Antigravity is used as a review surface for agent-generated code rather than as a primary editor.
- The non-AI stack still prioritizes low-friction basics: fast shells, simple aliases, and command-line tooling over heavyweight GUI workflows.

## Derived knowledge pages

- [[industry-trends/coding-agents-diverge-into-workflow-specific-products]]
- [[tools/claude-code]]
- [[topics/agent-workspace-layering]]
- [[topics/agentic-coding-workflows]]

## Why it matters

The article is useful because it shows what a practical Mac setup looks like when terminal-native agents are treated as first-class development tools. The author’s stack is not abstract advice; it is a concrete arrangement of package managers, shells, terminals, editors, and agent tools that are meant to minimize context switching. The most durable takeaway is the workflow shape: long-running delegated work goes to Codex, in-repo interactive work goes to Claude Code, and manual inspection happens in a separate IDE-like surface. That split is operationally meaningful because it suggests an emerging division between code production, code supervision, and lightweight editing, all anchored in the repository rather than a standalone chat window. The shell details matter too: worktrees, aliases, and faster version managers are presented as enabling infrastructure for parallel agent work, not as cosmetic customization. The CLI list also points to a pragmatic philosophy of installing only the tools you regularly deploy against or inspect from the terminal. The article’s significance is limited by its anecdotal evidence, but it is still a useful snapshot of one practitioner’s operating model. As of 2026-05-20, the recommendations are actionable as a personal workflow template, but they should be treated as a single-user setup rather than a validated standard.

## Limitations / open questions

This is entirely anecdotal and contains no benchmarks, comparative tests, or failure cases beyond the author’s preference changes. The article does not quantify whether terminal-native agents are safer, faster, or more reliable than GUI-based coding tools. Several recommendations depend on the author’s specific workflow, including multiple agents, worktrees, and MCP servers, but the setup cost and maintenance overhead are not discussed. Security and privacy tradeoffs are only hinted at via Tailscale, SSH keys, and local transcription, with no real threat model. The list of daily drivers and CLI tools is broad but shallow; most items are named without explanation of when alternatives might be better. The article also assumes comfort with shell customization and Git worktrees, which may not transfer cleanly to less experienced users.

## Contradictions / unverified claims

The piece implies that terminal-native agents have displaced IDE-first coding tools for the author, but it offers no evidence that this generalizes beyond one setup. Claims like fnm being about 10x faster shell startup, or Claude Code being the best single install for a fresh Mac, are presented as personal judgment rather than measured results. The setup also mixes durable tooling advice with taste-level choices, so readers should not overread the author’s preferences as universal best practice. The strongest skepticism point is that the article celebrates a complex multi-tool stack while simultaneously recommending simplicity; that tension is not resolved with evidence.

## Source metadata

- Canonical URL: https://medium.com/macoclock/setting-up-mac-for-development-may-2026-b6b456efd823
- Raw markdown: `raw/readwise/setting-up-mac-for-development-may-2026-01ktpm1xqjsx1ra42yp56bera0.md`
- Raw HTML: `raw/readwise/setting-up-mac-for-development-may-2026-01ktpm1xqjsx1ra42yp56bera0.html`
