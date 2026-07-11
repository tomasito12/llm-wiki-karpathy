---
title: How to Make Claude Code Validate its own Work
slug: how-to-make-claude-code-validate-its-own-work-01krkb42j4y9839773m7rz83xe
category: source
tags:
- agent-evals
- agent-orchestration
- agentic
- automation-supervision
- browser-use
- cli-tool
- coding
- coding-agents
- multimodal-ai
- test-and-verification
- tool-use
- ui-generation
- verification-over-principles
- verification-systems
- visual-specifications
- workflow-based-evaluation
- workflow-design
source_id: how-to-make-claude-code-validate-its-own-work-01krkb42j4y9839773m7rz83xe
author: Eivind Kjosbakken
publication: Medium
published_date: '2026-05-05'
assessed_as_of: '2026-05-05'
ingested_at: '2026-06-02T20:21:28.458586+00:00'
canonical_url: https://towardsdatascience.com/how-to-make-claude-code-validate-its-own-work/?utm_campaign=tds%20variable&utm_medium=email&_hsenc=p2ANqtz-983i5IEFCGSE-P3c2Jm_8BItpnyWH-44FiF0Jaq6ncB_r2wi2b8socrX_9XHnImlvp31VqD0tsty1czZcJ4NV54cmKLQ&_hsmi=418698396&utm_source=newsletter
content_sha256: 5eacc8d04a25802f212a38676f70d13b2732869de087b065a211721005fd4da5
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
derived_how_to:
- how-to/self-verification-for-agent-workflows.md
derived_tools:
- tools/claude-code.md
derived_topics:
- topics/agent-self-verification.md
- topics/visual-specifications-for-ai-systems.md
derived_trends:
- industry-trends/verification-loops-become-central-to-ai-workflows.md
derived_pages:
- how-to/self-verification-for-agent-workflows.md
- industry-trends/verification-loops-become-central-to-ai-workflows.md
- tools/claude-code.md
- topics/agent-self-verification.md
- topics/visual-specifications-for-ai-systems.md
---

# How to Make Claude Code Validate its own Work

This article is about making a coding assistant check its own work before it stops. The author says that when Claude Code can test its result, it does a better job than when it has to guess on the first try. One example is a slow language-model workflow: the author split one large call into three smaller calls and had Claude compare the results so it could confirm the change worked. Another example is web design: Claude was given screenshots and access to Google Chrome so it could look at the page it built and compare it with the intended design. If the page did not match, Claude kept adjusting the code and checking again. The point is that tools for verification help the model correct its own mistakes instead of waiting for a human to notice them. The article presents this as a practical workflow for coding agents, not as a new theory about artificial intelligence. The examples are simple, but they show how a model can be more useful when it can inspect outputs directly. As of 2026-05-05, the advice looks actionable for hands-on Claude Code users, but the evidence is mainly one person’s experience.

## Key insights

- Verification is most effective when the task has a known target output, such as matching a reference result or screenshot.
- Giving Claude access to run tests or inspect rendered pages can reduce human back-and-forth because the model can catch its own mismatches.
- The author’s latency example shows a common optimization pattern: split a large language-model call into smaller pieces and compare against the original behavior.
- For visual tasks, browser access acts as the verification layer; without it, the model has to rely on textual descriptions alone.
- The article’s practical value is in workflow design, not in a new algorithm: the same agent becomes more reliable when it can check its work.

## Derived knowledge pages

- [[how-to/self-verification-for-agent-workflows]]
- [[industry-trends/verification-loops-become-central-to-ai-workflows]]
- [[tools/claude-code]]
- [[topics/agent-self-verification]]
- [[topics/visual-specifications-for-ai-systems]]

## Why it matters

The piece is useful because it turns a vague recommendation — let the model validate itself — into an operational workflow: define an expected output, give the agent a way to inspect results, and let it iterate until the outputs match. That is a durable engineering idea for coding assistants because many failures are not about lack of generation skill but about lack of feedback. The article’s two examples are concrete enough to be reusable: one is functional validation through comparing model outputs, the other is visual validation through browser inspection. The first example also suggests a practical latency tactic: if a single call produces too many tokens and becomes slow, splitting the work can make the system easier to verify and parallelize. The strongest takeaway is that tool access changes the agent’s ability to self-correct, which can improve one-shot success rates on tasks with crisp acceptance criteria. The evidence is still limited to the author’s own experience, so the article supports a workflow pattern more than a quantified performance claim. As of 2026-05-05, this is actionable advice for developers using Claude Code, but it should be treated as a practical heuristic rather than a proven universal rule. For web pages, support-like review of rendered output could be useful, but the article only demonstrates a narrow design-implementation workflow, not broader service automation outcomes.

## Limitations / open questions

The evidence is anecdotal and comes from two personal examples, so it does not establish how often this approach works across different codebases or task types. The article does not give a rigorous benchmark, failure rate, or comparison against a baseline workflow without self-verification. It is unclear how well the approach handles tasks without a clear target output, ambiguous specifications, or bugs that require deeper reasoning rather than output comparison. The Chrome-based visual verification example depends on tool access and may be brittle across environments, frameworks, or browser automation limits. The latency example attributes the slowdown mainly to token volume, but the article does not show measurements proving that splitting the call was the best fix. Security, privacy, and cost implications of giving an agent more tool access are not discussed.

## Contradictions / unverified claims

The article treats self-verification as broadly beneficial, but that can oversimplify cases where the agent can overfit to a test or visually approximate a design without meeting hidden requirements. The claim that Claude can keep working until it verifies its own work is plausible for bounded tasks, but less convincing for open-ended problems with no reliable acceptance signal. The post also leans on success stories, so it is worth reading as workflow advice rather than evidence that self-checking always increases capability.

## Source metadata

- Canonical URL: https://towardsdatascience.com/how-to-make-claude-code-validate-its-own-work/?utm_campaign=tds%20variable&utm_medium=email&_hsenc=p2ANqtz-983i5IEFCGSE-P3c2Jm_8BItpnyWH-44FiF0Jaq6ncB_r2wi2b8socrX_9XHnImlvp31VqD0tsty1czZcJ4NV54cmKLQ&_hsmi=418698396&utm_source=newsletter
- Raw markdown: `raw/readwise/how-to-make-claude-code-validate-its-own-work-01krkb42j4y9839773m7rz83xe.md`
- Raw HTML: `raw/readwise/how-to-make-claude-code-validate-its-own-work-01krkb42j4y9839773m7rz83xe.html`

## Full source text

---
readwise_id: "01krkb42j4y9839773m7rz83xe"
title: "How to Make Claude Code Validate its own Work"
author: "Eivind Kjosbakken"
publication: "Medium"
source_url: "https://towardsdatascience.com/how-to-make-claude-code-validate-its-own-work/?utm_campaign=tds%20variable&utm_medium=email&_hsenc=p2ANqtz-983i5IEFCGSE-P3c2Jm_8BItpnyWH-44FiF0Jaq6ncB_r2wi2b8socrX_9XHnImlvp31VqD0tsty1czZcJ4NV54cmKLQ&_hsmi=418698396&utm_source=newsletter"
category: "article"
location: "archive"
published_date: "2026-05-05"
saved_at: "2026-05-14T13:34:22.787000+00:00"
updated_at: "2026-05-16T13:07:37.341519+00:00"
tags: ["processed"]
---

Claude Code works better when it checks its own work. This helps it fix mistakes and finish tasks faster. The author shows examples of using this to improve coding and web design.
