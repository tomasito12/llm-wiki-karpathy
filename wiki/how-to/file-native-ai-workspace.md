---
title: File-Native AI Workspace
slug: file-native-ai-workspace
entity_id: how_to:file-native-ai-workspace
category: how-to
tags:
- ai-engineering
- knowledge-systems
- workflow-design
first_seen: '2026-06-05'
last_seen: '2026-06-05'
source_count: 1
evidence_count: 14
source_ids:
- how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c
value_level: high
confidence: 0.98
synthesis_state: stage1-placeholder
---

# File-Native AI Workspace

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
This is about setting up an AI workflow that works directly on your own files instead of living only inside chat. It solves the problem of context loss, vendor lock-in, and repeated re-uploading of documents. The goal is to keep your notes portable while letting an AI tool act on them safely. It also helps when the note base is large enough that manual context sharing becomes unreliable.

## Caveats

This setup depends on disciplined folder structure and maintenance. If the vault grows large without a map, the model can miss relevant context or behave as if it has read more than it actually has. It also still depends on a vendor tool for execution, so portability is partial rather than absolute.

## Implementation Steps

- Store notes as markdown files in a local folder you control.
- Create a separate AIOS folder for AI-specific files and outputs.
- Add a portable identity file that tells the model how to work with you.
- Create a vault map that explains how the AI should navigate the notes.
- Create a skill map that defines available skills and when to use them.
- Point the AI tool at the correct folder.
- Start each new session with a short prompt that tells the model to read the identity file, then the vault map and skill map.

## Prerequisites

- A local note vault with markdown files.
- An AI tool that can read a selected folder.
- A willingness to maintain map files and session prompts.

## Evidence / supporting sources

### How I Use Obsidian + Claude Cowork to Run My Life (2026-06-05)

- Keep your knowledge in plain markdown files inside folders you control. Add a small translation layer with a portable identity file, a vault map, and a skill map so the AI knows who you are, where to go, and what it can do. Point the AI tool at the right folder, then start each session with a short prompt that tells it which files to read first. Keep AI-generated material in a separate folder so your personal notes stay clean. If the note base is large, use the map files instead of expecting the model to scan everything. (`09d6e13a1713` · neutral · answer_summary; [[sources/how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c|How I Use Obsidian + Claude Cowork to Run My Life]])
- Store notes as markdown files in a local folder you control. (`e90a9fb72355` · neutral · implementation_steps[0]; [[sources/how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c|How I Use Obsidian + Claude Cowork to Run My Life]])
- Create a separate AIOS folder for AI-specific files and outputs. (`0a1c25039ae7` · neutral · implementation_steps[1]; [[sources/how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c|How I Use Obsidian + Claude Cowork to Run My Life]])
- Add a portable identity file that tells the model how to work with you. (`b96333a3a293` · neutral · implementation_steps[2]; [[sources/how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c|How I Use Obsidian + Claude Cowork to Run My Life]])
- Create a vault map that explains how the AI should navigate the notes. (`3a64a584b50c` · neutral · implementation_steps[3]; [[sources/how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c|How I Use Obsidian + Claude Cowork to Run My Life]])
- Create a skill map that defines available skills and when to use them. (`e0c027903b39` · neutral · implementation_steps[4]; [[sources/how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c|How I Use Obsidian + Claude Cowork to Run My Life]])
- Point the AI tool at the correct folder. (`79586c8f17d7` · neutral · implementation_steps[5]; [[sources/how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c|How I Use Obsidian + Claude Cowork to Run My Life]])
- Start each new session with a short prompt that tells the model to read the identity file, then the vault map and skill map. (`bf70304146da` · neutral · implementation_steps[6]; [[sources/how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c|How I Use Obsidian + Claude Cowork to Run My Life]])
- A local note vault with markdown files. (`5dcb9fe0e60b` · neutral · prerequisites[0]; [[sources/how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c|How I Use Obsidian + Claude Cowork to Run My Life]])
- An AI tool that can read a selected folder. (`2d3cea9e3cd9` · neutral · prerequisites[1]; [[sources/how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c|How I Use Obsidian + Claude Cowork to Run My Life]])
- A willingness to maintain map files and session prompts. (`08dbd0244909` · neutral · prerequisites[2]; [[sources/how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c|How I Use Obsidian + Claude Cowork to Run My Life]])
- This is about setting up an AI workflow that works directly on your own files instead of living only inside chat. It solves the problem of context loss, vendor lock-in, and repeated re-uploading of documents. The goal is to keep your notes portable while letting an AI tool act on them safely. It also helps when the note base is large enough that manual context sharing becomes unreliable. (`a4ee0a0b698b` · neutral · what_and_problem; [[sources/how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c|How I Use Obsidian + Claude Cowork to Run My Life]])
- "The middle layer of the AI operating system. And this is where our maps and manuals live... This is a separate area from your idea verse that lives inside your main idea verse folder... The big three files that make this whole thing work." (`10ee430b10f3` · supporting · supporting_snippet; [[sources/how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c|How I Use Obsidian + Claude Cowork to Run My Life]])
- This setup depends on disciplined folder structure and maintenance. If the vault grows large without a map, the model can miss relevant context or behave as if it has read more than it actually has. It also still depends on a vendor tool for execution, so portability is partial rather than absolute. (`3efc27dda03e` · uncertainty · caveats; [[sources/how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c|How I Use Obsidian + Claude Cowork to Run My Life]])

## Contradictions / tensions

- This setup depends on disciplined folder structure and maintenance. If the vault grows large without a map, the model can miss relevant context or behave as if it has read more than it actually has. It also still depends on a vendor tool for execution, so portability is partial rather than absolute. (uncertainty; [[sources/how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c|How I Use Obsidian + Claude Cowork to Run My Life]])

## Related pages

- [[how-to/agentic-personal-knowledge-management|Agentic Personal Knowledge Management]]
- [[how-to/claude-skills-setup|Claude Skills Setup]]

## Sources

- [[sources/how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c|How I Use Obsidian + Claude Cowork to Run My Life]]
