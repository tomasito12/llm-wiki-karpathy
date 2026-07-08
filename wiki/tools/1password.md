---
title: 1Password
slug: 1password
entity_id: tool:1password
category: tool
tags:
- browser-use
- cloud-hosted
- enterprise-managed
- local-first
first_seen: '2026-03-10'
last_seen: '2026-05-17'
source_count: 2
evidence_count: 24
source_ids:
- 1password-vs-apple-passwords-the-only-comparison-you-need-before-your-next-renewal-01krjqv65fws03dx3ga13t0mzc
- the-first-10-apps-i-install-on-every-new-mac-2026-01kts4hyfyardwc2qg7v9n53dy
value_level: high
confidence: 0.965
synthesis_state: stage1-placeholder
types:
- app
- cloud-saas
- security
---

# 1Password

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
A subscription password manager with cross-platform apps and browser support. It stores logins plus richer secret types and is positioned for users who need more than a single-ecosystem vault.

## Core Capabilities

- It syncs credentials across major operating systems and browsers, so users do not need to stay inside one device ecosystem.
- It supports multiple vaults, which helps separate different classes of credentials and reduce accidental mixing.
- It lets users store more than passwords, including SSH keys, secure notes, API tokens, and documents.
- It supports sharing with anyone, not only users of one vendor's devices, which matters for mixed-device collaboration.
- It includes Travel Mode to hide sensitive vaults when crossing borders.
- It stores credentials so the rest of the software stack can be authenticated without manual password reuse.
- It stores secure documents, which the author uses for identity documents while traveling.
- It fills browser forms reliably enough to reduce repeated login friction across a fresh machine.

## Integration Ecosystem

- It supports Chrome, Firefox, Edge, Brave, and Safari for browser-based autofill and access.
- It runs on macOS, iOS, Windows, Android, and Linux, so it can follow users across heterogeneous device fleets.
- It integrates with browser autofill in the author’s setup.
- It supports family-plan sharing for multi-person use cases.

## Maturity signals

The article presents 1Password as an established product with a long feature history, noting that its feature set has been building since 2005. It is described as broadly available across major operating systems and browsers, which suggests a mature cross-platform footprint rather than a narrow niche app. The source does not provide adoption metrics.

## Strengths

- Works across macOS, iOS, Windows, Android, Linux, and major browsers, which matters when even one device falls outside a single-vendor ecosystem.
- Supports multiple vaults, making it easier to separate personal, work, and special-purpose credentials without mixing them into one flat list.
- Allows sharing with non-Apple users, which is practical when contractors or colleagues use mixed hardware.
- Stores custom fields, secure notes, SSH keys, API tokens, and documents, so it can hold more than basic login pairs.
- Includes Travel Mode, which is a niche but operationally meaningful feature for people who want to hide sensitive vaults during border crossings.

## Weaknesses / limitations

The source frames 1Password as expensive relative to a free alternative, and it offers no free tier. Its feature depth can also be more than many users need, which makes the subscription harder to justify for simple password-only use. The article does not evaluate enterprise policy controls, admin features, or measurable security performance.

## Evidence / supporting sources

### 1Password vs Apple Passwords: The Only Comparison You Need Before Your Next Renewal (2026-03-10)

