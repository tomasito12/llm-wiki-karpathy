---
title: Kimi 2.5
slug: kimi-2-5
entity_id: model:kimi-2-5
category: foundation-model
first_seen: '2026-04-20'
last_seen: '2026-04-22'
source_count: 2
evidence_count: 28
source_ids:
- i-spent-3-days-researching-self-hosted-ai-here-s-why-you-should-and-shouldn-t-actually-do-it-01kqkvbh9k2p2m6eh234khs2kf
- kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6
value_level: high
confidence: 0.87
synthesis_state: stage1-placeholder
types:
- coding-model
- open-weight-model
---

# Kimi 2.5

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
A large open-weight mixture-of-experts model tuned for agentic coding and multi-step task execution. The article presents it as unusually strong on hard benchmarks, especially when tools and swarm orchestration are available.

- Performs strongly on hard, tool-using benchmarks, which suggests it can handle multi-step reasoning rather than only short prompts.
- Supports parallel agent orchestration, which can improve throughput on large engineering tasks.
- Uses an open-weight release pattern that makes it easier to inspect and potentially deploy in more flexible environments than closed models.
- Has very low token pricing relative to the article’s cited premium competitors, which matters for repeated agent runs.

## Benchmark Observations

- The article reports 50.2% on Humanity’s Last Exam with tools, ahead of GPT-5.2 and Claude Opus 4.5 in the cited table.
- It reports 76.8% on SWE-bench Verified and 74.9% to 78.4% on BrowseComp depending on swarm use.
- The article claims a 4.5x speedup from swarm execution compared with single-agent execution on the same tasks.

## Comparative Observations

- The source says K2.5 beats GPT-5.2 and Claude Opus 4.5 on Humanity’s Last Exam with tools.
- It is said to outperform GPT-5.2 on BrowseComp and to sit within striking distance of Claude Sonnet 4.6 on SWE-bench Verified.
- The article frames it as 76% cheaper than Claude Opus 4.5 on the cited pricing comparison.
- The article contrasts it with proprietary Claude workflows by implying similar UX can be delivered through a local or open-weight backend.
- It is presented as evidence that open-weight models can be productized in ways that challenge the assumption that only large closed labs can ship frontier coding systems.

## Core Capabilities

- It is optimized for agentic code tasks and multi-step reasoning.
- It supports tool-using benchmark performance that the article ties to practical coding workflows.
- It combines open weights with low inference cost, which makes it easier to evaluate for large-scale automation.
- It can back a coding product that the article frames as frontier-level in user experience.
- It can be adapted as an open-weight base model for downstream product or workflow tuning.
- It is available through the Ollama cloud free tier, which makes it practical for experimentation.

## Maturity signals

The article says K2.5 was launched in July 2025 and had already accumulated benchmark visibility and community reaction by April 2026. It is available on Hugging Face and GitHub, which are practical distribution signals for an open-weight model. The source also notes that Western attention has been limited compared with Llama and Qwen, so visibility is lower than capability might suggest.

## Pricing / inference implications

The article cites $0.50 per million input tokens and $2.80 per million output tokens via OpenRouter, with a direct API cache price of $0.10 per million cached input tokens. That pricing makes long-context and repeat-query coding agents materially cheaper to run than the premium alternatives named in the source.

## Provider

Moonshot AI

## Service automation implications

No direct service automation implications are substantiated in the source; the relevance would be indirect for back-office automation that benefits from parallel task routing.

## Weaknesses / limitations

The article itself notes that its advantages are most pronounced on agentic benchmarks and narrower on simple single-turn tasks. The source also frames Claude and GPT as still strong for interactive use, so K2.5 is not a universal replacement. Independent verification of the benchmark and cost claims is not provided here.

## Evidence / supporting sources

### I Spent 3 Days Researching Self-Hosted AI. Here’s Why You Should (And Shouldn’t) Actually Do It (2026-04-22)

