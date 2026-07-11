---
title: Enterprises power agentic workflows in Cloudflare Agent Cloud with OpenAI
slug: enterprises-power-agentic-workflows-in-cloudflare-agent-cloud-with-openai-01kp3ezdp3sph9tehfvhebtbhn
category: source
source_id: enterprises-power-agentic-workflows-in-cloudflare-agent-cloud-with-openai-01kp3ezdp3sph9tehfvhebtbhn
author: OpenAI Blog
publication: OpenAI
published_date: '2026-04-13'
assessed_as_of: '2026-04-13'
ingested_at: '2026-06-06T21:45:34+00:00'
canonical_url: https://openai.com/index/cloudflare-openai-agent-cloud
content_sha256: a12065a98f979dc666433b639bc09c10b3b75bc9a0e1fda74da2d52fead842bc
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
---

# Enterprises power agentic workflows in Cloudflare Agent Cloud with OpenAI

This is an announcement about OpenAI models being made available inside Cloudflare’s Agent Cloud. In plain terms, it means companies using Cloudflare can build agents that use OpenAI models without wiring up a separate deployment stack. The pitch is that these agents can run closer to users, which should make them faster. The article also highlights Codex as a development tool that is now easier to use in Cloudflare’s secure sandbox environment. The main takeaway is not a new algorithm, but a packaging and distribution change for enterprise agent deployment.

## Key insights

- Cloudflare Agent Cloud is being positioned as a production environment for agents that can take actions, not just answer questions.
- The integration explicitly includes GPT-5.4 and Codex, so the announcement covers both runtime inference and development workflows.
- Cloudflare Workers AI is the underlying edge platform, which is the article’s main technical explanation for low-latency, globally distributed execution.
- The post claims the Codex harness is generally available in Cloudflare Sandboxes, with availability in Workers AI described as upcoming.
- The operational significance is real but narrow: the article is about deployment access and platform integration, not model evaluation or new agent capabilities.

## Derived knowledge pages

No derived knowledge pages captured.

## Why it matters

The article matters because it gives a concrete example of how a frontier-model provider and an edge platform are packaging agent deployment for enterprises as of 2026-04-13. The substance is less about a new model breakthrough and more about lowering the friction to run OpenAI-powered agents inside Cloudflare’s environment. That is relevant for teams that already use Cloudflare and want a managed path from model access to production deployment. The mention of secure sandboxes, Workers AI, and Agent Cloud suggests the value proposition is operational: build, test, and run agents within a platform that already handles edge distribution and enterprise infrastructure. The Codex addition broadens the story from agent execution to developer workflow support, since the article says the harness is generally available in Sandboxes and planned for Workers AI. The enterprise customer examples and usage metrics are mostly scale signals from the vendor, so they support interest but do not independently prove performance or ROI. The practical judgment as of 2026-04-13 is to treat this as actionable for Cloudflare-aligned enterprise teams, but still a platform announcement rather than evidence that these agent workflows outperform alternatives in production.

## Limitations / open questions

The article does not provide benchmarks, latency measurements, cost data, reliability results, or security details beyond the phrase 'secure, production-ready environment.' It is unclear what model governance, data isolation, auditability, or failure-handling controls are actually exposed to customers. The piece also does not explain pricing, deployment limits, or how much customization is available for the agents. The claims about scale rely on OpenAI-reported usage figures and named enterprise customers, but the article does not show independent validation or task-level outcomes. The Codex availability in Workers AI is described as future-facing without a concrete date.

## Contradictions / unverified claims

The announcement leans on broad language such as 'real work,' 'production-ready,' and 'secure' without showing evidence in the article. The scale claims are impressive but vendor-supplied, so they should be read as marketing context rather than proof of performance. The promise that edge deployment collapses distance between intelligence and the end user is plausible, but the piece does not quantify whether that matters for the listed enterprise workloads. There is also a tension between broad enterprise availability and the absence of concrete operational detail; the integration may be useful, but the article does not demonstrate it.

## Source metadata

- Canonical URL: https://openai.com/index/cloudflare-openai-agent-cloud
- Raw markdown: `raw/readwise/enterprises-power-agentic-workflows-in-cloudflare-agent-cloud-with-openai-01kp3ezdp3sph9tehfvhebtbhn.md`
- Raw HTML: `raw/readwise/enterprises-power-agentic-workflows-in-cloudflare-agent-cloud-with-openai-01kp3ezdp3sph9tehfvhebtbhn.html`

## Full source text

---
readwise_id: 01kp3ezdp3sph9tehfvhebtbhn
title: Enterprises power agentic workflows in Cloudflare Agent Cloud with OpenAI
author: OpenAI Blog
source_url: https://openai.com/index/cloudflare-openai-agent-cloud
category: rss
location: archive
published_date: '2026-04-13'
saved_at: '2026-04-13T13:02:27.083000+00:00'
updated_at: '2026-05-07T13:41:41.419108+00:00'
tags:
- processed
publication: OpenAI
---

Cloudflare Agent Cloud now lets millions of businesses use OpenAI’s advanced models like GPT-5.4 to build smart AI agents. These agents can handle real tasks such as customer support, system updates, and report generation quickly and securely. This partnership makes it easier for developers to create fast, scalable AI applications for enterprises worldwide.
