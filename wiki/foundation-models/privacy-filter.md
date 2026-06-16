---
title: Privacy Filter
slug: privacy-filter
entity_id: model:privacy-filter
category: foundation-model
tags:
- inference-efficient
- long-context-model
- open-weight-model
- tool-use-capable
first_seen: '2026-04-22'
last_seen: '2026-04-26'
source_count: 2
evidence_count: 33
source_ids:
- introducing-openai-privacy-filter-01kptv6v2rm47hbeqs6trnpaaj
- openai-just-open-sourced-the-one-thing-every-startup-should-have-built-first-01kqn8asyw9tae3fncffmy92cc
value_level: high
confidence: 0.955
synthesis_state: stage1-placeholder
types:
- open-weight-model
- reasoning-model
---

# Privacy Filter

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
- Open-weight model specialized for masking personally identifiable information in text.
- Built as a bidirectional token-classification model with span decoding, so it labels inputs in one pass and reconstructs coherent redaction spans.
- The source positions it as context-aware rather than purely rule-based, which matters for subtle cases like private names, dates, secrets, and ambiguous references.
- The model is small enough to run locally, which is the main operational differentiator for privacy-sensitive preprocessing workflows.

## Benchmark Observations

- OpenAI reports 96% F1 on PII-Masking-300k, with 94.04% precision and 98.04% recall.
- OpenAI reports 97.43% F1 on a corrected version of the benchmark after annotation issues were identified.
- The source says fine-tuning on a small amount of data raised F1 from 54% to 96% on the domain-adaption benchmark it evaluated.
- The article reports 96% F1 on the PII-Masking-300k benchmark and 97.43% on a corrected version of that benchmark.
- The article notes that OpenAI flagged annotation issues in the benchmark, which limits how much confidence to place in the published score alone.
- The article says OpenAI reported a jump from 54% F1 to 96% F1 on a domain-adaptation benchmark after light fine-tuning.

## Comparative Observations

- The source contrasts Privacy Filter with traditional PII tools that rely on deterministic rules for formats like phone numbers and email addresses, saying those tools miss subtler context-dependent personal information.
- OpenAI frames the model as achieving frontier-level privacy filtering performance while remaining small enough to run locally.
- The article positions the model against regex-based masking and argues it is better at context-sensitive identification of private names and entities.
- It is described as solving a narrow redaction problem more directly than a general-purpose reasoning model such as GPT-5.5, Claude, or Gemini.
- The piece frames it as a case where a small specialist model can be more appropriate than a much larger frontier model because the task is token labeling, not reasoning.

## Core Capabilities

- It masks personally identifiable information in text, including names, addresses, emails, phone numbers, dates, account numbers, and secrets.
- It performs token-level classification and span decoding, which helps produce coherent redaction boundaries.
- It supports long-context inference up to 128,000 tokens, which matters for documents and logs.
- It allows fine-tuning for different privacy policies and data distributions.
- It detects and masks personally identifiable information in unstructured text before the text is sent elsewhere.
- It can process long documents in one pass because the article says it supports a 128k context window.
- It can be tuned for different operating points, so teams can choose more recall or more precision depending on the workflow.
- It can be fine-tuned on small labeled datasets to adapt to specialized vocabularies and domain-specific identifiers.

## Maturity signals

OpenAI says the model is released under Apache 2.0 on Hugging Face and GitHub, with documentation for architecture, taxonomy, decoding, evaluation, and limitations. That combination points to a real release artifact rather than a concept note. The source does not provide external adoption evidence, so maturity should be read as release-ready rather than proven at scale.

## Pricing / inference implications

Running locally implies potentially lower marginal cost for high-volume redaction than sending all text to a hosted service, but the source gives no latency, hardware, or serving-cost numbers. The 1.5B total parameters with 50M active parameters suggest a relatively compact deployment footprint compared with larger frontier models.

## Provider

OpenAI

## Service automation implications

Useful for support and back-office systems that need to scrub names, contact details, account numbers, or secrets before storage or handoff. It can reduce risk in ticket queues, chat transcripts, document review, and logging pipelines, but human review remains important in high-stakes workflows.

## Weaknesses / limitations

