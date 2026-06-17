---
title: Agentic Coding Workflows
slug: agentic-coding-workflows
entity_id: topic:agentic-coding-workflows
category: topic
tags:
- agent-orchestration
- agent-systems
- ai-assisted-development
- ai-engineering
- ai-evaluation
- coding-agents
- human-ai-workflows
- software-engineering
- test-and-verification
- workflow-design
first_seen: '2026-03-18'
last_seen: '2026-06-08'
source_count: 8
evidence_count: 61
source_ids:
- agentic-coding-is-a-trap-01krv8ckkgpcbaz9tn6ryd5vy9
- ai-s-second-moment-the-explosion-that-changed-everything-01kr4pq886wnqdq05t20rejy0f
- domain-expertise-has-always-been-the-real-moat-01ktjz6cyb7sg9znxh03mrzw1v
- if-ai-writes-your-code-why-use-python-01krbncwpakyz5n828c0p8fnfg
- introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1
- setting-up-mac-for-development-may-2026-01ktpm1xqjsx1ra42yp56bera0
- why-i-stopped-using-gemma-4-and-switched-to-qwen-3-6-01kqm05wc7wq68ypednrdcpa0b
- wtf-is-a-loop-peter-steinberger-vs-boris-cherny-01kv4td5axnc0n0j86fd9vgxm9
value_level: high
confidence: 0.92625
synthesis_state: stage1-placeholder
---

# Agentic Coding Workflows

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Agentic coding workflows move implementation work from direct authoring toward delegated generation, with a human acting as planner, reviewer, and controller. They can increase throughput, but they also increase the distance between the developer and the code, which can make errors harder to spot and understanding harder to maintain. In practice, the workflow changes the unit of work from writing code to supervising generated code, splitting effort across planning, review, and repeated revision loops. The main operational question is not whether agents can generate code, but how much comprehension a human retains while relying on them.

## Key Points

- Supervision quality depends on the same coding judgment that overuse may weaken.
- Review-only loops can reduce learning because they remove the friction of writing, debugging, and refactoring code directly.
- Agentic workflows often shift effort into planning, repeated prompting, and code review rather than eliminating work.
- The pattern creates a structural trade-off between speed and retained comprehension.
- Long-horizon task completion is more important than single-turn code completion for real productivity gains.
- Error recovery without human intervention is a key threshold for practical agentic coding.
- Architectural consistency across many files is a distinguishing capability, not just local code generation.
- Human value shifts toward decomposition, oversight, and knowing which outputs are subtly wrong.
- Long-horizon coding tasks require sustained planning and execution, not just a strong first answer.
- Terminal and harness behavior can matter as much as model quality for real coding success.
- Cost and latency need to be evaluated against the full action sequence, not only against token price.
- A model can be acceptable in chat and still fail inside an agent loop.
- Task completion depends on tool discipline, state management, and error recovery.
- One-shot coding benchmarks do not capture the full difficulty of agentic execution.
- Agent output is easier to trust when the language and toolchain provide fast compile-check or test feedback.
- Human work shifts toward system design, task decomposition, and review of generated changes.
- Language migrations become more feasible when agents can execute many small edits and validations.
- Large code generation tasks are operationally bounded by supervision and verification, not just model capability.
- Parallel worktrees let multiple agents operate without colliding on the same branch.
- Human review remains important even when the agent does most of the implementation.
- The most useful agent setup is often repository-local rather than chat-first.
- Pre-agent programming tied code production to deep domain understanding; agentic tools decouple those steps.
- Generated code can pass tests and still be wrong if the tests do not encode the right domain rule.
- The best outcomes come from combining code-generation help with human review that knows the target domain.
- In high-stakes domains, the engineering bottleneck becomes correctness judgment rather than typing speed.
- A coding loop can read model output, test it, and re-prompt until the task is done.
- The loop becomes the unit of work, while the model becomes a subroutine.
- Verification and halting rules are central to making the workflow trustworthy.
- Reusable skills inside the loop compound value better than repeated free-form prompting.

## Operational Insight

Keep enough manual implementation in the loop to preserve debugging skill and architectural understanding; treat delegation as a bounded aid, not the default production path.

## Related Topics

