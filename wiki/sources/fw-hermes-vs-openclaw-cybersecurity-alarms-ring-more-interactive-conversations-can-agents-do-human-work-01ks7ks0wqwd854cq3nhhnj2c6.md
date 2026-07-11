---
title: 'Fw: Hermes vs. OpenClaw, Cybersecurity Alarms Ring, More-Interactive Conversations,
  Can Agents Do Human Work?'
slug: fw-hermes-vs-openclaw-cybersecurity-alarms-ring-more-interactive-conversations-can-agents-do-human-work-01ks7ks0wqwd854cq3nhhnj2c6
category: source
tags:
- ai-arms-control
- ai-governance
- ai-safety
- execution-oriented-agents
- human-ai-collaboration
- persistent-agents
- runtime-systems
- tool-centric-agents
- workflow-restructuring
source_id: fw-hermes-vs-openclaw-cybersecurity-alarms-ring-more-interactive-conversations-can-agents-do-human-work-01ks7ks0wqwd854cq3nhhnj2c6
author: Thomas Plischke
publication: WEB.DE News
published_date: '2026-05-22'
assessed_as_of: '2026-05-22'
ingested_at: '2026-06-06T15:34:28.126294+00:00'
canonical_url: mailto:reader-forwarded-email/b6eb5411cebb62548193883be6a3574b
content_sha256: 3e89a7a3221c11cde0819e58747ecb3739de26d4faa44f3a20d8be947df47930
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
derived_signals:
- signals/2026-05/fw-hermes-vs-openclaw-cybersecurity-alarms-ring-more-interactive-conversations-c-agent-memory-and-self-generated-skills-are-becoming-a-differentiator-eab85074c0.md
- signals/2026-05/fw-hermes-vs-openclaw-cybersecurity-alarms-ring-more-interactive-conversations-c-llms-are-becoming-a-practical-force-multiplier-for-cyber-offense-and-0344e351ee.md
- signals/2026-05/fw-hermes-vs-openclaw-cybersecurity-alarms-ring-more-interactive-conversations-c-real-time-multimodal-agents-are-splitting-fast-interaction-from-slow-b39908ea5d.md
derived_trends:
- industry-trends/persistent-agents.md
derived_pages:
- industry-trends/persistent-agents.md
- signals/2026-05/fw-hermes-vs-openclaw-cybersecurity-alarms-ring-more-interactive-conversations-c-agent-memory-and-self-generated-skills-are-becoming-a-differentiator-eab85074c0.md
- signals/2026-05/fw-hermes-vs-openclaw-cybersecurity-alarms-ring-more-interactive-conversations-c-llms-are-becoming-a-practical-force-multiplier-for-cyber-offense-and-0344e351ee.md
- signals/2026-05/fw-hermes-vs-openclaw-cybersecurity-alarms-ring-more-interactive-conversations-c-real-time-multimodal-agents-are-splitting-fast-interaction-from-slow-b39908ea5d.md
---

# Fw: Hermes vs. OpenClaw, Cybersecurity Alarms Ring, More-Interactive Conversations, Can Agents Do Human Work?

This roundup covers four linked AI stories. One is about a new open-source agent, Hermes, that can save memories and turn successful behavior into reusable skills. Another is a real-time multimodal model from Thinking Machines Lab that can listen, watch, and respond without waiting for a turn to end. A third warns that large language models are making some cyberattacks easier to scale and harder to detect. The last one asks whether current agent benchmarks actually match the kinds of work humans do. The common thread is that AI systems are becoming more interactive and more capable, but our tests and defenses are still catching up.

## Key insights

- Hermes Agent’s main distinction is not model quality but its memory-and-skill system, which turns completed tasks into reusable skills and archives stale ones.
- Thinking Machines Lab separates fast conversation handling from slower reasoning, which is a useful architecture pattern for low-latency multimodal agents.
- The Google report frames large language models as dual-use security tools: they can help defenders, but also speed malware mutation, vulnerability discovery, and infrastructure abuse.
- The benchmark study’s main contribution is methodological: it maps agent tasks to labor statistics, revealing that agent benchmarks overrepresent software work relative to broader employment distributions.
- The article’s strongest operational takeaway is that agent evaluation and agent security both need more realism as of 2026-05-22, not just larger model scores.

## Derived knowledge pages

- [[industry-trends/persistent-agents]]
- [[signals/2026-05/fw-hermes-vs-openclaw-cybersecurity-alarms-ring-more-interactive-conversations-c-agent-memory-and-self-generated-skills-are-becoming-a-differentiator-eab85074c0]]
- [[signals/2026-05/fw-hermes-vs-openclaw-cybersecurity-alarms-ring-more-interactive-conversations-c-llms-are-becoming-a-practical-force-multiplier-for-cyber-offense-and-0344e351ee]]
- [[signals/2026-05/fw-hermes-vs-openclaw-cybersecurity-alarms-ring-more-interactive-conversations-c-real-time-multimodal-agents-are-splitting-fast-interaction-from-slow-b39908ea5d]]

