---
title: DeepSeek V4
slug: deepseek-v4
entity_id: model:deepseek-v4
category: foundation-model
aliases:
- DeepSeek v4
first_seen: '2026-04-25'
last_seen: '2026-04-26'
source_count: 2
evidence_count: 29
source_ids:
- 10-insane-new-ai-tools-in-2026-i-stayed-up-all-night-playing-with-2nd-one-is-the-coolest-01kqm1ta31yhxbckq1c46n2zja
- the-sequence-radar-849-last-week-in-ai-openai-ships-agents-xai-eyes-cursor-deepseek-and-kimi-advance-01kq4r8j0majmt8av52cng4zw0
value_level: high
confidence: 0.88
synthesis_state: stage1-placeholder
types:
- multimodal-model
- open-weight-model
---

# DeepSeek V4

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
DeepSeek V4 is presented as an open-weight foundation model with native multimodal support for text, images, and video, plus a very large context window of over one million tokens. In the article it is framed as a practical, self-hostable alternative to proprietary APIs, aimed at users who want frontier-style capability with lower direct cloud inference costs if they deploy it themselves.

- Native multimodal input across text, images, and video reduces the need to stitch together separate models or pipelines.
- The >1M token context window is a meaningful fit for long-document analysis, extended sessions, and large retrieval-heavy workflows.
- Open-weight availability gives teams deployment control and makes local or private hosting possible.
- The article claims the model includes a new indexer that cuts computational costs by roughly 50%, which suggests stronger efficiency for high-volume use cases.
- Reported benchmark performance is strong in the article’s framing, with 92% on math and 90% on coding.

## Benchmark Observations

- The article claims 92% accuracy on math benchmarks.
- The article claims 90% accuracy on coding benchmarks.
- No benchmark methodology or evaluator details are provided in the source.

## Comparative Observations

- The article frames DeepSeek V4 as cheaper to operate than rival cloud-priced models if self-hosted.
- It is positioned as a stronger multimodal and long-context option than the prior V3 release.
- The source suggests it is part of a competitive push that has made major AI labs nervous.
- It is discussed alongside GPT-5.5 and Kimi 2.6 as part of a frontier-compression story from open and semi-open models.
- The source implies competition on long context, coding, tool use, latency, and cost rather than on chat quality alone.

## Core Capabilities

- Native multimodal support for text, images, and video
- Context window of over one million tokens
- Open-weight deployment with local or self-hosted use
- Cost-focused indexer claim for more efficient inference
- Benchmarked math and coding performance claims
- It is described as having a 1M context length, which is operationally relevant for long documents, large codebases, and extended agent traces.
- It is described as having agentic capabilities, which indicates it is intended for multi-step workflows that require action rather than only response generation.

## Maturity signals

The article describes DeepSeek V4 as having dropped in early March 2026, which signals it is being treated as a live product rather than a concept. The explicit open-weight and self-hosting language suggests practical availability for deployment. At the same time, the evidence in the source is still mostly announcement-style and benchmark-oriented, so real-world maturity should be confirmed through independent use and serving tests.

## Pricing / inference implications

The source implies a lower-cost ownership model if teams self-host, because it says there is no per-token cloud pricing in that setup. It also claims a new indexer cuts computational costs by roughly fifty percent, which would matter most for high-throughput or long-context workloads. However, the article does not provide infrastructure pricing, so any total-cost comparison should include hardware, ops, and maintenance.

## Provider

DeepSeek

## Related Models

- DeepSeek V3
- Kimi 2.5
- Gemma 4
- GPT-5.5
- Kimi 2.6

## Service automation implications

For service automation, the model is most relevant where long-context reasoning, image/video understanding, and self-hosted deployment matter together. That combination could support automated review pipelines, content analysis systems, or assistant-style services where keeping requests on private infrastructure is important. The article’s claim of lower computational cost also suggests potential value for higher-throughput automation, though the operational savings would depend on actual deployment efficiency.