- approval-based-coding-workflows
- harness-decay
- agent-runtime-architecture
- agent-runtime-architecture-for-voice
- verification-loops-in-ai-workflows
- tool-discipline-in-agent-loops
- workflow-restructuring-around-ai-agents
- domain-expertise-as-verification

## Evidence / supporting sources

### Agentic Coding is a Trap (undated)

- Agentic coding workflows move implementation work from direct authoring toward delegated generation, with a human acting as planner, reviewer, and controller. They can increase throughput, but they also increase the distance between the developer and the code, which can make errors harder to spot and understanding harder to maintain. In practice, the workflow changes the unit of work from writing code to supervising generated code, splitting effort across planning, review, and repeated revision loops. The main operational question is not whether agents can generate code, but how much comprehension a human retains while relying on them. (`ba31d78935d8` · neutral · knowledge_summary; [[sources/agentic-coding-is-a-trap-01krv8ckkgpcbaz9tn6ryd5vy9|Agentic Coding is a Trap]])
- Keep enough manual implementation in the loop to preserve debugging skill and architectural understanding; treat delegation as a bounded aid, not the default production path. (`645d7483a741` · neutral · operational_insight; [[sources/agentic-coding-is-a-trap-01krv8ckkgpcbaz9tn6ryd5vy9|Agentic Coding is a Trap]])
- This is a durable pattern in AI-assisted software engineering as of the article's publication date: teams increasingly blend direct coding with generated implementation, review, and orchestration. The operational issue is how to preserve human understanding, debugging ability, and review quality while still capturing productivity gains. (`18934fa9c30a` · neutral · relevance_note; [[sources/agentic-coding-is-a-trap-01krv8ckkgpcbaz9tn6ryd5vy9|Agentic Coding is a Trap]])
- Supervision quality depends on the same coding judgment that overuse may weaken. (`6bdc6887ba95` · supporting · key_points[0]; [[sources/agentic-coding-is-a-trap-01krv8ckkgpcbaz9tn6ryd5vy9|Agentic Coding is a Trap]])
- Review-only loops can reduce learning because they remove the friction of writing, debugging, and refactoring code directly. (`8fc01aa8df18` · supporting · key_points[1]; [[sources/agentic-coding-is-a-trap-01krv8ckkgpcbaz9tn6ryd5vy9|Agentic Coding is a Trap]])
- Agentic workflows often shift effort into planning, repeated prompting, and code review rather than eliminating work. (`59613776e23d` · supporting · key_points[2]; [[sources/agentic-coding-is-a-trap-01krv8ckkgpcbaz9tn6ryd5vy9|Agentic Coding is a Trap]])
- The pattern creates a structural trade-off between speed and retained comprehension. (`4dae0053f57c` · supporting · key_points[3]; [[sources/agentic-coding-is-a-trap-01krv8ckkgpcbaz9tn6ryd5vy9|Agentic Coding is a Trap]])
- "You generate a plan, and disconnect from writing any code. The agents know better, and handle all the implementation." (`30d300716e18` · supporting · supporting_snippet; [[sources/agentic-coding-is-a-trap-01krv8ckkgpcbaz9tn6ryd5vy9|Agentic Coding is a Trap]])

### AI’s Second Moment: The Explosion That Changed Everything (2026-03-18)

