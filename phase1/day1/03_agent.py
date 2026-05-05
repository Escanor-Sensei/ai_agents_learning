"""
=============================================================================
DAY 1 - FILE 03: THE AGENT (LLM-controlled loop with tools)
=============================================================================

CONCEPT (5 lines):
- An agent is an LLM in a LOOP that DECIDES what to do next.
- It has TOOLS — functions it can call to interact with the world.
- The loop: Think → Decide action → Execute tool → Observe result → Think again.
- This is called the ReAct pattern (Reasoning + Acting).
- The LLM controls the flow. The developer just sets up the tools and loop.

AGENT = LLM + LOOP + TOOLS + DECISION-MAKING
That's it. Everything else is implementation detail.
=============================================================================
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool

load_dotenv()

llm = ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL"))


# --- TOOLS ---
# A tool is just a Python function with a description.
# The @tool decorator tells LangChain "the LLM can call this"
# The docstring is CRITICAL — it's how the LLM knows WHEN to use this tool.

@tool
def calculator(expression: str) -> str:
    """Calculate a math expression. Input should be a valid Python math expression like '2 + 3 * 4'."""
    try:
        # eval() is used here for learning purposes only — NEVER in production!
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {e}"


@tool
def get_word_length(word: str) -> str:
    """Get the number of characters in a word. Input should be a single word."""
    return str(len(word))


# --- CREATE THE AGENT ---
# create_react_agent: creates an agent that follows the ReAct pattern
# It generates a prompt that tells the LLM:
#   "You have these tools. Think step by step. Use tools when needed."
from langgraph.prebuilt import create_react_agent

# This one function call hides A LOT of complexity.
# We'll peel it apart in file 07_raw_react.py
agent = create_react_agent(
    model=llm,
    tools=[calculator, get_word_length],
)

# --- RUN THE AGENT ---
print("=" * 60)
print("AGENT: LLM decides what to do")
print("=" * 60)

# Query that requires the agent to DECIDE which tool to use
query = "What is 15 * 23 + 7?"

print(f"\nQuery: {query}\n")

# The agent will:
# 1. Read the query
# 2. DECIDE it needs the calculator tool
# 3. Call calculator("15 * 23 + 7")
# 4. Observe the result
# 5. DECIDE the result is the final answer
# 6. Return the answer
result = agent.invoke({"messages": [("human", query)]})

# Print the full message trace to see the agent's thinking
for msg in result["messages"]:
    role = msg.__class__.__name__
    if hasattr(msg, "tool_calls") and msg.tool_calls:
        print(f"[{role}] Tool calls: {msg.tool_calls}")
    elif hasattr(msg, "content"):
        print(f"[{role}] {msg.content}")
    print()

print("=" * 60)

# --- NOW TRY A QUERY THAT NEEDS TWO TOOLS ---
print("\nQuery that needs TWO tools:")
query2 = "How many characters are in the word 'artificial' and what is that number times 5?"
print(f"Query: {query2}\n")

result2 = agent.invoke({"messages": [("human", query2)]})

for msg in result2["messages"]:
    role = msg.__class__.__name__
    if hasattr(msg, "tool_calls") and msg.tool_calls:
        print(f"[{role}] Tool calls: {msg.tool_calls}")
    elif hasattr(msg, "content"):
        print(f"[{role}] {msg.content}")
    print()

print("=" * 60)

# KEY OBSERVATION:
# - The LLM DECIDED which tools to call (we didn't hardcode it)
# - The LLM DECIDED when to stop (it chose to give a final answer)
# - The LLM could have called tools in any order
# - The LLM could have called the same tool multiple times
#
# THIS is what makes it an agent:
# The LLM is in the driver's seat. We just gave it a car (tools) and a map (prompt).
#
# BUT — what is create_react_agent ACTUALLY DOING?
# See file 07_raw_react.py to find out.
