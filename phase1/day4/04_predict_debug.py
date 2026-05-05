"""
=============================================================================
DAY 4 - FILE 03: PREDICT & DEBUG EXERCISES
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
# EXERCISE 1: What happens when calculator gets invalid input?
# =============================================
# PREDICT: The LLM sends "hello" to calculator. What happens?
# a) Agent crashes  b) Tool returns error, LLM handles it
# c) Tool returns error, agent crashes  d) LLM refuses to send "hello"
# MY PREDICTION: _______________________________________________

@tool
def calculator(expression: str) -> str:
    """Calculate a math expression. Input should be a valid Python math expression."""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"

def exercise_1():
    agent = create_react_agent(model=llm, tools=[calculator])
    result = agent.invoke({"messages": [("human",
        "Use the calculator to process the word 'hello'"
    )]})
    for msg in result["messages"]:
        role = msg.__class__.__name__
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            print(f"  [{role}] Tool calls: {msg.tool_calls}")
        elif hasattr(msg, "content") and msg.content:
            print(f"  [{role}] {str(msg.content)[:200]}")
    print("\n  LESSON: The tool returns an error string, the LLM sees it and adapts.")
    print("  Always return errors as strings, NEVER raise exceptions in tools!")


# =============================================
# EXERCISE 2: VERY long expression
# =============================================
# PREDICT: We ask for 1+2+3+...+20. Does the LLM:
# a) Send the full expression?  b) Split into chunks?  c) Calculate itself?
# MY PREDICTION: _______________________________________________

def exercise_2():
    agent = create_react_agent(model=llm, tools=[calculator])
    result = agent.invoke({"messages": [("human",
        "Calculate: 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 + 10 + "
        "11 + 12 + 13 + 14 + 15 + 16 + 17 + 18 + 19 + 20"
    )]})
    for msg in result["messages"]:
        role = msg.__class__.__name__
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                expr = tc['args'].get('expression', '')
                print(f"  [{role}] Expression sent: {expr[:100]}")
        elif hasattr(msg, "content") and msg.content:
            print(f"  [{role}] {str(msg.content)[:200]}")
    print("\n  LESSON: The LLM constructs the full expression in one tool call.")
    print("  It trusts the tool to handle the computation.")


# =============================================
# RUN ONE AT A TIME — Predict first, then uncomment
# =============================================
if __name__ == "__main__":
    print("=== Exercise 1: Invalid Tool Input ===")
    exercise_1()

    # print("\n=== Exercise 2: Long Expression ===")
    # exercise_2()
