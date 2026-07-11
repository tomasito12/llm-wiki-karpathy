---
title: Agents can do the work
slug: agents-can-do-the-work-01krxqx7zdb843b0pk9mambx6a
category: source
tags:
- agent-systems
- ai-engineering
- enterprise-ai
- enterprise-workflows
- organizational-design
- workflow-design
source_id: agents-can-do-the-work-01krxqx7zdb843b0pk9mambx6a
author: Jennifer Murphy
publication: The Intercom Blog
published_date: '2026-05-18'
assessed_as_of: '2026-05-18'
ingested_at: '2026-06-06T16:27:47.558732+00:00'
canonical_url: https://www.intercom.com/blog/agents-can-do-the-work/
content_sha256: e9403fecb39c537519c6f32710e910d1e2af7f2d161b6e40cb36fc9cafbec0aa
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
derived_topics:
- topics/ai-workflow-restructuring.md
- topics/organizational-ai-readiness.md
derived_trends:
- industry-trends/agent-evaluation-shifts-toward-readiness.md
derived_pages:
- industry-trends/agent-evaluation-shifts-toward-readiness.md
- topics/ai-workflow-restructuring.md
- topics/organizational-ai-readiness.md
---

# Agents can do the work

This piece says the real limit on AI agents is often not the model. It is whether the company’s systems, processes, and ownership rules are ready to let the agent act. The author splits that readiness into five levels, from clear content and boundaries to real data access and responsibility for mistakes. In the examples, agents could often do more than teams allowed them to do. So the practical question becomes: what are we ready to automate, and what is missing before the next step?

## Key insights

- Agent evaluations that focus only on capability can miss the real blocker: organizational readiness to permit action.
- Procedural readiness fails when the workflow exists only in human memory, especially for exception paths and decision branches.
- Data readiness is a major cliff because agents need the right object, trustworthy real-time data, and stable API connections at decision time.
- Execution readiness is as much about ownership and recovery as it is about technical ability to make the change.
- When deeper automation is blocked, teams often get useful results by redesigning the agent role to guide users step by step instead of acting for them.

## Derived knowledge pages

- [[industry-trends/agent-evaluation-shifts-toward-readiness]]
- [[topics/ai-workflow-restructuring]]
- [[topics/organizational-ai-readiness]]

## Why it matters

The article is useful because it separates model capability from the surrounding conditions required to use that capability in production. That distinction matters for AI engineering because it changes how teams should evaluate agent projects: a strong benchmark score does not prove an organization can safely expose actions, data, or business operations. The five-part readiness frame is durable because it compresses many common failure modes into operational categories that are easy to inspect: clear policies, clear boundaries, documented procedures, reliable data access, and clear accountability. The strongest practical point is that deeper automation is often blocked by missing infrastructure or unclear ownership rather than by a weak model. That makes the next investment decision less about buying a more powerful agent and more about fixing the process, data, and systems that constrain it. The piece also implies that “guiding” flows can be a legitimate deployed outcome when action is not yet safe or feasible, which is a useful calibration for product teams. The evidence is still limited to the author’s observations across six industries, so the framework is better treated as a planning lens than a validated general law. Actionable as of 2026-05-18, with the readiness framing likely durable if teams keep trying to expand agent permissions without first hardening the underlying operating environment.

## Limitations / open questions

The article gives a useful conceptual framework but not a formal study design, sample sizes, or quantitative outcomes. It cites examples from six industries, but the evidence remains anecdotal and could reflect selection bias toward organizations already interested in automation. The five readiness categories are intuitive, but the boundaries between them are somewhat subjective and may overlap in practice. The piece does not explain how to measure readiness, how to prioritize gaps, or what thresholds justify moving from guiding to executing. It also leaves open the economics of building readiness versus settling for lower-risk agent behavior. Security, compliance, and recovery are mentioned, but not operationalized in detail.

## Contradictions / unverified claims

The article pushes back on the common belief that model capability is the main bottleneck, but it may understate cases where model reliability genuinely is the constraint. Its argument also compresses a messy organizational problem into five buckets; useful for thinking, but not a full implementation method. The claim that most teams are held back more by structure than by AI capability is plausible from the examples, but the piece does not provide enough evidence to treat it as broadly proven.

## Source metadata

- Canonical URL: https://www.intercom.com/blog/agents-can-do-the-work/
- Raw markdown: `raw/readwise/agents-can-do-the-work-01krxqx7zdb843b0pk9mambx6a.md`
- Raw HTML: `raw/readwise/agents-can-do-the-work-01krxqx7zdb843b0pk9mambx6a.html`

## Full source text

---
readwise_id: "01krxqx7zdb843b0pk9mambx6a"
title: "Agents can do the work"
author: "Jennifer Murphy"
publication: "The Intercom Blog"
source_url: "https://www.intercom.com/blog/agents-can-do-the-work/"
category: "rss"
location: "archive"
published_date: "2026-05-18"
saved_at: "2026-05-18T14:30:11.766000+00:00"
updated_at: "2026-06-03T06:40:05.330035+00:00"
tags: ["processed"]
---

Agents today are more capable than ever. When businesses struggle to deploy them, it's a reflection of organizational readiness.