- Agentic coding workflows shift the programmer’s role from typing code line by line to supervising agents that plan, edit, test, and revise code over longer tasks. The durable operational change is not just faster code generation; it is a different division of labor where human judgment, architecture, and review become more important than manual implementation. These workflows depend on the agent’s ability to maintain context, recover from errors, and keep architectural consistency across a large task. They also create new failure modes around oversight quality, because productivity gains depend on the operator knowing when the agent is subtly wrong. (`793dcea22a96` · neutral · knowledge_summary; [[sources/ai-s-second-moment-the-explosion-that-changed-everything-01kr4pq886wnqdq05t20rejy0f|AI’s Second Moment: The Explosion That Changed Everything]])
- Use AI coding tools as a supervised execution layer for well-scoped work, not as an excuse to remove design discipline. The highest leverage goes to practitioners who can break problems down, verify outputs, and guide the agent through iterative correction. (`06d71289589f` · neutral · operational_insight; [[sources/ai-s-second-moment-the-explosion-that-changed-everything-01kr4pq886wnqdq05t20rejy0f|AI’s Second Moment: The Explosion That Changed Everything]])
- As of 2026-03-18, this pattern matters because many AI-assisted development stacks are moving from suggestion engines toward supervised execution loops. That affects how teams structure reviews, assign work, and evaluate whether a developer can direct an agent effectively. (`a8f6f70e25f0` · neutral · relevance_note; [[sources/ai-s-second-moment-the-explosion-that-changed-everything-01kr4pq886wnqdq05t20rejy0f|AI’s Second Moment: The Explosion That Changed Everything]])
- Long-horizon task completion is more important than single-turn code completion for real productivity gains. (`c06f5b137266` · supporting · key_points[0]; [[sources/ai-s-second-moment-the-explosion-that-changed-everything-01kr4pq886wnqdq05t20rejy0f|AI’s Second Moment: The Explosion That Changed Everything]])
- Error recovery without human intervention is a key threshold for practical agentic coding. (`46670a780756` · supporting · key_points[1]; [[sources/ai-s-second-moment-the-explosion-that-changed-everything-01kr4pq886wnqdq05t20rejy0f|AI’s Second Moment: The Explosion That Changed Everything]])
- Architectural consistency across many files is a distinguishing capability, not just local code generation. (`f10765f24a9e` · supporting · key_points[2]; [[sources/ai-s-second-moment-the-explosion-that-changed-everything-01kr4pq886wnqdq05t20rejy0f|AI’s Second Moment: The Explosion That Changed Everything]])
- Human value shifts toward decomposition, oversight, and knowing which outputs are subtly wrong. (`b1ad9b7d6024` · supporting · key_points[3]; [[sources/ai-s-second-moment-the-explosion-that-changed-everything-01kr4pq886wnqdq05t20rejy0f|AI’s Second Moment: The Explosion That Changed Everything]])
- Karpathy pinpointed what changed. “LLM agent capabilities (Claude and Codex especially) have crossed some kind of threshold of coherence around December 2025 and caused a phase shift in software engineering,” he wrote. The models did not just get smarter. They gained the ability to hold context over long tasks, recover from errors without human intervention, and maintain architectural consistency across thousands of lines of code. (`9c3b41abd2c0` · supporting · supporting_snippet; [[sources/ai-s-second-moment-the-explosion-that-changed-everything-01kr4pq886wnqdq05t20rejy0f|AI’s Second Moment: The Explosion That Changed Everything]])

### Domain Expertise Has Always Been the Real Moat (2026-05-30)

- Agentic coding changes software production by separating code generation from code verification. The model can draft the implementation, but a human still has to decide whether the output matches the real-world requirement. This shifts engineering value toward review, testing, and domain-aware validation rather than pure code-writing speed. The pattern is especially important when the system is used in environments where incorrect outputs can compile cleanly yet still fail operationally. (`16fd6f3b436c` · neutral · knowledge_summary; [[sources/domain-expertise-has-always-been-the-real-moat-01ktjz6cyb7sg9znxh03mrzw1v|Domain Expertise Has Always Been the Real Moat]])
- Design coding workflows so the agent produces drafts and the human owns correctness. The workflow should force explicit checks for domain constraints, not just syntax, tests, or compile success. (`0c9590983937` · neutral · operational_insight; [[sources/domain-expertise-has-always-been-the-real-moat-01ktjz6cyb7sg9znxh03mrzw1v|Domain Expertise Has Always Been the Real Moat]])
- Durable as of 2026-05-30: as code generation gets cheaper, the bottleneck in many agentic coding setups moves toward verification and domain review. That is highly relevant for AI-assisted development, where a working build can still encode the wrong business rule. (`8e0878b9c5d9` · neutral · relevance_note; [[sources/domain-expertise-has-always-been-the-real-moat-01ktjz6cyb7sg9znxh03mrzw1v|Domain Expertise Has Always Been the Real Moat]])
- Pre-agent programming tied code production to deep domain understanding; agentic tools decouple those steps. (`95067094134e` · supporting · key_points[0]; [[sources/domain-expertise-has-always-been-the-real-moat-01ktjz6cyb7sg9znxh03mrzw1v|Domain Expertise Has Always Been the Real Moat]])
- Generated code can pass tests and still be wrong if the tests do not encode the right domain rule. (`7d9e3a3688ab` · supporting · key_points[1]; [[sources/domain-expertise-has-always-been-the-real-moat-01ktjz6cyb7sg9znxh03mrzw1v|Domain Expertise Has Always Been the Real Moat]])
- The best outcomes come from combining code-generation help with human review that knows the target domain. (`db92d5553e26` · supporting · key_points[2]; [[sources/domain-expertise-has-always-been-the-real-moat-01ktjz6cyb7sg9znxh03mrzw1v|Domain Expertise Has Always Been the Real Moat]])
- In high-stakes domains, the engineering bottleneck becomes correctness judgment rather than typing speed. (`7d983623504c` · supporting · key_points[3]; [[sources/domain-expertise-has-always-been-the-real-moat-01ktjz6cyb7sg9znxh03mrzw1v|Domain Expertise Has Always Been the Real Moat]])
- "The code was a transcription of that understanding. Acquiring the understanding was the job." (`94efb8b25a38` · supporting · supporting_snippet; [[sources/domain-expertise-has-always-been-the-real-moat-01ktjz6cyb7sg9znxh03mrzw1v|Domain Expertise Has Always Been the Real Moat]])