## Weaknesses / limitations

The article gives benchmark-style claims but no testing methodology, so the accuracy numbers cannot be validated from the source alone. It also does not explain latency, memory footprint, or the practical serving burden of running a very large multimodal open-weight model. Self-hosting may eliminate per-token cloud pricing, but the source does not cover infrastructure, ops, or maintenance costs. Because the evidence is vendor-linked and promotional in tone, independent verification would still be needed before treating the performance claims as settled.

## Evidence / supporting sources

### 10 insane new AI tools in 2026 I stayed up all night playing with: 2nd one is the coolest (2026-04-25)

- The article frames DeepSeek V4 as cheaper to operate than rival cloud-priced models if self-hosted. (`23b1dd88db4b` · neutral · comparative_observations[0]; [[sources/10-insane-new-ai-tools-in-2026-i-stayed-up-all-night-playing-with-2nd-one-is-the-coolest-01kqm1ta31yhxbckq1c46n2zja|10 insane new AI tools in 2026 I stayed up all night playing with: 2nd one is the coolest]])
- It is positioned as a stronger multimodal and long-context option than the prior V3 release. (`f52901183a15` · neutral · comparative_observations[1]; [[sources/10-insane-new-ai-tools-in-2026-i-stayed-up-all-night-playing-with-2nd-one-is-the-coolest-01kqm1ta31yhxbckq1c46n2zja|10 insane new AI tools in 2026 I stayed up all night playing with: 2nd one is the coolest]])
- The source suggests it is part of a competitive push that has made major AI labs nervous. (`0ee621caabf5` · neutral · comparative_observations[2]; [[sources/10-insane-new-ai-tools-in-2026-i-stayed-up-all-night-playing-with-2nd-one-is-the-coolest-01kqm1ta31yhxbckq1c46n2zja|10 insane new AI tools in 2026 I stayed up all night playing with: 2nd one is the coolest]])
- DeepSeek V4 is best understood as a consolidation model for teams that want one system to handle mixed media and long-context tasks without splitting the workflow across multiple specialized models. The open-weight aspect makes it suitable for organizations that need tighter control over data placement or want to integrate the model into internal infrastructure. The long context and multimodal support point to workflows like document-heavy analysis, screenshot-informed coding, and mixed text/image/video review. (`c6a83e391cff` · neutral · deployment_implications; [[sources/10-insane-new-ai-tools-in-2026-i-stayed-up-all-night-playing-with-2nd-one-is-the-coolest-01kqm1ta31yhxbckq1c46n2zja|10 insane new AI tools in 2026 I stayed up all night playing with: 2nd one is the coolest]])
- The article describes DeepSeek V4 as having dropped in early March 2026, which signals it is being treated as a live product rather than a concept. The explicit open-weight and self-hosting language suggests practical availability for deployment. At the same time, the evidence in the source is still mostly announcement-style and benchmark-oriented, so real-world maturity should be confirmed through independent use and serving tests. (`85601b7584c8` · neutral · maturity_signals; [[sources/10-insane-new-ai-tools-in-2026-i-stayed-up-all-night-playing-with-2nd-one-is-the-coolest-01kqm1ta31yhxbckq1c46n2zja|10 insane new AI tools in 2026 I stayed up all night playing with: 2nd one is the coolest]])
- DeepSeek V4 is presented as an open-weight foundation model with native multimodal support for text, images, and video, plus a very large context window of over one million tokens. In the article it is framed as a practical, self-hostable alternative to proprietary APIs, aimed at users who want frontier-style capability with lower direct cloud inference costs if they deploy it themselves.

