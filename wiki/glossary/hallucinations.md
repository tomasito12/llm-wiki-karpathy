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
confidence: 0.8999999999999999
synthesis_state: stage1-placeholder
---

# Hallucinations

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Hallucinations are model outputs that sound confident and plausible but are unsupported, incorrect, or fabricated. In retrieval or tool-using systems, they often appear when the model favors internal priors over provided context.

## Related Terms

- Retrieval-Augmented Generation

## Relevance Note

Hallucination control is durable across AI systems because it directly affects trust, escalation, and whether a model can be used safely in support or knowledge workflows. It is especially important in retrieval-heavy assistants and service automation where the cost of a wrong answer is high.

## Evidence / supporting sources

### GPT-5.5 Instant: smarter, clearer, and more personalized (2026-05-05)

- In AI engineering, hallucinations are a core reliability problem because an assistant can sound confident while stating false or unsupported information. They matter most when users rely on the answer for decisions in high-stakes settings such as medicine, law, or finance. Common mitigations include retrieval, verification, better refusal behavior, and tighter routing or prompting. In practice, the concept also covers cases where a model produces inaccurate details, not just completely fabricated facts. (`5a9ac665b274` · neutral · extended_explanation; [[sources/gpt-5-5-instant-smarter-clearer-and-more-personalized-01kqwq48t17nzsnykvwspqt7s1|GPT-5.5 Instant: smarter, clearer, and more personalized]])
- Hallucinations are model-generated claims that are not grounded in the provided context or other reliable evidence, and therefore may be fluent yet incorrect. (`00608e36e3b2` · neutral · proposed_definition; [[sources/gpt-5-5-instant-smarter-clearer-and-more-personalized-01kqwq48t17nzsnykvwspqt7s1|GPT-5.5 Instant: smarter, clearer, and more personalized]])
- A central failure mode for language models and assistants, especially where correctness matters more than style. Useful for discussing answer reliability, safety, evaluation, and grounding methods. (`5fedf404a9b3` · neutral · relevance_note; [[sources/gpt-5-5-instant-smarter-clearer-and-more-personalized-01kqwq48t17nzsnykvwspqt7s1|GPT-5.5 Instant: smarter, clearer, and more personalized]])
- "In internal evaluations, GPT‑5.5 Instant produced 52.5% fewer hallucinated claims than GPT‑5.3 Instant on high-stakes prompts covering areas like medicine, law, and finance." (`f2e161e47cf3` · supporting · supporting_snippet; [[sources/gpt-5-5-instant-smarter-clearer-and-more-personalized-01kqwq48t17nzsnykvwspqt7s1|GPT-5.5 Instant: smarter, clearer, and more personalized]])

### I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You. (2026-04-09)

- The term covers a broad family of failure modes, from subtle factual errors to fully invented details. In practice, practitioners watch for hallucinations in search, retrieval-augmented generation, customer support, and agent workflows because these errors can look authoritative while still being wrong. The operational problem is not just correctness; it is also when and why the model ignores available evidence. That makes evaluation, grounding, and escalation design important. (`a7e0572b3a93` · neutral · extended_explanation; [[sources/i-ran-gemma-4-locally-here-s-what-nobody-s-telling-you-01kqfzwx5z81csjrvzvv6xgq9x|I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You.]])
- Hallucinations are model outputs that sound confident and plausible but are unsupported, incorrect, or fabricated. In retrieval or tool-using systems, they often appear when the model favors internal priors over provided context. (`296400571fae` · neutral · proposed_definition; [[sources/i-ran-gemma-4-locally-here-s-what-nobody-s-telling-you-01kqfzwx5z81csjrvzvv6xgq9x|I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You.]])
- Hallucination control is durable across AI systems because it directly affects trust, escalation, and whether a model can be used safely in support or knowledge workflows. It is especially important in retrieval-heavy assistants and service automation where the cost of a wrong answer is high. (`e6b4f89cc118` · neutral · relevance_note; [[sources/i-ran-gemma-4-locally-here-s-what-nobody-s-telling-you-01kqfzwx5z81csjrvzvv6xgq9x|I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You.]])
- It also tends to rely heavily on its internal knowledge even when you want it to prioritize retrieved context. If you’re building a RAG pipeline, test this explicitly before committing — some developers have hit hallucination rates higher than expected when the model decides it “knows” the answer already. (`bb7ea03f57f6` · supporting · supporting_snippet; [[sources/i-ran-gemma-4-locally-here-s-what-nobody-s-telling-you-01kqfzwx5z81csjrvzvv6xgq9x|I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You.]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- Retrieval-Augmented Generation

## Sources

- [[sources/gpt-5-5-instant-smarter-clearer-and-more-personalized-01kqwq48t17nzsnykvwspqt7s1|GPT-5.5 Instant: smarter, clearer, and more personalized]]
- [[sources/i-ran-gemma-4-locally-here-s-what-nobody-s-telling-you-01kqfzwx5z81csjrvzvv6xgq9x|I Ran Gemma 4 Locally. Here’s What Nobody’s Telling You.]]
