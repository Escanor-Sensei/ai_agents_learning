"""
=============================================================================
DAY 4 - FILE 03: TASK — Build Your Own Simple Agent
=============================================================================

INSTRUCTIONS:
Build a complete agent from scratch (NO LangChain) that can handle:

    "What is 15 * 23 + 7?"
    "How many characters in 'hello'? Multiply that by 10."

Requirements:
1. Use the Gemini REST API directly (like Files 02 and 04)
2. Implement a calculator tool as a Python function
3. Implement a get_word_length tool as a Python function
4. Define JSON schemas for both tools
5. Write a system prompt that tells the LLM to use tools when needed
6. Implement the agent loop:
   - Call LLM → check if tool call → execute tool → loop → return answer
7. Print the agent's decision at each step (which tool, what input, what result)
8. Handle the case where no tool is needed (direct answer)

SCORING:
- Basic: Handles single-tool math queries ✓
- Good: Handles single-tool word length queries ✓
- Great: Handles multi-step queries (word length → calculator) ✓
- Excellent: Has max iteration limit + handles errors gracefully ✓

=============================================================================
HINTS (read ONE AT A TIME, only if stuck):
=============================================================================

HINT 1: Start with the tool functions and their JSON schemas.
         Each schema needs: name, description, parameters (type, properties, required).

HINT 2: The API call needs: contents (messages), tools (declarations),
         systemInstruction. Use requests.post() to the Gemini URL.

HINT 3: The response has candidates[0].content.parts — each part is either:
         - {"functionCall": {"name": "...", "args": {...}}} — tool request
         - {"text": "..."} — text response (could be final answer)

HINT 4: To send a tool result back, add a "user" message with:
         {"functionResponse": {"name": "tool_name", "response": {"result": "..."}}}

HINT 5: The loop: while True → call LLM → if functionCall, run tool + loop
         → if text only, that's the final answer → break

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


# =========================
# TODO 1: Define your tools
# =========================

def calculator(expression: str) -> str:
    # YOUR CODE HERE
    pass


def get_word_length(word: str) -> str:
    # YOUR CODE HERE
    pass


TOOLS = {
    # YOUR CODE HERE: map tool names to functions
}


# =========================
# TODO 2: Define tool schemas (JSON)
# =========================

TOOL_DECLARATIONS = [
    # YOUR CODE HERE: one dict per tool with name, description, parameters
]


# =========================
# TODO 3: Write the LLM call function
# =========================

def call_llm(contents: list) -> dict:
    """Call Gemini API with tool declarations."""
    # YOUR CODE HERE: construct the request body and make the API call
    pass


# =========================
# TODO 4: Write the agent loop
# =========================

def run_agent(query: str, max_iterations: int = 10) -> str:
    """
    The agent loop:
    1. Send query to LLM
    2. If LLM returns functionCall → execute tool → send result → go to 1
    3. If LLM returns text → return it as the final answer
    """
    # YOUR CODE HERE
    pass


# =========================
# TODO 5: Test your agent
# =========================
if __name__ == "__main__":
    print("=" * 60)
    print("MY SIMPLE AGENT")
    print("=" * 60)

    # Test 1: Simple math
    print("\nTest 1: Simple math")
    answer = run_agent("What is 15 * 23 + 7?")
    print(f"Answer: {answer}")

    # Test 2: Word length
    print("\nTest 2: Word length")
    answer = run_agent("How many characters in the word 'artificial'?")
    print(f"Answer: {answer}")

    # Test 3: Multi-step (STRETCH GOAL)
    print("\nTest 3: Multi-step")
    answer = run_agent("How many characters in 'hello'? Multiply that by 10.")
    print(f"Answer: {answer}")

    # Test 4: No tool needed
    print("\nTest 4: No tool needed")
    answer = run_agent("What is Python?")
    print(f"Answer: {answer}")