### If AI Writes Your Code, Why Use Python? (2026-04-28)

- Software development workflows can shift from direct human typing to supervising agents that generate, port, and verify code. In that setup, the human spends more time on architecture, prompt constraints, and review than on line-by-line implementation. Strong compile-and-test feedback loops become especially valuable because they help agents self-correct while they work. The pattern is most relevant when large code changes, language migrations, or systems programming tasks can be decomposed into small reviewable steps. (`0aa51bcda63c` · neutral · knowledge_summary; [[sources/if-ai-writes-your-code-why-use-python-01krbncwpakyz5n828c0p8fnfg|If AI Writes Your Code, Why Use Python?]])
- For agent-assisted coding, favor languages and build loops that give fast, precise feedback to the model and the reviewer. The practical bottleneck moves from raw typing speed to supervision quality, test coverage, and the ease of validating incremental changes. (`54def2982527` · neutral · operational_insight; [[sources/if-ai-writes-your-code-why-use-python-01krbncwpakyz5n828c0p8fnfg|If AI Writes Your Code, Why Use Python?]])
- Durable for AI-assisted software delivery as of 2026-04-28: teams using coding agents need workflows that optimize review, verification, and decomposition rather than just developer typing speed. This matters most in service automation and internal tooling where large changes can be broken into agent-sized tasks. (`58885bbe913d` · neutral · relevance_note; [[sources/if-ai-writes-your-code-why-use-python-01krbncwpakyz5n828c0p8fnfg|If AI Writes Your Code, Why Use Python?]])
- Agent output is easier to trust when the language and toolchain provide fast compile-check or test feedback. (`7c41dea9f456` · supporting · key_points[0]; [[sources/if-ai-writes-your-code-why-use-python-01krbncwpakyz5n828c0p8fnfg|If AI Writes Your Code, Why Use Python?]])
- Human work shifts toward system design, task decomposition, and review of generated changes. (`18b2a2463824` · supporting · key_points[1]; [[sources/if-ai-writes-your-code-why-use-python-01krbncwpakyz5n828c0p8fnfg|If AI Writes Your Code, Why Use Python?]])
- Language migrations become more feasible when agents can execute many small edits and validations. (`6c386c62b9f9` · supporting · key_points[2]; [[sources/if-ai-writes-your-code-why-use-python-01krbncwpakyz5n828c0p8fnfg|If AI Writes Your Code, Why Use Python?]])
- Large code generation tasks are operationally bounded by supervision and verification, not just model capability. (`98f639f55bd1` · supporting · key_points[3]; [[sources/if-ai-writes-your-code-why-use-python-01krbncwpakyz5n828c0p8fnfg|If AI Writes Your Code, Why Use Python?]])
- "The human's job shifted from 'writing the code' to 'architecting the system and reviewing the output.'" (`99a7d97ee434` · supporting · supporting_snippet; [[sources/if-ai-writes-your-code-why-use-python-01krbncwpakyz5n828c0p8fnfg|If AI Writes Your Code, Why Use Python?]])

