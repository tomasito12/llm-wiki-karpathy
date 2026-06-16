---
title: Fine-tuning can revive memorized text the base model had suppressed
slug: fine-tuning-revives-memorized-copyright-text
entity_id: trend:fine-tuning-revives-memorized-copyright-text
category: industry-trend
tags:
- ai-research
- ai-safety
- behavioral-evaluation
- workflow-based-evaluation
first_seen: '2026-06-05'
last_seen: '2026-06-05'
source_count: 1
evidence_count: 9
source_ids:
- fw-qwen3-7-max-challenges-google-for-third-place-ai-saves-whales-fine-tuning-breaks-copyright-alignment-01ktc7y2va1qsw7r5ej6aq5f0q
value_level: high
confidence: 0.91
synthesis_state: stage1-placeholder
maturity: unknown
---

# Fine-tuning can revive memorized text the base model had suppressed

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
A model that has been aligned to avoid verbatim copying can still be pushed toward regurgitation by post-training on tasks that require reconstructing source text. The mechanism matters: customization is not a monotonic safety improvement, and guardrails should be treated as version- and task-specific rather than permanent properties of the model.

## Related Trends

- ai-governance-shifts-toward-layered-verification
- verification-loops-become-central-to-ai-workflows

## Supporting Data Points

- GPT-4o without fine-tuning served as a baseline and produced 7.36 percent BMC@5
- After fine-tuning, BMC@5 exceeded 40 percent for 10 of 30 books in one setup
- GPT-4o reached 91.9 percent BMC@5 in one test
- Fine-tuning on synthetic data produced BMC@5 scores near 0

## Time sensitivity

Actionable as of 2026-06-05; the underlying behavior depends on fine-tuning setup, but the failure mode is durable enough to remain relevant for future customization pipelines.

## Uncertainty / maturity

The evidence is strong for the specific experimental setup, but the article does not test whether the same models would plagiarize without the explicit author-style prompt. So the trend is real, but its exact boundary conditions are not fully established.

## Evidence / supporting sources

### Fw: Qwen3.7-Max Challenges Google for Third Place, AI Saves Whales, Fine-Tuning Breaks Copyright Alignment (2026-06-05)

