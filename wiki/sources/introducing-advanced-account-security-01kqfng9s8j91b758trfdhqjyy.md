---
title: Introducing Advanced Account Security
slug: introducing-advanced-account-security-01kqfng9s8j91b758trfdhqjyy
category: source
tags:
- ai-governance
- compliance-systems
- governance
source_id: introducing-advanced-account-security-01kqfng9s8j91b758trfdhqjyy
author: OpenAI Blog
publication: OpenAI
published_date: '2026-04-30'
assessed_as_of: '2026-04-30'
ingested_at: '2026-05-17T19:56:50.694355+00:00'
canonical_url: https://openai.com/index/advanced-account-security
content_sha256: 3175a04d1468980f246a2031d419f3dc996519a83160e4cff0f245046bb9d0d7
derived_glossary:
- glossary/fido-compliant-security-key.md
- glossary/passkey.md
derived_tools:
- tools/yubico.md
derived_topics:
- topics/privacy-controls-for-ai-products.md
derived_pages:
- glossary/fido-compliant-security-key.md
- glossary/passkey.md
- tools/yubico.md
- topics/privacy-controls-for-ai-products.md
---

# Introducing Advanced Account Security

OpenAI announced a new security setting for ChatGPT accounts called Advanced Account Security. It is meant for people who want stronger protection against someone taking over their account. The setting puts several safety measures in one place, including stronger sign-in methods, tighter recovery options, and shorter login sessions. It also applies to Codex when someone uses that same account. OpenAI says that if people choose this setting, their conversations will not be used to train the company’s models. The company also partnered with Yubico so people can more easily buy physical security keys, which are a strong way to protect an account from phishing. Some users, including certain trusted defenders working in cyber, will be required to turn it on starting June 1, 2026. The main downside is that recovery becomes stricter, so account access is harder to regain if the user loses the required credentials. As of 2026-04-30, this is a practical security upgrade, but it is only useful for people willing to manage the extra recovery burden.

## Key insights

- Advanced Account Security bundles multiple controls into one opt-in setting, which lowers the activation friction for stronger account protection.
- Disabling password, email, and SMS recovery makes the sign-in path more phishing-resistant, but it also shifts recovery responsibility onto the user.
- Automatic training exclusion is a meaningful privacy control for sensitive conversations, but the post does not describe any auditing or enforcement details.
- The Yubico bundle is a distribution move for hardware keys, but the article gives no evidence about uptake or effectiveness beyond the general security claim.
- The June 1, 2026 requirement for certain cyber users is the only clearly time-bounded policy change in the post.

## Derived knowledge pages

- [[glossary/fido-compliant-security-key]]
- [[glossary/passkey]]
- [[tools/yubico]]
- [[topics/privacy-controls-for-ai-products]]

## Why it matters

The post is useful because it shows how a vendor can package stronger account protection into a single account-level control rather than scattering settings across multiple menus. The most durable operational point is the combination of phishing-resistant sign-in, tighter recovery, and shorter sessions, which reduces attack surface but raises the cost of account recovery. For teams evaluating high-risk account hardening, the concrete design choice is to remove weaker recovery channels and rely on backup passkeys, security keys, and recovery keys instead. The training-exclusion default is also notable because it ties account security to data-handling expectations for sensitive users, although the post does not explain how that exclusion is verified. The Yubico partnership adds a practical distribution channel for physical keys, but the article is promotional and gives no evidence that it changes real adoption. For service automation, the relevant detail is that OpenAI says Advanced Account Security also protects Codex accounts tied to the same login, and that stronger account security will matter in enterprise environments, but the post does not provide rollout detail beyond that. As of 2026-04-30, this is actionable for high-risk users who can tolerate stricter recovery; for everyone else, it is mainly a security option to monitor rather than a universal default.

## Limitations / open questions

The post does not quantify risk reduction, adoption, or usability impact, so the practical benefit is asserted rather than measured. Recovery is intentionally harder, and OpenAI says Support will not help enrolled users with account recovery, which could be operationally costly if a user loses passkeys, security keys, or recovery keys. The training-exclusion promise is not described with technical enforcement detail, so it is unclear how users can audit that behavior. The enterprise extension is mentioned only as a future direction, with no implementation specifics.

## Contradictions / unverified claims

The strongest protections also create the hardest recovery path, which is a real tradeoff rather than a free security upgrade. The Yubico bundle may reduce friction, but the article does not show that preferred pricing or device design will materially change user behavior. The enterprise and cyber-defender claims are forward-looking and should be treated as policy intent, not evidence of broad operational success.

## Source metadata

- Canonical URL: https://openai.com/index/advanced-account-security
- Raw markdown: `raw/readwise/introducing-advanced-account-security-01kqfng9s8j91b758trfdhqjyy.md`
- Raw HTML: `raw/readwise/introducing-advanced-account-security-01kqfng9s8j91b758trfdhqjyy.html`
