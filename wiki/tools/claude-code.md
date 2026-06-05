---
title: Claude Code
slug: claude-code
entity_id: tool:claude-code
category: tool
tags:
- agentic
- browser-use
- cli-tool
- coding
- local-first
- tool-use
- workflow-automation
first_seen: '2026-03-25'
last_seen: '2026-05-05'
source_count: 7
evidence_count: 86
source_ids:
- how-claude-code-and-obsidian-broke-personal-knowledge-management-01kqky9zvey7e9mbv4tfscr37y
- how-i-built-an-ai-second-brain-using-claude-code-and-obsidian-01kr434kyy8fyj0wpm1gyx443z
- how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn
- how-to-make-claude-code-validate-its-own-work-01krkb42j4y9839773m7rz83xe
- i-spent-6-months-tuning-claude-code-here-s-the-exact-setup-that-finally-worked-01kr4358p7t4vfwjd4r6xqdmkj
- i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769
- obsidian-claude-code-is-your-24-7-ai-agent-here-is-how-to-build-yours-01kqkvgnyhw96eaf0eb9fj5gft
value_level: high
confidence: 0.9214285714285715
synthesis_state: stage1-placeholder
types:
- ai-application
- coding-agent
- terminal
---

# Claude Code

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Claude Code is the environment the article uses to load and run Claude Skills from the file system and marketplace. It is presented as the execution layer that discovers matching skills and applies their instructions to user requests.

## Core Capabilities

- It loads the appropriate Skill when a user request matches the Skill metadata, which is useful for repeatable workflows.
- It can manage skills through plugins and a marketplace, which makes distribution and installation more structured.
- It supports a file-based Skill format centered on SKILL.md, which keeps reusable instructions outside the chat transcript.
- It can operate as a terminal-based agent that reads repository files and writes changes back to disk.
- It can update multiple related markdown artifacts in a single operation, which is useful for keeping derived notes synchronized.
- It can be scripted through command-line invocations, making scheduled maintenance loops possible.
- It can read a directory of sources and update multiple wiki pages during a single ingest pass.
- It can discuss key takeaways with the user while processing, which helps with editorial decisions.
- It can run lint-like maintenance checks that look for contradictions, orphan pages, and missing concepts.
- It can read local markdown files from a connected vault so the agent can use stored context rather than starting from scratch.
- It can create and edit notes in the user's folder structure, which makes it useful for workflow automation over personal knowledge bases.
- It can use instructions from a CLAUDE.md file to follow local rules and writing preferences.
- It can operate in a planning mode that produces an editable plan document before destructive actions take place.
- It can use subagents with constrained tools and read-only permissions for review and exploration tasks.
- It can run in headless mode inside continuous integration to execute evaluation jobs and draft pull requests.
- It can be extended with hooks, skills, and MCP servers to enforce repository-specific behavior and external tool access.
- It runs command-line workflows on a local machine, which makes it suitable for automation that needs direct access to files and folders.
- It can read and write files in an Obsidian vault, which allows it to generate and maintain structured notes.
- It can use MCP integrations to search Gmail, pull calendar events, and access Drive data from one command.
- It can persist instructions in CLAUDE.md so recurring behavior does not need to be re-entered each session.
- It can generate and revise code while using verification tools to compare outputs against an expected result.
- It can continue iterating on a task until the result is close enough to the reference output.
- It can inspect rendered web pages through Chrome when the task is visual rather than purely textual.

## Integration Ecosystem

- It is integrated with the anthropics/skills marketplace for installing official and example skill sets.
- It works with the /plugin command flow for adding, listing, updating, and deleting plugins.
- It is described as the execution environment for Claude Skills rather than a standalone document editor.
- The article uses it with a local Obsidian vault as the file-backed knowledge base.
- The workflow relies on command-line access with Bash, Read, and Write permissions.
- It is framed as compatible with cron-style scheduled jobs on the operating system.
- It is used with markdown files on disk, so it fits a file-based workflow rather than a closed app workflow.
- It is paired with a CLAUDE.md schema file that constrains how the agent maintains the wiki.
- It works alongside Obsidian as the reading and browsing surface for the generated knowledge base.
- It connects through a filesystem MCP server that points at the Obsidian vault path.
- It can work with an Obsidian-specific MCP plugin that exposes tags, links, and active note context.
- It operates as a local desktop app rather than only as a chat interface.
- It is shown working with GitHub Actions for nightly evaluation and draft pull request automation.
- It is shown using the Model Context Protocol to connect to GitHub, filesystem, web search, and documentation servers.
- It is shown integrating with evaluation scripts, formatting hooks, and repository rules stored under a .claude directory.
- It is shown alongside worktrees and a project-local memory layout to keep parallel sessions isolated.
- It integrates with MCP, which the source uses for Gmail, Google Calendar, and Google Drive access.
- It works with local markdown files and Obsidian vault structures, so it fits file-native knowledge workflows.
- It uses CLAUDE.md as an instruction file, which creates a lightweight configuration surface for repeated commands.
- The source explicitly describes using Google Chrome as a visual inspection tool for Claude Code.
- The source also describes using code execution and output comparison as a verification loop for LLM-based processing.

## Maturity signals

The article presents Claude Code as the working environment for official skills, local skills, and plugin-based installation. That suggests a fairly mature product surface for skill discovery and execution, but the source is still a practitioner guide rather than independent evaluation. The piece does not provide adoption metrics or stability evidence.

## Related Tools

- Claude Skills
- Skill-creator
- Obsidian
- GitHub MCP
- E2B MCP
- Ollama
- Granola

## Strengths

