---
title: The hardest percentages
slug: the-hardest-percentages-01kp69pz8s9dp41q7ps3z6xftt
category: source
tags:
- agent-systems
- ai-engineering
- prompt-engineering
- support-automation
source_id: the-hardest-percentages-01kp69pz8s9dp41q7ps3z6xftt
author: Pratik Bothra
publication: Intercom
published_date: '2026-04-14'
assessed_as_of: '2026-04-14'
ingested_at: '2026-05-17T15:47:56.559997+00:00'
canonical_url: https://www.intercom.com/blog/the-hardest-percentages/
content_sha256: 2b8825662751478bf1e9499facd90d34620adf2f5fdb999589417070e5ec19cb
derived_how_to:
- how-to/procedural-support-automation.md
derived_topics:
- topics/agentic-workflows.md
- topics/context-engineering.md
derived_pages:
- how-to/procedural-support-automation.md
- topics/agentic-workflows.md
- topics/context-engineering.md
---

# The hardest percentages

This article is about why the hardest customer support questions matter most. It says that easy questions, like looking up information, are already handled well by artificial intelligence tools. The real challenge is when a customer needs several steps taken across different systems, such as checking a policy, verifying data, and making a refund decision. The author argues that these difficult cases take up a lot of time, even if they are a small share of total requests. Intercom presents a product called Fin Procedures that is meant to handle those multi-step tasks. The product lets support teams set up workflows, connect data sources, and even pause for a human to review sensitive steps. The article also says the product is already being used at scale and that satisfaction was higher in a test when it was turned on. The main message is that automation is most valuable when it can do work, not just answer questions. As of 2026-04-14, this is a useful product claim to study, but it is still a vendor-written source.

## Key insights

- Complex support requests can dominate handling time even when they are a minority of the queue.
- A support stack that only answers questions leaves the hardest, highest-stakes cases untouched.
- Branching logic, data connectors, simulations, and rollback matter because procedural automation needs ongoing maintenance.
- Human checkpoints are a practical control for gaps in integrations and sensitive decisions.
- A vendor product is more reusable than a services engagement when many customers need the same workflow surface.

## Derived knowledge pages

- [[how-to/procedural-support-automation]]
- [[topics/agentic-workflows]]
- [[topics/context-engineering]]

## Why it matters

The piece is useful because it separates support automation into informational, personalized, and action-led work, which is a clean way to think about what agents can and cannot do. It grounds the argument in a concrete operational pattern: a small set of rare cases can absorb a large share of team time, so improving those flows can matter more than shaving effort off easy questions. It also adds a product-design point: procedural automation needs editing, testing, rollback, connector monitoring, and human checkpoints, not just a model wrapper. The strongest practical lesson is that a support agent becomes materially more useful when it can execute steps across systems and surface a reviewable trail, rather than stopping at retrieval. The evidence is still vendor-authored, so the claims are best treated as a product case study and design hypothesis, not independent validation. For support and service automation, the closing claim is that the hard cases are the main leverage point, and that claim is actionable as of 2026-04-14 but should be validated against your own queue mix and containment data.

## Limitations / open questions

The evidence comes from a vendor blog, so the usage and satisfaction claims are not independently verified in the source. The randomized 5% holdout is mentioned, but the article does not describe the test design, baseline, confidence interval, or whether the result generalizes across customer segments. The scale claim of 1.5 million conversations and doubling volume is useful but still lacks details on mix, quality thresholds, and failure rates. It is also unclear how often human checkpoints are needed, how much setup effort is still required, and what happens when connectors are missing or policies change frequently. The article does not provide cost, latency, or deflection metrics for the complex workflows themselves.

## Contradictions / unverified claims

The article criticizes bespoke services-heavy setups, but it also acknowledges optional help from a forward-deployed team, so the boundary between product and services is not absolute. The stronger CSAT result is promising, but the source does not show whether the gain comes from broader workflow coverage, better UX, or selection effects in the tested cohort. The claim that procedural automation compounds across customers is plausible, but the article does not quantify that compounding beyond product-level assertions.

## Source metadata

- Canonical URL: https://www.intercom.com/blog/the-hardest-percentages/
- Raw markdown: `raw/readwise/the-hardest-percentages-01kp69pz8s9dp41q7ps3z6xftt.md`
- Raw HTML: `raw/readwise/the-hardest-percentages-01kp69pz8s9dp41q7ps3z6xftt.html`
