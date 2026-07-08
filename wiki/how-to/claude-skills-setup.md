---
title: Claude Skills Setup
slug: claude-skills-setup
entity_id: how_to:claude-skills-setup
category: how-to
tags:
- ai-engineering
- context-engineering
- developer-tooling
- knowledge-systems
- workflow-automation
first_seen: '2026-01-26'
last_seen: '2026-04-14'
source_count: 3
evidence_count: 41
source_ids:
- how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn
- the-complete-guide-to-building-skills-for-claude-01krv8epdjta6664ek10fvp7tz
- your-obsidian-vault-is-a-knowledge-graph-here-s-how-to-make-it-think-quickly-01kqm1b1r3e33mym3vd0d08wbn
value_level: high
confidence: 0.9533333333333333
synthesis_state: stage1-placeholder
---

# Claude Skills Setup

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
This is a setup procedure for packaging repeatable work so Claude can recognize when to use it and follow it consistently. It addresses the common problem of having to restate the same preferences, process steps, or team rules in every conversation. It also helps when a workflow depends on built-in Claude capabilities or on an MCP server, because the skill can sit on top of those tools and guide how they are used. The result is a reusable folder that makes a specific task easier to trigger and more reliable to execute.

## Caveats

The guide treats the suggested success thresholds as rough benchmarks, not hard standards. Some measurement advice is explicitly described as aspirational, so the procedure is operationally useful but not a rigorous evaluation framework. Skills can also fail for simple packaging mistakes like a misnamed SKILL.md or invalid frontmatter.

## Implementation Steps

- Identify 2 to 3 concrete use cases the skill should enable.
- Create a kebab-case skill folder with a required SKILL.md file.
- Write YAML frontmatter with a name and a description that includes both what the skill does and when to use it.
- Keep the SKILL.md body focused on core instructions and move detailed documentation into references/ files.
- Add optional scripts/ and assets/ only when the workflow needs executable code or output templates.
- Test triggering on obvious requests, paraphrased requests, and unrelated topics.
- Iterate on the description and instructions if the skill undertriggers, overtriggers, or fails execution tests.
- Create a .claude/skills folder for the skill.
- Add a SKILL.md file with YAML front matter at the top.
- Write a brief name and description that let Claude recognize when the skill applies.
- Put step-by-step instructions in the body of SKILL.md.
- Add examples that show concrete use of the skill.
- Keep the main instructions under 500 lines and move detailed reference material into separate files if needed.
- Run Claude Code in the vault root.
- Use /init to generate a first-pass CLAUDE.md.
- Rewrite CLAUDE.md with vault structure, conventions, and safety rules.
- Install Obsidian skills with npx skills add git@github.com:kepano/obsidian-skills.git.
- Update the active context before each session.
- Optionally ask Claude to append a short session log at the end of each session.

## Prerequisites

- A clear target workflow or use case.
- Access to Claude.ai, Claude Code, or the API environment where the skill will run.
- If the skill uses MCP, a working MCP server and correct tool names.
- Basic familiarity with Markdown and YAML frontmatter.
- Access to Claude Code or a similar environment that loads skills.
- A recurring workflow or task that benefits from reusable instructions.
- Templates, rules, or domain-specific details that should be encoded into the skill.
- A local Obsidian vault with a known folder structure.
- Claude Code installed and runnable from the terminal.
- A willingness to maintain a root CLAUDE.md file over time.

## Evidence / supporting sources

### How to build Claude Skills 2.0 Better than 99% of People (2026-03-25)