- The article contrasts it with proprietary Claude workflows by implying similar UX can be delivered through a local or open-weight backend. (`4b084012516c` · neutral · comparative_observations[0]; [[sources/i-spent-3-days-researching-self-hosted-ai-here-s-why-you-should-and-shouldn-t-actually-do-it-01kqkvbh9k2p2m6eh234khs2kf|I Spent 3 Days Researching Self-Hosted AI. Here’s Why You Should (And Shouldn’t) Actually Do It]])
- It is presented as evidence that open-weight models can be productized in ways that challenge the assumption that only large closed labs can ship frontier coding systems. (`e80e66e6a44b` · neutral · comparative_observations[1]; [[sources/i-spent-3-days-researching-self-hosted-ai-here-s-why-you-should-and-shouldn-t-actually-do-it-01kqkvbh9k2p2m6eh234khs2kf|I Spent 3 Days Researching Self-Hosted AI. Here’s Why You Should (And Shouldn’t) Actually Do It]])
- It shows that open-weight models can be wrapped into coding products and shipped as practical substitutes for some proprietary workflows. That reduces the assumption that frontier coding UX must depend on a closed model API. (`b32556290799` · neutral · deployment_implications; [[sources/i-spent-3-days-researching-self-hosted-ai-here-s-why-you-should-and-shouldn-t-actually-do-it-01kqkvbh9k2p2m6eh234khs2kf|I Spent 3 Days Researching Self-Hosted AI. Here’s Why You Should (And Shouldn’t) Actually Do It]])
- It is described as powering Cursor’s Composer 2 and as being available in Ollama’s cloud free tier, both of which are practical adoption signals. The source also frames it as part of a real product stack rather than a lab-only model. (`1d3fb2178431` · neutral · maturity_signals; [[sources/i-spent-3-days-researching-self-hosted-ai-here-s-why-you-should-and-shouldn-t-actually-do-it-01kqkvbh9k2p2m6eh234khs2kf|I Spent 3 Days Researching Self-Hosted AI. Here’s Why You Should (And Shouldn’t) Actually Do It]])
- An open-weight model presented here as strong enough to power a real coding product and to be used through local or hosted workflows. The article treats it as evidence that open-weight models can be fine-tuned into frontier-style product behavior.

