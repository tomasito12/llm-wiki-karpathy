---
title: The war between businesses and hackers enters a perilous new phase
slug: the-war-between-businesses-and-hackers-enters-a-perilous-new-phase-01krjzgpm35mgsws0fz2rpc80q
category: source
source_id: the-war-between-businesses-and-hackers-enters-a-perilous-new-phase-01krjzgpm35mgsws0fz2rpc80q
author: The Economist
publication: Economist
published_date: '2026-05-13'
assessed_as_of: '2026-05-13'
ingested_at: '2026-06-06T21:07:32.057614+00:00'
canonical_url: https://www.economist.com/business/2026/05/13/the-war-between-businesses-and-hackers-enters-a-perilous-new-phase
content_sha256: ca3e07f8903a18b861c0096e1cebfb61cf2758cdf5028a1f87763d4ee1b50911
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
---

# The war between businesses and hackers enters a perilous new phase

This piece is about how AI is making cyber-security more dangerous and more powerful at the same time. Hackers can use new models and agents to find weak spots faster and launch attacks with fewer people. Defenders are also getting new tools, including restricted cyber-focused models and software frameworks that help them test systems. One example in the article says Mozilla used an early Anthropic model to find hundreds of Firefox bugs. The main idea is simple: AI helps both sides, but attackers only need one opening while defenders must cover everything. As of May 13, 2026, the practical takeaway is to treat AI security as a board-level issue, but not to assume the problem is solved.

## Key insights

- Restricted-release cyber models can still be a security risk because other model-makers can replicate the capability set and attackers can use earlier generations already in circulation.
- AI changes the attacker/defender balance because attackers need one successful exploit while defenders need continuous coverage across a growing software surface.
- Agentic AI increases exposure by letting firms build more software and giving attackers more ways to chain tasks against that software.
- AI can materially improve defensive testing: Mozilla said an early model found 271 Firefox vulnerabilities and matched human bug-finding on that version.
- Security teams are responding with harnesses and shared deployment guidance, which suggests practical value lies in operational tooling as much as in model capability.

## Derived knowledge pages

No derived knowledge pages captured.

## Why it matters

The article is useful because it frames AI security as an operational race, not a distant abstract risk. It ties the risk directly to concrete model releases, named firms, and measurable outcomes like CrowdStrike’s reported 89% rise in AI-enhanced attacks in 2025. The most durable point is that access controls on powerful models do not fully contain the threat: once one lab ships a capability, others can follow and attackers can reuse older models. That matters for AI builders because product release decisions, access tiers, and evals are not just policy questions; they affect how easily offensive use cases spread. The article also shows that defensive value is real, but uneven: early models helped Mozilla find vulnerabilities, and Cisco is publishing harness guidance so firms can use general models more safely. That suggests a practical agenda of testing, hardening, and workflow design rather than relying on a single “safe” model. The stakes are significant, but the evidence is still mostly expert judgment and a few illustrative cases rather than a comprehensive benchmark. As of May 13, 2026, the right stance is to treat cyber-capable AI as actionable for security planning and product governance, while continuing to monitor because the text itself says there is no magic bullet yet.

## Limitations / open questions

The evidence base is narrow: the article relies heavily on named expert opinion, a few vendor disclosures, and one Mozilla example rather than broad independent measurement. The reported 89% increase in AI-enhanced attacks is cited through CrowdStrike, but the article does not explain methodology, baseline definitions, or whether the increase reflects reporting changes. Claims that annual CVE counts could rise ten-fold are speculative and presented as speculation, not as observed fact. The article does not quantify how much restricted-release models reduce real-world harm, or whether harnesses materially lower breach rates. It also leaves open the economics of who can sustain constant patching when AI finds vulnerabilities faster than patches can be written. The discussion of agents broadening attack surface is plausible, but the operational details of secure deployment, monitoring, and containment are thin.

## Contradictions / unverified claims

The article presents collaboration between labs and security firms as promising, but its own evidence suggests access controls are only partial barriers because capable models will diffuse and earlier models are already being used by attackers. The optimistic claim that defenders can win decisively at Firefox is a single-case example and may not generalize to other codebases or adversarial settings. The piece also leans on vivid language like “the genie is out of the bottle,” which is rhetorically strong but not a measured security assessment. The biggest unresolved tension is that AI is said to help both sides, yet the article offers no system-level evidence that defensive gains will keep pace with attacker adaptation.

## Source metadata

- Canonical URL: https://www.economist.com/business/2026/05/13/the-war-between-businesses-and-hackers-enters-a-perilous-new-phase
- Raw markdown: `raw/readwise/the-war-between-businesses-and-hackers-enters-a-perilous-new-phase-01krjzgpm35mgsws0fz2rpc80q.md`
- Raw HTML: `raw/readwise/the-war-between-businesses-and-hackers-enters-a-perilous-new-phase-01krjzgpm35mgsws0fz2rpc80q.html`

## Full source text

---
readwise_id: "01krjzgpm35mgsws0fz2rpc80q"
title: "The war between businesses and hackers enters a perilous new phase"
author: "The Economist"
publication: "Economist"
source_url: "https://www.economist.com/business/2026/05/13/the-war-between-businesses-and-hackers-enters-a-perilous-new-phase"
category: "article"
location: "archive"
published_date: "2026-05-13"
saved_at: "2026-05-14T10:11:33.634000+00:00"
updated_at: "2026-05-14T19:50:46.425823+00:00"
tags: ["processed"]
---

AI is making cyber-attacks more powerful and harder to stop. Companies and security firms are racing to use AI to defend themselves. Though the threat is big, better tools and teamwork offer hope to fight back.