- Create a skill as a folder under .claude/skills with a SKILL.md file at the center. Put only the context Claude would not already know into the skill, such as company-specific rules, templates, or repeated workflow steps. Keep the main SKILL.md concise and split deeper reference material into separate files when needed. Use clear metadata in YAML so Claude can recognize when the skill should load. Add examples and step-by-step instructions that make the task easy to execute consistently. (`a87b023a4e3d` · neutral · answer_summary; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])
- Create a .claude/skills folder for the skill. (`d5bc8dd404d3` · neutral · implementation_steps[0]; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])
- Add a SKILL.md file with YAML front matter at the top. (`abeabf977d0b` · neutral · implementation_steps[1]; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])
- Write a brief name and description that let Claude recognize when the skill applies. (`36b72b9a8301` · neutral · implementation_steps[2]; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])
- Put step-by-step instructions in the body of SKILL.md. (`0651c829053d` · neutral · implementation_steps[3]; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])
- Add examples that show concrete use of the skill. (`8090dd6462f7` · neutral · implementation_steps[4]; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])
- Keep the main instructions under 500 lines and move detailed reference material into separate files if needed. (`cb54de81629a` · neutral · implementation_steps[5]; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])
- Access to Claude Code or a similar environment that loads skills. (`25cc2d30a354` · neutral · prerequisites[0]; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])
- A recurring workflow or task that benefits from reusable instructions. (`de0048dfb719` · neutral · prerequisites[1]; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])
- Templates, rules, or domain-specific details that should be encoded into the skill. (`9e0c4d7225dd` · neutral · prerequisites[2]; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])
- This is about setting up reusable instructions so Claude can handle recurring tasks without being re-told the same rules every time. It solves the common problem of inconsistent prompting, repetitive explanations, and teams using the same AI in slightly different ways. A Skill packages the task logic, examples, and optional resources into a folder that Claude can load when the request matches. That makes it useful for work that repeats, like document formatting, design generation, or launch planning. The goal is to turn repeated manual prompting into a reusable workflow. (`6c328c097d72` · neutral · what_and_problem; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])
- "Basically, you can create a skill by simply creating .claude/skills a folder and file for the skill under SKILL.md" (`ea46c395764f` · supporting · supporting_snippet; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])
- The source stresses that metadata accuracy matters a lot, so weak or vague descriptions can reduce matching accuracy. It also recommends keeping SKILL.md under 500 lines, which means large workflows need deliberate file splitting. The article is explanatory rather than tested, so production reliability, governance, and security are not demonstrated here. (`c3bb28d18a7b` · uncertainty · caveats; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])

### The Complete Guide To Building Skills For Claude (2026-01-26)