- Native multimodal input across text, images, and video reduces the need to stitch together separate models or pipelines.
- The >1M token context window is a meaningful fit for long-document analysis, extended sessions, and large retrieval-heavy workflows.
- Open-weight availability gives teams deployment control and makes local or private hosting possible.
- The article claims the model includes a new indexer that cuts computational costs by roughly 50%, which suggests stronger efficiency for high-volume use cases.
- Reported benchmark performance is strong in the article’s framing, with 92% on math and 90% on coding. (`1d383725314f` · neutral · operational_profile; [[sources/10-insane-new-ai-tools-in-2026-i-stayed-up-all-night-playing-with-2nd-one-is-the-coolest-01kqm1ta31yhxbckq1c46n2zja|10 insane new AI tools in 2026 I stayed up all night playing with: 2nd one is the coolest]])
- The source implies a lower-cost ownership model if teams self-host, because it says there is no per-token cloud pricing in that setup. It also claims a new indexer cuts computational costs by roughly fifty percent, which would matter most for high-throughput or long-context workloads. However, the article does not provide infrastructure pricing, so any total-cost comparison should include hardware, ops, and maintenance. (`16ba142eeef2` · neutral · pricing_inference_implications; [[sources/10-insane-new-ai-tools-in-2026-i-stayed-up-all-night-playing-with-2nd-one-is-the-coolest-01kqm1ta31yhxbckq1c46n2zja|10 insane new AI tools in 2026 I stayed up all night playing with: 2nd one is the coolest]])
- For service automation, the model is most relevant where long-context reasoning, image/video understanding, and self-hosted deployment matter together. That combination could support automated review pipelines, content analysis systems, or assistant-style services where keeping requests on private infrastructure is important. The article’s claim of lower computational cost also suggests potential value for higher-throughput automation, though the operational savings would depend on actual deployment efficiency. (`fdb2840dbbea` · neutral · service_automation_implications; [[sources/10-insane-new-ai-tools-in-2026-i-stayed-up-all-night-playing-with-2nd-one-is-the-coolest-01kqm1ta31yhxbckq1c46n2zja|10 insane new AI tools in 2026 I stayed up all night playing with: 2nd one is the coolest]])
- The article claims 92% accuracy on math benchmarks. (`a8782504c20d` · supporting · benchmark_observations[0]; [[sources/10-insane-new-ai-tools-in-2026-i-stayed-up-all-night-playing-with-2nd-one-is-the-coolest-01kqm1ta31yhxbckq1c46n2zja|10 insane new AI tools in 2026 I stayed up all night playing with: 2nd one is the coolest]])
- The article claims 90% accuracy on coding benchmarks. (`9b3a85cee5d7` · supporting · benchmark_observations[1]; [[sources/10-insane-new-ai-tools-in-2026-i-stayed-up-all-night-playing-with-2nd-one-is-the-coolest-01kqm1ta31yhxbckq1c46n2zja|10 insane new AI tools in 2026 I stayed up all night playing with: 2nd one is the coolest]])
- No benchmark methodology or evaluator details are provided in the source. (`f1c87fc39507` · supporting · benchmark_observations[2]; [[sources/10-insane-new-ai-tools-in-2026-i-stayed-up-all-night-playing-with-2nd-one-is-the-coolest-01kqm1ta31yhxbckq1c46n2zja|10 insane new AI tools in 2026 I stayed up all night playing with: 2nd one is the coolest]])
- Native multimodal support for text, images, and video (`1c62698851e9` · supporting · core_capabilities[0]; [[sources/10-insane-new-ai-tools-in-2026-i-stayed-up-all-night-playing-with-2nd-one-is-the-coolest-01kqm1ta31yhxbckq1c46n2zja|10 insane new AI tools in 2026 I stayed up all night playing with: 2nd one is the coolest]])
- Context window of over one million tokens (`7f93b11d2c8d` · supporting · core_capabilities[1]; [[sources/10-insane-new-ai-tools-in-2026-i-stayed-up-all-night-playing-with-2nd-one-is-the-coolest-01kqm1ta31yhxbckq1c46n2zja|10 insane new AI tools in 2026 I stayed up all night playing with: 2nd one is the coolest]])
- Open-weight deployment with local or self-hosted use (`e5550e9f2158` · supporting · core_capabilities[2]; [[sources/10-insane-new-ai-tools-in-2026-i-stayed-up-all-night-playing-with-2nd-one-is-the-coolest-01kqm1ta31yhxbckq1c46n2zja|10 insane new AI tools in 2026 I stayed up all night playing with: 2nd one is the coolest]])
- Cost-focused indexer claim for more efficient inference (`07a82acb3a14` · supporting · core_capabilities[3]; [[sources/10-insane-new-ai-tools-in-2026-i-stayed-up-all-night-playing-with-2nd-one-is-the-coolest-01kqm1ta31yhxbckq1c46n2zja|10 insane new AI tools in 2026 I stayed up all night playing with: 2nd one is the coolest]])
- Benchmarked math and coding performance claims (`643e423013cb` · supporting · core_capabilities[4]; [[sources/10-insane-new-ai-tools-in-2026-i-stayed-up-all-night-playing-with-2nd-one-is-the-coolest-01kqm1ta31yhxbckq1c46n2zja|10 insane new AI tools in 2026 I stayed up all night playing with: 2nd one is the coolest]])
- "DeepSeek V4 dropped in early March 2026 and continued a run that has made every major AI lab nervous. The big shift from V3: full native multimodal support for text, images, and video in one model. Plus a context window of over one million tokens and a new indexer that cuts computational costs by roughly fifty percent. 92% accuracy on math benchmarks, 90% on coding. Open-weight: run it locally or deploy it yourself. No per-token cloud pricing if you self-host." (`35a83539b126` · supporting · supporting_snippet; [[sources/10-insane-new-ai-tools-in-2026-i-stayed-up-all-night-playing-with-2nd-one-is-the-coolest-01kqm1ta31yhxbckq1c46n2zja|10 insane new AI tools in 2026 I stayed up all night playing with: 2nd one is the coolest]])
- The article gives benchmark-style claims but no testing methodology, so the accuracy numbers cannot be validated from the source alone. It also does not explain latency, memory footprint, or the practical serving burden of running a very large multimodal open-weight model. Self-hosting may eliminate per-token cloud pricing, but the source does not cover infrastructure, ops, or maintenance costs. Because the evidence is vendor-linked and promotional in tone, independent verification would still be needed before treating the performance claims as settled. (`3688be25d1d8` · uncertainty · weaknesses_limitations; [[sources/10-insane-new-ai-tools-in-2026-i-stayed-up-all-night-playing-with-2nd-one-is-the-coolest-01kqm1ta31yhxbckq1c46n2zja|10 insane new AI tools in 2026 I stayed up all night playing with: 2nd one is the coolest]])

