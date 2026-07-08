---
title: Hallucinations
slug: hallucinations
entity_id: glossary:hallucinations
category: glossary
tags:
- ai-engineering
- evals
- orchestration
- retrieval
first_seen: '2026-04-09'
last_seen: '2026-05-05'
source_count: 2
evidence_count: 8
source_ids:
- gpt-5-5-instant-smarter-clearer-and-more-personalized-01kqwq48t17nzsnykvwspqt7s1
- i-ran-gemma-4-locally-here-s-what-nobody-s-telling-you-01kqfzwx5z81csjrvzvv6xgq9x
value_level: high
confidence: 0.9
synthesis_state: synthesized
synthesis_stale: false
synthesis_input_hash: 3367cf29e3e85a7d
current_input_hash: 3367cf29e3e85a7d
synthesis_schema_version: 1
synthesis_prompt_version: 1
last_synthesized_at: '2026-06-17T20:03:55Z'
---

# Hallucinations

## Executive synthesis

Hallucinations are model outputs that sound confident and plausible but are not grounded in provided context or reliable evidence, so they can be fluent yet wrong. In practice, the term covers both subtle factual mistakes and fully invented details. The main operational risk is trust: hallucinations can mislead users, especially in high-stakes or retrieval-heavy settings where the model may over-rely on internal priors instead of available evidence. The reviewed sources agree that this is a central reliability problem and that mitigation usually requires grounding, verification, refusal behavior, routing/prompting choices, and careful evaluation. One source adds an internal result claiming a large reduction in hallucinated claims for a newer model, but the comparison context is limited, so it should not be generalized without more evidence.

## Context card

- **Use this page when:** Use this page when you need a compact definition of hallucinations and a quick sense of why they matter in AI systems, especially retrieval- and tool-heavy workflows.
- **Best for questions about:** What hallucinations mean in AI engineering, How hallucinations show up in retrieval-augmented or tool-using systems, Why hallucinations matter for reliability, trust, and safety, Common mitigation approaches for hallucinations
- **Not enough for:** A full taxonomy of hallucination types, Benchmark methodology or exact evaluation setup behind the reported reduction, Detailed implementation guidance for a specific RAG or agent stack
- **Strongest sources:** GPT-5.5 Instant: smarter, clearer, and more personalized, I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You.
- **Related tags:** ai-engineering, evals, orchestration, retrieval

## What to remember

- Hallucinations are plausible-sounding model outputs that are not supported by evidence.
- They are a reliability problem, not just a wording problem.
- They matter most when users act on the answer in high-stakes or operational settings.
- Retrieval alone is not enough; models may still prefer internal priors over provided context.
- Good handling usually needs evaluation, grounding, verification, and refusal/escalation behavior.

## Consensus

- Hallucinations are model-generated outputs that are unsupported by the provided context or reliable evidence, even when they sound confident and fluent.
- They include both fully invented claims and smaller factual errors, not just extreme fabrications.
- They are a core reliability issue for assistants and language models, especially where correctness matters more than style.
- They are especially relevant in retrieval-heavy, tool-using, support, and agent workflows because the model may ignore available evidence or its own output may be treated as authoritative.
- Mitigations mentioned in the sources include retrieval, verification, better refusal behavior, tighter routing or prompting, grounding, evaluation, and escalation design.

## Tensions / open questions

- The sources agree on the broad definition, but one emphasizes grounding in provided context while the other frames hallucinations more broadly as any unsupported, incorrect, or fabricated output.
- The internal evaluation claim about fewer hallucinated claims is promising, but the evidence here does not include enough methodological detail to compare it confidently with other systems.
- The term is useful in practice, but it can blur together several failure modes, from minor inaccuracies to fully fabricated details.

## Evidence quality

- Evidence is fairly strong for the basic definition and practical importance because two independent sources agree closely.
- The guidance on mitigations is directionally consistent but general rather than prescriptive.
- One source reports an internal evaluation result (52.5% fewer hallucinated claims on high-stakes prompts), but the evaluation details are not provided here, so it should be treated as limited evidence for comparative performance.
- The page is best read as a glossary-level synthesis, not a deep empirical review.

## Practical takeaway

Treat hallucination control as a core design and eval requirement, not a polish issue: test whether the model actually uses retrieved context, measure unsupported claims, and add verification or refusal paths where wrong answers are costly.

## Evidence index

- Sources: 2
- Evidence items: 8
- Current input hash: `3367cf29e3e85a7d`
- Cached input hash: `3367cf29e3e85a7d`
- Last synthesized: 2026-06-17T20:03:55Z
- Synthesis status: `fresh`

## Related pages

- [[glossary/retrieval-augmented-generation|Retrieval-Augmented Generation]]

## Sources

- [[sources/gpt-5-5-instant-smarter-clearer-and-more-personalized-01kqwq48t17nzsnykvwspqt7s1|GPT-5.5 Instant: smarter, clearer, and more personalized]]
- [[sources/i-ran-gemma-4-locally-here-s-what-nobody-s-telling-you-01kqfzwx5z81csjrvzvv6xgq9x|I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You.]]