The source says performance may vary across languages, scripts, naming conventions, and domains outside the training distribution. It can miss uncommon identifiers and ambiguous private references, and it can over- or under-redact when context is limited, especially in short sequences. OpenAI also notes it is not an anonymization tool or compliance certification.

## Evidence / supporting sources

### Introducing OpenAI Privacy Filter (2026-04-22)

- The source contrasts Privacy Filter with traditional PII tools that rely on deterministic rules for formats like phone numbers and email addresses, saying those tools miss subtler context-dependent personal information. (`136ac0a57b7a` · neutral · comparative_observations[0]; [[sources/introducing-openai-privacy-filter-01kptv6v2rm47hbeqs6trnpaaj|Introducing OpenAI Privacy Filter]])
- OpenAI frames the model as achieving frontier-level privacy filtering performance while remaining small enough to run locally. (`be1303ad0a15` · neutral · comparative_observations[1]; [[sources/introducing-openai-privacy-filter-01kptv6v2rm47hbeqs6trnpaaj|Introducing OpenAI Privacy Filter]])
- - Fits as a local preprocessing stage before training, indexing, logging, or human review, so sensitive text can be filtered before leaving a machine.
- The 128,000-token context window and single-pass labeling make it practical for long documents and noisy production text where multi-step chunking would be awkward.
- Developers can tune recall versus precision and fine-tune for local policy, so deployment should include task-specific evaluation rather than relying on the default threshold.
- The model is better treated as a privacy layer inside a broader workflow than as a standalone compliance mechanism. (`0297bc2ab830` · neutral · deployment_implications; [[sources/introducing-openai-privacy-filter-01kptv6v2rm47hbeqs6trnpaaj|Introducing OpenAI Privacy Filter]])
- OpenAI says the model is released under Apache 2.0 on Hugging Face and GitHub, with documentation for architecture, taxonomy, decoding, evaluation, and limitations. That combination points to a real release artifact rather than a concept note. The source does not provide external adoption evidence, so maturity should be read as release-ready rather than proven at scale. (`caeaa81e70ad` · neutral · maturity_signals; [[sources/introducing-openai-privacy-filter-01kptv6v2rm47hbeqs6trnpaaj|Introducing OpenAI Privacy Filter]])
- - Open-weight model specialized for masking personally identifiable information in text.
- Built as a bidirectional token-classification model with span decoding, so it labels inputs in one pass and reconstructs coherent redaction spans.
- The source positions it as context-aware rather than purely rule-based, which matters for subtle cases like private names, dates, secrets, and ambiguous references.
- The model is small enough to run locally, which is the main operational differentiator for privacy-sensitive preprocessing workflows. (`191e744f5f64` · neutral · operational_profile; [[sources/introducing-openai-privacy-filter-01kptv6v2rm47hbeqs6trnpaaj|Introducing OpenAI Privacy Filter]])
- Running locally implies potentially lower marginal cost for high-volume redaction than sending all text to a hosted service, but the source gives no latency, hardware, or serving-cost numbers. The 1.5B total parameters with 50M active parameters suggest a relatively compact deployment footprint compared with larger frontier models. (`8eb24fa2e864` · neutral · pricing_inference_implications; [[sources/introducing-openai-privacy-filter-01kptv6v2rm47hbeqs6trnpaaj|Introducing OpenAI Privacy Filter]])
- Useful for support and back-office systems that need to scrub names, contact details, account numbers, or secrets before storage or handoff. It can reduce risk in ticket queues, chat transcripts, document review, and logging pipelines, but human review remains important in high-stakes workflows. (`09e6ccfe08bb` · neutral · service_automation_implications; [[sources/introducing-openai-privacy-filter-01kptv6v2rm47hbeqs6trnpaaj|Introducing OpenAI Privacy Filter]])
- OpenAI reports 96% F1 on PII-Masking-300k, with 94.04% precision and 98.04% recall. (`f515a757e80d` · supporting · benchmark_observations[0]; [[sources/introducing-openai-privacy-filter-01kptv6v2rm47hbeqs6trnpaaj|Introducing OpenAI Privacy Filter]])
- OpenAI reports 97.43% F1 on a corrected version of the benchmark after annotation issues were identified. (`61efa0df1fd1` · supporting · benchmark_observations[1]; [[sources/introducing-openai-privacy-filter-01kptv6v2rm47hbeqs6trnpaaj|Introducing OpenAI Privacy Filter]])
- The source says fine-tuning on a small amount of data raised F1 from 54% to 96% on the domain-adaption benchmark it evaluated. (`a8a6bc4a4041` · supporting · benchmark_observations[2]; [[sources/introducing-openai-privacy-filter-01kptv6v2rm47hbeqs6trnpaaj|Introducing OpenAI Privacy Filter]])
- It masks personally identifiable information in text, including names, addresses, emails, phone numbers, dates, account numbers, and secrets. (`40b72dcc986c` · supporting · core_capabilities[0]; [[sources/introducing-openai-privacy-filter-01kptv6v2rm47hbeqs6trnpaaj|Introducing OpenAI Privacy Filter]])
- It performs token-level classification and span decoding, which helps produce coherent redaction boundaries. (`c9b66f9c5f01` · supporting · core_capabilities[1]; [[sources/introducing-openai-privacy-filter-01kptv6v2rm47hbeqs6trnpaaj|Introducing OpenAI Privacy Filter]])
- It supports long-context inference up to 128,000 tokens, which matters for documents and logs. (`6b318c3dc79e` · supporting · core_capabilities[2]; [[sources/introducing-openai-privacy-filter-01kptv6v2rm47hbeqs6trnpaaj|Introducing OpenAI Privacy Filter]])
- It allows fine-tuning for different privacy policies and data distributions. (`79e03f971420` · supporting · core_capabilities[3]; [[sources/introducing-openai-privacy-filter-01kptv6v2rm47hbeqs6trnpaaj|Introducing OpenAI Privacy Filter]])
- "Privacy Filter is a small model with frontier personal data detection capability. It is designed for high-throughput privacy workflows, and is able to perform context-aware detection of PII in unstructured text. It can run locally" (`b1a9683123e0` · supporting · supporting_snippet; [[sources/introducing-openai-privacy-filter-01kptv6v2rm47hbeqs6trnpaaj|Introducing OpenAI Privacy Filter]])
- The source says performance may vary across languages, scripts, naming conventions, and domains outside the training distribution. It can miss uncommon identifiers and ambiguous private references, and it can over- or under-redact when context is limited, especially in short sequences. OpenAI also notes it is not an anonymization tool or compliance certification. (`917d4e1596c4` · uncertainty · weaknesses_limitations; [[sources/introducing-openai-privacy-filter-01kptv6v2rm47hbeqs6trnpaaj|Introducing OpenAI Privacy Filter]])