### Introducing Composer 2 (2026-03-19)

- Agentic coding workflows treat software development as a multi-step execution problem rather than a single completion task. The model or tool has to plan, act, inspect intermediate results, and continue across many actions. This makes terminal interaction, tool use, and long-horizon stability more important than short-form code generation alone. Evaluation should therefore focus on task completion across extended trajectories, not only on one-shot code snippets. (`b229f579a2b8` · neutral · knowledge_summary; [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]])
- When evaluating coding agents, measure long task trajectories, retries, and terminal-side success, because short benchmark wins can hide poor multi-step behavior. Systems that can keep working through hundreds of actions are more relevant for real developer automation than models optimized only for isolated completions. (`7598d1403fc8` · neutral · operational_insight; [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]])
- Agentic coding workflows remain relevant as development assistants take on longer sequences of edits, terminal commands, and verification steps. As of 2026-03-19, the durable lesson is that multi-step execution quality is a first-class design concern for coding agents, especially in IDEs and terminal-based automation. (`132e15fb99e6` · neutral · relevance_note; [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]])
- Long-horizon coding tasks require sustained planning and execution, not just a strong first answer. (`d4a5ef3d5d7c` · supporting · key_points[0]; [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]])
- Terminal and harness behavior can matter as much as model quality for real coding success. (`c48965ce27c0` · supporting · key_points[1]; [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]])
- Cost and latency need to be evaluated against the full action sequence, not only against token price. (`e5a5537ff7f2` · supporting · key_points[2]; [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]])
- "Composer 2 is able to solve challenging tasks requiring hundreds of actions." (`e7cc1100b484` · supporting · supporting_snippet; [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]])

### Setting Up Mac for Development [May 2026] (2026-05-20)

- Agentic coding workflows organize software development around AI agents that produce, modify, and review code inside a broader human-supervised process. The practical unit is not a single prompt but a loop: assign work, let the agent operate, inspect the diff, and decide whether to continue or intervene. These workflows often rely on repository-local context, branch isolation, and tooling integration so that multiple tasks can run in parallel without stepping on each other. They are especially useful when the work can be delegated in chunks but still needs human review before merge or release. (`52033f65cc82` · neutral · knowledge_summary; [[sources/setting-up-mac-for-development-may-2026-01ktpm1xqjsx1ra42yp56bera0|Setting Up Mac for Development [May 2026]]])
- Treat the agent as a collaborator that works on isolated branches or worktrees, not as a magical autopilot. The workflow becomes much more effective when the review surface is simple and the human can inspect exact code changes before accepting them. (`aedab1d3ff0b` · neutral · operational_insight; [[sources/setting-up-mac-for-development-may-2026-01ktpm1xqjsx1ra42yp56bera0|Setting Up Mac for Development [May 2026]]])
- This pattern is durable because coding agents are most useful when embedded in a supervised development loop. It matters for AI engineering and service automation teams that need controlled execution, reviewable changes, and parallel task handling rather than opaque autonomous behavior. (`a779e449dc3f` · neutral · relevance_note; [[sources/setting-up-mac-for-development-may-2026-01ktpm1xqjsx1ra42yp56bera0|Setting Up Mac for Development [May 2026]]])
- Parallel worktrees let multiple agents operate without colliding on the same branch. (`d6c83358df2f` · supporting · key_points[0]; [[sources/setting-up-mac-for-development-may-2026-01ktpm1xqjsx1ra42yp56bera0|Setting Up Mac for Development [May 2026]]])
- Human review remains important even when the agent does most of the implementation. (`4b462d66d9b6` · supporting · key_points[1]; [[sources/setting-up-mac-for-development-may-2026-01ktpm1xqjsx1ra42yp56bera0|Setting Up Mac for Development [May 2026]]])
- The most useful agent setup is often repository-local rather than chat-first. (`c9bf801cd2eb` · supporting · key_points[2]; [[sources/setting-up-mac-for-development-may-2026-01ktpm1xqjsx1ra42yp56bera0|Setting Up Mac for Development [May 2026]]])
- "Codex for long, delegated work. Parallel worktrees, multiple agents on different branches" and "The wt helper became essential once I started running multiple agents in parallel. Each one gets its own worktree." (`a5eb8c757cd0` · supporting · supporting_snippet; [[sources/setting-up-mac-for-development-may-2026-01ktpm1xqjsx1ra42yp56bera0|Setting Up Mac for Development [May 2026]]])