- It can automatically discover installed skills by scanning their metadata at session start, which reduces the need for manual triggering and makes reusable workflows easier to apply consistently.
- It supports a marketplace/plugin flow, so skills can be installed and managed through a structured mechanism instead of ad hoc file copying.
- It uses on-demand loading, which keeps the always-present context small and only loads the full instructions when a request matches the skill.
- It is paired with the Skill-creator meta skill, which the article describes as a loop for drafting, testing, evaluating, and improving skills.

## Weaknesses / limitations

The article does not provide evidence about robustness, failure modes, or production-scale reliability. The workflow depends heavily on accurate metadata and on users installing the right plugins, so misclassification or trust issues could reduce usefulness, but the source only hints at that indirectly.

## Evidence / supporting sources

### How Claude Code and Obsidian Broke Personal Knowledge Management (2026-04-11)

- The article uses it with a local Obsidian vault as the file-backed knowledge base. (`68c289e5974d` · neutral · integration_ecosystem[0]; [[sources/how-claude-code-and-obsidian-broke-personal-knowledge-management-01kqky9zvey7e9mbv4tfscr37y|How Claude Code and Obsidian Broke Personal Knowledge Management]])
- The workflow relies on command-line access with Bash, Read, and Write permissions. (`0ecb48e883ee` · neutral · integration_ecosystem[1]; [[sources/how-claude-code-and-obsidian-broke-personal-knowledge-management-01kqky9zvey7e9mbv4tfscr37y|How Claude Code and Obsidian Broke Personal Knowledge Management]])
- It is framed as compatible with cron-style scheduled jobs on the operating system. (`acc579a035c6` · neutral · integration_ecosystem[2]; [[sources/how-claude-code-and-obsidian-broke-personal-knowledge-management-01kqky9zvey7e9mbv4tfscr37y|How Claude Code and Obsidian Broke Personal Knowledge Management]])
- The source treats it as a practical local tool rather than a prototype concept, but offers no adoption statistics or ecosystem evidence. Its use here suggests enough maturity for individual workflow automation, yet the article gives no indication of broader operational standardization. (`14225e5976c0` · neutral · maturity_signals; [[sources/how-claude-code-and-obsidian-broke-personal-knowledge-management-01kqky9zvey7e9mbv4tfscr37y|How Claude Code and Obsidian Broke Personal Knowledge Management]])
- It fits as the execution layer for file-native AI workflows: ingesting new material, updating derived notes, and running periodic health checks from the terminal. For practitioners, the important point is that the agent is not just answering questions; it is editing and maintaining artifacts across many files. That makes it relevant to knowledge-base maintenance, coding workflows, and other automation loops where the model needs filesystem access. (`c351a7d0a946` · neutral · operational_relevance; [[sources/how-claude-code-and-obsidian-broke-personal-knowledge-management-01kqky9zvey7e9mbv4tfscr37y|How Claude Code and Obsidian Broke Personal Knowledge Management]])
- Claude Code is an autonomous terminal agent that can read, write, and modify files through the command line. In this article, it is used as the worker that maintains a markdown-based knowledge system. (`9452b5195191` · neutral · short_description; [[sources/how-claude-code-and-obsidian-broke-personal-knowledge-management-01kqky9zvey7e9mbv4tfscr37y|How Claude Code and Obsidian Broke Personal Knowledge Management]])
- - Can read and write multiple markdown files in one pass, which matters when the workflow depends on coordinated updates across summaries, indexes, and concept pages.
- Supports scripted command-line operation, so the same maintenance loop can be triggered manually or on a schedule.
- Can be given narrow allowed tools, which is useful when you want the agent to operate inside a constrained file-editing boundary rather than a broad desktop environment. (`3c1cc9be9791` · neutral · strengths; [[sources/how-claude-code-and-obsidian-broke-personal-knowledge-management-01kqky9zvey7e9mbv4tfscr37y|How Claude Code and Obsidian Broke Personal Knowledge Management]])
- It can operate as a terminal-based agent that reads repository files and writes changes back to disk. (`9727d3eb1ad7` · supporting · core_capabilities[0]; [[sources/how-claude-code-and-obsidian-broke-personal-knowledge-management-01kqky9zvey7e9mbv4tfscr37y|How Claude Code and Obsidian Broke Personal Knowledge Management]])
- It can update multiple related markdown artifacts in a single operation, which is useful for keeping derived notes synchronized. (`939307f84bdd` · supporting · core_capabilities[1]; [[sources/how-claude-code-and-obsidian-broke-personal-knowledge-management-01kqky9zvey7e9mbv4tfscr37y|How Claude Code and Obsidian Broke Personal Knowledge Management]])
- It can be scripted through command-line invocations, making scheduled maintenance loops possible. (`1738c432e8c8` · supporting · core_capabilities[2]; [[sources/how-claude-code-and-obsidian-broke-personal-knowledge-management-01kqky9zvey7e9mbv4tfscr37y|How Claude Code and Obsidian Broke Personal Knowledge Management]])
- By connecting Obsidian (as a local markdown interface) with Claude Code (as an autonomous terminal agent), you can completely eliminate the maintenance bottleneck. (`3ffca2c251cf` · supporting · supporting_snippet; [[sources/how-claude-code-and-obsidian-broke-personal-knowledge-management-01kqky9zvey7e9mbv4tfscr37y|How Claude Code and Obsidian Broke Personal Knowledge Management]])
- The article does not provide evidence about reliability, conflict resolution, or how often the agent makes incorrect edits. The workflow still depends on disciplined prompts and human review, so the operational savings may be smaller than the rhetoric implies. No cost, latency, or enterprise-readiness data is given. (`1921db2d924a` · uncertainty · weaknesses_limitations; [[sources/how-claude-code-and-obsidian-broke-personal-knowledge-management-01kqky9zvey7e9mbv4tfscr37y|How Claude Code and Obsidian Broke Personal Knowledge Management]])

