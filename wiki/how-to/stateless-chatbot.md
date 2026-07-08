---
title: Stateless Chatbot
slug: stateless-chatbot
entity_id: how_to:stateless-chatbot
category: how-to
tags:
- ai-engineering
- workflow-automation
first_seen: '2025-12-31'
last_seen: '2025-12-31'
source_count: 1
evidence_count: 12
source_ids:
- creating-a-stateless-chatbot-in-langgraph-01kqm094n15r71mj5g1xbsk1nj
value_level: high
confidence: 0.98
synthesis_state: stage1-placeholder
---

# Stateless Chatbot

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
This how-to shows the simplest chatbot setup in LangGraph: one that replies to each message on its own and does not carry conversation history from earlier turns. It is useful when you want to understand the basic chat flow first, before adding memory or longer conversation handling. The main problem it solves is showing how a chatbot can run with only the current input in state, and also why that approach breaks for follow-up questions that depend on earlier answers.

## Caveats

This design does not preserve conversation context across turns, so it is not enough for a real multi-turn assistant by itself. The source does not cover persistence, session tracking, or restart behavior, which would be needed for a more continuous chat experience.

## Implementation Steps

- Define a chat state with a Messages field.
- Use add_messages as the reducer so each new message updates the list instead of replacing it.
- Create one chat node that reads state['Messages'] and sends those messages to the model.
- Return the model reply as the updated Messages value.
- Wrap graph execution in a while loop and stop when the user types an exit command.

## Prerequisites

- A Python environment.
- LangGraph installed.
- A chat model client already initialized.

## Evidence / supporting sources

### Creating a Stateless Chatbot in LangGraph (2025-12-31)

- Create a chat state that stores messages, use a reducer so new messages are added cleanly, and build one node that sends the current messages to the model and returns the reply. Then run the graph in a loop so the user can keep asking new questions until they type an exit word. This gives you a working chatbot for simple turn-by-turn replies, but it will not remember earlier turns across separate user messages unless you add memory later. (`aeae142614d3` · neutral · answer_summary; [[sources/creating-a-stateless-chatbot-in-langgraph-01kqm094n15r71mj5g1xbsk1nj|Creating a Stateless Chatbot in LangGraph]])
- Define a chat state with a Messages field. (`047a0ac2dd6f` · neutral · implementation_steps[0]; [[sources/creating-a-stateless-chatbot-in-langgraph-01kqm094n15r71mj5g1xbsk1nj|Creating a Stateless Chatbot in LangGraph]])
- Use add_messages as the reducer so each new message updates the list instead of replacing it. (`2f91bd80af90` · neutral · implementation_steps[1]; [[sources/creating-a-stateless-chatbot-in-langgraph-01kqm094n15r71mj5g1xbsk1nj|Creating a Stateless Chatbot in LangGraph]])
- Create one chat node that reads state['Messages'] and sends those messages to the model. (`7cd07dadc404` · neutral · implementation_steps[2]; [[sources/creating-a-stateless-chatbot-in-langgraph-01kqm094n15r71mj5g1xbsk1nj|Creating a Stateless Chatbot in LangGraph]])
- Return the model reply as the updated Messages value. (`5f7b4934b20e` · neutral · implementation_steps[3]; [[sources/creating-a-stateless-chatbot-in-langgraph-01kqm094n15r71mj5g1xbsk1nj|Creating a Stateless Chatbot in LangGraph]])
- Wrap graph execution in a while loop and stop when the user types an exit command. (`66fd8515c8a8` · neutral · implementation_steps[4]; [[sources/creating-a-stateless-chatbot-in-langgraph-01kqm094n15r71mj5g1xbsk1nj|Creating a Stateless Chatbot in LangGraph]])
- A Python environment. (`f3cbb4257905` · neutral · prerequisites[0]; [[sources/creating-a-stateless-chatbot-in-langgraph-01kqm094n15r71mj5g1xbsk1nj|Creating a Stateless Chatbot in LangGraph]])
- LangGraph installed. (`81884cbb9b0a` · neutral · prerequisites[1]; [[sources/creating-a-stateless-chatbot-in-langgraph-01kqm094n15r71mj5g1xbsk1nj|Creating a Stateless Chatbot in LangGraph]])
- A chat model client already initialized. (`9e85387e95d7` · neutral · prerequisites[2]; [[sources/creating-a-stateless-chatbot-in-langgraph-01kqm094n15r71mj5g1xbsk1nj|Creating a Stateless Chatbot in LangGraph]])
- This how-to shows the simplest chatbot setup in LangGraph: one that replies to each message on its own and does not carry conversation history from earlier turns. It is useful when you want to understand the basic chat flow first, before adding memory or longer conversation handling. The main problem it solves is showing how a chatbot can run with only the current input in state, and also why that approach breaks for follow-up questions that depend on earlier answers. (`4b787b067d1c` · neutral · what_and_problem; [[sources/creating-a-stateless-chatbot-in-langgraph-01kqm094n15r71mj5g1xbsk1nj|Creating a Stateless Chatbot in LangGraph]])
- "This is a basic chatbot application using LangGraph. Stateless means the chatbot does not retain any conversation history." (`a59a14f28338` · supporting · supporting_snippet; [[sources/creating-a-stateless-chatbot-in-langgraph-01kqm094n15r71mj5g1xbsk1nj|Creating a Stateless Chatbot in LangGraph]])
- This design does not preserve conversation context across turns, so it is not enough for a real multi-turn assistant by itself. The source does not cover persistence, session tracking, or restart behavior, which would be needed for a more continuous chat experience. (`dd0361acb977` · uncertainty · caveats; [[sources/creating-a-stateless-chatbot-in-langgraph-01kqm094n15r71mj5g1xbsk1nj|Creating a Stateless Chatbot in LangGraph]])

## Contradictions / tensions

- This design does not preserve conversation context across turns, so it is not enough for a real multi-turn assistant by itself. The source does not cover persistence, session tracking, or restart behavior, which would be needed for a more continuous chat experience. (uncertainty; [[sources/creating-a-stateless-chatbot-in-langgraph-01kqm094n15r71mj5g1xbsk1nj|Creating a Stateless Chatbot in LangGraph]])

## Related pages

- [[how-to/context-compaction|Context Compaction]]

## Sources

- [[sources/creating-a-stateless-chatbot-in-langgraph-01kqm094n15r71mj5g1xbsk1nj|Creating a Stateless Chatbot in LangGraph]]