- It supports Chrome, Firefox, Edge, Brave, and Safari for browser-based autofill and access. (`846ea76322ee` · neutral · integration_ecosystem[0]; [[sources/1password-vs-apple-passwords-the-only-comparison-you-need-before-your-next-renewal-01krjqv65fws03dx3ga13t0mzc|1Password vs Apple Passwords: The Only Comparison You Need Before Your Next Renewal]])
- It runs on macOS, iOS, Windows, Android, and Linux, so it can follow users across heterogeneous device fleets. (`1ecb055e3ed9` · neutral · integration_ecosystem[1]; [[sources/1password-vs-apple-passwords-the-only-comparison-you-need-before-your-next-renewal-01krjqv65fws03dx3ga13t0mzc|1Password vs Apple Passwords: The Only Comparison You Need Before Your Next Renewal]])
- The article presents 1Password as an established product with a long feature history, noting that its feature set has been building since 2005. It is described as broadly available across major operating systems and browsers, which suggests a mature cross-platform footprint rather than a narrow niche app. The source does not provide adoption metrics. (`61395d755e6b` · neutral · maturity_signals; [[sources/1password-vs-apple-passwords-the-only-comparison-you-need-before-your-next-renewal-01krjqv65fws03dx3ga13t0mzc|1Password vs Apple Passwords: The Only Comparison You Need Before Your Next Renewal]])
- Useful when credentials must be available across Apple, Windows, Android, Linux, and multiple browsers. It also fits workflows that involve sharing secrets with people outside one vendor ecosystem or storing structured items beyond passwords. For service automation, the main relevance is keeping operational secrets, notes, and shared credentials organized across mixed-device teams, but the source does not discuss enterprise controls in depth. (`fa8447667d34` · neutral · operational_relevance; [[sources/1password-vs-apple-passwords-the-only-comparison-you-need-before-your-next-renewal-01krjqv65fws03dx3ga13t0mzc|1Password vs Apple Passwords: The Only Comparison You Need Before Your Next Renewal]])
- A subscription password manager with cross-platform apps and browser support. It stores logins plus richer secret types and is positioned for users who need more than a single-ecosystem vault. (`d37da3b3886b` · neutral · short_description; [[sources/1password-vs-apple-passwords-the-only-comparison-you-need-before-your-next-renewal-01krjqv65fws03dx3ga13t0mzc|1Password vs Apple Passwords: The Only Comparison You Need Before Your Next Renewal]])
- - Works across macOS, iOS, Windows, Android, Linux, and major browsers, which matters when even one device falls outside a single-vendor ecosystem.
- Supports multiple vaults, making it easier to separate personal, work, and special-purpose credentials without mixing them into one flat list.
- Allows sharing with non-Apple users, which is practical when contractors or colleagues use mixed hardware.
- Stores custom fields, secure notes, SSH keys, API tokens, and documents, so it can hold more than basic login pairs.
- Includes Travel Mode, which is a niche but operationally meaningful feature for people who want to hide sensitive vaults during border crossings. (`0304fe03409c` · neutral · strengths; [[sources/1password-vs-apple-passwords-the-only-comparison-you-need-before-your-next-renewal-01krjqv65fws03dx3ga13t0mzc|1Password vs Apple Passwords: The Only Comparison You Need Before Your Next Renewal]])
- It syncs credentials across major operating systems and browsers, so users do not need to stay inside one device ecosystem. (`750eea4f51ac` · supporting · core_capabilities[0]; [[sources/1password-vs-apple-passwords-the-only-comparison-you-need-before-your-next-renewal-01krjqv65fws03dx3ga13t0mzc|1Password vs Apple Passwords: The Only Comparison You Need Before Your Next Renewal]])
- It supports multiple vaults, which helps separate different classes of credentials and reduce accidental mixing. (`0dc4bb7dcca6` · supporting · core_capabilities[1]; [[sources/1password-vs-apple-passwords-the-only-comparison-you-need-before-your-next-renewal-01krjqv65fws03dx3ga13t0mzc|1Password vs Apple Passwords: The Only Comparison You Need Before Your Next Renewal]])
- It lets users store more than passwords, including SSH keys, secure notes, API tokens, and documents. (`01cd4503c227` · supporting · core_capabilities[2]; [[sources/1password-vs-apple-passwords-the-only-comparison-you-need-before-your-next-renewal-01krjqv65fws03dx3ga13t0mzc|1Password vs Apple Passwords: The Only Comparison You Need Before Your Next Renewal]])
- It supports sharing with anyone, not only users of one vendor's devices, which matters for mixed-device collaboration. (`2909681bf075` · supporting · core_capabilities[3]; [[sources/1password-vs-apple-passwords-the-only-comparison-you-need-before-your-next-renewal-01krjqv65fws03dx3ga13t0mzc|1Password vs Apple Passwords: The Only Comparison You Need Before Your Next Renewal]])
- It includes Travel Mode to hide sensitive vaults when crossing borders. (`bd657ea047ca` · supporting · core_capabilities[4]; [[sources/1password-vs-apple-passwords-the-only-comparison-you-need-before-your-next-renewal-01krjqv65fws03dx3ga13t0mzc|1Password vs Apple Passwords: The Only Comparison You Need Before Your Next Renewal]])
- 1Password runs on macOS, iOS, Windows, Android, Linux, and supports Chrome, Firefox, Edge, Brave, and Safari. (`ef8f9b1efece` · supporting · supporting_snippet; [[sources/1password-vs-apple-passwords-the-only-comparison-you-need-before-your-next-renewal-01krjqv65fws03dx3ga13t0mzc|1Password vs Apple Passwords: The Only Comparison You Need Before Your Next Renewal]])
- The source frames 1Password as expensive relative to a free alternative, and it offers no free tier. Its feature depth can also be more than many users need, which makes the subscription harder to justify for simple password-only use. The article does not evaluate enterprise policy controls, admin features, or measurable security performance. (`5fa8a24e2071` · uncertainty · weaknesses_limitations; [[sources/1password-vs-apple-passwords-the-only-comparison-you-need-before-your-next-renewal-01krjqv65fws03dx3ga13t0mzc|1Password vs Apple Passwords: The Only Comparison You Need Before Your Next Renewal]])

