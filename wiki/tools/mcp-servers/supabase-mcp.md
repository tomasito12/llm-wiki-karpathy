---
title: Supabase MCP
type: tool
created: 2026-05-06
updated: 2026-05-07
tags:
  - tools
---

## What problem does this tool solve?

Letting an assistant **draft and run SQL against your database** from plain-language questions instead of hand-writing queries—especially for analytics-style questions.

## Properties

- Compatibility claims in-source: **Supabase, Neon, self-hosted PostgreSQL**.
- **Schema auto-discovery** described so the model knows table structure on connect.
- Explicit caution: keep connections **read-only in production** to avoid destructive changes (example: “deleting rows at 3am”).
- Documentation entry point linked as [Supabase MCP guide](https://supabase.com/docs/guides/getting-started/mcp).
- Example prompts: recent signups, popular products by order count.

## Author assessments

- Positions it as “query your database in plain English” with the user not writing SQL manually. [[sources/6-mcp-servers-that-are-so-good-they-feel-illegal-in-2026-01kqm0f601dmv6jmsa9v3y9ry2]]
- Treats read-only production as a hard operational rule. [[sources/6-mcp-servers-that-are-so-good-they-feel-illegal-in-2026-01kqm0f601dmv6jmsa9v3y9ry2]]

## Sources

- [[sources/6-mcp-servers-that-are-so-good-they-feel-illegal-in-2026-01kqm0f601dmv6jmsa9v3y9ry2]]