### How I Built an AI Second Brain Using Claude Code and Obsidian (2026-05-03)

- It integrates with MCP, which the source uses for Gmail, Google Calendar, and Google Drive access. (`8acd60c82266` · neutral · integration_ecosystem[0]; [[sources/how-i-built-an-ai-second-brain-using-claude-code-and-obsidian-01kr434kyy8fyj0wpm1gyx443z|How I Built an AI Second Brain Using Claude Code and Obsidian]])
- It works with local markdown files and Obsidian vault structures, so it fits file-native knowledge workflows. (`142f3b1f9c79` · neutral · integration_ecosystem[1]; [[sources/how-i-built-an-ai-second-brain-using-claude-code-and-obsidian-01kr434kyy8fyj0wpm1gyx443z|How I Built an AI Second Brain Using Claude Code and Obsidian]])
- It uses CLAUDE.md as an instruction file, which creates a lightweight configuration surface for repeated commands. (`70d4721f92f5` · neutral · integration_ecosystem[2]; [[sources/how-i-built-an-ai-second-brain-using-claude-code-and-obsidian-01kr434kyy8fyj0wpm1gyx443z|How I Built an AI Second Brain Using Claude Code and Obsidian]])
- The article presents it as a practical developer tool rather than an experimental demo: it runs locally, has documented MCP support, and is already used for file and workflow automation. The source does not provide adoption metrics, so maturity should be read as tool-level practicality rather than market scale. (`9b22ed2c8a2b` · neutral · maturity_signals; [[sources/how-i-built-an-ai-second-brain-using-claude-code-and-obsidian-01kr434kyy8fyj0wpm1gyx443z|How I Built an AI Second Brain Using Claude Code and Obsidian]])
- This is useful wherever an agent needs direct filesystem access and the ability to run multi-step workflows without a browser. The source shows it as the control plane for a local knowledge workflow: reading mail and calendar data through MCP, writing structured notes, and cleaning up a vault. For service automation practitioners, the key point is that a command-line agent can sit between external data sources and local artifacts without a bespoke app layer. (`723daeca9c4e` · neutral · operational_relevance; [[sources/how-i-built-an-ai-second-brain-using-claude-code-and-obsidian-01kr434kyy8fyj0wpm1gyx443z|How I Built an AI Second Brain Using Claude Code and Obsidian]])
- Anthropic’s command-line AI tool that runs on a local machine and can read, write, and organize files directly. It is used here as the orchestrator for a personal daily-briefing workflow. (`67d1e04f66da` · neutral · short_description; [[sources/how-i-built-an-ai-second-brain-using-claude-code-and-obsidian-01kr434kyy8fyj0wpm1gyx443z|How I Built an AI Second Brain Using Claude Code and Obsidian]])
- - Can read and write local files directly, which makes it practical for file-native workflows and note automation.
- Supports MCP integrations, so it can pull data from Gmail, Google Calendar, and Google Drive without manual copy-paste.
- Uses a persistent CLAUDE.md instruction file, which lets the workflow encode repeated commands and preferences in one place.
- Can execute multi-step daily routines from plain-English instructions, which lowers the setup burden for non-engineering users. (`0a97e1e3b615` · neutral · strengths; [[sources/how-i-built-an-ai-second-brain-using-claude-code-and-obsidian-01kr434kyy8fyj0wpm1gyx443z|How I Built an AI Second Brain Using Claude Code and Obsidian]])
- It runs command-line workflows on a local machine, which makes it suitable for automation that needs direct access to files and folders. (`32cdf14342d7` · supporting · core_capabilities[0]; [[sources/how-i-built-an-ai-second-brain-using-claude-code-and-obsidian-01kr434kyy8fyj0wpm1gyx443z|How I Built an AI Second Brain Using Claude Code and Obsidian]])
- It can read and write files in an Obsidian vault, which allows it to generate and maintain structured notes. (`e2ce38bd0250` · supporting · core_capabilities[1]; [[sources/how-i-built-an-ai-second-brain-using-claude-code-and-obsidian-01kr434kyy8fyj0wpm1gyx443z|How I Built an AI Second Brain Using Claude Code and Obsidian]])
- It can use MCP integrations to search Gmail, pull calendar events, and access Drive data from one command. (`9d27d45f9947` · supporting · core_capabilities[2]; [[sources/how-i-built-an-ai-second-brain-using-claude-code-and-obsidian-01kr434kyy8fyj0wpm1gyx443z|How I Built an AI Second Brain Using Claude Code and Obsidian]])
- It can persist instructions in CLAUDE.md so recurring behavior does not need to be re-entered each session. (`a85d35bf85c6` · supporting · core_capabilities[3]; [[sources/how-i-built-an-ai-second-brain-using-claude-code-and-obsidian-01kr434kyy8fyj0wpm1gyx443z|How I Built an AI Second Brain Using Claude Code and Obsidian]])
- "Claude Code is different. It’s Anthropic’s command-line AI tool. It runs in your terminal, directly on your machine." (`07faeb081efd` · supporting · supporting_snippet; [[sources/how-i-built-an-ai-second-brain-using-claude-code-and-obsidian-01kr434kyy8fyj0wpm1gyx443z|How I Built an AI Second Brain Using Claude Code and Obsidian]])
- The source also shows that it needs prompt iteration and cleanup to behave well: the first version over-long summarized email, missed recurring events, and mis-carried tasks. OAuth and permission setup can be finicky, and the workflow still depends on careful instruction design rather than magic autonomy. That makes it powerful, but not maintenance-free. (`8caaefe5f63c` · uncertainty · weaknesses_limitations; [[sources/how-i-built-an-ai-second-brain-using-claude-code-and-obsidian-01kr434kyy8fyj0wpm1gyx443z|How I Built an AI Second Brain Using Claude Code and Obsidian]])

