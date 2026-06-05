---
title: Message Reducers for Chat State
slug: langgraph-message-reducers
entity_id: topic:langgraph-message-reducers
category: topic
tags:
- agent-systems
- context-engineering
- runtime-architecture
first_seen: '2025-12-31'
last_seen: '2025-12-31'
source_count: 1
evidence_count: 9
source_ids:
- creating-a-stateless-chatbot-in-langgraph-01kqm094n15r71mj5g1xbsk1nj
value_level: medium
confidence: 0.88
synthesis_state: stage1-placeholder
---

# Message Reducers for Chat State

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Message reducers are state-update functions that control how new chat messages are merged into existing state. In a chatbot workflow, they prevent new turns from overwriting prior turns when the system needs to preserve a message list. This matters because chat orchestration often depends on appending, not replacing, conversation history during a run. Reducer choice changes whether the graph behaves like an accumulator or a single-value pipeline. The operational detail is especially important in frameworks that use explicit state objects and node-based execution.

## Examples

The tutorial uses add_messages and explains that without a reducer, a new AI message would overwrite the previous one rather than preserving both messages in the list.

## Key Points

- Reducers decide whether state is appended or replaced.
- Message accumulation is a state-management choice, not just a model choice.
- Reducer behavior can make an implementation look memory-aware inside one run even when cross-turn memory is absent.
- Explicit merge logic helps avoid accidental context loss during graph updates.

## Operational Insight

When building chat flows with explicit state, treat reducers as part of the conversation contract. The wrong reducer can silently erase context or make the graph behave in ways that look stateless even when you intended accumulation.

## Related Topics

- stateless-chatbot-architecture

## Evidence / supporting sources

### Creating a Stateless Chatbot in LangGraph (2025-12-31)

- The tutorial uses add_messages and explains that without a reducer, a new AI message would overwrite the previous one rather than preserving both messages in the list. (`21a92db8f946` · neutral · examples; [[sources/creating-a-stateless-chatbot-in-langgraph-01kqm094n15r71mj5g1xbsk1nj|Creating a Stateless Chatbot in LangGraph]])
- Message reducers are state-update functions that control how new chat messages are merged into existing state. In a chatbot workflow, they prevent new turns from overwriting prior turns when the system needs to preserve a message list. This matters because chat orchestration often depends on appending, not replacing, conversation history during a run. Reducer choice changes whether the graph behaves like an accumulator or a single-value pipeline. The operational detail is especially important in frameworks that use explicit state objects and node-based execution. (`caff079aa5b1` · neutral · knowledge_summary; [[sources/creating-a-stateless-chatbot-in-langgraph-01kqm094n15r71mj5g1xbsk1nj|Creating a Stateless Chatbot in LangGraph]])
- When building chat flows with explicit state, treat reducers as part of the conversation contract. The wrong reducer can silently erase context or make the graph behave in ways that look stateless even when you intended accumulation. (`08f262e1a800` · neutral · operational_insight; [[sources/creating-a-stateless-chatbot-in-langgraph-01kqm094n15r71mj5g1xbsk1nj|Creating a Stateless Chatbot in LangGraph]])
- This is durable because many chat and agent frameworks rely on state reducers or merge logic to control history, tool outputs, and intermediate artifacts. In support automation, reducer behavior determines whether the assistant can keep a useful interaction record during a session. (`665abd73b310` · neutral · relevance_note; [[sources/creating-a-stateless-chatbot-in-langgraph-01kqm094n15r71mj5g1xbsk1nj|Creating a Stateless Chatbot in LangGraph]])
- Reducers decide whether state is appended or replaced. (`69793ce91f67` · supporting · key_points[0]; [[sources/creating-a-stateless-chatbot-in-langgraph-01kqm094n15r71mj5g1xbsk1nj|Creating a Stateless Chatbot in LangGraph]])
- Message accumulation is a state-management choice, not just a model choice. (`39f54de94cc6` · supporting · key_points[1]; [[sources/creating-a-stateless-chatbot-in-langgraph-01kqm094n15r71mj5g1xbsk1nj|Creating a Stateless Chatbot in LangGraph]])
- Reducer behavior can make an implementation look memory-aware inside one run even when cross-turn memory is absent. (`f165d79e045b` · supporting · key_points[2]; [[sources/creating-a-stateless-chatbot-in-langgraph-01kqm094n15r71mj5g1xbsk1nj|Creating a Stateless Chatbot in LangGraph]])
- Explicit merge logic helps avoid accidental context loss during graph updates. (`af917eb5929c` · supporting · key_points[3]; [[sources/creating-a-stateless-chatbot-in-langgraph-01kqm094n15r71mj5g1xbsk1nj|Creating a Stateless Chatbot in LangGraph]])
- "add_messages is a reducer function . Its job is to update the conversation history every time a new message arrives." (`02ed5f4247c0` · supporting · supporting_snippet; [[sources/creating-a-stateless-chatbot-in-langgraph-01kqm094n15r71mj5g1xbsk1nj|Creating a Stateless Chatbot in LangGraph]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- stateless-chatbot-architecture

## Sources

- [[sources/creating-a-stateless-chatbot-in-langgraph-01kqm094n15r71mj5g1xbsk1nj|Creating a Stateless Chatbot in LangGraph]]