### The First 10 Apps I Install on Every New Mac (2026) (2026-05-17)

- It integrates with browser autofill in the author’s setup. (`cdc0ee7e13ba` · neutral · integration_ecosystem[0]; [[sources/the-first-10-apps-i-install-on-every-new-mac-2026-01kts4hyfyardwc2qg7v9n53dy|The First 10 Apps I Install on Every New Mac (2026)]])
- It supports family-plan sharing for multi-person use cases. (`8f3295dbc0f1` · neutral · integration_ecosystem[1]; [[sources/the-first-10-apps-i-install-on-every-new-mac-2026-01kts4hyfyardwc2qg7v9n53dy|The First 10 Apps I Install on Every New Mac (2026)]])
- The source treats 1Password as a mature default rather than an experimental tool, and the author has used it since 2017. The mention of family plans, document storage, and browser autofill suggests a broad, established feature set. The price increase in March 2026 indicates an active commercial product with changing subscription economics, not a static utility. (`28096b2cf009` · neutral · maturity_signals; [[sources/the-first-10-apps-i-install-on-every-new-mac-2026-01kts4hyfyardwc2qg7v9n53dy|The First 10 Apps I Install on Every New Mac (2026)]])
- This is a foundational identity and access layer for a Mac workflow. The article ties it to password login, secure document retrieval, and reliable browser autofill, which are all operationally important when setting up or rehydrating a machine. For service automation teams, the durable lesson is that a password manager is not optional plumbing; it is the first dependency after the browser. (`b17d91729b5e` · neutral · operational_relevance; [[sources/the-first-10-apps-i-install-on-every-new-mac-2026-01kts4hyfyardwc2qg7v9n53dy|The First 10 Apps I Install on Every New Mac (2026)]])
- A subscription password manager with secure document storage and browser autofill. The author uses it as the second install because everything else depends on logging in somewhere. (`6ee00538cecc` · neutral · short_description; [[sources/the-first-10-apps-i-install-on-every-new-mac-2026-01kts4hyfyardwc2qg7v9n53dy|The First 10 Apps I Install on Every New Mac (2026)]])
- - Browser autofill is described as reliable enough that the author has not had to fight with it, which matters because authentication friction compounds across many tools.
- Secure document storage solved a real travel workflow problem when the author needed a passport scan from a hotel room.
- Family sharing is a practical fit when the same identity layer must work for both individual and household use.
- The author treats it as the gate to everything else, which reflects its role as operational infrastructure rather than a convenience app. (`b75107523a2b` · neutral · strengths; [[sources/the-first-10-apps-i-install-on-every-new-mac-2026-01kts4hyfyardwc2qg7v9n53dy|The First 10 Apps I Install on Every New Mac (2026)]])
- It stores credentials so the rest of the software stack can be authenticated without manual password reuse. (`8370eef946c6` · supporting · core_capabilities[0]; [[sources/the-first-10-apps-i-install-on-every-new-mac-2026-01kts4hyfyardwc2qg7v9n53dy|The First 10 Apps I Install on Every New Mac (2026)]])
- It stores secure documents, which the author uses for identity documents while traveling. (`ea985bb3cacd` · supporting · core_capabilities[1]; [[sources/the-first-10-apps-i-install-on-every-new-mac-2026-01kts4hyfyardwc2qg7v9n53dy|The First 10 Apps I Install on Every New Mac (2026)]])
- It fills browser forms reliably enough to reduce repeated login friction across a fresh machine. (`10e1630d9e69` · supporting · core_capabilities[2]; [[sources/the-first-10-apps-i-install-on-every-new-mac-2026-01kts4hyfyardwc2qg7v9n53dy|The First 10 Apps I Install on Every New Mac (2026)]])
- "You can’t install anything else without logging in somewhere. So this is always second. I’ve used 1Password since 2017... the secure document storage has saved me twice when I needed a passport scan from a hotel room, and the browser autofill is the only one I’ve never had to fight with." (`c1a20f241fb9` · supporting · supporting_snippet; [[sources/the-first-10-apps-i-install-on-every-new-mac-2026-01kts4hyfyardwc2qg7v9n53dy|The First 10 Apps I Install on Every New Mac (2026)]])
- The main limitation called out in the source is cost: the individual plan is $47.88/year and the family plan is more expensive after a March 2026 price increase. The author also notes Bitwarden and iCloud Keychain as viable alternatives, which means 1Password’s advantage is preference and convenience rather than clear universal necessity. (`54b647aa9770` · uncertainty · weaknesses_limitations; [[sources/the-first-10-apps-i-install-on-every-new-mac-2026-01kts4hyfyardwc2qg7v9n53dy|The First 10 Apps I Install on Every New Mac (2026)]])