### How to build Claude Skills 2.0 Better than 99% of People (2026-03-25)

- It is integrated with the anthropics/skills marketplace for installing official and example skill sets. (`f354130dc066` · neutral · integration_ecosystem[0]; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])
- It works with the /plugin command flow for adding, listing, updating, and deleting plugins. (`e0cdf1b8f554` · neutral · integration_ecosystem[1]; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])
- It is described as the execution environment for Claude Skills rather than a standalone document editor. (`31278d192716` · neutral · integration_ecosystem[2]; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])
- The article presents Claude Code as the working environment for official skills, local skills, and plugin-based installation. That suggests a fairly mature product surface for skill discovery and execution, but the source is still a practitioner guide rather than independent evaluation. The piece does not provide adoption metrics or stability evidence. (`ce40f1fdc1ab` · neutral · maturity_signals; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])
- This matters for teams that want reusable, file-based workflow instructions rather than repeating prompts in chat. The article frames Claude Code as the place where skills are discovered at startup, matched by metadata, and then loaded only when needed, which is operationally useful for repeatable internal workflows and agent setup. It is also the interface used for plugin installation and skill management, so it sits at the center of the workflow rather than being a passive feature. (`11682e5aad84` · neutral · operational_relevance; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])
- Claude Code is the environment the article uses to load and run Claude Skills from the file system and marketplace. It is presented as the execution layer that discovers matching skills and applies their instructions to user requests. (`456a9da9bca4` · neutral · short_description; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])
- - It can automatically discover installed skills by scanning their metadata at session start, which reduces the need for manual triggering and makes reusable workflows easier to apply consistently.
- It supports a marketplace/plugin flow, so skills can be installed and managed through a structured mechanism instead of ad hoc file copying.
- It uses on-demand loading, which keeps the always-present context small and only loads the full instructions when a request matches the skill.
- It is paired with the Skill-creator meta skill, which the article describes as a loop for drafting, testing, evaluating, and improving skills. (`b0a740e9aac1` · neutral · strengths; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])
- It loads the appropriate Skill when a user request matches the Skill metadata, which is useful for repeatable workflows. (`ea9a1877c6e1` · supporting · core_capabilities[0]; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])
- It can manage skills through plugins and a marketplace, which makes distribution and installation more structured. (`1fe4a57c7dee` · supporting · core_capabilities[1]; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])
- It supports a file-based Skill format centered on SKILL.md, which keeps reusable instructions outside the chat transcript. (`7469b4513ffc` · supporting · core_capabilities[2]; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])
- "Claude Code loads the appropriate Skill in response to a user request and executes the task according to the instructions." (`1579ca6c962e` · supporting · supporting_snippet; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])
- The article does not provide evidence about robustness, failure modes, or production-scale reliability. The workflow depends heavily on accurate metadata and on users installing the right plugins, so misclassification or trust issues could reduce usefulness, but the source only hints at that indirectly. (`4d917997b6b1` · uncertainty · weaknesses_limitations; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])

### How to Make Claude Code Validate its own Work (2026-05-05)