- Start by choosing 2 to 3 concrete use cases that the skill should handle. Write a folder with a required SKILL.md file, keep the YAML frontmatter short and specific, and make sure the description says both what the skill does and when to use it. Put the detailed instructions in the body, and move longer references or assets into linked files so the prompt stays small. Then test whether the skill loads on obvious and paraphrased requests, check that it does not trigger on unrelated prompts, and iterate on the description and steps if it undertriggers, overtriggers, or fails during execution. (`74322c24527f` · neutral · answer_summary; [[sources/the-complete-guide-to-building-skills-for-claude-01krv8epdjta6664ek10fvp7tz|The Complete Guide To Building Skills For Claude]])
- Identify 2 to 3 concrete use cases the skill should enable. (`a06095a20323` · neutral · implementation_steps[0]; [[sources/the-complete-guide-to-building-skills-for-claude-01krv8epdjta6664ek10fvp7tz|The Complete Guide To Building Skills For Claude]])
- Create a kebab-case skill folder with a required SKILL.md file. (`a5cab53584f1` · neutral · implementation_steps[1]; [[sources/the-complete-guide-to-building-skills-for-claude-01krv8epdjta6664ek10fvp7tz|The Complete Guide To Building Skills For Claude]])
- Write YAML frontmatter with a name and a description that includes both what the skill does and when to use it. (`04aa40574adb` · neutral · implementation_steps[2]; [[sources/the-complete-guide-to-building-skills-for-claude-01krv8epdjta6664ek10fvp7tz|The Complete Guide To Building Skills For Claude]])
- Keep the SKILL.md body focused on core instructions and move detailed documentation into references/ files. (`4282ea691d64` · neutral · implementation_steps[3]; [[sources/the-complete-guide-to-building-skills-for-claude-01krv8epdjta6664ek10fvp7tz|The Complete Guide To Building Skills For Claude]])
- Add optional scripts/ and assets/ only when the workflow needs executable code or output templates. (`2efe1b69299f` · neutral · implementation_steps[4]; [[sources/the-complete-guide-to-building-skills-for-claude-01krv8epdjta6664ek10fvp7tz|The Complete Guide To Building Skills For Claude]])
- Test triggering on obvious requests, paraphrased requests, and unrelated topics. (`c0bd3667198e` · neutral · implementation_steps[5]; [[sources/the-complete-guide-to-building-skills-for-claude-01krv8epdjta6664ek10fvp7tz|The Complete Guide To Building Skills For Claude]])
- Iterate on the description and instructions if the skill undertriggers, overtriggers, or fails execution tests. (`7079a2c3da89` · neutral · implementation_steps[6]; [[sources/the-complete-guide-to-building-skills-for-claude-01krv8epdjta6664ek10fvp7tz|The Complete Guide To Building Skills For Claude]])
- A clear target workflow or use case. (`4474ee1c4699` · neutral · prerequisites[0]; [[sources/the-complete-guide-to-building-skills-for-claude-01krv8epdjta6664ek10fvp7tz|The Complete Guide To Building Skills For Claude]])
- Access to Claude.ai, Claude Code, or the API environment where the skill will run. (`ffcecaf10617` · neutral · prerequisites[1]; [[sources/the-complete-guide-to-building-skills-for-claude-01krv8epdjta6664ek10fvp7tz|The Complete Guide To Building Skills For Claude]])
- If the skill uses MCP, a working MCP server and correct tool names. (`651bd955c0ff` · neutral · prerequisites[2]; [[sources/the-complete-guide-to-building-skills-for-claude-01krv8epdjta6664ek10fvp7tz|The Complete Guide To Building Skills For Claude]])
- Basic familiarity with Markdown and YAML frontmatter. (`eb2886c76025` · neutral · prerequisites[3]; [[sources/the-complete-guide-to-building-skills-for-claude-01krv8epdjta6664ek10fvp7tz|The Complete Guide To Building Skills For Claude]])
- This is a setup procedure for packaging repeatable work so Claude can recognize when to use it and follow it consistently. It addresses the common problem of having to restate the same preferences, process steps, or team rules in every conversation. It also helps when a workflow depends on built-in Claude capabilities or on an MCP server, because the skill can sit on top of those tools and guide how they are used. The result is a reusable folder that makes a specific task easier to trigger and more reliable to execute. (`f6d1e15d2494` · neutral · what_and_problem; [[sources/the-complete-guide-to-building-skills-for-claude-01krv8epdjta6664ek10fvp7tz|The Complete Guide To Building Skills For Claude]])
- A skill is a set of instructions - packaged as a simple folder - that teaches Claude how to handle specific tasks or workflows. Skills are one of the most powerful ways to customize Claude for your specific needs. Instead of re-explaining your preferences, processes, and domain expertise in every conversation, skills let you teach Claude once and benefit every time. (`64dea8c17f0b` · supporting · supporting_snippet; [[sources/the-complete-guide-to-building-skills-for-claude-01krv8epdjta6664ek10fvp7tz|The Complete Guide To Building Skills For Claude]])
- The guide treats the suggested success thresholds as rough benchmarks, not hard standards. Some measurement advice is explicitly described as aspirational, so the procedure is operationally useful but not a rigorous evaluation framework. Skills can also fail for simple packaging mistakes like a misnamed SKILL.md or invalid frontmatter. (`9d3cf21ccf55` · uncertainty · caveats; [[sources/the-complete-guide-to-building-skills-for-claude-01krv8epdjta6664ek10fvp7tz|The Complete Guide To Building Skills For Claude]])

### Your Obsidian Vault Is a Knowledge Graph. Here’s How to Make It Think (quickly). (2026-04-14)

