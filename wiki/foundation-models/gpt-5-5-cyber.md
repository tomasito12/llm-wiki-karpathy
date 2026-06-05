---
title: GPT-5.5-Cyber
slug: gpt-5-5-cyber
entity_id: model:gpt-5-5-cyber
category: foundation-model
tags:
- enterprise-oriented
- frontier-model
- proprietary-model
- tool-use-capable
first_seen: '2026-05-07'
last_seen: '2026-05-07'
source_count: 1
evidence_count: 14
source_ids:
- scaling-trusted-access-for-cyber-with-gpt-5-5-and-gpt-5-5-cyber-01kr27359qcdmbzw8af82znqzf
value_level: high
confidence: 0.86
synthesis_state: stage1-placeholder
types:
- frontier-model
- proprietary-model
---

# GPT-5.5-Cyber

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
GPT-5.5-Cyber is described as a more permissive preview variant for specialized authorized cyber workflows. The source places it in the narrow slice of tasks where defenders may still face refusals under the safer default model, including authorized red teaming, penetration testing, and controlled validation. Its main distinction is not broad superiority, but access behavior tuned for higher-risk defensive work under stronger verification and monitoring.

## Benchmark Observations

- The source states the preview is not expected to outperform GPT-5.5 across every cyber evaluation.
- No numerical evaluation results are provided.

## Comparative Observations

- Compared with GPT-5.5, GPT-5.5-Cyber is more permissive but not clearly more capable overall.
- The model is positioned as a specialist escalation path rather than the default starting point for most defenders.

## Core Capabilities

- It is designed to be more permissive on security-related requests that are still authorized and defensive.
- It can support advanced workflows such as authorized red teaming and penetration testing under controlled validation.
- It is meant to work with stronger verification and account-level controls than the default model path.

## Maturity signals

As of 2026-05-07, GPT-5.5-Cyber is in limited preview and is explicitly framed as a smaller-scope offering for specialized partners and defenders. The article says it has already been used during alpha testing for automated red-teaming and validation of high-severity vulnerabilities, but that evidence is vendor-controlled and not independently audited in the text.

## Pricing / inference implications

No pricing is provided. The implied cost structure is governance-heavy: the operational burden seems to be verification, monitoring, and partner feedback loops rather than raw model access alone.

## Provider

OpenAI

## Related Models

- GPT-5.5
- GPT-5.4-Cyber

## Service automation implications

Its service-automation relevance is limited to high-trust security operations, not customer-facing automation. The main implication is that some analyst workflows that require exploit validation or red-team-style testing can be supported under a controlled governance model, but only with strict authorization.

## Weaknesses / limitations

OpenAI explicitly says this first preview is not intended to significantly increase cyber capability beyond GPT-5.5 and is primarily trained to be more permissive. The source also says it is not expected to outperform GPT-5.5 across every cyber evaluation, so the value depends on policy fit, not a universal capability gain.

## Evidence / supporting sources

### Scaling Trusted Access for Cyber with GPT-5.5 and GPT-5.5-Cyber (2026-05-07)