### Why I Stopped Using Gemma 4 and Switched to Qwen 3.6 (2026-04-25)

- Agentic coding workflows are software-development loops where a model does more than answer a prompt: it reads files, calls tools, edits code, runs checks, and recovers from mistakes across multiple turns. These workflows place a premium on state tracking, tool discipline, and stopping behavior, because the hard part is often not code generation but completing the task without looping or losing context. Single-turn benchmark performance can be a weak proxy for this kind of work. Practical evaluation should emphasize end-to-end task completion, error recovery, and correct tool sequencing. (`b328243af783` · neutral · knowledge_summary; [[sources/why-i-stopped-using-gemma-4-and-switched-to-qwen-3-6-01kqm05wc7wq68ypednrdcpa0b|Why I Stopped Using Gemma 4 and Switched to Qwen 3.6]])
- Judge coding models by whether they can finish a multi-step task inside an execution loop, not by whether they sound smart in chat. The source's CSV example shows why tool discipline and self-recovery matter more than fluent output. (`16b50dbee9d8` · neutral · operational_insight; [[sources/why-i-stopped-using-gemma-4-and-switched-to-qwen-3-6-01kqm05wc7wq68ypednrdcpa0b|Why I Stopped Using Gemma 4 and Switched to Qwen 3.6]])
- This matters for any engineering team building code assistants, repo agents, or terminal-based automation because the failure mode is usually orchestration, not syntax. As of 2026-04-25, the durable lesson is that agentic coding needs workflow-level evaluation and harness design, not just prompt tuning. (`bd6bf8beb3eb` · neutral · relevance_note; [[sources/why-i-stopped-using-gemma-4-and-switched-to-qwen-3-6-01kqm05wc7wq68ypednrdcpa0b|Why I Stopped Using Gemma 4 and Switched to Qwen 3.6]])
- A model can be acceptable in chat and still fail inside an agent loop. (`06ba119bc4de` · supporting · key_points[0]; [[sources/why-i-stopped-using-gemma-4-and-switched-to-qwen-3-6-01kqm05wc7wq68ypednrdcpa0b|Why I Stopped Using Gemma 4 and Switched to Qwen 3.6]])
- Task completion depends on tool discipline, state management, and error recovery. (`11cdbc033e0d` · supporting · key_points[1]; [[sources/why-i-stopped-using-gemma-4-and-switched-to-qwen-3-6-01kqm05wc7wq68ypednrdcpa0b|Why I Stopped Using Gemma 4 and Switched to Qwen 3.6]])
- One-shot coding benchmarks do not capture the full difficulty of agentic execution. (`d89b92cd17fd` · supporting · key_points[2]; [[sources/why-i-stopped-using-gemma-4-and-switched-to-qwen-3-6-01kqm05wc7wq68ypednrdcpa0b|Why I Stopped Using Gemma 4 and Switched to Qwen 3.6]])
- "Agent work is not that. Agent work is twenty turns of tool calls, state management, and recovery from errors." (`dcf2a9fc7dee` · supporting · supporting_snippet; [[sources/why-i-stopped-using-gemma-4-and-switched-to-qwen-3-6-01kqm05wc7wq68ypednrdcpa0b|Why I Stopped Using Gemma 4 and Switched to Qwen 3.6]])

### WTF Is a Loop? Peter Steinberger vs. Boris Cherny (2026-06-08)

