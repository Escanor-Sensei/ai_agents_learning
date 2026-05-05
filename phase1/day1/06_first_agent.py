"""
=============================================================================
DAY 1 - FILE 06: FIRST REAL AGENT (LangChain, deeper dive)
=============================================================================

Now that you've seen the raw version (file 05), let's understand what
LangChain's create_react_agent ACTUALLY does for you:

1. Converts your @tool functions into JSON schemas (function calling)
2. Sends those schemas to Gemini so it returns structured tool calls
3. Runs the ReAct loop (same while loop as file 05)
4. Handles parsing, error recovery, and message formatting

This file shows you HOW to inspect every piece.
=============================================================================
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

load_dotenv()

llm = ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL"))


# ---- TOOLS ----
# Notice the docstrings — these become the tool descriptions that the LLM reads.
# Bad docstring = LLM picks wrong tool. We'll test this later.

@tool
def calculator(expression: str) -> str:
    """Calculate a math expression. Input should be a valid Python math expression like '2 + 3 * 4'. Returns the numeric result."""
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error calculating '{expression}': {e}"


@tool
def get_word_length(word: str) -> str:
    """Count the number of characters in a word or phrase. Input should be the text to measure. Returns the character count as a number."""
    return str(len(word))


# ---- INSPECT: What does LangChain send to the LLM? ----
# Let's look at the tool schemas LangChain generates

print("=" * 60)
print("TOOL SCHEMAS (what the LLM actually sees)")
print("=" * 60)

tools = [calculator, get_word_length]

for t in tools:
    print(f"\nTool: {t.name}")
    print(f"Description: {t.description}")
    print(f"Schema: {t.args_schema.model_json_schema()}")

# ---- CREATE AGENT ----
agent = create_react_agent(
    model=llm,
    tools=tools,
)

# ---- INSPECT: The agent's graph structure ----
# LangGraph models the agent as a state machine (graph)
print("\n" + "=" * 60)
print("AGENT GRAPH STRUCTURE")
print("=" * 60)

# This shows you the nodes and edges — the skeleton of the agent
graph = agent.get_graph()
print(f"Nodes: {list(graph.nodes.keys())}")
# Print edges
for node_name, node in graph.nodes.items():
    print(f"  Node: {node_name}")

print("\nMermaid diagram (paste into https://mermaid.live to visualize):")
print(graph.draw_mermaid())


# ---- RUN WITH FULL TRACE ----
print("\n" + "=" * 60)
print("RUNNING AGENT WITH FULL MESSAGE TRACE")
print("=" * 60)

query = "What is 15 * 23 + 7?"
print(f"\nQuery: {query}\n")

result = agent.invoke({"messages": [("human", query)]})

# Print EVERY message to see the full loop
print("\n--- Full Message Trace ---")
for i, msg in enumerate(result["messages"]):
    role = msg.__class__.__name__
    print(f"\n[Message {i}] Type: {role}")

    if hasattr(msg, "content") and msg.content:
        print(f"  Content: {msg.content}")

    if hasattr(msg, "tool_calls") and msg.tool_calls:
        for tc in msg.tool_calls:
            print(f"  Tool Call: {tc['name']}({tc['args']})")

    if hasattr(msg, "name") and msg.name:
        print(f"  Tool Name: {msg.name}")

print("\n" + "=" * 60)

# ---- MAP TO RAW VERSION ----
# Message 0: HumanMessage     -> messages[0] in raw version (user query)
# Message 1: AIMessage         -> LLM response with ACTION in raw version
#             (with tool_calls)   (but here it's structured JSON, not text parsing!)
# Message 2: ToolMessage       -> OBSERVATION in raw version (tool result)
# Message 3: AIMessage         -> FINAL_ANSWER in raw version
#
# The STRUCTURE is identical. The MECHANISM is different:
# - Raw: text parsing ("ACTION: calculator\nACTION_INPUT: 15 * 23 + 7")
# - Framework: native function calling (structured JSON, more reliable)


# ---- KEY INSIGHT ----
# What create_react_agent actually creates:
#
# 1. A LangGraph StateGraph with:
#    - "agent" node: calls the LLM with tools bound
#    - "tools" node: executes the tool the LLM chose
#    - Edge: agent -> tools (if tool call) -> agent (loop back)
#    - Edge: agent -> END (if no tool call = final answer)
#
# 2. The state is a dict with "messages" key (list of all messages)
#
# 3. Each iteration:
#    - "agent" node adds an AIMessage (with or without tool_calls)
#    - If tool_calls: "tools" node executes them, adds ToolMessages
#    - Loop continues until AIMessage has no tool_calls
#
# This is EXACTLY our while loop from file 05, but with:
# - Graph-based orchestration instead of a while loop
# - Native function calling instead of text parsing
# - Proper message types instead of raw dicts
