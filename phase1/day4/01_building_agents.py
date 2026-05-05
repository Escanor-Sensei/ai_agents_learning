"""
=============================================================================
DAY 4 - FILE 01: BUILDING YOUR AGENT (From 1 Tool to Multi-Tool)
=============================================================================

CONCEPT:
- Days 1-3 taught the pieces: prompts, agents, ReAct, planning, tools, memory.
- Today we BUILD a complete agent step by step.
- Pattern: LLM + loop + tools + decision-making.
- Start with 1 tool, then add a second to see tool selection in action.
- The LLM DECIDES whether to use tools, which tool, and when to stop.

ANALOGY FOR .NET DEVS:
- Like building your first Web API controller with dependency injection.
- Request → Route to handler → Call service → Return response.
- Adding a second tool = registering a second service in DI.

BUILDS ON:
- Day 1: What an agent is (LLM + loop + tools)
- Day 2: ReAct pattern, planning vs execution
- Day 3: Tool calling, tool descriptions, memory
=============================================================================
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from _tools import calculator, get_word_length, ALL_TOOLS, trace_messages, count_calls

load_dotenv()

llm = ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL"))


# =========================
# STEP 1: Agent with ONE tool
# =========================

print("=" * 60)
print("STEP 1: Agent with 1 tool (calculator)")
print("=" * 60)

agent_1tool = create_react_agent(model=llm, tools=[calculator])

# Math query → should use calculator
result = agent_1tool.invoke({"messages": [("human", "What is 15 * 23 + 7?")]})
print("\nQuery: What is 15 * 23 + 7?")
trace_messages(result)

# Non-math query → should answer directly (no tool)
result2 = agent_1tool.invoke({"messages": [("human", "What is the capital of France?")]})
print("\nQuery: What is the capital of France?")
trace_messages(result2)

print("""
KEY: The agent DECIDES whether to use tools. It's not forced to.
Math query → calls calculator. Knowledge query → answers directly.
This is the difference between an agent and a workflow.
""")


# =========================
# STEP 2: Agent with TWO tools (tool selection)
# =========================

print("=" * 60)
print("STEP 2: Agent with 2 tools (calculator + get_word_length)")
print("=" * 60)

agent_2tools = create_react_agent(model=llm, tools=ALL_TOOLS)
print("  Tools:", [t.name for t in ALL_TOOLS])

# Only needs calculator
print("\nTest 1: Only needs calculator")
r1 = agent_2tools.invoke({"messages": [("human", "What is 99 * 77?")]})
trace_messages(r1)

# Only needs get_word_length
print("\nTest 2: Only needs get_word_length")
r2 = agent_2tools.invoke({"messages": [("human", "How many characters in 'pneumonia'?")]})
trace_messages(r2)

# Needs BOTH tools
print("\nTest 3: Needs BOTH tools (multi-step)")
r3 = agent_2tools.invoke({"messages": [("human",
    "How many characters are in 'elephant'? Multiply that by 12."
)]})
trace_messages(r3)
llm_calls, tool_calls = count_calls(r3)
print(f"  Stats: {llm_calls} LLM calls, {tool_calls} tool calls")

# No tools needed
print("\nTest 4: No tools needed")
r4 = agent_2tools.invoke({"messages": [("human", "Who wrote Romeo and Juliet?")]})
trace_messages(r4)


print("""
=============================================================================
WHAT YOU JUST BUILT
=============================================================================

  ┌─────────────────────────────┐
  │         User Input          │
  └──────────────┬──────────────┘
                 │
  ┌──────────────▼──────────────┐
  │    LLM Decides Next Step    │◄─────────┐
  │  (use tool? give answer?)   │          │
  └──────┬──────────────┬───────┘          │
         │              │                  │
    Use Tool       Give Answer             │
         │              │                  │
  ┌──────▼──────┐  ┌────▼─────┐            │
  │  Execute    │  │  Return  │            │
  │  Tool       │  │  Answer  │            │
  └──────┬──────┘  └──────────┘            │
         │                                 │
  ┌──────▼──────┐                          │
  │  Observe    │──────────────────────────┘
  │  Result     │  (loop back with tool result)
  └─────────────┘

=============================================================================
DEEP THEORY: Under the Hood
=============================================================================

1. WHAT create_react_agent HIDES (~50 lines of logic):

   a) TOOL DECLARATION (JSON schema for each tool)
      TOOL_DECLARATIONS = [{
          "name": "calculator",
          "description": "Calculate a math expression...",
          "parameters": {"type": "object", "properties": {...}}
      }]

   b) LLM CALL (HTTP POST with tool schemas)
      body = {"contents": messages, "tools": [{"functionDeclarations": ...}]}
      response = requests.post(GEMINI_URL, json=body)

   c) THE AGENT LOOP
      for iteration in range(max_iterations):
          response = call_llm(contents)
          if response has functionCall:
              result = execute_tool(name, args)
              contents.append(functionResponse)
          else:
              return response.text  # done

   d) functionResponse WIRE FORMAT
      {"role": "user", "parts": [{"functionResponse": {
          "name": "calculator", "response": {"result": "352"}
      }}]}

2. ADDING TOOLS = ADDING DICT ENTRIES
   The loop is IDENTICAL with 1 or 10 tools.
   Adding a tool = adding to TOOLS dict + TOOL_DECLARATIONS list.
   The loop dispatches by name — it doesn't care how many tools exist.
   This is the DI container pattern: register services, resolve by name.

3. TOOL SELECTION WITH MULTIPLE TOOLS
   The LLM reads ALL descriptions before each decision.
   With 2 tools this is easy. With 10+, descriptions matter MORE.
   Multi-step: get_word_length → observe result → calculator → answer.

=============================================================================
""")