- Agentic coding workflows are setups where a model does not just answer prompts, but participates in a larger program that iterates on code, checks results, and decides whether to continue. The important shift is from one-off prompting to a repeatable control flow with explicit stopping conditions, verification, and reuse of intermediate work. These workflows become more useful when the loop is backed by durable state and tested skills rather than ad hoc prompting. They are especially relevant when code generation, review, and repair need to run with limited human attention. (`1c74c7321614` · neutral · knowledge_summary; [[sources/wtf-is-a-loop-peter-steinberger-vs-boris-cherny-01kv4td5axnc0n0j86fd9vgxm9|WTF Is a Loop? Peter Steinberger vs. Boris Cherny]])
- Treat the model as one step inside a managed workflow, not as the workflow itself. The control logic, feedback checks, and halting rules are the real engineering surface. (`0ba987116890` · neutral · operational_insight; [[sources/wtf-is-a-loop-peter-steinberger-vs-boris-cherny-01kv4td5axnc0n0j86fd9vgxm9|WTF Is a Loop? Peter Steinberger vs. Boris Cherny]])
- This is a durable pattern for AI-assisted development and service automation because many production tasks need iteration, validation, and safe stopping rather than a single prompt. It matters wherever teams want agents to make code changes, review output, or run maintenance tasks with limited supervision. (`b2193e75c9d6` · neutral · relevance_note; [[sources/wtf-is-a-loop-peter-steinberger-vs-boris-cherny-01kv4td5axnc0n0j86fd9vgxm9|WTF Is a Loop? Peter Steinberger vs. Boris Cherny]])
- A coding loop can read model output, test it, and re-prompt until the task is done. (`e8901ad513b4` · supporting · key_points[0]; [[sources/wtf-is-a-loop-peter-steinberger-vs-boris-cherny-01kv4td5axnc0n0j86fd9vgxm9|WTF Is a Loop? Peter Steinberger vs. Boris Cherny]])
- The loop becomes the unit of work, while the model becomes a subroutine. (`3cad3cae0540` · supporting · key_points[1]; [[sources/wtf-is-a-loop-peter-steinberger-vs-boris-cherny-01kv4td5axnc0n0j86fd9vgxm9|WTF Is a Loop? Peter Steinberger vs. Boris Cherny]])
- Verification and halting rules are central to making the workflow trustworthy. (`b7f92ffd9844` · supporting · key_points[2]; [[sources/wtf-is-a-loop-peter-steinberger-vs-boris-cherny-01kv4td5axnc0n0j86fd9vgxm9|WTF Is a Loop? Peter Steinberger vs. Boris Cherny]])
- Reusable skills inside the loop compound value better than repeated free-form prompting. (`7cba4073dac0` · supporting · key_points[3]; [[sources/wtf-is-a-loop-peter-steinberger-vs-boris-cherny-01kv4td5axnc0n0j86fd9vgxm9|WTF Is a Loop? Peter Steinberger vs. Boris Cherny]])
- “A loop is a small program you write that prompts the coding agent for you, reads what it produced, decides whether it is done, and if not, prompts it again.” (`ce45916d088b` · supporting · supporting_snippet; [[sources/wtf-is-a-loop-peter-steinberger-vs-boris-cherny-01kv4td5axnc0n0j86fd9vgxm9|WTF Is a Loop? Peter Steinberger vs. Boris Cherny]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- agent-runtime-architecture
- agent-runtime-architecture-for-voice
- approval-based-coding-workflows
- domain-expertise-as-verification
- harness-decay
- tool-discipline-in-agent-loops
- verification-loops-in-ai-workflows
- workflow-restructuring-around-ai-agents

## Sources

- [[sources/agentic-coding-is-a-trap-01krv8ckkgpcbaz9tn6ryd5vy9|Agentic Coding is a Trap]]
- [[sources/ai-s-second-moment-the-explosion-that-changed-everything-01kr4pq886wnqdq05t20rejy0f|AI’s Second Moment: The Explosion That Changed Everything]]
- [[sources/domain-expertise-has-always-been-the-real-moat-01ktjz6cyb7sg9znxh03mrzw1v|Domain Expertise Has Always Been the Real Moat]]
- [[sources/if-ai-writes-your-code-why-use-python-01krbncwpakyz5n828c0p8fnfg|If AI Writes Your Code, Why Use Python?]]
- [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]]
- [[sources/setting-up-mac-for-development-may-2026-01ktpm1xqjsx1ra42yp56bera0|Setting Up Mac for Development [May 2026]]]
- [[sources/why-i-stopped-using-gemma-4-and-switched-to-qwen-3-6-01kqm05wc7wq68ypednrdcpa0b|Why I Stopped Using Gemma 4 and Switched to Qwen 3.6]]
- [[sources/wtf-is-a-loop-peter-steinberger-vs-boris-cherny-01kv4td5axnc0n0j86fd9vgxm9|WTF Is a Loop? Peter Steinberger vs. Boris Cherny]]