- The source explicitly describes using Google Chrome as a visual inspection tool for Claude Code. (`a3da17c85873` · neutral · integration_ecosystem[0]; [[sources/how-to-make-claude-code-validate-its-own-work-01krkb42j4y9839773m7rz83xe|How to Make Claude Code Validate its own Work]])
- The source also describes using code execution and output comparison as a verification loop for LLM-based processing. (`37bce8f03594` · neutral · integration_ecosystem[1]; [[sources/how-to-make-claude-code-validate-its-own-work-01krkb42j4y9839773m7rz83xe|How to Make Claude Code Validate its own Work]])
- Claude Code is presented as a practical developer tool rather than an experimental prototype. The article assumes it is already usable in real coding workflows and that tool access such as Chrome inspection is available for agent verification loops. Evidence of maturity here is anecdotal, not market-wide. (`f3291cad9ab5` · neutral · maturity_signals; [[sources/how-to-make-claude-code-validate-its-own-work-01krkb42j4y9839773m7rz83xe|How to Make Claude Code Validate its own Work]])
- This source treats Claude Code as an agent that becomes more useful when it can validate its own work against a known target. That matters for coding workflows where the agent needs to test changes, inspect rendered output, or compare outputs against a reference before handing work back to a human. The practical pattern is especially relevant for iterative implementation tasks, latency debugging, and UI work in existing codebases. (`d1fe4a7289ed` · neutral · operational_relevance; [[sources/how-to-make-claude-code-validate-its-own-work-01krkb42j4y9839773m7rz83xe|How to Make Claude Code Validate its own Work]])
- Claude Code is a coding agent that can write, inspect, and revise code while using external tools to check its own output. (`333893ebab79` · neutral · short_description; [[sources/how-to-make-claude-code-validate-its-own-work-01krkb42j4y9839773m7rz83xe|How to Make Claude Code Validate its own Work]])
- - Can keep iterating until its output matches a verifiable target, which improves the odds of one-shot success on bounded coding tasks.
- Works well when paired with test execution or browser inspection, because the agent can compare actual results against expected results instead of relying on a single generation pass.
- The source shows it can handle a design implementation loop when given screenshots and Chrome access, which is useful for visual QA and UI refinement. (`624d12cda89b` · neutral · strengths; [[sources/how-to-make-claude-code-validate-its-own-work-01krkb42j4y9839773m7rz83xe|How to Make Claude Code Validate its own Work]])
- It can generate and revise code while using verification tools to compare outputs against an expected result. (`7a92136b6ff8` · supporting · core_capabilities[0]; [[sources/how-to-make-claude-code-validate-its-own-work-01krkb42j4y9839773m7rz83xe|How to Make Claude Code Validate its own Work]])
- It can continue iterating on a task until the result is close enough to the reference output. (`0427c40c26c1` · supporting · core_capabilities[1]; [[sources/how-to-make-claude-code-validate-its-own-work-01krkb42j4y9839773m7rz83xe|How to Make Claude Code Validate its own Work]])
- It can inspect rendered web pages through Chrome when the task is visual rather than purely textual. (`747cb5567311` · supporting · core_capabilities[2]; [[sources/how-to-make-claude-code-validate-its-own-work-01krkb42j4y9839773m7rz83xe|How to Make Claude Code Validate its own Work]])
- Claude Code is a very powerful model out of the box. To leverage its full capabilities, however, you need to give it access to validate and verify its own work. (`f7c9a5022a81` · supporting · supporting_snippet; [[sources/how-to-make-claude-code-validate-its-own-work-01krkb42j4y9839773m7rz83xe|How to Make Claude Code Validate its own Work]])
- The source does not provide a rigorous benchmark, so the gains are based on a personal workflow report rather than controlled measurement. The approach depends on having a clear acceptance signal; tasks without a precise target, or with hidden requirements, may not benefit as much. The Chrome-based visual loop also depends on environment/tool access and may be brittle in some stacks. (`980d0a466d41` · uncertainty · weaknesses_limitations; [[sources/how-to-make-claude-code-validate-its-own-work-01krkb42j4y9839773m7rz83xe|How to Make Claude Code Validate its own Work]])

### I Spent 6 Months Tuning Claude Code. Here’s the Exact Setup That Finally Worked. (2026-04-25)

