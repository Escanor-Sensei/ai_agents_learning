"""
=============================================================================
DAY 2 - FILE 04: PREDICT & DEBUG EXERCISES
=============================================================================

Run each exercise one at a time.
For each: PREDICT what will happen BEFORE running, then run and compare.
=============================================================================
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

load_dotenv()

llm = ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL"))


# =============================================
# EXERCISE 1: Tool with NO description
# =============================================
# PREDICT: What happens when the LLM sees a tool with an empty docstring?
# Does it: a) never call it, b) call it randomly, c) crash?
# MY PREDICTION: _______________________________________________

@tool
def mystery_tool(x: str) -> str:
    """"""  # Empty description!
    return f"Result: {x.upper()}"

def exercise_1():
    agent = create_react_agent(model=llm, tools=[mystery_tool])
    result = agent.invoke({"messages": [("human", "Convert 'hello' to uppercase")]})
    
    tools_used = [tc["name"] for msg in result["messages"]
                  if hasattr(msg, "tool_calls") and msg.tool_calls
                  for tc in msg.tool_calls]
    
    print(f"  Tools used: {tools_used}")
    print(f"  Answer: {result['messages'][-1].content[:150]}")
    print(f"\n  LESSON: Without a description, the LLM guesses from the function name.")
    print(f"  In production, ALWAYS write clear tool descriptions.")


# =============================================
# EXERCISE 2: Tool that randomly fails
# =============================================
# PREDICT: If a tool fails 50% of the time, does the agent:
# a) retry? b) give up? c) answer without the tool?
# MY PREDICTION: _______________________________________________

import random

@tool
def flaky_calculator(expression: str) -> str:
    """Calculate a math expression. Sometimes fails due to server issues."""
    if random.random() < 0.5:
        return "ERROR: Server timeout. Try again."
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"

def exercise_2():
    random.seed(42)
    agent = create_react_agent(model=llm, tools=[flaky_calculator])
    result = agent.invoke({"messages": [("human", "What is 100 * 55?")]})
    
    attempts = sum(1 for msg in result["messages"]
                   if hasattr(msg, "tool_calls") and msg.tool_calls)
    
    print(f"  Tool call attempts: {attempts}")
    print(f"  Answer: {result['messages'][-1].content[:150]}")
    print(f"\n  LESSON: ReAct agents naturally retry on error!")
    print(f"  The LLM sees the error message and decides to try again.")


# =============================================
# RUN ONE AT A TIME — Predict first, then uncomment
# =============================================
if __name__ == "__main__":
    print("=== Exercise 1: Tool with NO description ===")
    exercise_1()
    
    # print("\n=== Exercise 2: Flaky Tool ===")
    # exercise_2()
