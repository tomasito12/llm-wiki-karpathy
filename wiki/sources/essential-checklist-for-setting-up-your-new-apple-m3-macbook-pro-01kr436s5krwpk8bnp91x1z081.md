---
title: Essential Checklist for Setting up Your New Apple M3 MacBook Pro
slug: essential-checklist-for-setting-up-your-new-apple-m3-macbook-pro-01kr436s5krwpk8bnp91x1z081
category: source
source_id: essential-checklist-for-setting-up-your-new-apple-m3-macbook-pro-01kr436s5krwpk8bnp91x1z081
author: Wen Yang
publication: Medium
published_date: '2024-02-10'
assessed_as_of: '2024-02-10'
ingested_at: '2026-06-06T21:45:49+00:00'
canonical_url: https://medium.com/data-science/essential-checklist-for-setting-up-your-new-apple-m3-macbook-pro-306e94e974b4
content_sha256: aae66b032b472cc3a974cc53162bf2bee6be284462bab095235c3af138e51a15
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
---

# Essential Checklist for Setting up Your New Apple M3 MacBook Pro

This is a practical checklist for turning a new MacBook Pro into a usable developer machine. The author focuses on a few basics: move bookmarks, install a better terminal setup, get AWS tools working on Apple silicon, and bring over SSH keys safely. The interesting part is that it calls out a few real friction points, like AWS installers that can trigger unnecessary Rosetta steps and SSH keys that can break if copied through a text editor. It is useful because it shows a complete setup flow, not just isolated tips. The basic idea is to use simple, reproducible commands and keep the old workstation’s files intact when migrating.

## Key insights

- For Apple silicon Macs, installing AWS CLI with Homebrew is presented as the cleaner path than the official installer because it avoids an unnecessary Rosetta 2 prompt.
- Copying SSH private keys through a text editor can corrupt them with invisible characters; transferring the files themselves preserved validity in the author’s workflow.
- VS Code is used as the editing bridge for dotfiles, making terminal customization easier than editing shell config with vim or nano.
- Powerlevel10k setup is treated as a multi-step terminal personalization workflow, including font installation and explicit shell configuration in .zshrc.
- The article’s strongest value is as a migration checklist for a new dev laptop, not as a deep guide to any single tool.

## Derived knowledge pages

No derived knowledge pages captured.

## Why it matters

The piece is useful because it compresses a real workstation migration into a reproducible sequence: browser state, editor setup, shell customization, AWS tooling, and SSH continuity. For an advanced practitioner, the durable part is not the author’s exact visual preferences but the operational pattern of preparing a new macOS laptop so common workflows survive the move. The article also surfaces a few concrete friction points that are easy to overlook in a fresh Apple silicon setup, especially the need to use the right installation path for AWS CLI and the importance of transferring SSH keys as files rather than pasted text. That makes it a decent reference for anyone standardizing a new Mac for terminal-heavy development work. The stakes are limited, though: most of the content is a personal preference stack and routine command sequence rather than a novel technique or validated benchmark. As of 2024-02-10, it is actionable as a practical setup checklist, but it is better treated as a helpful anecdotal guide than as a durable best-practice standard. The article does not substantively discuss customer support, voice, or meeting workflows, so there is no broader automation takeaway to extend here.

## Limitations / open questions

The article is a single-user setup narrative, so it does not compare alternatives, measure reliability, or test whether the chosen stack is better than other common Mac developer setups. The AWS CLI and Session Manager steps are presented as working for the author, but there is no verification beyond personal success, and no discussion of security tradeoffs, versioning, or long-term maintenance. The SSH key transfer advice is practical, but it assumes the user already has safe access to the old machine and a trustworthy transfer channel. The terminal theme and editor choices are highly subjective and do not establish generalizable value. The guide also omits details about 1Password migration beyond an external link, so that part is incomplete.

## Contradictions / unverified claims

The main tension is between the article’s practical tone and the limited evidence behind some claims: it presents one successful setup as if it were a checklist for others, but most steps are preference-driven. The note that the official AWS CLI guide can trigger Rosetta on Apple M1-M3 machines is plausible within the author’s experience, but the article does not show the exact installer behavior or whether it depends on a specific version. The SSH-key warning is credible, yet the failure mode is anecdotal rather than systematically demonstrated. Overall, there is little hype, but the source should still be read as a worked example, not a canonical setup standard.

## Source metadata

- Canonical URL: https://medium.com/data-science/essential-checklist-for-setting-up-your-new-apple-m3-macbook-pro-306e94e974b4
- Raw markdown: `raw/readwise/essential-checklist-for-setting-up-your-new-apple-m3-macbook-pro-01kr436s5krwpk8bnp91x1z081.md`
- Raw HTML: `raw/readwise/essential-checklist-for-setting-up-your-new-apple-m3-macbook-pro-01kr436s5krwpk8bnp91x1z081.html`

## Full source text

---
readwise_id: 01kr436s5krwpk8bnp91x1z081
title: Essential Checklist for Setting up Your New Apple M3 MacBook Pro
author: Wen Yang
source_url: https://medium.com/data-science/essential-checklist-for-setting-up-your-new-apple-m3-macbook-pro-306e94e974b4
category: article
location: archive
published_date: '2024-02-10'
saved_at: '2026-05-08T15:27:26.387000+00:00'
updated_at: '2026-05-08T15:30:05.339694+00:00'
tags:
- processed
publication: Medium
---

The author shares steps to set up a new Apple M3 MacBook Pro for work, including migrating bookmarks, customizing the terminal, and installing AWS CLI. The guide covers installing tools like Homebrew, iTerm2, Oh My Zsh, and PowerLevel10K for a better developer experience. It also explains how to transfer SSH keys and configure AWS profiles for smooth project access.
