---
title: Passkey
slug: passkey
entity_id: glossary:passkey
category: glossary
tags:
- governance
first_seen: '2026-04-13'
last_seen: '2026-04-30'
source_count: 3
evidence_count: 12
source_ids:
- introducing-advanced-account-security-01kqfng9s8j91b758trfdhqjyy
- technology-radar-01krc5f8a8a6x35ke2kdjn5d9w
- trusted-access-for-the-next-era-of-cyber-defense-01kp6svpv90410gkqh95k962t0
value_level: high
confidence: 0.7733333333333334
synthesis_state: stage1-placeholder
---

# Passkey

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
A passkey is a phishing-resistant authentication credential based on public-key cryptography that can replace passwords. The private key stays on the user's device or in a credential manager, while the public key is registered with the service.

## Related Terms

- Closed-Resource Information Trust
- FIDO-compliant security key

## Relevance Note

Passkeys matter because authentication is one of the highest-value control points in AI-powered products and admin tooling. Phishing-resistant login reduces account takeover risk for support agents, operators, and end users who interact with conversational systems and internal automation.

## Evidence / supporting sources

### Introducing Advanced Account Security (2026-04-30)

- Passkeys replace the weakest part of many login systems: passwords that can be guessed, reused, or stolen in phishing attacks. A user usually unlocks the passkey with a device gesture such as a fingerprint, face scan, or device PIN, and the site verifies a cryptographic response rather than a typed secret. That makes passkeys harder to phish than passwords because there is no shared password for an attacker to capture and replay. In practice, passkeys matter most for high-value accounts, admin access, and any workflow where a compromise would expose sensitive data or control other systems. (`fe648b4e39c0` · neutral · extended_explanation; [[sources/introducing-advanced-account-security-01kqfng9s8j91b758trfdhqjyy|Introducing Advanced Account Security]])
- A passkey is a phishing-resistant login method that uses cryptographic keys stored on a device or security platform instead of a password. It is designed to reduce account takeover risk by making it harder for attackers to steal reusable credentials. (`d1d9ec95b7c0` · neutral · proposed_definition; [[sources/introducing-advanced-account-security-01kqfng9s8j91b758trfdhqjyy|Introducing Advanced Account Security]])
- Passkeys are increasingly important for securing AI accounts, admin consoles, and workflow tools that can expose private prompts, documents, or connected systems. For conversational AI and service automation stacks, phishing-resistant login reduces the chance that an attacker can hijack a support agent console, admin panel, or automation workspace. (`5ac2bc715a12` · neutral · relevance_note; [[sources/introducing-advanced-account-security-01kqfng9s8j91b758trfdhqjyy|Introducing Advanced Account Security]])
- "Advanced Account Security requires passkeys or physical security keys while disabling password-based login, helping make phishing-resistant sign-in the default for people who need it most." (`b45f9308a41a` · supporting · supporting_snippet; [[sources/introducing-advanced-account-security-01kqfng9s8j91b758trfdhqjyy|Introducing Advanced Account Security]])

### Technology Radar (2026-04-13)

- Passkeys are designed to remove the shared secret that makes passwords and one-time codes vulnerable to interception. Because the credential is bound to the origin, a lookalike site cannot use it the way it can steal a password or intercept an SMS code. In practice, passkeys reduce login friction and can improve sign-in success rates when implemented well. They are especially useful when an organization wants stronger account security without forcing users through awkward extra steps. (`803971ca77ec` · neutral · extended_explanation; [[sources/technology-radar-01krc5f8a8a6x35ke2kdjn5d9w|Technology Radar]])
- A passkey is a phishing-resistant authentication credential based on public-key cryptography that can replace passwords. The private key stays on the user's device or in a credential manager, while the public key is registered with the service. (`ef24d8e0cd5d` · neutral · proposed_definition; [[sources/technology-radar-01krc5f8a8a6x35ke2kdjn5d9w|Technology Radar]])
- Passkeys matter because authentication is one of the highest-value control points in AI-powered products and admin tooling. Phishing-resistant login reduces account takeover risk for support agents, operators, and end users who interact with conversational systems and internal automation. (`860da6f4114e` · neutral · relevance_note; [[sources/technology-radar-01krc5f8a8a6x35ke2kdjn5d9w|Technology Radar]])
- passkeys have matured into Adopt. They are FIDO2 credentials that can replace passwords using asymmetric public-key cryptography. The private key is stored in a hardware-backed secure enclave on the user's device, protected by biometrics or a PIN, and never leaves it. Each credential is origin-bound to its relying-party domain, making passkeys structurally phishing-resistant (`bd5a8d2471ec` · supporting · supporting_snippet; [[sources/technology-radar-01krc5f8a8a6x35ke2kdjn5d9w|Technology Radar]])

### Trusted access for the next era of cyber defense (2026-04-14)

- Passkeys replace memorized passwords with cryptographic authentication tied to a device or account. That makes them harder to steal with phishing, password reuse, or database leaks. In practice, they are useful where account takeover risk is high and where teams want simpler login flows with stronger security. They often work alongside other identity checks rather than replacing every form of access control. (`67ac8f9f9c5f` · neutral · extended_explanation; [[sources/trusted-access-for-the-next-era-of-cyber-defense-01kp6svpv90410gkqh95k962t0|Trusted access for the next era of cyber defense]])
- A passkey is a phishing-resistant login credential that lets a user authenticate without typing a password. It typically relies on device-bound cryptographic keys and user verification such as biometrics or a device PIN. (`cbc5bd2aba49` · neutral · proposed_definition; [[sources/trusted-access-for-the-next-era-of-cyber-defense-01kp6svpv90410gkqh95k962t0|Trusted access for the next era of cyber defense]])
- Passkeys matter in AI systems because access to sensitive model capabilities, admin consoles, and security workflows often depends on strong user authentication. They reduce reliance on passwords alone and can support safer gating for high-risk actions. (`93819da7345e` · neutral · relevance_note; [[sources/trusted-access-for-the-next-era-of-cyber-defense-01kp6svpv90410gkqh95k962t0|Trusted access for the next era of cyber defense]])
- "strong KYC and identity verification" (`ad2b8f17eaa2` · supporting · supporting_snippet; [[sources/trusted-access-for-the-next-era-of-cyber-defense-01kp6svpv90410gkqh95k962t0|Trusted access for the next era of cyber defense]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- Closed-Resource Information Trust
- FIDO-compliant security key

## Sources

- [[sources/introducing-advanced-account-security-01kqfng9s8j91b758trfdhqjyy|Introducing Advanced Account Security]]
- [[sources/technology-radar-01krc5f8a8a6x35ke2kdjn5d9w|Technology Radar]]
- [[sources/trusted-access-for-the-next-era-of-cyber-defense-01kp6svpv90410gkqh95k962t0|Trusted access for the next era of cyber defense]]