- It is shown working with GitHub Actions for nightly evaluation and draft pull request automation. (`e4c032e96a7e` · neutral · integration_ecosystem[0]; [[sources/i-spent-6-months-tuning-claude-code-here-s-the-exact-setup-that-finally-worked-01kr4358p7t4vfwjd4r6xqdmkj|I Spent 6 Months Tuning Claude Code. Here’s the Exact Setup That Finally Worked.]])
- It is shown using the Model Context Protocol to connect to GitHub, filesystem, web search, and documentation servers. (`c42eb05d66e8` · neutral · integration_ecosystem[1]; [[sources/i-spent-6-months-tuning-claude-code-here-s-the-exact-setup-that-finally-worked-01kr4358p7t4vfwjd4r6xqdmkj|I Spent 6 Months Tuning Claude Code. Here’s the Exact Setup That Finally Worked.]])
- It is shown integrating with evaluation scripts, formatting hooks, and repository rules stored under a .claude directory. (`e2c22e33fb45` · neutral · integration_ecosystem[2]; [[sources/i-spent-6-months-tuning-claude-code-here-s-the-exact-setup-that-finally-worked-01kr4358p7t4vfwjd4r6xqdmkj|I Spent 6 Months Tuning Claude Code. Here’s the Exact Setup That Finally Worked.]])
- It is shown alongside worktrees and a project-local memory layout to keep parallel sessions isolated. (`5a4075e0703b` · neutral · integration_ecosystem[3]; [[sources/i-spent-6-months-tuning-claude-code-here-s-the-exact-setup-that-finally-worked-01kr4358p7t4vfwjd4r6xqdmkj|I Spent 6 Months Tuning Claude Code. Here’s the Exact Setup That Finally Worked.]])
- The article frames Claude Code as established enough to support Plan Mode, subagents, hooks, skills, worktrees, and headless CI use. It also shows an ecosystem of community and vendor-supported extensions such as skills and MCP servers. At the same time, the piece suggests that many engineers are still underusing it, which implies maturity at the product level but uneven operational adoption. (`172c9c17036d` · neutral · maturity_signals; [[sources/i-spent-6-months-tuning-claude-code-here-s-the-exact-setup-that-finally-worked-01kr4358p7t4vfwjd4r6xqdmkj|I Spent 6 Months Tuning Claude Code. Here’s the Exact Setup That Finally Worked.]])
- The piece treats Claude Code as the orchestration surface for a full engineering workflow rather than a chat box. That makes it relevant for teams that want agentic code changes, repository-specific guardrails, and automated eval loops. It is especially relevant where one session must coordinate reading code, editing files, running checks, and opening pull requests with limited context. (`325ef1af9db8` · neutral · operational_relevance; [[sources/i-spent-6-months-tuning-claude-code-here-s-the-exact-setup-that-finally-worked-01kr4358p7t4vfwjd4r6xqdmkj|I Spent 6 Months Tuning Claude Code. Here’s the Exact Setup That Finally Worked.]])
- An AI coding assistant for planning, editing, reviewing, and automating software changes inside a repository. In this article it is used with subagents, hooks, skills, worktrees, and headless runs to make longer tasks more controlled and repeatable. (`ae09c7e35f20` · neutral · short_description; [[sources/i-spent-6-months-tuning-claude-code-here-s-the-exact-setup-that-finally-worked-01kr4358p7t4vfwjd4r6xqdmkj|I Spent 6 Months Tuning Claude Code. Here’s the Exact Setup That Finally Worked.]])
- - Supports a layered workflow where memory, rules, subagents, hooks, and skills each handle a different part of the task, which reduces the need to cram everything into one prompt.
- Works well with Plan Mode and read-only subagents for risky tasks, so teams can review a concrete plan before edits are applied.
- Fits headless automation and worktree-based parallelism, which lets one run implement code, another run evals, and a third draft the PR without blocking on a single session.
- The article presents it as highly configurable for repo-specific guardrails, including path-scoped rules and permission deferrals for sensitive operations. (`e53f118b05c9` · neutral · strengths; [[sources/i-spent-6-months-tuning-claude-code-here-s-the-exact-setup-that-finally-worked-01kr4358p7t4vfwjd4r6xqdmkj|I Spent 6 Months Tuning Claude Code. Here’s the Exact Setup That Finally Worked.]])
- It can operate in a planning mode that produces an editable plan document before destructive actions take place. (`835d5ed167f0` · supporting · core_capabilities[0]; [[sources/i-spent-6-months-tuning-claude-code-here-s-the-exact-setup-that-finally-worked-01kr4358p7t4vfwjd4r6xqdmkj|I Spent 6 Months Tuning Claude Code. Here’s the Exact Setup That Finally Worked.]])
- It can use subagents with constrained tools and read-only permissions for review and exploration tasks. (`cbd9f21984db` · supporting · core_capabilities[1]; [[sources/i-spent-6-months-tuning-claude-code-here-s-the-exact-setup-that-finally-worked-01kr4358p7t4vfwjd4r6xqdmkj|I Spent 6 Months Tuning Claude Code. Here’s the Exact Setup That Finally Worked.]])
- It can run in headless mode inside continuous integration to execute evaluation jobs and draft pull requests. (`019b7371e33c` · supporting · core_capabilities[2]; [[sources/i-spent-6-months-tuning-claude-code-here-s-the-exact-setup-that-finally-worked-01kr4358p7t4vfwjd4r6xqdmkj|I Spent 6 Months Tuning Claude Code. Here’s the Exact Setup That Finally Worked.]])
- It can be extended with hooks, skills, and MCP servers to enforce repository-specific behavior and external tool access. (`b688d86ab068` · supporting · core_capabilities[3]; [[sources/i-spent-6-months-tuning-claude-code-here-s-the-exact-setup-that-finally-worked-01kr4358p7t4vfwjd4r6xqdmkj|I Spent 6 Months Tuning Claude Code. Here’s the Exact Setup That Finally Worked.]])
- "For most engineers using Claude Code right now the answer is ‘command not found’ or a single file containing a vague instruction to write clean code. That is fine. It also leaves roughly 80% of the product on the floor." (`df118d058271` · supporting · supporting_snippet; [[sources/i-spent-6-months-tuning-claude-code-here-s-the-exact-setup-that-finally-worked-01kr4358p7t4vfwjd4r6xqdmkj|I Spent 6 Months Tuning Claude Code. Here’s the Exact Setup That Finally Worked.]])
- The setup depends on disciplined configuration; the article explicitly says the empty-folder version leaves much of the product unused. It also implies that token overhead from large memory files and too many MCP servers can erode performance, so careless configuration can make the tool less effective. The article does not provide independent evidence that every team will benefit equally from the same stack. (`b664ed7ccb40` · uncertainty · weaknesses_limitations; [[sources/i-spent-6-months-tuning-claude-code-here-s-the-exact-setup-that-finally-worked-01kr4358p7t4vfwjd4r6xqdmkj|I Spent 6 Months Tuning Claude Code. Here’s the Exact Setup That Finally Worked.]])

### I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me. (2026-04-19)

