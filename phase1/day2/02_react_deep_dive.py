"""
=============================================================================
DAY 2 - FILE 02: ReAct DEEP DIVE — Tracing the Agent Loop
=============================================================================

CONCEPT:
- File 01 showed ReAct vs Planning at a high level.
- Now we TRACE a ReAct agent step-by-step to see EXACTLY what happens.
- We'll see: how many LLM calls, which tools, what the agent "thinks."
- Key insight: the agent loop is just LLM → tool → LLM → tool → ... → answer.

ANALOGY FOR .NET DEVS:
- Like adding middleware logging to see every HTTP request/response in your pipeline.
=============================================================================
"""

import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from _tools import calculator, get_word_length, search_web, ALL_TOOLS, trace_messages, count_calls, get_final_answer

load_dotenv()

llm = ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL"))


# =========================
# STEP 1: Multi-step query with full trace
# =========================

print("=" * 60)
print("TRACING: Multi-step query")
print("=" * 60)

agent = create_react_agent(model=llm, tools=ALL_TOOLS)

query = "Search for Python programming, count the characters in 'Python', and calculate 6 * 7"
print(f"Query: {query}\n")

result = agent.invoke({"messages": [("human", query)]})

print("Full message trace:")
trace_messages(result)

llm_calls, tool_calls = count_calls(result)
print(f"\nStats: {llm_calls} LLM calls, {tool_calls} tool calls, {len(result['messages'])} total messages")
print(f"Final answer: {get_final_answer(result)}")


# =========================
# STEP 2: Detailed message inspection
# =========================

print("\n\n" + "=" * 60)
print("INSPECTING: Raw message objects")
print("=" * 60)

print(f"\nTotal messages: {len(result['messages'])}")
for i, msg in enumerate(result["messages"]):
    msg_type = msg.__class__.__name__
    has_tools = hasattr(msg, "tool_calls") and msg.tool_calls
    content_len = len(str(msg.content)) if hasattr(msg, "content") and msg.content else 0
    print(f"  [{i}] {msg_type:15s} | content_len={content_len:4d} | has_tool_calls={has_tools}")

print("""
KEY INSIGHT:
Every message in the trace is a Python object:
  - HumanMessage: your input
  - AIMessage: LLM's response (might contain tool_calls instead of text)
  - ToolMessage: result of executing a tool

The "loop" is: AIMessage with tool_calls → ToolMessage → AIMessage → ...
When AIMessage has text content (no tool_calls), the loop ends.
""")


# =========================
# STEP 3: JSON dump of agent state
# =========================

print("=" * 60)
print("JSON DUMP: Full agent result structure")
print("=" * 60)

for i, msg in enumerate(result["messages"]):
    msg_type = msg.__class__.__name__
    dump = {"index": i, "type": msg_type}

    if hasattr(msg, "content") and msg.content:
        dump["content"] = str(msg.content)[:150]
    if hasattr(msg, "tool_calls") and msg.tool_calls:
        dump["tool_calls"] = [{"name": tc["name"], "args": tc["args"]} for tc in msg.tool_calls]
    if hasattr(msg, "name"):
        dump["tool_name"] = msg.name

    print(json.dumps(dump, indent=2))


print("""
=============================================================================
UNDER THE HOOD: The ReAct Loop Internalized
=============================================================================

1. ITERATION COUNT DEPENDS ON THE QUERY
   - "What is 2+2?" → 1 LLM call (might not even use a tool)
   - "Search X, count Y, calculate Z" → 3-4 LLM calls + 3 tool calls
   - Each iteration: LLM sees ALL previous messages → context grows

2. THE IMPLICIT SYSTEM PROMPT
   When you call create_react_agent, LangGraph adds a system prompt like:
     "You have access to these tools: [schemas]. Use them when needed."
   You never see it, but it's there — it's what makes the LLM call tools.

3. TOOL CALLING IS NOT GUARANTEED
   The LLM MIGHT:
   - Call 0 tools (answer from knowledge)
   - Call 1 tool (simple query)
   - Call the WRONG tool (bad descriptions)
   - Call the same tool twice (retry on error)
   The framework handles all cases — it just keeps looping.

4. TOKEN GROWTH PER ITERATION
   Iteration 1: prompt + query → ~500 tokens
   Iteration 2: + AI message + tool result → ~800 tokens
   Iteration 3: + AI message + tool result → ~1100 tokens
   Each step RESENDS everything from scratch.
   → 10 iterations could mean 5000+ tokens for a simple query.

5. RAW IMPLEMENTATION (What the framework hides)
   The raw version is: HTTP POST → check for functionCall → execute
   → HTTP POST with functionResponse → check again → repeat.
   Wire format for tool result:
   {"role": "user", "parts": [{"functionResponse": {
       "name": "calculator", "response": {"result": "42"}
   }}]}

=============================================================================
""")
