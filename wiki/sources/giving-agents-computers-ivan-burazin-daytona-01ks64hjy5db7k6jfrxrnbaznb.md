---
title: Giving Agents Computers — Ivan Burazin, Daytona
slug: giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb
category: source
tags:
- agent-evals
- agent-systems
- developer-tooling
- distribution
- enterprise-ai
- enterprise-workflows
- execution-environments
- infrastructure
- infrastructure-economics
- long-running-agents
- runtime-architecture
- runtime-systems
source_id: giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb
author: Latent Space
publication: latent.space
published_date: '2026-05-21'
assessed_as_of: '2026-05-21'
ingested_at: '2026-06-06T21:50:49+00:00'
canonical_url: https://www.latent.space/p/daytona
content_sha256: 15810bf8aff0f14cc6e3b0968fb28f10ac5e005a2181eadff7cbe0d24332623f
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
derived_interview_insights:
- interview-insights/2026-05/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb-agent-infrastructure-sales-are-won-by-responsiveness-and-trust-not-just-benchmarks.md
- interview-insights/2026-05/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb-agent-workloads-split-into-steady-background-use-and-spiky-rl-eval-bursts.md
- interview-insights/2026-05/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb-agents-need-stateful-computers-not-disposable-code-runners.md
- interview-insights/2026-05/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb-cli-access-is-a-stronger-agent-interface-than-mcp-for-doing-real-work.md
- interview-insights/2026-05/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb-windows-support-is-strategically-important-because-legacy-work-still-lives-there.md
derived_pages:
- interview-insights/2026-05/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb-agent-infrastructure-sales-are-won-by-responsiveness-and-trust-not-just-benchmarks.md
- interview-insights/2026-05/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb-agent-workloads-split-into-steady-background-use-and-spiky-rl-eval-bursts.md
- interview-insights/2026-05/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb-agents-need-stateful-computers-not-disposable-code-runners.md
- interview-insights/2026-05/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb-cli-access-is-a-stronger-agent-interface-than-mcp-for-doing-real-work.md
- interview-insights/2026-05/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb-windows-support-is-strategically-important-because-legacy-work-still-lives-there.md
---

# Giving Agents Computers — Ivan Burazin, Daytona

This interview is about what AI agents need from infrastructure if they are going to do real work. Daytona’s CEO argues that agents need more than a container or code runner; they need a full computer that can keep state, start fast, and scale up or down quickly. That is why Daytona runs on bare metal and uses its own scheduler instead of relying only on standard cloud patterns. He also says different agent workloads behave very differently: some look like steady human use, while RL and eval jobs spike hard and unpredictably. The practical takeaway is that agent infrastructure is becoming its own product category, with Windows, macOS, and computer-use support becoming important pieces of the stack.

## Key insights

- Daytona’s differentiated primitive is not a sandbox in the narrow sense, but a stateful, composable computer for agents that can persist and resume work.
- The company’s bare-metal plus custom-scheduler design is explicitly tied to low-latency startup and fast concurrent scale-up, including 60 ms single launches and 50,000 launches in about 75 seconds.
- RL and eval traffic creates a very different capacity problem from background agents: bursts can jump from zero to very large CPU demand, which makes average utilization a poor planning metric.
- Burazin treats Windows support as strategically important because much knowledge work still lives inside legacy Windows apps, while macOS support is constrained by Apple’s licensing and snapshot restrictions.
- He argues that agent-era business models should expose consumption APIs rather than rely on SaaS vendors simply reselling tokens, because that does not match the underlying economics or the need to access siloed data.

## Derived knowledge pages

- [[interview-insights/2026-05/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb-agent-infrastructure-sales-are-won-by-responsiveness-and-trust-not-just-benchmarks]]
- [[interview-insights/2026-05/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb-agent-workloads-split-into-steady-background-use-and-spiky-rl-eval-bursts]]
- [[interview-insights/2026-05/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb-agents-need-stateful-computers-not-disposable-code-runners]]
- [[interview-insights/2026-05/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb-cli-access-is-a-stronger-agent-interface-than-mcp-for-doing-real-work]]
- [[interview-insights/2026-05/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb-windows-support-is-strategically-important-because-legacy-work-still-lives-there]]

## Why it matters

The piece is useful because it compresses a live infrastructure design debate into concrete product and workload choices. Daytona is presented not as another generic sandbox vendor, but as a system optimized for agent-specific requirements: persistent state, instant startup, dynamic resize, and high concurrency on bare metal. That is a durable engineering frame because it ties architecture to observed demand rather than to abstract cloud ideology. The interview gives specific operational signals that are worth keeping in mind, including the claim that one customer runs roughly 850,000 sandboxes per day and that RL/eval usage moved from zero to roughly half of Daytona’s mix in months. Those numbers are interview claims, not independently verified benchmarks, but they do show where the product believes the stress points are. The discussion of managed Kubernetes, desktop computers, and computer-use workloads is especially relevant for teams building agent runtimes, eval infrastructure, or tool-using systems. The open-source and support sections also matter: Burazin says the strongest sales lever is responsiveness and trust, not stars or branding, which is a practical reminder that infrastructure products can win on operations as much as on benchmarks. As of 2026-05-21, the article is actionable mainly for teams deciding whether they need stateful agent runtimes, Windows/macOS support, or a bare-metal strategy; the broader “AI cloud” framing is interesting but still somewhat speculative.

## Limitations / open questions

Several of the strongest claims are self-reported, including growth rate, customer scale, and benchmark performance, and the interview does not provide independent verification or methodology. The 60 ms startup and 50,000-at-once numbers are useful signals, but the exact workload, isolation model, and comparison set are not fully specified. The pricing and economics of macOS support are described as constrained by Apple’s licensing and concurrency limits, but the article does not resolve how viable that business becomes at scale. The claim that agent infra should resemble Stripe more than AWS is a strategic analogy, not an empirical result. The discussion of open source helping adoption is mixed: Burazin also says the biggest impact is often better context for integrations rather than major top-of-funnel growth. The article does not deeply quantify security, multi-tenancy, or compliance tradeoffs for bare metal sandboxes.

## Contradictions / unverified claims

The interview leans heavily on a first-principles narrative, but the source does not show controlled comparisons against other sandboxes, Kubernetes setups, or desktop-automation stacks. Some of the market sizing language around agent computers and knowledge work is speculative and extrapolates from broad labor figures rather than measured demand. The claim that the market for every future agent is “infinite” is rhetorically strong and not a model. The argument that SaaS vendors should stop reselling tokens and expose APIs is plausible, but it is still a business thesis, not a proven market law. The strongest credible parts are the concrete operational details and customer pain points; the more sweeping cloud-category predictions should be treated as directional.

## Source metadata

- Canonical URL: https://www.latent.space/p/daytona
- Raw markdown: `raw/readwise/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb.md`
- Raw HTML: `raw/readwise/giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb.html`

## Full source text

---
readwise_id: "01ks64hjy5db7k6jfrxrnbaznb"
title: "Giving Agents Computers — Ivan Burazin, Daytona"
author: "Latent Space"
publication: "latent.space"
source_url: "https://www.latent.space/p/daytona"
category: "podcast"
location: "archive"
published_date: "2026-05-21"
saved_at: "2026-05-21T20:44:56.718000+00:00"
updated_at: "2026-06-01T09:12:12.582823+00:00"
tags: ["processed"]
---

We chat with Daytona's CEO about their insane 74% MoM Growth, 850K Daily Runs, Bare Metal Sandboxes, RL Evals, and the New Agent Cloud
