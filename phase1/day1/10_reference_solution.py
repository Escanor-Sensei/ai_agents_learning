"""
=============================================================================
DAY 1 - REFERENCE SOLUTION: Task 1 (Agent from scratch)
=============================================================================

⚠️  DO NOT READ THIS until you've attempted 08_task_build_agent.py yourself!
     Struggle is where learning happens.
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


# ---- TOOLS ----
def calculator(expression: str) -> str:
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"


def get_word_length(word: str) -> str:
    return str(len(word))


TOOLS = {"calculator": calculator, "get_word_length": get_word_length}

SYSTEM_PROMPT = """You are a helpful assistant with these tools:

1. calculator - Evaluate a math expression. Example input: 2 + 3 * 4
2. get_word_length - Count characters in a word. Example input: hello

To use a tool, respond EXACTLY like this:
THOUGHT: <why you need this tool>
TOOL: <tool_name>
INPUT: <tool_input>

When you have the final answer:
THOUGHT: <your reasoning>
ANSWER: <final answer>

Rules:
- One tool per turn
- Always start with THOUGHT
- Wait for tool results before continuing"""


# ---- LLM CALL ----
def call_llm(messages: list) -> str:
    contents = []
    for msg in messages:
        contents.append({
            "role": msg["role"],
            "parts": [{"text": msg["content"]}]
        })

    response = requests.post(
        GEMINI_URL,
        headers={"Content-Type": "application/json"},
        json={"contents": contents}
    )

    if response.status_code != 200:
        raise Exception(f"API error: {response.status_code} - {response.text}")

    return response.json()["candidates"][0]["content"]["parts"][0]["text"]


# ---- PARSER ----
def parse_response(text: str) -> dict:
    """Parse LLM response into structured data."""
    result = {"type": "unknown", "thought": "", "raw": text}

    for line in text.strip().split("\n"):
        line = line.strip()
        if line.startswith("THOUGHT:"):
            result["thought"] = line[len("THOUGHT:"):].strip()
        elif line.startswith("TOOL:"):
            result["type"] = "tool_call"
            result["tool"] = line[len("TOOL:"):].strip()
        elif line.startswith("INPUT:"):
            result["input"] = line[len("INPUT:"):].strip()
        elif line.startswith("ANSWER:"):
            result["type"] = "final_answer"
            result["answer"] = line[len("ANSWER:"):].strip()

    # If we didn't find our markers, treat the whole thing as a final answer
    if result["type"] == "unknown":
        result["type"] = "final_answer"
        result["answer"] = text.strip()

    return result


# ---- AGENT LOOP ----
def run_agent(query: str, max_iterations: int = 5) -> str:
    messages = [
        {"role": "user", "content": SYSTEM_PROMPT + "\n\nUser query: " + query}
    ]

    print(f"\n{'='*50}")
    print(f"Query: {query}")
    print(f"{'='*50}")

    for i in range(max_iterations):
        print(f"\n--- Step {i + 1} ---")

        # Call LLM
        response_text = call_llm(messages)
        print(f"LLM: {response_text}")

        # Parse
        parsed = parse_response(response_text)
        print(f"Parsed: type={parsed['type']}, thought={parsed.get('thought', '')}")

        if parsed["type"] == "final_answer":
            answer = parsed.get("answer", response_text)
            print(f"\n✓ Final Answer: {answer}")
            return answer

        elif parsed["type"] == "tool_call":
            tool_name = parsed["tool"]
            tool_input = parsed.get("input", "")
            print(f"→ Calling: {tool_name}({tool_input})")

            if tool_name in TOOLS:
                tool_result = TOOLS[tool_name](tool_input)
            else:
                tool_result = f"Error: Unknown tool '{tool_name}'"

            print(f"→ Result: {tool_result}")

            # Add to conversation
            messages.append({"role": "model", "content": response_text})
            messages.append({
                "role": "user",
                "content": f"Tool result: {tool_result}\n\nContinue with the next step or provide ANSWER."
            })

    return "Max iterations reached."


# ---- TEST ----
if __name__ == "__main__":
    # Test 1
    result = run_agent("What is 15 * 23 + 7?")
    print(f"\nGot: {result} | Expected: 352")

    # Test 2
    print("\n")
    result2 = run_agent("How many characters in 'hello' multiplied by 10?")
    print(f"\nGot: {result2} | Expected: 50")
