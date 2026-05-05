"""
=============================================================================
DAY 3 - FILE 06: PREDICT & DEBUG EXERCISES
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
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

llm = ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL"))


# =============================================
# EXERCISE 1: Memory contains WRONG information
# =============================================
# Setup: We tell the agent "My name is Alice" but memory returns "Bob"
# PREDICT: Does the agent trust the memory tool or the conversation?
# MY PREDICTION: _______________________________________________

@tool
def memory_search_wrong(query: str) -> str:
    """Search long-term memory for facts about the user."""
    return "Found in memory: user_name = Bob, favorite_color = red"

def exercise_1():
    memory = MemorySaver()
    agent = create_react_agent(model=llm, tools=[memory_search_wrong], checkpointer=memory)
    config = {"configurable": {"thread_id": "ex1"}}

    result = agent.invoke(
        {"messages": [("human", "My name is Alice. Check your memory — what name do you have for me?")]},
        config=config
    )
    print(f"  Response: {result['messages'][-1].content[:200]}")
    print("\n  QUESTION: Did it trust memory ('Bob') or the conversation ('Alice')?")
    print("  LESSON: Agents can be confused by conflicting sources!")


# =============================================
# EXERCISE 2: Reflection always scores LOW
# =============================================
# PREDICT: If the evaluator always returns score=4, does the agent:
# a) Retry infinitely?  b) Stop at max retries?  c) Crash?
# MY PREDICTION: _______________________________________________

def exercise_2():
    def harsh_evaluator(query: str, answer: str) -> tuple:
        return 4, "Not specific enough. Needs more concrete examples."

    def generate(query: str, critique: str = "") -> str:
        prompt = f"Answer: {query}"
        if critique:
            prompt += f"\nPrevious feedback: {critique}"
        return llm.invoke(prompt).content

    query = "What is Python?"
    max_retries = 3

    for attempt in range(1, max_retries + 1):
        answer = generate(query, "" if attempt == 1 else critique)
        score, critique = harsh_evaluator(query, answer)
        print(f"  Attempt {attempt}: Score={score}, Answer={answer[:80]}...")
        if score >= 7:
            print("  → Accepted!")
            break
    else:
        print(f"  → Max retries ({max_retries}) exhausted. Returning last answer.")
        print("  LESSON: Always have a max_retries limit! Without it → infinite loop.")


# =============================================
# RUN ONE AT A TIME — Predict first, then uncomment
# =============================================
if __name__ == "__main__":
    print("=== Exercise 1: Wrong Memory ===")
    exercise_1()

    # print("\n=== Exercise 2: Always-Low Reflection Score ===")
    # exercise_2()
