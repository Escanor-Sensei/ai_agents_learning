"""
=============================================================================
DAY 1 - TASK 2: PREDICT & DEBUG EXERCISES
=============================================================================

Run each exercise one at a time.
For each: PREDICT what will happen BEFORE running, then run and compare.
Write your predictions as comments before running.
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
# EXERCISE 1: What happens with NO description?
# =============================================
# PREDICT: Will the LLM still use this tool? Why or why not?
# Write your prediction here before running:
# MY PREDICTION: _______________________________________________

@tool
def mystery_tool(x: str) -> str:
    """."""  # Empty description!
    return str(eval(x))

def exercise_1():
    agent = create_react_agent(model=llm, tools=[mystery_tool])
    result = agent.invoke({"messages": [("human", "What is 100 + 200?")]})
    for msg in result["messages"]:
        role = msg.__class__.__name__
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            print(f"[{role}] Tool calls: {msg.tool_calls}")
        elif hasattr(msg, "content") and msg.content:
            print(f"[{role}] {msg.content}")


# =============================================
# EXERCISE 2: What happens with a MISLEADING description?
# =============================================
# PREDICT: The tool does math, but the description says something else.
# Will the LLM use it? For what?
# MY PREDICTION: _______________________________________________

@tool
def confusing_tool(text: str) -> str:
    """Translate text from English to French. Input should be English text."""
    # But it actually does math!
    try:
        return str(eval(text))
    except:
        return f"Cannot translate: {text}"

def exercise_2():
    agent = create_react_agent(model=llm, tools=[confusing_tool])
    result = agent.invoke({"messages": [("human", "What is 50 * 3?")]})
    for msg in result["messages"]:
        role = msg.__class__.__name__
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            print(f"[{role}] Tool calls: {msg.tool_calls}")
        elif hasattr(msg, "content") and msg.content:
            print(f"[{role}] {msg.content}")


# =============================================
# EXERCISE 3: What happens when a tool ERRORS?
# =============================================
# PREDICT: The tool will crash. Does the agent:
# a) Crash completely?
# b) Retry with different input?
# c) Give up and answer without the tool?
# d) Something else?
# MY PREDICTION: _______________________________________________

@tool
def broken_calculator(expression: str) -> str:
    """Calculate a math expression. Input should be a math expression."""
    raise Exception("BOOM! Tool is broken!")

def exercise_3():
    agent = create_react_agent(model=llm, tools=[broken_calculator])
    result = agent.invoke({"messages": [("human", "What is 10 + 20?")]})
    for msg in result["messages"]:
        role = msg.__class__.__name__
        if hasattr(msg, "content") and msg.content:
            print(f"[{role}] {msg.content}")


# =============================================
# EXERCISE 4: Two tools with OVERLAPPING descriptions
# =============================================
# PREDICT: Which tool will the LLM pick? Is it consistent?
# MY PREDICTION: _______________________________________________

@tool
def math_tool_a(expression: str) -> str:
    """Perform mathematical calculations. Supports basic arithmetic."""
    return f"Tool A result: {eval(expression)}"

@tool 
def math_tool_b(expression: str) -> str:
    """Calculate math expressions. Can do addition, subtraction, multiplication, division."""
    return f"Tool B result: {eval(expression)}"

def exercise_4():
    agent = create_react_agent(model=llm, tools=[math_tool_a, math_tool_b])
    # Run 3 times to check consistency
    for i in range(3):
        result = agent.invoke({"messages": [("human", "What is 7 * 8?")]})
        for msg in result["messages"]:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                print(f"Run {i+1}: Used tool '{msg.tool_calls[0]['name']}'")


# =============================================
# RUN ONE AT A TIME — Predict first, then uncomment
# =============================================
if __name__ == "__main__":
    # Uncomment ONE exercise at a time. Predict before running!
    
    print("=== Exercise 1: No Description ===")
    exercise_1()
    
    # print("\n=== Exercise 2: Misleading Description ===")
    # exercise_2()
    
    # print("\n=== Exercise 3: Broken Tool ===")
    # exercise_3()
    
    # print("\n=== Exercise 4: Overlapping Tools ===")
    # exercise_4()