- The article uses it as the model behind Cursor’s Composer 2, which suggests it can support real coding-product workloads.
- It is positioned as open-weight, which makes it easier to adapt, host, or fine-tune than a closed proprietary model.
- Its presence in Ollama’s cloud free tier suggests it is being operationalized for developer workflows rather than remaining purely experimental. (`052b2089679a` · neutral · operational_profile; [[sources/i-spent-3-days-researching-self-hosted-ai-here-s-why-you-should-and-shouldn-t-actually-do-it-01kqkvbh9k2p2m6eh234khs2kf|I Spent 3 Days Researching Self-Hosted AI. Here’s Why You Should (And Shouldn’t) Actually Do It]])
- Because it appears in a free tier and in an open-weight deployment story, the article implies it may be usable in lower-cost workflows than premium proprietary APIs. The source does not give enough pricing data to quantify the economics beyond that. (`67b50b325fba` · neutral · pricing_inference_implications; [[sources/i-spent-3-days-researching-self-hosted-ai-here-s-why-you-should-and-shouldn-t-actually-do-it-01kqkvbh9k2p2m6eh234khs2kf|I Spent 3 Days Researching Self-Hosted AI. Here’s Why You Should (And Shouldn’t) Actually Do It]])
- The article does not establish direct service automation implications beyond the general possibility of local or hosted deployment for internal agents. (`7dea1cf6bcb4` · neutral · service_automation_implications; [[sources/i-spent-3-days-researching-self-hosted-ai-here-s-why-you-should-and-shouldn-t-actually-do-it-01kqkvbh9k2p2m6eh234khs2kf|I Spent 3 Days Researching Self-Hosted AI. Here’s Why You Should (And Shouldn’t) Actually Do It]])
- It can back a coding product that the article frames as frontier-level in user experience. (`6262f6161657` · supporting · core_capabilities[0]; [[sources/i-spent-3-days-researching-self-hosted-ai-here-s-why-you-should-and-shouldn-t-actually-do-it-01kqkvbh9k2p2m6eh234khs2kf|I Spent 3 Days Researching Self-Hosted AI. Here’s Why You Should (And Shouldn’t) Actually Do It]])
- It can be adapted as an open-weight base model for downstream product or workflow tuning. (`3d8787295861` · supporting · core_capabilities[1]; [[sources/i-spent-3-days-researching-self-hosted-ai-here-s-why-you-should-and-shouldn-t-actually-do-it-01kqkvbh9k2p2m6eh234khs2kf|I Spent 3 Days Researching Self-Hosted AI. Here’s Why You Should (And Shouldn’t) Actually Do It]])
- It is available through the Ollama cloud free tier, which makes it practical for experimentation. (`2734ae8fca94` · supporting · core_capabilities[2]; [[sources/i-spent-3-days-researching-self-hosted-ai-here-s-why-you-should-and-shouldn-t-actually-do-it-01kqkvbh9k2p2m6eh234khs2kf|I Spent 3 Days Researching Self-Hosted AI. Here’s Why You Should (And Shouldn’t) Actually Do It]])
- “Cursor launches Composer 2... and a developer intercepts API traffic and finds the model ID: kimi-k2p5-rl-0317-s515-fast. ... Composer 2 was Kimi K2.5 → an open-weight Chinese model( Moonshot AI) which is fine-tuned with RL!” (`028af495672c` · supporting · supporting_snippet; [[sources/i-spent-3-days-researching-self-hosted-ai-here-s-why-you-should-and-shouldn-t-actually-do-it-01kqkvbh9k2p2m6eh234khs2kf|I Spent 3 Days Researching Self-Hosted AI. Here’s Why You Should (And Shouldn’t) Actually Do It]])
- The article does not provide a direct benchmark for Kimi K2.5 itself, so the performance claims are indirect. Its usefulness here is framed through product behavior and product interception, not through a controlled evaluation of code quality or reliability. (`607ba908db5a` · uncertainty · weaknesses_limitations; [[sources/i-spent-3-days-researching-self-hosted-ai-here-s-why-you-should-and-shouldn-t-actually-do-it-01kqkvbh9k2p2m6eh234khs2kf|I Spent 3 Days Researching Self-Hosted AI. Here’s Why You Should (And Shouldn’t) Actually Do It]])

### Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better (2026-04-20)

- The source says K2.5 beats GPT-5.2 and Claude Opus 4.5 on Humanity’s Last Exam with tools. (`7e0c71f9be04` · neutral · comparative_observations[0]; [[sources/kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6|Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better]])
- It is said to outperform GPT-5.2 on BrowseComp and to sit within striking distance of Claude Sonnet 4.6 on SWE-bench Verified. (`a7db20c56c39` · neutral · comparative_observations[1]; [[sources/kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6|Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better]])
- The article frames it as 76% cheaper than Claude Opus 4.5 on the cited pricing comparison. (`e79e698c2e6e` · neutral · comparative_observations[2]; [[sources/kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6|Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better]])
- It favors workflows that decompose work into subtasks, run them in parallel, and aggregate results. That makes it attractive for automated refactoring, code review, and large-codebase question answering where input-heavy loops dominate cost. (`318cd1ff3b1f` · neutral · deployment_implications; [[sources/kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6|Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better]])
- The article says K2.5 was launched in July 2025 and had already accumulated benchmark visibility and community reaction by April 2026. It is available on Hugging Face and GitHub, which are practical distribution signals for an open-weight model. The source also notes that Western attention has been limited compared with Llama and Qwen, so visibility is lower than capability might suggest. (`65b05e35eb66` · neutral · maturity_signals; [[sources/kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6|Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better]])
- A large open-weight mixture-of-experts model tuned for agentic coding and multi-step task execution. The article presents it as unusually strong on hard benchmarks, especially when tools and swarm orchestration are available.