### OpenAI Just Open-Sourced the One Thing Every Startup Should Have Built First (2026-04-26)

- The article positions the model against regex-based masking and argues it is better at context-sensitive identification of private names and entities. (`ce1018e5060d` · neutral · comparative_observations[0]; [[sources/openai-just-open-sourced-the-one-thing-every-startup-should-have-built-first-01kqn8asyw9tae3fncffmy92cc|OpenAI Just Open-Sourced the One Thing Every Startup Should Have Built First]])
- It is described as solving a narrow redaction problem more directly than a general-purpose reasoning model such as GPT-5.5, Claude, or Gemini. (`3e5c1a790eaf` · neutral · comparative_observations[1]; [[sources/openai-just-open-sourced-the-one-thing-every-startup-should-have-built-first-01kqn8asyw9tae3fncffmy92cc|OpenAI Just Open-Sourced the One Thing Every Startup Should Have Built First]])
- The piece frames it as a case where a small specialist model can be more appropriate than a much larger frontier model because the task is token labeling, not reasoning. (`7ea7a4f25dbf` · neutral · comparative_observations[2]; [[sources/openai-just-open-sourced-the-one-thing-every-startup-should-have-built-first-01kqn8asyw9tae3fncffmy92cc|OpenAI Just Open-Sourced the One Thing Every Startup Should Have Built First]])
- Use it as a preprocessing layer before any hosted model call, especially for emails, support tickets, transcripts, logs, and retrieval indexing. The article’s long-context design reduces the need to chunk documents before redaction, which simplifies pipeline logic and lowers the chance of breaking entity spans. Its local execution and permissive license make it easier to keep raw text on-premise while still using downstream cloud models for summarization, extraction, or classification. The article does not provide throughput or latency data, so deployment sizing and batch behavior still need measurement on real workloads. (`62fb8e8cd3fc` · neutral · deployment_implications; [[sources/openai-just-open-sourced-the-one-thing-every-startup-should-have-built-first-01kqn8asyw9tae3fncffmy92cc|OpenAI Just Open-Sourced the One Thing Every Startup Should Have Built First]])
- The article presents it as a released open-weight model on Hugging Face and GitHub, under Apache 2.0. That suggests practical reuse potential rather than a closed demo, but the source does not show production adoption or third-party validation. The main maturity signal is the clear packaging around local use, fine-tuning, and evaluation rather than a research-only release. (`c85a4a146235` · neutral · maturity_signals; [[sources/openai-just-open-sourced-the-one-thing-every-startup-should-have-built-first-01kqn8asyw9tae3fncffmy92cc|OpenAI Just Open-Sourced the One Thing Every Startup Should Have Built First]])
- - A local token-classification model for masking personally identifiable information in unstructured text.
- Designed to run on a laptop or in a browser, which keeps unredacted text on the user’s machine instead of sending it to a cloud API.
- Uses a bidirectional labeling approach with BIOES spans and constrained decoding so it can mark entity boundaries cleanly rather than relying on brittle regex rules.
- Exposes operating points that let teams trade recall for precision depending on whether the use case is ingestion, review, or user-facing redaction.
- Can be fine-tuned on small domain-specific datasets when the default categories are not enough for a specialized workflow. (`5fec6192e144` · neutral · operational_profile; [[sources/openai-just-open-sourced-the-one-thing-every-startup-should-have-built-first-01kqn8asyw9tae3fncffmy92cc|OpenAI Just Open-Sourced the One Thing Every Startup Should Have Built First]])
- Local execution suggests low marginal inference cost compared with sending every document to a hosted model for redaction, but the article gives no actual latency or hardware cost numbers. Because it is small and runs on a laptop, it likely fits batch preprocessing or edge-style workflows better than heavy server-side inference, but that remains an inference from the deployment description, not a measured claim. (`f18a002eb028` · neutral · pricing_inference_implications; [[sources/openai-just-open-sourced-the-one-thing-every-startup-should-have-built-first-01kqn8asyw9tae3fncffmy92cc|OpenAI Just Open-Sourced the One Thing Every Startup Should Have Built First]])
- Strong fit as a pre-send filter for support automation pipelines that ingest customer messages, tickets, and transcripts. It can reduce the chance that private data is forwarded into hosted summarization, routing, or response-generation systems, but it does not replace legal review, retention controls, or human oversight. (`df7b96915861` · neutral · service_automation_implications; [[sources/openai-just-open-sourced-the-one-thing-every-startup-should-have-built-first-01kqn8asyw9tae3fncffmy92cc|OpenAI Just Open-Sourced the One Thing Every Startup Should Have Built First]])
- The article reports 96% F1 on the PII-Masking-300k benchmark and 97.43% on a corrected version of that benchmark. (`5397ca0150c8` · supporting · benchmark_observations[0]; [[sources/openai-just-open-sourced-the-one-thing-every-startup-should-have-built-first-01kqn8asyw9tae3fncffmy92cc|OpenAI Just Open-Sourced the One Thing Every Startup Should Have Built First]])
- The article notes that OpenAI flagged annotation issues in the benchmark, which limits how much confidence to place in the published score alone. (`d3d463e6069b` · supporting · benchmark_observations[1]; [[sources/openai-just-open-sourced-the-one-thing-every-startup-should-have-built-first-01kqn8asyw9tae3fncffmy92cc|OpenAI Just Open-Sourced the One Thing Every Startup Should Have Built First]])
- The article says OpenAI reported a jump from 54% F1 to 96% F1 on a domain-adaptation benchmark after light fine-tuning. (`de2222145614` · supporting · benchmark_observations[2]; [[sources/openai-just-open-sourced-the-one-thing-every-startup-should-have-built-first-01kqn8asyw9tae3fncffmy92cc|OpenAI Just Open-Sourced the One Thing Every Startup Should Have Built First]])
- It detects and masks personally identifiable information in unstructured text before the text is sent elsewhere. (`089cae6397ee` · supporting · core_capabilities[0]; [[sources/openai-just-open-sourced-the-one-thing-every-startup-should-have-built-first-01kqn8asyw9tae3fncffmy92cc|OpenAI Just Open-Sourced the One Thing Every Startup Should Have Built First]])
- It can process long documents in one pass because the article says it supports a 128k context window. (`16ce05b9428d` · supporting · core_capabilities[1]; [[sources/openai-just-open-sourced-the-one-thing-every-startup-should-have-built-first-01kqn8asyw9tae3fncffmy92cc|OpenAI Just Open-Sourced the One Thing Every Startup Should Have Built First]])
- It can be tuned for different operating points, so teams can choose more recall or more precision depending on the workflow. (`faebae420458` · supporting · core_capabilities[2]; [[sources/openai-just-open-sourced-the-one-thing-every-startup-should-have-built-first-01kqn8asyw9tae3fncffmy92cc|OpenAI Just Open-Sourced the One Thing Every Startup Should Have Built First]])
- It can be fine-tuned on small labeled datasets to adapt to specialized vocabularies and domain-specific identifiers. (`4911b0dab64a` · supporting · core_capabilities[3]; [[sources/openai-just-open-sourced-the-one-thing-every-startup-should-have-built-first-01kqn8asyw9tae3fncffmy92cc|OpenAI Just Open-Sourced the One Thing Every Startup Should Have Built First]])
- “OpenAI released Privacy Filter. Open weights. Apache 2.0. On Hugging Face and GitHub. It’s a small model: 1.5B total parameters, only 50M active because it’s a sparse Mixture-of-Experts. It runs on a laptop. It runs in a browser. The whole point is that it runs locally, so the unfiltered text never has to leave your machine.” (`34d6b6021250` · supporting · supporting_snippet; [[sources/openai-just-open-sourced-the-one-thing-every-startup-should-have-built-first-01kqn8asyw9tae3fncffmy92cc|OpenAI Just Open-Sourced the One Thing Every Startup Should Have Built First]])
- The model is not a compliance solution by itself, and the article explicitly says it only reduces risk. It may miss categories that are not explicitly represented in its label set, and short or context-poor texts are harder to classify reliably. The reported benchmark numbers are vendor-reported, so real-world quality in your language and domain still needs validation. (`cbc608edd308` · uncertainty · weaknesses_limitations; [[sources/openai-just-open-sourced-the-one-thing-every-startup-should-have-built-first-01kqn8asyw9tae3fncffmy92cc|OpenAI Just Open-Sourced the One Thing Every Startup Should Have Built First]])

