---
title: 'Millions of Calls, One Judge: How We Evaluated Our Voicebot in Production'
slug: millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-01kqkyaqcyqgmyjjqs3r374v14
category: source
tags:
- ai-engineering
- ai-evaluation
- ai-operationalization
- enterprise-ai
- inference-systems
- multimodal-ai
- production-failure
- support-automation
- test-and-verification
- verification-over-principles
- verification-systems
source_id: millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-01kqkyaqcyqgmyjjqs3r374v14
author: Théo Belen-Halimi
publication: Medium
published_date: '2026-04-30'
assessed_as_of: '2026-04-30'
ingested_at: '2026-06-05T17:13:29.831310+00:00'
canonical_url: https://medium.com/artefact-engineering-and-data-science/millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-8c00f6ea6654
content_sha256: e105aed5beb92ccc955b3a2332cb2f4f097dba150b663c03447261ee8a728f6a
derived_implementation_studies:
- voicebot-evaluation-at-telecom-scale
derived_topics:
- atomic-binary-evaluation-judges
- transcription-as-evaluation-bottleneck
derived_trends:
- verification-loops-become-central-to-ai-workflows
---

# Millions of Calls, One Judge: How We Evaluated Our Voicebot in Production

This piece is about how a company checked whether its voicebot was good enough to run in production at telecom scale. The interesting part is that they did not rely on one giant score or manual listening. They broke evaluation into many small yes/no checks, then combined them into metrics that both engineers and business teams could use. They also learned that transcription quality can matter more than prompt design, because bad transcripts distort the judge’s score. The article is useful because it shows a practical evaluation loop: calibrate on a labeled dataset, test with scripted calls, watch live traffic, and send failures back into review.

## Key insights

- A single “overall quality” judge was too vague; one binary judge per question produced scores that were explainable and debuggable.
- A Golden Dataset calibrated on stratified real conversations was treated as the gate for shipping evaluation metrics to production.
- Bot-vs-bot scenarios validated outcomes, but the article notes they can miss expensive or broken intermediate paths inside the conversation.
- The team found transcription quality to be the largest source of evaluation error, so they benchmarked multiple speech-to-text models before tuning judge prompts further.
- The article’s proposed next step is audio-native judging, but it explicitly notes GDPR and biometric-data constraints for voice recordings.

## Derived knowledge pages

- [[implementation-studies/voicebot-evaluation-at-telecom-scale]]
- [[industry-trends/verification-loops-become-central-to-ai-workflows]]
- [[topics/atomic-binary-evaluation-judges]]
- [[topics/transcription-as-evaluation-bottleneck]]

## Why it matters

The article is useful because it turns LLM evaluation from a vague prompt-scoring exercise into an operational system with calibration, release gates, and feedback loops. Its strongest contribution is the decomposition pattern: break one fuzzy metric into atomic binary checks, then recombine them into higher-level KPIs that business and technical teams can both understand. That is a durable engineering pattern as of 2026-04-30 because it addresses explainability, debugging, and release confidence at the same time. The offline lab plus online safety net structure is also practical: it makes evaluation part of the deployment process rather than an after-the-fact audit. The article is candid that judge quality depends on upstream transcription quality, which is a useful reminder that improving the evaluator may be less important than fixing the input representation. The evidence is strongest for the authors’ own production setup, not for a universal benchmark or a general theorem, so the claims should be treated as a well-documented case study rather than a proven standard. For voicebot and telecom-style call automation, the piece is especially relevant because it shows how to keep evaluation grounded when millions of calls make human review impossible as of 2026-04-30.

## Limitations / open questions

The article reports one production system, so the results may not transfer cleanly to other domains, languages, or call mixes. The Golden Dataset is only 500 conversations, which is useful for calibration but still a limited sample of production variability. The article gives an alignment claim for one metric (“Request Resolved”) but does not provide full metric-by-metric performance or error analysis. The exact design of the binary judges, prompt templates, and aggregation thresholds is only described at a high level. The bot-vs-bot scenarios validate end states, but the article itself notes they miss the quality, cost, and failure modes of the middle of the conversation. The online safety net is described operationally, but the article does not quantify false positives, kill-switch sensitivity, or human review load. Audio-native evaluation is identified as a next frontier, but the compliance and storage burden is unresolved.

## Contradictions / unverified claims

The article argues that binary judges and AND/OR aggregation are better than a single holistic score, which is persuasive here, but it is still an internal design choice rather than comparative evidence against other evaluation frameworks. The claim that transcription mattered more than prompt engineering is plausible and well motivated, but it is based on one team’s benchmark and should not be generalized without more data. The “one judge, one question” approach improves clarity, yet it may oversimplify interactions where quality depends on coupled behaviors. The audio-native evaluation idea is appealing, but the privacy and biometric-data caveats make it more constrained than the article’s forward-looking tone might suggest. Overall, the article is practical and grounded, but it is still a single-case engineering narrative rather than a broad empirical study.

## Source metadata

- Canonical URL: https://medium.com/artefact-engineering-and-data-science/millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-8c00f6ea6654
- Raw markdown: `raw/readwise/millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-01kqkyaqcyqgmyjjqs3r374v14.md`
- Raw HTML: `raw/readwise/millions-of-calls-one-judge-how-we-evaluated-our-voicebot-in-production-01kqkyaqcyqgmyjjqs3r374v14.html`