- A model that has been aligned to avoid verbatim copying can still be pushed toward regurgitation by post-training on tasks that require reconstructing source text. The mechanism matters: customization is not a monotonic safety improvement, and guardrails should be treated as version- and task-specific rather than permanent properties of the model. (`9d2be858cbc8` · neutral · trend_description; [[sources/fw-qwen3-7-max-challenges-google-for-third-place-ai-saves-whales-fine-tuning-breaks-copyright-alignment-01ktc7y2va1qsw7r5ej6aq5f0q|Fw: Qwen3.7-Max Challenges Google for Third Place, AI Saves Whales, Fine-Tuning Breaks Copyright Alignment]])
- The article reports that fine-tuning on summary-to-paragraph generation caused DeepSeek-V3.1, Gemini 2.5 Pro, and GPT-4o to reproduce large verbatim spans from books they had pretrained on, including cases above 40 percent BMC@5 and one case reaching 91.9 percent. (`80baa933fc56` · supporting · evidence_from_source; [[sources/fw-qwen3-7-max-challenges-google-for-third-place-ai-saves-whales-fine-tuning-breaks-copyright-alignment-01ktc7y2va1qsw7r5ej6aq5f0q|Fw: Qwen3.7-Max Challenges Google for Third Place, AI Saves Whales, Fine-Tuning Breaks Copyright Alignment]])
- GPT-4o without fine-tuning served as a baseline and produced 7.36 percent BMC@5 (`cf0f20568a12` · supporting · supporting_data_points[0]; [[sources/fw-qwen3-7-max-challenges-google-for-third-place-ai-saves-whales-fine-tuning-breaks-copyright-alignment-01ktc7y2va1qsw7r5ej6aq5f0q|Fw: Qwen3.7-Max Challenges Google for Third Place, AI Saves Whales, Fine-Tuning Breaks Copyright Alignment]])
- After fine-tuning, BMC@5 exceeded 40 percent for 10 of 30 books in one setup (`08963f5c077c` · supporting · supporting_data_points[1]; [[sources/fw-qwen3-7-max-challenges-google-for-third-place-ai-saves-whales-fine-tuning-breaks-copyright-alignment-01ktc7y2va1qsw7r5ej6aq5f0q|Fw: Qwen3.7-Max Challenges Google for Third Place, AI Saves Whales, Fine-Tuning Breaks Copyright Alignment]])
- GPT-4o reached 91.9 percent BMC@5 in one test (`5ce78ce2781d` · supporting · supporting_data_points[2]; [[sources/fw-qwen3-7-max-challenges-google-for-third-place-ai-saves-whales-fine-tuning-breaks-copyright-alignment-01ktc7y2va1qsw7r5ej6aq5f0q|Fw: Qwen3.7-Max Challenges Google for Third Place, AI Saves Whales, Fine-Tuning Breaks Copyright Alignment]])
- Fine-tuning on synthetic data produced BMC@5 scores near 0 (`a6b75036f2d6` · supporting · supporting_data_points[3]; [[sources/fw-qwen3-7-max-challenges-google-for-third-place-ai-saves-whales-fine-tuning-breaks-copyright-alignment-01ktc7y2va1qsw7r5ej6aq5f0q|Fw: Qwen3.7-Max Challenges Google for Third Place, AI Saves Whales, Fine-Tuning Breaks Copyright Alignment]])
- "Fine-tuning large language models on a seemingly benign task that would be useful to writers — expanding plot summaries into paragraphs of polished fiction — causes them to regurgitate substantial portions of books on which they were pretrained." (`9fb58368d669` · supporting · supporting_snippet; [[sources/fw-qwen3-7-max-challenges-google-for-third-place-ai-saves-whales-fine-tuning-breaks-copyright-alignment-01ktc7y2va1qsw7r5ej6aq5f0q|Fw: Qwen3.7-Max Challenges Google for Third Place, AI Saves Whales, Fine-Tuning Breaks Copyright Alignment]])
- Actionable as of 2026-06-05; the underlying behavior depends on fine-tuning setup, but the failure mode is durable enough to remain relevant for future customization pipelines. (`cf2837a1f21e` · uncertainty · time_sensitivity; [[sources/fw-qwen3-7-max-challenges-google-for-third-place-ai-saves-whales-fine-tuning-breaks-copyright-alignment-01ktc7y2va1qsw7r5ej6aq5f0q|Fw: Qwen3.7-Max Challenges Google for Third Place, AI Saves Whales, Fine-Tuning Breaks Copyright Alignment]])
- The evidence is strong for the specific experimental setup, but the article does not test whether the same models would plagiarize without the explicit author-style prompt. So the trend is real, but its exact boundary conditions are not fully established. (`406cc18ab0a7` · uncertainty · uncertainty_note; [[sources/fw-qwen3-7-max-challenges-google-for-third-place-ai-saves-whales-fine-tuning-breaks-copyright-alignment-01ktc7y2va1qsw7r5ej6aq5f0q|Fw: Qwen3.7-Max Challenges Google for Third Place, AI Saves Whales, Fine-Tuning Breaks Copyright Alignment]])

## Contradictions / tensions

- Actionable as of 2026-06-05; the underlying behavior depends on fine-tuning setup, but the failure mode is durable enough to remain relevant for future customization pipelines. (uncertainty; [[sources/fw-qwen3-7-max-challenges-google-for-third-place-ai-saves-whales-fine-tuning-breaks-copyright-alignment-01ktc7y2va1qsw7r5ej6aq5f0q|Fw: Qwen3.7-Max Challenges Google for Third Place, AI Saves Whales, Fine-Tuning Breaks Copyright Alignment]])
- The evidence is strong for the specific experimental setup, but the article does not test whether the same models would plagiarize without the explicit author-style prompt. So the trend is real, but its exact boundary conditions are not fully established. (uncertainty; [[sources/fw-qwen3-7-max-challenges-google-for-third-place-ai-saves-whales-fine-tuning-breaks-copyright-alignment-01ktc7y2va1qsw7r5ej6aq5f0q|Fw: Qwen3.7-Max Challenges Google for Third Place, AI Saves Whales, Fine-Tuning Breaks Copyright Alignment]])

## Related pages

- ai-governance-shifts-toward-layered-verification
- verification-loops-become-central-to-ai-workflows

## Sources

- [[sources/fw-qwen3-7-max-challenges-google-for-third-place-ai-saves-whales-fine-tuning-breaks-copyright-alignment-01ktc7y2va1qsw7r5ej6aq5f0q|Fw: Qwen3.7-Max Challenges Google for Third Place, AI Saves Whales, Fine-Tuning Breaks Copyright Alignment]]
