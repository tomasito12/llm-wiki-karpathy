---
title: Why I Stopped Using Gemma 4 and Switched to Qwen 3.6
slug: why-i-stopped-using-gemma-4-and-switched-to-qwen-3-6-01kqm05wc7wq68ypednrdcpa0b
category: source
tags:
- agent-systems
- agentic-model
- ai-evaluation
- coding-agents
- coding-model
- enterprise-ai
- inference-efficiency
- inference-efficient
- inference-systems
- open-model-pressure
- open-weight-model
- optimization-effects
- software-engineering
- tool-use-capable
- workflow-based-evaluation
- workflow-design
source_id: why-i-stopped-using-gemma-4-and-switched-to-qwen-3-6-01kqm05wc7wq68ypednrdcpa0b
author: Sumit Pandey
publication: Medium
published_date: '2026-04-25'
assessed_as_of: '2026-04-25'
ingested_at: '2026-06-08T16:07:57.013069+00:00'
canonical_url: https://medium.com/towards-deep-learning/why-i-stopped-using-gemma-4-and-switched-to-qwen-3-6-5a3c56d2b2b3
content_sha256: 07875aa4f8280480cc54a97d2e72984f001df1ad2bfaae717097563dbfdd3823
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
derived_models:
- foundation-models/qwen-3-6-35b-a3b.md
derived_topics:
- topics/agentic-coding-workflows.md
- topics/dense-vs-moe-model-consistency.md
derived_trends:
- industry-trends/agent-evaluation-shifts-toward-workflow-based-tool-use.md
- industry-trends/open-weight-models-become-viable-on-consumer-hardware.md
derived_pages:
- foundation-models/qwen-3-6-35b-a3b.md
- industry-trends/agent-evaluation-shifts-toward-workflow-based-tool-use.md
- industry-trends/open-weight-models-become-viable-on-consumer-hardware.md
- topics/agentic-coding-workflows.md
- topics/dense-vs-moe-model-consistency.md
---

# Why I Stopped Using Gemma 4 and Switched to Qwen 3.6

This article is about why one writer stopped using Gemma 4 and switched to Qwen 3.6 for coding tasks where an AI has to use tools, not just answer questions. The core idea is simple: some models look good in a chat box, but fail when they must plan, call tools, and recover from mistakes. The author says Gemma 4 kept looping and getting confused in an agent setup, while Qwen 3.6 finished the same work. What makes this interesting is that the article ties the experience to benchmarks meant to measure real tool use. The takeaway is that model choice depends on the workflow, and for agentic coding the author found Qwen far more usable as of 2026-04-25.

## Key insights

- Benchmarks that measure tool use and agent loops are more informative than single-turn chat benchmarks for this workflow.
- A model can look strong in ordinary prompts but fail badly once wrapped in an agent loop with tool calls and state changes.
- Qwen 3.6-35B-A3B is described as using only 3B active parameters per token, which the article presents as a reason it can outperform a dense 31B model in this setting.
- The author’s most convincing evidence is practical: the same CSV task that broke Gemma 4 reportedly completed cleanly in Qwen.
- HumanEval-style single-question coding tests may not predict agentic coding quality; the article explicitly says Gemma still leads on that narrower benchmark in community testing.

## Derived knowledge pages

- [[foundation-models/qwen-3-6-35b-a3b]]
- [[industry-trends/agent-evaluation-shifts-toward-workflow-based-tool-use]]
- [[industry-trends/open-weight-models-become-viable-on-consumer-hardware]]
- [[topics/agentic-coding-workflows]]
- [[topics/dense-vs-moe-model-consistency]]

## Why it matters

The piece is useful because it focuses on a concrete mismatch that matters in applied AI: the benchmark suite a model looks good on may not match the actual workload. The author’s main claim is not just that Qwen 3.6 is better overall, but that its sparse Mixture of Experts design and stronger tool-loop benchmarks map better to agentic coding than Gemma 4’s dense model. That is a durable engineering lesson if you build assistants that call tools, edit files, run code, or recover from errors, because those workflows depend on control flow and state tracking more than on one-shot answer quality. The article is strongest where it compares MCPMark, SWE-bench Verified, Terminal-Bench 2.0, and NL2Repo, since those are closer to the tasks the author actually ran. It is weaker where it generalizes from one practitioner’s experience and vendor-published charts to broader model conclusions, so the evidence supports a workflow-specific adoption decision more than a universal ranking. The practical read as of 2026-04-25 is to treat Qwen 3.6-35B-A3B as worth testing seriously for local agentic coding, while keeping claims about general superiority or architectural inevitability at arm’s length. For local, private coding and other on-device workflows, the article suggests this model is already usable; for broader support-style automation or voice/meeting use cases, the source does not discuss them, so no conclusion is warranted.

## Limitations / open questions

The evidence is partly anecdotal and partly based on benchmarks and issue reports, not a controlled evaluation. Some benchmark numbers cited in the article come from Qwen’s own materials, so independent verification matters. The article does not specify exact prompts, quantization settings, hardware details, or reproducibility steps for the reported task successes and failures. It also leaves open whether the same advantage holds across other agent frameworks, longer-horizon tasks, or different tool schemas. The claim that sparse Mixture of Experts is the key reason for better agent behavior is plausible in the article’s framing, but not demonstrated causally. The article also notes that Gemma 4 may still be preferable on HumanEval-style single-turn coding, so the conclusion is workflow-dependent rather than universal.

## Contradictions / unverified claims

The strongest tension is between the author’s broad language about open-source AI “catching up” and the actual evidence, which is narrower: one model appears better for one class of workflows. The article leans hard on a few benchmark numbers, but benchmark coverage is uneven and some cited metrics are vendor-produced. The claim that dense models are the “old pattern” goes beyond what the source strictly proves. The piece is persuasive as a practitioner report, but it should not be read as definitive proof that sparse MoE is always superior for all coding or reasoning tasks.

## Source metadata

- Canonical URL: https://medium.com/towards-deep-learning/why-i-stopped-using-gemma-4-and-switched-to-qwen-3-6-5a3c56d2b2b3
- Raw markdown: `raw/readwise/why-i-stopped-using-gemma-4-and-switched-to-qwen-3-6-01kqm05wc7wq68ypednrdcpa0b.md`
- Raw HTML: `raw/readwise/why-i-stopped-using-gemma-4-and-switched-to-qwen-3-6-01kqm05wc7wq68ypednrdcpa0b.html`

## Full source text

---
readwise_id: 01kqm05wc7wq68ypednrdcpa0b
title: Why I Stopped Using Gemma 4 and Switched to Qwen 3.6
author: Sumit Pandey
source_url: https://medium.com/towards-deep-learning/why-i-stopped-using-gemma-4-and-switched-to-qwen-3-6-5a3c56d2b2b3
category: article
location: archive
published_date: '2026-04-25'
saved_at: '2026-05-02T09:26:40.263000+00:00'
updated_at: '2026-05-02T14:21:31.501735+00:00'
tags:
- processed
publication: Medium
---

Why Qwen’s new Mixture of Experts model is the first open-source LLM that actually handles agentic coding workflows
