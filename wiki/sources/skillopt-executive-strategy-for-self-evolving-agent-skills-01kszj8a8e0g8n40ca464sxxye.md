---
title: 'Skillopt: Executive Strategy For Self-Evolving Agent Skills'
slug: skillopt-executive-strategy-for-self-evolving-agent-skills-01kszj8a8e0g8n40ca464sxxye
category: source
tags:
- agent-orchestration
- agent-systems
- ai-engineering
- context-engineering
- optimization-effects
- test-and-verification
source_id: skillopt-executive-strategy-for-self-evolving-agent-skills-01kszj8a8e0g8n40ca464sxxye
author: Yifan Yang, Ziyang Gong, Weiquan Huang, Qihao Yang, Ziwei Zhou, Zisu Huang,
  Yan Li, Xuemei Gao, Qi Dai, Bei Liu, Kai Qiu, Yuqing Yang, Dongdong Chen, Xue Yang,
  Chong Luo
publication: arXiv.org
ingested_at: '2026-06-08T19:47:13.504428+00:00'
canonical_url: https://readwise-assets.s3.amazonaws.com/media/wisereads/articles/skillopt-executive-strategy-fo/1293.pdf
content_sha256: d9b29c1c7fbbcf12e94d278d6b69f13d319e9ad798066fccf71a61ffc6ddcfd5
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
derived_topics:
- topics/agent-skill-optimization.md
- topics/bounded-text-updates-with-validation-gates.md
derived_pages:
- topics/agent-skill-optimization.md
- topics/bounded-text-updates-with-validation-gates.md
---

# Skillopt: Executive Strategy For Self-Evolving Agent Skills

SkillOpt is a way to improve an agent by training its instructions, not its weights. A frozen model runs tasks with a skill file, and a separate optimizer rewrites that file in small steps using feedback from past runs. Each candidate change must beat the old skill on held-out examples, so the system behaves more like controlled training than freeform prompt editing. The paper says this produces compact, readable skill documents that can transfer across models and even across different execution harnesses. In plain terms, it is trying to make agent procedures reusable and auditable instead of one-off prompt hacks.

## Key insights

- Bounded skill edits plus held-out acceptance are the core mechanism; the paper argues this is what makes text-space optimization stable rather than brittle.
- The optimizer keeps failed edits as negative feedback, so rejected proposals still influence later revisions without adding deployment-time cost.
- The slow/meta update is a separate cross-epoch memory for longer-horizon lessons; the deployed skill itself remains compact.
- The strongest gains appear on procedural benchmarks such as spreadsheet work, document QA, and tool-heavy tasks, where rules about formatting, evidence binding, and search discipline matter.
- The learned skills transfer across model scales and across Codex/Claude Code harnesses, which is stronger evidence of reusable procedure than benchmark-specific prompt tuning.

## Derived knowledge pages

- [[topics/agent-skill-optimization]]
- [[topics/bounded-text-updates-with-validation-gates]]

## Why it matters

This paper matters because it proposes a concrete way to treat agent procedure as trainable state, which is a durable abstraction for AI engineering as of the paper's publication date. The key contribution is not just that a model can be prompted differently, but that a skill document can be optimized with explicit controls: batch evidence, edit budgets, validation gating, and rejected-edit memory. That makes the process easier to audit than unconstrained self-revision, and the authors show the resulting artifacts are small enough to inspect and reuse. The evaluation is also broad enough to be operationally interesting: six benchmarks, seven target models, and three harnesses, with gains reported across direct chat, Codex, and Claude Code. The transfer results are especially useful because they suggest the optimized skill is not just a one-off prompt for one model-harness pair. The ablations strengthen the engineering story by showing that the validation gate, bounded edits, and slow/meta update matter more than tweaking batch sizes or the exact schedule. At the same time, the payoff is clearest when there is a reliable scorer and executable feedback, so the method is best read as a controlled optimization recipe for tasks with measurable outcomes. For voice, meetings, or support workflows, the paper does not directly study them, but the procedure is plausibly relevant wherever a reusable, inspectable instruction artifact can steer tool-using agents. Actionable as of the source framing in 2026: promising for benchmarked agent workflows with strong feedback signals, but still something to validate carefully before broad adoption.

## Limitations / open questions

The method depends on scored trajectories and a held-out selection split, so it fits best when there is an automatic verifier, exact-match metric, or otherwise reliable feedback signal. The paper notes that open-ended tasks with subjective or costly evaluation may need stronger human or model-based judgment. Training also requires extra rollout computation plus optimizer-model calls, even though deployment is cheap once best_skill.md is exported. The paper focuses on one compact skill per domain, so it may not scale cleanly to heterogeneous domains that need many disjoint procedures. Transfer is positive in the reported cases, but the authors still warn that skills can encode domain-specific heuristics, so moving them to substantially different models or settings still needs careful held-out testing.

## Contradictions / unverified claims

The strongest claims are empirical and bounded to the reported benchmarks; the paper does not prove that every agent domain benefits from this style of skill training. The comparison set is broad but still limited to the baselines and harnesses studied here, so 'best or tied-best on 52 of 52 cells' should be read in that scope only. The method looks more like disciplined prompt/skill search than a general solution to agent adaptation, especially since it relies on stable evaluators and repeated offline optimization. The transfer results are encouraging, but they do not eliminate the risk that some learned rules are benchmark- or harness-shaped rather than broadly general.