- Start by running Claude Code from the vault root and let it generate a starter CLAUDE.md. Then rewrite that file to describe your folder structure, note conventions, and things the agent must never touch. Add explicit instructions for where drafts should go and what context it should use for synthesis. Install the Obsidian skills package so Claude learns the vault-specific file grammar, including wikilinks and callouts. Keep the active context section fresh before each session so the agent does not work from stale priorities. (`a60c3b177906` · neutral · answer_summary; [[sources/your-obsidian-vault-is-a-knowledge-graph-here-s-how-to-make-it-think-quickly-01kqm1b1r3e33mym3vd0d08wbn|Your Obsidian Vault Is a Knowledge Graph. Here’s How to Make It Think (quickly).]])
- Run Claude Code in the vault root. (`2c8614a45291` · neutral · implementation_steps[0]; [[sources/your-obsidian-vault-is-a-knowledge-graph-here-s-how-to-make-it-think-quickly-01kqm1b1r3e33mym3vd0d08wbn|Your Obsidian Vault Is a Knowledge Graph. Here’s How to Make It Think (quickly).]])
- Use /init to generate a first-pass CLAUDE.md. (`c217e44c98aa` · neutral · implementation_steps[1]; [[sources/your-obsidian-vault-is-a-knowledge-graph-here-s-how-to-make-it-think-quickly-01kqm1b1r3e33mym3vd0d08wbn|Your Obsidian Vault Is a Knowledge Graph. Here’s How to Make It Think (quickly).]])
- Rewrite CLAUDE.md with vault structure, conventions, and safety rules. (`76aa84b8c4bb` · neutral · implementation_steps[2]; [[sources/your-obsidian-vault-is-a-knowledge-graph-here-s-how-to-make-it-think-quickly-01kqm1b1r3e33mym3vd0d08wbn|Your Obsidian Vault Is a Knowledge Graph. Here’s How to Make It Think (quickly).]])
- Install Obsidian skills with npx skills add git@github.com:kepano/obsidian-skills.git. (`4e125d4fc8b2` · neutral · implementation_steps[3]; [[sources/your-obsidian-vault-is-a-knowledge-graph-here-s-how-to-make-it-think-quickly-01kqm1b1r3e33mym3vd0d08wbn|Your Obsidian Vault Is a Knowledge Graph. Here’s How to Make It Think (quickly).]])
- Update the active context before each session. (`623044ade9b1` · neutral · implementation_steps[4]; [[sources/your-obsidian-vault-is-a-knowledge-graph-here-s-how-to-make-it-think-quickly-01kqm1b1r3e33mym3vd0d08wbn|Your Obsidian Vault Is a Knowledge Graph. Here’s How to Make It Think (quickly).]])
- Optionally ask Claude to append a short session log at the end of each session. (`0d8565c025a7` · neutral · implementation_steps[5]; [[sources/your-obsidian-vault-is-a-knowledge-graph-here-s-how-to-make-it-think-quickly-01kqm1b1r3e33mym3vd0d08wbn|Your Obsidian Vault Is a Knowledge Graph. Here’s How to Make It Think (quickly).]])
- A local Obsidian vault with a known folder structure. (`2b7293186909` · neutral · prerequisites[0]; [[sources/your-obsidian-vault-is-a-knowledge-graph-here-s-how-to-make-it-think-quickly-01kqm1b1r3e33mym3vd0d08wbn|Your Obsidian Vault Is a Knowledge Graph. Here’s How to Make It Think (quickly).]])
- Claude Code installed and runnable from the terminal. (`72180954763a` · neutral · prerequisites[1]; [[sources/your-obsidian-vault-is-a-knowledge-graph-here-s-how-to-make-it-think-quickly-01kqm1b1r3e33mym3vd0d08wbn|Your Obsidian Vault Is a Knowledge Graph. Here’s How to Make It Think (quickly).]])
- A willingness to maintain a root CLAUDE.md file over time. (`aceafde2b0ad` · neutral · prerequisites[2]; [[sources/your-obsidian-vault-is-a-knowledge-graph-here-s-how-to-make-it-think-quickly-01kqm1b1r3e33mym3vd0d08wbn|Your Obsidian Vault Is a Knowledge Graph. Here’s How to Make It Think (quickly).]])
- This is about preparing a Claude Code environment so it understands the structure and conventions of an Obsidian vault. The problem is that a capable agent can still misread markdown, ignore vault-specific syntax, or make unsafe edits if it is not taught the local file grammar and rules. The setup gives the agent a shared vocabulary for wikilinks, callouts, templates, and folder conventions. It also reduces the chance of it treating vault content like generic text instead of a structured knowledge base. (`0a3a84edf591` · neutral · what_and_problem; [[sources/your-obsidian-vault-is-a-knowledge-graph-here-s-how-to-make-it-think-quickly-01kqm1b1r3e33mym3vd0d08wbn|Your Obsidian Vault Is a Knowledge Graph. Here’s How to Make It Think (quickly).]])
- "I run /init the first time, which generates a starting point by scanning my vault structure. Then I rewrite it heavily." (`4cc24be4e9f0` · supporting · supporting_snippet; [[sources/your-obsidian-vault-is-a-knowledge-graph-here-s-how-to-make-it-think-quickly-01kqm1b1r3e33mym3vd0d08wbn|Your Obsidian Vault Is a Knowledge Graph. Here’s How to Make It Think (quickly).]])
- The generated file is only a starting point; without manual rewriting, it will miss the conventions that matter. Stale active context can make the agent pursue old priorities. Negative instructions matter because the agent may otherwise modify folders that should remain untouched. (`20542c5704ab` · uncertainty · caveats; [[sources/your-obsidian-vault-is-a-knowledge-graph-here-s-how-to-make-it-think-quickly-01kqm1b1r3e33mym3vd0d08wbn|Your Obsidian Vault Is a Knowledge Graph. Here’s How to Make It Think (quickly).]])