- Compared with GPT-5.5, GPT-5.5-Cyber is more permissive but not clearly more capable overall. (`550e645e87ba` · neutral · comparative_observations[0]; [[sources/scaling-trusted-access-for-cyber-with-gpt-5-5-and-gpt-5-5-cyber-01kr27359qcdmbzw8af82znqzf|Scaling Trusted Access for Cyber with GPT-5.5 and GPT-5.5-Cyber]])
- The model is positioned as a specialist escalation path rather than the default starting point for most defenders. (`88ed39863a91` · neutral · comparative_observations[1]; [[sources/scaling-trusted-access-for-cyber-with-gpt-5-5-and-gpt-5-5-cyber-01kr27359qcdmbzw8af82znqzf|Scaling Trusted Access for Cyber with GPT-5.5 and GPT-5.5-Cyber]])
- Deploying GPT-5.5-Cyber implies tighter organizational controls around who can use it and for what. The article says access is paired with stronger verification, account-level controls, misuse monitoring, and approved-use scoping, which makes it suitable only for governed security programs rather than general access. In practice, it looks like a specialist escalation path when GPT-5.5 with Trusted Access for Cyber still refuses authorized work. (`b646ff148dd3` · neutral · deployment_implications; [[sources/scaling-trusted-access-for-cyber-with-gpt-5-5-and-gpt-5-5-cyber-01kr27359qcdmbzw8af82znqzf|Scaling Trusted Access for Cyber with GPT-5.5 and GPT-5.5-Cyber]])
- As of 2026-05-07, GPT-5.5-Cyber is in limited preview and is explicitly framed as a smaller-scope offering for specialized partners and defenders. The article says it has already been used during alpha testing for automated red-teaming and validation of high-severity vulnerabilities, but that evidence is vendor-controlled and not independently audited in the text. (`c690ae340df0` · neutral · maturity_signals; [[sources/scaling-trusted-access-for-cyber-with-gpt-5-5-and-gpt-5-5-cyber-01kr27359qcdmbzw8af82znqzf|Scaling Trusted Access for Cyber with GPT-5.5 and GPT-5.5-Cyber]])
- GPT-5.5-Cyber is described as a more permissive preview variant for specialized authorized cyber workflows. The source places it in the narrow slice of tasks where defenders may still face refusals under the safer default model, including authorized red teaming, penetration testing, and controlled validation. Its main distinction is not broad superiority, but access behavior tuned for higher-risk defensive work under stronger verification and monitoring. (`3dc31968407b` · neutral · operational_profile; [[sources/scaling-trusted-access-for-cyber-with-gpt-5-5-and-gpt-5-5-cyber-01kr27359qcdmbzw8af82znqzf|Scaling Trusted Access for Cyber with GPT-5.5 and GPT-5.5-Cyber]])
- No pricing is provided. The implied cost structure is governance-heavy: the operational burden seems to be verification, monitoring, and partner feedback loops rather than raw model access alone. (`1cc427df68f8` · neutral · pricing_inference_implications; [[sources/scaling-trusted-access-for-cyber-with-gpt-5-5-and-gpt-5-5-cyber-01kr27359qcdmbzw8af82znqzf|Scaling Trusted Access for Cyber with GPT-5.5 and GPT-5.5-Cyber]])
- Its service-automation relevance is limited to high-trust security operations, not customer-facing automation. The main implication is that some analyst workflows that require exploit validation or red-team-style testing can be supported under a controlled governance model, but only with strict authorization. (`dfc29c956a5e` · neutral · service_automation_implications; [[sources/scaling-trusted-access-for-cyber-with-gpt-5-5-and-gpt-5-5-cyber-01kr27359qcdmbzw8af82znqzf|Scaling Trusted Access for Cyber with GPT-5.5 and GPT-5.5-Cyber]])
- The source states the preview is not expected to outperform GPT-5.5 across every cyber evaluation. (`30ea83ede43d` · supporting · benchmark_observations[0]; [[sources/scaling-trusted-access-for-cyber-with-gpt-5-5-and-gpt-5-5-cyber-01kr27359qcdmbzw8af82znqzf|Scaling Trusted Access for Cyber with GPT-5.5 and GPT-5.5-Cyber]])
- No numerical evaluation results are provided. (`3baa05d7d030` · supporting · benchmark_observations[1]; [[sources/scaling-trusted-access-for-cyber-with-gpt-5-5-and-gpt-5-5-cyber-01kr27359qcdmbzw8af82znqzf|Scaling Trusted Access for Cyber with GPT-5.5 and GPT-5.5-Cyber]])
- It is designed to be more permissive on security-related requests that are still authorized and defensive. (`8832a25b06a4` · supporting · core_capabilities[0]; [[sources/scaling-trusted-access-for-cyber-with-gpt-5-5-and-gpt-5-5-cyber-01kr27359qcdmbzw8af82znqzf|Scaling Trusted Access for Cyber with GPT-5.5 and GPT-5.5-Cyber]])
- It can support advanced workflows such as authorized red teaming and penetration testing under controlled validation. (`fc2343bc9c62` · supporting · core_capabilities[1]; [[sources/scaling-trusted-access-for-cyber-with-gpt-5-5-and-gpt-5-5-cyber-01kr27359qcdmbzw8af82znqzf|Scaling Trusted Access for Cyber with GPT-5.5 and GPT-5.5-Cyber]])
- It is meant to work with stronger verification and account-level controls than the default model path. (`066f97aea7c7` · supporting · core_capabilities[2]; [[sources/scaling-trusted-access-for-cyber-with-gpt-5-5-and-gpt-5-5-cyber-01kr27359qcdmbzw8af82znqzf|Scaling Trusted Access for Cyber with GPT-5.5 and GPT-5.5-Cyber]])
- “Today, we are rolling out GPT‑5.5‑Cyber in limited preview to defenders responsible for securing critical infrastructure to support specialized cybersecurity workflows that help protect the broader ecosystem.” (`eb0418add187` · supporting · supporting_snippet; [[sources/scaling-trusted-access-for-cyber-with-gpt-5-5-and-gpt-5-5-cyber-01kr27359qcdmbzw8af82znqzf|Scaling Trusted Access for Cyber with GPT-5.5 and GPT-5.5-Cyber]])
- OpenAI explicitly says this first preview is not intended to significantly increase cyber capability beyond GPT-5.5 and is primarily trained to be more permissive. The source also says it is not expected to outperform GPT-5.5 across every cyber evaluation, so the value depends on policy fit, not a universal capability gain. (`5c1c889eefd0` · uncertainty · weaknesses_limitations; [[sources/scaling-trusted-access-for-cyber-with-gpt-5-5-and-gpt-5-5-cyber-01kr27359qcdmbzw8af82znqzf|Scaling Trusted Access for Cyber with GPT-5.5 and GPT-5.5-Cyber]])

## Contradictions / tensions

- OpenAI explicitly says this first preview is not intended to significantly increase cyber capability beyond GPT-5.5 and is primarily trained to be more permissive. The source also says it is not expected to outperform GPT-5.5 across every cyber evaluation, so the value depends on policy fit, not a universal capability gain. (uncertainty; [[sources/scaling-trusted-access-for-cyber-with-gpt-5-5-and-gpt-5-5-cyber-01kr27359qcdmbzw8af82znqzf|Scaling Trusted Access for Cyber with GPT-5.5 and GPT-5.5-Cyber]])

## Related pages

- GPT-5.4-Cyber
- GPT-5.5

## Sources

- [[sources/scaling-trusted-access-for-cyber-with-gpt-5-5-and-gpt-5-5-cyber-01kr27359qcdmbzw8af82znqzf|Scaling Trusted Access for Cyber with GPT-5.5 and GPT-5.5-Cyber]]