- Performs strongly on hard, tool-using benchmarks, which suggests it can handle multi-step reasoning rather than only short prompts.
- Supports parallel agent orchestration, which can improve throughput on large engineering tasks.
- Uses an open-weight release pattern that makes it easier to inspect and potentially deploy in more flexible environments than closed models.
- Has very low token pricing relative to the article’s cited premium competitors, which matters for repeated agent runs. (`1596549c71af` · neutral · operational_profile; [[sources/kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6|Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better]])
- The article cites $0.50 per million input tokens and $2.80 per million output tokens via OpenRouter, with a direct API cache price of $0.10 per million cached input tokens. That pricing makes long-context and repeat-query coding agents materially cheaper to run than the premium alternatives named in the source. (`900950a09008` · neutral · pricing_inference_implications; [[sources/kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6|Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better]])
- No direct service automation implications are substantiated in the source; the relevance would be indirect for back-office automation that benefits from parallel task routing. (`e981ebe9f384` · neutral · service_automation_implications; [[sources/kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6|Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better]])
- The article reports 50.2% on Humanity’s Last Exam with tools, ahead of GPT-5.2 and Claude Opus 4.5 in the cited table. (`f8d9e3270626` · supporting · benchmark_observations[0]; [[sources/kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6|Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better]])
- It reports 76.8% on SWE-bench Verified and 74.9% to 78.4% on BrowseComp depending on swarm use. (`a3f647013285` · supporting · benchmark_observations[1]; [[sources/kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6|Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better]])
- The article claims a 4.5x speedup from swarm execution compared with single-agent execution on the same tasks. (`918ddc479938` · supporting · benchmark_observations[2]; [[sources/kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6|Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better]])
- It is optimized for agentic code tasks and multi-step reasoning. (`c6b6ad33a6d9` · supporting · core_capabilities[0]; [[sources/kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6|Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better]])
- It supports tool-using benchmark performance that the article ties to practical coding workflows. (`b131c457c9bc` · supporting · core_capabilities[1]; [[sources/kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6|Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better]])
- It combines open weights with low inference cost, which makes it easier to evaluate for large-scale automation. (`aba528793539` · supporting · core_capabilities[2]; [[sources/kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6|Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better]])
- Kimi K2.5 scores
76.8% on SWE-bench Verified
— within striking distance of Claude Sonnet 4.6. (`900a7ce4b4c5` · supporting · supporting_snippet; [[sources/kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6|Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better]])
- The article itself notes that its advantages are most pronounced on agentic benchmarks and narrower on simple single-turn tasks. The source also frames Claude and GPT as still strong for interactive use, so K2.5 is not a universal replacement. Independent verification of the benchmark and cost claims is not provided here. (`5434ae657f7c` · uncertainty · weaknesses_limitations; [[sources/kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6|Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better]])

## Contradictions / tensions

- The article itself notes that its advantages are most pronounced on agentic benchmarks and narrower on simple single-turn tasks. The source also frames Claude and GPT as still strong for interactive use, so K2.5 is not a universal replacement. Independent verification of the benchmark and cost claims is not provided here. (uncertainty; [[sources/kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6|Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better]])
- The article does not provide a direct benchmark for Kimi K2.5 itself, so the performance claims are indirect. Its usefulness here is framed through product behavior and product interception, not through a controlled evaluation of code quality or reliability. (uncertainty; [[sources/i-spent-3-days-researching-self-hosted-ai-here-s-why-you-should-and-shouldn-t-actually-do-it-01kqkvbh9k2p2m6eh234khs2kf|I Spent 3 Days Researching Self-Hosted AI. Here’s Why You Should (And Shouldn’t) Actually Do It]])

## Related pages

- [[foundation-models/claude-opus-4-7|Claude Opus 4.7]]

## Sources

- [[sources/i-spent-3-days-researching-self-hosted-ai-here-s-why-you-should-and-shouldn-t-actually-do-it-01kqkvbh9k2p2m6eh234khs2kf|I Spent 3 Days Researching Self-Hosted AI. Here’s Why You Should (And Shouldn’t) Actually Do It]]
- [[sources/kimi-k2-6-just-dropped-the-open-source-coding-agent-that-already-beats-claude-opus-4-5-at-76-lower-cost-just-got-better-01kqkv823tq6868pfbrjg0khg6|Kimi K2.6 Just Dropped — The Open-Source Coding Agent That Already Beats Claude Opus 4.5 at 76% Lower Cost Just Got Better]]