### The Sequence Radar #849: Last Week in AI: OpenAI Ships Agents, xAI Eyes Cursor, DeepSeek and Kimi Advance (2026-04-26)

- It is discussed alongside GPT-5.5 and Kimi 2.6 as part of a frontier-compression story from open and semi-open models. (`e425d7d9b8f6` · neutral · comparative_observations[0]; [[sources/the-sequence-radar-849-last-week-in-ai-openai-ships-agents-xai-eyes-cursor-deepseek-and-kimi-advance-01kq4r8j0majmt8av52cng4zw0|The Sequence Radar #849: Last Week in AI: OpenAI Ships Agents, xAI Eyes Cursor, DeepSeek and Kimi Advance]])
- The source implies competition on long context, coding, tool use, latency, and cost rather than on chat quality alone. (`89a7c0648eca` · neutral · comparative_observations[1]; [[sources/the-sequence-radar-849-last-week-in-ai-openai-ships-agents-xai-eyes-cursor-deepseek-and-kimi-advance-01kq4r8j0majmt8av52cng4zw0|The Sequence Radar #849: Last Week in AI: OpenAI Ships Agents, xAI Eyes Cursor, DeepSeek and Kimi Advance]])
- Long context can simplify orchestration for code, document, or multi-step agent tasks by reducing the need for aggressive summarization and retrieval. Teams may still need careful evaluation of reliability, latency, and tool-use behavior before relying on it in production. (`dceaea26cd73` · neutral · deployment_implications; [[sources/the-sequence-radar-849-last-week-in-ai-openai-ships-agents-xai-eyes-cursor-deepseek-and-kimi-advance-01kq4r8j0majmt8av52cng4zw0|The Sequence Radar #849: Last Week in AI: OpenAI Ships Agents, xAI Eyes Cursor, DeepSeek and Kimi Advance]])
- The model is presented as a serious competitive entrant in the open and semi-open ecosystem. The source does not provide adoption metrics, so maturity is inferred from its placement in a major AI roundup rather than from hard evidence. (`25232313c908` · neutral · maturity_signals; [[sources/the-sequence-radar-849-last-week-in-ai-openai-ships-agents-xai-eyes-cursor-deepseek-and-kimi-advance-01kq4r8j0majmt8av52cng4zw0|The Sequence Radar #849: Last Week in AI: OpenAI Ships Agents, xAI Eyes Cursor, DeepSeek and Kimi Advance]])
- An open or semi-open frontier model framed as part of the pressure from below on the coding and agentic stack. The source highlights its 1M context length and agentic capabilities as operationally important.

- The 1M context length is notable because very long context can reduce retrieval and chunking overhead in workflows that depend on large codebases or long documents.
- The source says it has 'impressive agentic capabilities,' which suggests it is being considered for execution-oriented rather than purely conversational use.
- It is positioned inside a competitive set where cost, latency, and tool use matter, so it is relevant for teams comparing deployment options below the frontier. (`db7219441813` · neutral · operational_profile; [[sources/the-sequence-radar-849-last-week-in-ai-openai-ships-agents-xai-eyes-cursor-deepseek-and-kimi-advance-01kq4r8j0majmt8av52cng4zw0|The Sequence Radar #849: Last Week in AI: OpenAI Ships Agents, xAI Eyes Cursor, DeepSeek and Kimi Advance]])
- The article does not give price or latency numbers. The main inference is that long-context agentic use cases can change cost structure, so token efficiency and serving economics will matter, but this source does not quantify them. (`3ebeb88343bc` · neutral · pricing_inference_implications; [[sources/the-sequence-radar-849-last-week-in-ai-openai-ships-agents-xai-eyes-cursor-deepseek-and-kimi-advance-01kq4r8j0majmt8av52cng4zw0|The Sequence Radar #849: Last Week in AI: OpenAI Ships Agents, xAI Eyes Cursor, DeepSeek and Kimi Advance]])
- The source does not directly connect this model to service automation, but long context and agentic capabilities could matter for ticket handling or case summarization if validated elsewhere. As of 2026-04-26, that remains an indirect possibility rather than a demonstrated use case. (`ff5895d2740c` · neutral · service_automation_implications; [[sources/the-sequence-radar-849-last-week-in-ai-openai-ships-agents-xai-eyes-cursor-deepseek-and-kimi-advance-01kq4r8j0majmt8av52cng4zw0|The Sequence Radar #849: Last Week in AI: OpenAI Ships Agents, xAI Eyes Cursor, DeepSeek and Kimi Advance]])
- It is described as having a 1M context length, which is operationally relevant for long documents, large codebases, and extended agent traces. (`d2d790507bc9` · supporting · core_capabilities[0]; [[sources/the-sequence-radar-849-last-week-in-ai-openai-ships-agents-xai-eyes-cursor-deepseek-and-kimi-advance-01kq4r8j0majmt8av52cng4zw0|The Sequence Radar #849: Last Week in AI: OpenAI Ships Agents, xAI Eyes Cursor, DeepSeek and Kimi Advance]])
- It is described as having agentic capabilities, which indicates it is intended for multi-step workflows that require action rather than only response generation. (`68000c66af05` · supporting · core_capabilities[1]; [[sources/the-sequence-radar-849-last-week-in-ai-openai-ships-agents-xai-eyes-cursor-deepseek-and-kimi-advance-01kq4r8j0majmt8av52cng4zw0|The Sequence Radar #849: Last Week in AI: OpenAI Ships Agents, xAI Eyes Cursor, DeepSeek and Kimi Advance]])
- DeepSeek v4
The
new version of DeepSeek is here
with 1M context length and impressive agentic capabilities. (`c9c7d4ba66e5` · supporting · supporting_snippet; [[sources/the-sequence-radar-849-last-week-in-ai-openai-ships-agents-xai-eyes-cursor-deepseek-and-kimi-advance-01kq4r8j0majmt8av52cng4zw0|The Sequence Radar #849: Last Week in AI: OpenAI Ships Agents, xAI Eyes Cursor, DeepSeek and Kimi Advance]])
- The source does not provide benchmarking detail or operational failure modes, so the strength claim is largely promotional in this roundup. 'Impressive agentic capabilities' is underspecified and does not tell a practitioner where the model breaks. (`82722e477cb3` · uncertainty · weaknesses_limitations; [[sources/the-sequence-radar-849-last-week-in-ai-openai-ships-agents-xai-eyes-cursor-deepseek-and-kimi-advance-01kq4r8j0majmt8av52cng4zw0|The Sequence Radar #849: Last Week in AI: OpenAI Ships Agents, xAI Eyes Cursor, DeepSeek and Kimi Advance]])

## Contradictions / tensions

- The article gives benchmark-style claims but no testing methodology, so the accuracy numbers cannot be validated from the source alone. It also does not explain latency, memory footprint, or the practical serving burden of running a very large multimodal open-weight model. Self-hosting may eliminate per-token cloud pricing, but the source does not cover infrastructure, ops, or maintenance costs. Because the evidence is vendor-linked and promotional in tone, independent verification would still be needed before treating the performance claims as settled. (uncertainty; [[sources/10-insane-new-ai-tools-in-2026-i-stayed-up-all-night-playing-with-2nd-one-is-the-coolest-01kqm1ta31yhxbckq1c46n2zja|10 insane new AI tools in 2026 I stayed up all night playing with: 2nd one is the coolest]])
- The source does not provide benchmarking detail or operational failure modes, so the strength claim is largely promotional in this roundup. 'Impressive agentic capabilities' is underspecified and does not tell a practitioner where the model breaks. (uncertainty; [[sources/the-sequence-radar-849-last-week-in-ai-openai-ships-agents-xai-eyes-cursor-deepseek-and-kimi-advance-01kq4r8j0majmt8av52cng4zw0|The Sequence Radar #849: Last Week in AI: OpenAI Ships Agents, xAI Eyes Cursor, DeepSeek and Kimi Advance]])

## Related pages

- DeepSeek V3
- GPT-5.5
- Gemma 4
- Kimi 2.5
- Kimi 2.6

## Sources

- [[sources/10-insane-new-ai-tools-in-2026-i-stayed-up-all-night-playing-with-2nd-one-is-the-coolest-01kqm1ta31yhxbckq1c46n2zja|10 insane new AI tools in 2026 I stayed up all night playing with: 2nd one is the coolest]]
- [[sources/the-sequence-radar-849-last-week-in-ai-openai-ships-agents-xai-eyes-cursor-deepseek-and-kimi-advance-01kq4r8j0majmt8av52cng4zw0|The Sequence Radar #849: Last Week in AI: OpenAI Ships Agents, xAI Eyes Cursor, DeepSeek and Kimi Advance]]
