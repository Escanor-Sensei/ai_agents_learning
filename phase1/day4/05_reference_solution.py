"""
=============================================================================
DAY 4 - REFERENCE SOLUTION: Task (Build Your Own Simple Agent)
=============================================================================

⚠️  DO NOT READ THIS until you've attempted 03_task_build_agent.py yourself!
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


# =========================
# TOOLS
# =========================
def calculator(expression: str) -> str:
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"


def get_word_length(word: str) -> str:
    return str(len(word))


TOOLS = {
    "calculator": calculator,
    "get_word_length": get_word_length,
}

TOOL_DECLARATIONS = [
    {
        "name": "calculator",
        "description": "Calculate a math expression. Input should be a valid Python math expression like '2 + 3 * 4'. Returns the numeric result.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The math expression to evaluate"
                }
            },
            "required": ["expression"]
        }
    },
    {
        "name": "get_word_length",
        "description": "Count the number of characters in a word or phrase. Returns the character count.",
        "parameters": {
            "type": "object",
            "properties": {
                "word": {
                    "type": "string",
                    "description": "The word or phrase to count characters in"
                }
            },
            "required": ["word"]
        }
    }
]


# =========================
# LLM CALL
# =========================
def call_llm(contents: list) -> dict:
    body = {
        "contents": contents,
        "tools": [{"functionDeclarations": TOOL_DECLARATIONS}],
        "systemInstruction": {
            "parts": [{"text":
                "You are a helpful assistant with a calculator and a word length counter. "
                "Use the appropriate tool when needed to answer questions accurately. "
                "Think step by step."
            }]
        }
    }

    response = requests.post(
        GEMINI_URL,
        headers={"Content-Type": "application/json"},
        json=body
    )

    if response.status_code != 200:
        raise Exception(f"API error {response.status_code}: {response.text}")

    return response.json()


# =========================
# AGENT LOOP
# =========================
def run_agent(query: str, max_iterations: int = 10) -> str:
    """
    Simple agent: input → decide → call tool → return result.
    Handles multi-step queries and no-tool queries.
    """

    contents = [{"role": "user", "parts": [{"text": query}]}]
    print(f"\n  Query: {query}")

    for iteration in range(max_iterations):
        # Call LLM
        response_data = call_llm(contents)
        candidate = response_data["candidates"][0]
        parts = candidate["content"]["parts"]
        contents.append({"role": "model", "parts": parts})

        # Check for tool calls
        has_tool_call = False
        final_text = ""

        for part in parts:
            if "functionCall" in part:
                has_tool_call = True
                func_call = part["functionCall"]
                tool_name = func_call["name"]
                tool_args = func_call.get("args", {})
                arg_value = list(tool_args.values())[0] if tool_args else ""

                print(f"    Step {iteration+1}: {tool_name}({arg_value})", end="")

                # Execute tool
                if tool_name in TOOLS:
                    tool_result = TOOLS[tool_name](arg_value)
                    print(f" → {tool_result}")
                else:
                    tool_result = f"Error: Unknown tool '{tool_name}'"
                    print(f" → {tool_result}")

                # Send result back to LLM
                contents.append({
                    "role": "user",
                    "parts": [{
                        "functionResponse": {
                            "name": tool_name,
                            "response": {"result": tool_result}
                        }
                    }]
                })

            elif "text" in part:
                final_text = part["text"]

        # If no tool call, we're done
        if not has_tool_call:
            print(f"    → Final answer (iteration {iteration+1})")
            return final_text

    return f"Agent stopped after {max_iterations} iterations"


# =========================
# TEST
# =========================
if __name__ == "__main__":
    print("=" * 60)
    print("REFERENCE SOLUTION — Simple Agent")
    print("=" * 60)

    # Test 1: Simple math
    print("\nTest 1: Simple math")
    answer = run_agent("What is 15 * 23 + 7?")
    print(f"  Answer: {answer[:200]}")

    # Test 2: Word length
    print("\nTest 2: Word length")
    answer = run_agent("How many characters in the word 'artificial'?")
    print(f"  Answer: {answer[:200]}")

    # Test 3: Multi-step (word length → calculator)
    print("\nTest 3: Multi-step")
    answer = run_agent("How many characters in 'hello'? Multiply that by 10.")
    print(f"  Answer: {answer[:200]}")

    # Test 4: No tool needed
    print("\nTest 4: No tool needed")
    answer = run_agent("What is Python?")
    print(f"  Answer: {answer[:200]}")

    print(f"""

{'='*60}
DAY 4 COMPLETE!
{'='*60}

You built a simple agent that:
  ✓ Takes user input
  ✓ Decides whether to use a tool (or answer directly)
  ✓ Calls the right tool with the right input
  ✓ Returns the result to the user
  ✓ Handles multi-step queries (chaining tool calls)

This is the foundation of ALL agents:
  INPUT → DECIDE → ACT → OBSERVE → REPEAT → ANSWER

Phase 1 is complete! You now understand:
  Day 1: What agents are (vs prompts/workflows)
  Day 2: How agents plan and execute (ReAct vs Plan-then-Execute)
  Day 3: How tools and memory work
  Day 4: How to BUILD an agent from scratch

Next up — Phase 2: Function calling, structured outputs,
error handling, and building a tool-using agent with 3+ real tools!
""")