## Contradictions / tensions

- The guide treats the suggested success thresholds as rough benchmarks, not hard standards. Some measurement advice is explicitly described as aspirational, so the procedure is operationally useful but not a rigorous evaluation framework. Skills can also fail for simple packaging mistakes like a misnamed SKILL.md or invalid frontmatter. (uncertainty; [[sources/the-complete-guide-to-building-skills-for-claude-01krv8epdjta6664ek10fvp7tz|The Complete Guide To Building Skills For Claude]])
- The source stresses that metadata accuracy matters a lot, so weak or vague descriptions can reduce matching accuracy. It also recommends keeping SKILL.md under 500 lines, which means large workflows need deliberate file splitting. The article is explanatory rather than tested, so production reliability, governance, and security are not demonstrated here. (uncertainty; [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]])
- The generated file is only a starting point; without manual rewriting, it will miss the conventions that matter. Stale active context can make the agent pursue old priorities. Negative instructions matter because the agent may otherwise modify folders that should remain untouched. (uncertainty; [[sources/your-obsidian-vault-is-a-knowledge-graph-here-s-how-to-make-it-think-quickly-01kqm1b1r3e33mym3vd0d08wbn|Your Obsidian Vault Is a Knowledge Graph. Here’s How to Make It Think (quickly).]])

## Related pages

- [[how-to/context-compaction|Context Compaction]]
- [[how-to/self-verification-for-agent-workflows|Self-Verification for Agent Workflows]]
- [[how-to/local-model-setup|Local Model Setup]]
- [[how-to/agent-maintained-knowledge-bases|Agent-Maintained Knowledge Bases]]

## Sources

- [[sources/how-to-build-claude-skills-2-0-better-than-99-of-people-01kqfzngwjk9z6mbkcj9yx6tfn|How to build Claude Skills 2.0 Better than 99% of People]]
- [[sources/the-complete-guide-to-building-skills-for-claude-01krv8epdjta6664ek10fvp7tz|The Complete Guide To Building Skills For Claude]]
- [[sources/your-obsidian-vault-is-a-knowledge-graph-here-s-how-to-make-it-think-quickly-01kqm1b1r3e33mym3vd0d08wbn|Your Obsidian Vault Is a Knowledge Graph. Here’s How to Make It Think (quickly).]]
