---
title: '[AINews] OpenAI GPT-next disproves 80 year old Erdős planar unit distance
  problem for under $1000'
slug: ainews-openai-gpt-next-disproves-80-year-old-erd-s-planar-unit-distance-problem-for-under-1000-01ks4q3akgtgx0fbah0rez80eh
category: source
source_id: ainews-openai-gpt-next-disproves-80-year-old-erd-s-planar-unit-distance-problem-for-under-1000-01ks4q3akgtgx0fbah0rez80eh
author: AINews
publication: Substack
published_date: '2026-05-21'
assessed_as_of: '2026-05-21'
ingested_at: '2026-06-06T21:39:57+00:00'
canonical_url: mailto:reader-forwarded-email/e62d9c0816df33c5c139473686318ef4
content_sha256: 4d2b475de68e7a3ee2a8c69556187ebb0b07188975ae0375bdb9cf3827cd96ff
---

# [AINews] OpenAI GPT-next disproves 80 year old Erdős planar unit distance problem for under $1000

This is a news roundup about a few AI releases and benchmarks, with one headline story: OpenAI says a general-purpose reasoning model found a counterexample to a long-standing geometry problem. That matters because it is not a special math system; the claim is that the same kind of model used for broad reasoning may also produce new scientific results. The post also covers Cohere’s open-weight Command A+, Google’s Gemini updates, and several agent and memory benchmarks. A lot of the value here is in what the comparisons reveal: agents still struggle with messy infrastructure, and longer test-time reasoning seems to be doing much of the work in frontier results.

## Key insights

- A general-purpose reasoning model allegedly produced a real research result in discrete geometry, which is more operationally interesting than another benchmark win because it suggests the model can generate new counterexamples, not just answer known problems.
- The source treats the long reasoning trace, reportedly around 125 pages, as evidence that test-time compute is becoming a major lever for frontier reasoning performance.
- InferenceBench and the related agent reports suggest current agents still fail on system-level engineering, dependency management, and configuration work even when they look strong in controlled demos.
- MINTEval’s low average accuracy across very long and frequently updated contexts supports treating memory as a distinct subsystem rather than assuming larger context windows alone will solve it.
- Cohere’s Command A+ is notable less for benchmark dominance than for being Apache 2.0 open weights with unusual architecture choices and practical deployment claims.

## Derived knowledge pages

No derived knowledge pages captured.

## Why it matters

The article’s most durable item is the OpenAI planar unit distance result, because it is presented as a genuine new mathematical disproof from a general-purpose model rather than a canned benchmark score. If the reporting is accurate, that is useful evidence that long-horizon reasoning can sometimes generate novel scientific outputs, not only polished answers. The source is also careful to note the asymmetry: this was a disproof, not the more impressive proof, so the result should be read as meaningful but not triumphant. The heavy emphasis on a 125-page reasoning trace makes the piece relevant to anyone tracking test-time compute, because it suggests frontier gains may be tied to allowing much larger internal search and deliberation. Cohere’s Command A+ matters in a different way: Apache 2.0 open weights plus low-hardware positioning and a distinctive architecture make it a useful reference point for deployable enterprise models, even if the benchmarks are mixed. The agent and memory benchmark items reinforce a practical lesson that is easy to miss in product demos: systems break on infra reality, long contexts, and state management before they break on raw model intelligence. For builders, the roundup is a reminder to separate model capability claims from task-environment reliability. Actionable as of 2026-05-21, with the math claim worth monitoring and the agent/tooling lessons already practical.

## Limitations / open questions

The math headline depends on an internal OpenAI result and secondhand social commentary in the roundup; the article does not include the full paper, proof details, or independent verification. The source says the result is a disproof, which is valuable, but it does not explain the construction well enough to judge novelty or generality. The reported 125-page reasoning trace is impressive, but the article does not show whether that verbosity is efficient, reproducible, or necessary. For Command A+, the benchmark picture is mixed, with strong non-hallucination behavior but weaker scientific reasoning and coding than top peers, so deployment value depends on the task. The agent and memory benchmarks are interesting, but they are still benchmark environments, and the article does not establish how cleanly they transfer to production systems. Several items are framed through social reactions and launch claims rather than deep technical writeups, which limits confidence in broad conclusions.

## Contradictions / unverified claims

The strongest claim in the roundup is also the most easily overstated: a disproof of a famous math problem is significant, but the source itself notes it is less impressive than a proof. The roundup leans on speculation about the exact OpenAI model and compute cost, so those details should be treated cautiously. Several other stories mix vendor framing with community extrapolation, especially the “test-time compute is the paradigm carrying progress” narrative, which is plausible but not proven by one article. The agent-benchmark section is a good corrective to hype, since it shows frontier models still stumble on messy operational work; that tension is the most grounded part of the piece.

## Source metadata

- Canonical URL: mailto:reader-forwarded-email/e62d9c0816df33c5c139473686318ef4
- Raw markdown: `raw/readwise/ainews-openai-gpt-next-disproves-80-year-old-erd-s-planar-unit-distance-problem-for-under-1000-01ks4q3akgtgx0fbah0rez80eh.md`
- Raw HTML: `raw/readwise/ainews-openai-gpt-next-disproves-80-year-old-erd-s-planar-unit-distance-problem-for-under-1000-01ks4q3akgtgx0fbah0rez80eh.html`
