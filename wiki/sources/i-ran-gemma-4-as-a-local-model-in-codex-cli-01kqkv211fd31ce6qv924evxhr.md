---
title: I ran Gemma 4 as a local model in Codex CLI
slug: i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr
category: source
tags:
- agent-systems
- ai-engineering
- inference-systems
- prompt-engineering
source_id: i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr
author: Daniel Vaughan
publication: Medium
published_date: '2026-04-13'
assessed_as_of: '2026-04-13'
ingested_at: '2026-05-17T13:37:08.445272+00:00'
canonical_url: https://medium.com/google-cloud/i-ran-gemma-4-as-a-local-model-in-codex-cli-7fda754dc0d4
content_sha256: 9b43e012a014ff6d708163182bfcb8e83ee07c55050d0f51db8aa2525ad7e6cf
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
derived_how_to:
- how-to/local-coding-model-setup.md
derived_models:
- foundation-models/gemma-4.md
derived_tools:
- tools/llama-cpp.md
- tools/ollama.md
derived_topics:
- topics/agentic-workflows.md
- topics/context-engineering.md
derived_pages:
- foundation-models/gemma-4.md
- how-to/local-coding-model-setup.md
- tools/llama-cpp.md
- tools/ollama.md
- topics/agentic-workflows.md
- topics/context-engineering.md
---

# I ran Gemma 4 as a local model in Codex CLI

This piece looks at whether a local AI model can do real coding work inside a command-line coding tool. The author tried Gemma 4 on two computers: a MacBook Pro and a Dell machine with more memory and a different chip. The test was not about theory; it was about whether the model could read files, write code, and run tests without constant help. The result was mixed but interesting. The faster computer did not produce the best outcome, because it made more mistakes and needed more retries. The slower local setup worked more reliably, but the cloud model was still the cleanest and quickest on this task. The article also shows that getting local models working can take a lot of setup, because the right software version and configuration flags matter. For beginners, the main lesson is that an AI model is only useful for coding if it can actually use tools reliably, not just talk quickly. As of 2026-04-13, the article suggests local coding is viable in some cases, but not yet a simple drop-in replacement for cloud models.

## Key insights

- For agentic coding, first-pass reliability mattered more than raw token speed in this test.
- Gemma 4's tool-calling quality was the threshold that made local use practical, not the token throughput.
- Local setups required precise configuration: model format, context length, cache quantization, and tool-template flags all mattered.
- A faster local model can still lose in end-to-end task time if it produces more retries and broken tool calls.
- The cloud baseline remained the cleanest result on this specific coding task, so a hybrid local/cloud workflow looked more realistic than full replacement.

## Derived knowledge pages

- [[foundation-models/gemma-4]]
- [[how-to/local-coding-model-setup]]
- [[tools/llama-cpp]]
- [[tools/ollama]]
- [[topics/agentic-workflows]]
- [[topics/context-engineering]]

## Why it matters

The piece matters because it turns local model discussion into an operational comparison inside a real agentic coding workflow rather than a theoretical debate. It shows that the useful question is not just how many tokens a model can generate per second, but whether it can reliably emit tool calls, write tests, and finish a task without repair passes. The article also highlights how much local deployment depends on glue details: model format, context size, cache quantization, template flags, and provider compatibility. That is useful for anyone evaluating whether a local model can sit inside a coding agent or other tool-using workflow, because failure can come from the serving stack as much as from the model itself. The comparison between the Mac and the GB10 suggests that hardware bandwidth alone does not explain end-to-end performance when a mixture-of-experts model activates only part of its parameters. For service automation adjacent workflows, the closing implication is that local assistants are more credible when they can reliably call tools, but the article does not provide support-center, voice, or back-office evidence beyond coding. Actionable as of 2026-04-13, but still a single-task spot check rather than broad proof of local deployment viability.

## Limitations / open questions

This is explicitly a single practical spot check, not a statistically robust benchmark. The task was one Python function with tests, so it does not show how Gemma 4 behaves on harder coding problems, longer projects, or messy multi-step agent loops. The Mac result depended on a highest-memory-fit Q4_K_M setup, so the author notes that higher precision or more roomier Apple Silicon machines could behave differently. The article also exposes serving-stack fragility: Ollama, llama.cpp, vLLM, and Codex CLI did not all interoperate cleanly, and version changes could alter results. The cloud baseline used GPT-5.4 with high reasoning effort, but the source does not provide a cost-normalized comparison.

## Contradictions / unverified claims

The article pushes back against the intuition that faster token generation automatically means a better coding experience, but that conclusion comes from one task and two local machines. The GB10 and Mac comparisons are shaped by quantization, tool-call reliability, and serving bugs, so they do not isolate model quality cleanly. The author also relies on vendor benchmark numbers for the tool-calling claim, which are useful but not independently validated here. The strongest practical claim is not that Gemma 4 beats cloud models, but that it crossed a usability threshold from broken tool calling to functional local agentic coding.

## Source metadata

- Canonical URL: https://medium.com/google-cloud/i-ran-gemma-4-as-a-local-model-in-codex-cli-7fda754dc0d4
- Raw markdown: `raw/readwise/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr.md`
- Raw HTML: `raw/readwise/i-ran-gemma-4-as-a-local-model-in-codex-cli-01kqkv211fd31ce6qv924evxhr.html`

## Full source text

---
readwise_id: 01kqkv211fd31ce6qv924evxhr
title: I ran Gemma 4 as a local model in Codex CLI
author: Daniel Vaughan
source_url: https://medium.com/google-cloud/i-ran-gemma-4-as-a-local-model-in-codex-cli-7fda754dc0d4
category: article
location: archive
published_date: '2026-04-13'
saved_at: '2026-05-02T07:57:10.156000+00:00'
updated_at: '2026-05-02T14:21:53.843972+00:00'
tags:
- processed
publication: Medium
---

The author tested Gemma 4 local models on a MacBook Pro and a Dell GB10 using Codex CLI for coding tasks. The Dell produced higher-quality code with fewer errors, while the Mac was faster in token generation but less reliable. Overall, code quality and tool-calling success mattered more than raw speed for this workflow.