## Contradictions / tensions

- The source frames 1Password as expensive relative to a free alternative, and it offers no free tier. Its feature depth can also be more than many users need, which makes the subscription harder to justify for simple password-only use. The article does not evaluate enterprise policy controls, admin features, or measurable security performance. (uncertainty; [[sources/1password-vs-apple-passwords-the-only-comparison-you-need-before-your-next-renewal-01krjqv65fws03dx3ga13t0mzc|1Password vs Apple Passwords: The Only Comparison You Need Before Your Next Renewal]])
- The main limitation called out in the source is cost: the individual plan is $47.88/year and the family plan is more expensive after a March 2026 price increase. The author also notes Bitwarden and iCloud Keychain as viable alternatives, which means 1Password’s advantage is preference and convenience rather than clear universal necessity. (uncertainty; [[sources/the-first-10-apps-i-install-on-every-new-mac-2026-01kts4hyfyardwc2qg7v9n53dy|The First 10 Apps I Install on Every New Mac (2026)]])

## Related pages

No related pages captured.

## Sources

- [[sources/1password-vs-apple-passwords-the-only-comparison-you-need-before-your-next-renewal-01krjqv65fws03dx3ga13t0mzc|1Password vs Apple Passwords: The Only Comparison You Need Before Your Next Renewal]]
- [[sources/the-first-10-apps-i-install-on-every-new-mac-2026-01kts4hyfyardwc2qg7v9n53dy|The First 10 Apps I Install on Every New Mac (2026)]]