- It is used with markdown files on disk, so it fits a file-based workflow rather than a closed app workflow. (`9b14b2b2afb1` · neutral · integration_ecosystem[0]; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- It is paired with a CLAUDE.md schema file that constrains how the agent maintains the wiki. (`651bab5d6815` · neutral · integration_ecosystem[1]; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- It works alongside Obsidian as the reading and browsing surface for the generated knowledge base. (`e6c4df2b3a88` · neutral · integration_ecosystem[2]; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- The article treats Claude Code as usable enough for a daily workflow, but not as a fully autonomous system. Its role here is experimental and personal rather than evidence of broad enterprise maturity. The source does not give adoption metrics, so maturity appears moderate at best from this account. (`defaa1dde673` · neutral · maturity_signals; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- The tool is being used less like a chat assistant and more like a filesystem-aware maintenance agent. That makes it relevant for teams that want an LLM to repeatedly transform incoming documents into structured artifacts, especially when the workflow depends on editing many files, not just answering one query. It also shows why agent behavior needs schema constraints and human diff review when the model is acting as a writer and curator rather than a pure generator. (`acb0384e86ac` · neutral · operational_relevance; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- An AI coding agent that can read a folder, process sources, and update files as part of an automated workflow. In this article it is used as the agent that ingests sources into a maintained wiki. (`512054a408fb` · neutral · short_description; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- - It can process a source, create summary pages, update indices, and revise related pages in one ingest cycle, which is useful when knowledge needs to be maintained across many files.
- It supports a conversational review loop during ingest, so the human can steer editorial choices instead of accepting a fully automatic batch job.
- It can generate a wiki-like structure from raw documents, which makes it more useful for knowledge workflows than a single-turn question-answer interface. (`7ce505f0a965` · neutral · strengths; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- It can read a directory of sources and update multiple wiki pages during a single ingest pass. (`f1305efe8c5b` · supporting · core_capabilities[0]; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- It can discuss key takeaways with the user while processing, which helps with editorial decisions. (`c2ad885ea735` · supporting · core_capabilities[1]; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- It can run lint-like maintenance checks that look for contradictions, orphan pages, and missing concepts. (`15b0b6aef412` · supporting · core_capabilities[2]; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- "Then I opened Claude Code, pointed it at the directory, and gave it the gist." (`3d60a1afc271` · supporting · supporting_snippet; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- The article reports that the workflow depends on schema discipline and git diff review, so the agent is not a set-and-forget system. It also concentrates most cost in ingest, and the author notes that the approach begins to strain around 100-200 sources, at which point a more robust retrieval or governance layer may be needed. (`41c31e650eff` · uncertainty · weaknesses_limitations; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])

### Obsidian + Claude Code is your 24×7 AI Agent: Here is how to build yours (2026-04-23)

- It connects through a filesystem MCP server that points at the Obsidian vault path. (`c4ce6e2bfee5` · neutral · integration_ecosystem[0]; [[sources/obsidian-claude-code-is-your-24-7-ai-agent-here-is-how-to-build-yours-01kqkvgnyhw96eaf0eb9fj5gft|Obsidian + Claude Code is your 24×7 AI Agent: Here is how to build yours]])
- It can work with an Obsidian-specific MCP plugin that exposes tags, links, and active note context. (`8fee76d69d14` · neutral · integration_ecosystem[1]; [[sources/obsidian-claude-code-is-your-24-7-ai-agent-here-is-how-to-build-yours-01kqkvgnyhw96eaf0eb9fj5gft|Obsidian + Claude Code is your 24×7 AI Agent: Here is how to build yours]])
- It operates as a local desktop app rather than only as a chat interface. (`093beb6bf25e` · neutral · integration_ecosystem[2]; [[sources/obsidian-claude-code-is-your-24-7-ai-agent-here-is-how-to-build-yours-01kqkvgnyhw96eaf0eb9fj5gft|Obsidian + Claude Code is your 24×7 AI Agent: Here is how to build yours]])
- The article treats Claude Code as available on desktop and already usable with tool access, which suggests a practical developer-facing product rather than an experiment. The mention of a dedicated Obsidian MCP plugin implies an emerging ecosystem around file-connected workflows. At the same time, the evidence is purely anecdotal and does not show adoption beyond one user's setup. (`ad277c8c794c` · neutral · maturity_signals; [[sources/obsidian-claude-code-is-your-24-7-ai-agent-here-is-how-to-build-yours-01kqkvgnyhw96eaf0eb9fj5gft|Obsidian + Claude Code is your 24×7 AI Agent: Here is how to build yours]])
- Claude Code is positioned as the execution layer that turns a note vault into something an agent can work with. For practitioners, the useful part is not just chat but tool access: it can list files, read notes, and create or edit markdown in a controlled folder. That makes it relevant for personal knowledge workflows, agent-assisted drafting, and lightweight automation over local content. The article uses it for recurring review and content extraction tasks rather than for code generation. (`54c135d22ceb` · neutral · operational_relevance; [[sources/obsidian-claude-code-is-your-24-7-ai-agent-here-is-how-to-build-yours-01kqkvgnyhw96eaf0eb9fj5gft|Obsidian + Claude Code is your 24×7 AI Agent: Here is how to build yours]])
- A desktop coding agent that can run tools and access local files when connected through allowed integrations. In this setup, it is used to read notes, create markdown files, and act on an Obsidian vault. (`05c159f369d3` · neutral · short_description; [[sources/obsidian-claude-code-is-your-24-7-ai-agent-here-is-how-to-build-yours-01kqkvgnyhw96eaf0eb9fj5gft|Obsidian + Claude Code is your 24×7 AI Agent: Here is how to build yours]])
- - It can act on local files when connected to a filesystem or Obsidian MCP bridge, which matters because the agent can work directly in the user's knowledge base instead of copying content into chat.
- It can follow a persistent instruction file such as CLAUDE.md, which helps keep behavior aligned with the user's structure and style.
- It supports repeatable workflows like weekly reviews and content mining, which are the kinds of tasks that benefit most from agentic file access. (`5107937b90da` · neutral · strengths; [[sources/obsidian-claude-code-is-your-24-7-ai-agent-here-is-how-to-build-yours-01kqkvgnyhw96eaf0eb9fj5gft|Obsidian + Claude Code is your 24×7 AI Agent: Here is how to build yours]])
- It can read local markdown files from a connected vault so the agent can use stored context rather than starting from scratch. (`88e8e96ec56a` · supporting · core_capabilities[0]; [[sources/obsidian-claude-code-is-your-24-7-ai-agent-here-is-how-to-build-yours-01kqkvgnyhw96eaf0eb9fj5gft|Obsidian + Claude Code is your 24×7 AI Agent: Here is how to build yours]])
- It can create and edit notes in the user's folder structure, which makes it useful for workflow automation over personal knowledge bases. (`24ca12d366f6` · supporting · core_capabilities[1]; [[sources/obsidian-claude-code-is-your-24-7-ai-agent-here-is-how-to-build-yours-01kqkvgnyhw96eaf0eb9fj5gft|Obsidian + Claude Code is your 24×7 AI Agent: Here is how to build yours]])
- It can use instructions from a CLAUDE.md file to follow local rules and writing preferences. (`fd0f27c2e84f` · supporting · core_capabilities[2]; [[sources/obsidian-claude-code-is-your-24-7-ai-agent-here-is-how-to-build-yours-01kqkvgnyhw96eaf0eb9fj5gft|Obsidian + Claude Code is your 24×7 AI Agent: Here is how to build yours]])
- "Then I installed Claude Code on desktop. The important bits: It runs as a local app and can talk to tools like filesystem or Obsidian MCP." (`054a1d15dd2e` · supporting · supporting_snippet; [[sources/obsidian-claude-code-is-your-24-7-ai-agent-here-is-how-to-build-yours-01kqkvgnyhw96eaf0eb9fj5gft|Obsidian + Claude Code is your 24×7 AI Agent: Here is how to build yours]])
- The article does not show error handling, audit trails, or safeguards beyond a simple instruction not to delete notes without asking. It also does not establish reliability across longer sessions or larger vaults. The setup appears useful for personal workflows, but the source gives no evidence that it is robust enough for shared or high-stakes environments. (`0732dd98f7be` · uncertainty · weaknesses_limitations; [[sources/obsidian-claude-code-is-your-24-7-ai-agent-here-is-how-to-build-yours-01kqkvgnyhw96eaf0eb9fj5gft|Obsidian + Claude Code is your 24×7 AI Agent: Here is how to build yours]])

## Contradictions / tensions

- The article does not provide evidence about robustness, failure modes, or production-scale reliability. The workflow depends heavily on accurate metadata and on users installing the right plugins, so misclassification or trust issues could reduce usefulness, but the source only hints at that indirectly. (uncertainty; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])
- The article does not provide evidence about reliability, conflict resolution, or how often the agent makes incorrect edits. The workflow still depends on disciplined prompts and human review, so the operational savings may be smaller than the rhetoric implies. No cost, latency, or enterprise-readiness data is given. (uncertainty; [[sources/how-claude-code-and-obsidian-broke-personal-knowledge-management-01kqky9zvey7e9mbv4tfscr37y|How Claude Code and Obsidian Broke Personal Knowledge Management]])
- The article reports that the workflow depends on schema discipline and git diff review, so the agent is not a set-and-forget system. It also concentrates most cost in ingest, and the author notes that the approach begins to strain around 100-200 sources, at which point a more robust retrieval or governance layer may be needed. (uncertainty; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- The article does not show error handling, audit trails, or safeguards beyond a simple instruction not to delete notes without asking. It also does not establish reliability across longer sessions or larger vaults. The setup appears useful for personal workflows, but the source gives no evidence that it is robust enough for shared or high-stakes environments. (uncertainty; [[sources/obsidian-claude-code-is-your-24-7-ai-agent-here-is-how-to-build-yours-01kqkvgnyhw96eaf0eb9fj5gft|Obsidian + Claude Code is your 24×7 AI Agent: Here is how to build yours]])
- The setup depends on disciplined configuration; the article explicitly says the empty-folder version leaves much of the product unused. It also implies that token overhead from large memory files and too many MCP servers can erode performance, so careless configuration can make the tool less effective. The article does not provide independent evidence that every team will benefit equally from the same stack. (uncertainty; [[sources/i-spent-6-months-tuning-claude-code-here-s-the-exact-setup-that-finally-worked-01kr4358p7t4vfwjd4r6xqdmkj|I Spent 6 Months Tuning Claude Code. Here’s the Exact Setup That Finally Worked.]])
- The source also shows that it needs prompt iteration and cleanup to behave well: the first version over-long summarized email, missed recurring events, and mis-carried tasks. OAuth and permission setup can be finicky, and the workflow still depends on careful instruction design rather than magic autonomy. That makes it powerful, but not maintenance-free. (uncertainty; [[sources/how-i-built-an-ai-second-brain-using-claude-code-and-obsidian-01kr434kyy8fyj0wpm1gyx443z|How I Built an AI Second Brain Using Claude Code and Obsidian]])
- The source does not provide a rigorous benchmark, so the gains are based on a personal workflow report rather than controlled measurement. The approach depends on having a clear acceptance signal; tasks without a precise target, or with hidden requirements, may not benefit as much. The Chrome-based visual loop also depends on environment/tool access and may be brittle in some stacks. (uncertainty; [[sources/how-to-make-claude-code-validate-its-own-work-01krkb42j4y9839773m7rz83xe|How to Make Claude Code Validate its own Work]])

## Related pages

- Claude Skills
- E2B MCP
- GitHub MCP
- Granola
- Obsidian
- Ollama
- Skill-creator

## Sources

- [[sources/how-claude-code-and-obsidian-broke-personal-knowledge-management-01kqky9zvey7e9mbv4tfscr37y|How Claude Code and Obsidian Broke Personal Knowledge Management]]
- [[sources/how-i-built-an-ai-second-brain-using-claude-code-and-obsidian-01kr434kyy8fyj0wpm1gyx443z|How I Built an AI Second Brain Using Claude Code and Obsidian]]
- [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]]
- [[sources/how-to-make-claude-code-validate-its-own-work-01krkb42j4y9839773m7rz83xe|How to Make Claude Code Validate its own Work]]
- [[sources/i-spent-6-months-tuning-claude-code-here-s-the-exact-setup-that-finally-worked-01kr4358p7t4vfwjd4r6xqdmkj|I Spent 6 Months Tuning Claude Code. Here’s the Exact Setup That Finally Worked.]]
- [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]]
- [[sources/obsidian-claude-code-is-your-24-7-ai-agent-here-is-how-to-build-yours-01kqkvgnyhw96eaf0eb9fj5gft|Obsidian + Claude Code is your 24×7 AI Agent: Here is how to build yours]]
