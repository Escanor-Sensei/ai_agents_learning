"""
=============================================================================
DAY 1 - TASK 1: Build Your Own Agent (NO SOLUTION — YOU DO THIS)
=============================================================================

INSTRUCTIONS:
Build a raw Python agent (no LangChain) that can answer:

    "What is 15 * 23 + 7?"

Requirements:
1. Use the Gemini REST API directly (like file 04_raw_prompt.py)
2. Implement a calculator tool as a Python function
3. Write a system prompt that tells the LLM to use tools
4. Implement the agent loop: call LLM -> parse -> execute tool -> loop
5. The agent should print its thinking at each step

You CAN reference files 04 and 05 for the API call structure,
but write the agent loop yourself from scratch.

STRETCH GOAL:
Also handle this query (requires TWO tool calls):
    "How many characters in 'hello' multiplied by 10?"

=============================================================================
HINTS (read these ONE AT A TIME, only if stuck):
=============================================================================

HINT 1: Your system prompt needs to tell the LLM a specific FORMAT for
         requesting tools. Something like:
         TOOL: calculator
         INPUT: 15 * 23 + 7

HINT 2: The loop pattern is:
         messages = [initial prompt]
         while True:
             response = call_llm(messages)
             if response wants a tool -> run tool -> add to messages
             if response has final answer -> break

HINT 3: To send tool results back, add them as a new "user" message:
         "Tool result: 352"
         Then call the LLM again with the updated messages.

=============================================================================
STARTER CODE (fill in the blanks):
=============================================================================
"""

import os
import json
from dotenv import load_dotenv

try:
    import requests
except ImportError:
    os.system("pip install requests")
    import requests

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"


# TOOL: Implement the calculator function
def calculator(expression: str) -> str:
    """Your code here"""
    pass


# LLM CALL: Fill in the API call
def call_llm(messages: list) -> str:
    """
    Send messages to Gemini and return the response text.
    Refer to file 04_raw_prompt.py for the API structure.
    """
    # YOUR CODE HERE
    # 1. Build the request body with contents
    # 2. Make the POST request
    # 3. Parse and return the text
    pass


# PARSER: Extract tool calls from LLM response
def parse_llm_response(text: str):
    """
    Parse the LLM's response.
    Return a dict like:
        {"type": "tool_call", "tool": "calculator", "input": "15 * 23 + 7"}
    or:
        {"type": "final_answer", "answer": "The result is 352"}
    """
    # YOUR CODE HERE
    pass


# THE AGENT LOOP: This is the heart of the agent
def run_agent(query: str) -> str:
    """
    1. Build initial messages with system prompt + user query
    2. Loop:
       a. Call LLM
       b. Parse response
       c. If tool call → execute tool → add result to messages → continue
       d. If final answer → return it
    3. Max 5 iterations to prevent infinite loops
    """
    # YOUR CODE HERE
    pass


# ---- TEST ----
if __name__ == "__main__":
    result = run_agent("What is 15 * 23 + 7?")
    print(f"\nFinal Answer: {result}")
    print(f"Expected: 352")

    # STRETCH: Uncomment when ready
    # result2 = run_agent("How many characters in 'hello' multiplied by 10?")
    # print(f"\nFinal Answer: {result2}")
    # print(f"Expected: 50")