## Why it matters

The piece is useful because it compresses several live engineering problems into one issue: how agents remember, how they act in real time, how they are evaluated, and how they are attacked. Hermes Agent is notable less as another chatbot wrapper than as a system that automatically creates skills, curates them, and maintains user/workflow memory; that is a concrete design for making agents accumulate experience instead of starting from scratch on every task. Thinking Machines Lab’s model shows a different architectural direction: split the fast interaction path from the slower reasoning path so audio, video, and text can be handled with short micro-turns and interruptions. That matters for any application that depends on low-latency conversational responsiveness, but the article is still describing a research preview with undisclosed training details and limited availability. The Google cybersecurity report is more than a generic warning because it names specific attack patterns: morphing malware, logical-flaw discovery, obfuscation networks, and attacks on AI infrastructure itself. Its practical value is that it documents why defenders need proactive review and patching workflows that assume adversaries can use LLMs to accelerate exploitation. The benchmark study is also valuable because it challenges a comfortable assumption: that agent benchmarks are already measuring the work agents will matter most for. If benchmark coverage is concentrated in software engineering, then progress on those scores may overstate readiness for administrative, managerial, and other economically important tasks. As of 2026-05-22, the durable takeaway is to treat agent memory, real-time interaction, cyber defense, and benchmark realism as active design constraints, while remaining cautious about claims that are tied to a single product launch or a single mapping study.

## Limitations / open questions

Hermes Agent is described at a high level, but the article does not provide quantitative evidence for its memory quality, skill quality, or real-world task success, so the advantage over OpenClaw could be narrow or workload-dependent. The Thinking Machines Lab model is a closed research preview with undisclosed training data, context window, pricing, and background model architecture, which limits evaluation and adoption planning. Its benchmark results are selective and compare different reasoning settings across systems, so the performance picture may not generalize outside the reported tests. The Google cybersecurity discussion is based on reported research and examples, but the article does not quantify attack prevalence, success rates in the wild, or defensive cost. The benchmark-mapping study is clever, but mapping benchmark tasks to O*NET activities through an LLM introduces subjectivity, and the authors’ sampling strategy means the coverage numbers are approximate rather than exhaustive. None of the items fully answers economics, deployment costs, or how these systems behave under production constraints.

## Contradictions / unverified claims

The roundup sometimes treats capability demos and benchmark wins as evidence of broad practical progress, but the underlying evidence is uneven across items. Hermes Agent’s auto-skilling story is appealing, yet the article provides no direct proof that automatically generated skills outperform carefully curated ones. The Thinking Machines Lab section combines impressive latency numbers with a still-closed system, so the engineering pattern is more solid than the product claim. The cybersecurity section is appropriately cautious, but the leap from model-assisted attacks to industrial-scale attack capacity is still an inference from research reports, not a measured field study. The benchmark paper’s claim that agent tests miss much of human work is plausible, but the mapping exercise depends on taxonomies and translation judgments, so it should be treated as a useful lens rather than a final measurement.

## Source metadata

- Canonical URL: mailto:reader-forwarded-email/b6eb5411cebb62548193883be6a3574b
- Raw markdown: `raw/readwise/fw-hermes-vs-openclaw-cybersecurity-alarms-ring-more-interactive-conversations-can-agents-do-human-work-01ks7ks0wqwd854cq3nhhnj2c6.md`
- Raw HTML: `raw/readwise/fw-hermes-vs-openclaw-cybersecurity-alarms-ring-more-interactive-conversations-can-agents-do-human-work-01ks7ks0wqwd854cq3nhhnj2c6.html`

## Full source text

---
readwise_id: "01ks7ks0wqwd854cq3nhhnj2c6"
title: "Fw: Hermes vs. OpenClaw, Cybersecurity Alarms Ring, More-Interactive Conversations, Can Agents Do Human Work?"
author: "Thomas Plischke"
publication: "WEB.DE News"
source_url: "mailto:reader-forwarded-email/b6eb5411cebb62548193883be6a3574b"
category: "email"
location: "archive"
published_date: "2026-05-22"
saved_at: "2026-05-22T10:30:26.456000+00:00"
updated_at: "2026-05-25T09:50:40.236529+00:00"
tags: ["processed"]
---

Hermes Agent is a new open-source AI that learns skills automatically and remembers user preferences better than OpenClaw. Thinking Machines Lab created a fast, interactive voice model that excels in conversation but still trails the smartest AI in reasoning. Researchers are mapping AI benchmarks to real jobs to see how agents can help many kinds of work beyond coding.
