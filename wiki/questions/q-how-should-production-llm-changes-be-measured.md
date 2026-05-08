---
title: How should production LLM changes be measured?
type: question
created: 2026-05-06
updated: 2026-05-06
tags: [ai-engineering]
---

## Synthesized answer

Treat measurement as a **product discipline**: maintain a small **golden dataset** grounded in real usage (including known-hard edge cases), prefer **binary checks** when possible (correct document retrieved, required facts present, task completed without tool error), and track **aggregate metrics over time** so a change to prompts, retrieval, agent policy, or model version shows **directional movement**. Subjective scalar “helpfulness” scores are weak regression signals compared to task-specific pass/fail criteria tied to failure modes.

## Sources

- [[sources/6-ai-concepts-you-must-master-to-build-production-ready-ai-systems-01kqfz8qd4s3rz9n6sx9dma9a8]]