## Contradictions / tensions

- The source says performance may vary across languages, scripts, naming conventions, and domains outside the training distribution. It can miss uncommon identifiers and ambiguous private references, and it can over- or under-redact when context is limited, especially in short sequences. OpenAI also notes it is not an anonymization tool or compliance certification. (uncertainty; [[sources/introducing-openai-privacy-filter-01kptv6v2rm47hbeqs6trnpaaj|Introducing OpenAI Privacy Filter]])
- The model is not a compliance solution by itself, and the article explicitly says it only reduces risk. It may miss categories that are not explicitly represented in its label set, and short or context-poor texts are harder to classify reliably. The reported benchmark numbers are vendor-reported, so real-world quality in your language and domain still needs validation. (uncertainty; [[sources/openai-just-open-sourced-the-one-thing-every-startup-should-have-built-first-01kqn8asyw9tae3fncffmy92cc|OpenAI Just Open-Sourced the One Thing Every Startup Should Have Built First]])

## Related pages

No related pages captured.

## Sources

- [[sources/introducing-openai-privacy-filter-01kptv6v2rm47hbeqs6trnpaaj|Introducing OpenAI Privacy Filter]]
- [[sources/openai-just-open-sourced-the-one-thing-every-startup-should-have-built-first-01kqn8asyw9tae3fncffmy92cc|OpenAI Just Open-Sourced the One Thing Every Startup Should Have Built First]]