## Source metadata

- Canonical URL: https://readwise-assets.s3.amazonaws.com/media/wisereads/articles/skillopt-executive-strategy-fo/1293.pdf
- Raw markdown: `raw/readwise/skillopt-executive-strategy-for-self-evolving-agent-skills-01kszj8a8e0g8n40ca464sxxye.md`
- Raw HTML: `raw/readwise/skillopt-executive-strategy-for-self-evolving-agent-skills-01kszj8a8e0g8n40ca464sxxye.html`

## Full source text

---
readwise_id: "01kszj8a8e0g8n40ca464sxxye"
title: "Skillopt: Executive Strategy For Self-Evolving Agent Skills"
author: "Yifan Yang, Ziyang Gong, Weiquan Huang, Qihao Yang, Ziwei Zhou, Zisu Huang, Yan Li, Xuemei Gao, Qi Dai, Bei Liu, Kai Qiu, Yuqing Yang, Dongdong Chen, Xue Yang, Chong Luo"
publication: "arXiv.org"
source_url: "https://readwise-assets.s3.amazonaws.com/media/wisereads/articles/skillopt-executive-strategy-fo/1293.pdf"
category: "pdf"
location: "archive"
saved_at: "2026-05-31T17:45:36.781000+00:00"
updated_at: "2026-06-01T06:45:20.118634+00:00"
tags: ["processed"]
---

SkillOpt: Executive Strategy for Self-Evolving Agent Skills Yifan Yang1 , ∗ , ‡ Ziyang Gong2 , ∗ Weiquan Huang3 , ∗ Qihao Yang2 , ∗ Ziwei Zhou4 , ∗ Zisu Huang4 , ∗ Yan Li 2 Xuemei Gao 1 Qi Dai 1 Bei Liu 1 Kai Qiu 1 Yuqing Yang 1 Dongdong Chen 1 Xue Yang2 , ‡ Chong Luo 1 1 Microsoft 2 Shanghai Jiao Tong University 3 Tongji University 4 Fudan University Agent skills today are hand-crafted, generated one-shot, or evolved through loosely controlled self-revision—none of which behaves like a deep-learning optimizer for the skill, and none of which reliably improves over its starting point under feedback. We argue the skill should instead be trained as the external state of a frozen agent, with the same discipline that makes weight-space optimization reproducible. SkillOpt is, to our knowledge, the first systematic controllable text-space optimizer for agent skills: a separate optimizer model turns scored rollouts into bounded add/delete/replace edits on a single skill document, and an edit is accepted only when it strictly improves a held-out validation score. A textual learning-rate budget, rejected-edit buffer, and epoch-wise slow/meta update make skill training stable while adding zero inference-time model calls at deployment. Across six benchmarks, seven target models, and three execution harnesses (direct chat, Codex, Claude Code), SkillOpt is best or tied on all 52 evaluated (model, benchmark, harness) cells and beats every per-cell competitor among human, one-shot LLM, Trace2Skill, TextGrad, GEPA, and EvoSkill skills. On GPT–5.5 it lifts the average no-skill accuracy by + 23 . 5 points in direct chat, by +24 . 8 inside the Codex agentic loop, and by +19 . 1 inside Claude Code. Transfer experiments further show that optimized skill artifacts retain value when moved across model scales, between Codex and Claude Code execution environments, and to a nearby math benchmark without further optimization. Code: https://aka.ms/SkillOpt Correspondence: yifanyang@microsoft.com, yangxue2019-sjtu@sjtu.edu.cn ∗ Equal contribution. ‡ Corresponding authors. 1 Introduction Frontier language models are increasingly deployed as agents, from single-prompt callers to multistep execution harnesses with tools, files, and verifiers [1–4]. In such settings, domain adaptation is no longer only about model weights or prompts: it also requires improving the procedures by which the agent gathers evidence, calls tools, follows domain conventions, and formats outputs [5, 6]. Agent skills provide a natural interface for this procedural adaptation [7, 8]: a skill is a portable natural-language artifact that packages procedures, domain heuristics, tool policies, output constraints, and failure modes, letting a frozen agent adapt through external text. If the recurring object of adaptation is the agent's procedure, the skill document itself should be trainable. Yet weight adaptation is often unavailable for closed frontier models and expensive Figure 1 Overview of SkillOpt. The target model executes tasks with a current skill, an additional frontier optimizer model converts trajectories into bounded add/delete/replace skill edits, and a held-out gate accepts only edits that improve validation performance. Accepted edits are exported as a reusable skill artifact, while rejected edits become negative feedback for later updates. for open ones, while manually written or one-shot skills are brittle under a target domain or harness. Recent systems convert execution experience into reusable textual artifacts—distilling trajectory lessons, refining skill folders via failure analysis, building domain-specific skill libraries, or optimizing prompts from trajectory feedback [9–13]—but leave open a more basic question: if skills are the adaptation layer, how should they be optimized? Our key idea is to treat skill editing as a controllable domain-adaptation process, with the skill document as the external state, an additional frontier model as the optimizer, and trainin…
