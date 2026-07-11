---
title: '[AINews] DeepSeek V4 Pro (1.6T-A49B) and Flash (284B-A13B), Base and Instruct
  — runnable on Huawei Ascend chips'
slug: ainews-deepseek-v4-pro-1-6t-a49b-and-flash-284b-a13b-base-and-instruct-runnable-on-huawei-ascend-chips-01kq1ghc73kbvsy1qm9z5ahy3t
category: source
tags:
- edge-deployment
- frontier-compression
- inference-efficiency
- long-context-adoption
- open-model-pressure
- runtime-systems
source_id: ainews-deepseek-v4-pro-1-6t-a49b-and-flash-284b-a13b-base-and-instruct-runnable-on-huawei-ascend-chips-01kq1ghc73kbvsy1qm9z5ahy3t
author: Latent Space
publication: Latent
published_date: '2026-04-25'
assessed_as_of: '2026-04-25'
ingested_at: '2026-06-06T21:35:34+00:00'
canonical_url: https://www.latent.space/p/ainews-deepseek-v4-pro-16t-a49b-and
content_sha256: ab9f72d3b0c4eacab0c52c2258c616197bcb665315b96b2bd4aa892b7a9aa3ea
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
derived_signals:
- signals/2026-04/ainews-deepseek-v4-pro-1-6t-a49b-and-flash-284b-a13b-base-and-instruct-runnable-open-weight-long-context-models-are-becoming-systems-releases-not-che-eaf3b878d3.md
derived_trends:
- industry-trends/open-weight-models-become-viable-on-consumer-hardware.md
derived_pages:
- industry-trends/open-weight-models-become-viable-on-consumer-hardware.md
- signals/2026-04/ainews-deepseek-v4-pro-1-6t-a49b-and-flash-284b-a13b-base-and-instruct-runnable-open-weight-long-context-models-are-becoming-systems-releases-not-che-eaf3b878d3.md
---

# [AINews] DeepSeek V4 Pro (1.6T-A49B) and Flash (284B-A13B), Base and Instruct — runnable on Huawei Ascend chips

This roundup is mostly about DeepSeek’s new V4 models and why they matter. The big headline is a 1 million token context window, which means the model can work over very long documents or long agent runs without losing track as easily. The article says DeepSeek also changed the attention design and checkpoint format so this long context is more practical to serve. The model looks strong among open-weight systems, but the writeup says it is still behind the best closed models overall. A lot of the discussion is really about engineering tradeoffs: model quality, token cost, hardware support, and whether the new design can be deployed outside DeepSeek. The rest of the roundup covers related AI news, but DeepSeek V4 is the main story.

## Key insights

- The most durable technical takeaway is the attention/KV-cache redesign for 1M-token inference, not just the benchmark score.
- V4 Pro and V4 Flash form a real two-tier open-weight lineup, with Flash looking especially relevant for practical long-context cost control.
- The roundup’s benchmark synthesis suggests V4 Pro is near the top of open weights, but still not a clear closed-frontier match.
- Mixed FP4/FP8 checkpoints and day-0 serving support matter because the article frames V4 as a full stack release, not only a model release.
- Low per-token pricing can still hide high end-to-end task cost when evaluations consume huge token volumes.

## Derived knowledge pages

- [[industry-trends/open-weight-models-become-viable-on-consumer-hardware]]
- [[signals/2026-04/ainews-deepseek-v4-pro-1-6t-a49b-and-flash-284b-a13b-base-and-instruct-runnable-open-weight-long-context-models-are-becoming-systems-releases-not-che-eaf3b878d3]]

## Why it matters

This piece matters because it shows a frontier open-weight release that is being judged on systems design as much as raw model quality. DeepSeek V4 is presented with unusually detailed architecture claims: compressed sparse attention, heavily compressed attention, shared KV vectors, mixed precision checkpoints, and 1M-token context. That combination makes the release useful as a reference point for anyone building long-context agents, document analyzers, or high-throughput inference stacks, because the article ties model behavior directly to memory and compute reduction. The benchmark synthesis is also operationally useful: the roundup does not claim DeepSeek has won the whole frontier, but it does say V4 Pro sits near the top of open weights while Flash changes the price-performance discussion. The strongest practical warning is that token economics still matter; one cited evaluation used so many tokens that the run cost stayed high despite cheap advertised pricing. The article also suggests that adoption depends on the serving substrate, since support on vLLM, Blackwell, Mac quants, and Ascend changes what is actually deployable. For advanced AI builders, the main value is understanding that long-context capability is now being shipped as an integrated architecture-plus-infrastructure package, not as a standalone checkpoint. As of 2026-04-25, this looks actionable for teams evaluating long-context open models, but still worth monitoring because the highest claims rely on third-party benchmarking and community interpretation rather than a single controlled evaluation.

## Limitations / open questions

The roundup relies heavily on third-party benchmark synthesis, social posts, and vendor claims rather than a single reproducible evaluation. It is unclear how much of V4’s reported advantage depends on prompting, mode selection, benchmark-specific tuning, or unusually large token budgets during evaluation. The article explicitly notes that V4 remains behind the best closed models in broad domains, and that some reasoning efficiency improvements may be limited relative to prior variants. The long-context architecture is described in detail, but the writeup does not provide enough implementation detail to judge how hard it will be for other labs to reproduce. Serving economics also remain open: low API prices do not guarantee low end-to-end cost when tasks expand token usage dramatically. The Huawei Ascend angle is strategically interesting, but the article only gives partial evidence about scale, supply, and deployment maturity.

## Contradictions / unverified claims

The roundup mixes strong praise with clear uncertainty, so several claims should be treated cautiously. Some posters frame V4 as one of the most important papers of the year, but that is enthusiasm rather than a measured conclusion. The idea that V4 is a major democratizing step is contested in the source itself, because the architecture may be too complex for many labs to copy cleanly. There is also tension between cheap headline pricing and high evaluation cost, which weakens any simple cost-efficiency narrative. The Huawei sovereignty framing is plausible in the article, but the evidence is still partial and partly interpretive rather than conclusive.

## Source metadata

- Canonical URL: https://www.latent.space/p/ainews-deepseek-v4-pro-16t-a49b-and
- Raw markdown: `raw/readwise/ainews-deepseek-v4-pro-1-6t-a49b-and-flash-284b-a13b-base-and-instruct-runnable-on-huawei-ascend-chips-01kq1ghc73kbvsy1qm9z5ahy3t.md`
- Raw HTML: `raw/readwise/ainews-deepseek-v4-pro-1-6t-a49b-and-flash-284b-a13b-base-and-instruct-runnable-on-huawei-ascend-chips-01kq1ghc73kbvsy1qm9z5ahy3t.html`

## Full source text

---
readwise_id: 01kq1ghc73kbvsy1qm9z5ahy3t
title: '[AINews] DeepSeek V4 Pro (1.6T-A49B) and Flash (284B-A13B), Base and Instruct
  — runnable on Huawei Ascend chips'
author: Latent Space
source_url: https://www.latent.space/p/ainews-deepseek-v4-pro-16t-a49b-and
category: rss
location: archive
published_date: '2026-04-25'
saved_at: '2026-04-25T05:06:56.939000+00:00'
updated_at: '2026-05-07T08:25:55.029913+00:00'
tags:
- processed
publication: Latent
---

DeepSeek V4 Pro and Flash are advanced AI models with very large contexts, running efficiently on Huawei Ascend chips to reduce reliance on NVIDIA hardware. The models offer strong performance for long documents and complex tasks while aiming for better cost and energy efficiency. This release is seen as important in the AI and geopolitical landscape, highlighting China’s push for computing independence.
